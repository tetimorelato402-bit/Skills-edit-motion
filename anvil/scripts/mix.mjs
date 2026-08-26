/**
 * Builds the film's full audio bed once: room tone under everything, the
 * voiceover placed at VO_AT, and every sfx cue the timeline declares.
 * No music. The mix is dry by design — the only thing holding the silences
 * open is the room tone.
 *
 * Sound cues are not listed here. They are `sfx` tracks in the timeline, next
 * to the motion they belong to, so a beat cannot be retimed without its sound
 * moving with it.
 */
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { VO_AT, film, duration } from "../build/timeline.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const A = (f) => join(ROOT, "audio", f);
const ms = (t) => Math.round(t * 1000);

const FADE_AT = duration - 0.55;

execFileSync("python3", [join(ROOT, "scripts/sfx.py")], { stdio: "inherit" });
execFileSync("python3", [join(ROOT, "scripts/roomtone.py"),
  duration.toFixed(3), A("room.wav"), FADE_AT.toFixed(3)], { stdio: "inherit" });

const cues = film.filter((t) => t.k === "sfx").sort((a, b) => a.at - b.at);
for (const c of cues) {
  const f = join(ROOT, "audio/sfx", `${c.src}.wav`);
  if (!existsSync(f)) throw new Error(`sfx cue "${c.src}" at ${c.at}s has no sound file`);
}

const inputs = ["-i", A("room.wav"), "-i", A("vo_trimmed.wav"),
                ...cues.flatMap((c) => ["-i", join(ROOT, "audio/sfx", `${c.src}.wav`)])];

const chains = [
  // The room tone sinks almost to nothing through the lock hold — the air
  // goes out of the room while the viewer stands at the closed door — and
  // comes back with the release, so the unlock lands into a real vacuum.
  // Only the generated floor is touched; the VO is never processed.
  `[0:a]volume='1-0.8*clip((t-10.45)/0.9,0,1)+0.8*clip((t-12.90)/0.35,0,1)':eval=frame[rm]`,
  // VO is the master reference: placed, never stretched, pitched or ducked.
  `[1:a]adelay=${ms(VO_AT)},apad[vo]`,
  ...cues.map((c, i) =>
    `[${i + 2}:a]volume=${c.gain},adelay=${ms(c.at)},apad[s${i}]`),
];
const labels = ["[rm]", "[vo]", ...cues.map((_, i) => `[s${i}]`)].join("");

execFileSync("ffmpeg", [
  "-hide_banner", "-v", "error", "-y", ...inputs,
  "-filter_complex",
  `${chains.join(";")};${labels}amix=inputs=${cues.length + 2}:duration=first:normalize=0,` +
  `alimiter=limit=0.97:level=disabled[a]`,
  "-map", "[a]", "-t", duration.toFixed(3),
  "-ar", "44100", "-ac", "1", "-c:a", "pcm_s24le", A("mix.wav"),
], { stdio: "inherit" });

console.log(`\nmix: ${duration.toFixed(3)}s → audio/mix.wav`);
console.log(`  VO at ${VO_AT}s, ${cues.length} sound cues:`);
for (const c of cues) console.log(`    ${c.at.toFixed(3)}s  ${c.src.padEnd(12)} ${c.gain}`);
