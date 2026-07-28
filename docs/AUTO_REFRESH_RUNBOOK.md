# Altair Nexus — Auto-refresh runbook

## Goal
Rebuild `aion-nexus/data/news.json` and `aion-nexus/data/stats.json` every hour as a fresh edition with new, source-backed, Italian-language briefing content while preserving the current frontend schema.

## Required output files
- `/root/.openclaw/workspace/aion-nexus/data/news.json`
- `/root/.openclaw/workspace/aion-nexus/data/stats.json`
- `/root/.openclaw/workspace/aion-nexus/site/stories/*.html` (generated locally from live JSON, no extra web/API calls)

## Categories
Use these category ids exactly:
- `ai`
- `tech`
- `geopolitica`
- `finanza`
- `mercati`
- `startup`
- `scienza`
- `futuro`

## News item schema
Each item must contain:
- `id`
- `category`
- `subcategory`
- `title`
- `hook`
- `body`
- `tags` (array)
- `sourceLabel`
- `sourceUrl`
- `sourceCount`
- `timestamp` (ISO 8601 with timezone)
- `featured` (boolean)
- `opinion`
- `qualityScore` (integer)
- `visual` (`ai|tech|geo|fin|markets|startup|science|future`)

## Visual map
- `ai` -> `ai`
- `tech` -> `tech`
- `geopolitica` -> `geo`
- `finanza` -> `fin`
- `mercati` -> `markets`
- `startup` -> `startup`
- `scienza` -> `science`
- `futuro` -> `future`

## Editorial rules
- Prefer 6 to 8 stories total.
- Prefer at most one story per category unless a second is clearly stronger than weaker categories.
- Prioritize AI, geopolitica, finanza, mercati, tech when strong news exists.
- Use fresh sources from the last 24 hours when possible.
- Prefer Reuters, AP, FT, Bloomberg, WSJ, Guardian, major official announcements, and other high-confidence outlets.
- Expand the basket selectively when the top-tier wire flow is thin, while keeping confidence high.
- Approved secondary sources by area:
  - AI / tech: The Verge, TechCrunch, VentureBeat, Semafor tech, official blogs/newsrooms from OpenAI, Google, Anthropic, Nvidia, Microsoft, Meta.
  - Finanza / mercati: CNBC, MarketWatch, investor-relations releases, earnings pages, ECB, Fed, IMF, BIS when directly relevant.
  - Geopolitica: BBC, Reuters World, AP World, Al Jazeera, major government / ministry / NATO / EU / UN statements.
  - Startup: Crunchbase News, Sifted, Tech.eu, verified company announcements.
  - Scienza / futuro: Nature, Science, CERN, NASA, ESA, major university and lab announcements.
- Use secondary sources to widen discovery, but verify material facts against a primary source or another high-confidence source whenever possible.
- Avoid low-confidence rumor posts.
- Write all copy in natural Italian.
- Keep titles sharp and editorial.
- Keep `hook` to 1–2 sentences.
- Keep `body` to 2 paragraphs.
- Keep `opinion` to one concise sentence.
- Set `qualityScore` roughly in the 84–97 range based on importance and confidence.
- Mark 3–4 strongest stories as `featured: true`.
- Treat each run as a new edition, but preserve the original `timestamp` for stories that remain in the edition.
- Only assign a new `timestamp` when a story is genuinely new or when a materially different source event replaces the old one.
- Never overwrite all story timestamps with the edition refresh time.
- Keep story publication time separate from edition refresh time.

## Stats rules
`stats.json` must include:
- `editionUpdatedAt`: ISO 8601 timestamp for when the edition was refreshed
- `newsGeneratedToday`: total number of items in `news.json`
- `sourcesAnalyzed`: approximate count of sources reviewed (integer)
- `topicEmerging`: 5–7 useful themes/tags
- `mostViewed`: 3 strongest story titles
- `signals`: array with:
  - `Edition: Public MVP`
  - `Cadence: Hourly auto-refresh · <local Europe/Rome time>`
  - `Mode: Italian briefing`
  - `Focus: Source-backed news`

## Update method
1. Use web search to identify key stories in the target categories.
2. For each refresh, widen queries beyond generic headlines and explicitly probe sub-themes such as product launches, funding, inference, regulation, enterprise adoption, earnings, macro guidance, shipping/energy chokepoints, major papers, and official releases.
3. Use web fetch when needed to verify core facts and improve fidelity.
4. Read the current live `news.json` first and use it as the source of original timestamps for stories that remain substantially the same.
4. Rebuild the full edition in memory first.
5. Write candidate files to temporary paths first:
   - `/root/.openclaw/workspace/aion-nexus/data/news.json.tmp`
   - `/root/.openclaw/workspace/aion-nexus/data/stats.json.tmp`
6. Serialize JSON safely only. Never hand-craft multiline JSON strings. Use a proper JSON serializer so newline characters are escaped correctly.
7. Validate both temp files by parsing them as JSON before replacing live files.
8. Only after successful validation, atomically replace live files:
   - move `news.json.tmp` -> `news.json`
   - move `stats.json.tmp` -> `stats.json`
9. After live JSON replacement succeeds, generate static story pages locally by running:
   - `python3 /root/.openclaw/workspace/aion-nexus/scripts/generate_story_pages.py`
   This step must use only the live local JSON files and must not trigger any new web/API retrieval.
10. After story pages generation, regenerate the dedicated Aion Brief page locally by running:
   - `python3 /root/.openclaw/workspace/aion-nexus/scripts/generate_aion_brief_page.py`
   This step must also use only local live JSON/stats files and must not trigger any new web/API retrieval.
11. Do not modify site layout/CSS/JS during refresh runs.
12. If web retrieval is degraded, keep quality high and prefer fewer stories rather than weak filler.
13. If validation fails at any point, leave the current live files untouched and report the failure.

## Consistency check
Before finishing:
- ensure `news.json.tmp` parses as valid JSON array
- ensure every item has all required keys
- ensure category ids and visual values match the allowed schema
- ensure `stats.json.tmp` parses as valid JSON object
- ensure `editionUpdatedAt` exists and is current for the new edition
- ensure `signals[].Cadence` matches the same refresh minute as `editionUpdatedAt`
- ensure story timestamps remain original for kept stories and only change for truly new stories
- ensure the site badge freshness can be derived from `editionUpdatedAt`, not from the newest story timestamp
- ensure the metrics card "Ultimo aggiornamento" will reflect `editionUpdatedAt`
- ensure the live `news.json` and `stats.json` on disk were actually replaced, not just the temp files
- ensure post-run file hashes or mtimes for the live files changed as expected
- ensure the live `stats.json.editionUpdatedAt` is newer than the pre-run value
, keep quality high and prefer fewer stories rather than weak filler.
11. If validation fails at any point, leave the current live files untouched and report the failure.

## Consistency check
Before finishing:
- ensure `news.json.tmp` parses as valid JSON array
- ensure every item has all required keys
- ensure category ids and visual values match the allowed schema
- ensure `stats.json.tmp` parses as valid JSON object
- ensure `editionUpdatedAt` exists and is current for the new edition
- ensure story timestamps remain original for kept stories and only change for truly new stories
- ensure the site badge freshness can be derived from `editionUpdatedAt`, not from the newest story timestamp
re `editionUpdatedAt` exists and is current for the new edition
- ensure story timestamps remain original for kept stories and only change for truly new stories
- ensure the site badge freshness can be derived from `editionUpdatedAt`, not from the newest story timestamp
