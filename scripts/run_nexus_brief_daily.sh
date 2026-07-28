#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace/aion-nexus
python3 scripts/generate_aion_brief_page.py
if [[ -f /root/.config/aion-nexus-image.env ]]; then
  set -a
  . /root/.config/aion-nexus-image.env
  set +a
fi
DAY_OF_YEAR=$(date +%j)
if [[ -n "${GEMINI_API_KEY:-}" ]]; then
  if (( DAY_OF_YEAR % 3 == 0 )); then
    python3 scripts/generate_aion_brief_image.py
  else
    echo "Skipping Aion Brief image generation today (day ${DAY_OF_YEAR}); image refresh runs every 3 days"
  fi
else
  echo 'GEMINI_API_KEY missing; generated page only'
fi
python3 scripts/generate_story_pages.py
python3 scripts/generate_ai_crawl_files.py
python3 scripts/generate_sitemap.py
python3 scripts/validate_public_urls.py
