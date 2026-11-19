# QA tools (not deployed)

Playwright helpers used to check `../index.html` after a build. Run from this folder (PowerShell or bash).

```
npm install; npx playwright install chromium   # once (on a local PC)
# optional: CHROMIUM_PATH=/path/to/chrome-or-headless_shell (see browser.js for the default)

node shot.js ../index.html OUT_DIR PREFIX home route apply   # full-page shots, 1280/390, light/dark; prints errors and horizontal overflow
node vp.js home 1440 900 out.png [light|dark] [scrollY]      # one viewport screenshot
node langvp.js en|kz home 1440 900 out.png [scrollY|selector]  # same, in English or Kazakh
node langqa.js en|kz [SHOTS_DIR]                             # all pages at 1440 and 390: leftover Cyrillic (en), clipped or colliding labels, overflow
node keys.js                                                 # rewrites ../src/keys.json from window.__i18nKeys()
```

## Deploy to the server (bridge.hemcenter.kz)

On the server, once: `git clone -b hemabridge-redesign https://github.com/sajberex-eng/hemabridge-site.git ~/hemabridge-site`.
Then after every change: `bash ~/hemabridge-site/tools/deploy.sh /path/to/webroot` (pulls from GitHub, backs up the webroot to `~/hemabridge-backups/`, copies only the public files).
