// Rewrites ../src/keys.json: every Russian string the pages show (window.__i18nKeys() on each page, merged).
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const url = await require('./pageurl')();
  const b = await chromium.launch({ executablePath: require('./browser') });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  const seen = new Set(), keys = [];
  for (const id of url.ids.concat(['404.html'])) {
    await p.goto(url(id)); await p.waitForTimeout(500);
    for (const k of await p.evaluate(() => window.__i18nKeys())) { if (!seen.has(k.key)) { seen.add(k.key); keys.push(k); } }
  }
  fs.writeFileSync(require('path').resolve(__dirname, '../src/keys.json'), JSON.stringify(keys, null, 1));
  const kinds = {}; keys.forEach(k => kinds[k.ctx.kind] = (kinds[k.ctx.kind] || 0) + 1);
  console.log(keys.length, JSON.stringify(kinds), 'chars', keys.reduce((a, k) => a + k.key.length, 0), 'errs', errs);
  await b.close(); process.exit(0);
})();
