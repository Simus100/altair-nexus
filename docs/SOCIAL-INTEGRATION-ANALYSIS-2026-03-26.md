# Altair Nexus — Analisi tecnica integrazione social

Data: 2026-03-26

## Obiettivo
Valutare come integrare un sistema di condivisione delle notizie sui social dentro Altair Nexus senza snaturare l'architettura attuale e mantenendo il progetto facilmente ripristinabile in caso di problemi.

## Sintesi esecutiva
Altair Nexus è già in una buona posizione per diventare un prodotto editoriale multi-canale.

Il progetto è oggi:
- static-first
- JSON-driven
- orientato a una homepage editoriale pubblica
- già dotato di una semantica contenutistica sufficiente per generare output derivati

Questo rende l'integrazione social **fattibile**, ma con una distinzione importante:

1. **condivisione semplice**: facile e immediata
2. **social preview di qualità**: richiede URL condivisibili e metadata migliori
3. **pubblicazione editoriale multi-canale**: possibile, ma serve un piccolo layer in più tra contenuto e distribuzione

## Struttura attuale del progetto

### Frontend pubblico
- `site/index.html`
- `site/history.html`
- `site/assets/app.js`
- `site/assets/styles.css`

### Dati editoriali
- `data/news.json`
- `data/categories.json`
- `data/stats.json`
- `data/history/`

### Tooling
- `scripts/validate_nexus_json.py`
- script di refresh periodico in `scripts/`
- script di generazione immagine brief

### Documentazione
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/AUTO_REFRESH_RUNBOOK.md`
- guide operative aggiuntive

## Come funziona oggi
Il frontend carica i JSON con `fetch()` e renderizza:
- latest feed
- top stories
- focus panel
- category radar
- dashboard metriche
- Aion Brief

Il cuore del prodotto, quindi, non è un backend ma il **content model**.
Questo è un vantaggio: il social layer può essere costruito come derivazione del contenuto esistente, senza introdurre subito server-side complexity.

## Punti di forza rispetto all'integrazione social

### 1. Il contenuto è già strutturato
Ogni story in `news.json` contiene già campi molto utili per i social:
- `id`
- `title`
- `hook`
- `body`
- `category`
- `tags`
- `sourceLabel`
- `sourceUrl`
- `timestamp`
- `featured`
- `opinion`
- `qualityScore`

Tradotto: il progetto ha già i mattoni minimi per generare copy brevi, caption, snippet e selezioni editoriali.

### 2. Esiste già una logica di ranking
I contenuti vengono ordinati per:
- timestamp
- quality score
- featured status

Questo è molto utile per decidere:
- cosa mostrare in share priority
- cosa promuovere sui social
- cosa lasciare solo in homepage

### 3. Il progetto è static-first
Per la fase iniziale questo è ideale:
- meno superfici di errore
- deploy semplice
- rollback semplice
- possibilità di generare asset statici per share preview

### 4. C'è già una componente visual/editoriale
L'immagine del brief e il tono del prodotto aiutano a costruire un'identità social coerente.
Altair Nexus non parte da zero come “lista di link”: parte già come prodotto editoriale.

## Limiti attuali

### 1. Nessun URL canonico per singola storia
Questo è il limite principale.

Oggi il sito lavora soprattutto in-page: clicchi un item e si apre il focus nel pannello interno.
Per i social però serve almeno una di queste opzioni:
- pagina dedicata per articolo
- route con query string tipo `?story=<id>`
- route hash tipo `#story=<id>`

Per la vera shareability, la query string è molto più utile dell'hash, perché è più adatta a future estensioni e a eventuale rendering server-side/static generation.

### 2. Metadata social incompleti
In `site/index.html` ci sono title e description base, ma mancano elementi centrali:
- Open Graph completo
- Twitter card
- canonical URL
- eventuali metadata dinamici per story

Risultato: il link può essere condiviso, ma non ancora come prodotto editoriale ben impacchettato.

### 3. Il content model non distingue ancora tra homepage e distribuzione social
Il modello attuale è ottimo per la homepage, meno per la syndication.
Mancano campi opzionali come:
- `slug`
- `summary`
- `canonicalUrl`
- `shareTitle`
- `shareDescription`
- `socialImage`
- `socialPriority`
- `socialEnabled`
- `postedTo`
- `postedAt`

### 4. Nessun layer di review per publishing sociale
Per ora il workflow è orientato a produrre l'edizione pubblica.
Non esiste ancora un passaggio esplicito:
- candidati social
- approvazione
- pubblicazione
- tracciamento

### 5. Nessuna strategia di fallback social
Se una preview, un'immagine o un URL per story falliscono, al momento il sistema non ha un comportamento di riserva definito.

## Modello di integrazione consigliato

## Livello 1 — Share layer leggero
Primo obiettivo: rendere il sito condivisibile bene, senza cambiare natura al progetto.

Componenti:
- metadata social per homepage
- pulsanti share per homepage e story
- URL condivisibili per notizia
- fallback alla homepage se lo story id non esiste

### Vantaggi
- basso rischio
- impatto immediato
- nessuna piattaforma esterna necessaria
- rollback semplice

## Livello 2 — Story routing pubblico
Secondo obiettivo: far sì che ogni storia abbia una sua identità URL.

Opzioni:

### Opzione A — query string sul frontend statico
Esempio:
- `/site/?story=ai-20260326-bytedance-seedance-capcut-rollout`

Pro:
- minima invasività
- nessun backend
- implementazione rapida

Contro:
- metadata social dinamici limitati se il sito resta puramente client-side

### Opzione B — pagine statiche generate per story
Esempio:
- `/site/stories/ai-20260326-bytedance-seedance-capcut-rollout.html`

Pro:
- preview social completa per singola notizia
- SEO migliore
- canonical puliti

Contro:
- pipeline più ricca
- serve generazione file a ogni refresh

### Valutazione
Per Altair Nexus conviene partire da **Opzione A** e pianificare **Opzione B** come evoluzione naturale.

## Livello 3 — Social publishing ops
Terzo obiettivo: usare il contenuto per distribuire notizie fuori dal sito.

Pipeline suggerita:
1. selezione delle storie candidate
2. generazione copy per canale
3. generazione o scelta asset visuale
4. review umana
5. pubblicazione
6. logging esito

### Canali più naturali
- **X**: headline + angle rapido
- **LinkedIn**: hook + insight + implicazione
- **Telegram / WhatsApp channel**: digest breve

### Canali meno urgenti all'inizio
- Instagram: utile solo con una strategia visual davvero dedicata
- Facebook: non prioritario per il tipo di prodotto

## Evoluzioni consigliate del data model
Senza rompere il modello attuale, si possono aggiungere campi opzionali.

### Minimo consigliato
- `slug`
- `summary`
- `canonicalSource`
- `secondarySources`
- `shareTitle`
- `shareDescription`
- `socialPriority`
- `socialEnabled`

### Per una fase successiva
- `socialImage`
- `socialVariants`
- `distributionStatus`
- `postedTo`
- `postedAt`
- `utmCampaign`

## Considerazioni tecniche importanti

### Metadata dinamici: vero collo di bottiglia
Se vuoi che quando qualcuno condivide una singola storia compaiano:
- titolo giusto
- descrizione giusta
- immagine giusta

allora il client-side puro non basta sempre.

Per questo il cammino più solido è:
- prima URL story-friendly client-side
- poi static generation delle story pages

### Social buttons non equivalgono a social strategy
Aggiungere solo i bottoni “condividi” è facile, ma da soli non creano distribuzione editoriale.
Sono utili, ma il valore vero nasce quando il contenuto viene preparato per il canale.

### Review umana consigliata
Soprattutto all'inizio, la pubblicazione automatica piena è sconsigliata.
Meglio:
- generazione bozza
- revisione
- pubblicazione manuale o semi-manuale

## Rischi e mitigazioni

### Rischio: rompere la homepage attuale
Mitigazione:
- feature flag semplice
- sviluppo incrementale
- backup prima di ogni modifica
- test locale via `python3 -m http.server 4173`

### Rischio: URL story non riconosciuti
Mitigazione:
- fallback sicuro alla homepage standard
- messaggio soft oppure selezione del primo contenuto disponibile

### Rischio: metadata incoerenti
Mitigazione:
- definire valori di default
- preferire campi derivati da `title` e `hook`
- validare i campi social durante il build

### Rischio: automazione social troppo aggressiva
Mitigazione:
- fase bozza obbligatoria
- nessuna autopubblicazione iniziale
- logging degli output generati

## Ripristinabilità e rollback
Questo progetto deve restare sempre recuperabile.

### Principio operativo
Ogni modifica al layer social deve essere:
- isolata
- reversibile
- documentata
- verificabile localmente

### Misure minime consigliate
1. creare backup snapshot prima delle modifiche
2. lavorare per passi piccoli
3. salvare nuovi file in modo additivo quando possibile
4. non sovrascrivere mai dati live senza validazione preventiva
5. tenere una guida di rollback dedicata

### Stato attuale del backup
È stato creato uno snapshot locale del progetto prima dell'analisi:
- `/root/.openclaw/workspace/backups/aion-nexus-social-analysis-20260326-175229.tar.gz`

Questo consente di ripristinare rapidamente lo stato corrente del workshop se necessario.

## Conclusione
Sì, integrare la condivisione social in Altair Nexus è non solo possibile, ma coerente con la struttura del progetto.

La base tecnica è già buona.
Il punto non è “se si può fare”, ma **in quale ordine farlo senza rompere ciò che già funziona**.

L'ordine corretto è:
1. migliorare la shareability del sito
2. introdurre URL per story
3. arricchire il content model con campi social opzionali
4. costruire un layer di generazione bozze
5. solo dopo valutare pubblicazione semi-automatica

Questa strada mantiene Altair Nexus leggero, editoriale e recuperabile.
