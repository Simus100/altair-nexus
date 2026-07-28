const categoriesUrl = '../../data/categories.json';
const newsUrl = '../../data/news.json';
const statsUrl = '../../data/stats.json';

const accentMap = {
  cyan: 'var(--cyan)',
  violet: 'var(--violet)',
  blue: 'var(--blue)',
  teal: 'var(--teal)',
  pink: 'var(--pink)',
  amber: 'var(--amber)',
  emerald: 'var(--emerald)',
  orange: 'var(--orange)',
};

const visualClassMap = {
  ai: 'visual-ai',
  tech: 'visual-tech',
  geo: 'visual-geo',
  fin: 'visual-fin',
  markets: 'visual-markets',
  startup: 'visual-startup',
  science: 'visual-science',
  future: 'visual-future',
};

const DEFAULT_META = {
  title: 'Altair Nexus — Briefing pubblico su AI, tech e mercati',
  description: 'Altair Nexus è una homepage editoriale che rende leggibili le notizie chiave su AI, tecnologia, geopolitica, finanza, mercati, startup e scienza.',
};

function absoluteUrl(relativeOrAbsolute) {
  return new URL(relativeOrAbsolute, window.location.href).toString();
}

function deepLinkUrl(storyId) {
  const url = new URL(window.location.href);
  if (storyId) {
    url.searchParams.set('story', storyId);
  } else {
    url.searchParams.delete('story');
  }
  url.hash = '';
  return url.toString();
}

function storyPageSlug(storyId) {
  return String(storyId || 'story')
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'story';
}

function storyPageUrl(item) {
  if (!item?.id) return deepLinkUrl(null);
  return new URL(`./stories/${storyPageSlug(item.id)}.html`, window.location.href).toString();
}

function setMeta(selector, content) {
  const node = document.querySelector(selector);
  if (!node) return;
  node.setAttribute('content', content);
}

function setCanonical(href) {
  const node = document.querySelector('link[rel="canonical"]');
  if (!node) return;
  node.setAttribute('href', href);
}

function updatePageMeta(item, category) {
  const title = item
    ? `${item.title} — Altair Nexus`
    : DEFAULT_META.title;
  const description = item
    ? (cleanPublicHook(item.hook, item.sourceLabel) || item.opinion || DEFAULT_META.description)
    : DEFAULT_META.description;
  const canonical = item ? storyPageUrl(item) : homepageUrl();
  const image = absoluteUrl('./assets/aion-brief-generated.jpg');

  document.title = title;
  setCanonical(canonical);
  setMeta('meta[name="description"]', description);
  setMeta('meta[property="og:title"]', title);
  setMeta('meta[property="og:description"]', description);
  setMeta('meta[property="og:url"]', canonical);
  setMeta('meta[property="og:image"]', image);
  setMeta('meta[property="og:image:alt"]', item ? `Visual editoriale per ${item.title}` : 'Visual editoriale di Altair Nexus');
  setMeta('meta[name="twitter:title"]', title);
  setMeta('meta[name="twitter:description"]', description);
  setMeta('meta[name="twitter:image"]', image);

  const activeCategory = category?.name || item?.category;
  document.body.dataset.activeStory = item?.id || '';
  document.body.dataset.activeCategory = activeCategory || '';
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
  try {
    return await response.json();
  } catch (error) {
    throw new Error(`Invalid JSON in ${url}: ${error.message}`);
  }
}

async function loadData() {
  const [categories, news, stats] = await Promise.all([
    fetchJson(categoriesUrl),
    fetchJson(newsUrl),
    fetchJson(statsUrl),
  ]);
  return { categories, news, stats };
}

function fmtDate(ts) {
  const d = new Date(ts);
  return d.toLocaleString('it-IT', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
  });
}

function byTimestampDesc(a, b) {
  return new Date(b.timestamp) - new Date(a.timestamp);
}

function byScoreDesc(a, b) {
  return (b.qualityScore || 0) - (a.qualityScore || 0);
}

function cleanPublicHook(text, sourceLabel = '') {
  let cleaned = String(text || '').replace(/\s+/g, ' ').trim();
  if (!cleaned) return '';
  const labels = [sourceLabel, 'Reuters', 'BBC', 'TechCrunch', 'Associated Press', 'AP', 'Al Jazeera', 'NASA', 'Google']
    .filter(Boolean)
    .map((label) => String(label).trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  if (labels.length) {
    const labelGroup = labels.join('|');
    cleaned = cleaned.replace(
      new RegExp(`^(?:La|Il|Lo|L’|L'|The)?\\s*(${labelGroup})\\s+(racconta|riporta|riferisce|segnala|mette in luce|mette a fuoco|descrive|annuncia|conferma)[,:;]?\\s+(che\\s+)?`, 'i'),
      '',
    ).trim();
  }
  cleaned = cleaned.replace(/^(Secondo|In un(?:a)?\s+analisi(?:\s+di)?)\s+/i, '').trim();
  cleaned = normalizePublicBrand(cleaned);
  return cleaned ? cleaned.charAt(0).toUpperCase() + cleaned.slice(1) : '';
}

function normalizePublicBrand(text) {
  return String(text || '')
    .replace(/\bAION\s+NEXUS\b/gi, 'Altair Nexus')
    .replace(/\bAion\s+Nexus\b/gi, 'Altair Nexus');
}

function splitBodyAndContext(body) {
  const bodyParts = [];
  const contextParts = [];
  String(body || '').split(/\n\n+/).map((paragraph) => paragraph.trim()).filter(Boolean).forEach((paragraph) => {
    if (/^(Per\s+(?:AION\s+NEXUS|Altair\s+Nexus)\b|In\s+ottica\s+(?:AION\s+NEXUS|Altair\s+Nexus)\b)/i.test(paragraph)) {
      contextParts.push(normalizePublicBrand(paragraph));
    } else {
      bodyParts.push(normalizePublicBrand(paragraph));
    }
  });
  return { bodyParts, contextParts };
}

function computeMetrics(categories, news, stats) {
  const grouped = Object.fromEntries(categories.map((c) => [c.id, news.filter((n) => n.category === c.id).sort(byScoreDesc)]));
  const categoryAverages = [...categories]
    .map((c) => ({
      id: c.id,
      name: c.name,
      count: grouped[c.id].length,
      avg: (grouped[c.id].reduce((a, n) => a + (n.qualityScore || 0), 0) / Math.max(grouped[c.id].length, 1))
    }))
    .sort((a, b) => b.avg - a.avg);
  const hottest = categoryAverages[0]?.name || '—';
  const dominant = categoryAverages.sort((a, b) => (b.count * 100 + b.avg) - (a.count * 100 + a.avg))[0]?.name || hottest;
  const tags = {};
  news.forEach((item) => item.tags?.forEach((tag) => { tags[tag] = (tags[tag] || 0) + 1; }));
  const topTags = (stats.topicEmerging?.length ? stats.topicEmerging : Object.entries(tags).sort((a,b) => b[1]-a[1]).slice(0, 8).map(([tag]) => tag));
  const latestTs = stats?.editionUpdatedAt || news.slice().sort(byTimestampDesc)[0]?.timestamp || null;
  const activeCategories = categoryAverages.filter((item) => item.count > 0).length;
  const highPriority = news.filter((item) => (item.qualityScore || 0) >= 90).length;
  const avgScore = news.reduce((sum, item) => sum + (item.qualityScore || 0), 0) / Math.max(news.length, 1);
  const intensity = highPriority >= 3 || avgScore >= 89
    ? 'Alta concentrazione'
    : highPriority >= 1 || avgScore >= 84
      ? 'Selettiva ma forte'
      : 'Diffusa e moderata';
  const editorNote = dominant === 'Geopolitica'
    ? 'Il baricentro si concentra sul trasferimento del rischio geopolitico verso energia, logistica e pricing di mercato.'
    : 'L’edizione segnala che il vantaggio si sposta sempre più dalla semplice novità alla capacità di integrazione ed esecuzione.';
  return {
    newsToday: stats.newsGeneratedToday || news.length,
    sources: stats.sourcesAnalyzed || Math.max(18, news.length * 3),
    hottest,
    dominant,
    latestUpdate: latestTs ? fmtDate(latestTs) : '—',
    coverage: `${activeCategories}/${categories.length}`,
    intensity,
    topTags,
    grouped,
    categoryAverages,
    mostViewed: stats.mostViewed || [],
    signals: stats.signals || [],
    editorNote,
  };
}

function renderBreaking(news) {
  const host = document.getElementById('breaking-items');
  host.innerHTML = news
    .slice()
    .sort(byTimestampDesc)
    .slice(0, 5)
    .map((item) => `<span class="breaking-item">${item.title}</span>`)
    .join('');
}

function sourceLink() {
  return '';
}

function homepageUrl() {
  return deepLinkUrl(null);
}

function shareText(item) {
  return item ? `${item.title} — ${cleanPublicHook(item.hook, item.sourceLabel) || item.hook}` : 'Altair Nexus — Briefing pubblico su AI, tech e mercati';
}

function shareDescription(item) {
  return item
    ? (cleanPublicHook(item.hook, item.sourceLabel) || item.opinion || DEFAULT_META.description)
    : DEFAULT_META.description;
}

function buildAionOpinion(item, category) {
  const categoryName = category?.name || item.category || 'scenario';
  const tags = Array.isArray(item.tags) ? item.tags.filter(Boolean).slice(0, 3) : [];
  const subcategory = item?.subcategory ? String(item.subcategory).trim() : '';
  const score = Number(item?.qualityScore || 0);

  const categoryLens = {
    ai: 'la partita vera si giochi sulla capacità di trasformare vantaggio tecnico in distribuzione e standard di mercato',
    tech: 'conti soprattutto il controllo dei passaggi critici dell’infrastruttura e non solo l’annuncio di giornata',
    geopolitica: 'il punto decisivo sia quanto rapidamente il rischio politico si trasferisce su logistica, energia e prezzi',
    finanza: 'il mercato stia misurando soprattutto sostenibilità, costo del capitale e credibilità dell’esecuzione',
    mercati: 'gli operatori stiano prezzando la tenuta del sistema più che il rumore delle singole headline',
    startup: 'conti meno la narrativa e molto di più la capacità di finanziare crescita, distribuzione e resistenza nel tempo',
    scienza: 'il valore emerga quando la scoperta mostra una traiettoria concreta verso applicazioni, piattaforme o vantaggi cumulativi',
    futuro: 'il segnale abbia peso quando anticipa cambiamenti di abitudini, infrastrutture o modelli industriali'
  };

  const intensity = score >= 93
    ? 'Se il quadro regge anche nelle prossime ore, questo può diventare un passaggio che riallinea davvero le aspettative.'
    : score >= 88
      ? 'Non è ancora una svolta definitiva, ma è il tipo di movimento che cambia il modo in cui il dossier viene letto.'
      : 'Per ora vale più come indicatore anticipatore che come svolta pienamente consolidata.';

  const tagLine = tags.length
    ? ` I segnali su ${tags.join(', ')} suggeriscono che il mercato leggerà questa storia soprattutto come test di tenuta e direzione.`
    : '';

  const subcategoryLine = subcategory
    ? ` Nel perimetro ${subcategory.toLowerCase()}, Aion legge qui un indizio che va oltre il fatto singolo.`
    : '';

  const lens = categoryLens[item?.category] || 'la notizia conti soprattutto per ciò che anticipa sulla direzione del contesto';

  return `Sul fronte ${categoryName.toLowerCase()} il punto non è ripetere la cronaca, ma capire se ${lens}.${subcategoryLine}${tagLine} ${intensity}`.replace(/\s+/g, ' ').trim();
}

function socialShareUrls(item) {
  const link = item ? storyPageUrl(item) : homepageUrl();
  const text = shareText(item);
  return {
    link,
    x: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(link)}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(link)}`,
    whatsapp: `https://wa.me/?text=${encodeURIComponent(`${text}\n\n${link}`)}`,
    telegram: `https://t.me/share/url?url=${encodeURIComponent(link)}&text=${encodeURIComponent(text)}`,
  };
}

function shareActions(item, options = {}) {
  const urls = socialShareUrls(item);
  const copyLabel = options.copyLabel || 'Copia link';
  const includeNativeShare = options.includeNativeShare ?? Boolean(item);
  const nativeLabel = options.nativeLabel || 'Condividi';
  return `
    <div class="share-actions ${options.className || ''}" aria-label="${options.ariaLabel || 'Condivisione'}">
      <button class="source-link story-share-button share-pill-main" type="button" data-share-story="${item?.id || 'homepage'}" data-share-kind="${item ? 'story' : 'homepage'}" aria-label="${item ? 'Copia link diretto a questa notizia' : 'Copia link della homepage'}" title="${item ? 'Copia link diretto a questa notizia' : 'Copia link della homepage'}">
        ${copyLabel}
      </button>
      ${includeNativeShare ? `<button class="source-link story-share-native" type="button" data-native-share="${item?.id || 'homepage'}" data-share-kind="${item ? 'story' : 'homepage'}" aria-label="Apri condivisione di sistema">${nativeLabel}</button>` : ''}
      <a class="source-link" href="${urls.whatsapp}" target="_blank" rel="noreferrer">WhatsApp</a>
      <a class="source-link" href="${urls.telegram}" target="_blank" rel="noreferrer">Telegram</a>
      <a class="source-link" href="${urls.linkedin}" target="_blank" rel="noreferrer">LinkedIn</a>
      <a class="source-link" href="${urls.x}" target="_blank" rel="noreferrer">X</a>
    </div>
  `;
}

function fallbackCopyText(text) {
  const temp = document.createElement('textarea');
  temp.value = text;
  temp.setAttribute('readonly', '');
  temp.style.position = 'absolute';
  temp.style.left = '-9999px';
  document.body.appendChild(temp);
  temp.select();
  temp.setSelectionRange(0, temp.value.length);
  const ok = document.execCommand('copy');
  document.body.removeChild(temp);
  return ok;
}

function bindCopyButtons(scope = document) {
  scope.querySelectorAll('[data-copy-link]').forEach((button) => {
    if (button.dataset.copyBound === 'true') return;
    button.dataset.copyBound = 'true';
    const link = button.dataset.copyLink;
    const defaultLabel = button.dataset.copyLabel || 'Copia link';
    button.addEventListener('click', async () => {
      try {
        if (navigator.clipboard?.writeText && window.isSecureContext) {
          await navigator.clipboard.writeText(link);
        } else if (!fallbackCopyText(link)) {
          throw new Error('clipboard unavailable');
        }
        button.textContent = 'Link copiato';
      } catch (error) {
        button.textContent = 'Copia fallita';
      }
      window.setTimeout(() => {
        button.textContent = defaultLabel;
      }, 1800);
    });
  });
}

function bindShareButtons(item, scope = document) {
  scope.querySelectorAll('[data-share-story]').forEach((copyButton) => {
    const kind = copyButton.dataset.shareKind || 'story';
    const link = kind === 'homepage' ? homepageUrl() : storyPageUrl(item);
    copyButton.dataset.copyLink = link;
    copyButton.dataset.copyLabel = kind === 'homepage' ? 'Copia link' : 'Copia link';
  });
  bindCopyButtons(scope);

  scope.querySelectorAll('[data-native-share]').forEach((nativeButton) => {
    const kind = nativeButton.dataset.shareKind || 'story';
    if (!navigator.share) {
      nativeButton.hidden = true;
    } else {
      nativeButton.addEventListener('click', async () => {
        const targetUrl = kind === 'homepage' ? homepageUrl() : storyPageUrl(item);
        try {
          await navigator.share({
            title: kind === 'homepage' ? DEFAULT_META.title : `${item.title} — Altair Nexus`,
            text: kind === 'homepage' ? DEFAULT_META.description : cleanPublicHook(item.hook, item.sourceLabel),
            url: targetUrl,
          });
        } catch (error) {
          if (error?.name !== 'AbortError') {
            window.prompt('Condividi questo link:', targetUrl);
          }
        }
      });
    }
  });
}

function setSelectedFeedItem(itemId) {
  document.querySelectorAll('.feed-item').forEach((node) => {
    node.classList.toggle('active', node.dataset.id === itemId);
  });
}

function activateStory(item, category, options = {}) {
  if (!item || !category) return;
  renderStory(item, category);
  updatePageMeta(item, category);
  setSelectedFeedItem(item.id);
  if (options.updateHistory !== false) {
    window.history.replaceState({ story: item.id }, '', deepLinkUrl(item.id));
  }
  if (options.scroll) {
    document.getElementById('focus')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function renderHeroLead(news, categories) {
  const lead = news.slice().sort((a, b) => byScoreDesc(a, b) || byTimestampDesc(a, b))[0];
  const category = categories.find((c) => c.id === lead.category);
  const host = document.getElementById('hero-lead');
  if (!host) return;
  host.innerHTML = `
    <div class="hero-lead-visual ${visualClassMap[lead.visual] || ''}"></div>
    <div class="hero-lead-body">
      <div class="story-meta">
        <span class="meta-pill">${category?.name || lead.category}</span>
        <span class="meta-pill">${lead.subcategory}</span>
        <span class="meta-pill">${fmtDate(lead.timestamp)}</span>
      </div>
      <h1>${lead.title}</h1>
      <p class="hero-lead-hook">${cleanPublicHook(lead.hook, lead.sourceLabel)}</p>
      <p class="hero-lead-body-copy">${splitBodyAndContext(lead.body).bodyParts[0] || ''}</p>
      <div class="hero-lead-actions">
        <button id="open-lead-story" class="primary-button">Apri approfondimento</button>
        ${sourceLink(lead)}
      </div>
    </div>
  `;

  document.getElementById('open-lead-story')?.addEventListener('click', () => {
    activateStory(lead, category, { scroll: true });
  });
}

function renderLatestFeed(news, categories) {
  const host = document.getElementById('latest-feed');
  host.innerHTML = news
    .slice()
    .sort(byTimestampDesc)
    .slice(0, 6)
    .map((item, idx) => {
      const category = categories.find((c) => c.id === item.category);
      return `
        <article class="feed-item ${idx === 0 ? 'active' : ''}" data-id="${item.id}">
          <div class="feed-time">${fmtDate(item.timestamp)}</div>
          <h3>${item.title}</h3>
          <p>${cleanPublicHook(item.hook, item.sourceLabel)}</p>
          <div class="story-meta">
            <span class="meta-pill">${category?.name || item.category}</span>
            <span class="meta-pill">${item.sourceLabel}</span>
          </div>
          <div class="card-cta">Apri focus <span aria-hidden="true">→</span></div>
        </article>
      `;
    }).join('');

  host.querySelectorAll('.feed-item').forEach((el) => {
    el.addEventListener('click', () => {
      const item = news.find((entry) => entry.id === el.dataset.id);
      const category = categories.find((c) => c.id === item.category);
      activateStory(item, category, { scroll: true });
    });
  });
}

function renderStory(item, category) {
  const panel = document.getElementById('story-panel');
  const { bodyParts, contextParts } = splitBodyAndContext(item.body);
  const storyBody = bodyParts
    .map((paragraph) => `<p class="story-body">${paragraph}</p>`)
    .join('');
  const aionOpinion = [...contextParts, item.opinion].filter(Boolean).join('\n\n') || cleanPublicHook(item.hook, item.sourceLabel);
  const aionContext = `<p class="story-body story-body-extended">${buildAionOpinion(item, category)}</p>`;
  const publicHook = cleanPublicHook(item.hook, item.sourceLabel) || item.hook || '';

  panel.innerHTML = `
    <div class="story-hero ${visualClassMap[item.visual] || ''}"></div>
    <div class="story-meta">
      <span class="meta-pill">${category.name}</span>
      <span class="meta-pill">${item.subcategory}</span>
      <span class="meta-pill">${fmtDate(item.timestamp)}</span>
      <span class="meta-pill">${item.sourceCount} fonti</span>
      <span class="meta-pill">Score ${item.qualityScore}</span>
    </div>
    <h3 class="story-title">${item.title}</h3>
    <p class="story-hook">${publicHook}</p>
    <div class="story-tags">${(item.tags || []).map((t) => `<span class="tag-pill">#${t}</span>`).join('')}</div>
    ${storyBody}
    <div class="story-footer-row">
      <div class="story-meta">
        <span class="meta-pill">Fonte: ${item.sourceLabel}</span>
        <span class="meta-pill">Categoria: ${category.name}</span>
      </div>
      <div class="story-meta story-meta-share">
        ${shareActions(item, { includeNativeShare: false })}
      </div>
    </div>
    <div class="story-footer-row story-footer-source-row">
      <div class="story-meta">
        ${sourceLink(item)}
      </div>
    </div>
    ${aionContext ? `<div class="story-opinion story-opinion-aion"><strong>L'opinione di Aion</strong>${aionContext}</div>` : ''}
    ${aionOpinion ? `<div class="story-opinion"><strong>Perché conta</strong><p>${aionOpinion}</p></div>` : ''}
  `;

  bindShareButtons(item);
}

function renderTopStories(news, categories) {
  const host = document.getElementById('top-stories');
  const top = news.slice().sort((a, b) => byScoreDesc(a, b) || byTimestampDesc(a, b)).slice(0, 3);
  host.innerHTML = top.map((item, idx) => {
    const category = categories.find((c) => c.id === item.category);
    return `
      <article class="top-story ${idx === 0 ? 'top-story-main' : ''}" data-id="${item.id}">
        <div class="top-story-visual ${visualClassMap[item.visual] || ''}"></div>
        <div class="top-story-content">
          <div class="story-meta">
            <span class="meta-pill">${category?.name || item.category}</span>
            <span class="meta-pill">${fmtDate(item.timestamp)}</span>
          </div>
          <h3>${item.title}</h3>
          <p>${cleanPublicHook(item.hook, item.sourceLabel)}</p>
          <div class="story-tags">${(item.tags || []).slice(0,3).map((t) => `<span class="tag-pill">#${t}</span>`).join('')}</div>
          <div class="card-cta">Apri focus <span aria-hidden="true">→</span></div>
        </div>
      </article>
    `;
  }).join('');

  host.querySelectorAll('.top-story').forEach((el) => {
    el.addEventListener('click', () => {
      const item = news.find((entry) => entry.id === el.dataset.id);
      const category = categories.find((c) => c.id === item.category);
      activateStory(item, category, { scroll: true });
    });
  });
}

function renderFeatured(news, categories) {
  const host = document.getElementById('featured-grid');
  const featured = news.slice().filter((item) => item.featured).sort(byTimestampDesc).slice(0, 4);
  host.innerHTML = featured.map((item) => {
    const category = categories.find((c) => c.id === item.category);
    return `
      <article class="feature-card" data-id="${item.id}">
        <div class="feature-visual ${visualClassMap[item.visual] || ''}"></div>
        <div class="story-meta">
          <span class="meta-pill">${category?.name || item.category}</span>
          <span class="meta-pill">${fmtDate(item.timestamp)}</span>
        </div>
        <h3>${item.title}</h3>
        <p>${cleanPublicHook(item.hook, item.sourceLabel)}</p>
        <div class="story-tags">${(item.tags || []).slice(0,3).map((t) => `<span class="tag-pill">#${t}</span>`).join('')}</div>
        <div class="card-cta card-cta-padded">Apri focus <span aria-hidden="true">→</span></div>
      </article>
    `;
  }).join('');

  host.querySelectorAll('.feature-card').forEach((el) => {
    el.addEventListener('click', () => {
      const item = news.find((entry) => entry.id === el.dataset.id);
      const category = categories.find((c) => c.id === item.category);
      activateStory(item, category, { scroll: true });
    });
  });
}

function renderSignals(signals) {
  const host = document.getElementById('hero-signals');
  host.innerHTML = signals.map((item) => `
    <div class="signal-row">
      <span>${item.label}</span>
      <strong>${item.value}</strong>
    </div>
  `).join('');
}

function renderCategories(categories, grouped) {
  const host = document.getElementById('category-grid');
  let activeId = categories[0]?.id;

  function draw() {
    host.innerHTML = categories.map((cat) => {
      const lead = grouped[cat.id]?.[0];
      const color = accentMap[cat.accent] || 'var(--cyan)';
      return `
        <button class="category-card ${cat.id === activeId ? 'active' : ''}" data-id="${cat.id}">
          <div class="category-top">
            <div>
              <div class="category-name">${cat.name}</div>
            </div>
            <span class="accent-dot" style="background:${color}"></span>
          </div>
          <div class="category-desc">${cat.description}</div>
          ${lead ? `
            <div class="category-title">${lead.title}</div>
            <div class="category-hook">${cleanPublicHook(lead.hook, lead.sourceLabel)}</div>
            <div class="card-cta">Apri focus <span aria-hidden="true">→</span></div>
          ` : '<div class="category-hook">Nessun contenuto ancora disponibile.</div>'}
        </button>
      `;
    }).join('');

    host.querySelectorAll('.category-card').forEach((el) => {
      el.addEventListener('click', () => {
        activeId = el.dataset.id;
        draw();
        const category = categories.find((c) => c.id === activeId);
        const lead = grouped[activeId]?.[0];
        if (category && lead) {
          activateStory(lead, category, { scroll: true });
        }
      });
    });
  }

  draw();
}

function renderDashboard(metrics) {
  document.getElementById('metric-news-today').textContent = metrics.newsToday;
  document.getElementById('metric-sources').textContent = metrics.sources;
  document.getElementById('metric-latest-update').textContent = metrics.latestUpdate;
  document.getElementById('metric-hottest').textContent = metrics.hottest;
  document.getElementById('metric-dominant').textContent = metrics.dominant;
  document.getElementById('metric-intensity').textContent = metrics.intensity;
  document.getElementById('metric-coverage').textContent = metrics.coverage;
  document.getElementById('metric-editor-note').textContent = metrics.editorNote;
  document.getElementById('most-viewed').innerHTML = metrics.mostViewed
    .map((item, idx) => `<div class="list-row"><span>${String(idx + 1).padStart(2, '0')}</span><strong>${item}</strong></div>`)
    .join('');
}

function renderFreshness(news, stats) {
  const host = document.getElementById('freshness-badge');
  if (!host) return;
  const freshness = stats?.editionUpdatedAt || news?.slice().sort(byTimestampDesc)[0]?.timestamp;
  if (!freshness) return;
  host.textContent = `Aggiornato ${fmtDate(freshness)}`;
}

function renderHomepageShare() {
  const host = document.getElementById('homepage-share-actions');
  if (!host) return;
  host.innerHTML = shareActions(null, {
    copyLabel: 'Copia link',
    includeNativeShare: false,
    className: 'share-actions-home',
    ariaLabel: 'Condivisione homepage'
  });
  bindShareButtons(null, host);
}

function renderAionBriefShare() {
  const host = document.getElementById('aion-brief-share-actions');
  if (!host) return;
  const briefUrl = 'https://nexus.universalis.it/site/aion-brief.html';
  const text = 'Aion Brief — Sintesi del giorno — Altair Nexus';
  host.innerHTML = `
    <div class="share-actions share-actions-home" aria-label="Condivisione Aion Brief">
      <button class="source-link story-share-button share-pill-main" type="button" data-copy-link="${briefUrl}" data-copy-label="Copia link">Copia link</button>
      <a class="source-link" href="https://wa.me/?text=${encodeURIComponent(`${text}\n\n${briefUrl}`)}" target="_blank" rel="noreferrer">WhatsApp</a>
      <a class="source-link" href="https://t.me/share/url?url=${encodeURIComponent(briefUrl)}&text=${encodeURIComponent(text)}" target="_blank" rel="noreferrer">Telegram</a>
      <a class="source-link" href="https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(briefUrl)}" target="_blank" rel="noreferrer">LinkedIn</a>
      <a class="source-link" href="https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(briefUrl)}" target="_blank" rel="noreferrer">X</a>
    </div>
  `;
  bindCopyButtons(host);
}

function renderAionBrief(news, categories) {
  const textHost = document.getElementById('aion-brief-text');
  const freshnessHost = document.getElementById('aion-brief-freshness');
  const dominantHost = document.getElementById('aion-dominant-signal');
  const themeHost = document.getElementById('aion-main-theme');
  const watchHost = document.getElementById('aion-watchpoint');
  if (!textHost || !freshnessHost || !news?.length) return;

  const sorted = news.slice().sort((a, b) => byScoreDesc(a, b) || byTimestampDesc(a, b));
  const top = sorted.slice(0, 3);
  const latest = news.slice().sort(byTimestampDesc)[0];
  const dominantCategory = categories.find((c) => c.id === top[0]?.category)?.name || top[0]?.category || 'Segnale in aggiornamento';
  const scoreSpread = top.map((item) => item.qualityScore || 0);
  const strongExecutionTheme = scoreSpread.some((score) => score >= 90)
    ? 'Esecuzione operativa e distribuzione'
    : 'Riposizionamento competitivo';
  const watchpoint = top[1]?.category === 'geo'
    ? 'Trasferimento del rischio geopolitico su energia e mercati'
    : 'Capacità di trasformare annuncio in adozione reale';

  const summary = [
    `Il quadro di oggi è più interessante per convergenza che per singola headline. Le storie più forti mostrano che il baricentro si sta spostando dall'effetto novità alla capacità di integrare tecnologie, asset industriali e distribuzione in flussi operativi concreti.`,
    `Letti insieme, ${top[0]?.title || 'il tema principale'}, ${top[1]?.title || 'il secondo segnale'} e ${top[2]?.title || 'il terzo fronte'} raccontano un mercato che premia esecuzione, presidio dei colli di bottiglia e velocità di messa a terra più dei semplici annunci.`
  ].join(' ');

  textHost.textContent = summary;
  freshnessHost.textContent = `Sintesi aggiornata ${fmtDate(latest.timestamp)}`;
  if (dominantHost) dominantHost.textContent = dominantCategory;
  if (themeHost) themeHost.textContent = strongExecutionTheme;
  if (watchHost) watchHost.textContent = watchpoint;
}

loadData().then(({ categories, news, stats }) => {
  const metrics = computeMetrics(categories, news, stats);
  renderBreaking(news);
  renderLatestFeed(news, categories);
  renderSignals(metrics.signals);
  renderFreshness(news, stats);
  renderHomepageShare();
  renderAionBriefShare();
  renderAionBrief(news, categories);
  renderTopStories(news, categories);
  renderCategories(categories, metrics.grouped);
  renderFeatured(news, categories);
  renderDashboard(metrics);

  const requestedStoryId = new URL(window.location.href).searchParams.get('story');
  const requestedStory = requestedStoryId ? news.find((item) => item.id === requestedStoryId) : null;
  const selectedItem = requestedStory || news.slice().sort((a, b) => byScoreDesc(a, b) || byTimestampDesc(a, b))[0] || news[0];
  const selectedCategory = selectedItem ? categories.find((c) => c.id === selectedItem.category) : null;

  if (selectedItem && selectedCategory) {
    activateStory(selectedItem, selectedCategory, {
      updateHistory: Boolean(requestedStory),
      scroll: Boolean(requestedStory)
    });
  } else {
    updatePageMeta(null, null);
  }

  window.addEventListener('popstate', () => {
    const storyId = new URL(window.location.href).searchParams.get('story');
    const item = storyId ? news.find((entry) => entry.id === storyId) : null;
    const fallback = news.slice().sort((a, b) => byScoreDesc(a, b) || byTimestampDesc(a, b))[0] || news[0];
    const nextItem = item || fallback;
    const nextCategory = nextItem ? categories.find((c) => c.id === nextItem.category) : null;
    if (nextItem && nextCategory) {
      activateStory(nextItem, nextCategory, { updateHistory: false, scroll: false });
    } else {
      updatePageMeta(null, null);
    }
  });
}).catch((error) => {
  console.error('Altair Nexus bootstrap failed', error);
  updatePageMeta(null, null);
  const panel = document.getElementById('story-panel');
  if (panel) {
    panel.innerHTML = `
      <div class="story-empty">
        Impossibile caricare gli articoli in questo momento.<br />
        <small>${error.message}</small>
      </div>
    `;
  }
});
