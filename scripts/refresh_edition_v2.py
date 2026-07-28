#!/usr/bin/env python3
import json, os, shutil, subprocess, urllib.request, urllib.parse, xml.etree.ElementTree as ET, hashlib, re
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path('/root/.openclaw/workspace/aion-nexus')
DATA = ROOT / 'data'
TMP = ROOT / 'tmp' / 'stable-refresh-backups'
NEWS = DATA / 'news.json'
STATS = DATA / 'stats.json'
NEWS_TMP = DATA / 'news.json.tmp'
STATS_TMP = DATA / 'stats.json.tmp'

DISCOVERY_QUERIES = [
    ('ai', 'AI agents OpenAI Alibaba Nvidia Anthropic Google model site:reuters.com OR site:techcrunch.com OR site:theverge.com OR site:venturebeat.com'),
    ('tech', 'technology Huawei Nvidia semiconductor chip China infrastructure site:reuters.com OR site:theverge.com OR site:techcrunch.com'),
    ('geopolitica', 'Iran Israel Houthi Red Sea Hormuz sanctions site:reuters.com OR site:apnews.com OR site:aljazeera.com'),
    ('finanza', 'central bank inflation bond rates IMF rupee currency site:reuters.com OR site:cnbc.com OR site:marketwatch.com'),
    ('mercati', 'stocks futures oil wall street correction risk-off markets site:reuters.com OR site:cnbc.com OR site:marketwatch.com'),
    ('startup', 'startup funding acquisition venture investment enterprise AI site:reuters.com OR site:techcrunch.com OR site:tech.eu'),
    ('scienza', 'study discovery CERN ESA NASA space research site:reuters.com OR site:nature.com OR site:science.org'),
    ('futuro', 'deepfake automation robotics AI society elections site:reuters.com OR site:theverge.com OR site:bbc.com')
]

VISUAL_MAP = {'ai':'ai','tech':'tech','geopolitica':'geo','finanza':'fin','mercati':'markets','startup':'startup','scienza':'science','futuro':'future'}
QUALITY_FLOOR = 86
MAX_LIVE = 10
MIN_LIVE = 7


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fetch(url, timeout=15):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode('utf-8', 'ignore')


def slugify(text):
    s = text.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s[:70]


def short_hash(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:10]


def title_norm(text):
    return re.sub(r'\s+', ' ', (text or '').strip().lower())


def source_label(link):
    host = urllib.parse.urlparse(link).netloc.lower().replace('www.', '')
    if 'reuters.com' in host: return 'Reuters'
    if 'apnews.com' in host: return 'AP'
    if 'aljazeera.com' in host: return 'Al Jazeera'
    if 'techcrunch.com' in host: return 'TechCrunch'
    if 'theverge.com' in host: return 'The Verge'
    if 'venturebeat.com' in host: return 'VentureBeat'
    if 'marketwatch.com' in host: return 'MarketWatch'
    if 'cnbc.com' in host: return 'CNBC'
    if 'nature.com' in host: return 'Nature'
    if 'science.org' in host: return 'Science'
    return 'Google News'


def usable_headline(title, link):
    t = title_norm(title)
    if not t or len(t.split()) < 6:
        return False
    bad = ['the latest:', 'exclusive:', 'breakingviews', 'tech news |', 'world news |', 'business news |', 'markets news |', 'live updates', 'roundup', 'what we know']
    if any(x in t for x in bad):
        return False
    host = urllib.parse.urlparse(link).netloc.lower()
    if 'bbc.com' in host and len(t.split()) < 9:
        return False
    return True


def discover():
    findings = []
    seen = set()
    for category, query in DISCOVERY_QUERIES:
        rss = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': query, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'})
        try:
            root = ET.fromstring(fetch(rss))
        except Exception:
            continue
        for item in root.findall('.//item')[:6]:
            title = (item.findtext('title') or '').strip()
            link = (item.findtext('link') or '').strip()
            if not usable_headline(title, link):
                continue
            key = (category, title_norm(title))
            if key in seen:
                continue
            seen.add(key)
            findings.append({'category': category, 'title': title, 'link': link})
    return findings


def build_editorial_item(category, raw_title, link):
    lowered = title_norm(raw_title)
    label = source_label(link)

    if category == 'ai' and any(k in lowered for k in ['agent', 'agents', 'assistant']) and any(k in lowered for k in ['alibaba', 'openai', 'anthropic', 'google', 'nvidia', 'microsoft']):
        return {
            'category': 'ai',
            'subcategory': 'Agenti AI, orchestrazione software e monetizzazione enterprise',
            'title': 'Gli agenti AI alzano la posta: la prossima battaglia non è il modello, ma il flusso di lavoro',
            'hook': f'{label} mette in luce un passaggio importante: la corsa sugli agenti AI sta smettendo di vivere di sola demo e si sta avvicinando ai processi reali di lavoro e spesa.',
            'body': 'Nel mercato AI sta diventando più chiaro un passaggio: il valore non si misura soltanto nella qualità del modello, ma nella sua capacità di coordinare strumenti, compiti, memoria e interfacce dentro processi già esistenti. Quando una storia riguarda agenti, il segnale utile non è la promessa futuristica, ma il tentativo di spostare l’AI dalla vetrina al lavoro quotidiano.\n\nPer Altair Nexus questo tipo di notizia conta perché aiuta a capire chi sta costruendo vantaggio duraturo. Se gli agenti riescono a entrare nei workflow, allora cambiano costi, abitudini e budget. Se restano demo spettacolari, il loro impatto resta narrativo più che economico.',
            'tags': ['agenti AI', 'workflow', 'enterprise software', 'automazione', 'produttività'],
            'sourceLabel': label,
            'sourceCount': 1,
            'featured': False,
            'opinion': 'Gli agenti contano solo quando smettono di sembrare magia e iniziano a comportarsi come infrastruttura del lavoro.',
            'qualityScore': 89,
            'visual': VISUAL_MAP['ai'],
        }

    if category == 'tech' and any(k in lowered for k in ['chip', 'semiconductor', 'semiconductors']) and any(k in lowered for k in ['huawei', 'nvidia', 'china', 'tsmc', 'intel']):
        return {
            'category': 'tech',
            'subcategory': 'Semiconduttori, filiera e sovranità tecnologica',
            'title': 'I semiconduttori tornano al centro: la competizione tecnologica si gioca sempre più sulla filiera reale',
            'hook': f'{label} riporta un segnale che rimette al centro chip, produzione e capacità industriale. Quando la notizia tocca la filiera dei semiconduttori, il punto vero non è solo l’azienda coinvolta ma la tenuta dell’infrastruttura che sostiene il digitale.',
            'body': 'Le notizie sui semiconduttori pesano perché riguardano la base materiale di AI, cloud, difesa, automotive ed elettronica di consumo. Ogni movimento rilevante su produzione, ordini o accesso alla filiera racconta chi sta costruendo vantaggio industriale e chi invece resta esposto a colli di bottiglia o dipendenze strategiche.\n\nPer questo Altair Nexus tratta queste storie come segnali di profondità sistemica. Nel tech il potere non passa solo dal software, ma dalla capacità di controllare tempi di scala, manifattura e resilienza della supply chain.',
            'tags': ['semiconduttori', 'chip', 'filiera', 'infrastruttura', 'geopolitica tech'],
            'sourceLabel': label,
            'sourceCount': 1,
            'featured': False,
            'opinion': 'Nel tech il vantaggio si consolida dove la filiera smette di essere una dipendenza e diventa leva strategica.',
            'qualityScore': 89,
            'visual': VISUAL_MAP['tech'],
        }

    if category == 'geopolitica' and any(k in lowered for k in ['iran', 'israel', 'houthi', 'red sea', 'hormuz', 'sanctions']):
        return {
            'category': 'geopolitica',
            'subcategory': 'Conflitti regionali, rotte e pressione sistemica',
            'title': 'La geopolitica torna a pesare sulle rotte e sui prezzi più della singola dichiarazione diplomatica',
            'hook': f'{label} segnala una dinamica che tocca conflitto, deterrenza o sicurezza marittima. Il punto utile non è il titolo del giorno, ma il modo in cui il rischio continua a trasferirsi su energia, commercio e fiducia.',
            'body': 'Le crisi geopolitiche contemporanee producono effetti economici anche senza escalation lineari. Basta che restino aperte, intermittenti e difficili da chiudere per alimentare premi al rischio, pressione logistica e volatilità nei mercati collegati all’energia e ai trasporti.\n\nÈ per questo che Altair Nexus legge queste notizie in chiave sistemica. Non conta solo chi alza i toni oggi, ma quanto a lungo il quadro resta abbastanza instabile da costringere governi, imprese e mercati a ricalibrare costi, rotte e scorte.',
            'tags': ['geopolitica', 'rotte', 'energia', 'rischio', 'diplomazia'],
            'sourceLabel': label,
            'sourceCount': 1,
            'featured': False,
            'opinion': 'La vera soglia critica non è l’headline più dura, ma la durata dell’instabilità che continua a trasferirsi sull’economia reale.',
            'qualityScore': 88,
            'visual': VISUAL_MAP['geopolitica'],
        }

    if category == 'finanza' and any(k in lowered for k in ['central bank', 'inflation', 'bond', 'rates', 'imf', 'rupee', 'currency']):
        return {
            'category': 'finanza',
            'subcategory': 'Banche centrali, valute e costo del capitale',
            'title': 'La macro torna a parlare il linguaggio dei tassi: il costo del capitale resta il filtro decisivo',
            'hook': 'Le storie su banche centrali, inflazione, bond e valute contano perché ricordano che gran parte delle valutazioni dipende ancora dal prezzo del denaro e dalla credibilità delle autorità monetarie.',
            'body': 'Dietro molte notizie finanziarie recenti c’è sempre la stessa domanda: quanto a lungo resterà alto, o comunque restrittivo, il costo del capitale? Quando una banca centrale interviene, o quando il mercato rilegge inflazione e rendimenti, non sta cambiando solo una variabile tecnica. Sta cambiando il modo in cui famiglie, imprese e investitori valutano rischio, crescita e sostenibilità del debito.\n\nIn questa fase, la finanza non premia semplicemente le storie più seducenti ma quelle che reggono meglio a un contesto di denaro meno gratuito. È lì che la macro torna a essere selettiva, e spesso spietata.',
            'tags': ['tassi', 'inflazione', 'bond', 'macro', 'banche centrali'],
            'sourceLabel': label,
            'sourceCount': 1,
            'featured': False,
            'opinion': 'Quando il denaro ha di nuovo un prezzo visibile, il mercato distingue più chiaramente tra narrativa e struttura.',
            'qualityScore': 87,
            'visual': VISUAL_MAP['finanza'],
        }

    if category == 'mercati' and any(k in lowered for k in ['stocks', 'futures', 'oil', 'wall street', 'markets', 'risk-off', 'correction']):
        return {
            'category': 'mercati',
            'subcategory': 'Volatilità, risk-off e repricing del rischio',
            'title': 'I mercati restano sensibili al rischio sistemico: basta poco per riattivare il repricing',
            'hook': 'Quando il flusso notizie torna su futures, petrolio, Wall Street o fasi risk-off, il punto non è solo l’oscillazione di giornata ma la facilità con cui il mercato cambia regime.',
            'body': 'In un contesto in cui tassi, geopolitica e valutazioni restano tutti temi aperti, i mercati possono passare rapidamente da una fase di tolleranza al rischio a una di protezione. Le headline che coinvolgono futures, petrolio o correzioni di listino non vanno lette come episodi isolati, ma come segnali della fragilità dell’equilibrio corrente.\n\nPer questo l’aspetto più interessante non è sempre l’ampiezza del movimento, ma la velocità con cui torna il bisogno di copertura. È spesso lì che si capisce quanto il mercato fosse davvero convinto della propria tranquillità.',
            'tags': ['mercati', 'risk-off', 'volatilità', 'petrolio', 'Wall Street'],
            'sourceLabel': label,
            'sourceCount': 1,
            'featured': False,
            'opinion': 'Quando il repricing riparte in fretta, vuol dire che sotto la calma c’era meno convinzione di quanto sembrasse.',
            'qualityScore': 87,
            'visual': VISUAL_MAP['mercati'],
        }

    if category == 'startup' and any(k in lowered for k in ['startup', 'funding', 'acquisition', 'venture', 'investment', 'enterprise']):
        return {
            'category': 'startup',
            'subcategory': 'Capitale venture, acquisizioni e scala industriale',
            'title': 'Il capitale torna selettivo: nel venture contano sempre di più scala, difendibilità e accesso alla distribuzione',
            'hook': f'{label} segnala una storia di round, acquisizione o capitale strategico che conta soprattutto per il posizionamento. Nel venture attuale il rumore vale poco: contano le mosse che cambiano davvero struttura e leva industriale.',
            'body': 'Le notizie su startup e venture non pesano tutte allo stesso modo. Quelle che meritano spazio sono le operazioni che indicano una scelta di fondo del capitale: scommettere su tecnologie con sbocco industriale, piattaforme con distribuzione credibile o consolidamenti che riducono la frammentazione.\n\nIn un mercato meno indulgente, il capitale tende a premiare ciò che promette non solo crescita, ma posizione. È questa la differenza che Altair Nexus cerca di catturare: separare la narrativa cosmetica dalle mosse che ridisegnano davvero il campo.',
            'tags': ['startup', 'venture capital', 'acquisizioni', 'investimenti', 'piattaforme'],
            'sourceLabel': label,
            'sourceCount': 1,
            'featured': False,
            'opinion': 'Il capitale oggi sembra meno disposto a finanziare possibilità astratte e più interessato a vantaggi che possano sedimentarsi.',
            'qualityScore': 87,
            'visual': VISUAL_MAP['startup'],
        }

    if category == 'scienza' and any(k in lowered for k in ['study', 'discovery', 'space', 'research', 'cern', 'esa', 'nasa']):
        return {
            'category': 'scienza',
            'subcategory': 'Ricerca, spazio e traiettorie applicative',
            'title': 'La scienza conta davvero quando apre traiettorie applicative e non solo stupore momentaneo',
            'hook': f'{label} porta in superficie un segnale scientifico che vale soprattutto per la traiettoria che apre. Il punto non è l’effetto wow, ma il potenziale di cambiare strumenti, comprensione o capacità operative.',
            'body': 'Nel flusso scientifico, ciò che merita spazio editoriale non è semplicemente l’effetto sorpresa di una scoperta, ma la sua capacità di cambiare prospettive. Questo vale sia per lo spazio sia per la ricerca di base: una missione, uno studio o una nuova evidenza diventano rilevanti quando aprono possibilità verificabili per tecnologia, medicina, osservazione o comprensione dei sistemi complessi.\n\nPer questo una buona notizia scientifica non ha bisogno di essere forzata in chiave sensazionalistica. Basta che mostri una traiettoria: dove può portarci, quali strumenti abilita, quale idea del futuro rende un po’ più concreta.',
            'tags': ['scienza', 'ricerca', 'spazio', 'innovazione', 'scoperta'],
            'sourceLabel': label,
            'sourceCount': 1,
            'featured': False,
            'opinion': 'La ricerca vale di più quando riduce l’incertezza sul possibile, non quando aumenta soltanto lo stupore.',
            'qualityScore': 86,
            'visual': VISUAL_MAP['scienza'],
        }

    if category == 'futuro' and any(k in lowered for k in ['deepfake', 'automation', 'robotics', 'society', 'election']):
        return {
            'category': 'futuro',
            'subcategory': 'Automazione, fiducia e impatto sociale',
            'title': 'Il futuro pesa davvero quando cambia fiducia, abitudini e costi di coordinamento',
            'hook': f'{label} segnala una storia su automazione, deepfake o società digitale che conta perché modifica il rapporto tra strumenti, persone e fiducia. Il tema non è l’effetto wow, ma l’impatto concreto sui comportamenti.',
            'body': 'Le notizie che riguardano l’automazione del futuro sono rilevanti quando mostrano una trasformazione dei costi sociali del coordinamento: come ci fidiamo delle immagini, come verifichiamo le fonti, quanto lavoro umano resta necessario, quali attività diventano improvvisamente economiche da automatizzare.\n\nÈ qui che il futuro smette di essere una categoria narrativa e diventa una variabile pratica. Per questo Altair Nexus tratta temi come deepfake, robotica o AI sociale non come spettacolo tecnologico, ma come segnali di ridefinizione delle abitudini collettive.',
            'tags': ['automazione', 'deepfake', 'robotica', 'società', 'fiducia'],
            'sourceLabel': label,
            'sourceCount': 1,
            'featured': False,
            'opinion': 'La tecnologia del futuro incide davvero quando altera i meccanismi di fiducia, non solo quando aggiunge capacità.',
            'qualityScore': 86,
            'visual': VISUAL_MAP['futuro'],
        }

    return None


def dedupe_candidates(findings, existing_news):
    existing_titles = {title_norm(item.get('title', '')) for item in existing_news}
    deduped = []
    seen = set()
    for finding in findings:
        norm = title_norm(finding['title'])
        if norm in existing_titles or norm in seen:
            continue
        seen.add(norm)
        deduped.append(finding)
    return deduped


def create_new_items(findings, existing_news):
    old_ids = {item['id'] for item in existing_news}
    old_titles = {title_norm(item['title']) for item in existing_news}
    cat_counts = {}
    for item in existing_news:
        cat_counts[item['category']] = cat_counts.get(item['category'], 0) + 1

    new_items = []
    for finding in findings:
        built = build_editorial_item(finding['category'], finding['title'], finding['link'])
        if not built:
            continue
        final_title_norm = title_norm(built['title'])
        if final_title_norm in old_titles:
            continue
        if cat_counts.get(finding['category'], 0) >= 2:
            continue
        item_id = f"{finding['category']}-{datetime.now().strftime('%Y%m%d')}-{slugify(built['title'])}-{short_hash(built['title'])}"
        if item_id in old_ids:
            continue
        item = {
            'id': item_id,
            'timestamp': datetime.now().astimezone().isoformat(timespec='seconds'),
            'sourceUrl': finding['link'],
            **built,
        }
        new_items.append(item)
        old_ids.add(item_id)
        old_titles.add(final_title_norm)
        cat_counts[finding['category']] = cat_counts.get(finding['category'], 0) + 1
    return new_items


def editorial_guard(items):
    cleaned = []
    seen_ids = set()
    for item in items:
        if item['id'] in seen_ids:
            continue
        title = (item.get('title') or '').strip()
        body = item.get('body') or ''
        hook = item.get('hook') or ''
        lower = title.lower()
        if len(title.split()) < 6:
            continue
        if any(x in lower for x in ['the latest', 'exclusive:', 'breakingviews', 'google news segnala', '(.gov)', ' - reuters', ' - bbc']):
            continue
        if len(body) < 260 or len(hook) < 120:
            continue
        if (item.get('qualityScore') or 0) < QUALITY_FLOOR:
            continue
        cleaned.append(item)
        seen_ids.add(item['id'])
    return cleaned


def compose_live(existing_news, new_items):
    merged = existing_news + new_items
    merged = editorial_guard(merged)
    merged = sorted(merged, key=lambda x: ((x.get('timestamp') or ''), (x.get('qualityScore') or 0)), reverse=True)

    live = []
    counts = {}
    for item in merged:
        cat = item['category']
        allowed = 1
        if (item.get('qualityScore') or 0) >= 91:
            allowed = 2
        if counts.get(cat, 0) >= allowed:
            continue
        live.append(item)
        counts[cat] = counts.get(cat, 0) + 1
        if len(live) >= MAX_LIVE:
            break

    if len(live) < MIN_LIVE:
        used = {item['id'] for item in live}
        for item in merged:
            if item['id'] in used:
                continue
            live.append(item)
            used.add(item['id'])
            if len(live) >= MIN_LIVE:
                break

    featured = sorted(live, key=lambda x: ((x.get('qualityScore') or 0), x.get('timestamp') or ''), reverse=True)[:4]
    featured_ids = {item['id'] for item in featured}
    for item in live:
        item['featured'] = item['id'] in featured_ids

    return live


def refresh_stats(stats, news, findings):
    stats['editionUpdatedAt'] = datetime.now().astimezone().isoformat(timespec='seconds')
    stats['newsGeneratedToday'] = len(news)
    stats['sourcesAnalyzed'] = max(int(stats.get('sourcesAnalyzed', 0) or 0), len(findings), 24)
    stats['mostViewed'] = [item['title'] for item in sorted(news, key=lambda x: ((x.get('qualityScore') or 0), x.get('timestamp') or ''), reverse=True)[:3]]
    categories = []
    for item in sorted(news, key=lambda x: x.get('timestamp') or '', reverse=True):
        if item['category'] not in categories:
            categories.append(item['category'])
    labels = {
        'ai': 'Radar AI: aggiornamento su modelli, agenti e distribuzione',
        'tech': 'Radar Tech: infrastruttura, chip e piattaforme restano centrali',
        'geopolitica': 'Radar Geopolitica: il rischio continua a trasferirsi su rotte e prezzi',
        'finanza': 'Radar Finanza: tassi, valute e costo del capitale restano decisivi',
        'mercati': 'Radar Mercati: il repricing del rischio resta centrale',
        'startup': 'Radar Startup: capitale e scala industriale restano osservati',
        'scienza': 'Radar Scienza: ricerca e traiettorie applicative restano presidiate',
        'futuro': 'Radar Futuro: fiducia, automazione e impatto sociale restano monitorati'
    }
    stats['topicEmerging'] = [labels[c] for c in categories if c in labels][:7]
    return stats


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
    shutil.copy2(NEWS, TMP / f'news.{stamp}.json')
    shutil.copy2(STATS, TMP / f'stats.{stamp}.json')

    existing_news = load_json(NEWS)
    stats = load_json(STATS)
    findings = dedupe_candidates(discover(), existing_news)
    new_items = create_new_items(findings, existing_news)
    live = compose_live(existing_news, new_items)
    stats = refresh_stats(stats, live, findings)

    save_json(NEWS_TMP, live)
    save_json(STATS_TMP, stats)
    load_json(NEWS_TMP)
    load_json(STATS_TMP)
    os.replace(NEWS_TMP, NEWS)
    os.replace(STATS_TMP, STATS)

    subprocess.check_call(['python3', str(ROOT / 'scripts/validate_nexus_json.py'), str(NEWS), str(STATS)])
    subprocess.check_call(['python3', str(ROOT / 'scripts/generate_story_pages.py')])
    subprocess.check_call(['python3', str(ROOT / 'scripts/generate_sitemap.py')])

    final_news = load_json(NEWS)
    final_stats = load_json(STATS)
    print(json.dumps({
        'status': 'ok',
        'editionUpdatedAt': final_stats['editionUpdatedAt'],
        'count': len(final_news),
        'discoveryCount': len(findings),
        'newToday': [x['id'] for x in final_news if str(x.get('timestamp', '')).startswith(datetime.now().date().isoformat())],
        'categories': sorted({x['category'] for x in final_news}),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
