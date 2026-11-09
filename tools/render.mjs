// Renders tools/blocks.html into assets/*.png at 2x.
// Blocks with several links are rows of tiles, one image per tile (see the gutter note below).
// Run: node tools/render.mjs   (needs Chrome: CHROME=/path/to/chrome, puppeteer-core via MEDIA_ROOT engine)
import { pathToFileURL, fileURLToPath } from 'node:url';
import { join, dirname } from 'node:path';
import { homedir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '..', 'assets');
const MEDIA = process.env.MEDIA_ROOT || join(homedir(), 'Projects/GitHub/media');
const { loadRuntime } = await import(pathToFileURL(join(MEDIA, 'engine/browser_runtime.mjs')).href);
const { puppeteer, executablePath } = await loadRuntime();


const br = await puppeteer.launch({ executablePath: process.env.CHROME || executablePath, headless: true, args: ['--allow-file-access-from-files'] });
const pg = await br.newPage();
await pg.setViewport({ width: 830, height: 900, deviceScaleFactor: 2 });
await pg.goto(pathToFileURL(join(HERE, 'blocks.html')).href, { waitUntil: 'load' });
await pg.evaluate(() => document.fonts.ready);
const box = sel => pg.$eval(sel, e => { const r = e.getBoundingClientRect(); return { x: r.x, y: r.y + scrollY, w: r.width, h: r.height }; });
const shot = (name, c) => pg.screenshot({ path: join(OUT, `${name}.png`), omitBackground: true, captureBeyondViewport: true, clip: c });
for (const id of ['hero', 'work', 'media-title', 'main', 'dsml-title']) {
  const b = await box('#' + id); await shot(id, { x: b.x, y: b.y, width: b.w, height: b.h }); console.log(id);
}
// Tiles with their own links: each strip carries half of the transparent gutter on its inner sides,
// so strips placed side by side meet inside the gutter and no seam shows.
for (const row of ['media', 'dsml']) {
  const r = await box(`#${row}-row`), n = await pg.$$eval(`#${row}-row > .blk`, e => e.length);
  for (let i = 1; i <= n; i++) {
    const b = await box(`#${row}-${i}`);
    const x0 = i === 1 ? r.x : b.x - 8, x1 = i === n ? r.x + r.w : b.x + b.w + 8;
    await shot(`${row}-${i}`, { x: x0, y: b.y, width: x1 - x0, height: b.h });
    console.log(`${row}-${i}`, ((x1 - x0) / r.w * 100).toFixed(3) + '%');
  }
}
await br.close();
