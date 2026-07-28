# Altair Nexus — GitHub Publish Guide

Questa guida serve a pubblicare **tutto il codice reperibile** del progetto Altair Nexus su GitHub, senza perdere lo stato attuale.

## Obiettivo
Pubblicare su GitHub il progetto presente in:

- `/root/.openclaw/workspace/aion-nexus`

con dentro almeno:
- frontend statico (`site/`)
- dati (`data/`)
- documentazione (`docs/`)
- script (`scripts/`)
- README

## Struttura attuale del progetto
File/cartelle rilevanti da includere nel repository:

- `README.md`
- `data/categories.json`
- `data/news.json`
- `data/stats.json`
- `site/index.html`
- `site/assets/app.js`
- `site/assets/styles.css`
- `site/assets/debug.js`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/AUTO_REFRESH_RUNBOOK.md`
- `docs/UI-REDESIGN-TIMELINE-2026-03-17.md`
- `scripts/validate_nexus_json.py`
- `scripts/build_refresh_20260317_2205.py`

## Prima di pubblicare: cosa NON caricare per default
Valuta con attenzione se escludere:
- `backups/`
- `tmp/`
- file di memoria personali del workspace OpenClaw
- file non appartenenti davvero al progetto

Il repository GitHub dovrebbe contenere **solo il progetto Altair Nexus**, non l'intero workspace personale.

## Verifica locale del progetto
Dal root del progetto:

```bash
cd /root/.openclaw/workspace/aion-nexus
python3 -m http.server 4173
```

Apri:

```text
http://localhost:4173/site/
```

## Creazione repository su GitHub
### Opzione web
1. Vai su GitHub
2. Clicca **New repository**
3. Nome consigliato: `altair-nexus`
4. Scegli visibilità: `Private` o `Public`
5. Non aggiungere README/.gitignore/license se vuoi spingere lo stato locale senza conflitti iniziali
6. Crea il repository

## Collegamento del repository locale al remoto GitHub
Dentro il progetto:

```bash
cd /root/.openclaw/workspace/aion-nexus
git remote add origin git@github.com:TUO-USERNAME/altair-nexus.git
```

Oppure HTTPS:

```bash
git remote add origin https://github.com/TUO-USERNAME/altair-nexus.git
```

Verifica:

```bash
git remote -v
```

## Controlla stato Git prima del push
```bash
git status
```

Se ci sono modifiche locali che vuoi includere, fai commit.

## Commit dello stato corrente
```bash
git add README.md data site docs scripts
git commit -m "Snapshot current Altair Nexus state"
```

Se vuoi includere tutto il progetto tracciato:

```bash
git add .
git commit -m "Publish Altair Nexus current project state"
```

## Push iniziale su GitHub
Se il branch locale è `master`:

```bash
git push -u origin master
```

Se preferisci `main`:

```bash
git branch -M main
git push -u origin main
```

## Se vuoi partire da backup invece che dalla working tree attuale
Puoi ricostruire il repository dal bundle backup:

```bash
git clone /root/.openclaw/workspace/backups/aion-nexus-full-20260319-210013/repo.bundle aion-nexus-restored
cd aion-nexus-restored
git remote add origin git@github.com:TUO-USERNAME/altair-nexus.git
git push -u origin master
```

Se vuoi riprodurre anche le modifiche locali catturate dal backup:

```bash
git apply /root/.openclaw/workspace/backups/aion-nexus-full-20260319-210013/working-tree.diff
git add .
git commit -m "Reapply local snapshot from restore point"
git push
```

## .gitignore consigliato
Esempio minimo:

```gitignore
.DS_Store
Thumbs.db
*.log
.tmp
*.tmp
__pycache__/
```

Se nel progetto nasceranno output temporanei, aggiungili qui.

## Checklist finale
- repository GitHub creato
- remote `origin` configurato
- file di progetto presenti
- eventuali file sensibili esclusi
- commit effettuato
- push completato
- pagina GitHub verificata

## Nota pratica
Dato che il progetto vive dentro un workspace OpenClaw più ampio, il consiglio giusto è mantenere il repository GitHub limitato alla cartella operativa del progetto e non al workspace intero. La directory locale può restare `aion-nexus/` per compatibilità con service e automazioni, anche se il repository pubblico si chiama `altair-nexus`.
