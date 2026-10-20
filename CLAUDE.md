# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HemaBridge: a static, single-page marketing site (Russian source, English and Kazakh translations) for a Kazakhstan hematology program. No framework, no package manager, no tests. The deliverable is `index.html` + `i18n/` + `img/` + `robots.txt` + `.htaccess`, uploaded by hand to a free InfinityFree host (`DEPLOY-InfinityFree.md`). `PRODUCT.md` holds the product brief; `.impeccable/surfaces/index-html.md` holds the design direction contract.

## The build (read this before editing)

`index.html` is **generated**. Never hand-edit it; edit `src/` and rebuild:

```
cd src && python3 build.py      # writes ../index.html and ../i18n/{en,kk}.js
```

`build.py` starts from `src/original.html` (the untouched original page, including its inline script) and applies string replacements through `rep(s, old, new)`, which **exits if the anchor does not occur exactly once**. A failed anchor means the original markup was changed or an earlier step already consumed it. Order matters:

1. Inline replacements in `build.py` (fonts, meta, page-head illustrations via `head_art()`, doctor cards, etc.).
2. `src/style.css` replaces the original `<style>`; `src/hero.html` replaces the home hero + route map; `src/wizard.html` replaces the application form (multi-step wizard).
3. `src/fixes_home.py` and `src/i18n_patch.py` are `exec`'d on the assembled string `s` (they share its `rep` and `B`). `i18n_patch.py` patches the original inline script (route/title/theme/lang handlers) and inlines `src/i18n_runtime.js`.
4. `src/extra.js` (route map, mobile stop list, wizard, "second opinion" preselect) is spliced into the page script just before `window.addEventListener('hashchange', route)`. It runs inside the same IIFE as the original script, so it can use `tr()`, `STEPS`, etc.
5. `src/write_i18n.py` writes the dictionaries from `src/translations.json`.

The footer version stamp (`версия YYYY-MM-DD.N`) is a string in `build.py`; bump it on every release, because it is how you confirm which build a user is actually seeing on the host.

## Architecture

- Hash routing: one HTML file, 13 `<div class="page" data-page="...">` blocks shown/hidden by `route()`; `#kz`/`#en` are legacy hashes that now just switch language. A hash that is not a page id but an element id (e.g. `#kz-prep`, `#referral-form`) scrolls inside its page.
- i18n: Russian text lives in the HTML; `tr()` looks up the **normalized Russian string** (whitespace collapsed) in a dictionary (`window.__I18N_en` / `__I18N_kk`, lazy-loaded from `i18n/*.js`). `applyDom()` swaps every text node and `alt/aria-label/title/placeholder/data-label` attribute, remembering originals in WeakMaps so switching back to RU works. Consequences:
  - Mixed-content paragraphs (text around a link, `<abbr>`, `<span>`) are separate keys; translate fragments so they read as one sentence in order.
  - Any change to Russian copy changes its key, so the translation silently falls back to Russian until `src/translations.json` is updated. Strings produced by scripts are listed in `window.__i18nDyn` (in `extra.js`); containers filled by JS use `data-i18n-skip` and are re-painted by `refreshDynamic()`.
  - Language is stored in `localStorage['hb-lang']` (`ru|en|kz`) and can be forced with `?lang=kz|en`.
- To re-extract all Russian keys after copy changes: open the built page in headless Chromium and call `window.__i18nKeys()` (returns `{key, ctx}`; the result is what `src/keys.json` contains). Add the missing keys to `src/translations.json` as `{"<ru>": {"en": "...", "kk": "..."}}`, then rebuild. `merge_translations.py` is a one-off that depends on scratch paths outside the repo.
- Diagram labels in the route SVG are shrunk to fit by `fitSvgLabels()`; long translations of nav/button/SVG labels need short wording.
- Dark theme: CSS custom properties on `:root` with `prefers-color-scheme` plus `[data-theme]` overrides; any new colour needs both sets.
- Forms are demo-only (`data-demo`, no network). If they ever submit real patient data, KZ law requires hosting in Kazakhstan, so do not point them at InfinityFree.

## Checking changes

There is no test suite. Verify visually and with the page's own checks:

- Playwright with the preinstalled Chromium: use `executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'` (the full `chrome` binary refuses the old headless mode). Load `file:///.../index.html#home`, test 1440 and 390 widths, light and dark (`colorScheme`), and every language (preset `localStorage['hb-lang']` via `addInitScript`).
- Always check: no page errors, no horizontal overflow (`documentElement.scrollWidth - innerWidth`), no Cyrillic left in the English view.
- `/home/user/.claude/skills/impeccable/scripts/impeccable detect --json index.html` runs the design-slop detector (known false positives: `dark-glow`, `cramped-padding` on `.table-scroll`).

## Release and git

- Work on `hemabridge-redesign` (what GitHub Pages / the user views); `main` only has the initial README. A session stop hook requires everything committed and pushed, so commit and push after each change.
- To ship to the host, zip `index.html`, `i18n/`, `img/`, `robots.txt`, `.htaccess` (all of them: a missing `i18n/` makes KZ/EN buttons do nothing). The site is intentionally `noindex` (meta + `robots.txt`) until launch.
