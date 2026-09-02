import {continueRender, delayRender, staticFile} from 'remotion';

/**
 * Two faces, self-hosted. The woff2 files are committed, not fetched at render
 * time — a film that needs the network to look right is not reproducible.
 *
 * Nothing is drawn until both faces are actually parsed. Without the explicit
 * document.fonts.load, Chromium happily screenshots the first frames in a
 * fallback sans and the 180px line silently changes width.
 */
if (typeof document !== 'undefined') {
  const handle = delayRender('Loading Inter and IBM Plex Mono');
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = staticFile('fonts/fonts.css');
  link.onload = () => {
    Promise.all([
      document.fonts.load('800 180px Inter'),
      document.fonts.load('500 13px "IBM Plex Mono"'),
    ])
      .then(() => document.fonts.ready)
      .then(() => continueRender(handle));
  };
  link.onerror = () => continueRender(handle);
  document.head.appendChild(link);
}

export {};
