// Blueprint palette and type rules (BRIEF.md sections 4.3, 4.5, 7, Appendix A).
export const C = {
  blue: '#1F3DFF', // Blueprint Blue
  yellow: '#F6E27A', // Idea Yellow
  white: '#FFFFFF', // Paper White
  navy: '#0A1446', // Night Navy
  sky: '#E8ECFF', // Sky Tint
  coral: '#FF5A36', // Spark Coral
  dim: '#4E61E2', // bulb "off": 22% Idea Yellow over Blueprint Blue
  chatBg: '#0B0D16',
  chatIn: '#262A3A',
  inkSoft: '#5A6390',
};

export const FPS = 30;
export const W = 1080;
export const H = 1920;
// Text safe zone: x 108..972, above y 1440.
export const SAFE = { left: 108, right: 972, bottom: 1440 };

export const FONT = {
  inter: "'Inter', 'Noto Color Emoji', sans-serif",
  news: "'Newsreader', serif",
  caveat: "'Caveat', cursive",
};

// One fixed price, shown small and never called out (BRIEF 3). PLACEHOLDER: confirm the real price with Vanessa.
export const PRICE = '$49';
