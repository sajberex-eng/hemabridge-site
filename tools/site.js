// Whole-site check after a build. usage: node site.js [SHOTS_DIR]
// Every page from ../src/pages.json (+ 404) at 1440 and 390, light and dark, RU / EN / KZ:
//   page errors, horizontal overflow, exactly one <h1>, unique <title>/description, canonical, JSON-LD parses,
//   robots meta, every internal link and asset answers 200, anchors exist, leftover Cyrillic in the English view,
//   old single-page hashes (/#route ...) land on the right page.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const { start, ROOT } = require('./serve');
const pages = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/pages.json'), 'utf8')).pages;
const shots = process.argv[2];
(async () => {
  const srv = await start();
  const browser = await chromium.launch({ executablePath: require('./browser') });
  const issues = [], seen = { title: {}, desc: {} }, links = new Set(), anchors = [];
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
          await p.goto(srv.url + pg.path, { waitUntil: 'load' });
          await p.waitForTimeout(lang === 'ru' ? 250 : 600);
          const d = await p.evaluate(() => ({
            ov: document.documentElement.scrollWidth - innerWidth,
            h1: document.querySelectorAll('h1').length,
            vis: [...document.querySelectorAll('[data-page]')].filter(x => !x.hidden).length,
            title: document.title, htmlLang: document.documentElement.lang,
            desc: (document.querySelector('meta[name=description]') || {}).content,
            canon: (document.querySelector('link[rel=canonical]') || {}).href,
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
          if (lang === 'ru' && w === 1440 && scheme === 'light') {
            if (pg.id !== '404') {
              if (!d.canon || !d.canon.endsWith('/' + pg.path)) add(where, 'canonical ' + d.canon);
              for (const k of ['title', 'desc']) { if (seen[k][d[k]]) add(where, `same ${k} as ${seen[k][d[k]]}`); seen[k][d[k]] = pg.id; }
              if (d.title.length > 75) add(where, 'title is ' + d.title.length + ' chars');
              if (!d.desc || d.desc.length > 165) add(where, 'description is ' + (d.desc || '').length + ' chars');
            }
            if (pg.id !== '404') d.links.forEach(l => { links.add(l.split('#')[0]); if (l.includes('#')) anchors.push([where, l]); });
            if (shots) await p.screenshot({ path: path.join(shots, 'site-' + pg.id + '.png'), fullPage: true });
          }
          if (lang === 'en') {
            if (d.htmlLang !== 'en') add(where, 'html lang ' + d.htmlLang);
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
    if (!(want ? got.endsWith(want) : (got === '' || got === '#home'))) add('legacy #' + hash, 'landed on /' + got);
  }
  await browser.close(); srv.close();
  console.log(issues.length ? issues.join('\n') : 'no issues');
  console.log(`checked ${list.length} pages, ${links.size} internal links, ${anchors.length} anchors`);
  process.exit(issues.length ? 1 : 0);
})();
