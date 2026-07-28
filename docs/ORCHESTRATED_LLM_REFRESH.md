# Altair Nexus — Orchestrated LLM refresh

## Obiettivo
Tenere stabile il discovery automatico già esistente, ma spostare la scrittura editoriale finale su Aion/OpenClaw in chat, senza invocare API LLM esterne da Python.

## Architettura proposta

### 1) Discovery automatico invariato
Comando:

```bash
bash scripts/run_nexus_refresh_orchestrated.sh
```

Questo step:
- esegue `python3 scripts/refresh_edition_stable.py --candidates-only`
- genera `tmp/refresh-candidates.json`
- prepara `tmp/editorial-handoff/` con:
  - `refresh-candidates.json`
  - `live-news.snapshot.json`
  - `live-stats.snapshot.json`
  - `README.md`

### 2) Editorial generation in chat
Aion/OpenClaw legge i candidati e produce un bundle JSON editoriale completo:

```json
{
  "news": [ ... ],
  "stats": { ... }
}
```

Bundle consigliato:

- `tmp/editorial-bundle.json`

Questo è il punto in cui interviene il loop umano/agente. Non esiste in repo una chiamata Python diretta al modello di chat, e **non viene simulata**.

### 3) Finalizzazione / pubblicazione
Helper dedicato:

```bash
python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json --dry-run
python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json
```

Il finalizer:
- legge il bundle
- valida struttura `news`/`stats`
- esegue `scripts/validate_nexus_json.py`
- congela una copia snapshot del bundle in `tmp/editorial-bundle-snapshots/`
- in dry-run scrive preview in `tmp/refresh-preview/`
- in publish:
  - crea backup in `tmp/orchestrated-refresh-backups/<timestamp>/`
  - aggiorna `data/news.json`
  - aggiorna `data/stats.json`
  - archivia ogni item pubblicato nel mese corretto sotto `data/history/YYYY-MM.json`
  - aggiorna `data/history/index.json` con conteggi coerenti
  - se un item esiste già in history, lo aggiorna senza perdere metadati utili come `firstSeenAt`, `archivedMonth`, `archivedCategoryName`
  - evita duplicati inutili usando prima `id` e in fallback `canonicalKey`
  - rigenera `site/stories/*.html`
  - rigenera `site/sitemap.xml`
  - rigenera anche `site/aion-brief.html` se lo script locale è presente

## Audit del percorso esistente

### `scripts/refresh_edition_stable.py --candidates-only`
Già presente e utilizzabile.
- Discovery e dedup restano in Python
- In modalità `--candidates-only` salva solo candidati grezzi in `tmp/refresh-candidates.json`
- Non tocca i file live

### `scripts/validate_nexus_json.py`
Già presente.
Controlla:
- shape base di `news.json` e `stats.json`
- campi obbligatori per ogni news item
- category ids ammessi
- visual ids ammessi
- warning su body troppo corti / duplicati / sourceUrl Google News

### `scripts/generate_story_pages.py`
Già presente.
- Legge `data/news.json`
- Rigenera le story pages statiche in `site/stories/`

### `scripts/generate_sitemap.py`
Già presente.
- Legge `data/news.json` + `data/stats.json`
- Rigenera `site/sitemap.xml`

## Comandi pratici

### Avvio handoff orchestrato
```bash
bash scripts/run_nexus_refresh_orchestrated.sh
```

### Validazione bundle senza pubblicare
```bash
python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json --dry-run
```

### Pubblicazione live
```bash
python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json
```

### Se vuoi saltare la rigenerazione della brief page
```bash
python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json --skip-brief-page
```

## Limiti dichiarati
- La discovery può essere automatizzata.
- La pubblicazione finale può essere resa sicura e ripetibile.
- **La generazione editoriale del bundle richiede ancora l'agente/LLM in loop** oppure un umano che prepari il JSON.
- Gli script locali **non** chiamano il modello di chat direttamente.
- Quindi il flusso fully automatico end-to-end non esiste ancora senza un orchestratore esterno che faccia passare il bundle dalla chat al filesystem.

## Rischi residui
- Il validator attuale controlla bene la shape, ma non la qualità editoriale reale.
- Un bundle formalmente valido può comunque essere debole, duplicato o troppo vicino al testo sorgente.
- Se l'agente produce `newsGeneratedToday` incoerente con `len(news)`, il finalizer blocca la publish.
- Se la chat non salva correttamente il bundle su disco, il flusso si ferma prima della pubblicazione: è voluto, per sicurezza.

## Principi editoriali e di history
- Il live (`data/news.json`) è un'edizione corrente selettiva: può tenere storie forti già presenti e aggiungere nuove storie quando meritano davvero di entrare.
- I pezzi riusati devono mantenere il loro timestamp originale.
- La history (`data/history/*.json`) è da trattare come memoria editoriale di lungo periodo: l'idea è che gli articoli restino disponibili lì nel tempo.
- La pulizia deve essere conservativa: intervenire solo su cloni evidenti, articoli malriusciti o record palesemente sporchi (es. body con navigation noise, sourceUrl Google News non risolto, duplicati quasi identici).
- Il publish orchestrato ora aggiorna automaticamente la history in modalità conservativa: archivia o aggiorna i record pubblicati, ma non fa purge aggressive della memoria editoriale.
- Non fare purge aggressive della history senza audit esplicito.

## Stato desiderato del workflow
Minimo e praticabile:
1. Python scopre candidati
2. Aion/OpenClaw scrive il bundle editoriale
3. Finalizer valida e pubblica
4. Eventuali pulizie sulla history avvengono come manutenzione separata e conservativa

Questo lascia stabili i job automatici di discovery e la compatibilità con i file live (`data/news.json`, `data/stats.json`, story pages, sitemap), evitando overengineering.
