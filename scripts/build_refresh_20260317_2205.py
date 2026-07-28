import json
from datetime import datetime
from pathlib import Path

base = Path('/root/.openclaw/workspace/aion-nexus/data')
news_path = base / 'news.json'
stats_path = base / 'stats.json'
news_tmp = base / 'news.json.tmp'
stats_tmp = base / 'stats.json.tmp'

current = json.loads(news_path.read_text())
current_by_id = {item['id']: item for item in current}

def ts(item_id, default):
    return current_by_id.get(item_id, {}).get('timestamp', default)

edition_ts = '2026-03-17T22:05:00+01:00'
new_story_ts = edition_ts

news = [
  {
    'id': 'ai-20260317-alibaba-wukong-enterprise-agents-refresh',
    'category': 'ai',
    'subcategory': 'enterprise agents',
    'title': 'Alibaba porta Wukong nel lavoro quotidiano: gli agenti AI entrano davvero nei workflow enterprise',
    'hook': 'Reuters riferisce che Alibaba ha lanciato Wukong per coordinare più agenti AI su documenti, fogli di calcolo, meeting e ricerca. Il punto non è l’ennesima demo: è la distribuzione dentro software già usato da milioni di lavoratori.',
    'body': 'Alibaba ha presentato Wukong, piattaforma enterprise che orchestra più agenti AI in una singola interfaccia per attività operative come editing documentale, aggiornamento di spreadsheet, trascrizione di riunioni e ricerca. Secondo Reuters, il prodotto è in beta su invito, disponibile come applicazione desktop e integrato anche in DingTalk, la piattaforma di collaborazione del gruppo con oltre 20 milioni di utenti corporate. L’apertura annunciata verso Slack, Microsoft Teams e WeChat rafforza l’idea di un prodotto pensato per entrare nei flussi di lavoro esistenti, non per restare confinato in un ecosistema chiuso.',
    'body': 'Alibaba ha presentato Wukong, piattaforma enterprise che orchestra più agenti AI in una singola interfaccia per attività operative come editing documentale, aggiornamento di spreadsheet, trascrizione di riunioni e ricerca. Secondo Reuters, il prodotto è in beta su invito, disponibile come applicazione desktop e integrato anche in DingTalk, la piattaforma di collaborazione del gruppo con oltre 20 milioni di utenti corporate. L’apertura annunciata verso Slack, Microsoft Teams e WeChat rafforza l’idea di un prodotto pensato per entrare nei flussi di lavoro esistenti, non per restare confinato in un ecosistema chiuso.\n\nPer Altair Nexus il segnale resta molto forte: la competizione sugli agenti AI si sta spostando dalla qualità del modello alla capacità di entrare nei processi reali con permessi, interfacce e distribuzione. Quando un incumbent come Alibaba muove questa pedina, la conversazione smette di ruotare attorno alla novità e comincia a parlare di esecuzione industriale.',
    'tags': ['Alibaba', 'Wukong', 'AI agents', 'enterprise automation'],
    'sourceLabel': 'Reuters',
    'sourceUrl': 'https://wkzo.com/2026/03/16/alibaba-launches-ai-platform-for-enterprises-as-agent-craze-sweeps-china/',
    'sourceCount': 1,
    'timestamp': ts('ai-20260317-alibaba-wukong-enterprise-agents-refresh', new_story_ts),
    'featured': True,
    'opinion': 'Conta perché la gara sugli agenti si sta spostando dalla vetrina alla distribuzione nei software del lavoro vero.',
    'qualityScore': 94,
    'visual': 'ai'
  },
  {
    'id': 'tech-20260317-nvidia-inference-inflection-refresh',
    'category': 'tech',
    'subcategory': 'AI infrastructure',
    'title': 'Nvidia alza la posta del GTC: la finestra da mille miliardi è l’inference, non solo il training',
    'hook': 'Reuters riporta che Nvidia vede oltre 1.000 miliardi di dollari di opportunità di vendita per Blackwell e Rubin entro il 2027. Il messaggio di fondo è chiaro: il vero terreno da presidiare è servire inferenza continua su scala globale.',
    'body': 'Nella giornata del GTC, Reuters ha messo in evidenza il punto strategico più ambizioso della narrativa Nvidia: la domanda futura non riguarda soltanto l’addestramento dei modelli ma soprattutto l’inference operativa, quella che regge chatbot, copiloti, automazione, ricerca e software enterprise in produzione. Legare Blackwell e Rubin a una prospettiva di oltre 1.000 miliardi di dollari entro il 2027 significa presentare la roadmap non come semplice sequenza di chip, ma come dorsale di un intero ciclo industriale.',
    'body': 'Nella giornata del GTC, Reuters ha messo in evidenza il punto strategico più ambizioso della narrativa Nvidia: la domanda futura non riguarda soltanto l’addestramento dei modelli ma soprattutto l’inference operativa, quella che regge chatbot, copiloti, automazione, ricerca e software enterprise in produzione. Legare Blackwell e Rubin a una prospettiva di oltre 1.000 miliardi di dollari entro il 2027 significa presentare la roadmap non come semplice sequenza di chip, ma come dorsale di un intero ciclo industriale.\n\nPer Altair Nexus è la prosecuzione più concreta del tema già emerso nelle ore precedenti: Nvidia vuole trasformare il vantaggio nell’AI da leadership hardware a dipendenza infrastrutturale. Se il mercato accetta questa lettura, lo stack dell’inference diventa il centro di gravità del settore e le barriere competitive si alzano ancora.',
    'tags': ['Nvidia', 'GTC', 'Blackwell', 'Rubin', 'inference'],
    'sourceLabel': 'Reuters',
    'sourceUrl': 'https://news.google.com/rss/articles/CBMiqAFBVV95cUxPYW5JS25vNndXY1cxWWF3R3E2NERDV0dPSlMweUh3YURBWXQwNU5JdFNUMmV4Rlk1Ynk0Q0ZxNUZoWkt4RGNsd0JCeGlNanJNQmE4N2MwVG91V3R2U0xaeTRVMENWdU45VEUxdXI4V1dNRGE5XzRBZDlBajd5NWdlNGZIbVRHODVtMmZJLThET1RtMDBWbmVxNGhkMHFWc3pJWFRNNVo1c2M?oc=5',
    'sourceCount': 1,
    'timestamp': ts('tech-20260317-nvidia-inference-inflection-refresh', new_story_ts),
    'featured': True,
    'opinion': 'Se il training ha acceso il ciclo, Nvidia vuole possedere il punto in cui quel ciclo genera ricavi quotidiani: l’inference.',
    'qualityScore': 96,
    'visual': 'tech'
  },
  {
    'id': 'geopolitica-20260317-hormuz-allies-pressure-refresh',
    'category': 'geopolitica',
    'subcategory': 'energia e sicurezza',
    'title': 'La guerra con l’Iran entra nei contatori: l’energia va in triage e Hormuz resta il nervo del sistema',
    'hook': 'AP descrive governi costretti a conservare energia e contenere prezzi in rapido rialzo mentre il rischio su Hormuz resta centrale. La novità è che la crisi non pesa solo sui dossier militari: sta già ridisegnando priorità economiche interne.',
    'body': 'L’Associated Press racconta un passaggio più avanzato della crisi: non solo tensione militare e diplomatica, ma decisioni concrete di gestione dell’energia, dei consumi e dei costi in più paesi. Se la guerra con l’Iran continua a mettere pressione sullo Stretto di Hormuz, il problema non resta confinato al traffico marittimo: entra nei bilanci pubblici, nelle bollette, nelle scelte industriali e nella stabilità politica dei governi chiamati a fronteggiare prezzi elevati e offerta più fragile.',
    'body': 'L’Associated Press racconta un passaggio più avanzato della crisi: non solo tensione militare e diplomatica, ma decisioni concrete di gestione dell’energia, dei consumi e dei costi in più paesi. Se la guerra con l’Iran continua a mettere pressione sullo Stretto di Hormuz, il problema non resta confinato al traffico marittimo: entra nei bilanci pubblici, nelle bollette, nelle scelte industriali e nella stabilità politica dei governi chiamati a fronteggiare prezzi elevati e offerta più fragile.\n\nPer Altair Nexus questa rimane la storia-ombrello dell’edizione. Quando la sicurezza di un choke point energetico si trasforma in misure di razionamento, risparmio e contenimento dei prezzi, la geopolitica smette di essere sfondo e torna a dettare condizioni immediate a mercati, inflazione e crescita.',
    'tags': ['Iran', 'Hormuz', 'energia', 'shipping', 'inflazione'],
    'sourceLabel': 'AP News',
    'sourceUrl': 'https://news.google.com/rss/articles/CBMinAFBVV95cUxPQTVfdkhMYVZTTGxEYTdwRV94Ymc5QVZJNFN2RmZmZFFuR0hUVW1ocGRkeWNiUnEtdTVwek5raGtnb1F4RTB3TGVBWWs2cXZRSENDcWdEX1pmMW5FcmZYeGFJMEF3SFI1c053NV9WN2p4c1ktM1NKemlzemVEc3lTNjB5dVhiQmVKU1BKem1PaWpMY2U0eW5HWFVhcVk?oc=5',
    'sourceCount': 1,
    'timestamp': ts('geopolitica-20260317-hormuz-allies-pressure-refresh', new_story_ts),
    'featured': True,
    'opinion': 'Quando l’emergenza energetica passa dal rischio percepito al triage operativo, il mercato deve ricominciare a prezzare il peggio.',
    'qualityScore': 97,
    'visual': 'geo'
  },
  {
    'id': 'finanza-20260317-central-banks-bark-without-biting',
    'category': 'finanza',
    'subcategory': 'banche centrali',
    'title': 'Fed, BCE e colleghi possono ancora guidare il mercato senza toccare i tassi',
    'hook': 'Reuters osserva che le banche centrali stanno riscoprendo il valore del linguaggio: meno mosse immediate, più gestione delle aspettative. In una fase agitata da energia e guerra, anche il tono diventa politica monetaria.',
    'body': 'L’analisi Reuters mette a fuoco un equilibrio delicato: dopo una stagione di rialzi aggressivi, le principali banche centrali possono mantenere condizioni restrittive anche senza agire subito sui tassi, semplicemente rafforzando il messaggio di vigilanza. Questo approccio conta ancora di più mentre lo shock energetico complica il quadro, perché permette di tenere ancorate le aspettative senza aggiungere immediatamente un ulteriore freno a economie già meno lineari.',
    'body': 'L’analisi Reuters mette a fuoco un equilibrio delicato: dopo una stagione di rialzi aggressivi, le principali banche centrali possono mantenere condizioni restrittive anche senza agire subito sui tassi, semplicemente rafforzando il messaggio di vigilanza. Questo approccio conta ancora di più mentre lo shock energetico complica il quadro, perché permette di tenere ancorate le aspettative senza aggiungere immediatamente un ulteriore freno a economie già meno lineari.\n\nPer Altair Nexus il punto utile è questo: non serve una stretta formale per irrigidire le condizioni finanziarie. Se il mercato capisce che i banchieri centrali useranno la comunicazione per comprare tempo, il costo del denaro può restare alto abbastanza a lungo da pesare su credito, multipli e propensione al rischio.',
    'tags': ['Fed', 'BCE', 'banche centrali', 'tassi', 'forward guidance'],
    'sourceLabel': 'Reuters',
    'sourceUrl': 'https://news.google.com/rss/articles/CBMinwFBVV95cUxNTVRPd0Fmc2dHZFVwbEtZaUk0c1FrOC1XSGNudGxpcVdFeHIwNGliTkl0Si1xWXlqRV9yeEIwUkl0TGVZZFBlaHVWbHlnaVhfdGJneUtaZkhvZUZ2eXBJZTNZcXlnSE9iSGx3UC1fXzZsOGwtTU1pb3dDdDJqYW5zVGdxS2lXakRJWGxLVE5qQ2dIcTduNHRYSVlRdF9Db0U?oc=5',
    'sourceCount': 1,
    'timestamp': new_story_ts,
    'featured': False,
    'opinion': 'In questa fase la forward guidance pesa quasi quanto un intervento vero, perché il mercato è già abbastanza nervoso da fare il resto da solo.',
    'qualityScore': 90,
    'visual': 'fin'
  },
  {
    'id': 'mercati-20260317-oil-stocks-selectivity-refresh',
    'category': 'mercati',
    'subcategory': 'equity sentiment',
    'title': 'Il petrolio riparte, ma Wall Street non crolla: i listini restano in modalità selettiva',
    'hook': 'AP nota che il nuovo rialzo del greggio non ha provocato una resa generalizzata delle azioni USA. È un mercato che non si sente tranquillo, ma continua a scegliere cosa difendere.',
    'body': 'La seduta americana mostra ancora una volta una tenuta incompleta: il greggio torna a salire, ma i listini non reagiscono con un risk-off indiscriminato. Questo suggerisce che il capitale continua a distinguere tra storie considerate più robuste — in particolare AI e infrastruttura tecnologica — e comparti più esposti a margini, consumi ed energia. La resilienza quindi esiste, ma è selettiva e dipende dal fatto che molti investitori trattano ancora lo shock petrolifero come potenzialmente gestibile.',
    'body': 'La seduta americana mostra ancora una volta una tenuta incompleta: il greggio torna a salire, ma i listini non reagiscono con un risk-off indiscriminato. Questo suggerisce che il capitale continua a distinguere tra storie considerate più robuste — in particolare AI e infrastruttura tecnologica — e comparti più esposti a margini, consumi ed energia. La resilienza quindi esiste, ma è selettiva e dipende dal fatto che molti investitori trattano ancora lo shock petrolifero come potenzialmente gestibile.\n\nPer Altair Nexus è un equilibrio fragile: finché il mercato pensa di poter isolare il rischio in pochi segmenti, regge. Se però Hormuz resta sotto pressione e il barile continua a rincarare, la selettività può rapidamente trasformarsi in difesa più larga e meno elegante.',
    'tags': ['Wall Street', 'petrolio', 'mercati', 'rotazione', 'risk sentiment'],
    'sourceLabel': 'AP News',
    'sourceUrl': 'https://news.google.com/rss/articles/CBMi8gFBVV95cUxNNDZmMnl2TDh2OWJDckQwYXZLVHg4RzdrOFZlRUFzVzlFWXBMdnVlaTNJN1YzY1N3cEVHV3RmX3lsS3Z3UEFZNzdLXzBEY19ESkZLcWJXenE2WEUxcVQwWGw1VDNkUW56WXNNdjFsMzcxQmlfOXRUQVlWd2lfYVFTWUp6Qkd3QjRVWjBDMnRRRWZveU1Tbzhfbi1pYkJWN0JOU0VEQmptdUY5dUdGNHdRUVdncE91Q3E4azBhMU53VjBFUWFUYWtYMzdDUDRqRURNbXNaT0FQWEVYZ0xZQlVIcjNES2Rac2pNWWYxUU9TU1hmZw?oc=5',
    'sourceCount': 1,
    'timestamp': ts('mercati-20260317-oil-stocks-selectivity-refresh', new_story_ts),
    'featured': True,
    'opinion': 'La tenuta delle borse sembra più una selezione tattica del rischio che una vera normalizzazione.',
    'qualityScore': 92,
    'visual': 'markets'
  },
  {
    'id': 'startup-20260317-mastercard-bvnk-refresh',
    'category': 'startup',
    'subcategory': 'fintech infrastructure',
    'title': 'Mastercard compra BVNK: le stablecoin passano dall’hype al plumbing dei pagamenti',
    'hook': 'Reuters segnala un’acquisizione fino a 1,8 miliardi di dollari. Il tema non è la narrativa crypto in sé, ma l’infrastruttura che può portare regolamento digitale e pagamenti stabili dentro i circuiti mainstream.',
    'body': 'L’operazione su BVNK conta perché sposta le stablecoin in un’area molto meno speculativa e molto più industriale. BVNK lavora sull’infrastruttura per pagamenti e settlement in asset digitali stabili, cioè il pezzo che decide se la tecnologia resta un esperimento o entra davvero nei flussi transfrontalieri, nel treasury management e nei costi di regolamento. Per Mastercard è una mossa di presidio strategico su un layer potenzialmente importante del denaro programmabile.',
    'body': 'L’operazione su BVNK conta perché sposta le stablecoin in un’area molto meno speculativa e molto più industriale. BVNK lavora sull’infrastruttura per pagamenti e settlement in asset digitali stabili, cioè il pezzo che decide se la tecnologia resta un esperimento o entra davvero nei flussi transfrontalieri, nel treasury management e nei costi di regolamento. Per Mastercard è una mossa di presidio strategico su un layer potenzialmente importante del denaro programmabile.\n\nPer Altair Nexus il segnale resta di maturazione: quando un grande network dei pagamenti compra plumbing invece di limitarsi a partnership leggere, il mercato riceve un messaggio preciso. La partita si sta spostando dall’hype all’adozione operativa, e lì vincono rete, compliance e integrazione.',
    'tags': ['Mastercard', 'BVNK', 'stablecoin', 'fintech', 'payments'],
    'sourceLabel': 'Reuters',
    'sourceUrl': 'https://news.google.com/rss/articles/CBMiogFBVV95cUxNbDd0WElvQW9xWHJrVW5KTjlBUjgxRXNQM2o2V21RNkk1cV9lc2RfLVkxdVlBbEdrdEFqM3RwQXBfcGZkd1hSWGlWNGpYcFpieG0xUWplWHY4NEpMYXBSV1gwbGRvY29ZOVBoNHRVNTVac3g1bkUydG9OeGxaNkJEdFFvSlhnOWV3Y09NYlN2WEd2UDFCNWFjNm9tOHBLaWpWenc?oc=5',
    'sourceCount': 1,
    'timestamp': ts('startup-20260317-mastercard-bvnk-refresh', new_story_ts),
    'featured': False,
    'opinion': 'Se i grandi network comprano infrastruttura stablecoin, l’adozione sta iniziando a pesare più della narrativa crypto.',
    'qualityScore': 93,
    'visual': 'startup'
  },
  {
    'id': 'scienza-20260317-cern-xiccplus-refresh',
    'category': 'scienza',
    'subcategory': 'fisica delle particelle',
    'title': 'Il CERN osserva uno “heavy proton”: Xi-cc-plus apre nuova materia da misurare, non da mitizzare',
    'hook': 'Il Guardian racconta la scoperta di Xi-cc-plus grazie al detector LHCb aggiornato. È una notizia forte perché aggiunge una misura rara e utile sulla forza forte, non l’ennesimo slogan sulla fisica del futuro.',
    'body': 'Al CERN i ricercatori hanno osservato Xi-cc-plus, una particella affine al protone ma circa quattro volte più pesante, resa visibile dalle nuove capacità del rivelatore LHCb. Il valore scientifico è concreto: queste osservazioni permettono di affinare la comprensione della forza nucleare forte, cioè l’interazione che tiene insieme il cuore della materia ordinaria. Il fatto che il segnale emerga già dopo un anno dal potenziamento del detector suggerisce anche che l’upgrade strumentale stia producendo risultati molto rapidamente.',
    'body': 'Al CERN i ricercatori hanno osservato Xi-cc-plus, una particella affine al protone ma circa quattro volte più pesante, resa visibile dalle nuove capacità del rivelatore LHCb. Il valore scientifico è concreto: queste osservazioni permettono di affinare la comprensione della forza nucleare forte, cioè l’interazione che tiene insieme il cuore della materia ordinaria. Il fatto che il segnale emerga già dopo un anno dal potenziamento del detector suggerisce anche che l’upgrade strumentale stia producendo risultati molto rapidamente.\n\nPer Altair Nexus questa resta una delle notizie migliori della giornata: poca retorica, molta sostanza. La fisica fondamentale avanza così — con strumenti migliori, misure rare e un guadagno di precisione che vale più di qualsiasi titolo urlato sulla rivoluzione imminente.',
    'tags': ['CERN', 'LHCb', 'Xi-cc-plus', 'forza forte', 'particle physics'],
    'sourceLabel': 'The Guardian',
    'sourceUrl': 'https://www.theguardian.com/science/2026/mar/17/scientists-discover-heavier-proton-upgraded-detector',
    'sourceCount': 1,
    'timestamp': ts('scienza-20260317-cern-xiccplus-refresh', new_story_ts),
    'featured': False,
    'opinion': 'Le scoperte più affidabili in fisica raramente promettono miracoli: costruiscono comprensione.',
    'qualityScore': 90,
    'visual': 'science'
  }
]

# fix accidental duplicate keys already resolved by Python last-one-wins; kept intentionally simple

stats = {
  'editionUpdatedAt': edition_ts,
  'newsGeneratedToday': len(news),
  'sourcesAnalyzed': 11,
  'topicEmerging': [
    'AI agents enterprise',
    'AI inference economics',
    'Hormuz energy risk',
    'central bank signaling',
    'oil resilience trade',
    'stablecoin plumbing',
    'particle physics'
  ],
  'mostViewed': [
    'La guerra con l’Iran entra nei contatori: l’energia va in triage e Hormuz resta il nervo del sistema',
    'Nvidia alza la posta del GTC: la finestra da mille miliardi è l’inference, non solo il training',
    'Alibaba porta Wukong nel lavoro quotidiano: gli agenti AI entrano davvero nei workflow enterprise'
  ],
  'signals': [
    {'label': 'Edition', 'value': 'Public MVP'},
    {'label': 'Cadence', 'value': 'Hourly auto-refresh · 22:05 CET'},
    {'label': 'Mode', 'value': 'Italian briefing'},
    {'label': 'Focus', 'value': 'Source-backed news'}
  ]
}

news_tmp.write_text(json.dumps(news, ensure_ascii=False, indent=2) + '\n')
stats_tmp.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n')

# Parse back as a safety check
json.loads(news_tmp.read_text())
json.loads(stats_tmp.read_text())

print(f'wrote {news_tmp} and {stats_tmp}')
