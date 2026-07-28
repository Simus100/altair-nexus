# DYNAMIC_CATEGORY_NOVELTY_PLAN.md

Piano tecnico per rendere Altair Nexus più dinamico nel riconoscere novità vere per categoria, senza aumentare rumore, cloni o regressioni.

## Obiettivo

Migliorare la capacità del refresh di capire quando una categoria porta:
- una novità reale
- un aggiornamento marginale
- una variante dello stesso tema
- un nuovo asse editoriale interno alla categoria

L'obiettivo NON è aumentare semplicemente il numero di notizie.
L'obiettivo è aumentare la qualità della selezione e la sensibilità al cambiamento reale.

---

## Stato attuale

Il sistema oggi ha già:
- dedupe per titolo
- canonical key
- narrative signature
- blocco clone tra articoli troppo simili
- controllo live/history
- migliore varietà editoriale rispetto a prima

Limite attuale:
- la classificazione è ancora abbastanza statica
- la discovery per categoria è ancora parzialmente rigida
- il sistema riconosce bene i cloni, ma meno bene i cambi di asse dentro una stessa categoria

---

## Principio guida

Ogni categoria deve imparare a distinguere tra:
1. stesso tema ripetuto
2. stesso tema ma nuovo sviluppo davvero rilevante
3. nuovo sottotema dentro la categoria
4. giorno debole, in cui è meglio non forzare una novità artificiale

---

## Fase 1 — Memoria corta per categoria

Aggiungere una lettura delle migliori 3-5 storie recenti per ogni categoria da live + history recente.

Per ogni categoria costruire:
- recent canonical keys
- recent narrative signatures
- recent dominant tokens
- recent source hosts

Uso:
- confrontare ogni nuovo candidato con lo storico corto della propria categoria
- misurare se è davvero nuovo o solo una variazione

### Output atteso
Un dizionario tipo:
```json
{
  "tech": {
    "recentCanonicalKeys": [...],
    "recentNarratives": [...],
    "recentTokens": [...]
  }
}
```

---

## Fase 2 — Novelty score per categoria

Per ogni candidato generare un punteggio di novità che tenga conto di:
- distanza dai canonical key recenti
- distanza narrativa dalla stessa categoria
- nuovi token dominanti non presenti nei giorni precedenti
- differenza di fonte / host se utile
- penalità se il tema è già saturo negli ultimi 1-2 giorni

### Concetto
Non basta dire “non è clone”.
Bisogna dire:
- quanto è nuovo dentro la categoria
- quanto apre un asse diverso

### Output atteso
Ogni item candidato dovrebbe avere:
- `noveltyScore`
- `noveltyClass`: `new_axis | relevant_update | marginal_update | clone_risk`

---

## Fase 3 — Query dinamiche per categoria

Ogni categoria deve avere 3 livelli di query:

1. **base queries**
   - stabili
   - sempre presenti

2. **rotating queries**
   - sottotemi che ruotano
   - servono ad ampliare senza perdere identità

3. **opportunity queries**
   - si attivano se i token recenti mostrano un asse emergente

### Esempio tech
- base: chip, semiconductors, AI infrastructure
- rotating: networking, packaging, data center power, cloud infra
- opportunity: export controls, memory, inference stack, server bottlenecks

### Regola
Le query dinamiche devono ampliare la copertura, non riempire slot.

---

## Fase 4 — Stato di categoria

Per ogni categoria mantenere uno stato leggero:
- quiet
- active
- saturated
- shifting
- stale

### Significato
- `quiet`: poche novità recenti, va bene cercare un nuovo asse
- `active`: categoria ricca ma ancora aperta
- `saturated`: troppe storie molto simili, servono filtri più duri
- `shifting`: la categoria sta cambiando asse, favorire novità vere
- `stale`: meglio non forzare articoli deboli solo per coprire la categoria

### Uso
Lo stato modula:
- aggressività della discovery
- severità del novelty filter
- priorità editoriale

---

## Fase 5 — Guardrail

Qualsiasi introduzione di dinamismo deve rispettare sempre:
- niente aumento del rumore
- niente crescita dei cloni
- niente rottura live/history
- niente peggioramento della leggibilità editoriale

Prima di pubblicare:
1. dry-run
2. controllo `tmp/refresh-health/latest.json`
3. controllo categorie e narrative
4. controllo manuale di 2-3 candidati nuovi

---

## Piano di implementazione consigliato

### Step A
Implementare la memoria corta per categoria e il novelty score.

### Step B
Usare il novelty score solo come metrica diagnostica, senza cambiare ancora la selezione finale.

### Step C
Se i risultati sono buoni, integrare il novelty score nell'editorial score.

### Step D
Solo dopo, rendere dinamiche alcune query secondarie.

Nota operativa: iniziare con query dinamiche leggere solo su 2-3 categorie pilota, senza aumentare il tetto di nuove storie per refresh.

### Step E
Infine introdurre uno stato di categoria leggero.

---

## Regola operativa

Non introdurre tutte le fasi insieme.
Una fase alla volta.
Ogni fase deve essere verificata sia tecnicamente sia editorialmente.

---

## Criterio di successo

Il sistema migliora davvero se:
- le categorie appaiono più vive ma non più rumorose
- emergono più spesso assi nuovi dentro la stessa categoria
- cala la sensazione di ripetizione mascherata
- il sito sembra più intelligente, non solo più attivo
