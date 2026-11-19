// Chromium for Playwright: $CHROMIUM_PATH if set, else the cloud container's preinstalled headless shell if present,
// else Playwright's own browser (on a local PC run `npx playwright install chromium` once in tools/).
const fs = require('fs');
const CLOUD = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
module.exports = process.env.CHROMIUM_PATH || (fs.existsSync(CLOUD) ? CLOUD : undefined);
