#!/usr/bin/env python3
import json
import pathlib
import re
from datetime import datetime

ROOT = pathlib.Path('/root/.openclaw/workspace/aion-nexus')
NEWS_PATH = ROOT / 'data' / 'news.json'
CATEGORIES_PATH = ROOT / 'data' / 'categories.json'
HISTORY_DIR = ROOT / 'data' / 'history'
INDEX_PATH = HISTORY_DIR / 'index.json'
MONTH_KEY_RE = re.compile(r'^\d{4}-\d{2}$')


def load_json(path, default=None):
    if default is None:
        default = []
    if not path.exists():
        return default
    return json.loads(path.read_text())


def dump_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')


def month_key(ts):
    dt = datetime.fromisoformat(ts)
    return dt.strftime('%Y-%m')


def item_key(item):
    return item.get('id') or '|'.join([
        item.get('category', ''),
        item.get('title', ''),
        item.get('sourceUrl', ''),
        item.get('timestamp', ''),
    ])


def month_label(key):
    dt = datetime.strptime(key, '%Y-%m')
    month_names = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
    return f"{month_names[dt.month - 1]} {dt.year}"


def valid_month_key(key):
    return bool(MONTH_KEY_RE.match(key))


def main():
    news = load_json(NEWS_PATH, [])
    categories = load_json(CATEGORIES_PATH, [])
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    touched = set()
    for item in news:
        ts = item.get('timestamp')
        if not ts:
            continue
        key = month_key(ts)
        touched.add(key)
        month_path = HISTORY_DIR / f'{key}.json'
        current = load_json(month_path, [])
        existing = {item_key(entry): entry for entry in current}
        archived = dict(item)
        archived['archivedMonth'] = key
        archived['archivedCategoryName'] = next((c.get('name') for c in categories if c.get('id') == item.get('category')), item.get('category'))
        k = item_key(archived)
        if k in existing:
            prev = existing[k]
            archived['firstSeenAt'] = prev.get('firstSeenAt', archived.get('timestamp'))
        else:
            archived['firstSeenAt'] = archived.get('timestamp')
        existing[k] = archived
        merged = list(existing.values())
        merged.sort(key=lambda entry: entry.get('timestamp', ''), reverse=True)
        dump_json(month_path, merged)

    months = []
    story_to_month = {}
    for path in sorted(HISTORY_DIR.glob('*.json')):
        if path.name == 'index.json':
            continue
        key = path.stem
        if not valid_month_key(key):
            continue
        items = load_json(path, [])
        for entry in items:
            story_id = entry.get('id')
            if story_id:
                story_to_month[story_id] = key
        months.append({
            'key': key,
            'label': month_label(key),
            'file': f'../../data/history/{path.name}',
            'count': len(items),
        })
    months.sort(key=lambda entry: entry['key'], reverse=True)
    dump_json(INDEX_PATH, {'months': months, 'storyToMonth': story_to_month})
    print(json.dumps({'index': str(INDEX_PATH), 'months': len(months), 'touched': sorted(touched)}))


if __name__ == '__main__':
    main()
