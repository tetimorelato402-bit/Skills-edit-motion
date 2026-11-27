import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { C, FONT, PRICE } from '../theme';

/**
 * The generic, UNBRANDED app (BRIEF 7.1). No app name, logo or wordmark anywhere.
 * Every screen reads its own local frame (wrap in <Sequence from=…>).
 */

export type Idea = { name: string; pitch: string; handle: string };
export const IDEAS: Record<string, Idea> = {
  larder: { name: 'Larder Ring', pitch: "A swap shelf for neighbors' spare pantry items", handle: '@lowlampnotes' },
  stillroom: { name: 'Stillroom Hours', pitch: 'A quiet room you can book by the hour', handle: '@quietfern' },
  hallway: { name: 'Hallway Gym', pitch: 'A fold-down workout rack for studio apartments', handle: '@theoideas' },
  flatfold: { name: 'Flatfold Cart', pitch: 'A laundry cart that folds flat for tiny apartments', handle: '@tidewren' },
};

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const useSpring = (at: number, cfg = { damping: 12, stiffness: 200, mass: 0.6 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: f - at, fps, config: cfg });
};

// ---------------------------------------------------------------- icons (drawn, generic)
export const LockIcon: React.FC<{ size?: number; color?: string }> = ({ size = 30, color = C.navy }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <rect x="4" y="10.5" width="16" height="11" rx="3" fill={color} />
    <path d="M7.5 10.5 V7.5 a4.5 4.5 0 0 1 9 0 V10.5" stroke={color} strokeWidth="2.4" fill="none" />
  </svg>
);
export const CheckIcon: React.FC<{ size?: number; k?: number }> = ({ size = 44, k = 1 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="11" fill={C.blue} />
    <path d="M6.5 12.5 L10.3 16.2 L17.6 8.4" stroke={C.white} strokeWidth="2.6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="20" strokeDashoffset={20 * (1 - k)} />
  </svg>
);
const FingerprintIcon: React.FC<{ size?: number; color?: string }> = ({ size = 64, color = C.blue }) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth="2.6" strokeLinecap="round">
    {[6, 10, 14, 18].map((r, i) => (
      <path key={i} d={`M${24 - r} ${30 + i} a${r} ${r + 2} 0 0 1 ${r * 2} 0`} />
    ))}
    <path d="M24 20 V40" />
  </svg>
);

// ---------------------------------------------------------------- shell + pieces
export const AppShell: React.FC<{ title: string; back?: boolean; children: React.ReactNode; bg?: string }> = ({ title, back = true, children, bg = C.sky }) => (
  <div style={{ position: 'absolute', inset: 0, background: bg, fontFamily: FONT.inter, color: C.navy, overflow: 'hidden' }}>
    <div style={{ position: 'absolute', top: 120, left: 72, right: 72, display: 'flex', alignItems: 'center', gap: 26 }}>
      {back ? (
        <svg width="28" height="46" viewBox="0 0 30 48">
          <path d="M24 4 L6 24 L24 44" stroke={C.navy} strokeWidth="5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      ) : null}
      <div style={{ fontWeight: 700, fontSize: 52, letterSpacing: -0.5 }}>{title}</div>
    </div>
    <div style={{ position: 'absolute', top: 250, left: 72, right: 72 }}>{children}</div>
  </div>
);

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: C.white, borderRadius: 24, padding: 44, boxShadow: '0 8px 30px rgba(10,20,70,0.08)', ...style }}>{children}</div>
);

export const Pill: React.FC<{ text: string; variant: 'review' | 'live' | 'sold' | 'example' | 'soft'; scale?: number }> = ({ text, variant, scale = 1 }) => {
  const st: Record<string, React.CSSProperties> = {
    review: { background: '#FFF4D6', color: '#7A5A00' },
    live: { background: C.blue, color: C.white },
    sold: { background: C.yellow, color: C.navy },
    example: { background: C.sky, color: C.inkSoft, fontSize: 22, padding: '6px 14px' },
    soft: { background: C.sky, color: C.navy },
  };
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 10,
        fontWeight: 700,
        fontSize: 28,
        padding: '10px 22px',
        borderRadius: 999,
        transform: `scale(${scale})`,
        ...st[variant],
      }}
    >
      {variant === 'live' ? <span style={{ width: 12, height: 12, borderRadius: 6, background: C.yellow }} /> : null}
      {text}
    </span>
  );
};

export const ExampleTag = () => <Pill text="Example idea" variant="example" />;

export const IdeaCard: React.FC<{ idea: Idea; showPrice?: boolean; showSeller?: boolean; status?: React.ReactNode; style?: React.CSSProperties }> = ({
  idea,
  showPrice,
  showSeller,
  status,
  style,
}) => (
  <Card style={style}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
      <ExampleTag />
      {status}
    </div>
    <div style={{ fontWeight: 800, fontSize: 56, letterSpacing: -1 }}>{idea.name}</div>
    <div style={{ fontWeight: 400, fontSize: 34, lineHeight: 1.35, color: '#2A3366', marginTop: 12 }}>{idea.pitch}</div>
    {showPrice || showSeller ? (
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 30, fontSize: 28, color: C.inkSoft, fontWeight: 500 }}>
        <span>{showSeller ? idea.handle : ''}</span>
        <span>{showPrice ? PRICE : ''}</span>
      </div>
    ) : null}
  </Card>
);

export const PrimaryButton: React.FC<{ text: string; pressAt?: number }> = ({ text, pressAt }) => {
  const f = useCurrentFrame();
  const press = pressAt === undefined ? 0 : interpolate(f - pressAt, [-2, 0, 4], [0, 1, 0], clamp);
  const ripple = pressAt === undefined ? 0 : interpolate(f - pressAt, [0, 12], [0, 1], clamp);
  return (
    <div
      style={{
        position: 'relative',
        overflow: 'hidden',
        background: C.blue,
        color: C.white,
        fontWeight: 600,
        fontSize: 40,
        textAlign: 'center',
        padding: '34px 0',
        borderRadius: 28,
        transform: `scale(${1 - 0.05 * press})`,
      }}
    >
      {pressAt !== undefined && f >= pressAt ? (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            width: 900 * ripple,
            height: 900 * ripple,
            marginLeft: -450 * ripple,
            marginTop: -450 * ripple,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 70%)',
            opacity: 1 - ripple,
          }}
        />
      ) : null}
      {text}
    </div>
  );
};

const Caret: React.FC = () => {
  const f = useCurrentFrame();
  return <span style={{ display: 'inline-block', width: 4, height: '1.05em', background: C.blue, marginLeft: 3, verticalAlign: '-0.15em', opacity: Math.floor(f / 8) % 2 ? 0 : 1 }} />;
};

const typed = (f: number, text: string, start: number, cps: number) => text.slice(0, Math.max(0, Math.min(text.length, Math.floor((f - start) * cps))));

// ---------------------------------------------------------------- 1. New idea form
export const NewIdeaForm: React.FC<{ what: string; who?: string; why?: string; start?: number; cps?: number }> = ({ what, who = '', why = '', start = 0, cps = 2.6 }) => {
  const f = useCurrentFrame();
  const t1 = typed(f, what, start, cps);
  const done1 = t1.length === what.length;
  const field = (label: string, value: string, active: boolean) => (
    <div style={{ marginBottom: 34 }}>
      <div style={{ fontWeight: 600, fontSize: 30, color: C.inkSoft, marginBottom: 12 }}>{label}</div>
      <div
        style={{
          background: C.white,
          border: `3px solid ${active ? C.blue : '#D5DBF5'}`,
          borderRadius: 24,
          padding: '28px 30px',
          minHeight: 70,
          fontSize: 38,
          lineHeight: 1.35,
          fontWeight: 500,
        }}
      >
        {value}
        {active ? <Caret /> : null}
      </div>
    </div>
  );
  return (
    <AppShell title="New idea">
      {field('What it is', t1, !done1 || (!who && !why))}
      {field("Who it's for", who, false)}
      {field('Why it matters', why, false)}
      <div style={{ marginTop: 24 }}>
        <PrimaryButton text="Continue" />
      </div>
    </AppShell>
  );
};

// ---------------------------------------------------------------- 2. Fingerprint stamp
export const FingerprintStamp: React.FC<{ idea: Idea; at?: number; date?: string }> = ({ idea, at = 4, date = 'Nov 26, 2026' }) => {
  const f = useCurrentFrame();
  const k = interpolate(f - at, [0, 4], [0, 1], clamp);
  const shake = f >= at + 4 && f < at + 8 ? Math.sin((f - at) * 3) * 4 : 0;
  return (
    <AppShell title="Your idea">
      <div style={{ transform: `translateY(${shake}px)` }}>
        <IdeaCard idea={idea} />
      </div>
      {f >= at ? (
        <div
          style={{
            marginTop: 50,
            display: 'flex',
            justifyContent: 'center',
            opacity: k,
            transform: `scale(${2.2 - 1.2 * k}) rotate(-6deg)`,
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 22,
              border: `6px solid ${C.blue}`,
              color: C.blue,
              borderRadius: 20,
              padding: '22px 34px',
              fontWeight: 800,
              fontSize: 40,
              background: 'rgba(255,255,255,0.6)',
            }}
          >
            <FingerprintIcon />
            Fingerprinted · {date}
          </div>
        </div>
      ) : null}
    </AppShell>
  );
};

// ---------------------------------------------------------------- 3/4. Review -> Live
export const ReviewScreen: React.FC<{ idea: Idea; checks?: [number, number]; liveAt?: number }> = ({ idea, checks = [4, 10], liveAt }) => {
  const f = useCurrentFrame();
  const live = liveAt !== undefined && f >= liveAt;
  const pop = useSpring(liveAt ?? 9999, { damping: 8, stiffness: 260, mass: 0.5 });
  const row = (label: string, at: number) => {
    const k = interpolate(f - at, [0, 5], [0, 1], clamp);
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 22, fontSize: 36, fontWeight: 600, opacity: f >= at ? 1 : 0.25, marginTop: 26 }}>
        <CheckIcon k={k} />
        {label}
      </div>
    );
  };
  return (
    <AppShell title="Your idea">
      <IdeaCard
        idea={idea}
        status={live ? <Pill text="Live" variant="live" scale={0.6 + 0.4 * pop} /> : <Pill text="In review" variant="review" />}
      />
      <Card style={{ marginTop: 34 }}>
        {row('Reviewed', checks[0])}
        {row('Compared with every other idea', checks[1])}
      </Card>
    </AppShell>
  );
};

// ---------------------------------------------------------------- 5. Search (buyer side)
export const SearchScreen: React.FC<{ idea: Idea; query: string; start?: number; cardAt?: number }> = ({ idea, query, start = 2, cardAt }) => {
  const f = useCurrentFrame();
  const q = typed(f, query, start, 0.6);
  const at = cardAt ?? start + Math.ceil(query.length / 0.6) + 3;
  const s = useSpring(at);
  return (
    <AppShell title="Search" back={false}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 22,
          background: C.white,
          border: `3px solid ${C.blue}`,
          borderRadius: 999,
          padding: '26px 36px',
          fontSize: 40,
          fontWeight: 500,
        }}
      >
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={C.inkSoft} strokeWidth="2.6" strokeLinecap="round">
          <circle cx="10.5" cy="10.5" r="7" />
          <path d="M16 16 L21 21" />
        </svg>
        <span>
          {q}
          <Caret />
        </span>
      </div>
      {f >= at ? (
        <div style={{ marginTop: 40, opacity: Math.min(1, s * 1.4), transform: `translateY(${(1 - s) * 40}px)` }}>
          <IdeaCard idea={idea} showPrice showSeller />
        </div>
      ) : null}
    </AppShell>
  );
};

// ---------------------------------------------------------------- 6/7. NDA + Buy
export const HeldChip: React.FC<{ k?: number }> = ({ k = 1 }) => (
  <div
    style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 14,
      background: C.white,
      border: `2px solid #D5DBF5`,
      borderRadius: 999,
      padding: '16px 28px',
      fontSize: 30,
      fontWeight: 600,
      color: C.navy,
      opacity: k,
      transform: `translateX(${(1 - k) * 60}px)`,
    }}
  >
    <LockIcon />
    Payment held until handover
  </div>
);

export const NdaScreen: React.FC<{ idea: Idea; signer?: string; signStart?: number; signFrames?: number; buyAt?: number; chipAt?: number }> = ({
  idea,
  signer = 'Rosa M.',
  signStart = 2,
  signFrames = 14,
  buyAt,
  chipAt,
}) => {
  const f = useCurrentFrame();
  const sk = interpolate(f - signStart, [0, signFrames], [0, 1], clamp);
  const ck = chipAt === undefined ? 0 : interpolate(f - chipAt, [0, 6], [0, 1], clamp);
  return (
    <AppShell title="Read the full idea">
      <Card>
        <div style={{ fontWeight: 800, fontSize: 44 }}>Non-disclosure agreement</div>
        <div style={{ fontSize: 30, lineHeight: 1.5, color: '#2A3366', marginTop: 18 }}>
          You agree to keep <b>{idea.name}</b> confidential. Sign to read the full idea.
        </div>
        {[0.95, 0.88, 0.7].map((w, i) => (
          <div key={i} style={{ height: 16, width: `${w * 100}%`, background: '#E6E9F7', borderRadius: 8, marginTop: 18 }} />
        ))}
        <div style={{ marginTop: 40, position: 'relative', height: 120, borderBottom: `3px solid ${C.navy}` }}>
          <div
            style={{
              position: 'absolute',
              left: 10,
              bottom: 6,
              fontFamily: FONT.caveat,
              fontWeight: 600,
              fontSize: 96,
              color: C.blue,
              clipPath: `inset(0 ${100 - sk * 100}% 0 0)`,
              whiteSpace: 'nowrap',
            }}
          >
            {signer}
          </div>
        </div>
        <div style={{ fontSize: 24, color: C.inkSoft, marginTop: 10 }}>Signature</div>
      </Card>
      <div style={{ marginTop: 40 }}>
        <PrimaryButton text="Buy this idea" pressAt={buyAt} />
      </div>
      {chipAt !== undefined && f >= chipAt ? (
        <div style={{ marginTop: 30, display: 'flex', justifyContent: 'center' }}>
          <HeldChip k={ck} />
        </div>
      ) : null}
    </AppShell>
  );
};

// ---------------------------------------------------------------- 8. Sold
export const SoldScreen: React.FC<{ idea: Idea; at?: number }> = ({ idea, at = 0 }) => {
  const f = useCurrentFrame();
  const s = useSpring(at, { damping: 9, stiffness: 240, mass: 0.6 });
  const glow = interpolate(f - at, [0, 3, 18], [0, 1, 0.35], clamp);
  return (
    <div style={{ position: 'absolute', inset: 0, background: C.navy, fontFamily: FONT.inter, overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute',
          left: 540 - 700,
          top: 760 - 700,
          width: 1400,
          height: 1400,
          borderRadius: '50%',
          background: `radial-gradient(circle, rgba(246,226,122,${0.55 * glow}) 0%, rgba(246,226,122,0) 60%)`,
        }}
      />
      <div style={{ position: 'absolute', top: 300, left: 108, right: 108, textAlign: 'center', color: C.white }}>
        <div style={{ display: 'inline-block' }}>
          <ExampleTag />
        </div>
        <div style={{ fontWeight: 700, fontSize: 48, marginTop: 24 }}>{idea.name}</div>
      </div>
      <div
        style={{
          position: 'absolute',
          top: 560,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontWeight: 800,
          fontSize: 230,
          letterSpacing: -6,
          color: C.yellow,
          transform: `scale(${0.4 + 0.6 * s})`,
        }}
      >
        Sold
      </div>
      <div style={{ position: 'absolute', top: 900, left: 0, right: 0, display: 'flex', justifyContent: 'center' }}>
        <HeldChip k={interpolate(f - at, [4, 10], [0, 1], clamp)} />
      </div>
      <div
        style={{
          position: 'absolute',
          top: 1020,
          left: 0,
          right: 0,
          textAlign: 'center',
          color: C.white,
          fontWeight: 600,
          fontSize: 38,
          opacity: interpolate(f - at, [6, 12], [0, 1], clamp),
        }}
      >
        Sold once. One owner.
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- 9. Call frame
const RoundBtn: React.FC<{ bg: string; children: React.ReactNode }> = ({ bg, children }) => (
  <div style={{ width: 120, height: 120, borderRadius: 60, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{children}</div>
);
export const CallFrame: React.FC<{ main: React.ReactNode; self: React.ReactNode; label?: string }> = ({ main, self, label = 'Handover call' }) => (
  <div style={{ position: 'absolute', inset: 0, background: '#070B22', fontFamily: FONT.inter }}>
    <div style={{ position: 'absolute', top: 120, left: 0, right: 0, textAlign: 'center', color: C.white, fontWeight: 600, fontSize: 34, opacity: 0.9 }}>{label}</div>
    <div style={{ position: 'absolute', top: 200, left: 40, right: 40, height: 1180, borderRadius: 40, overflow: 'hidden', background: '#111733' }}>{main}</div>
    <div
      style={{
        position: 'absolute',
        top: 1010,
        right: 80,
        width: 300,
        height: 400,
        borderRadius: 28,
        overflow: 'hidden',
        background: '#1A2040',
        border: '4px solid rgba(255,255,255,0.85)',
        boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
      }}
    >
      {self}
    </div>
    <div style={{ position: 'absolute', top: 1460, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 50 }}>
      <RoundBtn bg="rgba(255,255,255,0.16)">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round">
          <rect x="9" y="3" width="6" height="11" rx="3" />
          <path d="M5.5 11 a6.5 6.5 0 0 0 13 0 M12 17.5 V21" />
        </svg>
      </RoundBtn>
      <RoundBtn bg="rgba(255,255,255,0.16)">
        <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinejoin="round">
          <rect x="3" y="6.5" width="12.5" height="11" rx="2.5" />
          <path d="M15.5 10.5 L21 7.5 V16.5 L15.5 13.5 Z" />
        </svg>
      </RoundBtn>
      <RoundBtn bg={C.coral}>
        <svg width="56" height="56" viewBox="0 0 24 24" fill="#fff">
          <path d="M3 14.2 c5-4.3 13-4.3 18 0 l-2 2.6 c-.4.5-1.1.6-1.6.2 l-1.9-1.5 c-.4-.3-.6-.8-.5-1.3 l.3-1.4 c-2.1-.7-4.5-.7-6.6 0 l.3 1.4 c.1.5-.1 1-.5 1.3 l-1.9 1.5 c-.5.4-1.2.3-1.6-.2 Z" />
        </svg>
      </RoundBtn>
    </div>
  </div>
);

/** Placeholder tile for AI clips that do not exist yet (so rough cuts can be timed now). */
export const Placeholder: React.FC<{ label: string; tone?: string }> = ({ label, tone = '#18204A' }) => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      background: `linear-gradient(160deg, ${tone}, #070B22)`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      textAlign: 'center',
      color: 'rgba(255,255,255,0.55)',
      fontFamily: FONT.inter,
      fontWeight: 600,
      fontSize: 34,
      padding: 40,
      boxSizing: 'border-box',
    }}
  >
    {label}
  </div>
);
