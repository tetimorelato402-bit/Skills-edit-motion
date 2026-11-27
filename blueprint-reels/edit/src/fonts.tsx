import React from 'react';
import { continueRender, delayRender, staticFile } from 'remotion';

const faces: [string, number, string][] = [
  ['Inter', 400, 'inter-latin-400-normal.woff2'],
  ['Inter', 500, 'inter-latin-500-normal.woff2'],
  ['Inter', 600, 'inter-latin-600-normal.woff2'],
  ['Inter', 700, 'inter-latin-700-normal.woff2'],
  ['Inter', 800, 'inter-latin-800-normal.woff2'],
  ['Newsreader', 600, 'newsreader-latin-600-normal.woff2'],
  ['Caveat', 600, 'caveat-latin-600-normal.woff2'],
];

let loaded: Promise<void> | null = null;
const loadAll = () => {
  if (!loaded) {
    loaded = Promise.all(
      faces.map(async ([family, weight, file]) => {
        const f = new FontFace(family, `url(${staticFile('fonts/' + file)}) format('woff2')`, { weight: String(weight) });
        await f.load();
        (document.fonts as unknown as { add: (f: FontFace) => void }).add(f);
      }),
    ).then(() => undefined);
  }
  return loaded;
};

/** Wrap every composition in this so text never renders in a fallback font. */
export const Fonts: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [handle] = React.useState(() => delayRender('fonts'));
  React.useEffect(() => {
    loadAll().then(() => continueRender(handle));
  }, [handle]);
  return <>{children}</>;
};
