/** Render entry: deterministic, no clock. The renderer calls setTime(t). */
import { build, render, css } from "./stage.js";
import { film } from "./timeline.js";

const style = document.createElement("style");
style.textContent = css;
document.head.append(style);

build(document.getElementById("root")!);
render(film, 0);

declare global { interface Window { setTime(t: number): void; ready: boolean } }
window.setTime = (t: number) => render(film, t);

document.fonts.ready.then(() => { window.ready = true; });
