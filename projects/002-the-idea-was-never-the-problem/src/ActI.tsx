import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {A1, ACT_I_DURATION} from './timeline';
import {C, SENTENCE} from './theme';
import {Eyebrow} from './components/Eyebrow';
import {Square} from './components/Square';
import {Word} from './components/Word';
import {TextureLayer} from './components/TextureLayer';
import './fonts';

export {ACT_I_DURATION};

/**
 * ACT I — DEAD.  bars 1–3, frames 0–480, 0.00–8.00s.
 *
 * This act is the hardest thing in the film to get right, and getting it right
 * means resisting every instinct. It must read as LIFELESS, not as broken and
 * not as funny. Comedy would let the viewer off the hook; a visible bug would
 * give them something to blame. What has to land is the quiet, plausible
 * deadness of a thing they have made themselves and not noticed.
 *
 * So: nothing here is wrong. The square is correctly placed. The sentence is
 * correctly spelled. The margins are right, the colour is right, the type is
 * right. Every single thing that a checklist would catch has been done.
 *
 * The rules, all seven, and none of them may be softened:
 *
 *   1. Linear easing on everything. There is no Easing import in this file and
 *      there must never be one — verify.mjs fails the build if one appears.
 *   2. No anticipation, no follow-through. Objects start at full speed, stop dead.
 *   3. No overshoot, no settle, no weight. The square has no mass.
 *   4. Everything animates identically. The square's fade and the words' fades
 *      are the same gesture at the same rate; nothing is orchestrated, nothing
 *      makes way for anything else.
 *   5. Uniform spacing. The four words are evenly spaced in time, so there is
 *      no rhythm to hear.
 *   6. Off-grid timing. The audio ticks sit on 90 BPM; these do not. Sound and
 *      picture never agree, and the viewer feels wrong without knowing why.
 *   7. Fade in, fade out. Opacity only — the laziest transition available.
 */


/** Linear, clamped. The only interpolation this act is permitted. */
const fadeIn = (frame: number, start: number, dur: number): number =>
  interpolate(frame, [start, start + dur], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

export const ActI: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{background: C.BONE}}>
      <Eyebrow />

      <Square opacity={fadeIn(frame, A1.SQUARE, A1.SQUARE_FADE)} />

      {SENTENCE.map((text, i) => (
        <Word
          key={text}
          text={text}
          index={i}
          opacity={fadeIn(frame, A1.WORDS[i], A1.WORD_FADE)}
        />
      ))}

      {/*
        Frames 400–480: nothing happens for eighty frames. Held far too long,
        on purpose. The restlessness that builds here is the film's entire
        setup — Act II is only legible as an answer to a question the viewer
        has already started asking. Do not shorten it.
      */}

      <TextureLayer ground="bone" />
    </AbsoluteFill>
  );
};
