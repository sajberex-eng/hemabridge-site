// Whole-site check after a build. usage: node site.js [SHOTS_DIR]
// Every page from ../src/pages.json (+ 404) at 1440 and 390, light and dark, RU / EN / KZ:
//   page errors, horizontal overflow, exactly one <h1>, unique <title>/description, canonical, JSON-LD parses,
//   robots meta, every internal link and asset answers 200, anchors exist, leftover Cyrillic in the English view,
//   old single-page hashes (/#route ...) land on the right page. Each language is checked at its own address
//   (/, /kk/, /en/): canonical, hreflang, unique titles; ?lang= and a saved language redirect to that address.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const { start, ROOT } = require('./serve');
const pages = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/pages.json'), 'utf8')).pages;
const shots = process.argv[2];
(async () => {
  const srv = await start();
  const browser = await chromium.launch({ executablePath: require('./browser') });
  const issues = [], seen = { title: {}, desc: {} }, links = new Set(), anchors = [];
  const DIR = { ru: '', en: 'en/', kz: 'kk/' }, HL = { ru: 'ru', en: 'en', kz: 'kk' };
  const add = (where, what) => issues.push(where + ': ' + what);
  const list = pages.map(p => ({ id: p.id, path: p.slug ? p.slug + '/' : '', draft: p.draft })).concat([{ id: '404', path: 'no-such-page/' }]);
  for (const pg of list) {
    for (const lang of ['ru', 'en', 'kz']) {
      for (const [w, h] of [[1440, 900], [390, 844]]) {
        for (const scheme of (lang === 'ru' ? ['light', 'dark'] : ['light'])) {
          const where = `${pg.id} ${lang} ${w} ${scheme}`;
          const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme, reducedMotion: 'reduce' });
          await ctx.addInitScript(l => { try { localStorage.setItem('hb-lang', l); } catch (e) {} }, lang);
          const p = await ctx.newPage();
          p.on('pageerror', e => add(where, 'page error ' + e.message));
          p.on('console', m => { if (m.type() === 'error' && !(pg.id === '404' && /404/.test(m.text()))) add(where, 'console ' + m.text()); });
          p.on('requestfailed', r => { if (!/fonts\.g/.test(r.url())) add(where, 'request failed ' + r.url()); });
          p.on('response', r => { if (r.status() >= 400 && !(pg.id === '404' && r.url().endsWith(pg.path))) add(where, r.status() + ' ' + r.url()); });
          const at = pg.id === '404' ? pg.path : DIR[lang] + pg.path;
          await p.goto(srv.url + at, { waitUntil: 'load' });
          await p.waitForTimeout(lang === 'ru' ? 250 : 600);
          const d = await p.evaluate(() => ({
            ov: document.documentElement.scrollWidth - innerWidth,
            h1: document.querySelectorAll('h1').length,
            vis: [...document.querySelectorAll('[data-page]')].filter(x => !x.hidden).length,
            title: document.title, htmlLang: document.documentElement.lang,
            desc: (document.querySelector('meta[name=description]') || {}).content,
            canon: (document.querySelector('link[rel=canonical]') || {}).href,
            hreflang: [...document.querySelectorAll('link[rel=alternate][hreflang]')].map(l => l.hreflang + ' ' + l.href),
            url: location.href,
            robots: (document.querySelector('meta[name=robots]') || {}).content,
            ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { JSON.parse(s.textContent); return true; } catch (e) { return false; } }),
            links: [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.startsWith(location.origin)),
            imgs: [...document.images].filter(i => i.complete && !i.naturalWidth && i.loading !== 'lazy').map(i => i.src),
            cyr: (() => { const out = []; const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
              while ((n = tw.nextNode())) { const pe = n.parentElement; if (!pe || /SCRIPT|STYLE/.test(pe.nodeName) || !pe.getClientRects().length) continue;
                if (/[Ѐ-ӿ]/.test(n.nodeValue)) out.push(n.nodeValue.trim().slice(0, 70)); } return out; })(),
          }));
          if (d.ov > 0) add(where, 'horizontal overflow ' + d.ov + 'px');
          if (d.h1 !== 1) add(where, 'h1 count ' + d.h1);
          if (d.vis !== 1) add(where, 'visible sections ' + d.vis);
          if (d.imgs.length) add(where, 'broken images ' + d.imgs.join(' '));
          if (d.ld.includes(false) || !d.ld.length) add(where, 'JSON-LD missing or invalid');
          if (!/noindex/.test(d.robots || '')) add(where, 'no noindex (the site must stay closed until launch)');
          if (pg.id !== '404' && !d.url.startsWith(srv.url + at)) add(where, 'redirected to ' + d.url);
          if (pg.id !== '404' && d.htmlLang !== HL[lang]) add(where, 'html lang ' + d.htmlLang);
          if (w === 1440 && scheme === 'light') {
            if (pg.id !== '404') {
              if (!d.canon || !d.canon.endsWith('/' + DIR[lang] + pg.path)) add(where, 'canonical ' + d.canon);
              if (d.hreflang.length !== 4 || !d.hreflang.some(x => x.startsWith('x-default '))) add(where, 'hreflang ' + d.hreflang.join(', '));
              for (const k of ['title', 'desc']) { const key = lang + ' ' + d[k]; if (seen[k][key]) add(where, `same ${k} as ${seen[k][key]}`); seen[k][key] = pg.id; }
              if (d.title.length > 85) add(where, 'title is ' + d.title.length + ' chars');
              if (!d.desc || d.desc.length > 165) add(where, 'description is ' + (d.desc || '').length + ' chars');
            }
            if (pg.id !== '404') d.links.forEach(l => { links.add(l.split('#')[0]); if (l.includes('#')) anchors.push([where, l]); });
            if (shots && lang === 'ru') await p.screenshot({ path: path.join(shots, 'site-' + pg.id + '.png'), fullPage: true });
          }
          if (lang === 'en') {
            if (/[Ѐ-ӿ]/.test(d.title)) add(where, 'Cyrillic in title: ' + d.title);
            if (/[Ѐ-ӿ]/.test(d.desc)) add(where, 'Cyrillic in description');
            const bad = d.cyr.filter(t => !/Скачать на русском|Қазақ тілінде|ҚР ДСМ/.test(t));
            if (bad.length && w === 1440 && !pg.draft) add(where, 'Cyrillic left: ' + bad.slice(0, 5).join(' | '));
          }
          if (lang === 'kz' && d.title === (seen.ruTitle || {})[pg.id]) add(where, 'title not translated to Kazakh');
          if (lang === 'ru') (seen.ruTitle = seen.ruTitle || {})[pg.id] = d.title;
          await ctx.close();
        }
      }
    }
  }
  // links and anchors
  const ctx = await browser.newContext(); const p = await ctx.newPage();
  for (const l of links) { const r = await ctx.request.get(l); if (r.status() !== 200) add('link', r.status() + ' ' + l); }
  for (const [where, l] of anchors) {
    await p.goto(l); const ok = await p.evaluate(h => !!document.getElementById(h), decodeURIComponent(l.split('#')[1]));
    if (!ok) add(where, 'anchor not found ' + l);
  }
  // hashes of the old single-page site must land on the new pages
  for (const [hash, want] of [['route', 'marshrut/'], ['tech', 'tehnologii/'], ['followup', '#followup'], ['referral-form', 'vracham/#referral-form'], ['stage-3', 'marshrut/#stage-3'], ['home', ''], ['kz', '']]) {
    await p.goto(srv.url + 'no-such-page/'); await p.goto(srv.url + '#' + hash); await p.waitForTimeout(500);
    const got = p.url().slice(srv.url.length);
    if (!(want ? got.endsWith(want) : (got === '' || got === '#home' || got === 'kk/'))) add('legacy #' + hash, 'landed on /' + got);
  }
  // language addresses: ?lang= and a saved choice move a visitor from the Russian address; the switcher links to the same page
  for (const [from, saved, want] of [['kliniki/?lang=en', null, 'en/kliniki/'], ['kliniki/?lang=kz', null, 'kk/kliniki/'], ['marshrut/', 'kz', 'kk/marshrut/'],
                                     ['en/marshrut/', 'kz', 'en/marshrut/'], ['en/marshrut/?lang=ru', null, 'marshrut/'], ['#en', null, 'en/']]) {
    const c2 = await browser.newContext(); if (saved) await c2.addInitScript(l => { try { localStorage.setItem('hb-lang', l); } catch (e) {} }, saved);
    const q = await c2.newPage(); await q.goto(srv.url + from); await q.waitForTimeout(500);
    const got = q.url().slice(srv.url.length).split('#')[0];
    if (got !== want) add('language /' + from + (saved ? ' saved ' + saved : ''), 'landed on /' + got + ', expected /' + want);
    await c2.close();
  }
  { const c2 = await browser.newContext(); const q = await c2.newPage(); await q.goto(srv.url + 'kk/kliniki/');
    const sw = await q.$$eval('.lang a', as => as.map(a => a.getAttribute('data-lang') + '=' + a.pathname + (a.getAttribute('aria-current') ? '*' : '')));
    if (sw.join(' ') !== 'ru=/kliniki/ kz=/kk/kliniki/* en=/en/kliniki/') add('switcher /kk/kliniki/', sw.join(' '));
    await c2.close(); }
  await browser.close(); srv.close();
  console.log(issues.length ? issues.join('\n') : 'no issues');
  console.log(`checked ${list.length} pages, ${links.size} internal links, ${anchors.length} anchors`);
  process.exit(issues.length ? 1 : 0);
})();
