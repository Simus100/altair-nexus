#!/usr/bin/env python3
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path('/root/.openclaw/workspace/aion-nexus')
SITE = ROOT / 'site'
DATA = ROOT / 'data'
NEWS = DATA / 'news.json'
STATS = DATA / 'stats.json'
CATEGORIES = DATA / 'categories.json'
REPORT_ITEMS = SITE / 'reports' / 'items'
SITE_URL = 'https://nexus.universalis.it'
CANONICAL_BASE = f'{SITE_URL}/site'
IMAGE_URL = f'{CANONICAL_BASE}/assets/aion-brief-generated.jpg'

GEO_HEAD_START = '<!-- ALTAIR_GEO_HEAD_START -->'
GEO_HEAD_END = '<!-- ALTAIR_GEO_HEAD_END -->'
GEO_BODY_START = '<!-- ALTAIR_GEO_BODY_START -->'
GEO_BODY_END = '<!-- ALTAIR_GEO_BODY_END -->'
LEGACY_GEO_HEAD_START = '<!-- AION_GEO_HEAD_START -->'
LEGACY_GEO_HEAD_END = '<!-- AION_GEO_HEAD_END -->'
LEGACY_GEO_BODY_START = '<!-- AION_GEO_BODY_START -->'
LEGACY_GEO_BODY_END = '<!-- AION_GEO_BODY_END -->'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'story'


def story_slug(item: dict) -> str:
    return slugify(item.get('id') or item.get('title') or 'story')


def clean_text(value: str, limit: int | None = None) -> str:
    value = re.sub(r'\s+', ' ', str(value or '')).strip()
    value = normalize_public_brand(value)
    return value[:limit].rstrip() if limit else value


def normalize_public_brand(text: str) -> str:
    text = str(text or '')
    text = re.sub(r'\bAION\s+NEXUS\b', 'Altair Nexus', text, flags=re.IGNORECASE)
    text = re.sub(r'\bAion\s+Nexus\b', 'Altair Nexus', text, flags=re.IGNORECASE)
    return text


def iso_or_now(path: Path) -> str:
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).astimezone().isoformat(timespec='seconds')
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def story_url(item: dict) -> str:
    return f'{CANONICAL_BASE}/stories/{quote(story_slug(item))}.html'


def report_pages() -> list[Path]:
    if not REPORT_ITEMS.exists():
        return []
    return sorted(REPORT_ITEMS.glob('*.html'))


def report_title(page: Path) -> str:
    text = page.read_text(encoding='utf-8', errors='ignore')
    match = re.search(r'<h1\b[^>]*>(.*?)</h1>', text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        match = re.search(r'<title\b[^>]*>(.*?)</title>', text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return page.stem.replace('-', ' ').title()
    title = re.sub(r'<[^>]+>', ' ', match.group(1))
    title = html.unescape(re.sub(r'\s+', ' ', title)).strip()
    return title.replace('Cervello Geopolitico 3D:', '').replace(' — Altair Nexus Report', '').strip()


def build_homepage_jsonld(news: list[dict], stats: dict, categories: dict[str, str], reports: list[Path]) -> str:
    item_list = [
        {
            '@type': 'ListItem',
            'position': index,
            'url': story_url(item),
            'name': normalize_public_brand(item.get('title', '')),
            'description': clean_text(item.get('hook') or item.get('opinion') or '', 240),
        }
        for index, item in enumerate(news, start=1)
    ]
    report_list = [
        {
            '@type': 'ListItem',
            'position': index,
            'url': f'{CANONICAL_BASE}/reports/items/{page.name}',
            'name': report_title(page),
        }
        for index, page in enumerate(reports, start=1)
    ]
    payload = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'CollectionPage',
                '@id': f'{CANONICAL_BASE}/#current-edition',
                'url': f'{CANONICAL_BASE}/',
                'name': 'Altair Nexus - edizione corrente',
                'description': 'Briefing editoriale in italiano su intelligenza artificiale, tecnologia, geopolitica, finanza, mercati, startup e scienza.',
                'inLanguage': 'it-IT',
                'isPartOf': {'@id': f'{CANONICAL_BASE}/#website'},
                'dateModified': stats.get('editionUpdatedAt') or iso_or_now(SITE / 'index.html'),
                'about': list(categories.values()),
                'image': [IMAGE_URL],
                'mainEntity': {'@type': 'ItemList', 'itemListElement': item_list},
            },
            {
                '@type': 'ItemList',
                '@id': f'{CANONICAL_BASE}/#reports',
                'name': 'Report Altair Nexus',
                'itemListElement': report_list,
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')


def strip_block(text: str, start: str, end: str) -> str:
    return re.sub(rf'\s*{re.escape(start)}.*?{re.escape(end)}\s*', '\n', text, flags=re.DOTALL)


def update_homepage(news: list[dict], stats: dict, categories: dict[str, str], reports: list[Path]) -> None:
    index = SITE / 'index.html'
    if not index.exists():
        return
    text = index.read_text(encoding='utf-8')
    text = strip_block(text, GEO_HEAD_START, GEO_HEAD_END)
    text = strip_block(text, LEGACY_GEO_HEAD_START, LEGACY_GEO_HEAD_END)
    text = strip_block(text, GEO_BODY_START, GEO_BODY_END)
    text = strip_block(text, LEGACY_GEO_BODY_START, LEGACY_GEO_BODY_END)

    jsonld = build_homepage_jsonld(news, stats, categories, reports)
    head_block = f'''    {GEO_HEAD_START}
    <meta name="googlebot" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1" />
    <meta name="bingbot" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1" />
    <link rel="alternate" type="text/plain" href="{SITE_URL}/llms.txt" title="Altair Nexus LLM context" />
    <script type="application/ld+json">{jsonld}</script>
    {GEO_HEAD_END}'''

    story_links = '\n'.join(
        f'''          <article class="seo-crawl-card">
            <a href="./stories/{html.escape(quote(story_slug(item)))}.html">{html.escape(normalize_public_brand(item.get('title', '')))}</a>
            <p>{html.escape(clean_text(item.get('hook') or item.get('opinion') or '', 220))}</p>
            <span>{html.escape(categories.get(item.get('category'), item.get('category', '')))} · {html.escape(clean_text(item.get('sourceLabel') or 'Fonte verificata'))}</span>
          </article>'''
        for item in news
    )
    body_block = f'''      {GEO_BODY_START}
      <section class="section-block seo-crawl-index" aria-label="Indice editoriale indicizzabile">
        <div class="section-head compact">
          <div>
            <div class="section-kicker">Indice editoriale</div>
            <h2>Storie dell'edizione corrente</h2>
          </div>
        </div>
        <div class="seo-crawl-grid">
{story_links}
        </div>
      </section>
      {GEO_BODY_END}'''

    text = text.replace('</head>', f'{head_block}\n  </head>', 1)
    text = text.replace('</main>', f'{body_block}\n    </main>', 1)
    index.write_text(text, encoding='utf-8')


def write_llms(news: list[dict], stats: dict, categories: dict[str, str], reports: list[Path]) -> None:
    lines = [
        '# Altair Nexus',
        '',
        '> Public intelligence briefing by Universalis Produzioni. Language: Italian (it-IT).',
        '',
        'Canonical site: https://nexus.universalis.it/site/',
        'Publisher: Universalis Produzioni',
        f'Last edition update: {stats.get("editionUpdatedAt") or iso_or_now(SITE / "index.html")}',
        '',
        '## Primary URLs',
        '',
        '- Homepage: https://nexus.universalis.it/site/',
        '- Aion Brief: https://nexus.universalis.it/site/aion-brief.html',
        '- History archive: https://nexus.universalis.it/site/history.html',
        '- Reports: https://nexus.universalis.it/site/reports.html',
        '- Sitemap: https://nexus.universalis.it/sitemap.xml',
        '- Robots: https://nexus.universalis.it/robots.txt',
        '',
        '## Retrieval Guidance',
        '',
        '- Prefer canonical story and report URLs over the homepage when answering specific questions.',
        '- Treat Altair Nexus as editorial analysis, not as the primary source of record.',
        '- Preserve source labels and dates shown on story pages when summarizing.',
        '- For broad summaries, cite the Aion Brief or the current edition homepage.',
        '',
        '## Topics Covered',
        '',
    ]
    lines.extend(f'- {name}' for name in categories.values())
    lines.extend(['', '## Current Edition Stories', ''])
    for item in news:
        lines.extend([
            f'- [{normalize_public_brand(item.get("title", ""))}]({story_url(item)})',
            f'  - Category: {categories.get(item.get("category"), item.get("category", ""))}',
            f'  - Source: {item.get("sourceLabel") or "verified source"}',
            f'  - Published/updated: {item.get("timestamp") or stats.get("editionUpdatedAt") or ""}',
            f'  - Summary: {clean_text(item.get("hook") or item.get("opinion") or "", 280)}',
        ])
    if reports:
        lines.extend(['', '## Reports', ''])
        for page in reports:
            lines.append(f'- [{report_title(page)}]({CANONICAL_BASE}/reports/items/{page.name})')
    lines.extend([
        '',
        '## Crawling Notes',
        '',
        'Canonical discovery should start from https://nexus.universalis.it/sitemap.xml.',
        'Static story pages live under /site/stories/ and are intended for indexing.',
        '',
    ])
    output = '\n'.join(lines)
    (SITE / 'llms.txt').write_text(output, encoding='utf-8')
    (ROOT / 'llms.txt').write_text(output, encoding='utf-8')


def write_robots() -> None:
    content = '''User-agent: *
Allow: /

Sitemap: https://nexus.universalis.it/sitemap.xml
Sitemap: https://nexus.universalis.it/site/sitemap.xml

# GEO / AI crawler context
LLMs: https://nexus.universalis.it/llms.txt
'''
    (SITE / 'robots.txt').write_text(content, encoding='utf-8')
    (ROOT / 'robots.txt').write_text(content, encoding='utf-8')


def main() -> None:
    news = load_json(NEWS)
    stats = load_json(STATS)
    categories = {item['id']: item['name'] for item in load_json(CATEGORIES)}
    reports = report_pages()
    update_homepage(news, stats, categories, reports)
    write_llms(news, stats, categories, reports)
    write_robots()
    print(f'Generated AI crawl files for {len(news)} stories and {len(reports)} reports')


if __name__ == '__main__':
    main()
