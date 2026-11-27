import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { C, FONT } from '../theme';

/**
 * Generic dark group chat (BRIEF 7.2). Deliberately not any real app: plain header,
 * initials avatars, rounded bubbles, Jordan's bubbles in Blueprint Blue.
 */
export type Member = { id: string; name: string; color: string };
export type ChatMsg = {
  at: number; // frame the bubble pops in
  from: string; // member id; 'me' = outgoing
  text?: string;
  sticker?: string; // big emoji sticker
  attachment?: React.ReactNode; // e.g. a screenshot thumbnail
};

export const COUNCIL: Member[] = [
  { id: 'me', name: 'Jordan', color: C.blue },
  { id: 'tay', name: 'Tay', color: '#B45CFF' },
  { id: 'marcus', name: 'Marcus', color: '#20B486' },
  { id: 'priya', name: 'Priya', color: '#FF8A3D' },
];

const Avatar: React.FC<{ m: Member; size?: number }> = ({ m, size = 64 }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size / 2,
      background: m.color,
      color: C.white,
      fontFamily: FONT.inter,
      fontWeight: 700,
      fontSize: size * 0.42,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
    }}
  >
    {m.name[0]}
  </div>
);

const Bubble: React.FC<{ msg: ChatMsg; members: Member[]; showName: boolean }> = ({ msg, members, showName }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: f - msg.at, fps, config: { damping: 14, stiffness: 220, mass: 0.6 } });
  const me = msg.from === 'me';
  const m = members.find((x) => x.id === msg.from)!;
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: me ? 'row-reverse' : 'row',
        alignItems: 'flex-end',
        gap: 16,
        transform: `scale(${0.7 + 0.3 * s}) translateY(${(1 - s) * 30}px)`,
        transformOrigin: me ? 'right bottom' : 'left bottom',
        opacity: Math.min(1, s * 1.5),
      }}
    >
      {!me ? <Avatar m={m} /> : null}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: me ? 'flex-end' : 'flex-start', maxWidth: 700 }}>
        {showName && !me ? (
          <div style={{ fontFamily: FONT.inter, fontWeight: 600, fontSize: 26, color: m.color, margin: '0 0 6px 18px', filter: 'brightness(1.3)' }}>{m.name}</div>
        ) : null}
        {msg.sticker ? (
          <div style={{ fontSize: 150, lineHeight: 1 }}>{msg.sticker}</div>
        ) : msg.attachment ? (
          <div style={{ borderRadius: 22, overflow: 'hidden', border: `4px solid ${me ? C.blue : C.chatIn}` }}>{msg.attachment}</div>
        ) : (
          <div
            style={{
              background: me ? C.blue : C.chatIn,
              color: C.white,
              fontFamily: FONT.inter,
              fontWeight: 500,
              fontSize: 34,
              lineHeight: 1.3,
              padding: '18px 26px',
              borderRadius: 22,
              borderBottomRightRadius: me ? 6 : 22,
              borderBottomLeftRadius: me ? 22 : 6,
            }}
          >
            {msg.text}
          </div>
        )}
      </div>
    </div>
  );
};

export const TypingDots: React.FC<{ color?: string }> = ({ color = '#9AA0B8' }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ display: 'inline-flex', gap: 10, background: C.chatIn, padding: '22px 26px', borderRadius: 22, borderBottomLeftRadius: 6 }}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            width: 14,
            height: 14,
            borderRadius: 7,
            background: color,
            opacity: 0.4 + 0.6 * Math.max(0, Math.sin((f / 30) * Math.PI * 2 * 1.6 - i * 0.9)),
          }}
        />
      ))}
    </div>
  );
};

/**
 * Full-screen chat. Messages appear at their `at` frame; the list is bottom-anchored so new
 * bubbles push older ones up (the "scroll" with a light whoosh in the mix).
 */
export const ChatScreen: React.FC<{
  title?: string;
  members?: Member[];
  messages: ChatMsg[];
  typing?: { from: string; start: number; end: number }[];
}> = ({ title = 'the council 💀', members = COUNCIL, messages, typing = [] }) => {
  const f = useCurrentFrame();
  const visible = messages.filter((m) => f >= m.at);
  const typers = typing.filter((t) => f >= t.start && f < t.end);
  return (
    <div style={{ position: 'absolute', inset: 0, background: C.chatBg, overflow: 'hidden' }}>
      {/* header */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 250,
          paddingTop: 110,
          background: 'rgba(18,20,32,0.96)',
          borderBottom: '1px solid #1C2032',
          display: 'flex',
          alignItems: 'center',
          gap: 22,
          paddingLeft: 60,
          zIndex: 2,
          boxSizing: 'border-box',
        }}
      >
        <svg width="30" height="48" viewBox="0 0 30 48">
          <path d="M24 4 L6 24 L24 44" stroke={C.white} strokeWidth="5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <div style={{ display: 'flex' }}>
          {members.slice(1).map((m, i) => (
            <div key={m.id} style={{ marginLeft: i ? -18 : 0, border: `3px solid ${C.chatBg}`, borderRadius: 40 }}>
              <Avatar m={m} size={62} />
            </div>
          ))}
        </div>
        <div>
          <div style={{ fontFamily: FONT.inter, fontWeight: 700, fontSize: 38, color: C.white }}>{title}</div>
          <div style={{ fontFamily: FONT.inter, fontWeight: 500, fontSize: 24, color: '#8A90A8' }}>{members.length} members</div>
        </div>
      </div>
      {/* message list, bottom anchored above the safe zone */}
      <div
        style={{
          position: 'absolute',
          left: 56,
          right: 56,
          bottom: 1920 - 1420,
          display: 'flex',
          flexDirection: 'column',
          gap: 22,
        }}
      >
        {visible.map((m, i) => (
          <Bubble key={i} msg={m} members={members} showName={i === 0 || visible[i - 1].from !== m.from} />
        ))}
        {typers.map((t, i) => (
          <div key={'t' + i} style={{ display: 'flex', gap: 16, alignItems: 'flex-end' }}>
            <Avatar m={members.find((x) => x.id === t.from)!} />
            <TypingDots />
          </div>
        ))}
      </div>
      {/* composer */}
      <div
        style={{
          position: 'absolute',
          left: 40,
          right: 40,
          top: 1460,
          height: 96,
          borderRadius: 48,
          background: '#171A28',
          border: '1px solid #262A3A',
          display: 'flex',
          alignItems: 'center',
          paddingLeft: 40,
          fontFamily: FONT.inter,
          fontSize: 32,
          color: '#5C627A',
        }}
      >
        Message
      </div>
    </div>
  );
};

/** Floating single bubble used over AI shots (F01-S02..S05). */
export const FloatingBubble: React.FC<{ text: string; at: number; from: string; x?: number; y?: number; members?: Member[] }> = ({
  text,
  at,
  from,
  x = 108,
  y = 1040,
  members = COUNCIL,
}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  return (
    <div style={{ position: 'absolute', left: x, top: y, filter: 'drop-shadow(0 10px 24px rgba(0,0,0,0.45))' }}>
      <Bubble msg={{ at, from, text }} members={members} showName />
    </div>
  );
};

export const typingK = (f: number, start: number, len: number, cps = 2.2) =>
  Math.max(0, Math.min(len, Math.floor((f - start) * cps)));

export const fadeIn = (f: number, at: number, d = 6) => interpolate(f - at, [0, d], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
