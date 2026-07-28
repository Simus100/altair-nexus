#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path('/root/.openclaw/workspace/aion-nexus')
DATA = ROOT / 'data'
TMP = ROOT / 'tmp'
NEWS = DATA / 'news.json'
STATS = DATA / 'stats.json'
HISTORY_DIR = DATA / 'history'
HISTORY_INDEX = HISTORY_DIR / 'index.json'
CATEGORIES = DATA / 'categories.json'
NEWS_TMP = DATA / 'news.json.tmp'
STATS_TMP = DATA / 'stats.json.tmp'
VALIDATOR = ROOT / 'scripts' / 'validate_nexus_json.py'
PUBLIC_URL_VALIDATOR = ROOT / 'scripts' / 'validate_public_urls.py'
GENERATE_STORIES = ROOT / 'scripts' / 'generate_story_pages.py'
GENERATE_SITEMAP = ROOT / 'scripts' / 'generate_sitemap.py'
GENERATE_BRIEF = ROOT / 'scripts' / 'generate_aion_brief_page.py'
ENHANCE_REPORT_SEO = ROOT / 'scripts' / 'enhance_report_seo.py'
GENERATE_AI_CRAWL = ROOT / 'scripts' / 'generate_ai_crawl_files.py'
BACKUP_DIR = TMP / 'orchestrated-refresh-backups'
BUNDLE_SNAPSHOTS_DIR = TMP / 'editorial-bundle-snapshots'
MONTH_KEY_RE = re.compile(r'^\d{4}-\d{2}$')


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def month_label(key: str) -> str:
    dt = datetime.strptime(key, '%Y-%m')
    month_names = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
    return f"{month_names[dt.month - 1]} {dt.year}"


def archive_month_for(item: dict) -> str:
    timestamp = item.get('timestamp')
    if not timestamp:
        fail(f'news item without timestamp cannot be archived: {item.get("id") or item.get("title") or "<unknown>"}')
    return datetime.fromisoformat(timestamp).strftime('%Y-%m')


def valid_month_key(key: str) -> bool:
    return bool(MONTH_KEY_RE.match(key))


def history_primary_key(item: dict) -> str | None:
    return item.get('id') or item.get('canonicalKey')


def history_fallback_key(item: dict) -> str:
    return '|'.join([
        item.get('category', ''),
        item.get('title', ''),
        item.get('sourceUrl', ''),
        item.get('timestamp', ''),
    ])


def history_lookup_keys(item: dict) -> list[str]:
    keys = []
    primary = history_primary_key(item)
    if primary:
        keys.append(primary)
    fallback = item.get('canonicalKey') if item.get('id') else None
    if fallback and fallback not in keys:
        keys.append(fallback)
    compound = history_fallback_key(item)
    if compound not in keys:
        keys.append(compound)
    return keys


def history_dedupe_key(item: dict) -> str:
    return history_primary_key(item) or history_fallback_key(item)


def build_category_names() -> dict[str, str]:
    categories = load_json(CATEGORIES)
    if not isinstance(categories, list):
        return {}
    return {
        item.get('id'): item.get('name')
        for item in categories
        if isinstance(item, dict) and item.get('id') and item.get('name')
    }


def load_history_months() -> dict[str, list[dict]]:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    months: dict[str, list[dict]] = {}
    for path in sorted(HISTORY_DIR.glob('*.json')):
        if path.name == 'index.json':
            continue
        payload = load_json(path)
        items = payload if isinstance(payload, list) else []
        if valid_month_key(path.stem):
            months.setdefault(path.stem, []).extend(items)
            continue
        for item in items:
            if not isinstance(item, dict) or not item.get('timestamp'):
                continue
            months.setdefault(archive_month_for(item), []).append(item)
    return months


def merge_history_item(live_item: dict, existing_item: dict | None, category_names: dict[str, str], archive_month: str) -> dict:
    archived = dict(existing_item or {})
    archived.update(live_item)
    archived['archivedMonth'] = archive_month
    archived['archivedCategoryName'] = (
        category_names.get(archived.get('category'))
        or archived.get('archivedCategoryName')
        or archived.get('category')
    )
    archived['firstSeenAt'] = (
        (existing_item or {}).get('firstSeenAt')
        or archived.get('firstSeenAt')
        or archived.get('timestamp')
    )
    return archived


def archive_published_news(news: list[dict]) -> dict:
    category_names = build_category_names()
    months = load_history_months()
    touched = set()
    added = 0
    updated = 0

    for live_item in news:
        target_month = archive_month_for(live_item)
        touched.add(target_month)
        month_items = months.setdefault(target_month, [])
        lookup_keys = set(history_lookup_keys(live_item))
        existing_item = None

        for month_key, items in months.items():
            kept_items = []
            for entry in items:
                entry_keys = set(history_lookup_keys(entry))
                if lookup_keys.isdisjoint(entry_keys):
                    kept_items.append(entry)
                    continue
                if existing_item is None:
                    existing_item = entry
                if month_key != target_month:
                    touched.add(month_key)
            months[month_key] = kept_items if month_key != target_month else [entry for entry in kept_items]

        merged = merge_history_item(live_item, existing_item, category_names, target_month)
        months[target_month].append(merged)
        if existing_item is None:
            added += 1
        else:
            updated += 1

    index_months = []
    story_to_month = {}
    for month_key, items in months.items():
        unique_items = []
        seen = set()
        for entry in items:
            dedupe_key = history_dedupe_key(entry)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            unique_items.append(entry)
        unique_items.sort(key=lambda entry: entry.get('timestamp', ''), reverse=True)
        months[month_key] = unique_items
        save_json(HISTORY_DIR / f'{month_key}.json', unique_items)
        for entry in unique_items:
            story_id = entry.get('id')
            if story_id:
                story_to_month[story_id] = month_key
        index_months.append({
            'key': month_key,
            'label': month_label(month_key),
            'file': f'../../data/history/{month_key}.json',
            'count': len(unique_items),
        })

    index_months.sort(key=lambda entry: entry['key'], reverse=True)
    save_json(HISTORY_INDEX, {'months': index_months, 'storyToMonth': story_to_month})
    return {
        'touchedMonths': sorted(touched),
        'added': added,
        'updated': updated,
        'index': str(HISTORY_INDEX),
    }


def normalize_bundle(bundle_path: Path) -> tuple[list, dict]:
    bundle = load_json(bundle_path)
    if not isinstance(bundle, dict):
        fail(f'bundle must be a JSON object: {bundle_path}')
    if 'news' not in bundle or 'stats' not in bundle:
        fail(f'bundle must contain top-level keys "news" and "stats": {bundle_path}')
    news = bundle['news']
    stats = bundle['stats']
    if not isinstance(news, list):
        fail(f'bundle.news must be a JSON array: {bundle_path}')
    if not isinstance(stats, dict):
        fail(f'bundle.stats must be a JSON object: {bundle_path}')
    return news, stats


def ensure_stats_alignment(news: list, stats: dict) -> None:
    if not stats.get('editionUpdatedAt'):
        fail('stats.editionUpdatedAt is required')
    if stats.get('newsGeneratedToday') != len(news):
        fail(f'stats.newsGeneratedToday must equal len(news): {stats.get("newsGeneratedToday")} != {len(news)}')


def make_backup() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
    target = BACKUP_DIR / stamp
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(NEWS, target / 'news.json')
    shutil.copy2(STATS, target / 'stats.json')
    return target


def restore_live_data(backup_dir: Path) -> None:
    shutil.copy2(backup_dir / 'news.json', NEWS)
    shutil.copy2(backup_dir / 'stats.json', STATS)


def run_checked(cmd: list[str]) -> None:
    subprocess.check_call(cmd)


def regenerate_public_site(skip_brief_page: bool) -> None:
    run_checked(['python3', str(GENERATE_STORIES)])
    if ENHANCE_REPORT_SEO.exists():
        run_checked(['python3', str(ENHANCE_REPORT_SEO)])
    if GENERATE_BRIEF.exists() and not skip_brief_page:
        run_checked(['python3', str(GENERATE_BRIEF)])
    if GENERATE_AI_CRAWL.exists():
        run_checked(['python3', str(GENERATE_AI_CRAWL)])
    run_checked(['python3', str(GENERATE_SITEMAP)])
    if PUBLIC_URL_VALIDATOR.exists():
        run_checked(['python3', str(PUBLIC_URL_VALIDATOR)])


def snapshot_bundle(bundle_path: Path) -> Path:
    BUNDLE_SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
    target = BUNDLE_SNAPSHOTS_DIR / f'{stamp}-{bundle_path.name}'
    shutil.copy2(bundle_path, target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate and publish an editorial JSON bundle prepared by OpenClaw/Aion.')
    parser.add_argument('--bundle', required=True, help='Path to editorial bundle JSON with top-level keys: news, stats')
    parser.add_argument('--dry-run', action='store_true', help='Validate and write preview files only; do not publish live data')
    parser.add_argument('--skip-brief-page', action='store_true', help='Do not regenerate site/aion-brief.html even if the script exists')
    args = parser.parse_args()

    bundle_path = Path(args.bundle)
    if not bundle_path.is_absolute():
        bundle_path = (ROOT / bundle_path).resolve()
    if not bundle_path.exists():
        fail(f'bundle not found: {bundle_path}')

    news, stats = normalize_bundle(bundle_path)
    ensure_stats_alignment(news, stats)

    frozen_bundle_path = snapshot_bundle(bundle_path)

    save_json(NEWS_TMP, news)
    save_json(STATS_TMP, stats)

    run_checked(['python3', str(VALIDATOR), str(NEWS_TMP), str(STATS_TMP)])

    preview_dir = TMP / 'refresh-preview'
    preview_dir.mkdir(parents=True, exist_ok=True)
    preview_news = preview_dir / 'news.from-orchestrated.json'
    preview_stats = preview_dir / 'stats.from-orchestrated.json'
    save_json(preview_news, news)
    save_json(preview_stats, stats)

    if args.dry_run:
        if NEWS_TMP.exists():
            NEWS_TMP.unlink()
        if STATS_TMP.exists():
            STATS_TMP.unlink()
        print(json.dumps({
            'status': 'dry-run-ok',
            'bundle': str(bundle_path),
            'frozenBundle': str(frozen_bundle_path),
            'previewNews': str(preview_news),
            'previewStats': str(preview_stats),
            'count': len(news),
            'editionUpdatedAt': stats.get('editionUpdatedAt'),
        }, ensure_ascii=False, indent=2))
        return

    backup_dir = make_backup()
    os.replace(NEWS_TMP, NEWS)
    os.replace(STATS_TMP, STATS)

    try:
        history_result = archive_published_news(news)
        regenerate_public_site(args.skip_brief_page)
    except Exception:
        restore_live_data(backup_dir)
        try:
            regenerate_public_site(args.skip_brief_page)
        except Exception as restore_error:
            print(f'rollback regeneration failed: {restore_error}', file=sys.stderr)
        raise

    live_news = load_json(NEWS)
    live_stats = load_json(STATS)
    print(json.dumps({
        'status': 'published',
        'bundle': str(bundle_path),
        'frozenBundle': str(frozen_bundle_path),
        'backupDir': str(backup_dir),
        'count': len(live_news),
        'editionUpdatedAt': live_stats.get('editionUpdatedAt'),
        'history': history_result,
        'generated': {
            'storyPages': str(ROOT / 'site' / 'stories'),
            'reportSeo': str(ROOT / 'site' / 'reports') if ENHANCE_REPORT_SEO.exists() else None,
            'sitemap': str(ROOT / 'site' / 'sitemap.xml'),
            'aionBriefPage': str(ROOT / 'site' / 'aion-brief.html') if GENERATE_BRIEF.exists() and not args.skip_brief_page else None,
        }
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
