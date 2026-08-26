/** Render entry: deterministic, no clock. The renderer calls setTime(t). */
import { build, render, css } from "./stage.js";
import { film, type Format } from "./timeline.js";

const style = document.createElement("style");
style.textContent = css;
document.head.append(style);

const format = (new URLSearchParams(location.search).get("format") ?? "vertical") as Format;
build(document.getElementById("root")!, format);
render(film, 0);

declare global { interface Window { setTime(t: number): void; ready: boolean } }
window.setTime = (t: number) => render(film, t);

document.fonts.ready.then(() => { window.ready = true; });
