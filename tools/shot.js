// usage: node shot.js <outdir> <prefix> [page id...]   (page ids are in ../src/pages.json)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [out, prefix, ...hashes] = process.argv.slice(2);
  const url = await require('./pageurl')();
  const browser = await chromium.launch({ executablePath: require('./browser') });
  const errors = [];
  for (const h of (hashes.length ? hashes : ['home'])) {
    for (const [w, hgt, tag] of [[1280, 800, 'd'], [390, 844, 'm']]) {
      for (const scheme of ['light', 'dark']) {
        const ctx = await browser.newContext({ viewport: { width: w, height: hgt }, colorScheme: scheme, reducedMotion: 'reduce' });
        const p = await ctx.newPage();
        p.on('pageerror', e => errors.push(h + ': ' + e.message));
        p.on('console', m => { if (m.type() === 'error') errors.push(h + ' console: ' + m.text()); });
        await p.goto(url(h));
        await p.waitForTimeout(700);
        await p.screenshot({ path: `${out}/${prefix}-${h}-${tag}-${scheme}.png`, fullPage: true });
        const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
        if (ov > 0) errors.push(`${h} ${tag} ${scheme}: horizontal overflow ${ov}px`);
        await ctx.close();
      }
    }
  }
  await browser.close();
  console.log(errors.length ? errors.join('\n') : 'no errors');
})();
