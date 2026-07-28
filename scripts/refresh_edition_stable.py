#!/usr/bin/env python3
import json, os, shutil, subprocess, urllib.request, urllib.parse, xml.etree.ElementTree as ET, hashlib, re, sys, html
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path('/root/.openclaw/workspace/aion-nexus')
DATA = ROOT / 'data'
TMP = ROOT / 'tmp' / 'stable-refresh-backups'
HEALTH_DIR = ROOT / 'tmp' / 'refresh-health'
PREVIEW_DIR = ROOT / 'tmp' / 'refresh-preview'
CANDIDATES_PATH = ROOT / 'tmp' / 'refresh-candidates.json'
NEWS = DATA / 'news.json'
STATS = DATA / 'stats.json'
NEWS_TMP = DATA / 'news.json.tmp'
STATS_TMP = DATA / 'stats.json.tmp'
HISTORY_DIR = DATA / 'history'

DISCOVERY_QUERIES = [
    ('ai', 'AI agents enterprise workflow copilots Anthropic OpenAI Google Nvidia site:reuters.com OR site:techcrunch.com OR site:venturebeat.com OR site:semafor.com OR site:anthropic.com OR site:nvidianews.nvidia.com'),
    ('tech', 'semiconductor chip Huawei Nvidia TSMC data center infrastructure networking site:reuters.com OR site:theverge.com OR site:techcrunch.com OR site:arstechnica.com OR site:ieee.org OR site:nvidianews.nvidia.com'),
    ('geopolitica', 'Iran Israel Houthi Hormuz Red Sea sanctions diplomacy shipping energy site:reuters.com OR site:apnews.com OR site:bbc.com OR site:theguardian.com OR site:politico.com'),
    ('finanza', 'inflation rates bonds IMF currency central bank debt Fed ECB BIS site:reuters.com OR site:cnbc.com OR site:marketwatch.com OR site:ft.com OR site:bloomberg.com OR site:wsj.com'),
    ('mercati', 'oil wall street futures correction volatility risk-off freight yields commodities site:reuters.com OR site:cnbc.com OR site:marketwatch.com OR site:ft.com OR site:bloomberg.com OR site:wsj.com'),
    ('startup', 'startup funding venture acquisition enterprise software robotics site:reuters.com OR site:techcrunch.com OR site:tech.eu OR site:sifted.eu OR site:axios.com OR site:theinformation.com'),
    ('scienza', 'study discovery NASA ESA CERN science research site:reuters.com OR site:nature.com OR site:science.org OR site:scientificamerican.com OR site:newscientist.com'),
    ('futuro', 'deepfake automation robotics society trust elections AI media site:reuters.com OR site:theverge.com OR site:bbc.com OR site:technologyreview.com OR site:arstechnica.com OR site:semafor.com')
]

DISCOVERY_FEEDS = {
    'ai': [
        {'url': 'https://blog.google/technology/ai/rss/', 'tier': 'high'},
        {'url': 'https://www.wired.com/feed/tag/ai/latest/rss', 'tier': 'medium'},
        {'url': 'https://techcrunch.com/feed/', 'tier': 'medium'},
        {'url': 'https://feeds.feedburner.com/venturebeat/SZYF', 'tier': 'medium'},
        {'url': 'https://www.semafor.com/tech/rss.xml', 'tier': 'medium'},
        {'url': 'https://nvidianews.nvidia.com/rss.xml', 'tier': 'high'},
    ],
    'tech': [
        {'url': 'https://www.theverge.com/rss/index.xml', 'tier': 'medium'},
        {'url': 'https://techcrunch.com/feed/', 'tier': 'medium'},
        {'url': 'https://blog.google/technology/ai/rss/', 'tier': 'high'},
        {'url': 'https://feeds.arstechnica.com/arstechnica/index', 'tier': 'medium'},
        {'url': 'https://spectrum.ieee.org/rss/fulltext', 'tier': 'medium'},
        {'url': 'https://nvidianews.nvidia.com/rss.xml', 'tier': 'high'},
    ],
    'geopolitica': [
        {'url': 'https://feeds.bbci.co.uk/news/world/rss.xml', 'tier': 'high'},
        {'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'tier': 'medium'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml', 'tier': 'high'},
        {'url': 'https://www.theguardian.com/world/rss', 'tier': 'high'},
    ],
    'finanza': [
        {'url': 'https://feeds.marketwatch.com/marketwatch/topstories/', 'tier': 'medium'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml', 'tier': 'high'},
        {'url': 'https://www.ft.com/rss/home', 'tier': 'high'},
        {'url': 'https://www.ecb.europa.eu/rss/press.html', 'tier': 'high'},
    ],
    'mercati': [
        {'url': 'https://feeds.marketwatch.com/marketwatch/topstories/', 'tier': 'medium'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml', 'tier': 'high'},
        {'url': 'https://www.ft.com/rss/home', 'tier': 'high'},
        {'url': 'https://www.ft.com/markets?format=rss', 'tier': 'high'},
    ],
    'scienza': [
        {'url': 'https://www.nature.com/nature.rss', 'tier': 'high'},
        {'url': 'https://www.science.org/rss/news_current.xml', 'tier': 'high'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Science.xml', 'tier': 'high'},
        {'url': 'https://www.scientificamerican.com/feed/', 'tier': 'medium'},
    ],
    'startup': [
        {'url': 'https://techcrunch.com/category/startups/feed/', 'tier': 'medium'},
        {'url': 'https://sifted.eu/feed', 'tier': 'medium'},
        {'url': 'https://news.crunchbase.com/feed/', 'tier': 'medium'},
        {'url': 'https://www.axios.com/feeds/feed.rss', 'tier': 'medium'},
    ],
    'futuro': [
        {'url': 'https://www.theverge.com/rss/index.xml', 'tier': 'medium'},
        {'url': 'https://www.wired.com/feed/tag/ai/latest/rss', 'tier': 'medium'},
        {'url': 'https://blog.google/technology/ai/rss/', 'tier': 'high'},
        {'url': 'https://www.technologyreview.com/feed/', 'tier': 'medium'},
        {'url': 'https://feeds.arstechnica.com/arstechnica/index', 'tier': 'medium'},
    ],
}

ROTATING_DISCOVERY_QUERIES = {
    'ai': [
        'AI agents enterprise automation workflow copilots memory tools site:reuters.com OR site:venturebeat.com OR site:techcrunch.com OR site:semafor.com',
        'AI enterprise assistants software workplace orchestration site:reuters.com OR site:venturebeat.com OR site:theverge.com OR site:anthropic.com'
    ],
    'tech': [
        'semiconductor packaging memory servers data center power networking site:reuters.com OR site:theverge.com OR site:techcrunch.com OR site:arstechnica.com',
        'AI infrastructure servers networking chip packaging site:reuters.com OR site:theverge.com OR site:techcrunch.com OR site:ieee.org'
    ],
    'mercati': [
        'oil volatility futures defensives yields freight risk-off site:reuters.com OR site:cnbc.com OR site:marketwatch.com OR site:ft.com',
        'wall street volatility commodities yields sentiment correction site:reuters.com OR site:cnbc.com OR site:marketwatch.com OR site:bloomberg.com'
    ],
    'geopolitica': [
        'Iran Hormuz Red Sea shipping energy sanctions diplomacy site:reuters.com OR site:apnews.com OR site:bbc.com OR site:theguardian.com',
        'Middle East shipping chokepoints oil routes diplomacy risk site:reuters.com OR site:bbc.com OR site:politico.com OR site:ft.com'
    ],
    'startup': [
        'startup funding enterprise AI software venture site:techcrunch.com OR site:sifted.eu OR site:axios.com OR site:theinformation.com',
        'robotics startup acquisition funding enterprise tools site:reuters.com OR site:tech.eu OR site:crunchbase.com OR site:techcrunch.com'
    ]
}

VISUAL_MAP = {'ai':'ai','tech':'tech','geopolitica':'geo','finanza':'fin','mercati':'markets','startup':'startup','scienza':'science','futuro':'future'}
QUALITY_FLOOR = 84
MAX_LIVE = 10
MIN_LIVE = 6
MAX_NEW_PER_REFRESH = 8
MIN_NEW_PER_REFRESH = 4
MAX_CATEGORY_COUNT = 2
MAX_CATEGORY_COUNT_HIGH_QUALITY = 2
HIGH_QUALITY_SECOND_SLOT = 92

FORMAT_BLUEPRINTS = {
    'standard_analysis': {'label': 'standard_analysis', 'lead': 'analysis', 'body_style': 'three_paragraphs'},
    'quick_brief': {'label': 'quick_brief', 'lead': 'fact_first', 'body_style': 'quick_brief'},
    'scenario_watch': {'label': 'scenario_watch', 'lead': 'consequence_first', 'body_style': 'scenario_watch'},
    'actor_focus': {'label': 'actor_focus', 'lead': 'actor_first', 'body_style': 'actor_focus'},
}

SCENARIO_CATEGORY = {
    'ai_agents': 'ai',
    'tech_semis': 'tech',
    'geo_conflict': 'geopolitica',
    'macro_rates': 'finanza',
    'market_repricing': 'mercati',
    'startup_capital': 'startup',
    'science_milestone': 'scienza',
    'future_society': 'futuro',
}

SCENARIO_SUBCATEGORY = {
    'ai_agents': 'Agenti AI, workflow e distribuzione enterprise',
    'tech_semis': 'Semiconduttori, filiera e sovranità tecnologica',
    'geo_conflict': 'Conflitti regionali, rotte e trasmissione del rischio',
    'macro_rates': 'Tassi, valute e costo del capitale',
    'market_repricing': 'Repricing, risk-off e vulnerabilità del sentiment',
    'startup_capital': 'Venture, funding e scala industriale',
    'science_milestone': 'Ricerca, spazio e traiettorie applicative',
    'future_society': 'Automazione, fiducia e coordinamento sociale',
}

NARRATIVE_VOCAB = {
    'geo_iran_routes': {'iran','israel','houthi','hormuz','red','sea','shipping','rotte','routes','guerra','war','crisi','conflitto'},
    'energy_risk_oil': {'oil','petrolio','energy','energia','futures','commodity','commodities','brent','risk-off','volatility','volatilità'},
    'macro_imf_rates_fx': {'imf','inflation','inflazione','rates','tassi','bond','currency','valuta','debito','debt','yield','macro'},
    'ai_agents_enterprise': {'ai','agent','agents','agenti','workflow','copilot','enterprise','software','automation','automazione'},
    'chips_supply_chain': {'chip','chips','semiconductor','semiconduttori','filiera','supply','chain','nvidia','huawei','tsmc','infrastructure','infrastruttura'},
    'future_trust_media': {'deepfake','robocall','trust','fiducia','media','society','società','election','elections','fake'},
    'science_research': {'science','scienza','research','ricerca','study','discovery','space','spazio','nasa','esa','cern'},
    'startup_capital': {'startup','funding','venture','seed','acquisition','capital','capitale','round','investimento','investment'},
}


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; AION-NEXUS/1.0)'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'ignore')


def fetch_response(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; AION-NEXUS/1.0)'})
    return urllib.request.urlopen(req, timeout=timeout)


def strip_html_text(value):
    value = html.unescape(value or '')
    value = re.sub(r'<script.*?</script>', ' ', value, flags=re.S | re.I)
    value = re.sub(r'<style.*?</style>', ' ', value, flags=re.S | re.I)
    value = re.sub(r'<[^>]+>', ' ', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def extract_article_text(raw_html):
    text = raw_html or ''
    candidates = re.findall(r'<p[^>]*>(.*?)</p>', text, flags=re.S | re.I)
    cleaned = [strip_html_text(chunk) for chunk in candidates]
    cleaned = [chunk for chunk in cleaned if len(chunk) >= 80]
    if cleaned:
        merged = "\n\n".join(cleaned)
        if len(merged) >= 500:
            return merged[:6000]
    fallback = strip_html_text(text)
    return fallback[:6000]


def parse_pub_date(value):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone().isoformat(timespec='seconds')
    except Exception:
        return None


def resolve_google_news_url(url, timeout=20):
    if not url:
        return url
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    if 'news.google.com' not in host:
        return url
    article_id = parsed.path.rsplit('/', 1)[-1]
    feed_api = f'https://news.google.com/rss/articles/{article_id}'
    try:
        raw = fetch(feed_api, timeout=timeout)
        root = ET.fromstring(raw)
        item = root.find('.//item')
        if item is not None:
            source = item.find('source')
            source_text = (source.text or '').strip() if source is not None else ''
            description = item.findtext('description') or ''
            hrefs = re.findall(r'href="([^"]+)"', description)
            for href in hrefs:
                clean = href.strip()
                if clean and 'news.google.com' not in urllib.parse.urlparse(clean).netloc.lower():
                    return clean
            if source_text:
                for href in hrefs:
                    if source_text.lower().replace(' ', '') in href.lower().replace(' ', ''):
                        return href
    except Exception:
        pass
    return url


def enrich_signal_source(signal, timeout=20):
    original_link = signal.get('link') or ''
    discovery_source = signal.get('discoverySource') or ''
    if discovery_source == 'direct-rss':
        source_url = original_link
    else:
        resolved_url = resolve_google_news_url(original_link, timeout=timeout)
        source_url = resolved_url or original_link
    source_text = ''
    source_excerpt = ''
    fetch_status = 'unfetched'
    try:
        with fetch_response(source_url, timeout=timeout) as response:
            final_url = response.geturl() or source_url
            raw = response.read().decode('utf-8', 'ignore')
            source_text = extract_article_text(raw)
            source_url = final_url
            fetch_status = 'ok' if source_text else 'empty'
    except Exception:
        fetch_status = 'fetch_failed'
    if source_text:
        source_excerpt = source_text[:2000]
    meta = resolve_source_metadata(signal.get('title', ''), source_url)
    signal.update({
        'sourceUrlResolved': source_url,
        'sourceText': source_excerpt,
        'sourceTextLength': len(source_text),
        'sourceFetchStatus': fetch_status,
        'sourceLabelGuess': meta['sourceLabel'],
        'sourceTier': meta['sourceTier'],
        'sourceHost': meta['sourceHost'],
    })
    return signal


def generate_editorial_content(signal, scenario, source_label):
    source_text = (signal.get('sourceText') or '').strip()
    if len(source_text) < 500:
        return None

    original_title = clean_raw_title(signal.get('title', ''))
    blueprint = choose_format_blueprint(signal, scenario, signal.get('title', ''))
    fallback_hook = unique_hook(signal, scenario, blueprint)
    base_tokens = [tok for tok in text_tokens(original_title) if tok not in {'reuters', 'news', 'update', 'latest'}]

    translation_map = {
        'ai_agents': {
            'title_prefix': 'L’AI esce dalla demo',
            'hook': 'Il segnale rilevante è se l’intelligenza artificiale riesce a entrare davvero in prodotti, processi e budget reali.',
            'body': [
                'Il cuore della storia non è l’effetto vetrina, ma la capacità di trasformare l’AI in un pezzo stabile del lavoro quotidiano.',
                'Il punto è capire se il segnale riguarda adozione, distribuzione e affidabilità, non solo entusiasmo tecnologico.',
                'Se questa traiettoria regge, il vantaggio competitivo si sposta dalla demo alla continuità operativa.',
            ],
            'opinion': 'Il passaggio decisivo arriva quando l’AI smette di stupire e inizia davvero a lavorare.',
        },
        'tech_semis': {
            'title_prefix': 'La filiera tecnologica si irrigidisce',
            'hook': 'Qui si vede dove si accumulano potere industriale, capacità produttiva e dipendenze strategiche.',
            'body': [
                'La competizione tecnologica non si gioca solo sul prodotto finale, ma sulla tenuta della filiera.',
                'Conta la capacità di trasformare domanda, infrastruttura e componenti in esecuzione continua.',
                'Il tema va letto come indicatore di forza industriale prima ancora che come singola headline tech.',
            ],
            'opinion': 'Nel tech conta meno il proclama e più la capacità di tenere la filiera sotto controllo.',
        },
        'geo_conflict': {
            'title_prefix': 'Il rischio geopolitico si allarga',
            'hook': 'Una crisi regionale smette in fretta di essere locale quando tocca rotte, assicurazioni ed energia.',
            'body': [
                'Il punto non è solo l’episodio, ma il modo in cui l’instabilità si trasferisce nell’economia reale.',
                'Quando tensione, logistica e prezzi iniziano a muoversi insieme, i mercati trattano il rischio come qualcosa di più strutturale.',
                'Sono segnali di attrito persistente, non semplice rumore del giorno.',
            ],
            'opinion': 'La soglia critica non è il titolo del giorno, ma la durata del disordine che si deposita sui flussi reali.',
        },
        'macro_rates': {
            'title_prefix': 'Il capitale torna selettivo',
            'hook': 'Torna al centro il costo della stabilità, del debito e della crescita.',
            'body': [
                'Il nodo da osservare è come cambiano le attese su tassi, valuta e sostenibilità finanziaria.',
                'Quando il denaro costa di più, il mercato distingue più rapidamente tra strutture robuste e fragilità coperte dalla liquidità.',
                'Il valore della storia sta nel segnale di selettività che può trascinare su credito, investimenti e fiducia.',
            ],
            'opinion': 'Quando il capitale torna a pesare, la differenza tra solidità e narrazione diventa molto più visibile.',
        },
        'market_repricing': {
            'title_prefix': 'I mercati tornano a coprirsi',
            'hook': 'Sta emergendo un repricing del rischio che può cambiare tono e ampiezza dei movimenti.',
            'body': [
                'Il punto utile non è solo la variazione di giornata, ma la velocità con cui torna il bisogno di protezione.',
                'Se energia, geopolitica e sentiment iniziano a convergere, il mercato tende a ricalibrare il prezzo del rischio in modo più severo.',
                'Sono passaggi in cui il rumore tattico può diventare revisione di struttura.',
            ],
            'opinion': 'Quando il repricing accelera, quasi sempre significa che la calma precedente era meno solida di quanto sembrasse.',
        },
        'startup_capital': {
            'title_prefix': 'Il venture sceglie con più durezza',
            'hook': 'Qui si vede dove il capitale continua a riconoscere scala, distribuzione e difendibilità.',
            'body': [
                'Il valore della storia non è solo nel round o nel nome coinvolto, ma nel tipo di struttura che il mercato sta premiando.',
                'In una fase più selettiva, il capitale guarda con più attenzione a esecuzione, accesso e tenuta del modello.',
                'È così che il venture smette di essere solo narrativa e diventa disciplina industriale.',
            ],
            'opinion': 'Il capitale è più utile dei pitch quando inizia a premiare chi può reggere oltre l’hype.',
        },
        'science_milestone': {
            'title_prefix': 'Una scoperta apre una traiettoria',
            'hook': 'Riduce un po’ l’incertezza su ciò che diventa concretamente possibile.',
            'body': [
                'Il punto non è solo l’effetto sorpresa, ma la direzione che una scoperta o un risultato di ricerca rende più credibile.',
                'Il valore editoriale sta nel capire se la novità apre strumenti, applicazioni o nuovi margini di osservazione.',
                'La scienza pesa davvero quando modifica lentamente il campo delle ipotesi praticabili, non solo il ciclo dell’attenzione.',
            ],
            'opinion': 'Una buona notizia scientifica conta quando rende il futuro un po’ meno speculativo.',
        },
        'future_society': {
            'title_prefix': 'La tecnologia cambia il costo della fiducia',
            'hook': 'Qui entrano in gioco i meccanismi con cui persone, media e organizzazioni distinguono il vero dal plausibile.',
            'body': [
                'Il tema vero non è solo la nuova capacità tecnica, ma il costo sociale che può generare in verifica, coordinamento e difesa.',
                'Quando automazione, modelli e strumenti intelligenti avanzano, cambia anche il modo in cui istituzioni e piattaforme devono proteggersi.',
                'Sono indizi di trasformazione culturale prima ancora che regolatoria.',
            ],
            'opinion': 'La tecnologia incide davvero quando costringe a spendere di più per fidarsi del reale.',
        },
    }

    profile = translation_map.get(scenario)
    if not profile:
        return None

    source_lead = trim_sentence(source_text.split('\n\n')[0], 420)
    source_mid = trim_sentence(source_text.split('\n\n')[1] if '\n\n' in source_text else source_text, 420)
    source_tail = trim_sentence(source_text.split('\n\n')[2] if source_text.count('\n\n') >= 2 else source_text, 420)

    def italian_focus_from_title(title):
        cleaned = clean_raw_title(title)
        replacements = {
            'cost': 'costi', 'reliability': 'affidabilità', 'news': 'novità', 'latest': 'ultime mosse',
            'rescued': 'salvato', 'wounded': 'ferito', 'airman': 'militare', 'launches': 'lancio',
            'agent': 'agente', 'agents': 'agenti', 'video': 'video', 'model': 'modello',
            'models': 'modelli', 'market': 'mercato', 'markets': 'mercati', 'science': 'ricerca',
            'startup': 'startup', 'chips': 'chip', 'chip': 'chip', 'trust': 'fiducia',
        }
        words = []
        for raw in re.findall(r"[A-Za-zÀ-ÿ0-9']+", cleaned):
            low = raw.lower()
            mapped = replacements.get(low)
            if mapped:
                words.append(mapped)
            elif raw[:1].isupper() or raw.isupper():
                words.append(raw)
            elif low in {'google', 'gemini', 'huawei', 'nature', 'wired', 'cursor', 'polymarket', 'bbc'}:
                words.append(raw)
        if not words:
            return profile['title_prefix']
        return ' '.join(words[:5])

    focus = italian_focus_from_title(original_title)
    title = trim_sentence(f"{profile['title_prefix']}: {focus}", 90)
    hook = trim_sentence(profile['hook'], 200)
    if len(hook) < 80:
        hook = trim_sentence(fallback_hook, 200)

    body_parts = [
        trim_sentence(f"{source_lead} {profile['body'][0]}", 460),
        trim_sentence(f"{source_mid} {profile['body'][1]}", 460),
        trim_sentence(f"{source_tail} {profile['body'][2]}", 460),
    ]
    body = "\n\n".join(body_parts)
    body = trim_sentence(body, 1500)
    if len(body) < 500:
        return None

    opinion = trim_sentence(profile['opinion'], 150)

    tags = []
    seen = set()
    category_label = SCENARIO_CATEGORY.get(scenario, signal.get('category', ''))
    tag_map = {
        'ai_agents': ['agenti AI', 'software', 'workflow', 'produttività', 'modelli'],
        'tech_semis': ['chip', 'filiera', 'infrastruttura', 'tecnologia', 'industria'],
        'geo_conflict': ['geopolitica', 'rotte', 'energia', 'rischio', 'conflitto'],
        'macro_rates': ['tassi', 'debito', 'valute', 'capitale', 'macro'],
        'market_repricing': ['mercati', 'volatilità', 'rischio', 'energia', 'listini'],
        'startup_capital': ['startup', 'venture', 'finanziamenti', 'scala', 'capitale'],
        'science_milestone': ['scienza', 'ricerca', 'scoperta', 'innovazione', 'osservazione'],
        'future_society': ['fiducia', 'automazione', 'media', 'società', 'tecnologia'],
    }
    for tok in tag_map.get(scenario, []):
        key = tok.lower()
        if key not in seen:
            tags.append(tok)
            seen.add(key)
    for tok in [category_label, source_label, 'analisi', 'Altair Nexus']:
        key = str(tok).lower()
        if key not in seen:
            tags.append(tok)
            seen.add(key)
        if len(tags) >= 5:
            break

    quality = 84 + min(13, max(0, len(source_text) // 350))
    return {
        'title': title,
        'hook': hook,
        'body': body,
        'opinion': opinion,
        'tags': tags[:5],
        'qualityScore': max(84, min(97, int(quality))),
    }


def slugify(text):
    s = text.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s[:70]


def short_hash(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:10]


def title_norm(text):
    return re.sub(r'\s+', ' ', (text or '').strip().lower())


def text_tokens(text):
    return [t for t in re.findall(r'[a-z0-9àèéìòù]+', title_norm(text)) if len(t) > 2]


def source_label(link, title=''):
    host = urllib.parse.urlparse(link).netloc.lower().replace('www.', '')
    if 'reuters.com' in host:
        return 'Reuters'
    if 'apnews.com' in host:
        return 'AP'
    if 'aljazeera.com' in host:
        return 'Al Jazeera'
    if 'techcrunch.com' in host:
        return 'TechCrunch'
    if 'theverge.com' in host:
        return 'The Verge'
    if 'venturebeat.com' in host or 'feeds.feedburner.com' in host:
        return 'VentureBeat'
    if 'marketwatch.com' in host:
        return 'MarketWatch'
    if 'cnbc.com' in host:
        return 'CNBC'
    if 'nature.com' in host:
        return 'Nature'
    if 'science.org' in host:
        return 'Science'
    if 'bbc.co.uk' in host or 'bbc.com' in host:
        return 'BBC'
    if 'wired.com' in host:
        return 'Wired'
    if 'sifted.eu' in host:
        return 'Sifted'
    if 'ft.com' in host:
        return 'FT'
    if 'bloomberg.com' in host:
        return 'Bloomberg'
    if 'wsj.com' in host:
        return 'WSJ'
    if 'nytimes.com' in host:
        return 'NYT'
    if 'semafor.com' in host:
        return 'Semafor'
    if 'arstechnica.com' in host:
        return 'Ars Technica'
    if 'ieee.org' in host or 'spectrum.ieee.org' in host:
        return 'IEEE Spectrum'
    if 'theguardian.com' in host:
        return 'Guardian'
    if 'politico.com' in host:
        return 'Politico'
    if 'axios.com' in host:
        return 'Axios'
    if 'theinformation.com' in host:
        return 'The Information'
    if 'nvidianews.nvidia.com' in host or host == 'nvidia.com' or host.endswith('.nvidia.com'):
        return 'Nvidia'
    if 'anthropic.com' in host:
        return 'Anthropic'
    if 'scientificamerican.com' in host:
        return 'Scientific American'
    if 'technologyreview.com' in host:
        return 'MIT Technology Review'
    if 'newscientist.com' in host:
        return 'New Scientist'
    if 'ecb.europa.eu' in host:
        return 'ECB'
    if host == 'bis.org' or host.endswith('.bis.org'):
        return 'BIS'
    return host or 'Source review pending'


def classify_source_tier(label):
    if label in {'Reuters', 'AP', 'BBC', 'Nature', 'Science', 'FT', 'Bloomberg', 'WSJ', 'NYT', 'Guardian', 'ECB', 'BIS'}:
        return 'high'
    if label in {'CNBC', 'MarketWatch', 'The Verge', 'TechCrunch', 'VentureBeat', 'Al Jazeera', 'Wired', 'Sifted', 'Semafor', 'Ars Technica', 'IEEE Spectrum', 'Politico', 'Axios', 'The Information', 'Nvidia', 'Anthropic', 'Scientific American', 'MIT Technology Review', 'New Scientist'}:
        return 'medium'
    return 'review'


def resolve_source_metadata(title, link):
    label = source_label(link, title)
    return {
        'sourceLabel': label,
        'sourceUrl': link,
        'sourceTier': classify_source_tier(label),
        'sourceHost': urllib.parse.urlparse(link).netloc.lower().replace('www.', ''),
    }


def usable_headline(title, link):
    t = title_norm(title)
    if not t or len(t.split()) < 6:
        return False
    bad = ['the latest:', 'exclusive:', 'breakingviews', 'tech news |', 'world news |', 'business news |', 'markets news |', 'live updates', 'roundup', 'what we know']
    if any(x in t for x in bad):
        return False
    return True


def clean_raw_title(raw_title):
    return re.sub(r'\s+-\s+(Reuters|AP News|BBC|CNBC|MarketWatch|TechCrunch|The Verge|VentureBeat|Nature|Science|Al Jazeera|apnews\.com|marketwatch\.com)\s*$', '', raw_title).strip()


def canonical_signal_key(category, raw_title):
    text = title_norm(clean_raw_title(raw_title))
    toks = [t for t in text_tokens(text) if t not in {'says','say','amid','after','over','into','with','from','site','news','latest','update'}]
    return f"{category}:{'-'.join(toks[:8])}"


def classify_signal_scenario(category, raw_title):
    lowered = title_norm(raw_title)
    if category == 'ai' and any(k in lowered for k in ['agent', 'agents', 'assistant', 'workflow', 'copilot']):
        return 'ai_agents'
    if category == 'tech' and any(k in lowered for k in ['chip', 'semiconductor', 'nvidia', 'huawei', 'intel', 'tsmc', 'data center', 'server']):
        return 'tech_semis'
    if category == 'geopolitica' and any(k in lowered for k in ['iran', 'israel', 'houthi', 'red sea', 'hormuz', 'war', 'sanction']):
        return 'geo_conflict'
    if category == 'finanza' and any(k in lowered for k in ['inflation', 'bond', 'rates', 'imf', 'currency', 'growth forecast', 'debt']):
        return 'macro_rates'
    if category == 'mercati' and any(k in lowered for k in ['stocks', 'wall street', 'oil', 'futures', 'correction', 'risk-off', 'volatility']):
        return 'market_repricing'
    if category == 'startup' and any(k in lowered for k in ['startup', 'funding', 'seed', 'acquisition', 'venture', 'series a', 'series b']):
        return 'startup_capital'
    if category == 'scienza' and any(k in lowered for k in ['study', 'research', 'mission', 'space', 'discovery', 'science']):
        return 'science_milestone'
    if category == 'futuro' and any(k in lowered for k in ['deepfake', 'robocall', 'automation', 'robotics', 'society', 'election', 'trust']):
        return 'future_society'
    fallback = {
        'ai': 'ai_agents',
        'tech': 'tech_semis',
        'geopolitica': 'geo_conflict',
        'finanza': 'macro_rates',
        'mercati': 'market_repricing',
        'startup': 'startup_capital',
        'scienza': 'science_milestone',
        'futuro': 'future_society',
    }
    return fallback.get(category)


def italianize_title(raw_title, scenario):
    clean = clean_raw_title(raw_title)
    tokens = [t for t in re.findall(r"[A-Za-zÀ-ÿ0-9']+", clean) if len(t) > 2]
    focus = ' '.join(tokens[:5]).strip()
    if not focus:
        return clean
    if scenario == 'tech_semis':
        return f"Chip e infrastruttura: {focus} sotto pressione industriale"
    if scenario == 'market_repricing':
        return f"Mercati sotto stress: {focus} rimette il rischio nei prezzi"
    if scenario == 'macro_rates':
        return f"Finanza globale: {focus} riporta tassi e debito al centro"
    if scenario == 'geo_conflict':
        return f"Geopolitica in tensione: {focus} amplia l’onda del rischio"
    if scenario == 'ai_agents':
        return f"AI e prodotti: {focus} segnala un salto oltre la demo"
    if scenario == 'startup_capital':
        return f"Startup e capitale: {focus} misura la selezione del venture"
    if scenario == 'science_milestone':
        return f"Scienza in movimento: {focus} apre una traiettoria concreta"
    if scenario == 'future_society':
        return f"Tecnologia e fiducia: {focus} alza il costo del coordinamento"
    return clean


def choose_format_blueprint(signal, scenario, raw_title):
    lowered = title_norm(raw_title)
    source_tier = signal.get('sourceTier')
    if scenario in {'geo_conflict', 'market_repricing', 'macro_rates'}:
        return FORMAT_BLUEPRINTS['scenario_watch']
    if scenario in {'ai_agents', 'startup_capital'}:
        return FORMAT_BLUEPRINTS['actor_focus']
    if any(k in lowered for k in ['update', 'launches', 'launch', 'wins', 'gets', 'secures', 'raises', 'backs', 'signs']):
        return FORMAT_BLUEPRINTS['quick_brief']
    if source_tier == 'high' and scenario in {'science_milestone', 'tech_semis'}:
        return FORMAT_BLUEPRINTS['quick_brief']
    return FORMAT_BLUEPRINTS['standard_analysis']


def trim_sentence(text, limit):
    text = re.sub(r'\s+', ' ', text or '').strip()
    if len(text) <= limit:
        return text
    clipped = text[:limit]
    if ' ' in clipped:
        clipped = clipped.rsplit(' ', 1)[0]
    return clipped.rstrip(' ,;:') + '…'


def source_sentences(source_text, min_len=40):
    blocked_fragments = [
        'subscribe', 'sign in', 'close search', 'most read', 'see all', 'learn more',
        'feed subscribe', 'global (english)', 'world sections', 'home world sections',
        'inside google', 'around the globe', 'life at google', 'developer tools',
        'google play', 'google nest', 'fitbit', 'chromebooks', 'products developer tools',
        'infrastructure & cloud', 'devices pixel', 'leadership sundar pichai'
    ]
    sentences = []
    for raw in re.split(r'(?<=[\.!?])\s+', source_text or ''):
        s = raw.strip()
        if len(s) < min_len:
            continue
        lowered = s.lower()
        if any(fragment in lowered for fragment in blocked_fragments):
            continue
        alpha_words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", s)
        if len(alpha_words) < 8:
            continue
        english_word_hits = sum(1 for word in ['the','and','with','from','this','that','these','those','market','latest','products','devices','leadership','subscribe'] if re.search(rf'\b{word}\b', lowered))
        italian_word_hits = sum(1 for word in ['il','lo','la','i','gli','le','un','una','con','per','nel','della','delle','degli','che','questo','questa'] if re.search(rf'\b{word}\b', lowered))
        if english_word_hits >= 3 and italian_word_hits == 0:
            continue
        sentences.append(s)
    return sentences


def source_keywords(signal, scenario, limit=5):
    stop = {
        'reuters', 'news', 'latest', 'update', 'says', 'after', 'amid', 'with', 'from',
        'this', 'that', 'their', 'about', 'into', 'over', 'site', 'briefing', 'analysis'
    }
    preferred = [
        tok for tok in text_tokens(' '.join([
            signal.get('title', ''),
            signal.get('sourceText', ''),
            scenario.replace('_', ' '),
        ]))
        if tok not in stop
    ]
    ordered = []
    seen = set()
    for tok in preferred:
        if tok in seen:
            continue
        seen.add(tok)
        ordered.append(tok)
        if len(ordered) >= limit:
            break
    return ordered


def build_source_driven_fallback(signal, scenario, meta, blueprint):
    source_text = (signal.get('sourceText') or '').strip()
    lowered_source = source_text.lower()
    noisy_markers = [
        'subscribe', 'sign in', 'close search', 'most read', 'see all', 'feed subscribe',
        'products developer tools', 'infrastructure & cloud', 'inside google', 'around the globe',
        'leadership sundar pichai', 'devices pixel', 'google nest', 'chromebooks'
    ]
    if len(source_text) < 220:
        return None
    if sum(1 for marker in noisy_markers if marker in lowered_source) >= 2:
        return None

    sentences = source_sentences(source_text)
    if len(sentences) < 2:
        return None

    fallback_title = italianize_title(signal['title'], scenario)
    fallback_hook = unique_hook(signal, scenario, blueprint)
    keywords = source_keywords(signal, scenario)

    lead = sentences[0]
    support = sentences[1] if len(sentences) > 1 else ''
    depth = next((s for s in sentences[2:] if not too_similar(s, lead)), support)

    if blueprint.get('lead') == 'fact_first':
        hook = trim_sentence(lead, 200)
    elif blueprint.get('lead') == 'actor_first':
        hook = trim_sentence(f"{meta['sourceLabel']} mette a fuoco {lead.lower()}", 200)
    elif blueprint.get('lead') == 'consequence_first':
        hook = trim_sentence(f"{fallback_hook} {support}", 200)
    else:
        hook = trim_sentence(f"{lead} {fallback_hook}", 200)
    if len(hook) < 80:
        hook = trim_sentence(fallback_hook, 200)

    title_focus = ' '.join(keywords[:3]).strip()
    title = trim_sentence(f"{fallback_title}: {title_focus}", 90) if title_focus else trim_sentence(fallback_title, 90)

    body_parts = []
    for candidate in [lead, support, depth]:
        candidate = trim_sentence(candidate, 460)
        if candidate and all(not too_similar(candidate, prev) for prev in body_parts):
            body_parts.append(candidate)
    cursor = 2
    while cursor < len(sentences) and len(body_parts) < 3:
        candidate = trim_sentence(sentences[cursor], 460)
        if candidate and all(not too_similar(candidate, prev) for prev in body_parts):
            body_parts.append(candidate)
        cursor += 1
    if len(body_parts) < 2:
        return None

    body = '\n\n'.join(body_parts[:3])[:1500]
    if len(body) < 500:
        return None

    tags = []
    seen_tags = set()
    for tok in keywords + [signal.get('category', ''), meta['sourceLabel'], 'analisi']:
        label = str(tok).strip()
        if not label:
            continue
        pretty = label.upper() if len(label) <= 3 else label.capitalize()
        key = pretty.lower()
        if key in seen_tags:
            continue
        seen_tags.add(key)
        tags.append(pretty)
        if len(tags) >= 5:
            break

    opinion_seed = next((s for s in body_parts[1:] if not too_similar(s, hook)), fallback_hook)
    opinion = trim_sentence(opinion_seed, 150)
    score = max(84, min(97, 84 + len(source_text) // 350))

    return {
        'title': title,
        'hook': hook,
        'body': body,
        'tags': tags,
        'opinion': opinion,
        'qualityScore': score,
    }


def unique_hook(signal, scenario, blueprint=None):
    lead = (blueprint or {}).get('lead')
    if scenario == 'tech_semis':
        if lead == 'fact_first':
            return 'La notizia segnala che sui chip il vantaggio non passa più solo dal prodotto finale, ma dalla capacità di reggere filiera, tempi e continuità industriale.'
        if lead == 'consequence_first':
            return 'Se la pressione sui semiconduttori cresce, l’effetto si vede ben oltre i laboratori: si irrigidiscono supply chain, tempi di esecuzione e margini strategici.'
        return 'Qui il punto non è il singolo nome coinvolto, ma il fatto che la competizione sui chip si stia spostando sempre di più sulla tenuta della filiera, sulla capacità produttiva e sulla continuità industriale.'
    if scenario == 'market_repricing':
        if lead == 'consequence_first':
            return 'Quando petrolio, volatilità e sentiment tornano a muoversi insieme, il mercato inizia di nuovo a prezzare un rischio più strutturale.'
        return 'Quello che conta davvero è la velocità con cui il mercato passa dall’attesa alla copertura quando guerra, energia e crescita iniziano a muoversi nella stessa direzione.'
    if scenario == 'macro_rates':
        if lead == 'fact_first':
            return 'Il segnale utile non è solo il dato macro in sé, ma il costo crescente di difendere stabilità, valuta e traiettoria di crescita.'
        return 'Sul fondo resta la domanda più importante di questa fase: quanto costa oggi difendere stabilità finanziaria, valuta e crescita quando il denaro non è più permissivo come prima.'
    if scenario == 'geo_conflict':
        if lead == 'consequence_first':
            return 'Anche senza una rottura definitiva, una crisi regionale persistente basta a trasferire tensione su rotte, prezzi e fiducia globale.'
        return 'Più che la singola dichiarazione, qui pesa il modo in cui una crisi regionale si trasferisce rapidamente su rotte, prezzi, assicurazioni e fiducia globale.'
    if scenario == 'ai_agents':
        if lead == 'actor_first':
            return 'In questa storia conta soprattutto chi prova a portare gli agenti fuori dalla demo e dentro software, workflow e budget reali.'
        return 'Il punto interessante è che gli agenti AI stanno provando a uscire dalla fase dimostrativa per entrare davvero dentro workflow, software e processi di lavoro.'
    if scenario == 'startup_capital':
        if lead == 'actor_first':
            return 'La domanda decisiva è quali operatori riescano ancora ad attrarre capitale mostrando distribuzione, difendibilità e margine di scala.'
        return 'La lettura utile è capire dove il capitale continua a vedere possibilità reali di scala, distribuzione e durata in un ecosistema che è diventato molto meno indulgente.'
    if scenario == 'science_milestone':
        if lead == 'fact_first':
            return 'Una scoperta conta davvero quando smette di essere solo sorprendente e inizia a rendere più concreta una traiettoria verificabile.'
        return 'Più dell’effetto sorpresa, qui conta la traiettoria concreta che una scoperta del genere può aprire su strumenti, osservazione o capacità operative.'
    if scenario == 'future_society':
        if lead == 'consequence_first':
            return 'Il tema non è solo la nuova capacità tecnica, ma il modo in cui automazione e deepfake alzano il costo sociale della fiducia.'
        return 'La questione vera è che automazione e deepfake stanno cambiando in modo pratico i meccanismi di fiducia e il costo del coordinamento sociale.'
    return 'Conta soprattutto l’implicazione che questa storia porta nel quadro più ampio.'


def compose_body(blueprint, p1, p2, p3):
    style = blueprint.get('body_style')
    if style == 'quick_brief':
        return f"{p1}\n\n{p2}\n\n{p3}"
    if style == 'scenario_watch':
        return f"{p1}\n\n{p2}\n\n{p3}"
    if style == 'actor_focus':
        return f"{p1}\n\n{p2}\n\n{p3}"
    return f'{p1}\n\n{p2}\n\n{p3}'


def render_editorial_item(signal, scenario):
    source_url = signal.get('sourceUrlResolved') or signal.get('link')
    meta = resolve_source_metadata(signal['title'], source_url)
    blueprint = choose_format_blueprint(signal, scenario, signal['title'])

    generated = generate_editorial_content(signal, scenario, meta['sourceLabel'])
    if generated:
        title = generated['title']
        hook = generated['hook']
        body = generated['body']
        tags = generated['tags']
        opinion = generated['opinion']
        score = generated['qualityScore']
    else:
        fallback = build_source_driven_fallback(signal, scenario, meta, blueprint)
        if not fallback:
            return None
        title = fallback['title']
        hook = fallback['hook']
        body = fallback['body']
        tags = fallback['tags']
        opinion = fallback['opinion']
        score = fallback['qualityScore']

    return {
        'category': SCENARIO_CATEGORY[scenario],
        'subcategory': SCENARIO_SUBCATEGORY[scenario],
        'title': title,
        'hook': hook,
        'body': body,
        'tags': tags,
        'format': blueprint['label'],
        'leadStyle': blueprint['lead'],
        'sourceLabel': meta['sourceLabel'],
        'sourceCount': 1,
        'featured': False,
        'opinion': opinion,
        'qualityScore': score,
        'visual': VISUAL_MAP[SCENARIO_CATEGORY[scenario]],
        'canonicalKey': canonical_signal_key(SCENARIO_CATEGORY[scenario], signal['title']),
        'sourceHost': meta['sourceHost'],
        'sourceTier': meta['sourceTier'],
    }


def mostly_italian(text):
    t = title_norm(text)
    if not t:
        return False
    english_markers = [
        ' the ', ' and ', ' with ', ' from ', ' latest ', ' headlines ', ' growth ', ' demand ',
        ' war ', ' launch ', ' stocks ', ' market ', ' futures ', ' subscribe ', ' sign in ',
        ' close search ', ' most read ', ' see all ', ' learn more ', ' products ', ' devices ',
        ' leadership ', ' developer tools ', ' infrastructure ', ' global network '
    ]
    italian_markers = [
        ' il ', ' lo ', ' la ', ' i ', ' gli ', ' le ', ' un ', ' una ', ' con ', ' per ', ' nel ',
        ' della ', ' delle ', ' degli ', ' che ', ' questo ', ' questa ', ' notizia ', ' mercato ',
        ' rischio ', ' capitale ', ' filiera ', ' storia '
    ]
    english_hits = sum(1 for m in english_markers if m in f' {t} ')
    italian_hits = sum(1 for m in italian_markers if m in f' {t} ')
    if english_hits >= 2 and italian_hits == 0:
        return False
    if english_hits >= 3:
        return False
    return True


def too_similar(a, b):
    sa = set(text_tokens(a))
    sb = set(text_tokens(b))
    if not sa or not sb:
        return False
    overlap = len(sa & sb) / max(1, min(len(sa), len(sb)))
    return overlap >= 0.72


def narrative_signature(item):
    text = ' '.join([
        item.get('title', ''),
        item.get('hook', ''),
        item.get('subcategory', ''),
        ' '.join(item.get('tags', []) or []),
    ])
    tokens = set(text_tokens(text))
    best = None
    best_score = 0
    for label, vocab in NARRATIVE_VOCAB.items():
        score = len(tokens & vocab)
        if score > best_score:
            best = label
            best_score = score
    return best or f"cat:{item.get('category','unknown')}"


def fingerprint(item):
    parts = [item.get('title',''), item.get('hook',''), item.get('subcategory',''), ' '.join(item.get('tags',[]) or [])]
    toks = [t for t in text_tokens(' '.join(parts)) if t not in {'della','delle','degli','dello','dalla','dalle','degli','dell','nelle','nella','sulla','sulle','dopo','oggi','ancora'}]
    return set(toks)


def items_are_clones(a, b):
    if a.get('canonicalKey') and a.get('canonicalKey') == b.get('canonicalKey'):
        return True
    if narrative_signature(a) == narrative_signature(b):
        fa, fb = fingerprint(a), fingerprint(b)
        if fa and fb and len(fa & fb) / max(1, min(len(fa), len(fb))) >= 0.75:
            return True
    if too_similar(a.get('title',''), b.get('title','')):
        return True
    return False


def dynamic_queries_for_category(category, category_context):
    queries = []
    base = [q for c, q in DISCOVERY_QUERIES if c == category]
    queries.extend(base)
    ctx = category_context.get(category, {})
    rotating = ROTATING_DISCOVERY_QUERIES.get(category, [])
    if not rotating:
        return queries

    recent_tokens = set(ctx.get('recentTokens', []))
    recent_narratives = set(ctx.get('recentNarratives', []))

    if category == 'tech':
        if 'chips_supply_chain' in recent_narratives:
            queries.append(rotating[0])
        else:
            queries.append(rotating[1])
    elif category == 'ai':
        if 'ai_agents_enterprise' in recent_narratives or 'workflow' in recent_tokens:
            queries.append(rotating[1])
        else:
            queries.append(rotating[0])
    elif category == 'mercati':
        if 'energy_risk_oil' in recent_narratives or 'oil' in recent_tokens:
            queries.append(rotating[1])
        else:
            queries.append(rotating[0])

    return queries[:2]


def discover_signals(category_context=None):
    findings = []
    seen_keys = set()
    category_context = category_context or {}
    categories = []
    seen_categories = set()
    for category, _ in DISCOVERY_QUERIES:
        if category not in seen_categories:
            categories.append(category)
            seen_categories.add(category)

    def add_signal(category, title, link, published_at=None, query=None, source='direct-rss', preset_tier=None):
        if not usable_headline(title, link):
            return False
        signal_key = canonical_signal_key(category, title)
        if signal_key in seen_keys:
            return False
        signal = {
            'category': category,
            'title': title,
            'link': link,
            'query': query or source,
            'publishedAt': published_at,
            'canonicalKey': signal_key,
            'discoverySource': source,
        }
        enriched = enrich_signal_source(signal)
        if preset_tier:
            enriched['sourceTier'] = preset_tier
        if source == 'google-news-backup' and 'news.google.com' in (enriched.get('sourceHost') or ''):
            return False
        if len((enriched.get('sourceText') or '').strip()) < 500:
            return False
        seen_keys.add(signal_key)
        findings.append(enriched)
        return True

    category_counts = {category: 0 for category in categories}

    for category in categories:
        for feed in DISCOVERY_FEEDS.get(category, []):
            try:
                root = ET.fromstring(fetch(feed['url'], timeout=20))
            except Exception:
                continue
            for item in root.findall('.//item')[:8]:
                title = clean_raw_title((item.findtext('title') or '').strip())
                link = (item.findtext('link') or '').strip()
                published_at = parse_pub_date(item.findtext('pubDate'))
                if add_signal(category, title, link, published_at=published_at, query=feed['url'], source='direct-rss', preset_tier=feed.get('tier')):
                    category_counts[category] += 1

    for category in categories:
        if category_counts.get(category, 0) >= 3:
            continue
        for query in dynamic_queries_for_category(category, category_context):
            rss = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': query, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'})
            try:
                root = ET.fromstring(fetch(rss))
            except Exception:
                continue
            limit = 8 if query == dynamic_queries_for_category(category, category_context)[0] else 4
            for item in root.findall('.//item')[:limit]:
                title = (item.findtext('title') or '').strip()
                link = (item.findtext('link') or '').strip()
                published_at = parse_pub_date(item.findtext('pubDate'))
                if add_signal(category, title, link, published_at=published_at, query=query, source='google-news-backup'):
                    category_counts[category] += 1
                if category_counts.get(category, 0) >= 3:
                    break
            if category_counts.get(category, 0) >= 3:
                break
    return findings


def existing_story_keys(existing_news):
    keys = set()
    for item in existing_news:
        ck = item.get('canonicalKey')
        if ck:
            keys.add(ck)
        else:
            keys.add(canonical_signal_key(item.get('category','unknown'), item.get('title','')))
    return keys


def dedupe_signals(findings, existing_news):
    existing_titles = {title_norm(item.get('title', '')) for item in existing_news}
    existing_keys = existing_story_keys(existing_news)
    recent_history = load_recent_history_items(days=21)
    history_keys = {item.get('canonicalKey') for item in recent_history if item.get('canonicalKey')}
    deduped = []
    seen = set()
    for finding in findings:
        norm = title_norm(finding['title'])
        key = finding.get('canonicalKey')
        host = finding.get('sourceHost')
        local_key = (key, host)
        if norm in existing_titles or key in existing_keys or key in history_keys or local_key in seen:
            continue
        seen.add(local_key)
        deduped.append(finding)
    return deduped


def build_category_context(existing_news, history_items, recent_limit=5):
    grouped = {}
    combined = sorted(list(existing_news) + list(history_items), key=lambda x: x.get('timestamp',''), reverse=True)
    for item in combined:
        cat = item.get('category')
        if not cat:
            continue
        grouped.setdefault(cat, [])
        if len(grouped[cat]) >= recent_limit:
            continue
        clone_seen = False
        for prev in grouped[cat]:
            if items_are_clones(item, prev):
                clone_seen = True
                break
        if not clone_seen:
            if not item.get('canonicalKey'):
                item['canonicalKey'] = canonical_signal_key(item.get('category','unknown'), item.get('title',''))
            grouped[cat].append(item)

    context = {}
    for cat, items in grouped.items():
        recent_keys = []
        recent_narratives = []
        recent_tokens = set()
        recent_hosts = set()
        for item in items:
            if item.get('canonicalKey'):
                recent_keys.append(item['canonicalKey'])
            recent_narratives.append(narrative_signature(item))
            recent_tokens.update(fingerprint(item))
            if item.get('sourceHost'):
                recent_hosts.add(item.get('sourceHost'))
        context[cat] = {
            'items': items,
            'recentCanonicalKeys': recent_keys,
            'recentNarratives': recent_narratives,
            'recentTokens': sorted(recent_tokens),
            'recentHosts': sorted(recent_hosts),
        }
    return context


def novelty_score(item, category_context):
    ctx = category_context.get(item.get('category'), {})
    recent_items = ctx.get('items', [])
    if not recent_items:
        return {
            'score': 100,
            'class': 'new_axis',
            'signals': ['empty_category_context']
        }

    score = 100
    signals = []
    item_key = item.get('canonicalKey')
    if item_key and item_key in set(ctx.get('recentCanonicalKeys', [])):
        score -= 30
        signals.append('canonical_repeat')

    item_sig = narrative_signature(item)
    if item_sig in set(ctx.get('recentNarratives', [])):
        score -= 8
        signals.append('narrative_seen')

    item_tokens = fingerprint(item)
    recent_tokens = set(ctx.get('recentTokens', []))
    if item_tokens:
        new_tokens = item_tokens - recent_tokens
        overlap = len(item_tokens & recent_tokens) / max(1, len(item_tokens))
        if new_tokens:
            score += min(14, len(new_tokens) * 2)
            signals.append(f'new_tokens:{len(new_tokens)}')
        if overlap >= 0.75:
            score -= 14
            signals.append('high_token_overlap')
        elif overlap <= 0.35:
            score += 8
            signals.append('low_token_overlap')

    clone_count = sum(1 for prev in recent_items if items_are_clones(item, prev))
    if clone_count:
        score -= min(30, clone_count * 15)
        signals.append(f'clone_risk:{clone_count}')

    host = item.get('sourceHost')
    if host and host not in set(ctx.get('recentHosts', [])):
        score += 4
        signals.append('new_source_host')

    score = max(0, min(100, score))
    if score >= 60:
        novelty_class = 'new_axis'
    elif score >= 52:
        novelty_class = 'relevant_update'
    elif score >= 30:
        novelty_class = 'marginal_update'
    else:
        novelty_class = 'clone_risk'

    return {
        'score': score,
        'class': novelty_class,
        'signals': signals,
    }


def editorial_score(signal, item, existing_news, category_context):
    score = int(item.get('qualityScore') or 0)
    if signal.get('sourceTier') == 'high':
        score += 4
    elif signal.get('sourceTier') == 'medium':
        score += 2
    live_categories = {entry.get('category') for entry in existing_news if entry.get('category')}
    if item.get('category') not in live_categories:
        score += 5
    same_category_count = sum(1 for entry in existing_news if entry.get('category') == item.get('category'))
    score -= same_category_count * 2

    novelty = novelty_score(item, category_context)
    item['noveltyScore'] = novelty['score']
    item['noveltyClass'] = novelty['class']
    item['noveltySignals'] = novelty['signals']
    if novelty['class'] == 'new_axis':
        score += 10
    elif novelty['class'] == 'relevant_update':
        score += 4
    elif novelty['class'] == 'marginal_update':
        score -= 2
    elif novelty['class'] == 'clone_risk':
        score -= 14

    score += int((novelty['score'] - 50) / 8)
    return score


def build_candidate_items(findings, existing_news, category_context):
    old_ids = {item['id'] for item in existing_news}
    old_titles = {title_norm(item['title']) for item in existing_news}
    old_keys = existing_story_keys(existing_news)
    candidates = []
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    for signal in findings:
        scenario = classify_signal_scenario(signal['category'], signal['title'])
        if not scenario:
            continue
        built = render_editorial_item(signal, scenario)
        if not built:
            continue
        if 'news.google.com' in ((signal.get('sourceHost') or '') + ' ' + (built.get('sourceHost') or '')):
            continue
        final_title_norm = title_norm(built['title'])
        if final_title_norm in old_titles or built['canonicalKey'] in old_keys:
            continue
        item_id = f"{signal['category']}-{datetime.now().strftime('%Y%m%d')}-{slugify(built['title'])}-{short_hash(built['canonicalKey'])}"
        if item_id in old_ids:
            continue
        item = {
            'id': item_id,
            'timestamp': signal.get('publishedAt') or now,
            'sourceUrl': signal.get('sourceUrlResolved') or signal['link'],
            **built,
        }
        candidates.append({'signal': signal, 'item': item, 'score': editorial_score(signal, item, existing_news, category_context)})
        old_ids.add(item_id)
        old_titles.add(final_title_norm)
        old_keys.add(built['canonicalKey'])
    candidates.sort(key=lambda x: (x['score'], x['item'].get('noveltyScore', 0), x['item'].get('qualityScore', 0)), reverse=True)
    filtered = []
    for bundle in candidates:
        item = bundle['item']
        if item.get('noveltyClass') == 'clone_risk':
            continue
        if any(items_are_clones(item, prev['item']) for prev in filtered):
            continue
        filtered.append(bundle)
    return filtered[:16]


def quality_guard(items):
    cleaned = []
    for item in items:
        title = (item.get('title') or '').strip()
        body = item.get('body') or ''
        hook = item.get('hook') or ''
        if len(title.split()) < 6:
            continue
        if len(body) < 500 or len(hook) < 80:
            continue
        if (item.get('qualityScore') or 0) < QUALITY_FLOOR:
            continue
        if item.get('sourceLabel') in {'Source review pending', 'Google News'}:
            continue
        if not mostly_italian(title) or not mostly_italian(hook) or not mostly_italian(body[:320]):
            continue
        body_norm = title_norm(body[:500])
        noisy_body_markers = ['subscribe sign in', 'close search bar', 'most read', 'see all', 'feed subscribe', 'global english']
        if any(marker in body_norm for marker in noisy_body_markers):
            continue
        if not item.get('canonicalKey'):
            item['canonicalKey'] = canonical_signal_key(item.get('category','unknown'), item.get('title',''))
        cleaned.append(item)
    unique = []
    for item in cleaned:
        if any(items_are_clones(item, prev) for prev in unique):
            continue
        unique.append(item)
    return unique


def pick_highlights_by_day(edition, history_items=None):
    source_items = []
    seen = set()
    for item in list(edition) + list(history_items or []):
        iid = item.get('id')
        if not iid or iid in seen:
            continue
        seen.add(iid)
        source_items.append(item)

    buckets = {}
    for item in source_items:
        day = (item.get('timestamp') or '')[:10]
        if day:
            buckets.setdefault(day, []).append(item)

    today = datetime.now().astimezone().date()
    chosen = []
    used = set()
    for delta in range(1, 5):
        day = (today.fromordinal(today.toordinal() - delta)).isoformat()
        day_items = buckets.get(day, [])
        if not day_items:
            continue
        best = sorted(day_items, key=lambda x: ((x.get('qualityScore') or 0), x.get('timestamp') or ''), reverse=True)[0]
        if best.get('id') not in used:
            chosen.append(best)
            used.add(best.get('id'))
    return chosen[:4]


def category_limit_for(item):
    return MAX_CATEGORY_COUNT_HIGH_QUALITY if (item.get('qualityScore') or 0) >= HIGH_QUALITY_SECOND_SLOT else MAX_CATEGORY_COUNT


def load_recent_history_items(days=7):
    cutoff = datetime.now().astimezone().date().toordinal() - days
    collected = []
    if not HISTORY_DIR.exists():
        return collected
    for path in sorted(HISTORY_DIR.glob('*.json')):
        try:
            items = load_json(path)
        except Exception:
            continue
        if not isinstance(items, list):
            continue
        for item in items:
            ts = (item.get('timestamp') or '')[:10]
            try:
                ord_day = datetime.fromisoformat(ts).date().toordinal()
            except Exception:
                continue
            if ord_day >= cutoff:
                if not item.get('canonicalKey'):
                    item['canonicalKey'] = canonical_signal_key(item.get('category','unknown'), item.get('title',''))
                collected.append(item)
    return collected


def assemble_edition(existing_news, candidate_bundles):
    cleaned_existing = quality_guard(existing_news)
    recent_history = quality_guard(load_recent_history_items(days=7))
    ranked_existing = sorted(cleaned_existing, key=lambda x: ((x.get('qualityScore') or 0), x.get('timestamp') or ''), reverse=True)
    ranked_candidates = [b['item'] for b in candidate_bundles]

    replacement_pool = []
    replaced_existing_ids = set()
    best_candidate_by_category = {}
    for item in ranked_candidates:
        cat = item.get('category')
        if cat not in best_candidate_by_category:
            best_candidate_by_category[cat] = item
    for existing in ranked_existing:
        candidate = best_candidate_by_category.get(existing.get('category'))
        if candidate and (candidate.get('noveltyScore', 0), candidate.get('qualityScore', 0)) >= ((existing.get('noveltyScore') or 0), (existing.get('qualityScore') or 0)):
            replaced_existing_ids.add(existing.get('id'))
            replacement_pool.append(candidate)
    ranked_existing = [item for item in ranked_existing if item.get('id') not in replaced_existing_ids]

    merged_candidates = []
    seen_candidate_ids = set()
    for item in replacement_pool + ranked_candidates:
        iid = item.get('id')
        if iid in seen_candidate_ids:
            continue
        seen_candidate_ids.add(iid)
        merged_candidates.append(item)

    edition = []
    used_titles = set()
    category_counts = {}
    narrative_counts = {}
    new_added = 0

    def can_add(item):
        cat = item['category']
        if category_counts.get(cat, 0) >= category_limit_for(item):
            return False
        norm = title_norm(item.get('title'))
        if norm in used_titles:
            return False
        if item.get('noveltyClass') == 'clone_risk':
            return False
        sig = narrative_signature(item)
        if narrative_counts.get(sig, 0) >= 2:
            return False
        for prev in edition:
            if items_are_clones(item, prev):
                return False
        return True

    for item in merged_candidates:
        if new_added >= MAX_NEW_PER_REFRESH or len(edition) >= MAX_LIVE:
            break
        if can_add(item):
            edition.append(item)
            used_titles.add(title_norm(item.get('title')))
            category_counts[item['category']] = category_counts.get(item['category'], 0) + 1
            sig = narrative_signature(item)
            narrative_counts[sig] = narrative_counts.get(sig, 0) + 1
            new_added += 1

    if len(edition) < MIN_LIVE:
        for item in ranked_existing:
            if len(edition) >= MIN_LIVE:
                break
            if can_add(item):
                edition.append(item)
                used_titles.add(title_norm(item.get('title')))
                category_counts[item['category']] = category_counts.get(item['category'], 0) + 1
                sig = narrative_signature(item)
                narrative_counts[sig] = narrative_counts.get(sig, 0) + 1

    if len(edition) < MAX_LIVE:
        for item in ranked_existing:
            if len(edition) >= MAX_LIVE:
                break
            if can_add(item):
                edition.append(item)
                used_titles.add(title_norm(item.get('title')))
                category_counts[item['category']] = category_counts.get(item['category'], 0) + 1
                sig = narrative_signature(item)
                narrative_counts[sig] = narrative_counts.get(sig, 0) + 1

    highlights = pick_highlights_by_day(edition, recent_history)
    highlight_ids = {item['id'] for item in highlights}
    for item in edition:
        item['featured'] = item['id'] in highlight_ids
    return edition


def ensure_history_consistency(live_news):
    by_month = {}
    for item in live_news:
        ts = item.get('timestamp') or ''
        month = ts[:7]
        if month:
            by_month.setdefault(month, []).append(item)
    for month, items in by_month.items():
        path = HISTORY_DIR / f'{month}.json'
        history = load_json(path) if path.exists() else []
        if not isinstance(history, list):
            history = []
        existing_ids = {x.get('id') for x in history if isinstance(x, dict)}
        missing = [x for x in items if x.get('id') not in existing_ids]
        if missing:
            history = missing + history
            deduped = []
            seen = set()
            for entry in sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True):
                eid = entry.get('id')
                if eid in seen:
                    continue
                seen.add(eid)
                deduped.append(entry)
            save_json(path, deduped)


def validate_live_history_consistency(live_news):
    missing = []
    for item in live_news:
        month = (item.get('timestamp') or '')[:7]
        path = HISTORY_DIR / f'{month}.json'
        if not path.exists():
            missing.append(item['id'])
            continue
        history = load_json(path)
        if item['id'] not in {x.get('id') for x in history if isinstance(x, dict)}:
            missing.append(item['id'])
    if missing:
        raise SystemExit('live/history mismatch: ' + ', '.join(missing))


def assert_reused_timestamps_preserved(existing_news, live_news):
    previous = {
        item.get('id'): item.get('timestamp')
        for item in existing_news
        if isinstance(item, dict) and item.get('id') and item.get('timestamp')
    }
    drift = []
    for item in live_news:
        item_id = item.get('id')
        if item_id in previous and item.get('timestamp') != previous[item_id]:
            drift.append({
                'id': item_id,
                'before': previous[item_id],
                'after': item.get('timestamp'),
            })
    if drift:
        raise SystemExit('timestamp drift on reused items: ' + json.dumps(drift[:6], ensure_ascii=False))


def refresh_stats(stats, news, findings):
    now = datetime.now().astimezone()
    stats['editionUpdatedAt'] = now.isoformat(timespec='seconds')
    stats['newsGeneratedToday'] = len(news)
    stats['sourcesAnalyzed'] = max(int(stats.get('sourcesAnalyzed', 0) or 0), len(findings), 24)
    ranked = sorted(news, key=lambda x: ((x.get('qualityScore') or 0), x.get('timestamp') or ''), reverse=True)
    stats['mostViewed'] = [item['title'] for item in ranked[:3]]
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
    stats['signals'] = [
        {'label': 'Edition', 'value': 'Public MVP'},
        {'label': 'Cadence', 'value': f"Hourly auto-refresh · {now.strftime('%H:%M %Z')}"},
        {'label': 'Mode', 'value': 'Italian briefing'},
        {'label': 'Focus', 'value': 'Source-backed news'}
    ]
    return stats


def write_health_log(existing_news, findings, candidate_bundles, live, dry_run=False, category_context=None):
    HEALTH_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    payload = {
        'generatedAt': now,
        'dryRun': dry_run,
        'existingCount': len(existing_news),
        'discoveryCount': len(findings),
        'candidateCount': len(candidate_bundles),
        'liveCount': len(live),
        'categories': sorted({item.get('category') for item in live if item.get('category')}),
        'narratives': sorted({narrative_signature(item) for item in live}),
        'sourcesSeen': sorted({f.get('sourceLabelGuess') for f in findings if f.get('sourceLabelGuess')}),
        'categoryContext': {
            cat: {
                'recentCanonicalKeys': ctx.get('recentCanonicalKeys', []),
                'recentNarratives': ctx.get('recentNarratives', []),
                'recentTokens': ctx.get('recentTokens', [])[:20],
                'recentHosts': ctx.get('recentHosts', []),
            }
            for cat, ctx in (category_context or {}).items()
        },
        'candidates': [
            {
                'id': bundle['item'].get('id'),
                'category': bundle['item'].get('category'),
                'title': bundle['item'].get('title'),
                'canonicalKey': bundle['item'].get('canonicalKey'),
                'sourceLabel': bundle['item'].get('sourceLabel'),
                'noveltyScore': bundle['item'].get('noveltyScore'),
                'noveltyClass': bundle['item'].get('noveltyClass'),
                'noveltySignals': bundle['item'].get('noveltySignals'),
                'score': bundle.get('score'),
                'sourceHost': bundle['item'].get('sourceHost'),
                'sourceUrl': bundle['item'].get('sourceUrl'),
                'scenario': classify_signal_scenario(bundle['item'].get('category'), bundle['signal'].get('title', '')),
                'rawTitle': bundle['signal'].get('title'),
                'sourceText': bundle['signal'].get('sourceText'),
                'discoverySource': bundle['signal'].get('discoverySource'),
            }
            for bundle in candidate_bundles[:20]
        ],
        'liveItems': [
            {
                'id': item.get('id'),
                'category': item.get('category'),
                'title': item.get('title'),
                'canonicalKey': item.get('canonicalKey'),
                'narrative': narrative_signature(item),
                'noveltyScore': item.get('noveltyScore'),
                'noveltyClass': item.get('noveltyClass'),
            }
            for item in live
        ],
        'discoverySample': findings[:12],
    }
    save_json(HEALTH_DIR / 'latest.json', payload)
    stamped = datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
    save_json(HEALTH_DIR / f'{stamped}.json', payload)


def main():
    dry_run = '--dry-run' in sys.argv
    candidates_only = '--candidates-only' in sys.argv
    TMP.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
    shutil.copy2(NEWS, TMP / f'news.{stamp}.json')
    shutil.copy2(STATS, TMP / f'stats.{stamp}.json')

    existing_news = load_json(NEWS)
    stats = load_json(STATS)
    recent_history_context = quality_guard(load_recent_history_items(days=7))
    category_context = build_category_context(existing_news, recent_history_context, recent_limit=5)
    findings = dedupe_signals(discover_signals(category_context), existing_news)
    candidate_bundles = build_candidate_items(findings, existing_news, category_context)
    live = assemble_edition(existing_news, candidate_bundles)
    assert_reused_timestamps_preserved(existing_news, live)
    stats = refresh_stats(stats, live, findings)
    write_health_log(existing_news, findings, candidate_bundles, live, dry_run=dry_run or candidates_only, category_context=category_context)

    if candidates_only:
        raw_candidates = []
        for bundle in candidate_bundles:
            signal = bundle['signal']
            item = bundle['item']
            raw_candidates.append({
                'id': item.get('id'),
                'category': item.get('category'),
                'scenario': classify_signal_scenario(item.get('category'), signal.get('title', '')),
                'raw_title': signal.get('title'),
                'sourceText': signal.get('sourceText'),
                'sourceUrl': signal.get('sourceUrlResolved') or signal.get('link'),
                'sourceHost': signal.get('sourceHost'),
                'sourceLabel': signal.get('sourceLabelGuess'),
                'publishedAt': signal.get('publishedAt'),
                'canonicalKey': item.get('canonicalKey'),
                'qualityScore': item.get('qualityScore'),
                'noveltyScore': item.get('noveltyScore'),
                'noveltyClass': item.get('noveltyClass'),
                'discoverySource': signal.get('discoverySource'),
            })
        save_json(CANDIDATES_PATH, raw_candidates)
        print(json.dumps({
            'status': 'candidates-only',
            'candidatesPath': str(CANDIDATES_PATH),
            'discoveryCount': len(findings),
            'candidateCount': len(candidate_bundles),
            'categories': sorted({x['category'] for x in raw_candidates}),
        }, ensure_ascii=False, indent=2))
        return

    if dry_run:
        preview_news = PREVIEW_DIR / 'news.preview.json'
        preview_stats = PREVIEW_DIR / 'stats.preview.json'
        save_json(preview_news, live)
        save_json(preview_stats, stats)
        print(json.dumps({
            'status': 'dry-run',
            'previewNews': str(preview_news),
            'previewStats': str(preview_stats),
            'discoveryCount': len(findings),
            'candidateCount': len(candidate_bundles),
            'count': len(live),
            'categories': sorted({x['category'] for x in live}),
            'narratives': sorted({narrative_signature(x) for x in live}),
        }, ensure_ascii=False, indent=2))
        return

    save_json(NEWS_TMP, live)
    save_json(STATS_TMP, stats)
    load_json(NEWS_TMP)
    load_json(STATS_TMP)
    os.replace(NEWS_TMP, NEWS)
    os.replace(STATS_TMP, STATS)
    ensure_history_consistency(live)
    validate_live_history_consistency(live)
    subprocess.check_call(['python3', str(ROOT / 'scripts/validate_nexus_json.py'), str(NEWS), str(STATS)])
    subprocess.check_call(['python3', str(ROOT / 'scripts/generate_story_pages.py')])
    subprocess.check_call(['python3', str(ROOT / 'scripts/generate_ai_crawl_files.py')])
    subprocess.check_call(['python3', str(ROOT / 'scripts/generate_sitemap.py')])
    subprocess.check_call(['python3', str(ROOT / 'scripts/validate_public_urls.py')])
    final_news = load_json(NEWS)
    final_stats = load_json(STATS)
    print(json.dumps({
        'status': 'ok',
        'editionUpdatedAt': final_stats['editionUpdatedAt'],
        'count': len(final_news),
        'discoveryCount': len(findings),
        'candidateCount': len(candidate_bundles),
        'healthLog': str(HEALTH_DIR / 'latest.json'),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
