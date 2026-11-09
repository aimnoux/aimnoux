// Renders tools/blocks.html into assets/*.png at 2x.
// One image per block: strips side by side leave a visible hairline at the seam.
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
for (const id of ['hero', 'work', 'media', 'main', 'dsml']) {
  const b = await pg.$eval('#' + id, e => { const r = e.getBoundingClientRect(); return { x: r.x, y: r.y + scrollY, w: r.width, h: r.height }; });
  await pg.screenshot({ path: join(OUT, `${id}.png`), omitBackground: true, captureBeyondViewport: true,
    clip: { x: b.x, y: b.y, width: b.w, height: b.h } });
  console.log(id);
}
await br.close();
