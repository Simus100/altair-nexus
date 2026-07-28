#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace/aion-nexus
python3 scripts/refresh_edition_stable.py
python3 scripts/generate_story_pages.py
python3 scripts/generate_aion_brief_page.py
python3 scripts/enhance_report_seo.py
python3 scripts/generate_ai_crawl_files.py
python3 scripts/generate_sitemap.py
python3 scripts/validate_public_urls.py
python3 - <<'PY'
import json, hashlib
from pathlib import Path
news=Path('data/news.json').read_bytes()
stats=Path('data/stats.json').read_bytes()
sitemap=Path('site/sitemap.xml').read_bytes()
obj=json.loads(stats)
print('news_sha256', hashlib.sha256(news).hexdigest())
print('stats_sha256', hashlib.sha256(stats).hexdigest())
print('sitemap_sha256', hashlib.sha256(sitemap).hexdigest())
print('editionUpdatedAt', obj.get('editionUpdatedAt'))
print('count', len(json.loads(news)))
PY
