# Last build step: cuts the assembled single document `s` into one static page per section, each with its own
# address, <title>, description, canonical and structured data. exec'd by build.py (shares `s`, `rep`, `re`, `B`, `SITE`).
# Addresses and search titles live in pages.json. Output: ../index.html, ../<slug>/index.html, ../404.html,
# ../sitemap.xml and ../public.txt (the list of public paths the server's deploy script copies).
import json as _json, os as _os, html as _html

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
    if(id === 'kz' || id === 'en'){ setLang(id, true); history.replaceState(null, '', location.pathname + location.search); id = ''; }
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
_js = rep(_js, "if(location.hash === '' || location.hash === '#home') drawRoute();", "drawRoute();")
_js = rep(_js, "more.setAttribute('href', '#stage-' + (i + 1));", "more.setAttribute('href', URLS.route + '#stage-' + (i + 1));")
_js = rep(_js, "if(curPage) document.title = tr(curPage.dataset.title) + ' — HemaBridge · ' + tr('Центр гематологии');",
          "if(curPage) document.title = tr(curPage.dataset.seoTitle || curPage.dataset.title);")

def _url(pid, P):
    return (P + _slug[pid] + '/') if _slug[pid] else (P or './')

def _links(html, cur, P):
    def fix(m):
        x = m.group(2)
        if x in _slug: return m.group(1) + _url(x, P) + '"'
        if not x or x in _shell_ids or x in _ids.get(cur, ()): return m.group(0)
        if x in _anchors: return m.group(1) + _url(_anchors[x], P) + '#' + x + '"'
        sys.exit('link to unknown anchor #%s on page %s' % (x, cur))
    html = re.sub(r'(<a\b[^>]*?\shref=")#([^"]*)"', fix, html)
    return re.sub(r'((?:src|href)=")((?:img|docs|i18n)/)', lambda m: m.group(1) + P + m.group(2), html)

def _text(x): return re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', '', x))).strip()

def _ld(p, block, canon):
    org = _json.loads(re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', _head, re.S).group(1))
    org.pop('@context')
    site = {'@type': 'WebSite', '@id': SITE + '#site', 'url': SITE, 'name': 'HemaBridge', 'inLanguage': 'ru', 'publisher': {'@id': org['@id']}}
    page = {'@type': 'WebPage' if p['id'] in ('home', 'legal', 'cabinet', 'apply', 'partners', 'doctors', 'about') else 'MedicalWebPage',
            '@id': canon + '#page', 'url': canon, 'name': p['title'], 'description': p['desc'], 'inLanguage': 'ru',
            'isPartOf': {'@id': SITE + '#site'}, 'about': {'@id': org['@id']}}
    graph = [org, site, page]
    if p['slug']:
        page['breadcrumb'] = {'@id': canon + '#crumbs'}
        graph.append({'@type': 'BreadcrumbList', '@id': canon + '#crumbs', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': p['nav'], 'item': canon}]})
    qa = re.findall(r'<details><summary>(.*?)</summary><div>(.*?)</div></details>', block, re.S) if 'class="wrap faq"' in block else []
    if qa:
        graph.append({'@type': 'FAQPage', '@id': canon + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': _text(q), 'acceptedAnswer': {'@type': 'Answer', 'text': _text(a)}} for q, a in qa]})
    return _json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('</', '<\\/')

def _page(p, block, P, canon):
    cur = p['id']
    e = lambda x: _html.escape(x, quote=True)
    head = _head
    head = rep(head, re.search(r'<title>.*?</title>', head).group(0), '<title>%s</title>' % e(p['title']))
    for pat, val in ((r'(<link rel="canonical" href=")[^"]*', canon), (r'(<meta property="og:url" content=")[^"]*', canon),
                     (r'(<meta name="description" content=")[^"]*', e(p['desc'])),
                     (r'(<meta property="og:title" content=")[^"]*', e(p['title'])),
                     (r'(<meta property="og:description" content=")[^"]*', e(p['desc']))):
        head, n = re.subn(pat, lambda m: m.group(1) + val, head)
        assert n == 1, pat
    a = head.index('<script type="application/ld+json">') + len('<script type="application/ld+json">')
    head = head[:a] + '\n' + _ld(p, block, canon) + '\n' + head[head.index('</script>', a):]
    head = head.replace('url("img/', 'url("' + P + 'img/')
    if cur in _slug and cur != 'home':  # mark the current section in the menu
        n0 = head.index('<nav '); n1 = head.index('</nav>')
        head = head[:n0] + head[n0:n1].replace('<a href="#%s"' % cur, '<a aria-current="page" href="#%s"' % cur) + head[n1:]
    block = block.replace(' hidden>', '>', 1) if block.startswith('<div class="page"') and ' hidden>' in block[:block.index('\n')] else block
    block = block.replace('<div class="page" ', '<div class="page" data-seo-title="%s" ' % e(p['title']), 1)
    urls = {k: _url(k, P) for k in _slug}
    vars_ = 'var ROOT = %s, URLS = %s, ANCHORS = %s;' % (_json.dumps(P), _json.dumps(urls), _json.dumps(_anchors, ensure_ascii=False, sort_keys=True))
    html = _links(head, cur, P) + _links(block, cur, P) + _links(_tail_html, cur, P) + _js.replace('/*__PAGE_VARS__*/', vars_)
    assert html.count('<h1') == 1, (cur, html.count('<h1'))
    return html

_public = ['index.html', '404.html', 'sitemap.xml', 'robots.txt', '.htaccess', 'i18n/', 'img/', 'docs/']
_sitemap = []
for _p in _cfg:
    _canon = SITE + (_p['slug'] + '/' if _p['slug'] else '')
    _out = _page(_p, _blocks[_p['id']], '../' if _p['slug'] else '', _canon)
    if _p['slug']:
        _os.makedirs(_ROOT + _p['slug'], exist_ok=True)
        _public.append(_p['slug'] + '/')
    open(_ROOT + (_p['slug'] + '/' if _p['slug'] else '') + 'index.html', 'w', encoding='utf-8').write(_out)
    if not _p.get('noindex') and not _p.get('draft'): _sitemap.append(_canon)

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

open(_ROOT + 'sitemap.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join('  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n' % (u, _ver) for u in _sitemap) + '</urlset>\n')
open(_ROOT + 'public.txt', 'w', encoding='utf-8').write('\n'.join(_public) + '\n')
print('pages:', len(_cfg), '+ 404; sitemap:', len(_sitemap))
