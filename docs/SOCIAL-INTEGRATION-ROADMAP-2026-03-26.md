# Altair Nexus — Roadmap integrazione social

Data: 2026-03-26

## Obiettivo
Introdurre capacità di condivisione e distribuzione social in Altair Nexus in modo progressivo, controllato e ripristinabile.

## Principio guida
Prima rendere il sito **condivisibile bene**.
Poi renderlo **distribuibile bene**.
Solo dopo valutarne la **pubblicazione automatica**.

---

## Fase 0 — Sicurezza operativa e rollback
**Obiettivo:** assicurare che ogni step sia reversibile.

### Task
- [x] Creare snapshot locale pre-lavori
- [ ] Aggiungere una guida di rollback dedicata nel progetto
- [ ] Definire una checklist pre-deploy e post-deploy
- [ ] Introdurre una convenzione di backup per ogni modifica rilevante
- [ ] Verificare sempre il sito in locale prima di pubblicare

### Deliverable
- backup archivio del progetto
- documento di rollback
- checklist operativa

### Exit criteria
- esiste almeno un punto di ripristino noto
- esiste una procedura semplice per tornare allo stato precedente

---

## Fase 1 — Social share foundations
**Obiettivo:** rendere la homepage e le storie condivisibili in modo più pulito.

### Task
- [ ] Aggiungere metadata Open Graph alla homepage
- [ ] Aggiungere Twitter/X card metadata
- [ ] Aggiungere canonical URL
- [ ] Definire una social preview image principale stabile
- [ ] Aggiungere favicon e polishing del pacchetto metadata
- [ ] Verificare l'anteprima link su piattaforme principali

### Deliverable
- `site/index.html` con metadata social base completi
- asset immagine per preview

### Note
Questa fase migliora molto la qualità del link condiviso anche senza cambiare routing o architettura.

### Exit criteria
- la homepage produce preview coerenti
- titolo, descrizione e immagine sono controllati

---

## Fase 2 — URL condivisibili per singola storia
**Obiettivo:** dare a ogni news un URL richiamabile.

### Strategia consigliata
Partire con query string:
- `site/?story=<id>`

### Task
- [ ] Estendere `app.js` per leggere `story` dalla URL
- [ ] Aprire automaticamente la story richiesta se presente
- [ ] Aggiornare la URL quando l'utente apre una storia
- [ ] Implementare fallback sicuro se la story non esiste
- [ ] Aggiungere pulsante “copia link” o “condividi questa notizia”

### Deliverable
- deep-linking per story id
- comportamento di fallback robusto

### Exit criteria
- ogni storia può essere linkata direttamente
- la homepage non si rompe se l'id non è valido

---

## Fase 3 — Estensione minima del content model
**Obiettivo:** preparare il contenuto alla distribuzione multi-canale senza rompere il modello attuale.

### Campi opzionali consigliati
- [ ] `slug`
- [ ] `summary`
- [ ] `canonicalSource`
- [ ] `secondarySources`
- [ ] `shareTitle`
- [ ] `shareDescription`
- [ ] `socialPriority`
- [ ] `socialEnabled`

### Task
- [ ] Aggiornare il runbook del refresh per contemplare i nuovi campi opzionali
- [ ] Aggiornare il validatore JSON per supportarli senza renderli obbligatori subito
- [ ] Documentare il significato editoriale di ogni campo

### Deliverable
- schema esteso ma backward-compatible
- validazione chiara

### Exit criteria
- i nuovi campi non rompono il frontend esistente
- il contenuto può già fornire materiale migliore per i social

---

## Fase 4 — UI di condivisione nel sito
**Obiettivo:** aggiungere un primo strato di condivisione lato utente.

### Task
- [ ] Aggiungere bottoni share nel pannello focus
- [ ] Aggiungere bottone share homepage
- [ ] Aggiungere bottone copy-link per story
- [ ] Definire testo share precompilato minimo
- [ ] Curare il comportamento mobile

### Deliverable
- UI share leggera e coerente con il design del progetto

### Exit criteria
- un utente può condividere homepage o story in pochi click
- i link prodotti sono leggibili e stabili

---

## Fase 5 — Generazione bozze social
**Obiettivo:** trasformare `news.json` in candidati social pronti per review.

### Strategia
Creare un piccolo layer di generazione, non ancora di pubblicazione.

### Output possibili
- `data/generated/social-drafts.json`
- oppure `tmp/social-drafts/`
- oppure export markdown/csv per review editoriale

### Task
- [ ] Definire criteri di selezione delle storie socializzabili
- [ ] Generare varianti per canale
- [ ] Distinguere copy per X, LinkedIn, Telegram
- [ ] Produrre angolo editoriale breve per ogni candidato
- [ ] Registrare timestamp e contenuto generato

### Deliverable
- generatore di bozze social
- formato di output chiaro e ispezionabile

### Exit criteria
- ogni run può proporre un set ridotto di candidati ad alta qualità
- nessuna pubblicazione automatica in questa fase

---

## Fase 6 — Review editoriale
**Obiettivo:** mantenere controllo umano prima della pubblicazione.

### Task
- [ ] Definire stato delle bozze: `draft`, `approved`, `rejected`, `posted`
- [ ] Decidere dove avviene la review: file, pannello semplice o workflow esterno
- [ ] Aggiungere note editoriali opzionali
- [ ] Registrare chi/come approva

### Deliverable
- workflow di review minimale ma reale

### Exit criteria
- nessun contenuto va fuori senza approvazione esplicita

---

## Fase 7 — Pubblicazione semi-automatica
**Obiettivo:** collegare la review alla distribuzione verso canali esterni.

### Task
- [ ] Scegliere i primi canali prioritari
- [ ] Integrare solo 1–2 piattaforme iniziali
- [ ] Loggare ogni tentativo di pubblicazione
- [ ] Salvare id esterni e orari di pubblicazione
- [ ] Gestire retry e fallimenti senza duplicati

### Canali consigliati per partire
1. LinkedIn
2. X
oppure
1. Telegram channel
2. LinkedIn

### Exit criteria
- un contenuto approvato può essere pubblicato in modo controllato
- gli errori non compromettono il sito

---

## Fase 8 — Story pages statiche dedicate
**Obiettivo:** ottenere metadata social e SEO davvero forti per singola notizia.

### Perché farlo dopo
Questa fase è molto valida, ma più strutturale. Conviene affrontarla quando:
- i deep link hanno già dimostrato valore
- la condivisione story-based è diventata importante

### Task
- [ ] Generare una pagina HTML statica per ogni story rilevante
- [ ] Applicare metadata specifici per story
- [ ] Definire canonical e fallback
- [ ] Valutare archivio pubblico per story condivise

### Exit criteria
- ogni storia importante ha una preview dedicata di qualità alta

---

## Sequenza pratica consigliata
Ordine reale di implementazione:

1. rollback guide
2. metadata social homepage
3. deep-link `?story=`
4. share buttons + copy link
5. estensione minima schema
6. generatore bozze social
7. review editoriale
8. solo dopo: pubblicazione semi-automatica e/o story pages statiche

---

## Strategia di ripristino
Ogni fase deve poter essere annullata rapidamente.

### Regole operative
- fare snapshot prima delle modifiche strutturali
- preferire aggiunte incrementali a refactor massivi
- tenere i nuovi asset social separati quando possibile
- validare sempre i JSON prima di sostituire file live
- testare in locale prima del rilascio

### Rollback target
In caso di problema bisogna poter:
- ripristinare `site/index.html`
- ripristinare `site/assets/app.js`
- ripristinare eventuali asset social aggiunti
- lasciare intatti `data/news.json` e `data/stats.json` se il problema è solo nel frontend

---

## KPI da osservare più avanti
Quando il layer social sarà attivo, i segnali utili da misurare saranno:
- click su share buttons
- copy-link usage
- traffico da social verso homepage
- traffico da social verso story deep links
- stories più condivise
- differenza tra performance homepage-share e story-share

---

## Decisione architetturale consigliata
Per non complicare troppo il workshop adesso:

**Scelta consigliata oggi**
- mantenere architettura static-first
- introdurre deep linking client-side
- rinviare story pages statiche a una seconda fase
- introdurre generazione bozze prima di qualsiasi autopublishing

È la strada con il miglior rapporto tra:
- velocità
- qualità
- controllo editoriale
- ripristinabilità
