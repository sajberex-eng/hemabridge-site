# Content update of November 2026; exec'd by build.py on the assembled page `s` (after fixes_home.py, before i18n_patch.py).
# Data lives next to this file: route.json (six route steps), contacts.json (phones/e-mails, empty = "будет добавлен"),
# clinics.json (centre cards with sources). Shares `rep`, `B` with build.py.
import json as _json, html as _html, os as _os

def _e(x): return _html.escape(x, quote=True)
_R = _json.load(open(B + 'route.json', encoding='utf-8'))
_C = _json.load(open(B + 'contacts.json', encoding='utf-8'))
_T = _R['service']

# Clinics page: the centres are candidates until a memorandum is signed, so the title says just «Клиники»
s = rep(s, 'data-page="clinics" data-title="Клиники-партнёры"', 'data-page="clinics" data-title="Клиники"')
s = rep(s, '<h1>Клиники-партнёры</h1>', '<h1>Клиники</h1>')

# ---------- 1. Route page: six steps ----------
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
          <p>Услуги программы — это консультация врача, международные консилиумы с отчётом и персональное ведение после возвращения. Платная часть начинается только после того, как вы приняли договор-оферту.</p>
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
        '<p class="lead">Шесть шагов: от консультации врача до ведения у гематолога дома. Консультация бесплатна, решение о продолжении всегда за вами.</p>')

# ---------- 2. Cost page: programme services ----------
s = rep(s, '<h2>Стоимость сопровождения</h2><p>Условия публикуются после утверждения финансовой модели центром.</p><span class="pending">На утверждении</span>',
        '<h2>Услуги программы</h2><p><strong>Консультация врача — бесплатно.</strong></p><p><strong>Консилиумы и отбор клиник — %s.</strong> Услуга «%s»: поиск клиник, консилиумы, перевод документов при необходимости и отчёт.</p><p><strong>Диспансерное наблюдение после возвращения</strong> — стоимость рассчитывается.</p><p><a href="#route">Что входит в каждый шаг</a></p>' % (_e(_T['price']), _e(_T['name'])))

# ---------- 2a. Cost page: follow-up plans for 1, 3 and 6 months (no prices yet; source: follow-up deck, counts from its month tables) ----------
s = rep(s, '<p><strong>Диспансерное наблюдение после возвращения</strong> — стоимость рассчитывается.</p>',
        '<p><strong>Персональное ведение у гематолога после возвращения</strong> — планы на 1, 3 и 6 месяцев, стоимость уточняется. <a href="#followup">Что входит в планы</a></p>')
_FU = [  # scenario, return day, [(visits, tele, call)] for 1 / 3 / 6 months
    ('CAR-T-терапия', 'Возвращение примерно на 30-й день после инфузии', ['2 очных визита', '4 очных визита · 1 телеконсультация · созвон с клиникой', '6 очных визитов · 2 телеконсультации · созвон с клиникой']),
    ('Аллогенная ТКМ', 'Возвращение примерно на 100-й день после трансплантации', ['2 очных визита', '5 очных визитов · созвон с клиникой', '8 очных визитов · 3 телеконсультации · созвон с клиникой']),
    ('Аутологичная ТКМ', 'Возвращение примерно на 30-й день после трансплантации', ['2 очных визита', '3 очных визита · 1 телеконсультация · созвон с клиникой', '5 очных визитов · 2 телеконсультации · созвон с клиникой']),
]
_FU_COLS = ['1 месяц', '3 месяца', '6 месяцев']
def _fu_cell(txt): return '<br>'.join(_e(x) for x in txt.split(' · '))
_fu_rows = ''.join('<tr><th scope="row">%s<span class="fu-when">%s</span></th>%s</tr>' % (_e(n), _e(w), ''.join('<td data-label="%s">%s</td>' % (_FU_COLS[k], _fu_cell(v)) for k, v in enumerate(cells))) for n, w, cells in _FU)
_followup = """  <section class="section" id="followup">
    <div class="wrap">
      <div class="split">
        <div>
          <h2>Планы ведения после возвращения</h2>
          <p>Персональное ведение у гематолога — отдельная услуга программы. При необходимости к нему подключаются зарубежные специалисты. Есть планы на 1, 3 и 6 месяцев. Врач подбирает план по виду лечения и вашему состоянию.</p>
        </div>
        <div>
          <ol class="plain fu-algo">
            <li><strong>До возвращения.</strong> Получаем от клиники выписку и план наблюдения, переводим их, назначаем вам врача и куратора.</li>
            <li><strong>Первая неделя дома.</strong> Очный визит, базовые анализы и памятка о тревожных признаках.</li>
            <li><strong>Плановое наблюдение.</strong> Визиты и анализы по календарю. Врач смотрит результаты в течение 24–48 часов.</li>
            <li><strong>3-й месяц.</strong> Плановый созвон с клиникой, где вы лечились. Итоги созвона вы получаете на русском языке.</li>
            <li><strong>Конец плана.</strong> Итоговый визит: решаем, что дальше.</li>
          </ol>
        </div>
      </div>
      <div class="table-scroll">
        <table>
          <thead><tr><th scope="col">Вид лечения</th><th scope="col">1 месяц</th><th scope="col">3 месяца</th><th scope="col">6 месяцев</th></tr></thead>
          <tbody>%s</tbody>
        </table>
      </div>
      <div class="note">
        <p><strong>Если что-то тревожит.</strong> Температура 38° и выше, спутанность, одышка, сыпь, диарея или кровотечение — в тот же день вас осмотрит врач или вы будете направлены в стационар. Мы сообщим об этом клинике.</p>
        <p>Если отклонения появились в анализах, назначаем внеплановую консультацию и при необходимости срочно связываемся с клиникой.</p>
        <p>Анализы и ПЭТ-КТ в планы не входят: их оплачивают отдельно или получают по ОСМС. Стоимость планов будет опубликована после утверждения.</p>
      </div>
    </div>
  </section>
""" % _fu_rows
_g = s.index('<div><h2>Государственный маршрут</h2></div>')
_g = s.rindex('  <section class="section">', 0, _g)
s = s[:_g] + _followup + s[_g:]

# ---------- 3. Contacts: separate slots for patients and partners ----------
def _tel(v): return '<a href="tel:%s">%s</a>' % (_e(''.join(c for c in v if c.isdigit() or c == '+')), _e(v))
def _mail(v): return '<a href="mailto:%s">%s</a>' % (_e(v), _e(v))
def _wa(v): return '<a href="https://wa.me/%s" rel="noopener">%s</a>' % (_e(''.join(c for c in v if c.isdigit())), _e(v))
def _slot(label, v, fmt, empty):
    return '<li>%s: %s</li>' % (label, fmt(v) if v else '<span class="tbd">%s</span>' % empty)
def _contact_items(k):
    c = _C[k]
    out = '<li>Координатор проекта: %s</li>' % _e(c['coordinator']) if c.get('coordinator') else ''
    out += _slot('Телефон', c.get('phone'), _tel, 'будет добавлен')
    if 'whatsapp' in c: out += _slot('WhatsApp', c.get('whatsapp'), _wa, 'будет добавлен')
    out += _slot('E-mail', c.get('email'), _mail, 'будет добавлен')
    return out

_old_contacts = s[s.index('        <h4>Контакты</h4>\n        <ul>'):s.index('        </ul>\n      </div>\n    </div>\n    <div class="foot-legal">')]
s = s.replace(_old_contacts, '''        <h4>Контакты для пациентов</h4>
        <ul>%s</ul>
        <h4 class="foot-h">Центр гематологии</h4>
        <ul>
          <li>Телефон: <a href="tel:+77770793165">+7 777 079 3165</a></li>
          <li>E-mail: <a href="mailto:info@hemcenter.kz">info@hemcenter.kz</a></li>
          <li>Сайт центра: <a href="https://hemcenter.kz" rel="noopener">hemcenter.kz</a></li>
          <li>Астана, ул. Кенесары, 4Б</li>
''' % _contact_items('patients'))

# ---------- 4. Partners page: questionnaire download + partner contacts ----------
_q = '''  <section class="section" id="questionnaire">
    <div class="wrap split">
      <div>
        <h2>Опросник для клиник</h2>
        <p class="lead">С опросника начинается отбор центра. По нему наши врачи сравнивают клиники по одним и тем же критериям.</p>
        <div class="actions q-files" data-i18n-skip="keep">
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
        <div class="note"><p><strong>Как заполнить и отправить.</strong> Ответы вносятся в столбец «Ответ клиники», рядом укажите источник и дату. Вопросы с приоритетом «Критично» обязательны: без ответа на них мы не можем рекомендовать центр пациентам. Заполненный файл верните сотруднику программы, от которого вы его получили.</p></div>
      </div>
    </div>
  </section>
'''
_p = s.index('<div class="page" data-page="partners"')
_pe = s.index('<!-- ================= О ПРОЕКТЕ', _p)
_blk = s[_p:_pe]
_cut = _blk.rindex('</div>')
_blk = _blk[:_cut] + _q + _blk[_cut:]
_blk = _blk.replace('<a class="btn btn-primary" href="#contacts-block" data-scroll>Стать партнёром</a>', '<a class="btn btn-primary" href="#questionnaire" data-scroll>Скачать опросник</a>')
assert 'Скачать опросник</a>' in _blk
s = s[:_p] + _blk + s[_pe:]

# ---------- 5. Legal page: the public offer ----------
s = rep(s, '<li><strong>Договор с пациентом (оферта)</strong><span class="pending">На юридической экспертизе</span></li>',
        '<li id="offer"><strong>Публичный договор-оферта</strong>Платная часть программы начинается после того, как вы приняли оферту. С офертой вы знакомитесь после консультации врача, до любой оплаты.<br><a href="docs/hemabridge-offer-appendix-1-ru.pdf" target="_blank" rel="noopener">Приложение № 1. Согласие пациента и Доверенные лица (PDF, проект)</a><br><span class="pending">Основной текст оферты готовится к публикации</span></li>')

# ---------- 6. Clinics page: candidate centres, grouped by country, one accordion card per clinic ----------
# Data: clinics.json (written from the coordinator's table by clinics_sheet.py); schema and markup: clinics_lib.py.
import sys as _sys
_sys.path.insert(0, B)
import clinics_lib as _CL
_K = _json.load(open(B + 'clinics.json', encoding='utf-8'))
_err, _warn = _CL.validate(_K)
for _w in _warn: print('clinics: предупреждение:', _w)
if _err:
    print('clinics.json: ошибки:\n  ' + '\n  '.join(_err)); raise SystemExit(1)
_cl, EXTRA_TR = _CL.render(_K)
_a = s.index('<div class="tpl-grid" style="margin-top:24px">', s.index('<div class="page" data-page="clinics"'))
_b = s.index('<div class="note"', _a)
s = s[:_a] + _cl.lstrip() + '      ' + s[_b:]
s = rep(s, '<p class="small">Эти центры сейчас проходят проверку по матрице отбора. Мы публикуем только те сведения, которые подтверждены первоисточником, — остальные поля заполняются по мере проверки.</p>',
        '<p class="lead">Эти центры сейчас проходят проверку по матрице отбора. Партнёрами они станут только после подписания меморандума.</p><p class="small">Сведения взяты с официальных сайтов клиник и государственных порталов; дата проверки указана в карточке каждой клиники. Клинику под ваш случай подбирают врачи на этапе консилиумов.</p>')
s = rep(s, '<div class="note" style="margin-top:24px"><p><strong>Что означают пометки.</strong> «Проверка по матрице идёт» — центр рассматривается как партнёр, часть сведений подтверждена первоисточником, остальные запрошены. Пока проверка и договор не завершены, мы не называем центр партнёром и не направляем туда пациентов.</p></div>',
        '<div class="note" style="margin-top:24px"><p><strong>Что означают статусы.</strong> «Кандидат · проверка» — центр проверяется по матрице отбора: часть сведений подтверждена первоисточником, остальные запрошены. «Кандидат · переговоры» — идут переговоры о меморандуме. «Партнёр» — меморандум подписан. Пока центр не стал партнёром, мы не направляем туда пациентов от имени программы.</p></div>')

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

# ---------- 11. Contact panels instead of the demo forms ----------
# Online forms may only collect patient data on servers in Kazakhstan (KZ law). Until then the application wizard
# (wizard.html, kept for later: set FORM_ENABLED = True in build.py) and the referral form are replaced by
# phone/WhatsApp panels. PHONE, PHONE_TEL, PHONE_WA and the icons come from fixes_home.py (contacts.json).
def _contact_buttons():
    return ('<div class="actions">\n'
            '          <a class="btn btn-primary" href="%s" target="_blank" rel="noopener">%sНаписать в WhatsApp</a>\n'
            '          <a class="btn btn-ghost" href="%s">%s<span class="num">%s</span></a>\n'
            '        </div>') % (PHONE_WA, ICON_CHAT, PHONE_TEL, ICON_PHONE, PHONE)

if not FORM_ENABLED:
    _a = s.index('      <form class="form" data-demo data-wizard novalidate>')
    _b = s.index('</form>', _a) + len('</form>')
    s = s[:_a] + '''      <div class="contact-panel">
        <h2>Как обратиться сейчас</h2>
        <p class="lead">Напишите в WhatsApp или позвоните координатору программы. Коротко расскажите о ситуации — мы подскажем, какие документы нужны, и договоримся о консультации гематолога.</p>
        %s
        <div class="cols-2 contact-more">
          <div>
            <h3>Что подготовить</h3>
            <ul class="plain">
              <li>Последние выписки и заключения врачей</li>
              <li>Результаты анализов и исследований, в том числе костного мозга, если они есть</li>
              <li>Сведения о проведённом и текущем лечении</li>
            </ul>
          </div>
          <div>
            <h3>Как передать документы</h3>
            <p>Не отправляйте медицинские документы до разговора с координатором: он подскажет, как передать их безопасно.</p>
          </div>
        </div>
        <p class="small">Онлайн-заявка появится после юридической экспертизы и подключения защищённого сервера в Казахстане. Обращение не означает автоматического назначения лечения или подтверждения необходимости лечения за рубежом.</p>
      </div>''' % _contact_buttons() + s[_b:]
    s = rep(s, '<p class="lead">Расскажите о ситуации. Врач-гематолог изучит информацию и свяжется с вами, чтобы обсудить возможный маршрут.</p>',
            '<p class="lead">Напишите или позвоните координатору программы. Врач-гематолог изучит документы и свяжется с вами, чтобы обсудить возможный маршрут.</p>')

    _a = s.index('<section class="section" id="referral-form">')
    _f = s.index('      <form class="form" data-demo novalidate>', _a)
    _b = s.index('</form>', _f) + len('</form>')
    s = s[:_a] + s[_a:_f].replace('<h2>Форма направления</h2>', '<h2>Как направить пациента</h2>') + '''      <div class="contact-panel">
        <p class="lead">Позвоните или напишите в WhatsApp координатору программы. Договоримся о передаче медицинского резюме и согласуем консультацию с гематологом программы.</p>
        %s
        <p class="small">Онлайн-форма направления появится после подключения защищённого сервера в Казахстане. Передавайте персональные данные пациента только с его согласия.</p>
      </div>''' % _contact_buttons() + s[_b:]

# ---------- 12. Diseases and treatment methods: owner's texts of 20.11.2026 (RU/KK/EN in translations.json) ----------
# No "updated / under medical review" badges; each disease group gets the owner's description, the specific
# "Чем мы можем помочь" lists stay. The methods text replaces the four paragraphs on the "tech" page.
def _page(s, pg):
    a = s.index('<div class="page" data-page="%s"' % pg)
    return a, s.index('<div class="page"', a + 20)

_DIS = [  # (h2 as in the page, new h2, owner's text)
    ('Острые лейкозы', None, 'Острый миелоидный и острый лимфобластный лейкоз требуют своевременного лечения. Применяются лекарственная терапия, трансплантация стволовых клеток, а при некоторых формах В-клеточного лейкоза — CAR-T-терапия.'),
    ('Хронические лейкозы', None, 'Хронический миелолейкоз и хронический лимфолейкоз часто удаётся контролировать современными препаратами. Иногда достаточно наблюдения. При неэффективности лечения может потребоваться консультация специализированного центра.'),
    ('Лимфомы', None, 'Лимфомы — опухолевые заболевания лимфатической системы. В зависимости от вида заболевания применяются лекарственная терапия, облучение, трансплантация стволовых клеток и CAR-T-терапия.'),
    ('Множественная миелома', None, 'Заболевание плазматических клеток костного мозга. Лечение включает комбинации современных препаратов, аутологичную трансплантацию, а в отдельных случаях — CAR-T и другие виды иммунотерапии.'),
    ('Миелодиспластические заболевания', None, 'При этих заболеваниях нарушается образование нормальных клеток крови. Лечение зависит от группы риска и может включать поддерживающую терапию, лекарственные препараты или трансплантацию стволовых клеток.'),
    ('Апластическая анемия', None, 'Заболевание, при котором костный мозг вырабатывает недостаточно клеток крови. Основные методы лечения — иммуносупрессивная терапия и трансплантация донорских стволовых клеток.'),
    ('Другие заболевания системы крови', 'Редкие заболевания крови', 'Редкие и сложные заболевания требуют точной диагностики и индивидуального подхода. Мы помогаем получить экспертное мнение и определить возможные варианты лечения.'),
]
_a, _b = _page(s, 'diseases'); _p = s[_a:_b]
_p = rep(_p, '<p class="lead">Коротко о заболевании и о том, в каких ситуациях обсуждается зарубежный этап лечения.</p>\n      <span class="updated">Дата актуализации: сентябрь 2026. Материалы проходят медицинскую редактуру.</span>',
         '<p class="lead">Лечение зависит от точного диагноза и состояния пациента. Не всегда требуется поездка за рубеж — сначала врач оценивает доступные возможности.</p>')
for _h, _nh, _t in _DIS:
    _i = _p.index('<h2>%s</h2>' % _h)
    _j = _p.index('<p>', _i); _k = _p.index('</p>', _j) + 4
    assert _p.index('</article>', _i) > _k
    _p = _p[:_j] + '<p>%s</p>' % _e(_t) + _p[_k:]
    if _nh: _p = rep(_p, '<h2>%s</h2>' % _h, '<h2>%s</h2>' % _nh)
_p = rep(_p, '<p class="small" style="margin-top:28px">Информация носит ознакомительный характер и не заменяет консультацию врача.',
         '''<div class="note cta-note">
        <h2>Нужно ли вам лечение за рубежом?</h2>
        <p>Начните с консультации гематолога. Мы изучим медицинские документы и поможем определить дальнейшие шаги.</p>
        <div class="actions"><a class="btn btn-primary" href="#apply">Получить врачебную оценку</a></div>
      </div>
      <p class="small" style="margin-top:28px">Информация носит справочный характер и не заменяет консультацию врача.''')
s = s[:_a] + _p + s[_b:]

_a, _b = _page(s, 'tech'); _p = s[_a:_b]
_p = rep(_p, '<p class="lead">У каждого направления свой маршрут. Везде он начинается с оценки врача и заканчивается наблюдением дома.</p>\n        <span class="updated">Дата актуализации: сентябрь 2026</span>',
         '<p class="lead">У каждого направления свой маршрут. Везде он начинается с оценки врача и заканчивается ведением у гематолога дома.</p>')
for _id, _nh, _t in [
    ('tkm', None, 'Метод лечения с использованием собственных или донорских кроветворных стволовых клеток. Мы помогаем оценить показания, пройти обследование, подготовиться к трансплантации и организовать последующее наблюдение.'),
    ('cart', None, 'Современный метод, при котором иммунные клетки пациента изменяют для распознавания опухоли. Применяется при отдельных видах лейкозов, лимфом и множественной миеломы.'),
    ('drugs', 'Современная лекарственная терапия', 'Таргетные препараты и иммунотерапия позволяют воздействовать на определённые механизмы заболевания. Выбор лечения зависит от диагноза, ранее проведённой терапии и доступности препаратов.'),
    ('second', None, 'Консультация зарубежного специалиста помогает уточнить диагноз и оценить варианты лечения. Во многих случаях это возможно дистанционно, без поездки пациента.')]:
    _i = _p.index('<div class="flow-block" id="%s">' % _id)
    _j = _p.index('<p>', _i); _k = _p.index('</p>', _j) + 4
    _p = _p[:_j] + '<p>%s</p>' % _e(_t) + _p[_k:]
    if _nh: _p = rep(_p, '<h2>Недоступные препараты</h2>', '<h2>%s</h2>' % _nh)
s = s[:_a] + _p + s[_b:]
