// Drive headless Chrome over CDP and capture frames of index.html.
// usage: node render.mjs <html> <outDir> <fps> <fromFrame> <toFrame>   (frames [from,to))
//        node render.mjs <html> <outDir> stills t1,t2,...              (named stills)
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const [, , htmlPath, outDir, a3, a4, a5] = process.argv;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
fs.mkdirSync(outDir, { recursive: true });
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'pma-chrome-'));
const ch = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${udd}`,
  '--hide-scrollbars', '--mute-audio', '--no-first-run', '--no-default-browser-check',
  '--force-color-profile=srgb', '--window-size=1920,1080', 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });

const browserWs = await new Promise((res, rej) => {
  let buf = '';
  ch.stderr.on('data', d => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) res(m[1]); });
  setTimeout(() => rej(new Error('chrome did not start: ' + buf)), 30000);
});
const port = new URL(browserWs).port;
let page;
for (let i = 0; i < 50 && !page; i++) {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  page = list.find(t => t.type === 'page');
  if (!page) await new Promise(r => setTimeout(r, 100));
}
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let id = 0; const pending = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { const { res, rej } = pending.get(m.id); pending.delete(m.id); m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); } };
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });

await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
await send('Page.enable');
await send('Runtime.enable');
await send('Page.navigate', { url: 'file://' + path.resolve(htmlPath) });
let ready = false;
for (let i = 0; i < 200 && !ready; i++) {
  try { const r = await send('Runtime.evaluate', { expression: 'JSON.stringify({r:window.__ready===true,e:window.__err||null})', returnByValue: true }); const v = JSON.parse(r.result.value); if (v.e) throw new Error('page error: ' + v.e); ready = v.r; } catch (e) { if (String(e).includes('page error')) throw e; }
  if (!ready) await new Promise(r => setTimeout(r, 100));
}
if (!ready) throw new Error('page not ready');

async function shot(t, file) {
  const r = await send('Runtime.evaluate', { expression: `renderFrame(${t});0`, returnByValue: true });
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
  const s = await send('Page.captureScreenshot', { format: 'jpeg', quality: 93 });
  fs.writeFileSync(file, Buffer.from(s.data, 'base64'));
}

const t0 = Date.now();
if (a3 === 'stills') {
  for (const t of a4.split(',').map(Number)) await shot(t, path.join(outDir, `still-${t.toFixed(2)}.jpg`));
} else {
  const fps = Number(a3), from = Number(a4), to = Number(a5);
  for (let f = from; f < to; f++) await shot(f / fps, path.join(outDir, String(f).padStart(5, '0') + '.jpg'));
}
console.log(`done in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
ws.close(); ch.kill('SIGKILL');
fs.rmSync(udd, { recursive: true, force: true });
process.exit(0);
