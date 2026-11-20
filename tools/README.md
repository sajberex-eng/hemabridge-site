# QA tools (not deployed)

Playwright helpers used to check the built site. They start a local server over the repository root themselves and take page ids from `../src/pages.json` (`home`, `route`, `bmt` …). Run from this folder (PowerShell or bash).

```
npm install; npx playwright install chromium   # once (on a local PC)
# optional: CHROMIUM_PATH=/path/to/chrome-or-headless_shell (see browser.js for the default)

node site.js [SHOTS_DIR]                                     # whole site, run after every build (takes a few minutes): errors, overflow, one h1, unique titles, canonical, JSON-LD, noindex, links and anchors, old #hashes, Cyrillic left in English
node serve.js                                                # browse the site at http://localhost:8765/
node shot.js OUT_DIR PREFIX home route apply                 # full-page shots, 1280/390, light/dark; prints errors and horizontal overflow
node vp.js home 1440 900 out.png [light|dark] [scrollY]      # one viewport screenshot
node langvp.js en|kz home 1440 900 out.png [scrollY|selector]  # same, in English or Kazakh
node langqa.js en|kz [SHOTS_DIR]                             # all pages at 1440 and 390: leftover Cyrillic (en), clipped or colliding labels, overflow
node keys.js                                                 # rewrites ../src/keys.json from window.__i18nKeys() on every page
node og.js                                                   # redraws ../img/og.jpg (link-preview picture) from og.html
```

Deploying is not done from here: the server publishes `hemabridge-redesign` on its own (see `../DEPLOY.md`).
