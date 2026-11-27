import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { C, FONT, SAFE } from '../theme';

/**
 * Hook caption (BRIEF 4.5): Newsreader 600, Idea Yellow, soft dark shadow, centered,
 * max two lines, ~68 px, top of the block at y 700. Optional extra line (e.g. "…and then you sell it").
 */
export const HookCaption: React.FC<{ text: string; extra?: string; extraFrom?: number; from?: number; to?: number }> = ({
  text,
  extra,
  extraFrom = 0,
  from = 0,
  to = Infinity,
}) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const extraOn = extra && f >= extraFrom;
  const extraK = extraOn ? interpolate(f - extraFrom, [0, 4], [0, 1], { extrapolateRight: 'clamp' }) : 0;
  return (
    <div
      style={{
        position: 'absolute',
        top: 700,
        left: SAFE.left,
        width: SAFE.right - SAFE.left,
        textAlign: 'center',
        fontFamily: FONT.news,
        fontWeight: 600,
        fontSize: 64, // 64 keeps every hook within two lines at the safe-zone width (measured)
        lineHeight: 1.12,
        color: C.yellow,
        textShadow: '0 3px 12px rgba(10,20,70,0.55)',
      }}
    >
      <div>{text}</div>
      {extraOn ? <div style={{ opacity: extraK, transform: `translateY(${(1 - extraK) * 10}px)` }}>{extra}</div> : null}
    </div>
  );
};

/** Dialogue subtitle pill (BRIEF 4.5): Inter 600 white 44 px, navy pill, y ~1180-1300. */
export const Subtitle: React.FC<{ text: string; from: number; to: number; y?: number; italic?: boolean }> = ({
  text,
  from,
  to,
  y = 1200,
  italic,
}) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const k = interpolate(f - from, [0, 3], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <div style={{ position: 'absolute', top: y, left: SAFE.left, width: SAFE.right - SAFE.left, display: 'flex', justifyContent: 'center' }}>
      <div
        style={{
          opacity: k,
          transform: `scale(${0.96 + 0.04 * k})`,
          background: 'rgba(10,20,70,0.72)',
          color: C.white,
          fontFamily: FONT.inter,
          fontWeight: 600,
          fontStyle: italic ? 'italic' : 'normal',
          fontSize: 44,
          lineHeight: 1.25,
          padding: '14px 30px',
          borderRadius: 40,
          textAlign: 'center',
          maxWidth: SAFE.right - SAFE.left,
        }}
      >
        {text}
      </div>
    </div>
  );
};

/** "Later." / "Next family dinner." card (BRIEF 7.3): Night Navy full frame, Inter 700 white. */
export const TitleCard: React.FC<{ text: string }> = ({ text }) => {
  const f = useCurrentFrame();
  const k = interpolate(f, [0, 5], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <div style={{ position: 'absolute', inset: 0, background: C.navy, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div
        style={{
          fontFamily: FONT.inter,
          fontWeight: 700,
          fontSize: 96,
          color: C.white,
          letterSpacing: -1,
          opacity: k,
          transform: `translateY(${(1 - k) * 18}px)`,
        }}
      >
        {text}
      </div>
    </div>
  );
};
