# Last build step: cuts the assembled single document `s` into one static page per section, each with its own
# address, <title>, description, canonical and structured data. exec'd by build.py (shares `s`, `rep`, `re`, `B`, `SITE`).
# Addresses and search titles live in pages.json. Output: ../index.html, ../<slug>/index.html, the same pages translated
# at build time in ../en/… and ../kk/… (i18n_build.py, dictionaries from translations.json + EXTRA_TR), ../404.html,
# ../sitemap.xml (with hreflang alternates) and ../public.txt (the list of public paths the server's deploy script copies).
import json as _json, os as _os, html as _html, sys as _sys
_sys.path.insert(0, B)
import i18n_build as _IB

# languages: dictionary key, folder, switcher code (the switcher and ?lang= say «kz»), html lang / hreflang
_LANGS = (('ru', '', 'ru'), ('kk', 'kk/', 'kz'), ('en', 'en/', 'en'))
_D = {'ru': {}}
_trj = _json.load(open(B + 'translations.json', encoding='utf-8'))
for _k, _v in globals().get('EXTRA_TR', {}).items(): _trj.setdefault(_k, _v)
for _l in ('en', 'kk'): _D[_l] = {ru: v[_l] for ru, v in _trj.items() if v.get(_l)}
def _t(x, lang): return _D[lang].get(_IB.norm(x), x) if lang != 'ru' else x

_cfg = _json.load(open(B + 'pages.json', encoding='utf-8'))['pages']
_ROOT = B + '../'
_ver = re.search(r'data-v="(\d{4}-\d{2}-\d{2})', s).group(1)

# ---- split: shell head | page blocks | shell tail ----
_main_end = s.index('</main>')
_starts = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="page" data-page="([^"]+)"[^>]*>', s[:_main_end])]
_head, _tail = s[:_starts[0][0]], s[_main_end:]
_head = re.sub(r'<!-- =+ [^>]* =+ -->\s*$', '', _head)
_blocks = {}
for _i, (_a, _id) in enumerate(_starts):
    _b = _starts[_i + 1][0] if _i + 1 < len(_starts) else _main_end
    _blocks[_id] = re.sub(r'\s*<!-- =+ [^>]* =+ -->\s*$', '\n\n', s[_a:_b])
_missing = set(_blocks) ^ {p['id'] for p in _cfg}
if _missing: sys.exit('pages.json and page blocks differ: %s' % sorted(_missing))

_script_at = _tail.rindex('<script>')
_tail_html, _js = _tail[:_script_at], _tail[_script_at:]
_ids = {k: set(re.findall(r'\sid="([^"]+)"', v)) for k, v in _blocks.items()}
_shell_ids = set(re.findall(r'\sid="([^"]+)"', _head + _tail_html))
_slug = {p['id']: p['slug'] for p in _cfg}
_anchors = {x: k for k, v in _ids.items() for x in v}

# ---- page script: one section per document, so route() no longer shows and hides sections ----
_a = _js.index('  function route(){')
_b = _js.index('  var themeBtn', _a)
_js = _js[:_a] + '''  // one section per document. A hash is an anchor on this page; hashes of the old single-page site
  // (#route, #tech, #followup ...) are sent to the page that now holds them. #kz / #en still switch language.
  function route(){
    var id = location.hash.slice(1);
    if(id === 'kz' || id === 'en'){ try{ localStorage.setItem('hb-lang', id); }catch(e){} location.replace(LANG_URLS[id]); return; }
    curPage = pages[0];
    if(id && !document.getElementById(id)){
      var pg = URLS.hasOwnProperty(id) ? id : ANCHORS[id];
      if(pg && pg !== curPage.dataset.page){ location.replace(URLS[pg] + (pg === id ? '' : '#' + id)); return; }
    }
    setPageTitle();
    fitSvgLabels();
    nav.classList.remove('open'); burger.setAttribute('aria-expanded','false');
    if(more) more.open = false;
    drawRoute();
  }

''' + _js[_b:]
_js = rep(_js, "var pages = Array.prototype.slice.call(document.querySelectorAll('[data-page]'));",
          "var pages = Array.prototype.slice.call(document.querySelectorAll('[data-page]'));\n  /*__PAGE_VARS__*/")
_js = rep(_js, "s.src = 'i18n/' + key + '.js?v=' + VERSION;", "s.src = ROOT + 'i18n/' + key + '.js?v=' + VERSION;")
# language = address: the page is already translated, the switcher is a set of links, ?lang= and a saved choice redirect
_js = rep(_js, "    if(key === 'ru' || DICTS[key]) return cb();",
          "    if(!DICTS[key] && window['__I18N_' + key]) DICTS[key] = window['__I18N_' + key];\n    if(key === 'ru' || DICTS[key]) return cb();")
_js = rep(_js, "    langBtns.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.lang === btn ? 'true' : 'false'); });\n", "")
_js = rep(_js, "  langBtns.forEach(function(b){ b.addEventListener('click', function(){ setLang(b.dataset.lang, true); }); });",
          "  langBtns.forEach(function(b){ b.addEventListener('click', function(){ try{ localStorage.setItem('hb-lang', b.dataset.lang); }catch(e){} }); });")
_a = _js.index('  function initLang(){'); _b = _js.index('\n  }\n', _a) + 5
_js = _js[:_a] + '''  function initLang(){
    var q = (location.search.match(/[?&]lang=(ru|kz|kk|en)/) || [])[1];
    if(q === 'kk') q = 'kz';
    var saved = null;
    try{ saved = localStorage.getItem('hb-lang'); }catch(e){}
    if(q){ try{ localStorage.setItem('hb-lang', q); }catch(e){} }
    // an explicit ?lang= always wins; a saved choice only moves a visitor away from the Russian (default) address
    var want = q || (PAGE_LANG === 'ru' ? saved : null);
    if(want && want !== PAGE_LANG && LANG_URLS[want]){ location.replace(LANG_URLS[want] + location.hash); return; }
    if(PAGE_LANG !== 'ru') setLang(PAGE_LANG, false); else applyDom();
  }
''' + _js[_b:]

_js = rep(_js, "if(location.hash === '' || location.hash === '#home') drawRoute();", "drawRoute();")
_js = rep(_js, "more.setAttribute('href', '#stage-' + (i + 1));", "more.setAttribute('href', URLS.route + '#stage-' + (i + 1));")
_js = rep(_js, "if(curPage) document.title = tr(curPage.dataset.title) + ' — HemaBridge · ' + tr('Центр гематологии');",
          "if(curPage) document.title = tr(curPage.dataset.seoTitle || curPage.dataset.title);")

def _url(pid, P):
    return (P + _slug[pid] + '/') if _slug[pid] else (P or './')

def _links(html, cur, P, L=''):
    def fix(m):
        x = m.group(2)
        if x in _slug: return m.group(1) + _url(x, P + L) + '"'
        if not x or x in _shell_ids or x in _ids.get(cur, ()): return m.group(0)
        if x in _anchors: return m.group(1) + _url(_anchors[x], P + L) + '#' + x + '"'
        sys.exit('link to unknown anchor #%s on page %s' % (x, cur))
    html = re.sub(r'(<a\b[^>]*?\shref=")#([^"]*)"', fix, html)
    return re.sub(r'((?:src|href)=")((?:img|docs|i18n)/)', lambda m: m.group(1) + P + m.group(2), html)

def _text(x): return re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', '', x))).strip()

def _ld(p, block, canon, lang='ru', title=None, desc=None):
    org = _json.loads(re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', _head, re.S).group(1))
    org.pop('@context')
    site = {'@type': 'WebSite', '@id': SITE + '#site', 'url': SITE, 'name': 'HemaBridge', 'inLanguage': ['ru', 'kk', 'en'], 'publisher': {'@id': org['@id']}}
    page = {'@type': 'WebPage' if p['id'] in ('home', 'legal', 'cabinet', 'apply', 'partners', 'doctors', 'about') else 'MedicalWebPage',
            '@id': canon + '#page', 'url': canon, 'name': title or p['title'], 'description': desc or p['desc'], 'inLanguage': lang,
            'isPartOf': {'@id': SITE + '#site'}, 'about': {'@id': org['@id']}}
    graph = [org, site, page]
    if p['slug']:
        page['breadcrumb'] = {'@id': canon + '#crumbs'}
        graph.append({'@type': 'BreadcrumbList', '@id': canon + '#crumbs', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': _t('Главная', lang), 'item': SITE + dict((k, d) for k, d, _ in _LANGS)[lang]},
            {'@type': 'ListItem', 'position': 2, 'name': _t(p['nav'], lang), 'item': canon}]})
    qa = re.findall(r'<details><summary>(.*?)</summary><div>(.*?)</div></details>', block, re.S) if 'class="wrap faq"' in block else []
    if qa:
        graph.append({'@type': 'FAQPage', '@id': canon + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': _text(q), 'acceptedAnswer': {'@type': 'Answer', 'text': _text(a)}} for q, a in qa]})
    return _json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('</', '<\\/')

def _canon(p, d=''):
    return SITE + d + (p['slug'] + '/' if p.get('slug') else '')

def _switcher(urls, lang):
    return '<div class="lang" role="group" aria-label="Язык сайта">\n' + ''.join(
        '        <a href="%s" data-lang="%s" hreflang="%s" lang="%s"%s>%s</a>\n' % (urls[b], b, k, k, ' aria-current="true"' if k == lang else '', b.upper())
        for k, _, b in _LANGS) + '      </div>'

def _page(p, block, root, canon, lang='ru'):
    """root: relative path from this page to the site root (assets); page links also get the language folder."""
    cur = p['id']
    L = dict((k, d) for k, d, _ in _LANGS)[lang]
    e = lambda x: _html.escape(x, quote=True)
    title, desc = _t(p['title'], lang), _t(p['desc'], lang)
    if lang != 'ru': block = _IB.translate_body('<body>' + block, _D[lang])[len('<body>'):]
    head = _head
    head = rep(head, '<html lang="ru">', '<html lang="%s">' % lang)
    head = rep(head, re.search(r'<title>.*?</title>', head).group(0), '<title>%s</title>' % e(title))
    for pat, val in ((r'(<link rel="canonical" href=")[^"]*', canon), (r'(<meta property="og:url" content=")[^"]*', canon),
                     (r'(<meta name="description" content=")[^"]*', e(desc)),
                     (r'(<meta property="og:title" content=")[^"]*', e(title)),
                     (r'(<meta property="og:description" content=")[^"]*', e(desc))):
        head, n = re.subn(pat, lambda m: m.group(1) + val, head)
        assert n == 1, pat
    if p.get('slug') != '404':   # hreflang: every language version of this page, Russian as the default
        alt = ''.join('<link rel="alternate" hreflang="%s" href="%s">\n' % (k, _canon(p, d)) for k, d, _ in _LANGS)
        alt += '<link rel="alternate" hreflang="x-default" href="%s">' % _canon(p)
        head = rep(head, '<link rel="canonical" href="%s">' % canon, '<link rel="canonical" href="%s">\n%s' % (canon, alt))
    head = rep(head, '<meta property="og:locale" content="ru_KZ">', '<meta property="og:locale" content="%s">' % {'ru': 'ru_KZ', 'en': 'en_US', 'kk': 'kk_KZ'}[lang])
    if lang != 'ru':
        head = re.sub(r'<meta name="keywords" content="[^"]*">\n', '', head)   # Russian search phrases only
        head = re.sub(r'(<meta property="og:image:alt" content=")([^"]*)', lambda m: m.group(1) + e(_t(_html.unescape(m.group(2)), lang)), head)
    a = head.index('<script type="application/ld+json">') + len('<script type="application/ld+json">')
    head = head[:a] + '\n' + _ld(p, block, canon, lang, title, desc) + '\n' + head[head.index('</script>', a):]
    head = head.replace('url("img/', 'url("' + root + 'img/')
    if cur in _slug and cur != 'home':  # mark the current section in the menu
        n0 = head.index('<nav '); n1 = head.index('</nav>')
        head = head[:n0] + head[n0:n1].replace('<a href="#%s"' % cur, '<a aria-current="page" href="#%s"' % cur) + head[n1:]
    tail = p['slug'] + '/' if p.get('slug') and p['slug'] != '404' else ''
    lang_urls = dict((b, (root + d + tail) or './') for k, d, b in _LANGS)
    sw = re.search(r'<div class="lang" role="group" aria-label="Язык сайта">.*?</div>', head, re.S).group(0)
    head = head.replace(sw, _switcher(lang_urls, lang))
    block = block.replace(' hidden>', '>', 1) if block.startswith('<div class="page"') and ' hidden>' in block[:block.index('\n')] else block
    block = block.replace('<div class="page" ', '<div class="page" data-seo-title="%s" ' % e(title), 1)
    urls = {k: _url(k, root + L) for k in _slug}
    vars_ = 'var ROOT = %s, URLS = %s, ANCHORS = %s, PAGE_LANG = %s, LANG_URLS = %s;' % (
        _json.dumps(root), _json.dumps(urls), _json.dumps(_anchors, ensure_ascii=False, sort_keys=True),
        _json.dumps({'kk': 'kz'}.get(lang, lang)), _json.dumps(lang_urls))
    js = _js.replace('/*__PAGE_VARS__*/', vars_)
    if lang != 'ru':   # dictionary before the page script: scripts paint in this language from the first frame
        js = '<script src="%si18n/%s.js?v=%s"></script>\n' % (root, lang, _ver_full) + js
    html = _links(head, cur, root, L) + _links(block, cur, root, L) + _links(_tail_html, cur, root, L) + js
    if lang != 'ru': html = _IB.translate_body(html, _D[lang])
    html = re.sub(r'(<span class="ver" data-v="([^"]+)">)</span>',
                  lambda m: m.group(1) + _html.escape(_t('версия', lang)) + ' ' + m.group(2) + '</span>', html)
    html = html.replace('https://hemcenter.kz/ru" data-hc', 'https://hemcenter.kz/%s" data-hc' % lang)
    assert html.count('<h1') == 1, (cur, html.count('<h1'))
    return html

_ver_full = re.search(r'data-v="([^"]+)"', s).group(1)
_public = ['index.html', '404.html', 'sitemap.xml', 'robots.txt', '.htaccess', 'i18n/', 'img/', 'docs/', 'en/', 'kk/']
_sitemap = []
for _p in _cfg:
    for _lang, _d, _ in _LANGS:
        _rel = _d + (_p['slug'] + '/' if _p['slug'] else '')
        _out = _page(_p, _blocks[_p['id']], '../' * _rel.count('/'), _canon(_p, _d), _lang)
        _os.makedirs(_ROOT + _rel, exist_ok=True)
        open(_ROOT + _rel + 'index.html', 'w', encoding='utf-8').write(_out)
    if _p['slug']: _public.append(_p['slug'] + '/')
    if not _p.get('noindex') and not _p.get('draft'): _sitemap.append(_p)

# 404 page: same shell, absolute paths because it is served at any depth
_nf = {'id': '404', 'slug': '404', 'nav': 'Страница не найдена', 'title': 'Страница не найдена — HemaBridge', 'desc': 'Такой страницы на сайте HemaBridge нет.'}
_nf_block = '''<div class="page" data-page="404" data-title="Страница не найдена">
  <section class="page-head glow">
    <div class="wrap">
      <div class="crumb"><a href="#home">Главная</a> / Страница не найдена</div>
      <h1>Страница не найдена</h1>
      <p class="lead">Возможно, адрес изменился. Начните с главной или сразу расскажите о своей ситуации врачу.</p>
      <div class="actions"><a class="btn btn-primary" href="#home">На главную</a><a class="btn btn-ghost" href="#apply">Получить врачебную оценку</a></div>
    </div>
  </section>
</div>

'''
_ids['404'] = set(); _slug['404'] = '404'
_out = _page(_nf, _nf_block, '/', SITE + '404.html')
del _slug['404']
open(_ROOT + '404.html', 'w', encoding='utf-8').write(_out)

_alts = lambda p: ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (k, _canon(p, d)) for k, d, _ in _LANGS) + \
    '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % _canon(p)
open(_ROOT + 'sitemap.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + ''.join('  <url><loc>%s</loc><lastmod>%s</lastmod>%s</url>\n' % (_canon(p, d), _ver, _alts(p)) for p in _sitemap for k, d, _ in _LANGS) + '</urlset>\n')
open(_ROOT + 'public.txt', 'w', encoding='utf-8').write('\n'.join(_public) + '\n')
print('pages:', len(_cfg), 'x', len(_LANGS), 'languages + 404; sitemap:', len(_sitemap) * len(_LANGS))
