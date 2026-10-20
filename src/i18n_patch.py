# Language switching: patches the page script; exec'd by build.py on the assembled page `s`.
import re as _re
# 1. the old KZ/EN placeholder pages go away (content is now translated in place)
a=s.index('<!-- ================= KZ / EN заглушки'); b=s.index('</main>')
s=s[:a]+s[b:]
# 2. footer version stamp as its own node
s=_re.sub(r'(© 2026 ТОО «Центр гематологии») · версия ([0-9.\-]+)</p>', r'\1 · <span class="ver" data-v="\2"></span></p>', s)
m=_re.search(r'data-v="([0-9.\-]+)"', s); VER=m.group(1)
# 3. script patches
rt=open(B+'i18n_runtime.js',encoding='utf-8').read().replace('__VERSION__',VER)
old_set="""  function setLang(code){
    langBtns.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.lang === code ? 'true' : 'false'); });
  }
"""
s=rep(s,old_set,rt)
s=rep(s,"    var id = (location.hash || '#home').slice(1);\n","    var id = (location.hash || '#home').slice(1);\n    if(id === 'kz' || id === 'en'){ setLang(id, true); history.replaceState(null, '', '#home'); id = 'home'; }\n")
s=rep(s,"    document.title = target.dataset.title + ' — HemaBridge · Центр гематологии';\n    setLang(pid === 'kz' ? 'kz' : pid === 'en' ? 'en' : 'ru');\n    document.documentElement.lang = pid === 'kz' ? 'kk' : pid === 'en' ? 'en' : 'ru';\n","    curPage = target;\n    setPageTitle();\n")
s=rep(s,"themeBtn.setAttribute('aria-label', t === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему');","themeBtn.setAttribute('aria-label', t === 'dark' ? tr('Включить светлую тему') : tr('Включить тёмную тему'));")
s=rep(s,"out.textContent = 'Заполните обязательные поля и подтвердите согласие. Первое незаполненное поле выделено.';","out.textContent = tr(FORM_MSG.all);")
s=rep(s,"out.textContent = 'Демонстрационный режим: форма заполнена корректно, но данные не отправлены. После запуска здесь появится подтверждение и следующий шаг.';","out.textContent = tr(FORM_MSG.done);")
old_btn=_re.search(r"  langBtns\.forEach\(function\(b\)\{\n    b\.addEventListener\('click', function\(\)\{\n      var code = b\.dataset\.lang;.*?\n    \}\);\n  \}\);\n",s,_re.S)
assert old_btn
s=s.replace(old_btn.group(0),"  langBtns.forEach(function(b){ b.addEventListener('click', function(){ setLang(b.dataset.lang, true); }); });\n")
s=rep(s,"  window.addEventListener('hashchange', route);\n  route();\n","  window.addEventListener('hashchange', route);\n  route();\n  initLang();\n")
# diagram label fitting also when the home page becomes visible / fonts arrive
s=rep(s,"    curPage = target;\n    setPageTitle();\n","    curPage = target;\n    setPageTitle();\n    fitSvgLabels();\n")
s=rep(s,"  initLang();\n","  initLang();\n  if(document.fonts && document.fonts.ready) document.fonts.ready.then(fitSvgLabels);\n")
# 4. dynamic panels are written by the script, not translated in place
s=rep(s,'<div class="rt-body" id="rtBody">','<div class="rt-body" id="rtBody" data-i18n-skip>')
s=s.replace('<div class="form-result" role="status"></div>','<div class="form-result" role="status" data-i18n-skip></div>')

# links to the clinic's own site open it in the language chosen here (/ru, /kk, /en)
s=s.replace('<a class="btn btn-ghost" href="https://hemcenter.kz" rel="noopener">','<a class="btn btn-ghost" href="https://hemcenter.kz/ru" data-hc rel="noopener">')
s=s.replace('<a href="https://hemcenter.kz" rel="noopener">hemcenter.kz</a>','<a href="https://hemcenter.kz/ru" data-hc rel="noopener">hemcenter.kz</a>')
assert s.count('data-hc')>=2
