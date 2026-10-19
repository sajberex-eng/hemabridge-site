import re, sys
import os
B=os.path.dirname(os.path.abspath(__file__))+'/'
src=open(B+'original.html',encoding='utf-8').read()
def rep(s, old, new, count=1):
    n=s.count(old)
    if n!=count: sys.exit(f'expected {count} got {n}: {old[:80]!r}')
    return s.replace(old,new)


def head_art(s, page, src, w, h, alt, wide=False):
    a = s.index('<div class="page" data-page="%s"' % page)
    a = s.index('<section class="page-head glow">\n    <div class="wrap">\n', a)
    start = a + len('<section class="page-head glow">\n')
    end = s.index('\n    </div>\n  </section>', start)
    inner = s[start+len('    <div class="wrap">\n'):end]
    cls = 'wrap head-grid wide' if wide else 'wrap head-grid'
    new = '    <div class="%s">\n      <div>\n%s\n      </div>\n      <img class="illus" src="img/%s" width="%d" height="%d" loading="lazy" decoding="async" alt="%s">' % (cls, inner, src, w, h, alt)
    return s[:start] + new + s[end:]
s=src
s=rep(s,'family=Golos+Text:wght@400;500;600;700&display=swap','family=Golos+Text:wght@400;500;600;700&family=Ysabeau:wght@500;600;700&display=swap')
s=rep(s,'<meta name="theme-color" content="#2C3850">','<meta name="theme-color" content="#FBF7F0" media="(prefers-color-scheme: light)">\n<meta name="theme-color" content="#141A17" media="(prefers-color-scheme: dark)">')
# css
a=s.index('<style>')+len('<style>'); b=s.index('</style>')
s=s[:a]+'\n'+open(B+'style.css',encoding='utf-8').read()+s[b:]
# hero + route
a=s.index('  <section class="hero">'); b=s.index('</figure>\n    </div>\n  </section>\n')+len('</figure>\n    </div>\n  </section>\n')
s=s[:a]+open(B+'hero.html',encoding='utf-8').read()+s[b:]
# services
s=rep(s,'''      <h2>Чем мы помогаем</h2>
      <p class="lead" style="margin-bottom:34px">С чем к нам обращаются чаще всего. Всё начинается с оценки врача-гематолога.</p>''','''      <div class="section-intro">
        <h2>Чем мы помогаем</h2>
        <p class="lead">С чем к нам обращаются чаще всего. Всё начинается с оценки врача-гематолога.</p>
      </div>''')
s=rep(s,'<a class="card" href="#apply">','<a class="card feature" href="#apply">')
s,n=re.subn(r'<svg class="pic" (viewBox="0 0 160 90" role="img" aria-label="[^"]*")>(\s*<rect width="160" height="90" fill="(var\(--tile-\d\))"/>)', r'<svg class="pic" \1 style="background:\3">\2', s)
assert n==6, n
old='''<a class="card" href="#route">
          <svg class="pic" viewBox="0 0 160 90" role="img" aria-label="Календарь'''
assert s.count(old)==1
s=s.replace(old,old.replace('class="card"','class="card wide"'))
# trio + stories
s=rep(s,'''<section class="section">
    <div class="wrap cols-3">
      <div>
        <h2>Партнёрские центры</h2>''','''<section class="section">
    <div class="wrap cols-3 trio">
      <div>
        <h2>Партнёрские центры</h2>''')
s=rep(s,'''        <p class="small">Раздел готовится к публикации.</p>''','''        <div class="story" aria-label="Как будет устроена история пациента">
          <ol>
            <li><i>1</i><span><b>Исходная ситуация</b>Диагноз и вопрос, с которым пришла семья</span></li>
            <li><i>2</i><span><b>Решение врачей</b>Что сделали дома и нужна ли была поездка</span></li>
            <li><i>3</i><span><b>Возвращение домой</b>Как идёт наблюдение после лечения</span></li>
          </ol>
          <p class="small">Первые истории готовятся к публикации — только с согласия пациентов.</p>
        </div>''')
# glows
s=rep(s,'''<section class="section final">
    <div class="wrap">
      <h2>Начните с врачебной оценки — она ни к чему не обязывает</h2>
      <p class="lead">Отправьте документы — врач-гематолог оценит ситуацию и объяснит, какой маршрут подходит именно вам.</p>
      <div class="actions">
        <a class="btn btn-primary" href="#apply">Получить врачебную оценку</a>
        <a class="btn btn-ghost" href="#apply">Получить второе мнение</a>
        <a class="btn btn-ghost" href="#partners">Стать партнёром</a>
      </div>
    </div>''','''<section class="section final bridge">
    <div class="wrap final-grid">
      <div>
        <h2>Начните с врачебной оценки — она ни к чему не обязывает</h2>
        <p class="lead">Отправьте документы — врач-гематолог оценит ситуацию и объяснит, какой маршрут подходит именно вам.</p>
        <div class="actions">
          <a class="btn btn-primary" href="#apply">Получить врачебную оценку</a>
          <a class="btn btn-ghost" href="#apply">Получить второе мнение</a>
          <a class="btn btn-ghost" href="#partners">Стать партнёром</a>
        </div>
      </div>
      <img class="illus" src="img/hero-bridge.webp" width="1400" height="934" loading="lazy" decoding="async" alt="Врач-гематолог обсуждает с пациенткой документы на мосту между домом и клиникой">
    </div>''')
s=rep(s,'''<p class="lead">Ответ на этот вопрос даёт врач-гематолог после изучения документов. Мы не продаём поездку — мы помогаем принять клиническое решение.</p>''','''<p class="lead">Ответ на этот вопрос даёт врач-гематолог после изучения документов. Мы не продаём поездку — мы помогаем принять клиническое решение.</p>
        <img class="illus" src="img/consultation.webp" width="900" height="900" loading="lazy" decoding="async" alt="Врач-гематолог спокойно обсуждает с пациенткой результаты обследования">''')
s=rep(s,'''<div>
        <h2>Профессиональный канал связи</h2>''','''<div>
        <img class="illus" style="margin:0 0 24px" src="img/doctor-to-doctor.webp" width="900" height="900" loading="lazy" decoding="async" alt="Врач из Казахстана на видеосвязи с зарубежным коллегой обсуждает случай пациента">
        <h2>Профессиональный канал связи</h2>''')
s=rep(s,'''<div><h2>Что получает центр</h2><div class="actions"><a class="btn btn-primary" href="#contacts-block" data-scroll>Стать партнёром</a></div></div>''','''<div><h2>Что получает центр</h2><div class="actions"><a class="btn btn-primary" href="#contacts-block" data-scroll>Стать партнёром</a></div><img class="illus" src="img/doctor-to-doctor.webp" width="900" height="900" loading="lazy" decoding="async" alt="Врач-гематолог на видеосвязи с врачом партнёрской клиники"></div>''')
s=rep(s,'''    <div class="wrap">
      <div class="crumb"><a href="#home">Главная</a> / Технологии</div>
      <h1>Технологии и виды помощи</h1>
      <p class="lead">У каждого направления свой маршрут. Везде он начинается с оценки врача и заканчивается наблюдением дома.</p>
      <span class="updated">Дата актуализации: сентябрь 2026</span>
    </div>''','''    <div class="wrap head-grid">
      <div>
        <div class="crumb"><a href="#home">Главная</a> / Технологии</div>
        <h1>Технологии и виды помощи</h1>
        <p class="lead">У каждого направления свой маршрут. Везде он начинается с оценки врача и заканчивается наблюдением дома.</p>
        <span class="updated">Дата актуализации: сентябрь 2026</span>
      </div>
      <img class="illus" src="img/cells-hands.webp" width="900" height="900" loading="lazy" decoding="async" alt="Ладони бережно держат клетки крови и медицинскую папку">
    </div>''')
s=s.replace('<section class="page-head">','<section class="page-head glow">')
# headings order
s=re.sub(r'(<article class="disease">\s*<div>)<h3>(.*?)</h3>',r'\1<h2>\2</h2>',s)
s=re.sub(r'(<p class="who">[^<]*</p>)<h3>(.*?)</h3>',r'\1<h2>\2</h2>',s)
s=s.replace('<div class="task"><h4>Чем мы можем помочь</h4>','<div class="task"><h3>Чем мы можем помочь</h3>')
# doctors
person='<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="17" r="8"/><path d="M8 42c1.5-9 8-13.5 16-13.5S38.5 33 40 42"/><path d="M19 29.5l5 6 5-6"/></svg>'
def doc(m):
    dl, chips = m.group(1), m.group(2)
    return ('<article class="tpl doc">\n          <div class="portrait">'+person+'<span>Фото появится с профилем</span></div>\n'
            '          <div class="doc-body">\n            <h3>ФИО врача</h3><span class="pending">Профиль готовится</span>\n'
            '            <blockquote style="margin-top:16px">Цитата врача появится вместе с профилем</blockquote>\n'
            '            '+dl+'\n            '+chips+'\n          </div>\n        </article>')
s,n=re.subn(r'<article class="tpl">\s*<div class="tpl-head"><div class="avatar">фото</div><div><h3>ФИО врача</h3><span class="pending">Профиль готовится</span></div></div>\s*(<dl class="fields">.*?</dl>)\s*(<div class="chips">.*?</div>)\s*</article>',doc,s,flags=re.S)
assert n==3,n
# apply wizard
a=s.index('      <form class="form" data-demo novalidate>\n        <span class="demo-flag">Демонстрационная форма — данные никуда не отправляются</span>\n        <fieldset>\n          <legend>Что вам нужно</legend>')
b=s.index('</form>',a)+len('</form>')
s=s[:a]+open(B+'wizard.html',encoding='utf-8').read().rstrip('\n')+s[b:]
s=head_art(s,'route','route-panorama.webp',1400,934,'Маршрут пациента: от дома в Казахстане через мост к партнёрской клинике',wide=True)
s=head_art(s,'diseases','lab-microscope.webp',900,900,'Микроскоп и пробирки в лаборатории центра гематологии')
s=head_art(s,'doctors','coordinator.webp',900,900,'Координатор программы на связи с пациентом')
s=head_art(s,'apply','patient-videocall.webp',900,900,'Пациентка дома на видеосвязи с врачом-гематологом')
s=rep(s,"""<h2>Психологическое сопровождение</h2>
        <p class="lead">Лечение за рубежом — нагрузка не только на пациента, но и на семью.</p>""","""<h2>Психологическое сопровождение</h2>
        <p class="lead">Лечение за рубежом — нагрузка не только на пациента, но и на семью.</p>
        <img class="illus" src="img/family-home.webp" width="1200" height="800" loading="lazy" decoding="async" alt="Пациентка с мужем у дома после возвращения с лечения">""")
s=rep(s,"""<p class="lead">Программу ведёт профильная клиника, которая каждый день занимается диагностикой и лечением заболеваний крови. Маршрутизация — продолжение этой работы, а не отдельная посредническая услуга.</p>""","""<div class="head-grid">
        <p class="lead">Программу ведёт профильная клиника, которая каждый день занимается диагностикой и лечением заболеваний крови. Маршрутизация — продолжение этой работы, а не отдельная посредническая услуга.</p>
        <img class="illus" src="img/lab-microscope.webp" width="900" height="900" loading="lazy" decoding="async" alt="Микроскоп и пробирки в собственной лаборатории центра">
      </div>""")
s=rep(s,'<meta name="viewport" content="width=device-width, initial-scale=1">','<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="robots" content="noindex, nofollow">')
s=rep(s,'· © 2026 ТОО «Центр гематологии»</p>','· © 2026 ТОО «Центр гематологии» · версия 2026-10-19.3</p>')
s=rep(s,'<meta name="robots" content="noindex, nofollow">','<meta name="robots" content="noindex, nofollow">\n<meta http-equiv="Cache-Control" content="no-cache">')
# js
s=rep(s,'''  window.addEventListener('hashchange', route);''',open(B+'extra.js',encoding='utf-8').read()+'''  window.addEventListener('hashchange', route);''')
open(B+'../index.html','w',encoding='utf-8').write(s)
print('ok', len(s))
