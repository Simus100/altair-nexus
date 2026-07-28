#!/usr/bin/env python3
import json
import html
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path('/root/.openclaw/workspace/aion-nexus')
NEWS = ROOT / 'data' / 'news.json'
CATEGORIES = ROOT / 'data' / 'categories.json'
HISTORY_DIR = ROOT / 'data' / 'history'
OUT = ROOT / 'site' / 'stories'
IMAGE = '/site/assets/aion-brief-generated.jpg'
SITE_URL = 'https://nexus.universalis.it'

VISUAL_CLASS = {
    'ai': 'visual-ai',
    'tech': 'visual-tech',
    'geo': 'visual-geo',
    'fin': 'visual-fin',
    'markets': 'visual-markets',
    'startup': 'visual-startup',
    'science': 'visual-science',
    'future': 'visual-future',
}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", '-', value)
    return value.strip('-') or 'story'


def story_slug(item: dict) -> str:
    return slugify(item.get('id') or item.get('title') or 'story')


def fmt_date(ts: str) -> str:
    return ts.replace('T', ' ').replace('+01:00', ' CET').replace('+02:00', ' CEST')


def clean_public_hook(text: str, source_label: str = '') -> str:
    """Keep source attribution in metadata/source rows, not in the subtitle."""
    cleaned = re.sub(r'\s+', ' ', str(text or '')).strip()
    if not cleaned:
        return ''
    labels = [source_label, 'Reuters', 'BBC', 'TechCrunch', 'Associated Press', 'AP', 'Al Jazeera', 'NASA', 'Google']
    labels = [re.escape(label.strip()) for label in labels if label and label.strip()]
    if labels:
        label_group = '|'.join(labels)
        cleaned = re.sub(
            rf'^(?:La|Il|Lo|L’|L\'|The)?\s*({label_group})\s+(racconta|riporta|riferisce|segnala|mette in luce|mette a fuoco|descrive|annuncia|conferma)[,:;]?\s+(che\s+)?',
            '',
            cleaned,
            flags=re.IGNORECASE,
        ).strip()
    cleaned = re.sub(r'^(Secondo|In un(?:a)?\s+analisi(?:\s+di)?)\s+', '', cleaned, flags=re.IGNORECASE).strip()
    cleaned = normalize_public_brand(cleaned)
    return cleaned[:1].upper() + cleaned[1:] if cleaned else ''


def normalize_public_brand(text: str) -> str:
    text = str(text or '')
    text = re.sub(r'\bAION\s+NEXUS\b', 'Altair Nexus', text, flags=re.IGNORECASE)
    text = re.sub(r'\bAion\s+Nexus\b', 'Altair Nexus', text, flags=re.IGNORECASE)
    return text


def split_body_and_context(body: str) -> tuple[list[str], list[str]]:
    body_parts = []
    context_parts = []
    for part in [p.strip() for p in str(body or '').split('\n\n') if p.strip()]:
        if re.match(r'^(Per\s+(?:AION\s+NEXUS|Altair\s+Nexus)\b|In\s+ottica\s+(?:AION\s+NEXUS|Altair\s+Nexus)\b)', part, flags=re.IGNORECASE):
            context_parts.append(part)
        else:
            body_parts.append(part)
    return body_parts, context_parts


def related_score(item: dict, candidate: dict) -> tuple[int, str]:
    score = 0
    if candidate.get('category') == item.get('category'):
        score += 5
    item_tags = {str(tag).lower() for tag in item.get('tags', []) if str(tag).strip()}
    candidate_tags = {str(tag).lower() for tag in candidate.get('tags', []) if str(tag).strip()}
    score += len(item_tags & candidate_tags) * 2
    if candidate.get('sourceLabel') == item.get('sourceLabel'):
        score += 1
    return score, str(candidate.get('timestamp') or '')


def build_aion_opinion(item: dict, category_name: str) -> str:
    tags = [str(tag).strip() for tag in item.get('tags', []) if str(tag).strip()][:3]
    subcategory = str(item.get('subcategory') or '').strip()
    score = int(item.get('qualityScore') or 0)
    category_id = item.get('category')

    category_lens = {
        'ai': 'la partita vera si giochi sulla capacità di trasformare vantaggio tecnico in distribuzione e standard di mercato',
        'tech': 'conti soprattutto il controllo dei passaggi critici dell’infrastruttura e non solo l’annuncio di giornata',
        'geopolitica': 'il punto decisivo sia quanto rapidamente il rischio politico si trasferisce su logistica, energia e prezzi',
        'finanza': 'il mercato stia misurando soprattutto sostenibilità, costo del capitale e credibilità dell’esecuzione',
        'mercati': 'gli operatori stiano prezzando la tenuta del sistema più che il rumore delle singole headline',
        'startup': 'conti meno la narrativa e molto di più la capacità di finanziare crescita, distribuzione e resistenza nel tempo',
        'scienza': 'il valore emerga quando la scoperta mostra una traiettoria concreta verso applicazioni, piattaforme o vantaggi cumulativi',
        'futuro': 'il segnale abbia peso quando anticipa cambiamenti di abitudini, infrastrutture o modelli industriali',
    }
    lens = category_lens.get(category_id, 'la notizia conti soprattutto per ciò che anticipa sulla direzione del contesto')
    intensity = (
        'Se il quadro regge anche nelle prossime ore, questo può diventare un passaggio che riallinea davvero le aspettative.'
        if score >= 93 else
        'Non è ancora una svolta definitiva, ma è il tipo di movimento che cambia il modo in cui il dossier viene letto.'
        if score >= 88 else
        'Per ora vale più come indicatore anticipatore che come svolta pienamente consolidata.'
    )
    subcategory_line = f' Nel perimetro {subcategory.lower()}, Aion legge qui un indizio che va oltre il fatto singolo.' if subcategory else ''
    tag_line = f" I segnali su {', '.join(tags)} suggeriscono che il mercato leggerà questa storia soprattutto come test di tenuta e direzione." if tags else ''
    text = f"Sul fronte {category_name.lower()} il punto non è ripetere la cronaca, ma capire se {lens}.{subcategory_line}{tag_line} {intensity}"
    return re.sub(r'\s+', ' ', text).strip()


def story_structured_data(item: dict, category_name: str, canonical: str, image: str, description: str) -> str:
    keywords = [str(tag).strip() for tag in item.get('tags', []) if str(tag).strip()]
    site_url = f'{SITE_URL}/site/'
    organization = {
        '@type': 'Organization',
        '@id': f'{SITE_URL}/#organization',
        'name': 'Universalis Produzioni',
        'url': 'https://www.universalis.it/',
        'logo': {'@type': 'ImageObject', 'url': image},
    }
    website = {
        '@type': 'WebSite',
        '@id': f'{SITE_URL}/site/#website',
        'name': 'Altair Nexus',
        'url': site_url,
        'inLanguage': 'it-IT',
        'publisher': {'@id': f'{SITE_URL}/#organization'},
    }
    breadcrumb = {
        '@type': 'BreadcrumbList',
        '@id': f'{canonical}#breadcrumb',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Altair Nexus', 'item': site_url},
            {'@type': 'ListItem', 'position': 2, 'name': 'History', 'item': f'{SITE_URL}/site/history.html'},
            {'@type': 'ListItem', 'position': 3, 'name': normalize_public_brand(item.get('title', '')), 'item': canonical},
        ],
    }
    payload = {
        '@context': 'https://schema.org',
        '@graph': [
            organization,
            website,
            breadcrumb,
            {
                '@type': 'NewsArticle',
                '@id': f'{canonical}#article',
                'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical},
                'headline': normalize_public_brand(item.get('title', '')),
                'description': description,
                'image': [image],
                'datePublished': item.get('timestamp', ''),
                'dateModified': item.get('timestamp', ''),
                'inLanguage': 'it-IT',
                'articleSection': category_name,
                'keywords': keywords,
                'about': keywords[:5],
                'isAccessibleForFree': True,
                'author': {'@type': 'Organization', 'name': 'Altair Nexus', 'url': site_url},
                'publisher': {'@id': f'{SITE_URL}/#organization'},
                'isPartOf': {'@id': f'{SITE_URL}/site/#website'},
                'breadcrumb': {'@id': f'{canonical}#breadcrumb'},
                'citation': item.get('sourceUrl') or '',
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')


def render_story(item: dict, category_name: str, all_items: list[dict]) -> str:
    slug = story_slug(item)
    title_text = normalize_public_brand(item['title'])
    title = html.escape(title_text)
    public_hook = clean_public_hook(item.get('hook') or item.get('opinion') or '', item.get('sourceLabel') or '')
    description_text = public_hook or item.get('opinion') or ''
    description = html.escape(description_text)
    canonical = f"{SITE_URL}/site/stories/{quote(slug)}.html"
    image = f"{SITE_URL}{IMAGE}"
    body_parts, context_parts = split_body_and_context(item.get('body') or '')
    body_html = '\n'.join(f'<p class="story-body">{html.escape(normalize_public_brand(p))}</p>' for p in body_parts)
    tags_html = ''.join(f'<span class="tag-pill">#{html.escape(tag)}</span>' for tag in item.get('tags', []))
    aion_opinion = html.escape(build_aion_opinion(item, category_name))

    related = sorted(
        [x for x in all_items if x.get('id') != item.get('id')],
        key=lambda candidate: related_score(item, candidate),
        reverse=True,
    )[:3]
    related_html = ''.join(
        f'''<a class="related-card" href="./{quote(story_slug(rel))}.html">\n'''
        f'''  <span class="related-kicker">{html.escape(category_name if rel.get('category') == item.get('category') else rel.get('category', '').title())}</span>\n'''
        f'''  <strong>{html.escape(normalize_public_brand(rel.get('title', '')))}</strong>\n'''
        f'''  <span>{html.escape(clean_public_hook(rel.get('hook', ''), rel.get('sourceLabel', '')))}</span>\n'''
        f'''</a>'''
        for rel in related
    )

    source_url = html.escape(item.get('sourceUrl') or '#')
    source_label = html.escape(item.get('sourceLabel') or 'Fonte')
    opinion_parts = context_parts + ([item.get('opinion')] if item.get('opinion') else [])
    opinion = html.escape(normalize_public_brand('\n\n'.join(str(part).strip() for part in opinion_parts if str(part).strip())))
    visual_class = VISUAL_CLASS.get(item.get('visual'), '')
    structured_data = story_structured_data(item, category_name, canonical, image, description_text)
    brief_lede = html.escape(description_text)
    brief_facts = [
        f"Categoria: {category_name}.",
        f"Fonte principale: {item.get('sourceLabel') or 'fonte verificata'}.",
    ]
    brief_facts_html = ''.join(
        f'<span>{html.escape(point)}</span>'
        for point in brief_facts
        if str(point).strip()
    )

    return f'''<!doctype html>
<html lang="it">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} — Altair Nexus</title>
    <meta name="description" content="{description}" />
    <meta name="robots" content="index,follow" />
    <meta property="og:site_name" content="Altair Nexus" />
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="it_IT" />
    <meta property="og:title" content="{title} — Altair Nexus" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="{image}" />
    <meta property="og:image:alt" content="Visual editoriale di Altair Nexus" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title} — Altair Nexus" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{image}" />
    <link rel="canonical" href="{canonical}" />
    <link rel="stylesheet" href="../assets/styles.css?v=20260719-brief-tags" />
    <script type="application/ld+json">{structured_data}</script>
    <style>
      .story-page {{ padding: 24px 0 56px; }}
      .story-page-grid {{ display: grid; gap: 20px; }}
      .story-page-card, .related-card {{
        background: linear-gradient(180deg, rgba(18, 26, 40, 0.96), rgba(13, 20, 33, 0.96));
        border: 1px solid rgba(141, 165, 204, 0.12);
        box-shadow: 0 12px 30px rgba(2, 8, 18, 0.18);
        border-radius: 26px;
      }}
      .story-page-card {{ overflow: hidden; border-color: rgba(141, 165, 204, 0.16); }}
      .story-page-inner {{ width: 100%; margin: 0 auto; padding: 28px 0 34px; }}
      .story-panel-static {{ background: transparent; border: 0; box-shadow: none; border-radius: 0; }}
      .story-back {{ display: inline-flex; width: calc(100% - 64px); max-width: 920px; margin: 0 auto 16px; color: var(--muted); }}
      .related-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 16px; }}
      .related-card {{ padding: 18px; display: grid; gap: 10px; }}
      .related-kicker {{ color: var(--cyan); font-size: .74rem; letter-spacing: .12em; text-transform: uppercase; }}
      .related-card strong {{ line-height: 1.35; }}
      .related-card span:last-child {{ color: var(--muted); font-size: .92rem; line-height: 1.55; }}
      .story-breadcrumb {{ display: flex; flex-wrap: wrap; gap: 8px; width: calc(100% - 64px); max-width: 920px; margin: 0 auto 12px; color: var(--muted); font-size: .84rem; }}
      .story-breadcrumb a {{ color: var(--muted); }}
      .story-opinion.story-brief {{ text-align: left; padding: 22px; background: linear-gradient(180deg, rgba(76, 231, 255, 0.055), rgba(255,255,255,0.026)); }}
      .story-opinion.story-brief strong {{ text-align: left; }}
      .story-opinion.story-brief .story-brief-lede {{ margin-left: 0; margin-right: 0; color: var(--heading); font-size: 1.04rem; line-height: 1.72; text-align: left; }}
      .story-brief-card {{ margin-top: 14px; display: grid; gap: 14px; color: var(--text); }}
      .story-brief-lede {{ margin: 0; max-width: 76ch; color: var(--heading); font-size: 1.04rem; line-height: 1.72; text-align: left; }}
      .story-brief-facts {{ display: flex; flex-wrap: wrap; gap: 8px; }}
      .story-brief-facts span {{ display: inline-flex; align-items: center; min-height: 30px; padding: 6px 10px; border-radius: 8px; background: rgba(255,255,255,0.04); border: 1px solid rgba(141, 165, 204, 0.16); color: var(--muted); font-size: .82rem; line-height: 1.2; }}
      @media (max-width: 800px) {{ .related-grid {{ grid-template-columns: 1fr; }} .story-page-inner {{ width: 100%; padding: 24px 0 32px; }} .story-back {{ width: calc(100% - 32px); }} .story-panel-static .story-title {{ max-width: 15ch; }} }}
    </style>
  </head>
  <body>
    <div class="background-grid"></div>
    <div class="background-glow glow-a"></div>
    <div class="background-glow glow-b"></div>
    <header class="topbar container">
      <div class="brand-block">
        <div class="brand-mark">Altair Nexus</div>
        <div class="brand-sub">Automation Intelligence by Universalis Produzioni</div>
      </div>
      <nav class="topnav">
        <a href="../">Home</a>
        <a href="../history.html">History</a>
      </nav>
    </header>
    <main class="container story-page">
      <div class="story-page-grid">
        <article class="story-page-card">
          <div class="story-hero {visual_class}"></div>
          <div class="story-page-inner">
            <nav class="story-breadcrumb" aria-label="Breadcrumb">
              <a href="../">Altair Nexus</a>
              <span>/</span>
              <a href="../history.html">History</a>
              <span>/</span>
              <span>{html.escape(category_name)}</span>
            </nav>
            <a class="story-back" href="../">← Torna alla homepage</a>
            <article class="story-panel story-panel-static">
              <div class="story-meta">
                <span class="meta-pill">{html.escape(category_name)}</span>
                <span class="meta-pill">{html.escape(item.get('subcategory',''))}</span>
                <span class="meta-pill">{html.escape(fmt_date(item.get('timestamp','')))}</span>
                <span class="meta-pill">{int(item.get('sourceCount', 0))} fonti</span>
              </div>
              <h1 class="story-title">{title}</h1>
              <p class="story-hook">{description}</p>
              <div class="story-opinion story-brief"><strong>In breve</strong><div class="story-brief-card"><p class="story-brief-lede">{brief_lede}</p><div class="story-brief-facts">{brief_facts_html}</div></div></div>
              <div class="story-tags">{tags_html}</div>
              {body_html}
              <div class="story-footer-row">
                <div class="story-meta">
                  <span class="meta-pill">Fonte: {source_label}</span>
                  <span class="meta-pill">Categoria: {html.escape(category_name)}</span>
                </div>
                <div class="story-meta story-meta-share">
                  <div class="share-actions" aria-label="Condivisione articolo">
                    <button class="source-link story-share-button share-pill-main" type="button" data-copy-link="{html.escape(canonical)}">Copia link</button>
                    <a class="source-link" href="https://wa.me/?text={quote(title_text + ' — ' + normalize_public_brand(item.get('hook','')) + '\n\n' + canonical)}" target="_blank" rel="noreferrer">WhatsApp</a>
                    <a class="source-link" href="https://t.me/share/url?url={quote(canonical)}&text={quote(title_text + ' — ' + normalize_public_brand(item.get('hook','')))}" target="_blank" rel="noreferrer">Telegram</a>
                    <a class="source-link" href="https://www.linkedin.com/sharing/share-offsite/?url={quote(canonical)}" target="_blank" rel="noreferrer">LinkedIn</a>
                    <a class="source-link" href="https://twitter.com/intent/tweet?text={quote(title_text + ' — ' + normalize_public_brand(item.get('hook','')))}&url={quote(canonical)}" target="_blank" rel="noreferrer">X</a>
                  </div>
                </div>
              </div>
              <div class="story-footer-row story-footer-source-row">
                <div class="story-meta">
                  <a class="source-link" href="{source_url}" target="_blank" rel="noreferrer">Fonte: {source_label}</a>
                </div>
              </div>
              <div class="story-opinion story-opinion-aion"><strong>L'opinione di Aion</strong><p class="story-body story-body-extended">{aion_opinion}</p></div>
              <div class="story-opinion"><strong>Perché conta</strong><p>{opinion}</p></div>
            </article>
          </div>
        </article>
        <section>
          <div class="section-head compact">
            <div>
              <div class="section-kicker">Altre storie</div>
              <h2>Continua a leggere</h2>
            </div>
          </div>
          <div class="related-grid">{related_html}</div>
        </section>
      </div>
    </main>
    <script>
      document.addEventListener('DOMContentLoaded', function () {{
        function fallbackCopy(text) {{
          const temp = document.createElement('textarea');
          temp.value = text;
          temp.setAttribute('readonly', '');
          temp.style.position = 'absolute';
          temp.style.left = '-9999px';
          document.body.appendChild(temp);
          temp.select();
          temp.setSelectionRange(0, temp.value.length);
          const ok = document.execCommand('copy');
          document.body.removeChild(temp);
          return ok;
        }}
        document.querySelectorAll('[data-copy-link]').forEach(function (button) {{
          const link = button.getAttribute('data-copy-link');
          button.addEventListener('click', async function () {{
            try {{
              if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {{
                await navigator.clipboard.writeText(link);
              }} else if (!fallbackCopy(link)) {{
                throw new Error('clipboard unavailable');
              }}
              button.textContent = 'Link copiato';
            }} catch (error) {{
              button.textContent = 'Copia fallita';
            }}
            window.setTimeout(function () {{
              button.textContent = 'Copia link';
            }}, 1800);
          }});
        }});
      }});
    </script>
  </body>
</html>
'''


def load_story_items() -> list[dict]:
    items = []
    seen = set()

    def add_many(payload):
        for item in payload if isinstance(payload, list) else []:
            if not isinstance(item, dict):
                continue
            key = item.get('id') or item.get('canonicalKey') or item.get('sourceUrl') or item.get('title')
            if not key or key in seen:
                continue
            seen.add(key)
            items.append(item)

    add_many(json.loads(NEWS.read_text(encoding='utf-8')))
    if HISTORY_DIR.exists():
        for path in sorted(HISTORY_DIR.glob('*.json')):
            if path.name == 'index.json':
                continue
            add_many(json.loads(path.read_text(encoding='utf-8')))
    return items


def cleanup_existing_story_pages() -> int:
    cleaned_count = 0
    hook_pattern = re.compile(r'(<p class="story-hook">)(.*?)(</p>)', flags=re.S)
    brief_pattern = re.compile(
        r'<div class="story-opinion"><strong>In breve</strong><ul class="story-brief-list">(.*?)</ul></div>',
        flags=re.S,
    )
    li_pattern = re.compile(r'<li>(.*?)</li>', flags=re.S)

    def migrate_brief(match):
        points = [
            html.unescape(re.sub(r'<[^>]+>', '', item)).strip()
            for item in li_pattern.findall(match.group(1))
        ]
        points = [point for point in points if point]
        if not points:
            return match.group(0)
        lede = html.escape(points[0])
        facts = ''.join(f'<span>{html.escape(point)}</span>' for point in points[1:])
        return (
            '<div class="story-opinion story-brief"><strong>In breve</strong>'
            f'<div class="story-brief-card"><p class="story-brief-lede">{lede}</p>'
            f'<div class="story-brief-facts">{facts}</div></div></div>'
        )

    for path in OUT.glob('*.html'):
        original = path.read_text(encoding='utf-8')
        updated = original.replace('Lettura di Aion: ', '')
        updated = re.sub(r'styles\.css\?v=[^"]+', 'styles.css?v=20260719-brief-tags', updated)
        updated = updated.replace(
            '      .story-brief-list { margin: 0 0 18px; padding: 16px 18px 16px 34px; border: 1px solid rgba(141, 165, 204, 0.14); border-radius: 18px; background: rgba(255,255,255,0.025); color: var(--text); }\n'
            '      .story-brief-list li { margin: 6px 0; line-height: 1.55; }\n',
            '',
        )
        updated = brief_pattern.sub(migrate_brief, updated)

        def clean_hook_match(match):
            hook_text = html.unescape(re.sub(r'<[^>]+>', '', match.group(2))).strip()
            cleaned_hook = clean_public_hook(hook_text)
            return f'{match.group(1)}{html.escape(cleaned_hook)}{match.group(3)}'

        updated = hook_pattern.sub(clean_hook_match, updated)
        if updated != original:
            path.write_text(updated, encoding='utf-8')
            cleaned_count += 1
    return cleaned_count


def main():
    news = load_story_items()
    categories = {c['id']: c['name'] for c in json.loads(CATEGORIES.read_text(encoding='utf-8'))}
    OUT.mkdir(parents=True, exist_ok=True)

    generated = 0
    for item in news:
        slug = story_slug(item)
        target = OUT / f'{slug}.html'
        html_text = render_story(item, categories.get(item.get('category'), item.get('category', '')), news)
        target.write_text(html_text, encoding='utf-8')
        generated += 1

    cleaned = cleanup_existing_story_pages()
    print(f'Generated {generated} story pages in {OUT}; cleaned {cleaned} existing pages')


if __name__ == '__main__':
    main()
