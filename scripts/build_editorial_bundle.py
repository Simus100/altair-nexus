#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path('/root/.openclaw/workspace/aion-nexus')
HANDOFF = ROOT / 'tmp' / 'editorial-handoff'
OUT = ROOT / 'tmp' / 'editorial-bundle.json'

live_news = json.loads((HANDOFF / 'live-news.snapshot.json').read_text(encoding='utf-8'))
live_stats = json.loads((HANDOFF / 'live-stats.snapshot.json').read_text(encoding='utf-8'))

news = []
for item in live_news:
    if item.get('id') == 'finanza-20260430-il-capitale-torna-selettivo-why-u-a-e-quitting-e8f3858615':
        news.append({
            'id': 'finanza-20260430-il-capitale-torna-selettivo-behind-powell-high-stakes-decision-72c447a49f',
            'category': 'finanza',
            'subcategory': 'Fed, indipendenza monetaria e nuovo rischio istituzionale',
            'title': 'Powell resta alla Fed anche dopo la presidenza: per i mercati è un test diretto sull’indipendenza della banca centrale',
            'hook': 'Il New York Times racconta la scelta di Jerome Powell di restare come governatore della Federal Reserve dopo la fine del suo mandato da presidente. È una sostituzione forte perché sposta la sezione Finanza su un asse più immediato per i mercati: non solo tassi, ma credibilità istituzionale, pressione politica e tenuta dell’autonomia monetaria americana.',
            'body': 'La notizia conta perché trasforma una questione di leadership in un segnale operativo per il mercato. Se Powell decide di non lasciare del tutto la Fed, il messaggio implicito è che la partita sull’indipendenza della banca centrale è ormai abbastanza delicata da giustificare una presenza di continuità dentro l’istituzione. Per investitori e operatori questo significa che il rischio non riguarda soltanto la direzione futura dei tassi, ma il grado di interferenza politica che Washington potrà esercitare sulla politica monetaria nei prossimi mesi.\n\nPer Altair Nexus il punto interessante è che qui il capitale deve valutare meno un dato macro e più la qualità della cornice che governa i dati macro. Quando la credibilità della Fed entra esplicitamente nella storia, il premio al rischio può spostarsi anche senza una mossa immediata sui tassi: passa attraverso dollaro, Treasury, aspettative di inflazione e fiducia nella capacità americana di mantenere separate politica e banca centrale. In questo senso la scelta di Powell pesa perché ricorda che, nel 2026, la stabilità finanziaria dipende ancora anche dalla tenuta delle istituzioni.',
            'tags': [
                'Jerome Powell',
                'Federal Reserve',
                'tassi',
                'indipendenza della banca centrale',
                'Stati Uniti'
            ],
            'sourceLabel': 'nytimes.com',
            'sourceUrl': 'https://www.nytimes.com/2026/04/30/business/powell-fed-trump.html',
            'sourceCount': 1,
            'timestamp': '2026-04-30T16:13:11+02:00',
            'featured': True,
            'opinion': 'Quando il presidente uscente della Fed sceglie di restare dentro l’istituzione per difenderne il perimetro, il mercato capisce che l’autonomia monetaria è diventata essa stessa un asset da monitorare.',
            'qualityScore': 89,
            'visual': 'fin'
        })
    else:
        news.append(item)

stats = dict(live_stats)
stats.update({
    'editionUpdatedAt': '2026-04-30T20:00:00+02:00',
    'newsGeneratedToday': len(news),
    'topicEmerging': [
        'Alle 20:00 l’edizione resta guidata dal rischio energetico e geopolitico: Iran, petrolio e costo strategico del conflitto continuano a orientare il quadro.',
        'In finanza la novità più forte è istituzionale: la scelta di Powell di restare alla Fed sposta l’attenzione sulla credibilità della banca centrale oltre il solo tema dei tassi.',
        'I candidati su Google Translate arrivano da fonte diretta ma restano troppo celebrativi per sostituire i presìdi già più solidi su AI, tech e futuro.',
        'La linea editoriale resta selettiva: continuità sulle storie ancora forti, ricambio solo dove la novità migliora davvero rilevanza e freschezza.',
        'Il risultato è un refresh prudente ma non statico: il quadro live si aggiorna senza diluire l’edizione con riempitivi deboli.'
    ],
    'mostViewed': [
        'Il Brent schizza ai massimi dal 2022: l’ipotesi di nuove opzioni USA sull’Iran riaccende il rischio globale',
        'La guerra con l’Iran costa già 25 miliardi: per i mercati non è solo un conto politico, ma un nuovo rischio da prezzare',
        'Powell resta alla Fed anche dopo la presidenza: per i mercati è un test diretto sull’indipendenza della banca centrale'
    ],
    'signals': [
        {'label': 'Edizione', 'value': 'MVP pubblico'},
        {'label': 'Cadenza', 'value': 'Refresh automatico ogni ora · 20:00 CEST'},
        {'label': 'Modalità', 'value': 'Briefing in italiano'},
        {'label': 'Focus', 'value': 'Notizie verificate dalle fonti'}
    ]
})

bundle = {
    'news': news,
    'stats': stats,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('w', encoding='utf-8') as fh:
    json.dump(bundle, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
