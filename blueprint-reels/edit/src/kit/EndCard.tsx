import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { LOCKUP_PATHS, LOCKUP_VIEWBOX } from '../logo/lockup-paths';
import { C, FONT } from '../theme';

/**
 * End card (BRIEF 7.4), identical in all four films. Local frame 0 = AT.
 * `on` = ON - AT (film 01: 10, films 02-04: 9).
 * Logo = the Appendix A lockup paths, unmodified, scaled uniformly so the visible
 * lockup (x 294..1329) is 800 px wide with its visible center at (540, 812).
 * No glow, shadow, blur, rotation, stretch or recolor except the bulb dim->on and ray reveal.
 */
const S = 800 / 1035;
const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a: string, b: string, t: number) => {
  const A = hex(a);
  const B = hex(b);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join('');
};
const clamp01 = (x: number) => Math.min(1, Math.max(0, x));

export const EndLogo: React.FC<{ f: number; on: number }> = ({ f, on }) => {
  const k = clamp01((f - on) / 2); // bulb: dim -> on over 2 frames
  // ray i (1..5) fully visible at ON + 8 + 5*(i-1), each fading in over 2 frames
  const ray = (i: number) => clamp01((f - (on + 8 + 5 * (i - 1) - 2)) / 2);
  const bulbFill = k >= 1 ? undefined : mix(C.dim, C.yellow, k);
  return (
    <svg
      viewBox={LOCKUP_VIEWBOX}
      width={1600 * S}
      height={600 * S}
      style={{ position: 'absolute', left: 540 - 811.5 * S, top: 812 - 298 * S }}
    >
      {LOCKUP_PATHS.map((p) => {
        let fill = p.fill;
        let opacity: number | undefined;
        if (p.groups.includes('bulb') && bulbFill) fill = bulbFill;
        const m = p.id.match(/^ray-(\d)$/);
        if (m) {
          const o = ray(Number(m[1]));
          if (o < 1) opacity = o;
        }
        return <path key={p.id} id={p.id} d={p.d} fill={fill} fillRule={p.evenodd ? 'evenodd' : undefined} opacity={opacity} />;
      })}
    </svg>
  );
};

export const EndCard: React.FC<{ on: number }> = ({ on }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < 3) {
    // 3 frames of Idea Yellow flash (the match cut from the film's last yellow light)
    return <div style={{ position: 'absolute', inset: 0, background: C.yellow }} />;
  }
  const tag = interpolate(f - (on + 36), [0, 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const btn = spring({ frame: f - (on + 48), fps, config: { damping: 11, stiffness: 220, mass: 0.6 } });
  return (
    <div style={{ position: 'absolute', inset: 0, background: C.blue }}>
      <EndLogo f={f} on={on} />
      <div
        style={{
          position: 'absolute',
          top: 1050,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: FONT.inter,
          fontWeight: 800,
          fontSize: 60,
          color: C.white,
          opacity: tag,
          transform: `translateY(${(1 - tag) * 26}px)`,
        }}
      >
        Get paid for thinking.
      </div>
      {f >= on + 48 ? (
        <div style={{ position: 'absolute', top: 1176, left: 0, right: 0, display: 'flex', justifyContent: 'center' }}>
          <div
            style={{
              background: C.white,
              color: C.blue,
              fontFamily: FONT.inter,
              fontWeight: 700,
              fontSize: 40,
              padding: '26px 64px',
              borderRadius: 999,
              transform: `scale(${btn})`,
            }}
          >
            Sell an idea
          </div>
        </div>
      ) : null}
    </div>
  );
};
