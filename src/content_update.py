# Content update of November 2026; exec'd by build.py on the assembled page `s` (after fixes_home.py, before i18n_patch.py).
# Data lives next to this file: route.json (nine stages), contacts.json (phones/e-mails, empty = "будет добавлен"),
# clinics.json (centre cards with sources). Shares `rep`, `B` with build.py.
import json as _json, html as _html, os as _os

def _e(x): return _html.escape(x, quote=True)
_R = _json.load(open(B + 'route.json', encoding='utf-8'))
_C = _json.load(open(B + 'contacts.json', encoding='utf-8'))
_T = _R['service']

# ---------- 1. Route page: five steps ----------
def _ul(items): return '<ul class="plain">' + ''.join('<li>%s</li>' % _e(i) for i in items) + '</ul>'
def _tags(st): return ''.join('<span class="place%s">%s</span>' % (' ours' if t == 'Услуга HemaBridge' else '', _e(t)) for t in st['tags'])
_cards = ''
for _i, _st in enumerate(_R['stages'], 1):
    _body = '<p>%s</p>' % _e(_st['text'])
    if _st.get('gets'): _body += '\n          <p class="gets"><strong>Вы получаете:</strong> %s</p>' % _e(_st['gets'])
    if _st.get('note'): _body += '\n          <p class="gets">%s</p>' % _e(_st['note'])
    if _st.get('link'): _body += '\n          <p class="rt-more"><a href="%s">%s</a></p>' % (_e(_st['link'][0]), _e(_st['link'][1]))
    if _st.get('happens'):
        _meta = '<dt>Где</dt><dd>%s</dd><dt>Оплата</dt><dd>%s</dd>' % (_e(_st['where']), _e(_st['pay']))
        if _st.get('term'): _meta += '<dt>Срок</dt><dd>%s</dd>' % _e(_st['term'])
        _meta += '<dt>Кто отвечает</dt><dd>%s</dd>' % _e(_st['who'])
        _body += """
          <details>
            <summary>Подробнее</summary>
            <dl class="stage-meta">%s</dl>
            <div class="stage-cols">
              <div><h4>Что происходит</h4>%s</div>
              <div><h4>Что делаете вы</h4>%s</div>
              <div><h4>Что делаем мы</h4>%s</div>
              <div><h4>Что вы получаете</h4>%s</div>
            </div>
          </details>""" % (_meta, _ul(_st['happens']), _ul(_st['you']), _ul(_st['we']), _ul(_st['get']))
    _cards += """        <li class="stage%s" id="stage-%d">
          <h3>%s</h3>
          <p class="rt-tags">%s</p>
          %s
        </li>
""" % ('' if _st['ours'] else ' ext', _i, _e(_st['title']), _tags(_st), _body)

_route = """  <section class="section">
    <div class="wrap">
      <div class="split">
        <div>
          <h2>Шесть шагов</h2>
          <p>Маршрут может завершиться на любом шаге. Если консилиумы покажут, что лечение возможно в Казахстане, поездка не нужна.</p>
          <a class="btn btn-primary" href="#apply">Оставить заявку</a>
        </div>
        <div>
          <p>Услуги программы — это консультация врача, международные консилиумы с отчётом и наблюдение после возвращения. Платная часть начинается только после того, как вы приняли договор-оферту.</p>
          <p>Договор на лечение вы заключаете напрямую с зарубежной клиникой. Лечение, его оплата и организация поездки — зона ответственности клиники.</p>
          <div class="note"><p><strong>Консилиумы и отбор клиник — %s.</strong> Полное название услуги: «%s». Оплачивается после принятия договора-оферты. Консультация до этого бесплатна.</p></div>
        </div>
      </div>
      <ol class="stages">
%s      </ol>
    </div>
  </section>
""" % (_e(_T['price']), _e(_T['name']), _cards)
_a = s.index('  <section class="section">\n    <div class="wrap split">\n      <div>\n        <h2>Девять этапов</h2>')
_b = s.rindex('  <section class="section">', 0, s.index('<h2>Психологическое сопровождение</h2>'))
s = s[:_a] + _route + s[_b:]
s = rep(s, '<p class="lead">Каждый этап имеет ответственного. Медицинские решения принимает врачебное ядро, организационные — операционная команда.</p>',
        '<p class="lead">Шесть шагов: от консультации врача до наблюдения дома. Консультация бесплатна, решение о продолжении всегда за вами.</p>')

# ---------- 2. Cost page: programme services ----------
s = rep(s, '<h2>Стоимость сопровождения</h2><p>Условия публикуются после утверждения финансовой модели центром.</p><span class="pending">На утверждении</span>',
        '<h2>Услуги программы</h2><p><strong>Консультация врача — бесплатно.</strong></p><p><strong>Консилиумы и отбор клиник — %s.</strong> Услуга «%s»: поиск клиник, консилиумы, перевод документов при необходимости и отчёт.</p><p><strong>Диспансерное наблюдение после возвращения</strong> — стоимость рассчитывается.</p><p><a href="#route">Что входит в каждый шаг</a></p>' % (_e(_T['price']), _e(_T['name'])))

# ---------- 3. Contacts: separate slots for patients and partners ----------
def _tel(v): return '<a href="tel:%s">%s</a>' % (_e(''.join(c for c in v if c.isdigit() or c == '+')), _e(v))
def _mail(v): return '<a href="mailto:%s">%s</a>' % (_e(v), _e(v))
def _wa(v): return '<a href="https://wa.me/%s" rel="noopener">%s</a>' % (_e(''.join(c for c in v if c.isdigit())), _e(v))
def _slot(label, v, fmt, empty):
    return '<li>%s: %s</li>' % (label, fmt(v) if v else '<span class="tbd">%s</span>' % empty)
def _contact_items(k):
    c = _C[k]
    out = _slot('Телефон', c.get('phone'), _tel, 'будет добавлен')
    if 'whatsapp' in c: out += _slot('WhatsApp', c.get('whatsapp'), _wa, 'будет добавлен')
    out += _slot('E-mail', c.get('email'), _mail, 'будет добавлен')
    return out

_old_contacts = s[s.index('        <h4>Контакты</h4>\n        <ul>'):s.index('        </ul>\n      </div>\n    </div>\n    <div class="foot-legal">')]
s = s.replace(_old_contacts, '''        <h4>Контакты для пациентов</h4>
        <ul>%s</ul>
        <h4 class="foot-h">Контакты для партнёров</h4>
        <ul>%s</ul>
        <h4 class="foot-h">Центр гематологии</h4>
        <ul>
          <li>Телефон: <a href="tel:+77770793165">+7 777 079 3165</a></li>
          <li>E-mail: <a href="mailto:info@hemcenter.kz">info@hemcenter.kz</a></li>
          <li>Сайт центра: <a href="https://hemcenter.kz" rel="noopener">hemcenter.kz</a></li>
          <li>Астана, ул. Кенесары, 4Б</li>
''' % (_contact_items('patients'), _contact_items('partners')))

# ---------- 4. Partners page: questionnaire download + partner contacts ----------
_q = '''  <section class="section" id="questionnaire">
    <div class="wrap split">
      <div>
        <h2>Опросник для клиник</h2>
        <p class="lead">С опросника начинается отбор центра. По нему наши врачи сравнивают клиники по одним и тем же критериям.</p>
        <div class="actions q-files" data-i18n-skip>
          <a class="btn btn-primary" href="docs/hemabridge-partner-questionnaire-ru.xlsx" download lang="ru">Скачать на русском (.xlsx)</a>
          <a class="btn btn-ghost" href="docs/hemabridge-partner-questionnaire-kk.xlsx" download lang="kk">Қазақ тілінде жүктеу (.xlsx)</a>
          <a class="btn btn-ghost" href="docs/hemabridge-partner-questionnaire-en.xlsx" download lang="en">Download in English (.xlsx)</a>
        </div>
        <p class="small">Файл Excel на русском, казахском и английском языках: 97 вопросов на четырёх закладках.</p>
      </div>
      <div>
        <ul class="rule-list">
          <li><strong>1. Медицинская информация</strong>Опыт программы, нозологии, трансплантация, поиск донора, результаты лечения, клеточная терапия, диагностика, инфраструктура — 58 вопросов.</li>
          <li><strong>2. Организационные вопросы</strong>Общие сведения, совместное ведение, логистика, юридические вопросы — 24 вопроса.</li>
          <li><strong>3. Финансовая сторона</strong>Пакетные цены, состав пакета, депозит и порядок оплаты — 9 вопросов.</li>
          <li><strong>4. Данные клиники</strong>Сильные стороны, преимущества для пациентов и ограничения — 6 вопросов.</li>
        </ul>
        <div class="note"><p><strong>Как заполнить и отправить.</strong> Ответы вносятся в столбец «Ответ клиники», рядом укажите источник и дату. Вопросы с приоритетом «Критично» обязательны: без ответа на них мы не можем рекомендовать центр пациентам. Заполненный файл отправьте на почту для партнёров.</p></div>
      </div>
    </div>
  </section>
  <section class="section" id="partner-contacts">
    <div class="wrap split">
      <div><h2>Контакты для партнёров</h2><p class="lead">Для вопросов о сотрудничестве и отправки заполненного опросника.</p></div>
      <ul class="rule-list contact-list">%s</ul>
    </div>
  </section>
''' % _contact_items('partners')
_p = s.index('<div class="page" data-page="partners"')
_pe = s.index('<!-- ================= О ПРОЕКТЕ', _p)
_blk = s[_p:_pe]
_cut = _blk.rindex('</div>')
_blk = _blk[:_cut] + _q + _blk[_cut:]
_blk = _blk.replace('<a class="btn btn-primary" href="#contacts-block" data-scroll>Стать партнёром</a>', '<a class="btn btn-primary" href="#questionnaire" data-scroll>Скачать опросник</a><a class="btn btn-ghost" href="#partner-contacts" data-scroll>Контакты для партнёров</a>')
assert 'Скачать опросник</a>' in _blk
s = s[:_p] + _blk + s[_pe:]

# ---------- 5. Legal page: the public offer ----------
s = rep(s, '<li><strong>Договор с пациентом (оферта)</strong><span class="pending">На юридической экспертизе</span></li>',
        '<li id="offer"><strong>Публичный договор-оферта</strong>Платная часть программы начинается после того, как вы приняли оферту. С офертой вы знакомитесь после консультации врача, до любой оплаты.<br><a href="docs/hemabridge-offer-appendix-1-ru.pdf" target="_blank" rel="noopener">Приложение № 1. Согласие пациента и Доверенные лица (PDF, проект)</a><br><span class="pending">Основной текст оферты готовится к публикации</span></li>')

# ---------- 6. Clinics page: candidate centres with sources ----------
_K = _json.load(open(B + 'clinics.json', encoding='utf-8'))
_cl = ''
for _c in _K['clinics']:
    _rows = ''.join('<dt>%s</dt><dd class="v">%s</dd>' % (_e(k), _e(v)) for k, v in _c['rows'])
    _src = ', '.join('<a href="%s" rel="noopener">%s</a>' % (_e(u), _e(n)) for n, u in _c['sources'])
    _cl += '''        <article class="tpl">
          <div class="tpl-head"><div><h3>%s</h3><span class="pending">%s</span></div></div>
          <dl class="fields">%s</dl>
          <div class="chips">%s</div>
          <p class="small src">Источники: %s</p>
        </article>
''' % (_e(_c['name']), _e(_c['status']), _rows, ''.join('<span class="chip">%s</span>' % _e(x) for x in _c['chips']), _src)
_a = s.index('<div class="tpl-grid" style="margin-top:24px">', s.index('<div class="page" data-page="clinics"'))
_b = s.index('<div class="note"', _a)
s = s[:_a] + '<div class="tpl-grid clinics-grid">\n' + _cl + '      </div>\n      ' + s[_b:]
s = rep(s, '<p class="small">Эти центры сейчас проходят проверку по матрице отбора. Мы публикуем только те сведения, которые подтверждены первоисточником, — остальные поля заполняются по мере проверки.</p>',
        '<p class="lead">Эти центры сейчас проходят проверку по матрице отбора. Партнёрами они станут только после подписания меморандума.</p><p class="small">Сведения взяты с официальных сайтов клиник и государственных порталов, актуальны на %s. Пометка «по данным клиники» означает, что мы ещё не получили независимого подтверждения. Клинику под ваш случай подбирают врачи на этапе консилиумов.</p>' % _e(_K['checked']))

# ---------- 7. Clinics page shows the centres first; the selection matrix moves to the partners page ----------
_cp = s.index('<div class="page" data-page="clinics"')
_ma = s.index('  <section class="section">\n    <div class="wrap">\n      <h2>Как мы отбираем центры</h2>', _cp)
_mb = s.index('  <section class="section">', _ma + 10)
_matrix = s[_ma:_mb].replace('<section class="section">', '<section class="section" id="selection">', 1)
s = s[:_ma] + s[_mb:]
s = rep(s, '  <section class="section" id="questionnaire">', _matrix + '  <section class="section" id="questionnaire">')
s = rep(s, '<a href="#clinics">Как мы отбираем центры</a>', '<a href="#selection">Как мы отбираем центры</a>')

# ---------- 8. State route: links to the official rules ----------
s = rep(s, '<div class="note"><p>Мы не обещаем квоту или государственное финансирование. Решение о направлении принимают уполномоченные государственные органы.</p></div>',
        '<div class="note"><p>Мы не обещаем квоту или государственное финансирование. Решение о направлении принимают уполномоченные государственные органы.</p></div>\n        <h3 class="gov-h">Официальные правила</h3>\n        <ul class="plain gov-links">\n          <li><a href="https://egov.kz/cms/ru/articles/health_care/2Fkvota" target="_blank" rel="noopener">Квоты на лечение в Казахстане и за рубежом</a> — портал электронного правительства eGov.kz</li>\n          <li><a href="https://adilet.zan.kz/rus/docs/V2100022866" target="_blank" rel="noopener">Правила направления граждан на лечение за рубеж</a> — приказ Министра здравоохранения от 26 мая 2021 года № ҚР ДСМ-45, актуальная редакция на «Әділет»</li>\n        </ul>')

# ---------- 9. About the Hematology Center: facts from the official site hemcenter.kz (read 18.11.2026) ----------
_a = s.index('<div class="cols-3">\n        <div class="tpl">\n          <h3>Профиль и статус</h3>')
_b = s.index('    </div>\n  </section>\n</div>\n\n<!-- ================= СТОИМОСТЬ', _a)
s = s[:_a] + '''<p class="lead">Первая в Республике Казахстан негосударственная гематологическая клиника. Принимает пациентов с заболеваниями крови в круглосуточном и дневном стационаре.</p>
      <div class="cols-3 hc-cards">
        <div class="tpl">
          <h3>Три филиала</h3>
          <dl class="fields">
            <dt>Астана</dt><dd class="v">ул. Кенесары, 4Б<br><a href="tel:+77719000864">+7 771 900 08 64</a></dd>
            <dt>Караганда</dt><dd class="v">пр. С. Сейфуллина, 17, 2 этаж<br><a href="tel:+77470955650">+7 747 095 5650</a></dd>
            <dt>Усть-Каменогорск</dt><dd class="v">ул. Серикбаева, здание 5, корпус 1, 2 этаж<br><a href="tel:+77470955650">+7 747 095 5650</a></dd>
          </dl>
        </div>
        <div class="tpl">
          <h3>Стационар и реанимация</h3>
          <p class="small">Койки круглосуточного и дневного стационара, кабинеты амбулаторного приёма. Реанимация расположена в отдельном блоке с изоляцией и системой ламинарного «чистого» воздуха.</p>
          <p class="small">Химиопрепараты готовят в кабинете централизованного разведения с ламинарным потоком воздуха.</p>
        </div>
        <div class="tpl">
          <h3>Диагностика</h3>
          <p class="small">Иммунофенотипирование, цитогенетика, молекулярная генетика, FISH, гистологические и иммуногистохимические исследования.</p>
          <p class="small">Диагностический этап для пациентов бесплатен: он оказывается в рамках гарантированного объёма бесплатной медицинской помощи.</p>
        </div>
      </div>
      <p>Основатели центра — гематологи, которые стояли у истоков программы трансплантации костного мозга в Казахстане. Руководитель центра — основатель и председатель правления Республиканской ассоциации врачей-гематологов.</p>
      <p class="small">Источник: официальный сайт <a href="https://hemcenter.kz/ru" data-hc target="_blank" rel="noopener">hemcenter.kz</a>, ноябрь 2026. Служба поддержки пациентов: <a href="tel:+77770793165">+7 777 079 3165</a>.</p>
''' + s[_b:]
s = rep(s, '<p class="lead">Программу ведёт профильная клиника, которая каждый день занимается диагностикой и лечением заболеваний крови. Маршрутизация — продолжение этой работы, а не отдельная посредническая услуга.</p>',
        '<div><p class="lead">Программу ведёт профильная клиника, которая каждый день занимается диагностикой и лечением заболеваний крови. Маршрутизация — продолжение этой работы, а не отдельная посредническая услуга.</p><p>Первая в Казахстане негосударственная гематологическая клиника. Три филиала: Астана, Караганда и Усть-Каменогорск. <a href="#about">Подробнее о центре</a></p></div>')

# ---------- 10. The financial-relations disclosure block is removed, with the two pointers to it ----------
import re as _re2
s, _n = _re2.subn(r'\s*<div class="note"><p><strong>Раскрытие финансовых отношений\.</strong>.*?</p></div>', '', s, flags=_re2.S); assert _n == 1
s, _n = _re2.subn(r'\s*<div class="note"><p><strong>Финансовые отношения с партнёрами\.</strong>.*?</p></div>', '', s, flags=_re2.S); assert _n == 1
s = rep(s, ' Характер финансовых отношений с партнёрами раскрывается в разделе «Стоимость».', '')
s, _n = _re2.subn(r'\s*<li>Раскрываем характер финансовых отношений с партнёрами</li>', '', s); assert _n == 1
s, _n = _re2.subn(r'\s*<li><strong>Раскрытие финансовых отношений с партнёрами</strong><span class="pending">На юридической экспертизе</span></li>', '', s); assert _n == 1
