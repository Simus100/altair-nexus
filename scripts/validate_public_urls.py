#!/usr/bin/env python3
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path('/root/.openclaw/workspace/aion-nexus')
SITE = ROOT / 'site'
DATA = ROOT / 'data'
SITE_ORIGIN = 'https://nexus.universalis.it'
NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attr_names = {'a': 'href', 'link': 'href', 'script': 'src', 'img': 'src'}
        attr_name = attr_names.get(tag)
        if not attr_name:
            return
        for name, value in attrs:
            if name == attr_name and value:
                self.links.append(value)


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


def filesystem_path_for_public_url(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        if f'{parsed.scheme}://{parsed.netloc}' != SITE_ORIGIN:
            return None
    path = unquote(parsed.path)
    if path in {'/robots.txt', '/sitemap.xml', '/llms.txt'}:
        path = f'/site{path}'
    if path == '/site':
        path = '/site/'
    if path.endswith('/'):
        path = f'{path}index.html'
    if not (path.startswith('/site/') or path.startswith('/data/')):
        return None
    return (ROOT / path.lstrip('/')).resolve()


def public_url_for_html_file(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == 'site/index.html':
        return f'{SITE_ORIGIN}/site/'
    return f'{SITE_ORIGIN}/{rel}'


def validate_internal_html_links(failures: list[str]) -> None:
    for page in sorted(SITE.glob('**/*.html')):
        collector = LinkCollector()
        collector.feed(page.read_text(encoding='utf-8'))
        base_url = public_url_for_html_file(page)
        for raw_link in collector.links:
            link = raw_link.strip()
            parsed = urlparse(link)
            if (
                not link
                or link.startswith('#')
                or parsed.scheme in {'mailto', 'tel', 'javascript', 'data'}
            ):
                continue
            absolute = link
            if not parsed.scheme and not parsed.netloc:
                from urllib.parse import urljoin
                absolute = urljoin(base_url, link)
            target = filesystem_path_for_public_url(absolute)
            if target and not target.is_file():
                failures.append(
                    f'HTML link has no file: {page.relative_to(ROOT)} -> {link}'
                )


def validate_seo_markers(failures: list[str]) -> None:
    required = [
        'rel="canonical"',
        'property="og:url"',
        'name="twitter:card"',
        'name="description"',
    ]
    for page in sorted(SITE.glob('**/*.html')):
        text = page.read_text(encoding='utf-8')
        missing = [marker for marker in required if marker not in text]
        if missing:
            failures.append(
                f'missing SEO markers in {page.relative_to(ROOT)}: {", ".join(missing)}'
            )


def main() -> int:
    failures = []

    for item in load_story_items():
        if not (item.get('id') or item.get('title')):
            continue
        page = SITE / 'stories' / f'{story_slug(item)}.html'
        if not page.exists():
            failures.append(f'missing story page: {page.relative_to(ROOT)}')

    sitemap = SITE / 'sitemap.xml'
    if sitemap.exists():
        for loc in ET.parse(sitemap).findall('.//sm:loc', NS):
            if not loc.text:
                continue
            target = filesystem_path_for_public_url(loc.text)
            if target and not target.is_file():
                failures.append(f'sitemap URL has no file: {loc.text}')
    else:
        failures.append(f'missing sitemap: {sitemap.relative_to(ROOT)}')

    root_sitemap = ROOT / 'sitemap.xml'
    if not root_sitemap.exists():
        failures.append('missing root sitemap alias: sitemap.xml')
    elif sitemap.exists() and root_sitemap.read_bytes() != sitemap.read_bytes():
        failures.append('root sitemap alias differs from site/sitemap.xml')

    if not (ROOT / 'robots.txt').exists():
        failures.append('missing root robots alias: robots.txt')

    validate_internal_html_links(failures)
    validate_seo_markers(failures)

    if failures:
        print('Public URL validation failed:', file=sys.stderr)
        for failure in failures[:50]:
            print(f'- {failure}', file=sys.stderr)
        if len(failures) > 50:
            print(f'- ... {len(failures) - 50} more', file=sys.stderr)
        return 1

    print('Public URL validation ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
