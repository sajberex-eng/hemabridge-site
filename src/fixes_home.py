# Impeccable critique fixes for the home page; exec'd by build.py on the assembled page `s`.
import re as _re
# move unfinished "О Центре" placeholder cards to the About page. This creates the «О Центре гематологии» section there;
# content_update.py (step 9) later replaces the cards inside it with facts from hemcenter.kz, so only the section survives.
a=s.index('      <div class="cols-3" style="margin-top:34px">\n        <div class="tpl">\n          <h3>Профиль и статус</h3>')
b=s.index('      <div class="note"><p>Благодаря собственной лаборатории',a)
tpl=s[a:b]; s=s[:a]+s[b:]
s=rep(s,'</section>\n</div>\n\n<!-- ================= СТОИМОСТЬ','</section>\n  <section class="section">\n    <div class="wrap">\n      <h2>О Центре гематологии</h2>\n'+tpl.replace(' style="margin-top:34px"','')+'    </div>\n  </section>\n</div>\n\n<!-- ================= СТОИМОСТЬ')
# programme phone / WhatsApp: single source in contacts.json (also used by content_update.py)
import json as _json0
_PC = _json0.load(open(B + 'contacts.json', encoding='utf-8'))['patients']
PHONE = _PC['phone']
PHONE_TEL = 'tel:+' + ''.join(c for c in PHONE if c.isdigit())
PHONE_WA = 'https://wa.me/' + ''.join(c for c in (_PC.get('whatsapp') or PHONE) if c.isdigit())
ICON_PHONE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>'
ICON_CHAT = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 11.5a8.5 8.5 0 0 1-12.4 7.6L3.5 20.5l1.4-4.4A8.5 8.5 0 1 1 20.5 11.5z"/></svg>'
# closing band with a phone instead of ending on placeholders
old_end='      <div class="actions"><a class="btn btn-ghost" href="https://hemcenter.kz" rel="noopener">Сайт Центра гематологии</a></div>\n    </div>\n  </section>\n'
closing='''
  <section class="section closing">
    <div class="wrap closing-row">
      <div>
        <h2>Остались вопросы?</h2>
        <p class="lead">Позвоните или напишите в WhatsApp координатору программы — подскажем, с чего начать и какие документы собрать.</p>
      </div>
      <div class="actions">
        <a class="btn btn-primary" href="%s">%s<span class="num">%s</span></a>
        <a class="btn btn-ghost" href="%s" target="_blank" rel="noopener">%sНаписать в WhatsApp</a>
      </div>
    </div>
  </section>
''' % (PHONE_TEL, ICON_PHONE, PHONE, PHONE_WA, ICON_CHAT)
s=rep(s,old_end,old_end+closing)
# kz anchor, card link to it
s=rep(s,'<section class="section kz">','<section class="section kz" id="kz-prep">')
i=s.index('aria-label="Пробирки и отметки о выполненной подготовке"'); j=s.rindex('<a class="card" href="#route">',0,i)
s=s[:j]+'<a class="card" href="#kz-prep">'+s[j+len('<a class="card" href="#route">'):]
# mobile menu: CTA + phone
s=rep(s,'      <div class="lang" role="group" aria-label="Язык сайта">','      <a class="nav-mobile" href="#apply">Получить врачебную оценку</a>\n      <a class="nav-mobile" href="%s">Позвонить: <span class="num">%s</span></a>\n      <div class="lang" role="group" aria-label="Язык сайта">' % (PHONE_TEL, PHONE))
# gloss HLA in body text
k=s.index('<body')
s=s[:k]+s[k:].replace('HLA-типирование','<abbr title="Анализ на тканевую совместимость — нужен для подбора донора">HLA</abbr>-типирование')
# comparison table labels for the stacked phone layout
s=_re.sub(r'(<tr><th scope="row">[^<]*</th>)<td>',r'\1<td data-label="Типичная модель медицинского туризма">',s)
s=s.replace('<td class="us">','<td class="us" data-label="HemaBridge">')
# plain-language wording for patients (approved by the user)
def _who(m):
    return '<p class="who">Кто отвечает: '+m.group(1).replace('врачебное ядро','гематологи программы')+'</p>'
s=_re.sub(r'<p class="who">Ответственный: ([^<]*)</p>',_who,s)
for a_,b_ in [
  ('<li><h3>Досбор диагностики в Казахстане','<li><h3>Дополнительные анализы в Казахстане'),
  ('врач–врач коммуникация и shared care.','врач–врач коммуникация и совместное ведение пациента.'),
  ('контрольные точки мониторинга и shared care с лечащим врачом','контрольные точки мониторинга и совместное ведение с лечащим врачом'),
  ('работает модель shared care — совместного ведения пациента','работает модель совместного ведения пациента'),
  ('<span>Shared care</span>','<span>Совместное ведение</span>'),
  ('<strong>Shared care</strong><p>','<strong>Совместное ведение</strong><p>'),
  ('<dt>Shared care</dt>','<dt>Совместное ведение</dt>'),
  ('<li><strong>Shared care</strong>Совместное ведение после возвращения.</li>','<li><strong>Совместное ведение</strong>После возвращения пациента — вместе с врачами в Казахстане.</li>'),
]:
    assert a_ in s, a_
    s=s.replace(a_,b_)
