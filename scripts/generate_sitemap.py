#!/usr/bin/env python3
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path('/root/.openclaw/workspace/aion-nexus')
SITE = ROOT / 'site'
DATA = ROOT / 'data'
SITE_URL = 'https://nexus.universalis.it/site'
ROOT_SITEMAP = ROOT / 'sitemap.xml'
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', NS)


def iso_or_now(path: Path) -> str:
    dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).astimezone()
    return dt.isoformat(timespec='seconds')


def story_slug(item: dict) -> str:
    value = str(item.get('id') or item.get('title') or 'story').lower().strip()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'story'


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

    add_many(json.loads((DATA / 'news.json').read_text(encoding='utf-8')))
    history_dir = DATA / 'history'
    if history_dir.exists():
        for path in sorted(history_dir.glob('*.json')):
            if path.name == 'index.json':
                continue
            add_many(json.loads(path.read_text(encoding='utf-8')))
    return items


def main():
    news = json.loads((DATA / 'news.json').read_text(encoding='utf-8'))
    stats = json.loads((DATA / 'stats.json').read_text(encoding='utf-8'))
    story_dir = SITE / 'stories'
    report_dir = SITE / 'reports' / 'items'
    report_pages = sorted(report_dir.glob('*.html'))
    live_story_pages = {f'{story_slug(item)}.html' for item in news if item.get('id') or item.get('title')}
    story_items = {
        f'{story_slug(item)}.html': item
        for item in load_story_items()
        if item.get('id') or item.get('title')
    }

    root = ET.Element(f'{{{NS}}}urlset')

    def add_url(loc: str, lastmod: str, changefreq: str, priority: str):
        url = ET.SubElement(root, f'{{{NS}}}url')
        ET.SubElement(url, f'{{{NS}}}loc').text = loc
        ET.SubElement(url, f'{{{NS}}}lastmod').text = lastmod
        ET.SubElement(url, f'{{{NS}}}changefreq').text = changefreq
        ET.SubElement(url, f'{{{NS}}}priority').text = priority

    edition_updated = stats.get('editionUpdatedAt') or iso_or_now(SITE / 'index.html')
    add_url(f'{SITE_URL}/', edition_updated, 'hourly', '1.0')
    llms = SITE / 'llms.txt'
    if llms.exists():
        add_url('https://nexus.universalis.it/llms.txt', iso_or_now(llms), 'weekly', '0.6')
    add_url(f'{SITE_URL}/history.html', iso_or_now(SITE / 'history.html'), 'daily', '0.7')
    add_url(f'{SITE_URL}/aion-brief.html', iso_or_now(SITE / 'aion-brief.html'), 'daily', '0.8')
    reports_index = SITE / 'reports.html'
    if reports_index.exists():
        add_url(f'{SITE_URL}/reports.html', iso_or_now(reports_index), 'daily', '0.86')

    missing_story_pages = []

    # Include canonical story pages derived from live news and the history
    # archive. Old static files can keep resolving for shared links, but they
    # should not be advertised to crawlers if no JSON record owns them.
    for page_name, item in sorted(story_items.items()):
        page = story_dir / page_name
        if not page.exists():
            missing_story_pages.append(page.relative_to(ROOT).as_posix())
            continue
        lastmod = (item or {}).get('timestamp') or iso_or_now(page)
        priority = '0.76' if page_name in live_story_pages and item.get('featured') else '0.72'
        add_url(f'{SITE_URL}/stories/{page_name}', lastmod, 'weekly', priority)

    if missing_story_pages:
        preview = '\n'.join(f'- {page}' for page in missing_story_pages[:30])
        suffix = f'\n- ... {len(missing_story_pages) - 30} more' if len(missing_story_pages) > 30 else ''
        raise SystemExit(f'Sitemap generation refused: missing generated story pages:\n{preview}{suffix}')

    # Include every published report automatically. New report HTML files placed
    # under site/reports/items/ are picked up by the next refresh/sitemap run.
    for page in report_pages:
        add_url(f'{SITE_URL}/reports/items/{page.name}', iso_or_now(page), 'weekly', '0.82')

    out = SITE / 'sitemap.xml'
    ET.ElementTree(root).write(out, encoding='utf-8', xml_declaration=True)
    ROOT_SITEMAP.write_bytes(out.read_bytes())
    print(f'Generated {out} and {ROOT_SITEMAP} with {len(root.findall(f"{{{NS}}}url"))} URLs')


if __name__ == '__main__':
    main()
