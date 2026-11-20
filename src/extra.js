  // interactive route map: each stop opens its description below the map
  var STEPS = /*__STEPS__*/[];
  var stops = Array.prototype.slice.call(document.querySelectorAll('.rt-stop'));
  var rtBody = document.getElementById('rtBody');
  var rtCur = 0, rtTimer, rtItems = [];
  var reduce = matchMedia('(prefers-reduced-motion: reduce)');
  function esc(x){ return x.replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function paintStep(i){
    var s = STEPS[i];
    document.getElementById('rtNum').textContent = i + 1;
    document.getElementById('rtTitle').textContent = tr(s.t);
    document.getElementById('rtTags').innerHTML = s.p.map(function(p){ return '<span class="place' + (p === 'Услуга HemaBridge' ? ' ours' : '') + '">' + esc(tr(p)) + '</span>'; }).join(' ');
    document.getElementById('rtText').textContent = tr(s.d);
    document.getElementById('rtWho').textContent = s.g ? tr('Вы получаете') + ': ' + tr(s.g) : (s.n ? tr(s.n) : '');
    document.getElementById('rtOf').textContent = '/' + STEPS.length;
    var more = document.getElementById('rtMore');
    more.textContent = tr('Подробнее о шаге');
    more.setAttribute('href', '#stage-' + (i + 1));
  }
  function selectStep(i, focus){
    if(i < 0 || i >= STEPS.length) return;
    rtCur = i;
    stops.forEach(function(g, k){ g.setAttribute('aria-pressed', k === i ? 'true' : 'false'); g.setAttribute('tabindex', k === i ? '0' : '-1'); });
    rtItems.forEach(function(b, k){ b.setAttribute('aria-pressed', k === i ? 'true' : 'false'); });
    document.getElementById('rtPrev').disabled = i === 0;
    document.getElementById('rtNext').disabled = i === STEPS.length - 1;
    if(focus) stops[i].focus({preventScroll: true});
    var sc = stops[i].ownerSVGElement && stops[i].ownerSVGElement.parentNode;
    if(sc && sc.scrollWidth > sc.clientWidth){
      var r = stops[i].getBoundingClientRect(), cr = sc.getBoundingClientRect();
      if(r.left < cr.left + 30 || r.right > cr.right - 30){
        sc.scrollTo({left: sc.scrollLeft + (r.left + r.width / 2) - (cr.left + cr.width / 2), behavior: reduce.matches ? 'auto' : 'smooth'});
      }
    }
    clearTimeout(rtTimer);
    if(reduce.matches){ paintStep(i); return; }
    rtBody.classList.add('swap');
    rtTimer = setTimeout(function(){ paintStep(i); rtBody.classList.remove('swap'); }, 140);
  }
  // phones: the wide map becomes a vertical list of the same route steps
  var rtScroll = document.querySelector('.route-scroll');
  if(stops.length && rtScroll){
    var list = document.createElement('ol');
    list.className = 'rt-list';
    list.setAttribute('aria-label', tr('Шаги маршрута'));
    list.setAttribute('data-i18n-skip', '');
    STEPS.forEach(function(st, k){
      var li = document.createElement('li');
      var abroad = !!st.a;
      li.className = abroad ? 'abroad' : '';
      var b = document.createElement('button');
      b.type = 'button';
      b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i' + st.i + '"/></svg><span class="n">' + (k + 1) + '</span><span class="t">' + esc(tr(st.t)) + '</span>';
      b.addEventListener('click', function(){ selectStep(k); document.getElementById('rtDetail').scrollIntoView({block: 'nearest', behavior: reduce.matches ? 'auto' : 'smooth'}); });
      li.appendChild(b); list.appendChild(li); rtItems.push(b);
    });
    rtScroll.parentNode.insertBefore(list, rtScroll.nextSibling);
  }
  function labelStops(){
    stops.forEach(function(g, k){ g.setAttribute('aria-label', tr('Шаг') + ' ' + (k + 1) + ': ' + tr(STEPS[k].t)); });
  }
  var FORM_MSG = {
    step: 'Заполните обязательные поля на этом шаге. Первое незаполненное поле выделено.',
    all: 'Заполните обязательные поля и подтвердите согласие. Первое незаполненное поле выделено.',
    done: 'Демонстрационный режим: форма заполнена корректно, но данные не отправлены. После запуска здесь появится подтверждение и следующий шаг.'
  };
  // every Russian string used by this script, so the translation tool can list them
  window.__i18nDyn = ['Вы получаете', 'Подробнее о шаге', 'Шаг', 'Шаги маршрута', 'Включить светлую тему', 'Включить тёмную тему', 'версия', 'Шаг 1 из 3', 'Шаг 2 из 3', 'Шаг 3 из 3', FORM_MSG.step, FORM_MSG.all, FORM_MSG.done]
    .concat(window.__hbSlogans || [])
    .concat(STEPS.reduce(function(acc, x){ return acc.concat([x.t, x.d, x.g || '', x.n || ''], x.p); }, []));
  // home headline: keep the rule under «HemaBridge» exactly as wide as the slogan's longest line
  function fitSloganLine(){
    var sl = document.querySelector('.hb-slogan');
    if(!sl || !sl.firstChild) return;
    var r = document.createRange(); r.selectNodeContents(sl);
    var w = 0, rects = r.getClientRects();
    for(var k = 0; k < rects.length; k++) w = Math.max(w, rects[k].width);
    if(w) sl.parentNode.style.setProperty('--hbw', Math.ceil(w) + 'px');
  }
  fitSloganLine();
  window.addEventListener('resize', fitSloganLine);
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(fitSloganLine);
  refreshDynamic = function(){
    fitSloganLine();
    labelStops();
    rtItems.forEach(function(b, k){ var t = b.querySelector('.t'); if(t) t.textContent = tr(STEPS[k].t); });
    var l = document.querySelector('.rt-list'); if(l) l.setAttribute('aria-label', tr('Шаги маршрута'));
    Array.prototype.forEach.call(document.querySelectorAll('form[data-wizard]'), function(f){ if(f._refreshCount) f._refreshCount(); });
    if(stops.length) paintStep(rtCur);
  };
  if(stops.length){
    labelStops();
    stops.forEach(function(g, k){
      g.setAttribute('role', 'button');
      g.addEventListener('click', function(){ selectStep(k); });
      g.addEventListener('keydown', function(e){
        if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); selectStep(k); }
        else if(e.key === 'ArrowRight' || e.key === 'ArrowDown'){ e.preventDefault(); selectStep(Math.min(k + 1, STEPS.length - 1), true); }
        else if(e.key === 'ArrowLeft' || e.key === 'ArrowUp'){ e.preventDefault(); selectStep(Math.max(k - 1, 0), true); }
      });
    });
    document.getElementById('rtPrev').addEventListener('click', function(){ selectStep(rtCur - 1); });
    document.getElementById('rtNext').addEventListener('click', function(){ selectStep(rtCur + 1); });
    selectStep(0);
    paintStep(0); rtBody.classList.remove('swap');
  }

  // multi-step application form
  Array.prototype.slice.call(document.querySelectorAll('form[data-wizard]')).forEach(function(f){
    var steps = Array.prototype.slice.call(f.querySelectorAll('.wz-step'));
    var marks = Array.prototype.slice.call(f.querySelectorAll('.wz-progress li'));
    var prev = f.querySelector('[data-wz-prev]'), next = f.querySelector('[data-wz-next]'), count = f.querySelector('[data-wz-count]');
    var cur = 0;
    f.classList.add('is-wizard');
    f._refreshCount = function(){ count.textContent = tr('Шаг ' + (cur + 1) + ' из ' + steps.length); };
    function go(i, focus){
      cur = i;
      steps.forEach(function(s, k){ s.classList.toggle('active', k === i); });
      marks.forEach(function(m, k){ m.className = k < i ? 'done' : k === i ? 'now' : ''; if(k === i){ m.setAttribute('aria-current','step'); } else { m.removeAttribute('aria-current'); } });
      prev.hidden = i === 0;
      next.hidden = i === steps.length - 1;
      count.textContent = tr('Шаг ' + (i + 1) + ' из ' + steps.length);
      f.classList.remove('was-checked');
      if(focus){
        var top = f.getBoundingClientRect().top + scrollY - 96;
        if(top < scrollY) window.scrollTo({top: top, behavior: reduce.matches ? 'auto' : 'smooth'});
        var first = steps[i].querySelector('input:not([type=radio]),textarea,input:checked');
        if(first) first.focus({preventScroll: true});
      }
    }
    next.addEventListener('click', function(){
      var bad = Array.prototype.slice.call(steps[cur].querySelectorAll('input,textarea')).filter(function(el){ return !el.checkValidity(); })[0];
      var out = f.querySelector('.form-result');
      if(bad){
        f.classList.add('was-checked');
        out.style.borderColor = 'var(--accent)';
        out.textContent = tr(FORM_MSG.step);
        out.classList.add('show');
        bad.focus();
        return;
      }
      out.classList.remove('show');
      go(cur + 1, true);
    });
    prev.addEventListener('click', function(){ f.querySelector('.form-result').classList.remove('show'); go(cur - 1, true); });
    // Enter in a field of an earlier step means "Next", not "submit the whole form"
    f.addEventListener('keydown', function(e){
      if(e.key !== 'Enter' || e.isComposing || cur === steps.length - 1) return;
      if(!e.target || e.target.tagName !== 'INPUT') return;
      e.preventDefault();
      next.click();
    });
    f.addEventListener('submit', function(){
      if(f.checkValidity()){ setTimeout(function(){ go(0); }, 0); return; }
      var bad = f.querySelector(':invalid');
      var host = bad && bad.closest('.wz-step');
      if(host) go(steps.indexOf(host));
      f.classList.add('was-checked');
    });
    go(0);
  });


  // "второе мнение" buttons open the form with that request preselected
  document.addEventListener('click', function(e){
    var r = e.target.closest('[data-req]');
    if(!r) return;
    var radio = document.querySelector('form[data-wizard] input[name="req"][value="' + r.getAttribute('data-req') + '"]');
    if(radio) radio.checked = true;
  });

  // "#stage-N" opens that stage's details on the route page
  function openStageFromHash(){
    var m = /^#stage-(\d)$/.exec(location.hash);
    var el = m && document.getElementById('stage-' + m[1]);
    var d = el && el.querySelector('details');
    if(d){ d.open = true; el.scrollIntoView(); }
  }
  window.addEventListener('hashchange', openStageFromHash);
  openStageFromHash();
  // clinics page: search and filters over the rendered list (without JS the whole list is shown)
  (function(){
    var form = document.querySelector('.cl-tools');
    if(!form) return;
    var items = Array.prototype.slice.call(document.querySelectorAll('details.cl'));
    var groups = Array.prototype.slice.call(document.querySelectorAll('.cl-group'));
    var count = document.querySelector('.cl-count'), empty = document.querySelector('.cl-empty');
    var q = form.querySelector('input[type=search]');
    var sel = {}; Array.prototype.forEach.call(form.querySelectorAll('select[data-f]'), function(s){ sel[s.getAttribute('data-f')] = s; });
    var COUNT = 'Показано {n} из {m}';
    window.__i18nDyn.push(COUNT);
    function apply(){
      var words = (q.value || '').toLowerCase().split(/\s+/).filter(Boolean), n = 0;
      items.forEach(function(d){
        var ok = (!sel.country.value || d.getAttribute('data-country') === sel.country.value)
          && (!sel.status.value || d.getAttribute('data-status') === sel.status.value)
          && (!sel.method.value || (' ' + d.getAttribute('data-m') + ' ').indexOf(' ' + sel.method.value + ' ') >= 0)
          && words.every(function(w){ return d.getAttribute('data-q').indexOf(w) >= 0; });
        d.hidden = !ok; if(ok) n++;
      });
      groups.forEach(function(g){
        var k = g.querySelectorAll('details.cl:not([hidden])').length, c = g.querySelector('.cl-n');
        g.hidden = !k; if(c) c.textContent = k;
      });
      count.textContent = tr(COUNT).replace('{n}', n).replace('{m}', items.length);
      empty.hidden = n > 0;
    }
    form.hidden = false; count.hidden = false;
    form.addEventListener('input', apply);
    form.addEventListener('change', apply);
    form.addEventListener('submit', function(e){ e.preventDefault(); });
    form.addEventListener('reset', function(){ setTimeout(apply, 0); });
    var rd = refreshDynamic; refreshDynamic = function(){ rd(); apply(); };
    function openFromHash(){
      var d = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if(d && d.classList && d.classList.contains('cl')){ d.hidden = false; d.open = true; d.scrollIntoView({block: 'start'}); }
    }
    window.addEventListener('hashchange', openFromHash);
    apply(); openFromHash();
  })();
