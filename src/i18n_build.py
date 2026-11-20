"""Build-time copy of applyDom() from i18n_runtime.js: translates a finished Russian page into English or Kazakh,
so /en/… and /kk/… are served as real pages (robots and link previews see the translation without running JS).

Same rules as the runtime: text nodes of <body> outside <script>/<style>, plus the
alt / aria-label / title / placeholder / data-label (and data-title) attributes; a string is looked up by its
whitespace-normalised form; anything missing from the dictionary stays Russian. Unlike the runtime, elements with a plain
[data-i18n-skip] (containers a script repaints: route step panel, clinic counter) are translated too, so robots see
the language; only [data-i18n-skip="keep"] (text that is deliberately in one language, e.g. download links) is left alone. The page script still loads the
dictionary and repaints what scripts draw (route map, clinic counter …).
"""
import html as _h, re as _r

ATTRS = ('alt', 'aria-label', 'title', 'placeholder', 'data-label', 'data-title')
_TOKEN = _r.compile(r'(<!--.*?-->|<[^>]*>)', _r.S)
_TAG = _r.compile(r'<\s*(/?)\s*([A-Za-z][\w:-]*)')
_VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
norm = lambda x: _r.sub(r'\s+', ' ', x).strip()

def _attr_fix(tag, d):
    cls = (_r.search(r'\sclass="([^"]*)"', tag) or [None, ''])[1].split()
    if 'rt-stop' in cls or 'theme-btn' in cls: return tag
    def one(m):
        v = _h.unescape(m.group(2)); k = norm(v)
        return m.group(1) + _h.escape(d[k], quote=True) + '"' if k in d else m.group(0)
    for a in ATTRS:
        tag = _r.sub(r'(\s%s=")([^"]*)"' % _r.escape(a), one, tag)
    return tag

def translate_body(doc, d):
    """Translates everything from <body …> on; the <head> is left to the caller."""
    b = doc.index('<body')
    out, raw, skip = [], None, None          # raw: inside script/style; skip: [tag, depth] of a data-i18n-skip element
    for tok in _TOKEN.split(doc[b:]):
        if not tok: continue
        if tok.startswith('<!--'): out.append(tok); continue
        if tok.startswith('<'):
            m = _TAG.match(tok)
            if not m: out.append(tok); continue
            close, name = m.group(1) == '/', m.group(2).lower()
            if raw:
                if close and name == raw: raw = None
                out.append(tok); continue
            selfclose = tok.endswith('/>') or name in _VOID
            if skip:
                if name == skip[0] and not selfclose: skip[1] += -1 if close else 1
                if skip[1] == 0: skip = None
                out.append(tok); continue
            if not close and 'data-i18n-skip="keep"' in tok:
                out.append(_attr_fix(tok, d) if name == 'svg' else tok)
                if not selfclose: skip = [name, 1]
                continue
            if not close and name in ('script', 'style'): raw = name
            out.append(tok if close else _attr_fix(tok, d)); continue
        if raw or skip or not tok.strip():
            out.append(tok); continue
        u = _h.unescape(tok)
        m = _r.match(r'^(\s*)(.*?)(\s*)$', u, _r.S)
        k = norm(m.group(2))
        out.append(_h.escape(m.group(1) + d[k] + m.group(3), quote=False) if k in d else tok)
    return doc[:b] + ''.join(out)
