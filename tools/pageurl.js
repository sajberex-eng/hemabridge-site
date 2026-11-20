// const url = await require('./pageurl')();  url('route') -> http://127.0.0.1:PORT/marshrut/
// Starts the local server (it does not keep the process alive) and maps a page id from ../src/pages.json to its address.
const fs = require('fs'), path = require('path');
const { start, ROOT } = require('./serve');
module.exports = async () => {
  const srv = await start();
  const pages = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/pages.json'), 'utf8')).pages;
  const f = id => { const p = pages.find(x => x.id === id); return srv.url + (p ? (p.slug ? p.slug + '/' : '') : id); };
  f.ids = pages.map(p => p.id); f.close = srv.close;
  return f;
};
