/**
 * Builds the film's full audio bed once: room tone under everything, the
 * voiceover placed at VO_AT, the anvil strike on the unlock. No music — the
 * mix is dry by design, so the only thing holding the silences open is the
 * room tone.
 */
import { execFileSync } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { VO_AT, CLANG_AT, duration } from "../build/timeline.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const A = (f) => join(ROOT, "audio", f);
const ms = (t) => Math.round(t * 1000);

/** the picture fades from here, so the tone goes with it */
const FADE_AT = duration - 0.55;

execFileSync("python3", [join(ROOT, "scripts/roomtone.py"),
  duration.toFixed(3), A("room.wav"), FADE_AT.toFixed(3)], { stdio: "inherit" });

execFileSync("ffmpeg", [
  "-hide_banner", "-v", "error", "-y",
  "-i", A("room.wav"),
  "-i", A("vo_trimmed.wav"),
  "-i", A("clang.wav"),
  "-filter_complex",
  // VO is the master reference: placed, never stretched, pitched or ducked.
  `[1:a]adelay=${ms(VO_AT)},apad[vo];` +
  // the strike sits on top and is never ducked
  `[2:a]pan=mono|c0=0.5*c0+0.5*c1,volume=0.9,adelay=${ms(CLANG_AT)},apad[cl];` +
  `[0:a][vo][cl]amix=inputs=3:duration=first:normalize=0,` +
  `alimiter=limit=0.97:level=disabled[a]`,
  "-map", "[a]", "-t", duration.toFixed(3),
  "-ar", "44100", "-ac", "1", "-c:a", "pcm_s24le", A("mix.wav"),
], { stdio: "inherit" });

console.log(`mix: ${duration.toFixed(3)}s → audio/mix.wav (VO at ${VO_AT}s, clang at ${CLANG_AT.toFixed(3)}s)`);
