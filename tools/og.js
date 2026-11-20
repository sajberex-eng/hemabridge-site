// Renders tools/og.html to img/og.jpg (1200x630 link-preview picture). usage: node og.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({ executablePath: require('./browser') });
  const p = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await p.goto(require('url').pathToFileURL(path.resolve(__dirname, 'og.html')).href);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  const fonts = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').length);
  await p.screenshot({ path: path.resolve(__dirname, '../img/og.jpg'), type: 'jpeg', quality: 88 });
  await browser.close();
  console.log('img/og.jpg written, web fonts loaded:', fonts);
})();
