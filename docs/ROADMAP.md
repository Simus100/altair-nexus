# Altair Nexus Roadmap

Altair Nexus deve crescere come prodotto editoriale leggero: prima una homepage forte e pubblicabile, poi automazione, poi strumenti interni.

## Current state
- static-first MVP in `site/`
- homepage JSON-driven
- real, source-backed stories visible on the homepage
- in-page story focus instead of dead prototype cards
- public metrics block and category radar

## Phase 1 — Public homepage hardening
**Goal:** make the current front page feel publishable.

### Tasks
- [x] Replace internal/prototype copy with public-facing editorial language
- [x] Surface real news directly in the hero, live feed, top stories, and highlights
- [x] Add clickable source links in the focus panel
- [x] Improve information hierarchy: hero lead, latest feed, top stories, category radar
- [ ] Add favicon, social preview image, and basic metadata polish
- [ ] Add a "last updated" stamp sourced from content data
- [ ] Add empty-state handling for failed or missing JSON payloads

## Phase 2 — Content model and sourcing
**Goal:** stabilize how stories are stored before adding automation.

### Tasks
- [ ] Extend `news.json` schema with optional fields: `region`, `priority`, `summaryBullets`, `canonicalSource`, `secondarySources`
- [ ] Split content into daily files (example: `data/daily/2026-03-16.json`) plus a generated homepage bundle
- [ ] Add a tiny normalization script to validate required fields and sort stories
- [ ] Define editorial rules: what qualifies as top story, highlight, or radar-only item
- [ ] Track source freshness and reject stale items automatically

## Phase 3 — Lightweight generation pipeline
**Goal:** automate collection without turning the MVP into a backend swamp.

### Tasks
- [ ] Create `scripts/build-homepage-data.js` to merge/sort story files into a single public bundle
- [ ] Create `scripts/research-digest.js` to fetch candidate headlines from trusted sources
- [ ] Add a manual review step before publication
- [ ] Save generated outputs to `data/generated/` for auditability
- [ ] Define safe fallback behavior when research fails or sources are incomplete

## Phase 4 — Public product polish
**Goal:** make the site feel like a product, not a concept.

### Tasks
- [ ] Add story pages or modal/article routing only if homepage density becomes limiting
- [ ] Improve typography scale and spacing rhythm across sections
- [ ] Add search/filter by category and tag
- [ ] Add responsive image/art direction for hero and cards
- [ ] Add analytics hooks for most-opened and most-clicked stories
- [ ] Add SEO basics: sitemap, canonical tags, Open Graph, robots

## Phase 5 — Internal operations layer
**Goal:** introduce tooling only when editorial flow justifies it.

### Tasks
- [ ] Internal queue for candidate stories
- [ ] Approve/reject UI for homepage publication
- [ ] Source control panel and source health checks
- [ ] Regeneration log with timestamps and failures
- [ ] Scheduled runs during the editorial window

## Suggested implementation order
1. polish metadata and resilience on the current homepage
2. stabilize data schema and add validation/build scripts
3. separate raw daily content from generated public bundle
4. automate research with human review in the loop
5. add analytics and, only later, internal admin tooling

## Non-goals for the MVP
- full CMS
- user accounts
- complex backend
- real-time websockets
- heavy frameworks without a clear editorial need
