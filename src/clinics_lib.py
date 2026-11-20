"""Clinics: one schema for the coordinator's table, clinics.json and the «Клиники» page.

Used by content_update.py (build: validate + render) and clinics_sheet.py (xlsx/CSV <-> clinics.json).
Every clinic has the same fields in the same order; an empty field is shown as «нет данных», never dropped.
"""
import datetime, html, re

# ---- fixed vocabularies -------------------------------------------------------------------------
STATUS = {  # code -> (label on the site and in the table, en, kk)
    'check': ('Кандидат · проверка', 'Candidate · under review', 'Үміткер · тексерілуде'),
    'talks': ('Кандидат · переговоры', 'Candidate · in negotiation', 'Үміткер · келіссөздер'),
    'partner': ('Партнёр', 'Partner', 'Серіктес'),
}
TRI = {'yes': 'да', 'no': 'нет', 'unknown': 'нет данных'}          # table value for each code
TKM = (('auto', 'Аутологичная', 'ауто'), ('allo', 'Аллогенная', 'алло'), ('haplo', 'Гаплоидентичная', 'гапло'))
COUNTRIES = {  # Russian name -> (en, kk). Add a country here before the coordinator can pick it.
    'Турция': ('Turkey', 'Түркия'), 'Индия': ('India', 'Үндістан'), 'Беларусь': ('Belarus', 'Беларусь'),
    'Израиль': ('Israel', 'Израиль'), 'Германия': ('Germany', 'Германия'), 'Южная Корея': ('South Korea', 'Оңтүстік Корея'),
    'Китай': ('China', 'Қытай'), 'Россия': ('Russia', 'Ресей'), 'ОАЭ': ('UAE', 'БАӘ'), 'Испания': ('Spain', 'Испания'),
    'Италия': ('Italy', 'Италия'), 'Сингапур': ('Singapore', 'Сингапур'), 'США': ('USA', 'АҚШ'), 'Узбекистан': ('Uzbekistan', 'Өзбекстан'),
}
# free-text fields (Russian), in card order; each may have an en/kk translation
TEXT = ('profile', 'tkm_note', 'cart_note', 'accreditation', 'facilities', 'foreign')
SAID = {'profile': 'Профиль', 'tkm': 'ТКМ', 'cart': 'CAR-T', 'accreditation': 'Аккредитации',
        'facilities': 'Оснащение и структура', 'foreign': 'Иностранным пациентам'}   # fields that can be «по данным клиники»
MONTHS = (('январь', 'January', 'қаңтар'), ('февраль', 'February', 'ақпан'), ('март', 'March', 'наурыз'), ('апрель', 'April', 'сәуір'),
          ('май', 'May', 'мамыр'), ('июнь', 'June', 'маусым'), ('июль', 'July', 'шілде'), ('август', 'August', 'тамыз'),
          ('сентябрь', 'September', 'қыркүйек'), ('октябрь', 'October', 'қазан'), ('ноябрь', 'November', 'қараша'), ('декабрь', 'December', 'желтоқсан'))
STALE_MONTHS = 12

# ---- validation ---------------------------------------------------------------------------------
def validate(data, where='клиника %d', first=1):
    """Returns (errors, warnings): lists of strings naming the clinic (or table row) and the field."""
    err, warn, ids = [], [], set()
    for n, c in enumerate(data.get('clinics', []), first):
        who = (where % n) + ' (%s)' % (c.get('name') or c.get('id') or '?')
        def e(msg): err.append('%s: %s' % (who, msg))
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', c.get('id') or ''):
            e('id — латиницей, цифрами и дефисами, например florence-nightingale')
        elif c['id'] in ids: e('id «%s» повторяется' % c['id'])
        ids.add(c.get('id'))
        for f in ('name', 'city'):
            if not (c.get(f) or '').strip(): e('не заполнено поле «%s»' % {'name': 'Название', 'city': 'Город'}[f])
        if c.get('country') not in COUNTRIES:
            e('страна «%s» не из списка (%s); новую страну добавляют в src/clinics_lib.py' % (c.get('country'), ', '.join(COUNTRIES)))
        if c.get('status') not in STATUS: e('статус: «%s» — допустимо: %s' % (c.get('status'), ', '.join(v[0] for v in STATUS.values())))
        if not re.fullmatch(r'20\d\d-(0[1-9]|1[0-2])', c.get('checked') or ''): e('дата проверки — в виде ГГГГ-ММ, например 2026-11')
        for k, label, _ in TKM:
            if (c.get('tkm') or {}).get(k) not in TRI: e('ТКМ %s: «%s» — допустимо: да, нет, нет данных' % (label.lower(), (c.get('tkm') or {}).get(k)))
        if c.get('cart') not in TRI: e('CAR-T: «%s» — допустимо: да, нет, нет данных' % c.get('cart'))
        for f in c.get('clinic_said', []):
            if f not in SAID: e('«Только по данным клиники»: «%s» — допустимо: %s' % (f, ', '.join(SAID.values())))
        if not c.get('sources'): e('нет ни одного источника')
        for s in c.get('sources', []):
            if len(s) != 2 or not s[0].strip() or not re.match(r'https://\S+$', s[1]):
                e('источник «%s» — нужно «название | https://ссылка»' % ' | '.join(map(str, s)))
        for lang in ('en', 'kk'):
            tr = c.get(lang) or {}
            for f in TEXT + ('city',):
                if (c.get(f) or '').strip() and not (tr.get(f) or '').strip():
                    warn.append('%s: нет перевода (%s) поля «%s» — на сайте будет русский текст' % (who, lang.upper(), f))
            if re.search('[А-Яа-яЁё]', c.get('name') or '') and not (tr.get('name') or '').strip():
                warn.append('%s: нет перевода (%s) названия' % (who, lang.upper()))
    return err, warn

# ---- rendering ----------------------------------------------------------------------------------
_e = lambda x: html.escape(x or '', quote=True)
ND = 'нет данных'

def month_label(ym):
    y, m = map(int, ym.split('-'))
    ru, en, kk = MONTHS[m - 1]
    return '%s %d' % (ru, y), '%s %d' % (en, y), '%d жылғы %s' % (y, kk)

def _stale(ym, today):
    y, m = map(int, ym.split('-'))
    return (today.year - y) * 12 + (today.month - m) > STALE_MONTHS

def render(data, today=None):
    """Returns (html, extra_translations) for the clinics section. extra: {ru: {'en':…, 'kk':…}}."""
    today = today or datetime.date.today()
    extra = {}
    def tr(ru, en, kk):
        if ru and (en or kk): extra.setdefault(ru, {'en': en or '', 'kk': kk or ''})
        return ru
    said = '<span class="said" title="Сведения с сайта клиники, ещё не подтверждённые независимо">по данным клиники</span>'
    def field(label, inner, key, c):
        return '<div class="cl-row"><dt>%s</dt><dd>%s%s</dd></div>' % (label, inner, (' ' + said) if key in c.get('clinic_said', []) else '')
    def text(c, f):
        v = (c.get(f) or '').strip()
        if not v: return '<span class="nd">%s</span>' % ND
        tr(v, (c.get('en') or {}).get(f), (c.get('kk') or {}).get(f))
        return _e(v)
    clinics = data['clinics']
    order = []                                   # countries in first-appearance order
    for c in clinics:
        if c['country'] not in order: order.append(c['country'])
    groups = ''
    for country in order:
        items = ''
        cs = [c for c in clinics if c['country'] == country]
        for c in cs:
            en, kk = c.get('en') or {}, c.get('kk') or {}
            tr(c['name'], en.get('name'), kk.get('name')); tr(c['city'], en.get('city'), kk.get('city'))
            methods = [k for k, _, _ in TKM if c['tkm'][k] == 'yes'] + (['cart'] if c['cart'] == 'yes' else [])
            tags = ''.join('<span class="tag">%s</span>' % short for k, _, short in TKM if c['tkm'][k] == 'yes')
            if c['cart'] == 'yes': tags += '<span class="tag tag-cart">CAR-T</span>'
            q = ' '.join(x for x in (c['name'], c['city'], en.get('name'), en.get('city'), kk.get('name'), kk.get('city'), country) + COUNTRIES[country] if x).lower()
            tkm = ''.join('<li class="t-%s"><span>%s</span> — <span>%s</span></li>' % (c['tkm'][k], label, TRI[c['tkm'][k]]) for k, label, _ in TKM)
            tkm = '<ul class="cl-tkm">%s</ul>' % tkm
            if (c.get('tkm_note') or '').strip(): tkm += '<p>%s</p>' % text(c, 'tkm_note')
            cart = '<span class="t-%s">%s</span>' % (c['cart'], TRI[c['cart']].capitalize())
            if (c.get('cart_note') or '').strip(): cart += '. <span>%s</span>' % text(c, 'cart_note')
            src = ', '.join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (_e(u), _e(n)) for n, u in c['sources'])
            ru_m, en_m, kk_m = month_label(c['checked']); tr(ru_m, en_m, kk_m)
            checked = _e(ru_m) + (' <span class="stale">требует перепроверки</span>' if _stale(c['checked'], today) else '')
            card = ''.join((
                field('Страна и город', '<span>%s</span>, <span>%s</span>' % (_e(country), _e(c['city'])), '', c),
                field('Профиль', text(c, 'profile'), 'profile', c),
                field('ТКМ', tkm, 'tkm', c),
                field('CAR-T', cart, 'cart', c),
                field('Аккредитации', text(c, 'accreditation'), 'accreditation', c),
                field('Оснащение и структура', text(c, 'facilities'), 'facilities', c),
                field('Иностранным пациентам', text(c, 'foreign'), 'foreign', c),
                field('Источники', src, '', c),
                field('Сведения проверены', checked, '', c)))
            items += '''          <details class="cl" id="%s" data-country="%s" data-status="%s" data-m="%s" data-q="%s">
            <summary><span class="cl-head"><span class="cl-name">%s</span><span class="cl-city">%s</span></span><span class="cl-tags">%s</span><span class="cl-st st-%s">%s</span></summary>
            <dl class="cl-card">%s</dl>
          </details>
''' % (_e(c['id']), _e(country), c['status'], ' '.join(methods), _e(q), _e(c['name']), _e(c['city']), tags, c['status'], STATUS[c['status']][0], card)
        groups += '''        <section class="cl-group" data-country="%s">
          <h3><span>%s</span> <span class="cl-n">%d</span></h3>
%s        </section>
''' % (_e(country), _e(country), len(cs), items)
    opt = lambda v, t: '<option value="%s">%s</option>' % (_e(v), _e(t))
    tools = ('''      <form class="cl-tools" role="search" hidden>
        <label class="cl-f cl-search"><span>Поиск</span><input type="search" placeholder="Название или город" autocomplete="off"></label>
        <label class="cl-f"><span>Страна</span><select data-f="country">%s</select></label>
        <label class="cl-f"><span>Метод</span><select data-f="method">%s</select></label>
        <label class="cl-f"><span>Статус</span><select data-f="status">%s</select></label>
        <button type="reset" class="btn btn-ghost cl-reset">Сбросить</button>
      </form>
      <p class="cl-count small" aria-live="polite" data-i18n-skip hidden></p>
''' % (opt('', 'Все страны') + ''.join(opt(c, c) for c in order),
       opt('', 'Любой метод') + ''.join(opt(k, 'ТКМ ' + label.lower()) for k, label, _ in TKM) + opt('cart', 'CAR-T'),
       opt('', 'Любой статус') + ''.join(opt(k, v[0]) for k, v in STATUS.items())))
    body = tools + '      <div class="cl-list">\n' + groups + '      </div>\n' + \
        '      <p class="cl-empty" hidden>Ничего не найдено. Измените условия поиска или сбросьте фильтры.</p>\n' + \
        '      <p class="small cl-foot"><span class="said">по данным клиники</span> — сведения с сайта клиники, которые мы ещё не подтвердили независимо.</p>\n'
    for ru, en, kk in STATUS.values(): tr(ru, en, kk)
    for ru, (en, kk) in COUNTRIES.items():
        if ru in order: tr(ru, en, kk)
    return body, extra
