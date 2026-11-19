#!/usr/bin/env bash
# Update the live site from GitHub. Run on the web server:
#   bash ~/hemabridge-site/tools/deploy.sh /path/to/webroot
# First time: git clone -b hemabridge-redesign https://github.com/sajberex-eng/hemabridge-site.git ~/hemabridge-site
# Copies only the public files (index.html, i18n, img, docs, robots.txt, .htaccess); src/, tools/, .git stay out of the webroot.
# Safe to run from cron: exits quietly when nothing changed.
# Before copying, the current webroot files are saved to ~/hemabridge-backups/<date>.tar.gz.
set -euo pipefail
WEB="${1:?usage: deploy.sh /path/to/webroot}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
[ -d "$WEB" ] || { echo "no such folder: $WEB" >&2; exit 1; }

cd "$REPO"
git pull -q --ff-only origin hemabridge-redesign
# nothing to do when the webroot already has this build (keeps cron runs quiet and backups few)
if [ -f "$WEB/index.html" ] && cmp -s "$REPO/index.html" "$WEB/index.html" && [ -d "$WEB/docs" ]; then exit 0; fi

mkdir -p ~/hemabridge-backups
STAMP=$(date +%Y%m%d-%H%M%S)
tar -czf ~/hemabridge-backups/"$STAMP".tar.gz -C "$WEB" . 2>/dev/null || true

for d in i18n img docs; do
  mkdir -p "$WEB/$d"
  cp -r "$REPO/$d/." "$WEB/$d/"
done
cp "$REPO/index.html" "$REPO/robots.txt" "$REPO/.htaccess" "$WEB/"

echo "deployed: $(grep -o 'data-v="[^"]*"' "$WEB/index.html" | head -1)  backup: ~/hemabridge-backups/$STAMP.tar.gz"
