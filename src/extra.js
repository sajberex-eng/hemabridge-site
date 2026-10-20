  // interactive route map: each stop opens its description below the map
  var STEPS = [
    {t:'Обращение и документы', p:['Казахстан'], d:'Вы заполняете форму и прикладываете выписки, заключения, результаты исследований. Координатор проверяет полноту пакета.', w:'координатор документооборота'},
    {t:'Врачебная оценка', p:['Казахстан'], d:'Гематолог изучает случай и формулирует клинический вопрос: что нужно пациенту и где это может быть сделано.', w:'гематологи программы'},
    {t:'Дополнительные анализы в Казахстане', p:['Казахстан'], d:'Недостающие исследования выполняются дома — до поездки, если это клинически оправдано.', w:'гематологи программы, лечащий врач'},
    {t:'Подбор центра', p:[], d:'Центр выбирается по клинической задаче и внутренней матрице отбора, а не по коммерческим условиям.', w:'гематологи программы'},
    {t:'Согласование с зарубежным врачом', p:['Партнёрский центр'], d:'Врач–врач обсуждение структурированного медицинского резюме, план лечения и предварительная смета от центра.', w:'гематологи программы'},
    {t:'Организация поездки', p:[], d:'Документы, приглашение, логистика, перевод, связь с семьёй.', w:'операционный блок'},
    {t:'Лечение', p:['Партнёрский центр'], d:'Мы остаёмся на связи с лечащей командой центра и с пациентом.', w:'партнёрский центр, гематологи программы'},
    {t:'Возвращение и структурированная передача', p:['Казахстан'], d:'Выписка, план наблюдения и рекомендации передаются лечащему врачу в Казахстане в согласованном формате.', w:'гематологи программы'},
    {t:'Долгосрочное наблюдение и обратная связь', p:['Казахстан','Партнёрский центр'], d:'Наблюдение продолжается в Казахстане, а связь с партнёрской клиникой не прерывается: контрольные анализы, повторные консультации и телемедицинские консилиумы.', w:'гематологи программы, лечащий врач, партнёрский центр'}
  ];
  var stops = Array.prototype.slice.call(document.querySelectorAll('.rt-stop'));
  var rtBody = document.getElementById('rtBody');
  var rtCur = 0, rtTimer, rtItems = [];
  var reduce = matchMedia('(prefers-reduced-motion: reduce)');
  function esc(x){ return x.replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function paintStep(i){
    var s = STEPS[i];
    document.getElementById('rtNum').textContent = i + 1;
    document.getElementById('rtTitle').innerHTML = esc(tr(s.t)) + s.p.map(function(p){ return ' <span class="place' + (p === 'Казахстан' ? '' : ' abroad') + '">' + esc(tr(p)) + '</span>'; }).join('');
    document.getElementById('rtText').textContent = tr(s.d);
    document.getElementById('rtWho').textContent = tr('Кто отвечает') + ': ' + tr(s.w);
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
  // phones: the wide map becomes a vertical list of the same nine stops
  var rtScroll = document.querySelector('.route-scroll');
  if(stops.length && rtScroll){
    var list = document.createElement('ol');
    list.className = 'rt-list';
    list.setAttribute('aria-label', tr('Этапы маршрута'));
    list.setAttribute('data-i18n-skip', '');
    STEPS.forEach(function(st, k){
      var li = document.createElement('li');
      var abroad = st.p.length === 1 && st.p[0] !== 'Казахстан';
      li.className = abroad ? 'abroad' : '';
      var b = document.createElement('button');
      b.type = 'button';
      b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i' + (k + 1) + '"/></svg><span class="n">' + (k + 1) + '</span><span class="t">' + esc(tr(st.t)) + '</span>';
      b.addEventListener('click', function(){ selectStep(k); document.getElementById('rtDetail').scrollIntoView({block: 'nearest', behavior: reduce.matches ? 'auto' : 'smooth'}); });
      li.appendChild(b); list.appendChild(li); rtItems.push(b);
    });
    rtScroll.parentNode.insertBefore(list, rtScroll.nextSibling);
  }
  function labelStops(){
    stops.forEach(function(g, k){ g.setAttribute('aria-label', tr('Этап') + ' ' + (k + 1) + ': ' + tr(STEPS[k].t)); });
  }
  var FORM_MSG = {
    step: 'Заполните обязательные поля на этом шаге. Первое незаполненное поле выделено.',
    all: 'Заполните обязательные поля и подтвердите согласие. Первое незаполненное поле выделено.',
    done: 'Демонстрационный режим: форма заполнена корректно, но данные не отправлены. После запуска здесь появится подтверждение и следующий шаг.'
  };
  // every Russian string used by this script, so the translation tool can list them
  window.__i18nDyn = ['Кто отвечает', 'Этап', 'Этапы маршрута', 'Казахстан', 'Партнёрский центр', 'Включить светлую тему', 'Включить тёмную тему', 'версия', FORM_MSG.step, FORM_MSG.all, FORM_MSG.done]
    .concat(STEPS.reduce(function(acc, x){ return acc.concat([x.t, x.d, x.w]); }, []));
  refreshDynamic = function(){
    labelStops();
    rtItems.forEach(function(b, k){ var t = b.querySelector('.t'); if(t) t.textContent = tr(STEPS[k].t); });
    var l = document.querySelector('.rt-list'); if(l) l.setAttribute('aria-label', tr('Этапы маршрута'));
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
    function go(i, focus){
      cur = i;
      steps.forEach(function(s, k){ s.classList.toggle('active', k === i); });
      marks.forEach(function(m, k){ m.className = k < i ? 'done' : k === i ? 'now' : ''; if(k === i){ m.setAttribute('aria-current','step'); } else { m.removeAttribute('aria-current'); } });
      prev.hidden = i === 0;
      next.hidden = i === steps.length - 1;
      count.textContent = 'Шаг ' + (i + 1) + ' из ' + steps.length;
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
