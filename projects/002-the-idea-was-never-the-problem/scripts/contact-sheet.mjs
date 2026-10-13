/**
 * Renders a contact sheet — the cheapest artefact that proves the act works.
 *
 * It goes through Remotion's renderer rather than pulling frames out of the
 * mp4, because the ffmpeg that ships with Playwright in this container is built
 * with --disable-everything and can neither demux mp4 nor decode h264. Doing it
 * this way is better anyway: one bundle, N stills, straight from the source of
 * truth, and no generation loss from the H.264 encode.
 *
 *   node scripts/contact-sheet.mjs ActI 0 37 47 ...
 */
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {mkdirSync, rmSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const BROWSER = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';

const [compId, ...frameArgs] = process.argv.slice(2);
const frames = frameArgs.map(Number);
if (!compId || frames.length === 0) {
  console.error('usage: node scripts/contact-sheet.mjs <composition> <frame> [frame...]');
  process.exit(1);
}

const outDir = join(ROOT, 'outputs/frames', compId);
rmSync(outDir, {recursive: true, force: true});
mkdirSync(outDir, {recursive: true});

console.log('bundling…');
const serveUrl = await bundle({entryPoint: join(ROOT, 'src/index.ts')});
const composition = await selectComposition({serveUrl, id: compId, browserExecutable: BROWSER});

for (const frame of frames) {
  const output = join(outDir, `${String(frame).padStart(4, '0')}.png`);
  await renderStill({
    composition,
    serveUrl,
    output,
    frame,
    browserExecutable: BROWSER,
  });
  console.log(`  frame ${String(frame).padStart(4)}  ${(frame / composition.fps).toFixed(3)}s`);
}
console.log(outDir);
