import React from 'react';
import {Img, staticFile, useCurrentFrame} from 'remotion';
import {TEXTURE} from '../theme';

const GRAIN_PLATES = 8;
/** plates advance every 3 frames — 20 grain updates a second, film rate */
const GRAIN_HOLD = 3;

const fill: React.CSSProperties = {
  position: 'absolute',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  objectFit: 'cover',
  pointerEvents: 'none',
};

/**
 * T1 TEXTURE PASS.
 *
 * One layer over the entire film, never per element, and never transformed with
 * the content — it sits on the lens, not on the objects. That is precisely what
 * makes it read as a printed surface rather than as a filter.
 *
 * On BONE the paper plate multiplies (paper takes light away from flat ink); on
 * UMBER it screens the inverted plate instead, so the texture lifts the blacks
 * rather than crushing them.
 */
export const TextureLayer: React.FC<{ground: 'bone' | 'umber'}> = () => {
  const frame = useCurrentFrame();
  const plate = Math.floor(frame / GRAIN_HOLD) % GRAIN_PLATES;

  return (
    /*
      No z-index and no isolation on this wrapper, deliberately. Anything that
      makes it a stacking context — a z-index, an opacity, a transform — seals
      the blend modes inside their own group, where the backdrop is transparent
      rather than the film. The plates then composite as flat grey sheets: the
      first build of this dropped the BONE ground from 196 to 160 and looked
      like fog. Texture is always the last child, so it paints on top anyway.
    */
    <div style={fill}>
      {/*
        Paper, then the fold, each as a multiply/screen pair. The pass is
        ground-agnostic by construction — on BONE the multiply side carries it,
        on UMBER the screen side does — so `ground` is no longer read here. It
        stays in the signature because the acts describe their own ground and
        that should keep being true at the call site.
      */}
      <Img
        src={staticFile('tex/paper_dark.png')}
        style={{...fill, mixBlendMode: 'multiply', opacity: TEXTURE.PAPER_DARK}}
      />
      <Img
        src={staticFile('tex/paper_light.png')}
        style={{...fill, mixBlendMode: 'screen', opacity: TEXTURE.PAPER_LIGHT}}
      />
      <Img
        src={staticFile('tex/crumple_dark.png')}
        style={{...fill, mixBlendMode: 'multiply', opacity: TEXTURE.CRUMPLE_DARK}}
      />
      <Img
        src={staticFile('tex/crumple_light.png')}
        style={{...fill, mixBlendMode: 'screen', opacity: TEXTURE.CRUMPLE_LIGHT}}
      />
      {/*
        The visible grain is a repeating background, not an <img> — a 384px
        plate has to tile to cover 1080x1920, and object-fit cannot tile.
      */}
      {Array.from({length: GRAIN_PLATES}, (_, i) => (
        <div
          key={i}
          style={{
            ...fill,
            backgroundImage: `url(${staticFile(`tex/grain${i}.png`)})`,
            backgroundRepeat: 'repeat',
            mixBlendMode: 'overlay',
            opacity: i === plate ? TEXTURE.GRAIN : 0,
          }}
        />
      ))}
      {/*
        CSS backgrounds do not go through Remotion's asset tracking, so the
        first screenshots would fire before the plates decoded and the grain
        would pop in several frames late — visible on a ground this still.
        These zero-size <Img> tags exist only to make the renderer wait.
      */}
      <div style={{position: 'absolute', width: 0, height: 0, overflow: 'hidden'}}>
        {Array.from({length: GRAIN_PLATES}, (_, i) => (
          <Img key={i} src={staticFile(`tex/grain${i}.png`)} style={{width: 1, height: 1}} />
        ))}
      </div>
    </div>
  );
};
