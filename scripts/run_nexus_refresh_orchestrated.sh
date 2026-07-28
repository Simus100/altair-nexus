#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace/aion-nexus

python3 scripts/refresh_edition_stable.py --candidates-only

handoff_dir="tmp/editorial-handoff"
mkdir -p "$handoff_dir"
cp tmp/refresh-candidates.json "$handoff_dir/refresh-candidates.json"
cp data/news.json "$handoff_dir/live-news.snapshot.json"
cp data/stats.json "$handoff_dir/live-stats.snapshot.json"

cat > "$handoff_dir/README.md" <<'EOF'
# Altair Nexus — orchestrated refresh handoff

Questo handoff serve quando la selezione/discovery dei candidati è automatica, ma la scrittura editoriale finale viene fatta da Aion/OpenClaw in chat.

## File disponibili
- `refresh-candidates.json` → candidati grezzi appena prodotti dal motore Python
- `live-news.snapshot.json` → snapshot dell'edizione live corrente
- `live-stats.snapshot.json` → snapshot delle stats live correnti

## Cosa deve fare l'agente
1. Leggere `refresh-candidates.json`
2. Produrre un bundle JSON valido con struttura:

```json
{
  "news": [ ... ],
  "stats": { ... }
}
```

3. Salvare il bundle, per esempio in:
   - `tmp/editorial-bundle.json`

## Validazione / dry-run
```bash
python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json --dry-run
```

## Pubblicazione live
```bash
python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json
```

## Note importanti
- Nessun provider LLM esterno viene invocato da questi script.
- La generazione editoriale resta esplicitamente fuori da Python: la fa l'agente/OpenClaw.
- Il finalizer valida `news`/`stats`, pubblica i file live e rigenera story pages + sitemap.
EOF

echo "RAW candidates written to tmp/refresh-candidates.json"
echo "Editorial handoff prepared in $handoff_dir"
echo "Next step: OpenClaw/Aion must produce tmp/editorial-bundle.json, then run:"
echo "  python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json --dry-run"
echo "  python3 scripts/finalize_orchestrated_refresh.py --bundle tmp/editorial-bundle.json"
