  /* ---------- language switching (RU source text, EN/KK dictionaries loaded on demand) ---------- */
  var VERSION = '__VERSION__';
  var DICTS = {};
  var LANG = 'ru';                         // dictionary key: ru | en | kk
  var BTN2KEY = {ru: 'ru', en: 'en', kz: 'kk'};
  var KEY2HTML = {ru: 'ru', en: 'en', kk: 'kk'};
  var refreshDynamic = null;
  var curPage = null;
  var textOrig = new WeakMap(), attrOrig = new WeakMap();
  var ATTR_SEL = '[alt],[aria-label],[title],[placeholder],[data-label]';
  var ATTR_NAMES = ['alt', 'aria-label', 'title', 'placeholder', 'data-label'];
  function norm(x){ return x.replace(/\s+/g, ' ').trim(); }
  function tr(x){
    if(LANG === 'ru' || !x) return x;
    var d = DICTS[LANG];
    if(!d) return x;
    var k = norm(x);
    return Object.prototype.hasOwnProperty.call(d, k) ? d[k] : x;
  }
  function skipped(el){ return !!(el && el.closest && el.closest('[data-i18n-skip]')); }
  function eachText(cb){
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null), n;
    while((n = w.nextNode())){
      var p = n.parentNode, tag = p && p.nodeName;
      if(!/\S/.test(n.nodeValue) || tag === 'SCRIPT' || tag === 'STYLE' || skipped(p)) continue;
      cb(n);
    }
  }
  function applyDom(){
    eachText(function(n){
      var o = textOrig.get(n);
      if(o === undefined){ o = n.nodeValue; textOrig.set(n, o); }
      var m = /^(\s*)([\s\S]*?)(\s*)$/.exec(o);
      var t = m[1] + tr(m[2]) + m[3];
      if(n.nodeValue !== t) n.nodeValue = t;
    });
    var els = document.querySelectorAll(ATTR_SEL);
    for(var i = 0; i < els.length; i++){
      var el = els[i];
      if(el.classList.contains('rt-stop') || el.classList.contains('theme-btn') || skipped(el) && el.nodeName !== 'svg') continue;
      var store = attrOrig.get(el);
      if(!store){ store = {}; attrOrig.set(el, store); }
      ATTR_NAMES.forEach(function(a){
        if(!el.hasAttribute(a)) return;
        if(store[a] === undefined) store[a] = el.getAttribute(a);
        var v = tr(store[a]);
        if(el.getAttribute(a) !== v) el.setAttribute(a, v);
      });
    }
    var hc = {ru: 'ru', en: 'en', kk: 'kk'}[LANG] || 'ru';
    Array.prototype.forEach.call(document.querySelectorAll('a[data-hc]'), function(a){ a.setAttribute('href', 'https://hemcenter.kz/' + hc); });
    var ver = document.querySelector('.ver');
    if(ver) ver.textContent = tr('версия') + ' ' + ver.getAttribute('data-v');
    [['meta[name="description"]', 'content'], ['meta[property="og:title"]', 'content'], ['meta[property="og:description"]', 'content']].forEach(function(pair){
      var m = document.querySelector(pair[0]);
      if(!m) return;
      if(!m.hasAttribute('data-orig')) m.setAttribute('data-orig', m.getAttribute(pair[1]));
      m.setAttribute(pair[1], tr(m.getAttribute('data-orig')));
    });
  }
  // diagram labels must fit between neighbouring stops: shrink the font a little when a translation is longer
  function fitSvgLabels(){
    var labels = document.querySelectorAll('.rt-stop .lbl');
    for(var i = 0; i < labels.length; i++){
      var l = labels[i];
      l.style.fontSize = '';
      var len = l.getComputedTextLength ? l.getComputedTextLength() : 0;
      if(len > 96) l.style.fontSize = Math.max(9.5, 13.5 * 96 / len).toFixed(2) + 'px';
    }
  }
  function setPageTitle(){
    if(curPage) document.title = tr(curPage.dataset.title) + ' — HemaBridge · ' + tr('Центр гематологии');
  }
  function loadDict(key, cb){
    if(key === 'ru' || DICTS[key]) return cb();
    var s = document.createElement('script');
    s.src = 'i18n/' + key + '.js?v=' + VERSION;
    s.onload = function(){ DICTS[key] = window['__I18N_' + key] || {}; cb(); };
    s.onerror = function(){ cb(); };
    document.head.appendChild(s);
  }
  function setLang(code, persist){
    var key = BTN2KEY[code] || 'ru';
    var btn = key === 'kk' ? 'kz' : key;
    langBtns.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.lang === btn ? 'true' : 'false'); });
    loadDict(key, function(){
      LANG = key;
      document.documentElement.lang = KEY2HTML[key];
      applyDom();
      setPageTitle();
      if(typeof syncThemeBtn === 'function') syncThemeBtn();
      if(refreshDynamic) refreshDynamic();
      fitSvgLabels();
      Array.prototype.forEach.call(document.querySelectorAll('.form-result.show'), function(r){ r.classList.remove('show'); });
    });
    if(persist){ try{ localStorage.setItem('hb-lang', btn); }catch(e){} }
  }
  function initLang(){
    var q = (location.search.match(/[?&]lang=(ru|kz|kk|en)/) || [])[1];
    if(q === 'kk') q = 'kz';
    var saved = null;
    try{ saved = localStorage.getItem('hb-lang'); }catch(e){}
    var want = q || saved || 'ru';
    if(want !== 'ru') setLang(want, !!q); else applyDom();
  }
  // used by the extraction tool: every Russian string the page can show
  window.__i18nKeys = function(){
    var seen = {}, out = [];
    function add(k, ctx){ k = norm(k); if(!/[A-Za-zА-Яа-яЁё]/.test(k) || seen[k]) return; seen[k] = 1; out.push({key: k, ctx: ctx}); }
    eachText(function(n){
      var p = n.parentNode, b = p.closest ? (p.closest('button,a,label,th,td,li,p,h1,h2,h3,h4,dt,dd,summary,figcaption,span,strong,div') || p) : p;
      var kind = p.closest && p.closest('svg') ? 'svg-label' : p.closest && p.closest('.btn') ? 'button' : p.closest && p.closest('.nav,.more-panel,.foot-grid') ? 'nav' : 'text';
      add(n.nodeValue, {kind: kind, para: norm(b.textContent).slice(0, 220)});
    });
    Array.prototype.forEach.call(document.querySelectorAll(ATTR_SEL), function(el){
      ATTR_NAMES.forEach(function(a){ if(el.hasAttribute(a) && !el.classList.contains('rt-stop') && !el.classList.contains('theme-btn')) add(el.getAttribute(a), {kind: 'attr:' + a, para: norm(el.textContent || '').slice(0, 120)}); });
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-title]'), function(el){ add(el.dataset.title, {kind: 'page-title', para: ''}); });
    ['meta[name="description"]', 'meta[property="og:title"]', 'meta[property="og:description"]'].forEach(function(sel){ var m = document.querySelector(sel); if(m) add(m.getAttribute('content'), {kind: 'meta', para: ''}); });
    (window.__i18nDyn || []).forEach(function(k){ add(k, {kind: 'script', para: ''}); });
    add('Центр гематологии', {kind: 'page-title', para: 'suffix of the browser tab title'});
    return out;
  };
