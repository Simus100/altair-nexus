# Altair Nexus — Rollback Guide

## Obiettivo
Ripristinare rapidamente il progetto in caso di regressioni durante lavori su frontend, contenuti o integrazione social.

## Principio
Prima di ogni modifica strutturale:
1. creare snapshot
2. fare modifiche piccole
3. testare localmente
4. solo dopo considerare il deploy/pubblicazione

## Snapshot disponibile
Snapshot creato prima dell'analisi social:
- `/root/.openclaw/workspace/backups/aion-nexus-social-analysis-20260326-175229.tar.gz`

## Ripristino completo da archivio
Esempio:

```bash
cd /root/.openclaw/workspace
mv aion-nexus aion-nexus.broken.$(date +%Y%m%d-%H%M%S)
mkdir -p aion-nexus
# estrai nella workspace root, perché l'archivio contiene già la cartella aion-nexus
rm -rf aion-nexus
tar -xzf /root/.openclaw/workspace/backups/aion-nexus-social-analysis-20260326-175229.tar.gz -C /root/.openclaw/workspace
```

## Ripristino selettivo frontend
Se il problema è solo nel frontend, conviene ripristinare solo:
- `site/index.html`
- `site/history.html`
- `site/assets/app.js`
- `site/assets/styles.css`
- eventuali nuovi asset social

Approccio consigliato:
1. estrarre il backup in una cartella temporanea
2. confrontare i file
3. copiare solo quelli necessari

Esempio:

```bash
cd /root/.openclaw/workspace
mkdir -p tmp/restore-aion-nexus
cd tmp/restore-aion-nexus
tar -xzf /root/.openclaw/workspace/backups/aion-nexus-social-analysis-20260326-175229.tar.gz
```

Poi confrontare:

```bash
diff -ru /root/.openclaw/workspace/aion-nexus/site ./aion-nexus/site
```

## Ripristino selettivo dati
Se il problema riguarda i contenuti JSON:
- `data/news.json`
- `data/stats.json`
- `data/categories.json`

Ripristinare solo questi file e poi validare:

```bash
python3 /root/.openclaw/workspace/aion-nexus/scripts/validate_nexus_json.py \
  /root/.openclaw/workspace/aion-nexus/data/news.json \
  /root/.openclaw/workspace/aion-nexus/data/stats.json
```

## Test locale post-ripristino
Dal root del progetto:

```bash
cd /root/.openclaw/workspace/aion-nexus
python3 -m http.server 4173
```

Poi aprire:
- `http://localhost:4173/site/`
- `http://localhost:4173/site/history.html`

## Checklist rapida dopo rollback
- homepage si apre
- latest feed visibile
- focus panel funziona
- history page si apre
- JSON validi
- nessun errore critico in console

## Buona pratica
Per i prossimi interventi, creare snapshot nominati per milestone, ad esempio:
- `aion-nexus-pre-social-meta-<timestamp>.tar.gz`
- `aion-nexus-pre-deep-link-<timestamp>.tar.gz`
- `aion-nexus-pre-social-drafts-<timestamp>.tar.gz`
