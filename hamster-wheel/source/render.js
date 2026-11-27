// usage: node render.js <outdir> <fps> [t1,t2,... preview times]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname;
const srv = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': p.endsWith('.js') ? 'text/javascript' : 'text/html' }); res.end(d); });
}).listen(0);
(async () => {
  const port = srv.address().port;
  const out = process.argv[2]; const fps = +process.argv[3];
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 720, height: 1280 } });
  pg.on('console', m => console.log('page:', m.text())); pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.goto(`http://localhost:${port}/scene.html`);
  await pg.waitForFunction('window.ready === true', null, { timeout: 60000 });
  const times = process.argv[4] ? process.argv[4].split(',').map(Number) : [...Array(Math.round(4 * fps)).keys()].map(i => i / fps);
  for (let i = 0; i < times.length; i++) {
    const url = await pg.evaluate(t => window.renderAt(t), times[i]);
    fs.writeFileSync(path.join(out, `f${String(i).padStart(4, '0')}.png`), Buffer.from(url.split(',')[1], 'base64'));
    if (i % 40 === 0) console.log('frame', i, '/', times.length);
  }
  await b.close(); srv.close();
})();
