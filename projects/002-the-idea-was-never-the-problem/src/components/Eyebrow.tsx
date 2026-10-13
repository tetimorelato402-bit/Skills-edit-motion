import React from 'react';
import {C, EYEBROW_TEXT, LAYOUT, TYPE} from '../theme';

/**
 * Present the entire film, never animated. It is the one fixed point: the
 * viewer's eye can return to it and confirm nothing about the frame has been
 * swapped between the two acts.
 */
export const Eyebrow: React.FC<{color?: string}> = ({color = C.GREY}) => (
  <div
    style={{
      position: 'absolute',
      top: LAYOUT.EYEBROW.top,
      left: LAYOUT.EYEBROW.left,
      ...TYPE.MICRO,
      color,
      whiteSpace: 'nowrap',
    }}
  >
    {EYEBROW_TEXT}
  </div>
);
