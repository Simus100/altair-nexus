# Altair Nexus MVP Architecture

## Why static-first
A static-first MVP reduces complexity while preserving a clean path to automation.

## Initial modules

### 1. Presentation layer
`site/`
- responsive landing page
- category grid
- in-page story expansion
- dashboard widgets

### 2. Content model
`data/`
- `categories.json`
- `news.json`
- later: `stats.json`, `sources.json`

### 3. Rendering logic
`site/assets/app.js`
- loads structured JSON
- renders homepage sections
- handles card expansion
- updates dashboard blocks

### 4. Future automation layer
Later modules:
- ingestion
- source ranking
- deduplication
- scoring
- summarization
- publishing

## Core MVP schema
Each news item should support:
- id
- title
- hook
- body
- category
- subcategory
- tags[]
- sourceLabel
- sourceCount
- timestamp
- featured
- opinion
- image
- qualityScore

## Expansion path
Static JSON -> generated JSON -> DB-backed content -> admin-controlled system.
