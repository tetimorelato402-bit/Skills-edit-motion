/** The container ships Chromium 1194; playwright 1.62 wants 1234. Use what's here. */
export const CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
export const LAUNCH = {
  executablePath: CHROME,
  args: ["--force-color-profile=srgb", "--font-render-hinting=none",
         "--hide-scrollbars", "--disable-lcd-text"],
};
