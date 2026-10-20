# Writes ../i18n/en.js and ../i18n/kk.js from translations.json (Russian text -> {en, kk}).
import json, os
_tp = B + 'translations.json'
if os.path.exists(_tp):
    _tr = json.load(open(_tp, encoding='utf-8'))
    _out = B + '../i18n/'
    os.makedirs(_out, exist_ok=True)
    for _lang in ('en', 'kk'):
        _d = {ru: v[_lang] for ru, v in _tr.items() if v.get(_lang)}
        _js = 'window.__I18N_%s=%s;\n' % (_lang, json.dumps(_d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
        open(_out + _lang + '.js', 'w', encoding='utf-8').write(_js)
    print('i18n:', len(_tr), 'strings')
