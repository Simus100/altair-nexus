# Altair Nexus

**Altair Nexus is the public intelligence layer of Universalis Produzioni: a static-first editorial platform that transforms fast-moving signals across AI, technology, geopolitics, markets, startups, finance, and science into a clear, navigable, high-signal briefing experience.**

It is designed for people and organizations that need more than a news feed: executives, founders, analysts, creators, operators, and decision-makers who want context, continuity, prioritization, and a readable map of what is changing.

Public site:

```text
https://nexus.universalis.it/site/
```

## Strategic Positioning

Altair Nexus is a frontier editorial intelligence product. It combines automated collection, structured analysis, static publishing, long-form AI-generated reports, persistent archives, SEO-ready public pages, and a branded editorial interface.

The product vision is simple: turn information overload into an operating surface for strategic awareness.

Instead of presenting isolated headlines, Altair Nexus organizes signals into a coherent daily and historical intelligence system. Each edition is built to answer practical questions:

- What is materially changing?
- Which signals are noise, and which deserve attention?
- How do developments connect across technology, capital, policy, infrastructure, and society?
- What should a reader track next?

## What It Delivers

Altair Nexus provides a public, lightweight, fast-loading intelligence experience with:

- a curated homepage for the current editorial briefing;
- an `Aion Brief` page for the synthetic daily reading;
- persistent historical archives by month and category;
- standalone long-form report pages;
- canonical metadata, Open Graph previews, Twitter cards, sitemap, and robots support;
- automated generation scripts for news, briefs, images, archives, story pages, report SEO, and sitemap updates;
- JSON-based data publishing for transparent, inspectable editorial outputs;
- static-first deployment, designed for speed, resilience, and low operational overhead.

## Why It Matters

The internet produces infinite updates. Strategic users need selection, framing, and memory.

Altair Nexus is built around that gap. It preserves the advantages of automation while maintaining an editorial layer that privileges relevance, continuity, and legibility. The system can refresh quickly, but its purpose is not velocity alone: it is to make change understandable.

Commercially, the project can support:

- branded intelligence portals;
- executive briefings;
- vertical research observatories;
- AI-native media products;
- public knowledge hubs;
- investor, market, policy, and technology monitoring surfaces;
- automated editorial infrastructure for organizations that need recurring, high-quality narrative intelligence.

## Public Experience

Main sections:

- `Home`: the current public intelligence briefing.
- `Aion Brief`: a focused synthesis of the day.
- `History`: a persistent archive of previous editions and stories.
- `Report`: a dedicated space for standalone analytical reports.
- `Story pages`: static, shareable pages with canonical metadata and social previews.

The interface is intentionally static-first: fast to serve, easy to cache, robust under traffic, and friendly to search engines and social sharing.

## Editorial Domains

Altair Nexus tracks high-impact domains where technological, economic, and geopolitical change converge:

- artificial intelligence and frontier model ecosystems;
- enterprise software, cloud, semiconductors, robotics, and infrastructure;
- geopolitics, regulation, security, energy, and institutional risk;
- finance, monetary policy, macro signals, and market structure;
- startups, venture capital, open-source ecosystems, and company formation;
- science, research, climate, space, and emerging technology;
- future-facing social, cultural, and strategic transformations.

## System Capabilities

- Static public frontend for speed and reliability.
- Data-driven homepage powered by structured JSON.
- Automated refresh and publishing helpers.
- Multipart historical archives for scalable static delivery.
- Dedicated scripts for story page generation and report SEO.
- Sitemap generation for public discovery.
- Local validation tools to reduce publishing errors.
- A branded editorial design system optimized for readability, sharing, and continuity.

## Architecture

```text
site/      Public frontend, static pages, assets, reports, sitemap, robots.txt
data/      Current edition data, statistics, categories, and historical archives
scripts/   Generation, validation, refresh, archive, report, and publishing helpers
docs/      Architecture notes, runbooks, quality plans, rollback guides, and roadmap
```

The project uses a pragmatic static-first architecture. Generated data and pages are committed as public artifacts, so the site can be served without a complex backend while still supporting recurring editorial automation.

## How The System Works

Altair Nexus separates the intelligence workflow into four layers:

1. **Data layer**: JSON files under `data/` hold the current edition, statistics, categories, and historical archives.
2. **Generation layer**: Python scripts under `scripts/` refresh the edition, validate data, build story pages, create the Aion Brief page, enrich report metadata, and regenerate the sitemap.
3. **Publishing layer**: static HTML, CSS, JavaScript, images, reports, story pages, `robots.txt`, and `sitemap.xml` live under `site/`.
4. **Distribution layer**: the site can be served by any static host or simple HTTP server, with no runtime database requirement.

This means the public experience is generated ahead of time. The browser loads static HTML and JSON, while the editorial automation happens before publication. That architecture keeps the product fast, inspectable, portable, and resilient.

## Data Flow

The normal publishing flow is:

```text
sources / candidates
  -> refresh edition
  -> validate JSON
  -> update current edition data
  -> archive historical items
  -> generate static story pages
  -> generate Aion Brief page
  -> enrich report SEO metadata
  -> regenerate sitemap
  -> publish static artifacts
```

The most important public data files are:

- `data/news.json`: current edition stories used by the homepage and public briefing.
- `data/stats.json`: edition metadata, update time, editorial notes, and public signals.
- `data/categories.json`: category taxonomy and presentation metadata.
- `data/history/index.json`: index of historical months and archive files.
- `data/history/*.json`: persistent monthly story archives.

The key public output files are:

- `site/index.html`: main public interface.
- `site/history.html`: historical archive interface.
- `site/aion-brief.html`: daily synthesis page.
- `site/reports.html`: report index.
- `site/reports/items/*.html`: standalone long-form reports.
- `site/stories/*.html`: generated static story pages.
- `site/sitemap.xml`: search engine discovery map.

## Script Workflow

The main local refresh entry point is:

```bash
scripts/run_nexus_refresh_local.sh
```

It runs the core generation chain:

```bash
python3 scripts/refresh_edition_stable.py
python3 scripts/generate_story_pages.py
python3 scripts/generate_aion_brief_page.py
python3 scripts/enhance_report_seo.py
python3 scripts/generate_sitemap.py
```

At the end, it prints hashes and edition metadata so the generated artifacts can be checked before publishing.

### Core Scripts

- `refresh_edition_stable.py`: refreshes the current public edition and writes the main JSON artifacts used by the site.
- `validate_nexus_json.py`: checks that the current edition data is valid before publication.
- `archive_news_monthly.py`: supports historical archive maintenance by organizing stories into monthly files.
- `generate_story_pages.py`: converts structured stories into standalone static HTML pages with canonical URLs, Open Graph metadata, Twitter cards, and JSON-LD.
- `generate_aion_brief_page.py`: builds the public `Aion Brief` synthesis page from the current edition.
- `generate_aion_brief_image.py`: generates or updates the editorial image used by the brief and social previews.
- `enhance_report_seo.py`: adds canonical metadata, social preview tags, and structured data to report pages.
- `generate_sitemap.py`: scans public pages, generated stories, and reports, then writes `site/sitemap.xml`.
- `run_nexus_brief_daily.sh`, `run_nexus_brief_image_daily.sh`, and `run_nexus_brief_page_daily.sh`: smaller daily jobs for refreshing brief-related artifacts.
- `run_nexus_refresh_orchestrated.sh` and `finalize_orchestrated_refresh.py`: orchestration helpers for more controlled refresh flows.
- `serve_nexus.py`: local serving helper for development and inspection.
- `rollback_quality_seo_20260630.sh`: rollback utility for a known quality and SEO recovery point.

### Report Publishing

Reports are designed as standalone HTML experiences under:

```text
site/reports/items/
```

After adding or editing a report, the expected flow is:

```bash
python3 scripts/enhance_report_seo.py
python3 scripts/generate_sitemap.py
```

This keeps report pages discoverable, shareable, and aligned with the rest of the public intelligence product.

### Story Page Generation

Story pages are generated from structured JSON data. The generator:

- slugifies each story into a stable static URL;
- writes a complete HTML page for each story;
- embeds SEO metadata and structured data;
- preserves source attribution and category context;
- adds related stories for internal navigation;
- uses the shared site design system and visual category classes.

The result is a set of public URLs that can be indexed, shared, archived, and linked independently from the homepage.

### Sitemap And Discovery

`generate_sitemap.py` builds the public sitemap from:

- the homepage;
- the history page;
- the Aion Brief page;
- the reports index;
- generated story pages;
- report item pages.

The sitemap uses edition timestamps where available and file modification times where appropriate. This helps search engines understand what changed and which public pages matter most.

## Useful Commands

```bash
python3 scripts/validate_nexus_json.py data/news.json data/stats.json
python3 scripts/generate_story_pages.py
python3 scripts/generate_aion_brief_page.py
python3 scripts/enhance_report_seo.py
python3 scripts/generate_sitemap.py
```

## Publishing Notes

For new report pages, place the HTML file under:

```text
site/reports/items/
```

Then run the report SEO enhancer and sitemap generator before publishing:

```bash
python3 scripts/enhance_report_seo.py
python3 scripts/generate_sitemap.py
```

Some optional automation scripts may require environment variables such as `GEMINI_API_KEY`. Never commit API keys, secrets, private credentials, or machine-local configuration files to the repository.

## Suggested GitHub Description

```text
Frontier public intelligence platform by Universalis Produzioni: AI-native briefings, strategic signal analysis, persistent archives, SEO-ready reports, and static-first editorial automation.
```
