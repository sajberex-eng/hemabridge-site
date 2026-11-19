# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HemaBridge: a static, single-page marketing site (Russian source, English and Kazakh translations) for a Kazakhstan hematology program (ТОО «Центр гематологии», Astana). No framework, no tests. The deliverable is `index.html` + `i18n/` + `img/` + `docs/` + `robots.txt` + `.htaccess`, live at **https://bridge.hemcenter.kz/** (the center's Apache/Ubuntu server; see `DEPLOY.md`). `PRODUCT.md` holds the product brief; `.impeccable/surfaces/index-html.md` holds the design direction contract; `PLAN.md` holds the current status and open items. The project owner works in Russian: answer in Russian.

The project now lives on the owner's Windows PC at `C:\Projects\HemaBridge` (a clone of `sajberex-eng/hemabridge-site`, branch `hemabridge-redesign`). Commands below are given for PowerShell; `python` may be `py` on Windows.

## The build (read this before editing)

`index.html` is **generated**. Never hand-edit it; edit `src/` and rebuild:

```
cd src; python build.py      # writes ../index.html and ../i18n/{en,kk}.js
```

`build.py` starts from `src/original.html` (the untouched original page, including its inline script) and applies string replacements through `rep(s, old, new)`, which **exits if the anchor does not occur exactly once**. A failed anchor means the original markup was changed or an earlier step already consumed it. Order matters:

1. Inline replacements in `build.py` (fonts, meta, page-head illustrations via `head_art()`, doctor cards, etc.).
2. `src/style.css` replaces the original `<style>`; `src/hero.html` replaces the home hero + route map; `src/wizard.html` replaces the application form (multi-step wizard).
3. `src/fixes_home.py` and `src/i18n_patch.py` are `exec`'d on the assembled string `s` (they share its `rep` and `B`). `i18n_patch.py` patches the original inline script (route/title/theme/lang handlers) and inlines `src/i18n_runtime.js`.
3a. `src/content_update.py` (exec'd between the two) holds the November 2026 content, driven by data files: `route.json` (six route steps: consultation, offer, case conferences (50 000 ₸), contract with clinic, treatment abroad, follow-up; `ours: false` marks the clinic's responsibility; also injected into `extra.js` as `STEPS` and used for the SVG labels in `hero.html`), `contacts.json` (patients only: project coordinator, phone, e-mail; an empty value renders «будет добавлен»; partner contacts are deliberately not published), `clinics.json` (candidate-centre cards with source links; facts must be re-checked on the official pages). It also builds the cost page's follow-up plans table (1/3/6 months, `#followup`), without prices.
4. `src/extra.js` (route map, mobile stop list, wizard, "second opinion" preselect) is spliced into the page script just before `window.addEventListener('hashchange', route)`. It runs inside the same IIFE as the original script, so it can use `tr()`, `STEPS`, etc.
5. `src/write_i18n.py` writes the dictionaries from `src/translations.json`.

The footer version stamp (`версия YYYY-MM-DD.N`) is a string in `build.py`; bump it on every release, because it is how you confirm which build a user is actually seeing on the host.

## Architecture

- Hash routing: one HTML file, 13 `<div class="page" data-page="...">` blocks shown/hidden by `route()`; `#kz`/`#en` are legacy hashes that now just switch language. A hash that is not a page id but an element id (e.g. `#kz-prep`, `#referral-form`) scrolls inside its page.
- i18n: Russian text lives in the HTML; `tr()` looks up the **normalized Russian string** (whitespace collapsed) in a dictionary (`window.__I18N_en` / `__I18N_kk`, lazy-loaded from `i18n/*.js`). `applyDom()` swaps every text node and `alt/aria-label/title/placeholder/data-label` attribute, remembering originals in WeakMaps so switching back to RU works. Consequences:
  - Mixed-content paragraphs (text around a link, `<abbr>`, `<span>`) are separate keys; translate fragments so they read as one sentence in order.
  - Any change to Russian copy changes its key, so the translation silently falls back to Russian until `src/translations.json` is updated. Strings produced by scripts are listed in `window.__i18nDyn` (in `extra.js`); containers filled by JS use `data-i18n-skip` and are re-painted by `refreshDynamic()`.
  - Language is stored in `localStorage['hb-lang']` (`ru|en|kz`) and can be forced with `?lang=kz|en`.
- To re-extract all Russian keys after copy changes: open the built page in headless Chromium and call `window.__i18nKeys()` (returns `{key, ctx}`; the result is what `src/keys.json` contains). Add the missing keys to `src/translations.json` as `{"<ru>": {"en": "...", "kk": "..."}}`, then rebuild.
- Diagram labels in the route SVG are shrunk to fit by `fitSvgLabels()`; long translations of nav/button/SVG labels need short wording.
- Dark theme: CSS custom properties on `:root` with `prefers-color-scheme` plus `[data-theme]` overrides; any new colour needs both sets.
- `docs/` holds the partner questionnaire workbooks (RU/KK/EN), generated by `python src/make_questionnaire.py` (needs openpyxl) from `src/questionnaire*.json`; the public file has one answer column and no internal columns.
- Forms are demo-only (`data-demo`, no network). Real patient data must stay on servers in Kazakhstan (KZ law); bridge.hemcenter.kz is the center's own server, InfinityFree (old test host) is not acceptable for that.

## Checking changes

There is no test suite. Verify visually and with the page's own checks:

- Ready-made helpers live in `tools/` (see `tools/README.md`): `shot.js`, `vp.js`, `langvp.js`, `langqa.js`, `keys.js`. They are not part of the deployed site.
- Setup once: Node.js, then `cd tools; npm install; npx playwright install chromium`. `tools/browser.js` picks `$CHROMIUM_PATH`, else the cloud container's headless shell if present, else Playwright's own Chromium. Pages load via `pathToFileURL`, so Windows paths work. Test 1440 and 390 widths, light and dark (`colorScheme`), and every language (preset `localStorage['hb-lang']` via `addInitScript`).
- Always check: no page errors, no horizontal overflow (`documentElement.scrollWidth - innerWidth`), no Cyrillic left in the English view.
- `.claude/skills/impeccable/scripts/impeccable detect --json index.html` runs the design-slop detector (known false positives: `dark-glow`, `cramped-padding` on `.table-scroll`).
- Design skills (Impeccable, Taste, Emil Kowalski) are vendored in `.claude/skills/` (see its README); `PRODUCT.md` and `.impeccable/surfaces/index-html.md` are the context Impeccable reads.

## Release and git

- Work on `hemabridge-redesign`; `main` only has the initial README. Commit and push after each change (GitHub is the source the server deploys from).
- Line endings are LF (`.gitattributes`); `rep()` anchors contain `\n`, so CRLF checkouts would break the build.
- Deploy is automatic: a cron job on the server runs a deploy script every 2 minutes that fetches `hemabridge-redesign` and rsyncs the public files to the webroot when the commit changes. So a push goes live in ~2 minutes; no manual step. Details in `DEPLOY.md`. The real SSH login, server address, key location, script path and webroot are kept only in the local, git-ignored `CLAUDE.local.md` (the repo is public: never commit them). The script never deletes files from the webroot, and it skips `src/`, `tools/`, `*.md`, `*.py`. All six public items are required (a missing `i18n/` makes KZ/EN do nothing, a missing `docs/` breaks the questionnaire and offer links).
- After deploying, check the footer stamp on https://bridge.hemcenter.kz/ (`data-v` attribute). The site is intentionally `noindex` (meta + `robots.txt`) until launch.
- Never publish internal margins or cost breakdowns (e.g. from the follow-up deck); follow-up prices stay hidden until the owner approves them.
