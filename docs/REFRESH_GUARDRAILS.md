# REFRESH_GUARDRAILS.md

Guida operativa per evitare regressioni nel motore editoriale di Altair Nexus.

## Scopo del sito

Altair Nexus non è un aggregatore pieno di slot.
Deve:
- selezionare poco
- evitare cloni narrativi
- massimizzare varietà reale
- mantenere coerenza tra live, story pages e history
- privilegiare lettura editoriale, non riempimento

## Regole dure

1. Non introdurre più storie che raccontano lo stesso tema con parole diverse.
2. Non aumentare la quantità se riduce la qualità o la varietà.
3. Ogni refresh deve poter generare normalmente 2-3 nuove notizie, non una valanga.
4. Ogni item live deve esistere anche nella history del mese.
5. Non toccare frontend/layout per correggere bug del motore editoriale.
6. Prima di ogni intervento importante: fare backup.
7. Prima di pubblicare: eseguire dry-run.
8. Ogni modifica deve essere coerente con lo scopo generale del sito.

## Checklist prima di modificare il refresh

- Ho fatto un backup?
- Sto correggendo backend invece che mascherare il problema nel frontend?
- La modifica aumenta la diversificazione reale?
- La modifica riduce il rischio di cloni?
- La modifica mantiene coerenza live/history?
- La modifica evita regressioni su story pages e sitemap?

## Checklist prima di pubblicare

1. Eseguire `python3 scripts/refresh_edition_stable.py --dry-run`
2. Controllare `tmp/refresh-preview/news.preview.json`
3. Controllare `tmp/refresh-health/latest.json`
4. Verificare:
   - 6-8 storie massime
   - 2-3 nuove storie normali per refresh
   - categorie varie
   - narrative diverse
   - nessun clone evidente
5. Solo dopo pubblicare il refresh reale

## Segnali di regressione

- Due storie con stesso senso ma titoli diversi
- Più pezzi su chip/AI/guerra che sembrano lo stesso articolo riscritto
- History non allineata al live
- Aumento del numero di storie senza aumento della varietà
- Testi troppo schematici o formulaici
- Sezioni che cambiano logica senza verificare il formato reale dei dati usati
- Spaziature o altezze anomale nelle card dovute a contenuti con lunghezze molto diverse

## Controlli UI minimi dopo modifiche contenuto/logica

Dopo ogni cambio su refresh, history o sezione homepage verificare sempre anche:
- Highlights: 4 card se i dati storici esistono
- Nessuna card con vuoti verticali evidenti non voluti
- Titolo, hook, tag e CTA restano visivamente bilanciati
- Nessuna sezione dipende da assunzioni sbagliate sul formato JSON
- Il contenuto più corto non deve rompere l'allineamento visivo del grid

## Evoluzione del sistema

Quando introduci più dinamismo per categoria:
- non aumentare il numero di storie solo per mostrare più attività
- distinguere sempre tra novità reale e variante della stessa storia
- usare memoria corta per categoria prima di cambiare le query
- rendere dinamiche le query solo dopo aver validato novelty score e controllo clone
- quando il novelty score entra nella selezione, farlo crescere per step e con dry-run obbligatorio

## Regola editoriale fondamentale

Se c'è un dubbio tra:
- più quantità
- più chiarezza e distinzione

scegli sempre la seconda.

## Nota per Aion

Quando migliori il sistema:
- fai una cosa alla volta
- verifica impatto tecnico ed editoriale
- non sommare tuning multipli senza test intermedio
- se una modifica migliora la pipeline ma peggiora la voce del sito, non va bene
- se una modifica migliora la voce ma rompe history/coerenza, non va bene

Il sistema deve sembrare più intelligente, non solo più attivo.
