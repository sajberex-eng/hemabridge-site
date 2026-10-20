# Impeccable critique fixes for the home page; exec'd by build.py on the assembled page `s`.
import re as _re
# move unfinished "О Центре" placeholder cards to the About page
a=s.index('      <div class="cols-3" style="margin-top:34px">\n        <div class="tpl">\n          <h3>Профиль и статус</h3>')
b=s.index('      <div class="note"><p>Благодаря собственной лаборатории',a)
tpl=s[a:b]; s=s[:a]+s[b:]
s=rep(s,'</section>\n</div>\n\n<!-- ================= СТОИМОСТЬ','</section>\n  <section class="section">\n    <div class="wrap">\n      <h2>О Центре гематологии</h2>\n'+tpl.replace(' style="margin-top:34px"','')+'    </div>\n  </section>\n</div>\n\n<!-- ================= СТОИМОСТЬ')
# closing band with a phone instead of ending on placeholders
old_end='      <div class="actions"><a class="btn btn-ghost" href="https://hemcenter.kz" rel="noopener">Сайт Центра гематологии</a></div>\n    </div>\n  </section>\n'
closing='''
  <section class="section closing">
    <div class="wrap closing-row">
      <div>
        <h2>Остались вопросы?</h2>
        <p class="lead">Позвоните координатору программы — подскажем, с чего начать и какие документы собрать.</p>
      </div>
      <div class="actions">
        <a class="btn btn-primary" href="tel:+77770793165"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg><span class="num">+7 777 079 3165</span></a>
        <a class="btn btn-ghost" href="#apply">Получить врачебную оценку</a>
      </div>
    </div>
  </section>
'''
s=rep(s,old_end,old_end+closing)
# kz anchor, card link to it
s=rep(s,'<section class="section kz">','<section class="section kz" id="kz-prep">')
i=s.index('aria-label="Пробирки и отметки о выполненной подготовке"'); j=s.rindex('<a class="card" href="#route">',0,i)
s=s[:j]+'<a class="card" href="#kz-prep">'+s[j+len('<a class="card" href="#route">'):]
# mobile menu: CTA + phone
s=rep(s,'      <div class="lang" role="group" aria-label="Язык сайта">','      <a class="nav-mobile" href="#apply">Получить врачебную оценку</a>\n      <a class="nav-mobile" href="tel:+77770793165">Позвонить: <span class="num">+7 777 079 3165</span></a>\n      <div class="lang" role="group" aria-label="Язык сайта">')
# gloss HLA in body text
k=s.index('<body')
s=s[:k]+s[k:].replace('HLA-типирование','<abbr title="Анализ на тканевую совместимость — нужен для подбора донора">HLA</abbr>-типирование')
# comparison table labels for the stacked phone layout
s=_re.sub(r'(<tr><th scope="row">[^<]*</th>)<td>',r'\1<td data-label="Типичная модель медицинского туризма">',s)
s=s.replace('<td class="us">','<td class="us" data-label="HemaBridge">')
