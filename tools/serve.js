// Tiny static server over the repository root, so pages are checked at their real addresses (/marshrut/ etc.).
// usage as a module: const { start } = require('./serve'); const srv = await start(); srv.url, srv.close()
// usage from a shell: node serve.js [port]   (then open http://localhost:8765/)
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const TYPES = { html: 'text/html; charset=utf-8', js: 'text/javascript; charset=utf-8', css: 'text/css', png: 'image/png', jpg: 'image/jpeg',
  webp: 'image/webp', svg: 'image/svg+xml', xml: 'application/xml', txt: 'text/plain; charset=utf-8', pdf: 'application/pdf',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' };
function start(port) {
  const server = http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]);
    let f = path.join(ROOT, p);
    if (!f.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
    if (fs.existsSync(f) && fs.statSync(f).isDirectory()) {
      if (!p.endsWith('/')) { res.writeHead(301, { Location: p + '/' }); return res.end(); }
      f = path.join(f, 'index.html');
    }
    if (!fs.existsSync(f)) { res.writeHead(404, { 'Content-Type': TYPES.html }); return res.end(fs.readFileSync(path.join(ROOT, '404.html'))); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(f).slice(1)] || 'application/octet-stream' });
    res.end(fs.readFileSync(f));
  });
  return new Promise(ok => server.listen(port || 0, '127.0.0.1', () =>
    { if (require.main !== module) server.unref(); ok({ url: 'http://127.0.0.1:' + server.address().port + '/', close: () => server.close() }); }));
}
module.exports = { start, ROOT };
if (require.main === module) start(+process.argv[2] || 8765).then(s => console.log('serving', ROOT, 'at', s.url));
