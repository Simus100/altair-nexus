from pathlib import Path

path = Path('/root/.openclaw/workspace/aion-nexus/scripts/refresh_edition_stable.py')
text = path.read_text()
text = text.replace("import json, os, shutil, subprocess, urllib.request, urllib.parse, xml.etree.ElementTree as ET, hashlib, re, sys\n", "import json, os, shutil, subprocess, urllib.request, urllib.parse, xml.etree.ElementTree as ET, hashlib, re, sys, html\n")
text = text.replace("from datetime import datetime\n", "from datetime import datetime\nfrom email.utils import parsedate_to_datetime\n")
insert_after = "def fetch(url, timeout=15):\n    req = urllib.request.Request(url, headers={'User-Agent': 'AION-NEXUS/1.0'})\n    with urllib.request.urlopen(req, timeout=timeout) as r:\n        return r.read().decode('utf-8', 'ignore')\n\n\n"
new_block = '''def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': 'AION-NEXUS/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'ignore')


def fetch_response(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'AION-NEXUS/1.0'})
    return urllib.request.urlopen(req, timeout=timeout)


def strip_html_text(value):
    value = html.unescape(value or '')
    value = re.sub(r'<script.*?</script>', ' ', value, flags=re.S | re.I)
    value = re.sub(r'<style.*?</style>', ' ', value, flags=re.S | re.I)
    value = re.sub(r'<[^>]+>', ' ', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def extract_article_text(raw_html):
    text = raw_html or ''
    candidates = re.findall(r'<p\b[^>]*>(.*?)</p>', text, flags=re.S | re.I)
    cleaned = [strip_html_text(chunk) for chunk in candidates]
    cleaned = [chunk for chunk in cleaned if len(chunk) >= 80]
    if cleaned:
        merged = '\n\n'.join(cleaned)
        if len(merged) >= 500:
            return merged[:6000]
    fallback = strip_html_text(text)
    return fallback[:6000]


def parse_pub_date(value):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone().isoformat(timespec='seconds')
    except Exception:
        return None


def resolve_google_news_url(url, timeout=20):
    if not url:
        return url
    try:
        with fetch_response(url, timeout=timeout) as response:
            return response.geturl() or url
    except Exception:
        return url


def enrich_signal_source(signal, timeout=20):
    original_link = signal.get('link') or ''
    resolved_url = resolve_google_news_url(original_link, timeout=timeout)
    source_url = resolved_url or original_link
    source_text = ''
    source_excerpt = ''
    fetch_status = 'unfetched'
    try:
        with fetch_response(source_url, timeout=timeout) as response:
            raw = response.read().decode('utf-8', 'ignore')
            source_text = extract_article_text(raw)
            fetch_status = 'ok' if source_text else 'empty'
    except Exception:
        fetch_status = 'fetch_failed'
    if source_text:
        source_excerpt = source_text[:2000]
    meta = resolve_source_metadata(signal.get('title', ''), source_url)
    signal.update({
        'sourceUrlResolved': source_url,
        'sourceText': source_excerpt,
        'sourceTextLength': len(source_text),
        'sourceFetchStatus': fetch_status,
        'sourceLabelGuess': meta['sourceLabel'],
        'sourceTier': meta['sourceTier'],
        'sourceHost': meta['sourceHost'],
    })
    return signal


def generate_editorial_content(signal, scenario, source_label):
    source_text = (signal.get('sourceText') or '').strip()
    if len(source_text) < 500:
        return None

    original_title = clean_raw_title(signal.get('title', ''))
    base_tokens = [tok for tok in text_tokens(original_title) if tok not in {'reuters', 'news', 'update', 'latest'}]
    emphasis = ', '.join(base_tokens[:5]) if base_tokens else signal.get('category', '')

    title_seed = original_title
    if len(title_seed) > 78:
        title_seed = title_seed[:75].rsplit(' ', 1)[0]
    hook_source = source_text.split('. ')[:2]
    hook = '. '.join(hook_source).strip()
    hook = hook[:197] + '...' if len(hook) > 200 else hook
    if not hook:
        hook = unique_hook(signal, scenario, choose_format_blueprint(signal, scenario, signal.get('title', '')))[:200]

    paragraphs = []
    for chunk in re.split(r'\n\s*\n', source_text):
        chunk = chunk.strip()
        if len(chunk) >= 180:
            paragraphs.append(chunk)
        if len(paragraphs) == 3:
            break
    if len(paragraphs) < 2:
        sentences = [s.strip() for s in re.split(r'(?<=[\.!?])\s+', source_text) if len(s.strip()) > 50]
        while sentences and len(paragraphs) < 3:
            take = ' '.join(sentences[:3]).strip()
            sentences = sentences[3:]
            if len(take) >= 160:
                paragraphs.append(take)
    if len(paragraphs) < 2:
        return None

    body_parts = []
    for idx, para in enumerate(paragraphs[:3]):
        if idx == 0:
            body_parts.append(f"{para} Sul piano editoriale, il punto è capire perché questa mossa conti oltre la singola headline.")
        elif idx == 1:
            body_parts.append(f"{para} Per Altair Nexus, il valore sta nel leggere l'impatto industriale, politico o finanziario che la notizia può trascinare.")
        else:
            body_parts.append(f"{para} La chiave è se questo segnale resti episodico oppure inizi a cambiare aspettative, allocazione di capitale o comportamento degli attori coinvolti.")
    body = '\n\n'.join(body_parts)
    body = body[:1500]
    if len(body) < 500:
        return None

    opinion = f"Segnale da seguire: {emphasis[:130]}".strip()
    opinion = opinion[:150]
    tags = []
    seen = set()
    for tok in base_tokens:
        if tok not in seen:
            tags.append(tok.capitalize() if len(tok) > 3 else tok.upper())
            seen.add(tok)
        if len(tags) == 5:
            break
    while len(tags) < 5:
        filler = [SCENARIO_CATEGORY.get(scenario, signal.get('category', '')), source_label.lower(), 'analisi', 'briefing', 'nexus']
        for tok in filler:
            key = tok.lower()
            if key not in seen:
                tags.append(tok.capitalize() if len(tok) > 3 else tok.upper())
                seen.add(key)
            if len(tags) == 5:
                break

    quality = 84 + min(13, max(0, len(source_text) // 400))
    return {
        'title': title_seed[:120],
        'hook': hook,
        'body': body,
        'opinion': opinion,
        'tags': tags[:5],
        'qualityScore': max(84, min(97, int(quality))),
    }


'''
if insert_after not in text:
    raise SystemExit('insert point not found')
text = text.replace(insert_after, new_block)
path.write_text(text)
