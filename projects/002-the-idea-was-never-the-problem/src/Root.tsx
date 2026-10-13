import React from 'react';
import {Composition} from 'remotion';
import {FPS, HEIGHT, WIDTH} from './grid';
import {ACT_I_DURATION, ActI} from './ActI';

/**
 * Only Act I is registered. The brief's stop gate: build Act I, render it, and
 * stop — if Act I does not read as lifeless, the film has no argument and
 * everything built on top of it is wasted.
 */
export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="ActI"
      component={ActI}
      durationInFrames={ACT_I_DURATION}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  </>
);
