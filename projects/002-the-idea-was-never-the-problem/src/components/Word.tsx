import React from 'react';
import {C, LAYOUT, TYPE} from '../theme';

/**
 * One word of the sentence, on its own line, centred.
 *
 * The component is deliberately dumb — it owns no timing and no curve. Both
 * acts drive it with the same four props, so any difference the viewer sees
 * between Act I and Act II came from the timeline, never from the type.
 */
export const Word: React.FC<{
  text: string;
  index: number;
  opacity: number;
  /** px; positive is below the resting line */
  dy?: number;
  blur?: number;
  color?: string;
}> = ({text, index, opacity, dy = 0, blur = 0, color = C.UMBER}) => (
  <div
    style={{
      position: 'absolute',
      top: LAYOUT.TEXT_TOP + index * LAYOUT.LINE_STEP,
      left: 0,
      width: '100%',
      textAlign: 'center',
      ...TYPE.DISPLAY,
      color,
      opacity,
      transform: `translateY(${dy}px)`,
      filter: blur > 0 ? `blur(${blur}px)` : 'none',
      willChange: 'transform, opacity',
    }}
  >
    {text}
  </div>
);
