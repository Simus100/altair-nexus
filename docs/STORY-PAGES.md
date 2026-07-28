# Altair Nexus — Story pages statiche

Data: 2026-03-26

## Obiettivo
Generare pagine statiche per singola notizia, così i link condivisi hanno un URL reale con metadata propri, senza aumentare le richieste API.

## Principio
Nessuna nuova chiamata web o API durante la generazione delle pagine story.

Le pagine vengono costruite **solo** a partire da:
- `data/news.json`
- `data/categories.json`

## Script
Generatore locale:
- `scripts/generate_story_pages.py`

Output:
- `site/stories/*.html`

## Benefici
- anteprime link migliori per story specifiche
- base più solida per SEO story-level
- nessun incremento del costo di ricerca o refresh editoriale
- architettura coerente con il modello static-first

## Come funziona
1. il refresh editoriale continua ad aggiornare `news.json` e `stats.json`
2. poi, localmente, si esegue lo script di generazione story pages
3. lo script crea una pagina HTML per ogni item corrente in `news.json`
4. rimuove eventuali pagine story obsolete non più presenti nell'edizione live

## Comando manuale
```bash
cd /root/.openclaw/workspace/aion-nexus
python3 scripts/generate_story_pages.py
```

## Impatto API
Praticamente nullo oltre al refresh esistente.

Lo script:
- non chiama web search
- non chiama API esterne
- non rigenera contenuto editoriale
- trasforma solo i dati già presenti in HTML statico

## Rollback
Le story pages stanno in una cartella dedicata:
- `site/stories/`

Rollback semplice:
- ripristinare da backup
- oppure rimuovere `site/stories/` e tornare alla condivisione via query param

## Estensione futura consigliata
Integrare lo script come ultimo step del refresh, dopo la validazione dei JSON live, così le story pages restano sempre coerenti con l'edizione corrente.
