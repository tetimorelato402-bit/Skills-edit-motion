import React from 'react';
import {C, LAYOUT} from '../theme';

/**
 * A grey square. 340x340, centred horizontally, its centre on the 1/3 line.
 *
 * It is deliberately the least interesting object available. If a plain grey
 * rectangle can be made to feel like something, the argument is proven
 * absolutely — anything more interesting would be doing secret work.
 *
 * Both acts render this same component at this same size and position; only
 * `opacity`, `dy` and `scale` differ, and that is the whole film.
 */
export const Square: React.FC<{
  opacity: number;
  /** vertical offset from the resting position, px */
  dy?: number;
  scale?: number;
}> = ({opacity, dy = 0, scale = 1}) => (
  <div
    style={{
      position: 'absolute',
      top: LAYOUT.SQUARE_TOP,
      left: '50%',
      width: LAYOUT.SQUARE,
      height: LAYOUT.SQUARE,
      marginLeft: -LAYOUT.SQUARE / 2,
      background: C.GREY,
      opacity,
      transform: `translateY(${dy}px) scale(${scale})`,
      willChange: 'transform, opacity',
    }}
  />
);
