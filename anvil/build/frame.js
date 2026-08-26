// src/motion.ts
function cubicBezier(x1, y1, x2, y2) {
  const A = (a, b) => 1 - 3 * b + 3 * a;
  const B = (a, b) => 3 * b - 6 * a;
  const C = (a) => 3 * a;
  const calc = (t, a, b) => ((A(a, b) * t + B(a, b)) * t + C(a)) * t;
  const slope = (t, a, b) => 3 * A(a, b) * t * t + 2 * B(a, b) * t + C(a);
  return (x) => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 8; i++) {
      const d = slope(t, x1, x2);
      if (d === 0) break;
      const err = calc(t, x1, x2) - x;
      if (Math.abs(err) < 1e-6) break;
      t -= err / d;
    }
    return calc(t, y1, y2);
  };
}
var ease = cubicBezier(0.22, 1, 0.36, 1);
var easeCamera = cubicBezier(0.42, 0, 0.22, 1);
var clamp01 = (v) => v < 0 ? 0 : v > 1 ? 1 : v;
var lerp = (a, b, p) => a + (b - a) * p;
var progress = (t, at, dur) => dur <= 0 ? t >= at ? 1 : 0 : clamp01((t - at) / dur);
function drift(t, phase, amp, p1 = 8.3, p2 = 13.7) {
  return amp * (0.62 * Math.sin(2 * Math.PI * t / p1 + phase) + 0.38 * Math.sin(2 * Math.PI * t / p2 + phase * 1.7));
}
var REST = {
  opacity: 1,
  x: 0,
  y: 0,
  scale: 1,
  z: 0,
  lift: 1,
  reveal: 1
};
var HIDDEN = { ...REST, opacity: 0 };
var FOCUS_REST = { x: 215, y: 466, radius: 1200, blur: 0 };
var CAMERA_REST = { scale: 1, fx: 215, fy: 466, center: 0 };
function settleIn(p) {
  const e = ease(p);
  const overshoot = Math.sin(Math.PI * clamp01((p - 0.55) / 0.45)) * 6e-3;
  return {
    opacity: ease(clamp01(p / 0.45)),
    scale: lerp(1.04, 1, e) - overshoot,
    lift: e
  };
}
function revealUp(p, { distance = 24, from = "below" } = {}) {
  const e = ease(p);
  const dir = from === "below" ? 1 : -1;
  return {
    opacity: ease(clamp01(p / 0.35)),
    y: lerp(distance * dir, 0, e),
    reveal: e
  };
}
function crossDepth(p, { depth = 220, aperture = false } = {}) {
  const e = ease(p);
  if (aperture) {
    const still = { opacity: 1, z: 0, lift: 1 };
    return { out: still, in: { ...still } };
  }
  return {
    // The outgoing screen holds full opacity until the incoming one covers
    // it. Fading both at once shows the stage through the middle of every
    // transition and washes the picture out — a light screen becoming a dark
    // one goes grey. It recedes in z the whole time; only its cover changes.
    // Opacity is eased like everything else. A linear ramp holds the incoming
    // screen near half-transparent through the middle of the beat, which is
    // what turns a dissolve into a double exposure; eased, it is effectively
    // opaque two frames in and the rest of the beat is depth, not blending.
    // The incoming screen resolves in the first quarter of the beat. Two
    // text-dense screens held at half opacity against each other read as a
    // double exposure, not as depth; the cover has to happen fast and the
    // rest of the duration is the new screen settling forward. The outgoing
    // one only starts fading once it is already hidden underneath.
    out: {
      opacity: 1 - ease(clamp01((p - 0.35) / 0.35)),
      z: lerp(0, -depth, e),
      lift: 1 - e
    },
    in: {
      opacity: aperture ? 1 : ease(clamp01(p / 0.3)),
      z: lerp(depth * 0.5, 0, e),
      lift: e
    }
  };
}
function recede(p, { depth = 520 } = {}) {
  const e = easeCamera(p);
  return { opacity: 1 - e, z: lerp(0, -depth, e), lift: 1 - e };
}
function apertureOpen(p, radius) {
  return radius * easeCamera(p);
}
function focusPush(p, from, to) {
  const e = easeCamera(p);
  return {
    scale: lerp(from.scale, to.scale, e),
    fx: lerp(from.fx, to.fx, e),
    fy: lerp(from.fy, to.fy, e),
    center: lerp(from.center, to.center ?? 1, e)
  };
}
function cameraTransform(c, t = 0, w = 430, h = 932) {
  const bx = drift(t, 0, 2, 11.3, 17.9);
  const by = drift(t, 1.9, 3.4, 9.7, 15.1);
  const bs = 1 + drift(t, 3.4, 45e-4, 12.9, 20.3);
  const dx = -c.scale * (c.fx - w / 2) * c.center + bx;
  const dy = -c.scale * (c.fy - h / 2) * c.center + by;
  return `translate(${dx.toFixed(3)}px, ${dy.toFixed(3)}px) scale(${(c.scale * bs).toFixed(4)})`;
}
function focusMask(f) {
  if (f.blur < 0.05) return "none";
  const inner = Math.max(f.radius * 0.55, 8).toFixed(1);
  const outer = Math.max(f.radius, 12).toFixed(1);
  return `radial-gradient(circle ${outer}px at ${f.x.toFixed(1)}px ${f.y.toFixed(1)}px, #000 0px, #000 ${inner}px, transparent ${outer}px)`;
}
function lerpFocus(a, b, p) {
  const e = easeCamera(p);
  return {
    x: lerp(a.x, b.x, e),
    y: lerp(a.y, b.y, e),
    radius: lerp(a.radius, b.radius, e),
    blur: lerp(a.blur, b.blur, e)
  };
}
function layerTransform(s) {
  return `translate(${s.x.toFixed(3)}px, ${s.y.toFixed(3)}px) translateZ(${s.z.toFixed(3)}px) scale(${s.scale.toFixed(4)})`;
}

// src/timeline.ts
var VO = {
  name: { on: 0.135, off: 1.051 },
  phone: { on: 1.636, off: 4.038 },
  commit: { on: 4.623, off: 5.659 },
  places: { on: 6.095, off: 7.115 },
  home: { on: 7.731, off: 8.541 },
  locked: { on: 9.307, off: 10.388 },
  arrive: { on: 10.943, off: 11.904 },
  opens: { on: 12.73, off: 13.435 },
  proof: { on: 13.931, off: 15.537 },
  circle: { on: 15.987, off: 17.954 },
  compound: { on: 18.464, off: 20.355 }
};
var VO_AT = 1;
var LEAD = 0.25;
var cue = (k) => ({ on: VO[k].on + VO_AT, off: VO[k].off + VO_AT });
var NAME = cue("name");
var PHONE = cue("phone");
var COMMIT = cue("commit");
var PLACES = cue("places");
var HOME = cue("home");
var LOCKED = cue("locked");
var ARRIVE = cue("arrive");
var OPENS = cue("opens");
var PROOF = cue("proof");
var CIRCLE = cue("circle");
var COMPOUND = cue("compound");
var FORMATS = {
  vertical: { width: 1080, height: 1920, phoneScale: 1.4 },
  // 1305 px tall, 68%
  wide: { width: 1920, height: 1080, phoneScale: 0.92 }
};
var SUBJECT = {
  commitments: { x: 215, y: 376 },
  // 06_home — the commitments card
  lock: { x: 215, y: 330 },
  // 07 — the padlock
  banner: { x: 215, y: -18 },
  // the system notification, above the device
  viewfinder: { x: 215, y: 340 }
  // 09 — the open camera
};
var HEAD = 0.35;
var OPEN_IN = 0.535;
var CROSS_Q = 0.32;
var CROSS_T = 0.18;
var CROSS_ACT = 0.34;
var CROSS = 0.44;
var PUSH = 0.55;
var TOAST_IN = 0.26;
var SHACKLE = 0.15;
var CLEAR = 0.15;
var OPEN = 0.276;
var CUT_PROOF = 0.24;
var CUT_SEEN = 0.2;
var CROSS_LONG = 0.26;
var filmOpensAt = HEAD;
var act1 = [
  { k: "hold", at: 0, dur: HEAD, note: "the beige world, empty, before the voice" },
  {
    k: "layer",
    id: "name",
    at: filmOpensAt,
    dur: OPEN_IN,
    via: "settleIn",
    note: "01 settles at 0.885"
  },
  {
    k: "hold",
    at: filmOpensAt + OPEN_IN,
    dur: NAME.off - (filmOpensAt + OPEN_IN),
    note: "under 'It starts with your name.'"
  },
  { k: "cross", out: "name", in: "phone", at: NAME.off, dur: CROSS_Q, depth: 400 },
  {
    k: "hold",
    at: NAME.off + CROSS_Q,
    dur: PHONE.off - (NAME.off + CROSS_Q),
    note: "under the two-sentence verification line"
  },
  { k: "cross", out: "phone", in: "commit", at: PHONE.off, dur: CROSS_Q, depth: 400 },
  // The one stagger in the film, and the only motion under a line outside
  // Act 3: the three chosen commitments light one at a time while she says
  // "Choose what you're committing to." Act 1 is the light act; this is the
  // line describing itself.
  {
    k: "stagger",
    ids: ["chip0", "chip1", "chip2"],
    at: COMMIT.on + 0.077,
    dur: 0.28,
    step: 0.08,
    from: { opacity: 0.35, scale: 0.94 },
    to: { opacity: 1, scale: 1 },
    note: "the commitments, one at a time, under their own line"
  },
  {
    k: "cross",
    out: "commit",
    in: "places",
    at: COMMIT.off,
    dur: CROSS_T,
    depth: 400,
    note: "0.18 s \u2014 the tightest gap in Act 1"
  },
  {
    k: "hold",
    at: COMMIT.off + CROSS_T,
    dur: PLACES.off - (COMMIT.off + CROSS_T),
    note: "under 'And exactly where you'll do it.'"
  }
];
var toHome = PLACES.off;
var homeIn = toHome + CROSS_ACT;
var toLocked = HOME.off;
var lockedIn = toLocked + CROSS;
var pushAt = lockedIn + 0.04;
var holdAt = pushAt + PUSH;
var pullAt = 11.36;
var toastAt = ARRIVE.on - LEAD - TOAST_IN;
var act2 = [
  {
    k: "cross",
    out: "places",
    in: "home",
    at: toHome,
    dur: CROSS_ACT,
    depth: 400,
    travel: 70,
    note: "into Act 2 \u2014 the film slows here"
  },
  { k: "sfx", at: toHome, src: "whoosh_up", gain: 0.34 },
  {
    k: "focus",
    at: homeIn - 0.2,
    dur: 0.55,
    to: { ...SUBJECT.commitments, radius: 250, blur: 2.4 },
    note: "the frame is on the commitments before 'This is your word.' lands"
  },
  {
    k: "el",
    id: "focusBloom",
    at: HOME.on - 0.09,
    dur: 0.34,
    from: { opacity: 0, scale: 0.7 },
    to: { opacity: 0.85, scale: 1 }
  },
  {
    k: "el",
    id: "focusBloom",
    at: HOME.on + 0.25,
    dur: 0.7,
    from: { opacity: 0.85 },
    to: { opacity: 0.16 }
  },
  {
    k: "hold",
    at: HOME.on,
    dur: HOME.off - HOME.on,
    note: "under 'This is your word.' \u2014 drift only"
  },
  {
    k: "cross",
    out: "home",
    in: "locked",
    at: toLocked,
    dur: CROSS,
    depth: 400,
    travel: 96,
    note: "06_home \u2192 07_tab_camera, travelling through the space"
  },
  // the camera pushes through the cut rather than cutting between two
  // stationary positions
  {
    k: "cam",
    at: toLocked,
    dur: CROSS,
    to: { fx: 215, fy: 560, scale: 1.1, center: 0.3 },
    note: "through the cut"
  },
  { k: "sfx", at: toLocked, src: "whoosh_down", gain: 0.38 },
  {
    k: "sfx",
    at: lockedIn - 0.03,
    src: "lock_catch",
    gain: 0.62,
    note: "the catch seating \u2014 the app is held closed"
  },
  {
    k: "cam",
    at: pushAt,
    dur: PUSH,
    to: { ...SUBJECT.lock, fx: SUBJECT.lock.x, fy: SUBJECT.lock.y, scale: 1.72, center: 0.86 },
    note: "focusPush into the lock \u2014 starts on silence, still moving at 10.307"
  },
  {
    k: "focus",
    at: pushAt,
    dur: PUSH + 0.16,
    to: { ...SUBJECT.lock, radius: 140, blur: 4.6 },
    note: "the rest of the screen gives way; only the lock stays sharp"
  },
  {
    k: "el",
    id: "focusBloom",
    at: LOCKED.on - 0.1,
    dur: 0.36,
    from: { opacity: 0, scale: 0.66 },
    to: { opacity: 0.7, scale: 1 }
  },
  {
    k: "el",
    id: "focusBloom",
    at: LOCKED.on + 0.3,
    dur: 0.9,
    from: { opacity: 0.7 },
    to: { opacity: 0.2 }
  },
  // The hold. Drift and breath only — 0.79 s of it, landing while she is
  // still speaking and running past the end of the line.
  {
    k: "hold",
    at: holdAt,
    dur: pullAt - holdAt,
    note: "the uncomfortable hold \u2014 0.789 s at full push, drift only"
  }
];
var releaseAt = ARRIVE.off;
var clearAt = releaseAt + SHACKLE;
var openAt = clearAt + CLEAR;
var opened = openAt + OPEN;
var act3 = [
  // 1 — the frame comes off the lock to receive a system notification
  {
    k: "cam",
    at: pullAt,
    dur: 0.4,
    to: { fx: 215, fy: 120, scale: 1.12, center: 0.5 },
    note: "the notification pulls the camera off the lock and up"
  },
  {
    k: "focus",
    at: pullAt,
    dur: 0.44,
    to: { ...SUBJECT.banner, radius: 270, blur: 2.2 }
  },
  {
    k: "layer",
    id: "toast",
    at: toastAt,
    dur: TOAST_IN,
    via: "revealUp",
    opts: { distance: 46, from: "above" },
    note: "the banner drops over the top edge of the device \u2014 settled 11.693"
  },
  { k: "sfx", at: toastAt + 0.06, src: "arrival", gain: 0.5 },
  {
    k: "hold",
    at: toastAt + TOAST_IN,
    dur: 12.55 - (toastAt + TOAST_IN),
    note: "under 'Until you actually arrive.' \u2014 the screen is still locked"
  },
  // 2 — the frame returns to the lock before the release, not after
  {
    k: "cam",
    at: 12.55,
    dur: 0.36,
    to: { ...SUBJECT.lock, fx: SUBJECT.lock.x, fy: SUBJECT.lock.y, scale: 1.44, center: 0.78 },
    note: "back to the lock while she is still speaking, so the eye is there first"
  },
  {
    k: "focus",
    at: 12.55,
    dur: 0.36,
    to: { ...SUBJECT.lock, radius: 165, blur: 3.8 }
  },
  // 3 — the lock releases, on the locked screen, in place
  {
    k: "sfx",
    at: releaseAt,
    src: "unlock",
    gain: 1,
    note: "the biggest sound in the film \u2014 the catch giving way, then air"
  },
  {
    k: "el",
    id: "lockShackle",
    at: releaseAt,
    dur: SHACKLE,
    from: { y: 0 },
    to: { y: -9 },
    note: "the shackle lifts \u2014 the only thing moving"
  },
  {
    k: "el",
    id: "lock",
    at: clearAt,
    dur: CLEAR,
    from: { opacity: 1, scale: 1 },
    to: { opacity: 0, scale: 0.84 }
  },
  {
    k: "el",
    id: "lockCopy",
    at: clearAt,
    dur: CLEAR,
    from: { opacity: 1, y: 0 },
    to: { opacity: 0, y: 8 },
    note: "'Not there yet' clears \u2014 the screen is no longer claiming to be locked"
  },
  {
    k: "el",
    id: "statusLabel",
    at: clearAt,
    dur: CLEAR,
    from: { opacity: 1 },
    to: { opacity: 0 }
  },
  {
    k: "el",
    id: "toast",
    at: clearAt,
    dur: CLEAR + 0.1,
    from: { opacity: 1, y: 0 },
    to: { opacity: 0, y: -22 },
    note: "the notification has done its job and withdraws"
  },
  // 4 — and only then, the cut
  {
    k: "cross",
    out: "locked",
    in: "opened",
    at: openAt,
    dur: OPEN,
    depth: 150,
    aperture: { x: SUBJECT.lock.x, y: SUBJECT.lock.y, radius: 660 },
    note: "07 \u2192 09, opening out of the lock's own centre"
  },
  {
    k: "el",
    id: "warmGlow",
    at: openAt,
    dur: 0.5,
    from: { opacity: 0, scale: 0.4 },
    to: { opacity: 1, scale: 1 }
  },
  {
    k: "el",
    id: "warmGlow",
    at: openAt + 0.5,
    dur: 0.8,
    from: { opacity: 1 },
    to: { opacity: 0.3, scale: 1.16 }
  },
  {
    k: "cam",
    at: openAt,
    dur: OPEN,
    to: {
      ...SUBJECT.viewfinder,
      fx: SUBJECT.viewfinder.x,
      fy: SUBJECT.viewfinder.y,
      scale: 1.08,
      center: 0.24
    },
    note: "the frame opens up as the lock lets go"
  },
  {
    k: "focus",
    at: openAt,
    dur: OPEN + 0.42,
    to: { ...SUBJECT.viewfinder, radius: 330, blur: 1.5 },
    note: "depth opens with it, but the viewfinder keeps the eye"
  },
  {
    k: "cam",
    at: opened,
    dur: 0.86,
    to: { fx: 215, fy: 466, scale: 1, center: 0 },
    note: "the last of the pull-back, decelerating under the line"
  },
  { k: "hold", at: opened, dur: LEAD, note: "the aftermath \u2014 09 settled at 13.480" },
  {
    k: "el",
    id: "focusBloom",
    at: OPENS.on - 0.1,
    dur: 0.38,
    from: { opacity: 0, scale: 0.7 },
    to: { opacity: 0.66, scale: 1 }
  },
  {
    k: "el",
    id: "focusBloom",
    at: OPENS.on + 0.3,
    dur: 0.9,
    from: { opacity: 0.66 },
    to: { opacity: 0 }
  },
  {
    k: "hold",
    at: OPENS.on,
    dur: OPENS.off - OPENS.on,
    note: "'Then it opens.' lands on a settled screen"
  }
];
var act4 = [
  {
    k: "cross",
    out: "opened",
    in: "proof",
    at: OPENS.off,
    dur: CUT_PROOF,
    depth: 400,
    note: "the snap \u2014 7 frames, no hold on either side"
  },
  {
    k: "hold",
    at: OPENS.off + CUT_PROOF,
    dur: PROOF.off - (OPENS.off + CUT_PROOF),
    note: "under 'Proof, not words.'"
  },
  {
    k: "cross",
    out: "proof",
    in: "seen",
    at: PROOF.off,
    dur: CUT_SEEN,
    depth: 400,
    note: "6 frames \u2014 the fastest cut in the film"
  },
  {
    k: "hold",
    at: PROOF.off + CUT_SEEN,
    dur: CIRCLE.off - (PROOF.off + CUT_SEEN),
    note: "under 'Your circle sees it. And you see them.'"
  }
];
var act5 = [
  { k: "cross", out: "seen", in: "routine", at: CIRCLE.off, dur: CROSS_LONG, depth: 400 },
  {
    k: "hold",
    at: CIRCLE.off + CROSS_LONG,
    dur: COMPOUND.off - (CIRCLE.off + CROSS_LONG),
    note: "under 'Show up enough, and it compounds.'"
  }
];
var voiceEnds = COMPOUND.off;
var beat = voiceEnds + 0.545;
var receded = beat + 0.6;
var markAt = receded + 0.32;
var markDone = markAt + 0.58;
var wordAt = markDone + 0.12;
var wordDone = wordAt + 0.54;
var tagAt = wordDone + 0.14;
var tagDone = tagAt + 0.6;
var fadeAt = tagDone + 0.9;
var filmEnds = fadeAt + 0.55;
var ending = [
  {
    k: "hold",
    at: voiceEnds,
    dur: beat - voiceEnds,
    note: "hold on the routine screen \u2014 the voice is gone and the film knows it"
  },
  {
    k: "exit",
    id: "routine",
    at: beat,
    dur: receded - beat,
    depth: 520,
    note: "everything recedes"
  },
  // the warm light lives in the phone's space; it leaves when the phone does,
  // or it sits in the empty frame behind the lockup as a stain
  {
    k: "el",
    id: "warmGlow",
    at: beat,
    dur: (receded - beat) * 0.7,
    from: { opacity: 0.32 },
    to: { opacity: 0 }
  },
  {
    k: "hold",
    at: receded,
    dur: markAt - receded,
    note: "the beige space alone, 0.32 s \u2014 the silence is the ending"
  },
  {
    k: "layer",
    id: "logo",
    at: markAt,
    dur: 0,
    via: "settleIn",
    note: "the lockup layer opens; its parts arrive one at a time"
  },
  {
    k: "el",
    id: "mark",
    at: markAt,
    dur: markDone - markAt,
    from: { opacity: 0, y: 26, scale: 0.96 },
    to: { opacity: 1, y: 0, scale: 1 },
    note: "the anvil mark forms, alone"
  },
  { k: "hold", at: markDone, dur: wordAt - markDone, note: "" },
  {
    k: "el",
    id: "wordmark",
    at: wordAt,
    dur: wordDone - wordAt,
    from: { opacity: 0, x: -18 },
    to: { opacity: 1, x: 0 },
    note: "ANVIL settles beside it"
  },
  { k: "hold", at: wordDone, dur: tagAt - wordDone, note: "" },
  {
    k: "el",
    id: "tagline",
    at: tagAt,
    dur: tagDone - tagAt,
    from: { opacity: 0, y: 10 },
    to: { opacity: 1, y: 0 },
    note: "the tagline fades in below"
  },
  {
    k: "hold",
    at: tagDone,
    dur: fadeAt - tagDone,
    note: "0.90 s. Let the silence sit."
  },
  {
    k: "el",
    id: "filmFade",
    at: fadeAt,
    dur: filmEnds - fadeAt,
    from: { opacity: 0 },
    to: { opacity: 1 },
    note: "out to ink \u2014 warm, not black"
  }
];
var LAYERS = {
  name: { space: "phone", screens: ["01_onboard_name"] },
  phone: { space: "phone", screens: ["02_onboard_phone"] },
  commit: { space: "phone", screens: ["04_onboard_commitments"] },
  places: { space: "phone", screens: ["05_onboard_places"] },
  home: { space: "phone", screens: ["06_home"] },
  locked: { space: "phone", screens: ["07_locked"] },
  opened: { space: "phone", screens: ["09_unlocked"] },
  proof: { space: "phone", screens: ["11_circle_live"] },
  seen: { space: "phone", screens: ["10_friend_arrived"] },
  routine: { space: "phone", screens: ["07_tab_routine"] },
  // The arrival banner is a SYSTEM notification, so it is hung across the top
  // edge of the device — wider than the device, outside its clip, and above
  // every app layer. Inside the frame it read as a caption on the app's own
  // state, which is the one thing it must not be.
  toast: {
    space: "camera",
    screens: ["08_toast"],
    box: { x: -16, y: -78, w: 462, h: 116 }
  },
  logo: { space: "stage", screens: ["logo"] }
};
var film = [...act1, ...act2, ...act3, ...act4, ...act5, ...ending];
var SECTION = {
  full: { from: 0, to: filmEnds },
  act1: { from: 0, to: HOME.on },
  act23: { from: 8, to: 14.4 },
  act45: { from: OPENS.off, to: voiceEnds },
  end: { from: voiceEnds - 0.6, to: filmEnds }
};

// build/screens.js
var SCREENS = { "06_home": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><g data-depth="0.34" data-phase="2.60"><rect width="430" height="932" fill="#E7E0D2"/><rect x="0" y="0" width="430" height="56" fill="#E7E0D2"/><line x1="0" y1="56" x2="430" y2="56" stroke="#D8CFBE"/></g><g transform="translate(30,28) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="48" y="35" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" letter-spacing="3" fill="#15130E">ANVIL</text><text x="114" y="34" font-family="Inter, system-ui, sans-serif" font-size="9" fill="#8B8475">\u25BE</text><text x="412" y="34" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">Hi, Matheus</text><g data-depth="0.86" data-phase="0.40"><text x="20" y="100" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">TODAY</text></g><g data-depth="1.1" data-phase="2.10"><rect data-el="cardTop" x="18" y="112" width="394" height="152" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><g transform="translate(215.0,142) scale(0.34) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#A8895E"/><rect x="34" y="40" width="12" height="14" fill="#A8895E"/></g><text x="215.0" y="182" font-family="Fraunces, Georgia, serif" font-size="18" font-weight="bold" fill="#15130E" text-anchor="middle">Anvil works with people</text><text x="215.0" y="204" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">Your commitments are set. Now bring one or</text><text x="215.0" y="222" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">two friends chasing the same goal.</text></g><g data-depth="1.3399999999999999" data-phase="3.80"><rect x="46" y="234" width="338" height="34" rx="12" fill="#241C13"/><text x="215.0" y="256" font-family="Fraunces, Georgia, serif" font-size="14" font-weight="bold" fill="#E7E0D2" text-anchor="middle">Start a circle</text></g><g data-depth="1.58" data-phase="5.50"><text x="20" y="298" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">YOUR COMMITMENTS</text></g><g data-depth="0.86" data-phase="7.20"><rect data-el="cardCommitments" x="18" y="310" width="394" height="132" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><text x="36" y="344" font-family="Inter, system-ui, sans-serif" font-size="14" font-weight="bold" fill="#15130E">Lift</text><text x="394" y="344" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="end">Iron Temple Gym</text><line x1="36" y1="356" x2="394" y2="356" stroke="#D8CFBE"/><text x="36" y="380" font-family="Inter, system-ui, sans-serif" font-size="14" font-weight="bold" fill="#15130E">Run</text><text x="394" y="380" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="end">Rickenbacker Causeway</text><line x1="36" y1="392" x2="394" y2="392" stroke="#D8CFBE"/><text x="36" y="416" font-family="Inter, system-ui, sans-serif" font-size="14" font-weight="bold" fill="#15130E">Swim</text><text x="394" y="416" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="end">Venetian Pool</text></g><g data-depth="1.1" data-phase="8.90"><text x="20" y="476" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">MARKS EARNED</text></g><g data-depth="1.3399999999999999" data-phase="10.60"><rect data-el="cardMarks" x="18" y="488" width="394" height="148" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><circle cx="104" cy="556" r="34" fill="#EBE1D0" stroke="#A8895E" stroke-width="2"/><g transform="translate(104,556) scale(0.32) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#7C6342"/><rect x="34" y="40" width="12" height="14" fill="#7C6342"/></g><circle cx="129" cy="580" r="9" fill="#7C6342"/><path d="M125 580 l3 3 l6 -6" stroke="#E7E0D2" stroke-width="2" fill="none" stroke-linecap="round"/><text x="104" y="608" font-family="Fraunces, Georgia, serif" font-size="13" font-weight="bold" fill="#15130E" text-anchor="middle">First Strike</text><text x="104" y="624" font-family="'DM Mono', ui-monospace, monospace" font-size="10" fill="#8B8475" text-anchor="middle">7 DAYS</text><circle cx="214" cy="556" r="34" fill="#F2EDE4" stroke="#A8895E" stroke-width="1.5"/><g transform="translate(214,556) scale(0.32) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#A8895E"/><rect x="34" y="40" width="12" height="14" fill="#A8895E"/></g><text x="214" y="608" font-family="Fraunces, Georgia, serif" font-size="13" font-weight="bold" fill="#15130E" text-anchor="middle">Steady</text><text x="214" y="624" font-family="'DM Mono', ui-monospace, monospace" font-size="10" fill="#8B8475" text-anchor="middle">30 DAYS</text><circle cx="324" cy="556" r="34" fill="#F2EDE4" stroke="#D8CFBE"/><g transform="translate(324,556) scale(0.32) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#D8CFBE"/><rect x="34" y="40" width="12" height="14" fill="#D8CFBE"/></g><text x="324" y="608" font-family="Fraunces, Georgia, serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Forged</text><text x="324" y="624" font-family="'DM Mono', ui-monospace, monospace" font-size="10" fill="#8B8475" text-anchor="middle">90 DAYS</text></g><g data-depth="0.3" data-phase="4.10"><rect x="18" y="848" width="394" height="70" rx="26" fill="#241C13"/><circle cx="60" cy="874" r="9" fill="none" stroke="#C3B49B" stroke-width="2"/><text x="60" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Circle</text><path d="M148 879 L157 868 L166 879 L166 883 L148 883 Z" fill="#F0E7D6" stroke="#F0E7D6" stroke-width="2" stroke-linejoin="round"/><text x="157" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#F0E7D6" text-anchor="middle">Home</text><rect x="148" y="908" width="18" height="2" rx="1" fill="#F0E7D6"/><rect x="245" y="868" width="18" height="15" rx="4" fill="none" stroke="#C3B49B" stroke-width="2"/><circle cx="254" cy="876" r="4" fill="#C3B49B"/><text x="254" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Camera</text><line x1="342" y1="868" x2="360" y2="868" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="874" x2="360" y2="874" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="880" x2="360" y2="880" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><text x="351" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Routine</text></g></svg>`, "04_onboard_commitments": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><rect width="430" height="932" fill="#E7E0D2"/><rect x="163.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="191.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="219.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="247.0" y="52" width="20" height="3" rx="1.5" fill="#A8895E"/><g data-depth="0.86" data-phase="0.40"><text x="34" y="90" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">FREE PLAN \xB7 3 COMMITMENTS</text><text x="34" y="124" font-family="Fraunces, Georgia, serif" font-size="26" font-weight="bold" fill="#15130E">Pick your commitments</text><text x="34" y="152" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475">Tap up to 3. Then set where you do each one.</text><g data-el="chip0"><rect x="34" y="172" width="84" height="34" rx="17" fill="#EBE1D0" stroke="#A8895E"/><text x="76.0" y="194" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#7C6342" text-anchor="middle">\u2713 Lift</text></g><g data-el="chip1"><rect x="128" y="172" width="75" height="34" rx="17" fill="#EBE1D0" stroke="#A8895E"/><text x="165.5" y="194" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#7C6342" text-anchor="middle">\u2713 Run</text></g><g data-el="chip2"><rect x="213" y="172" width="84" height="34" rx="17" fill="#EBE1D0" stroke="#A8895E"/><text x="255.0" y="194" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#7C6342" text-anchor="middle">\u2713 Swim</text></g><rect x="307" y="172" width="70" height="34" rx="17" fill="none" stroke="#D8CFBE"/><text x="342.0" y="194" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Bike</text><rect x="34" y="216" width="70" height="34" rx="17" fill="none" stroke="#D8CFBE"/><text x="69.0" y="238" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Work</text><rect x="114" y="216" width="70" height="34" rx="17" fill="none" stroke="#D8CFBE"/><text x="149.0" y="238" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Walk</text><rect x="194" y="216" width="70" height="34" rx="17" fill="none" stroke="#D8CFBE"/><text x="229.0" y="238" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Yoga</text><rect x="274" y="216" width="79" height="34" rx="17" fill="none" stroke="#D8CFBE"/><text x="313.5" y="238" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Climb</text><rect x="34" y="260" width="61" height="34" rx="17" fill="none" stroke="#D8CFBE"/><text x="64.5" y="282" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Row</text><rect x="105" y="260" width="79" height="34" rx="17" fill="none" stroke="#D8CFBE"/><text x="144.5" y="282" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Study</text><rect x="194" y="260" width="80" height="34" rx="17" fill="none" stroke="#A8895E" stroke-dasharray="4 3"/><text x="234" y="282" font-family="Inter, system-ui, sans-serif" font-size="13" font-weight="bold" fill="#7C6342" text-anchor="middle">Custom</text></g><g data-depth="1.1" data-phase="2.10"><rect x="34" y="320" width="362" height="42" rx="12" fill="#D8CFBE" opacity="0.5"/><text x="215.0" y="347" font-family="Fraunces, Georgia, serif" font-size="15" font-weight="bold" fill="#8B8475" text-anchor="middle">Set 3 places (3/3)</text></g></svg>`, "07_locked": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><g data-depth="0.34" data-phase="2.60"><rect width="430" height="932" fill="#E7E0D2"/><rect x="0" y="0" width="430" height="56" fill="#E7E0D2"/><line x1="0" y1="56" x2="430" y2="56" stroke="#D8CFBE"/></g><g transform="translate(30,28) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="48" y="35" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" letter-spacing="3" fill="#15130E">ANVIL</text><text x="114" y="34" font-family="Inter, system-ui, sans-serif" font-size="9" fill="#8B8475">\u25BE</text><text x="412" y="34" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">Hi, Matheus</text><g data-depth="0.86" data-phase="0.40"><text data-el="statusLabel" x="20" y="100" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">LOCKED</text></g><g data-depth="1.1" data-phase="2.10"><rect data-el="card" x="18" y="112" width="394" height="470" rx="20" fill="#F2EDE4" stroke="#D8CFBE"/><g data-el="lock"><circle data-el="lockRing" cx="215.0" cy="330" r="34" fill="none" stroke="#D8CFBE" stroke-width="1.5"/><rect data-el="lockBody" x="206.0" y="326" width="18" height="15" rx="3" fill="none" stroke="#8B8475" stroke-width="2"/><path data-el="lockShackle" d="M210.0 326 v-5 a5 5 0 0 1 10 0 v5" fill="none" stroke="#8B8475" stroke-width="2"/></g><g data-el="lockCopy"><text x="215.0" y="390" font-family="Fraunces, Georgia, serif" font-size="18" font-weight="bold" fill="#15130E" text-anchor="middle">Not there yet</text><text x="215.0" y="414" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">The camera opens when you reach</text><text x="215.0" y="432" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">one of your places. No shortcuts.</text></g></g><g data-depth="0.3" data-phase="4.10"><rect x="18" y="848" width="394" height="70" rx="26" fill="#241C13"/><circle cx="60" cy="874" r="9" fill="none" stroke="#C3B49B" stroke-width="2"/><text x="60" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Circle</text><path d="M148 879 L157 868 L166 879 L166 883 L148 883 Z" fill="none" stroke="#C3B49B" stroke-width="2" stroke-linejoin="round"/><text x="157" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Home</text><rect x="245" y="868" width="18" height="15" rx="4" fill="none" stroke="#F0E7D6" stroke-width="2"/><circle cx="254" cy="876" r="4" fill="#F0E7D6"/><circle cx="254" cy="874" r="17" fill="none" stroke="#A8895E" stroke-width="1.5"/><text x="254" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#F0E7D6" text-anchor="middle">Camera</text><rect x="245" y="908" width="18" height="2" rx="1" fill="#F0E7D6"/><line x1="342" y1="868" x2="360" y2="868" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="874" x2="360" y2="874" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="880" x2="360" y2="880" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><text x="351" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Routine</text></g></svg>`, "08_arrived": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><g data-depth="0.34" data-phase="2.60"><rect width="430" height="932" fill="#E7E0D2"/><rect x="0" y="0" width="430" height="56" fill="#E7E0D2"/><line x1="0" y1="56" x2="430" y2="56" stroke="#D8CFBE"/></g><g transform="translate(30,28) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="48" y="35" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" letter-spacing="3" fill="#15130E">ANVIL</text><text x="114" y="34" font-family="Inter, system-ui, sans-serif" font-size="9" fill="#8B8475">\u25BE</text><text x="412" y="34" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">Hi, Matheus</text><g data-depth="0.86" data-phase="0.40"><text data-el="statusLabel" x="20" y="100" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#7C6342">UNLOCKED \xB7 AT LIFT</text></g><g data-depth="1.1" data-phase="2.10"><rect data-el="card" x="18" y="112" width="394" height="470" rx="20" fill="#F2EDE4" stroke="#D8CFBE"/><g data-el="finder"><circle cx="215.0" cy="330" r="46" fill="none" stroke="#A8895E" stroke-width="3"/><circle cx="215.0" cy="318" r="19" fill="none" stroke="#A8895E" stroke-width="3"/></g><text data-el="hereLabel" x="215.0" y="424" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#A8895E" text-anchor="middle" letter-spacing="3">YOU ARE HERE</text></g><g data-depth="0.3" data-phase="4.10"><rect x="18" y="848" width="394" height="70" rx="26" fill="#241C13"/><circle cx="60" cy="874" r="9" fill="none" stroke="#C3B49B" stroke-width="2"/><text x="60" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Circle</text><path d="M148 879 L157 868 L166 879 L166 883 L148 883 Z" fill="none" stroke="#C3B49B" stroke-width="2" stroke-linejoin="round"/><text x="157" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Home</text><rect x="245" y="868" width="18" height="15" rx="4" fill="none" stroke="#F0E7D6" stroke-width="2"/><circle cx="254" cy="876" r="4" fill="#F0E7D6"/><circle cx="254" cy="874" r="17" fill="none" stroke="#A8895E" stroke-width="1.5"/><text x="254" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#F0E7D6" text-anchor="middle">Camera</text><rect x="245" y="908" width="18" height="2" rx="1" fill="#F0E7D6"/><line x1="342" y1="868" x2="360" y2="868" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="874" x2="360" y2="874" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="880" x2="360" y2="880" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><text x="351" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Routine</text></g></svg>`, "08_toast": `<svg xmlns="http://www.w3.org/2000/svg" width="462" height="116" viewBox="0 0 462 116"><g data-el="toast"><rect x="6" y="16" width="450" height="84" rx="26" fill="#241C13"/><circle cx="54" cy="58" r="21" fill="#A8895E"/><text x="54" y="65" font-family="Fraunces, Georgia, serif" font-size="18" font-weight="700" fill="#E7E0D2" text-anchor="middle">A</text><text x="90" y="52" font-family="Fraunces, Georgia, serif" font-size="18" font-weight="700" fill="#E7E0D2">You made it to Lift</text><text x="90" y="76" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#C3B49B">camera unlocked</text><text x="428" y="52" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">now</text></g></svg>`, "09_unlocked": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><g data-depth="0.34" data-phase="2.60"><rect width="430" height="932" fill="#E7E0D2"/><rect x="0" y="0" width="430" height="56" fill="#E7E0D2"/><line x1="0" y1="56" x2="430" y2="56" stroke="#D8CFBE"/></g><g transform="translate(30,28) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="48" y="35" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" letter-spacing="3" fill="#15130E">ANVIL</text><text x="114" y="34" font-family="Inter, system-ui, sans-serif" font-size="9" fill="#8B8475">\u25BE</text><text x="412" y="34" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">Hi, Matheus</text><g data-depth="0.86" data-phase="0.40"><text data-el="statusLabel" x="20" y="100" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#7C6342">UNLOCKED \xB7 AT LIFT</text></g><g data-depth="1.1" data-phase="2.10"><rect data-el="card" x="18" y="112" width="394" height="470" rx="20" fill="#241C13"/><g data-el="finder"><circle cx="215.0" cy="330" r="46" fill="none" stroke="#A8895E" stroke-width="3"/><circle cx="215.0" cy="318" r="19" fill="none" stroke="#A8895E" stroke-width="3"/><path d="M181.0 318 h10 l6-10 h36 l6 10 h10" fill="none" stroke="#A8895E" stroke-width="3" stroke-linejoin="round"/></g><text data-el="hereLabel" x="215.0" y="424" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#A8895E" text-anchor="middle" letter-spacing="3">YOU ARE HERE</text><g data-el="capture"><rect x="46" y="524" width="338" height="42" rx="14" fill="#7C6342"/><text x="215.0" y="551" font-family="Fraunces, Georgia, serif" font-size="15" font-weight="bold" fill="#E7E0D2" text-anchor="middle">Capture proof</text></g></g><g data-depth="0.3" data-phase="4.10"><rect x="18" y="848" width="394" height="70" rx="26" fill="#241C13"/><circle cx="60" cy="874" r="9" fill="none" stroke="#C3B49B" stroke-width="2"/><text x="60" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Circle</text><path d="M148 879 L157 868 L166 879 L166 883 L148 883 Z" fill="none" stroke="#C3B49B" stroke-width="2" stroke-linejoin="round"/><text x="157" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Home</text><rect x="245" y="868" width="18" height="15" rx="4" fill="none" stroke="#F0E7D6" stroke-width="2"/><circle cx="254" cy="876" r="4" fill="#F0E7D6"/><circle cx="254" cy="874" r="17" fill="none" stroke="#A8895E" stroke-width="1.5"/><text x="254" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#F0E7D6" text-anchor="middle">Camera</text><rect x="245" y="908" width="18" height="2" rx="1" fill="#F0E7D6"/><line x1="342" y1="868" x2="360" y2="868" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="874" x2="360" y2="874" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="880" x2="360" y2="880" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><text x="351" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Routine</text></g></svg>`, "01_onboard_name": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><rect width="430" height="932" fill="#E7E0D2"/><rect x="163.0" y="52" width="20" height="3" rx="1.5" fill="#A8895E"/><rect x="191.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="219.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="247.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><g transform="translate(215.0,140) scale(0.55) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="215.0" y="200" font-family="Fraunces, Georgia, serif" font-size="30" font-weight="bold" letter-spacing="7" fill="#15130E" text-anchor="middle">ANVIL</text><text x="215.0" y="224" font-family="'DM Mono', ui-monospace, monospace" font-size="12" letter-spacing="3" fill="#8B8475" text-anchor="middle">SHARPEN IRON WITH IRON</text><text x="56" y="280" font-family="'DM Mono', ui-monospace, monospace" font-size="13" fill="#8B8475">What should your circle call you?</text><g data-depth="0.86" data-phase="0.40"><rect x="56" y="296" width="318" height="42" rx="12" fill="#F2EDE4" stroke="#15130E" stroke-width="2"/><text x="72" y="323" font-family="Inter, system-ui, sans-serif" font-size="14" fill="#8B8475">First name</text></g><g data-depth="1.1" data-phase="2.10"><rect x="56" y="376" width="318" height="42" rx="12" fill="#D8CFBE" opacity="0.5"/><text x="215.0" y="403" font-family="Fraunces, Georgia, serif" font-size="15" font-weight="bold" fill="#8B8475" text-anchor="middle">Continue</text></g></svg>`, "02_onboard_phone": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><rect width="430" height="932" fill="#E7E0D2"/><rect x="163.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="191.0" y="52" width="20" height="3" rx="1.5" fill="#A8895E"/><rect x="219.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="247.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><text x="34" y="110" font-family="Fraunces, Georgia, serif" font-size="26" font-weight="bold" fill="#15130E">Your number</text><text x="34" y="140" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475">Verified once so your circle knows you're real.</text><text x="34" y="158" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475">Never shown without your say.</text><g data-depth="0.86" data-phase="0.40"><text x="34" y="200" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">MOBILE NUMBER</text></g><g data-depth="1.1" data-phase="2.10"><rect x="34" y="210" width="362" height="42" rx="12" fill="#F2EDE4" stroke="#15130E" stroke-width="2"/><text x="50" y="237" font-family="Inter, system-ui, sans-serif" font-size="14" fill="#8B8475">(305) 555-1234</text><text x="34" y="278" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475">A 6 digit code confirms it.</text></g><g data-depth="1.3399999999999999" data-phase="3.80"><rect x="34" y="300" width="362" height="42" rx="12" fill="#241C13"/><text x="215.0" y="327" font-family="Fraunces, Georgia, serif" font-size="15" font-weight="bold" fill="#E7E0D2" text-anchor="middle">Send code</text></g></svg>`, "05_onboard_places": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><rect width="430" height="932" fill="#E7E0D2"/><rect x="163.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="191.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="219.0" y="52" width="20" height="3" rx="1.5" fill="#D8CFBE"/><rect x="247.0" y="52" width="20" height="3" rx="1.5" fill="#A8895E"/><g data-depth="0.86" data-phase="0.40"><text x="34" y="90" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">FREE PLAN \xB7 3 COMMITMENTS</text><text x="34" y="124" font-family="Fraunces, Georgia, serif" font-size="26" font-weight="bold" fill="#15130E">Pick your commitments</text><text x="34" y="152" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475">Tap up to 3. Then set where you do each one.</text></g><g data-depth="1.1" data-phase="2.10"><rect x="34" y="176" width="362" height="98" rx="16" fill="#F2EDE4" stroke="#D8CFBE"/><text x="52" y="206" font-family="Inter, system-ui, sans-serif" font-size="15" font-weight="bold" fill="#15130E">Lift</text><text x="378" y="206" font-family="Inter, system-ui, sans-serif" font-size="15" fill="#8B8475" text-anchor="end">\u2715</text></g><g data-depth="1.3399999999999999" data-phase="3.80"><rect x="52" y="220" width="326" height="42" rx="12" fill="#F2EDE4" stroke="#D8CFBE" stroke-width="1"/><text x="68" y="247" font-family="Inter, system-ui, sans-serif" font-size="14" fill="#15130E">Iron Temple Gym</text></g><g data-depth="1.58" data-phase="5.50"><rect x="34" y="288" width="362" height="98" rx="16" fill="#F2EDE4" stroke="#D8CFBE"/><text x="52" y="318" font-family="Inter, system-ui, sans-serif" font-size="15" font-weight="bold" fill="#15130E">Run</text><text x="378" y="318" font-family="Inter, system-ui, sans-serif" font-size="15" fill="#8B8475" text-anchor="end">\u2715</text></g><g data-depth="0.86" data-phase="7.20"><rect x="52" y="332" width="326" height="42" rx="12" fill="#F2EDE4" stroke="#D8CFBE" stroke-width="1"/><text x="68" y="359" font-family="Inter, system-ui, sans-serif" font-size="14" fill="#15130E">Rickenbacker Causeway</text></g><g data-depth="1.1" data-phase="8.90"><rect x="34" y="400" width="362" height="98" rx="16" fill="#F2EDE4" stroke="#D8CFBE"/><text x="52" y="430" font-family="Inter, system-ui, sans-serif" font-size="15" font-weight="bold" fill="#15130E">Swim</text><text x="378" y="430" font-family="Inter, system-ui, sans-serif" font-size="15" fill="#8B8475" text-anchor="end">\u2715</text></g><g data-depth="1.3399999999999999" data-phase="10.60"><rect x="52" y="444" width="326" height="42" rx="12" fill="#F2EDE4" stroke="#15130E" stroke-width="2"/><text x="68" y="471" font-family="Inter, system-ui, sans-serif" font-size="14" fill="#15130E">Venetian Pool</text></g><g data-depth="1.58" data-phase="12.30"><rect x="34" y="524" width="362" height="46" rx="14" fill="#241C13"/><text x="215.0" y="553" font-family="Fraunces, Georgia, serif" font-size="16" font-weight="bold" fill="#E7E0D2" text-anchor="middle">Enter Anvil</text></g></svg>`, "07_tab_routine": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><g data-depth="0.34" data-phase="2.60"><rect width="430" height="932" fill="#E7E0D2"/><rect x="0" y="0" width="430" height="56" fill="#E7E0D2"/><line x1="0" y1="56" x2="430" y2="56" stroke="#D8CFBE"/></g><g transform="translate(30,28) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="48" y="35" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" letter-spacing="3" fill="#15130E">ANVIL</text><text x="114" y="34" font-family="Inter, system-ui, sans-serif" font-size="9" fill="#8B8475">\u25BE</text><text x="412" y="34" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">Hi, Matheus</text><g data-depth="0.86" data-phase="0.40"><text x="20" y="100" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">THE LONG GAME</text></g><g data-depth="1.1" data-phase="2.10"><rect x="18" y="112" width="394" height="108" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/></g><g data-depth="1.3399999999999999" data-phase="3.80"><text x="36" y="140" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">THIS WEEK</text><circle cx="42" cy="172" r="17" fill="#A8895E" stroke="#A8895E"/><path d="M36 172 l4 5 l8 -9" stroke="#E7E0D2" stroke-width="2.2" fill="none" stroke-linecap="round"/><text x="42" y="205" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475" text-anchor="middle">M</text><circle cx="99" cy="172" r="17" fill="#A8895E" stroke="#A8895E"/><path d="M93 172 l4 5 l8 -9" stroke="#E7E0D2" stroke-width="2.2" fill="none" stroke-linecap="round"/><text x="99" y="205" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475" text-anchor="middle">T</text><circle cx="156" cy="172" r="17" fill="#F2EDE4" stroke="#D8CFBE"/><circle cx="156" cy="172" r="3" fill="#D8CFBE"/><text x="156" y="205" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475" text-anchor="middle">W</text><circle cx="213" cy="172" r="17" fill="#A8895E" stroke="#A8895E"/><path d="M207 172 l4 5 l8 -9" stroke="#E7E0D2" stroke-width="2.2" fill="none" stroke-linecap="round"/><text x="213" y="205" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475" text-anchor="middle">T</text><circle cx="270" cy="172" r="17" fill="#A8895E" stroke="#A8895E"/><path d="M264 172 l4 5 l8 -9" stroke="#E7E0D2" stroke-width="2.2" fill="none" stroke-linecap="round"/><text x="270" y="205" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475" text-anchor="middle">F</text><circle cx="327" cy="172" r="17" fill="#F2EDE4" stroke="#D8CFBE"/><circle cx="327" cy="172" r="3" fill="#D8CFBE"/><text x="327" y="205" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475" text-anchor="middle">S</text><circle cx="384" cy="172" r="17" fill="#F2EDE4" stroke="#D8CFBE"/><circle cx="384" cy="172" r="3" fill="#D8CFBE"/><text x="384" y="205" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475" text-anchor="middle">S</text></g><g data-depth="1.58" data-phase="5.50"><rect x="18" y="236" width="394" height="106" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><text x="36" y="282" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" fill="#15130E">Current streak</text><text x="394" y="286" font-family="Fraunces, Georgia, serif" font-size="30" font-weight="bold" fill="#7C6342" text-anchor="end">12</text></g><g data-depth="0.86" data-phase="7.20"><rect x="36" y="302" width="358" height="7" rx="3.5" fill="#EBE1D0"/><rect x="36" y="302" width="143.20000000000002" height="7" rx="3.5" fill="#7C6342"/><text x="36" y="330" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475">18 days to Forged</text></g><g data-depth="1.1" data-phase="8.90"><rect x="18" y="360" width="394" height="48" rx="16" fill="#F2EDE4" stroke="#D8CFBE"/><text x="215.0" y="390" font-family="Inter, system-ui, sans-serif" font-size="15" fill="#15130E" text-anchor="middle">Add or modify a commitment</text></g><g data-depth="1.3399999999999999" data-phase="10.60"><rect x="18" y="418" width="394" height="48" rx="16" fill="#F2EDE4" stroke="#D8CFBE"/><text x="215.0" y="448" font-family="Inter, system-ui, sans-serif" font-size="15" fill="#15130E" text-anchor="middle">Create or join a circle</text></g><g data-depth="0.3" data-phase="4.10"><rect x="18" y="848" width="394" height="70" rx="26" fill="#241C13"/><circle cx="60" cy="874" r="9" fill="none" stroke="#C3B49B" stroke-width="2"/><text x="60" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Circle</text><path d="M148 879 L157 868 L166 879 L166 883 L148 883 Z" fill="none" stroke="#C3B49B" stroke-width="2" stroke-linejoin="round"/><text x="157" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Home</text><rect x="245" y="868" width="18" height="15" rx="4" fill="none" stroke="#C3B49B" stroke-width="2"/><circle cx="254" cy="876" r="4" fill="#C3B49B"/><text x="254" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Camera</text><line x1="342" y1="868" x2="360" y2="868" stroke="#F0E7D6" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="874" x2="360" y2="874" stroke="#F0E7D6" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="880" x2="360" y2="880" stroke="#F0E7D6" stroke-width="2" stroke-linecap="round"/><text x="351" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#F0E7D6" text-anchor="middle">Routine</text><rect x="342" y="908" width="18" height="2" rx="1" fill="#F0E7D6"/></g></svg>`, "07_tab_circle": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><g data-depth="0.34" data-phase="2.60"><rect width="430" height="932" fill="#E7E0D2"/><rect x="0" y="0" width="430" height="56" fill="#E7E0D2"/><line x1="0" y1="56" x2="430" y2="56" stroke="#D8CFBE"/></g><g transform="translate(30,28) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="48" y="35" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" letter-spacing="3" fill="#15130E">ANVIL</text><text x="114" y="34" font-family="Inter, system-ui, sans-serif" font-size="9" fill="#8B8475">\u25BE</text><text x="412" y="34" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">Hi, Matheus</text><g data-depth="0.86" data-phase="0.40"><text x="20" y="100" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">PROOF, NOT WORDS</text></g><g data-depth="1.1" data-phase="2.10"><rect x="18" y="112" width="394" height="230" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><g transform="translate(215.0,178) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#D8CFBE"/><rect x="34" y="40" width="12" height="14" fill="#D8CFBE"/></g><text x="215.0" y="228" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" fill="#15130E" text-anchor="middle">Quiet in here</text><text x="215.0" y="256" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">When your circle shows up, their proof</text><text x="215.0" y="276" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">lands here. It fades once everyone has</text><text x="215.0" y="296" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">seen it.</text></g><g data-depth="0.3" data-phase="4.10"><rect x="18" y="848" width="394" height="70" rx="26" fill="#241C13"/><circle cx="60" cy="874" r="9" fill="#F0E7D6" stroke="#F0E7D6" stroke-width="2"/><text x="60" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#F0E7D6" text-anchor="middle">Circle</text><rect x="51" y="908" width="18" height="2" rx="1" fill="#F0E7D6"/><path d="M148 879 L157 868 L166 879 L166 883 L148 883 Z" fill="none" stroke="#C3B49B" stroke-width="2" stroke-linejoin="round"/><text x="157" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Home</text><rect x="245" y="868" width="18" height="15" rx="4" fill="none" stroke="#C3B49B" stroke-width="2"/><circle cx="254" cy="876" r="4" fill="#C3B49B"/><text x="254" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Camera</text><line x1="342" y1="868" x2="360" y2="868" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="874" x2="360" y2="874" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="880" x2="360" y2="880" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><text x="351" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Routine</text></g></svg>`, "10_friend_arrived": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><g data-depth="0.34" data-phase="2.60"><rect width="430" height="932" fill="#E7E0D2"/><rect x="0" y="0" width="430" height="56" fill="#E7E0D2"/><line x1="0" y1="56" x2="430" y2="56" stroke="#D8CFBE"/></g><g transform="translate(30,28) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="48" y="35" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" letter-spacing="3" fill="#15130E">ANVIL</text><text x="114" y="34" font-family="Inter, system-ui, sans-serif" font-size="9" fill="#8B8475">\u25BE</text><text x="412" y="34" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">Hi, Matheus</text><g data-depth="0.86" data-phase="0.40"><text x="20" y="100" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">TODAY</text></g><g data-depth="1.1" data-phase="2.10"><rect x="18" y="112" width="394" height="152" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><g transform="translate(215.0,142) scale(0.34) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#A8895E"/><rect x="34" y="40" width="12" height="14" fill="#A8895E"/></g><text x="215.0" y="182" font-family="Fraunces, Georgia, serif" font-size="18" font-weight="bold" fill="#15130E" text-anchor="middle">Anvil works with people</text><text x="215.0" y="204" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">Your commitments are set. Now bring one or</text><text x="215.0" y="222" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="middle">two friends chasing the same goal.</text></g><g data-depth="1.3399999999999999" data-phase="3.80"><rect x="46" y="234" width="338" height="34" rx="12" fill="#241C13"/><text x="215.0" y="256" font-family="Fraunces, Georgia, serif" font-size="14" font-weight="bold" fill="#E7E0D2" text-anchor="middle">Start a circle</text></g><g data-depth="1.58" data-phase="5.50"><text x="20" y="298" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">YOUR COMMITMENTS</text></g><g data-depth="0.86" data-phase="7.20"><rect x="18" y="310" width="394" height="132" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><text x="36" y="344" font-family="Inter, system-ui, sans-serif" font-size="14" font-weight="bold" fill="#15130E">Lift</text><text x="394" y="344" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="end">Iron Temple Gym</text><line x1="36" y1="356" x2="394" y2="356" stroke="#D8CFBE"/><text x="36" y="380" font-family="Inter, system-ui, sans-serif" font-size="14" font-weight="bold" fill="#15130E">Run</text><text x="394" y="380" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="end">Rickenbacker Causeway</text><line x1="36" y1="392" x2="394" y2="392" stroke="#D8CFBE"/><text x="36" y="416" font-family="Inter, system-ui, sans-serif" font-size="14" font-weight="bold" fill="#15130E">Swim</text><text x="394" y="416" font-family="Inter, system-ui, sans-serif" font-size="13" fill="#8B8475" text-anchor="end">Venetian Pool</text></g><g data-depth="1.1" data-phase="8.90"><text x="20" y="476" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">MARKS EARNED</text></g><g data-depth="1.3399999999999999" data-phase="10.60"><rect x="18" y="488" width="394" height="148" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><circle cx="104" cy="556" r="34" fill="#EBE1D0" stroke="#A8895E" stroke-width="2"/><g transform="translate(104,556) scale(0.32) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#7C6342"/><rect x="34" y="40" width="12" height="14" fill="#7C6342"/></g><circle cx="129" cy="580" r="9" fill="#7C6342"/><path d="M125 580 l3 3 l6 -6" stroke="#E7E0D2" stroke-width="2" fill="none" stroke-linecap="round"/><text x="104" y="608" font-family="Fraunces, Georgia, serif" font-size="13" font-weight="bold" fill="#15130E" text-anchor="middle">First Strike</text><text x="104" y="624" font-family="'DM Mono', ui-monospace, monospace" font-size="10" fill="#8B8475" text-anchor="middle">7 DAYS</text><circle cx="214" cy="556" r="34" fill="#F2EDE4" stroke="#A8895E" stroke-width="1.5"/><g transform="translate(214,556) scale(0.32) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#A8895E"/><rect x="34" y="40" width="12" height="14" fill="#A8895E"/></g><text x="214" y="608" font-family="Fraunces, Georgia, serif" font-size="13" font-weight="bold" fill="#15130E" text-anchor="middle">Steady</text><text x="214" y="624" font-family="'DM Mono', ui-monospace, monospace" font-size="10" fill="#8B8475" text-anchor="middle">30 DAYS</text><circle cx="324" cy="556" r="34" fill="#F2EDE4" stroke="#D8CFBE"/><g transform="translate(324,556) scale(0.32) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#D8CFBE"/><rect x="34" y="40" width="12" height="14" fill="#D8CFBE"/></g><text x="324" y="608" font-family="Fraunces, Georgia, serif" font-size="13" font-weight="bold" fill="#8B8475" text-anchor="middle">Forged</text><text x="324" y="624" font-family="'DM Mono', ui-monospace, monospace" font-size="10" fill="#8B8475" text-anchor="middle">90 DAYS</text></g><g data-depth="0.3" data-phase="4.10"><rect x="18" y="848" width="394" height="70" rx="26" fill="#241C13"/><circle cx="60" cy="874" r="9" fill="none" stroke="#C3B49B" stroke-width="2"/><text x="60" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Circle</text><path d="M148 879 L157 868 L166 879 L166 883 L148 883 Z" fill="#F0E7D6" stroke="#F0E7D6" stroke-width="2" stroke-linejoin="round"/><text x="157" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#F0E7D6" text-anchor="middle">Home</text><rect x="148" y="908" width="18" height="2" rx="1" fill="#F0E7D6"/><rect x="245" y="868" width="18" height="15" rx="4" fill="none" stroke="#C3B49B" stroke-width="2"/><circle cx="254" cy="876" r="4" fill="#C3B49B"/><text x="254" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Camera</text><line x1="342" y1="868" x2="360" y2="868" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="874" x2="360" y2="874" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="880" x2="360" y2="880" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><text x="351" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Routine</text><rect x="46" y="70" width="338" height="62" rx="18" fill="#241C13"/><circle cx="82" cy="101" r="17" fill="#A8895E"/><text x="82" y="107" font-family="Fraunces, Georgia, serif" font-size="15" font-weight="bold" fill="#E7E0D2" text-anchor="middle">J</text><text x="110" y="97" font-family="Fraunces, Georgia, serif" font-size="15" font-weight="bold" fill="#E7E0D2">Jeff made it to the gym</text><text x="110" y="115" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B">your move</text></g></svg>`, "11_circle_live": `<svg xmlns="http://www.w3.org/2000/svg" width="430" height="932" viewBox="0 0 430 932"><g data-depth="0.34" data-phase="2.60"><rect width="430" height="932" fill="#E7E0D2"/><rect x="0" y="0" width="430" height="56" fill="#E7E0D2"/><line x1="0" y1="56" x2="430" y2="56" stroke="#D8CFBE"/></g><g transform="translate(30,28) scale(0.3) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="48" y="35" font-family="Fraunces, Georgia, serif" font-size="19" font-weight="bold" letter-spacing="3" fill="#15130E">ANVIL</text><text x="114" y="34" font-family="Inter, system-ui, sans-serif" font-size="9" fill="#8B8475">\u25BE</text><text x="412" y="34" font-family="'DM Mono', ui-monospace, monospace" font-size="12" fill="#8B8475" text-anchor="end">Hi, Matheus</text><g data-depth="0.86" data-phase="0.40"><text x="20" y="100" font-family="'DM Mono', ui-monospace, monospace" font-size="11" letter-spacing="2" fill="#8B8475">PROOF, NOT WORDS</text><defs><linearGradient id="ph" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A8895E"/><stop offset="1" stop-color="#7C6342"/></linearGradient></defs></g><g data-depth="1.1" data-phase="2.10"><rect x="18" y="112" width="394" height="268" rx="18" fill="#F2EDE4" stroke="#D8CFBE"/><path d="M30 112 h370 a12 12 0 0 1 12 12 v186 h-394 v-186 a12 12 0 0 1 12 -12 Z" fill="url(#ph)"/><circle cx="52" cy="272" r="17" fill="#E7E0D2"/><text x="52" y="278" font-family="Fraunces, Georgia, serif" font-size="16" font-weight="bold" fill="#7C6342" text-anchor="middle">J</text><text x="78" y="268" font-family="Inter, system-ui, sans-serif" font-size="15" font-weight="bold" fill="#E7E0D2">Jeff</text><text x="78" y="286" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#EBE1D0">Iron Temple \xB7 just now</text><text x="36" y="352" font-family="Fraunces, Georgia, serif" font-size="15" font-style="italic" fill="#15130E">Showed up.</text><text x="394" y="352" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#8B8475" text-anchor="end">seen by 2</text></g><g data-depth="0.3" data-phase="4.10"><rect x="18" y="848" width="394" height="70" rx="26" fill="#241C13"/><circle cx="60" cy="874" r="9" fill="#F0E7D6" stroke="#F0E7D6" stroke-width="2"/><text x="60" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#F0E7D6" text-anchor="middle">Circle</text><rect x="51" y="908" width="18" height="2" rx="1" fill="#F0E7D6"/><path d="M148 879 L157 868 L166 879 L166 883 L148 883 Z" fill="none" stroke="#C3B49B" stroke-width="2" stroke-linejoin="round"/><text x="157" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Home</text><rect x="245" y="868" width="18" height="15" rx="4" fill="none" stroke="#C3B49B" stroke-width="2"/><circle cx="254" cy="876" r="4" fill="#C3B49B"/><text x="254" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Camera</text><line x1="342" y1="868" x2="360" y2="868" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="874" x2="360" y2="874" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><line x1="342" y1="880" x2="360" y2="880" stroke="#C3B49B" stroke-width="2" stroke-linecap="round"/><text x="351" y="902" font-family="'DM Mono', ui-monospace, monospace" font-size="11" fill="#C3B49B" text-anchor="middle">Routine</text></g></svg>`, "12_notification": '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="150" viewBox="0 0 920 150"><g data-depth="0.86" data-phase="0.40"><rect width="920" height="150" rx="34" fill="#FBF8F1" stroke="#D8CFBE" stroke-width="2"/><rect x="26" y="30" width="90" height="90" rx="20" fill="#E7E0D2" stroke="#D8CFBE" stroke-width="2"/><g transform="translate(71,75) scale(0.62) translate(-40,-32)" opacity="1"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g><text x="150" y="58" font-family="Inter, system-ui, sans-serif" font-size="34" font-weight="bold" fill="#15130E">ANVIL</text><text x="880" y="54" font-family="Inter, system-ui, sans-serif" font-size="26" fill="#8B8475" text-anchor="end">now</text><text x="150" y="104" font-family="Inter, system-ui, sans-serif" font-size="34" fill="#15130E">Joe arrived at the gym</text></g></svg>', "logo": '<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">\n<g transform="translate(772,457)"><g data-el="mark"><g transform="scale(2.6) translate(-40,-32)"><path d="M8 20 L72 20 L62 30 L50 30 L50 40 L56 52 L24 52 L30 40 L30 30 L18 30 Z" fill="#15130E"/><rect x="34" y="40" width="12" height="14" fill="#15130E"/></g></g></g>\n<text data-el="wordmark" x="896" y="502" font-family="Fraunces, Georgia, serif" font-size="92" font-weight="700" letter-spacing="16" fill="#15130E">ANVIL</text>\n<text data-el="tagline" x="960" y="596" font-family="Inter, system-ui, sans-serif" font-size="29" fill="#8B8475" text-anchor="middle">Sharpen iron with iron.</text>\n</svg>' };

// src/stage.ts
var EL_REST = { opacity: 1, x: 0, y: 0, scale: 1 };
var PHONE_W = 430;
var PHONE_H = 932;
var RADIUS = 44;
function evaluate(tracks, t) {
  const layers = {};
  for (const id of Object.keys(LAYERS)) layers[id] = { ...HIDDEN };
  const els = {};
  for (const tr of tracks) {
    if (tr.k === "el" && !(tr.id in els)) els[tr.id] = { ...EL_REST, ...tr.from };
    if (tr.k === "stagger") {
      for (const id of tr.ids) if (!(id in els)) els[id] = { ...EL_REST, ...tr.from };
    }
  }
  const clips = {};
  let camera = { ...CAMERA_REST };
  {
    let from = { ...CAMERA_REST };
    for (const tr of tracks.filter((x) => x.k === "cam").sort((a, b) => a.at - b.at)) {
      const to = { fx: tr.to.fx, fy: tr.to.fy, scale: tr.to.scale, center: tr.to.center };
      if (t >= tr.at) camera = focusPush(progress(t, tr.at, tr.dur), from, to);
      from = to;
    }
  }
  let focus = { ...FOCUS_REST };
  {
    let from = { ...FOCUS_REST };
    for (const tr of tracks.filter((x) => x.k === "focus").sort((a, b) => a.at - b.at)) {
      const to = { ...from, ...tr.to };
      if (t >= tr.at) focus = lerpFocus(from, to, progress(t, tr.at, tr.dur));
      from = to;
    }
  }
  for (const tr of [...tracks].sort((a, b) => a.at - b.at)) {
    if (tr.k === "stagger") {
      const step = tr.step ?? 0.08;
      tr.ids.forEach((id, i) => {
        const q = ease(progress(t, tr.at + i * step, tr.dur));
        const from = { ...EL_REST, ...tr.from };
        const to = { ...from, ...tr.to };
        els[id] = {
          opacity: lerp(from.opacity, to.opacity, q),
          x: lerp(from.x, to.x, q),
          y: lerp(from.y, to.y, q),
          scale: lerp(from.scale, to.scale, q)
        };
      });
      continue;
    }
    if (t < tr.at) continue;
    const p = progress(t, tr.at, tr.dur);
    switch (tr.k) {
      case "el": {
        const e = ease(p);
        const from = { ...els[tr.id] ?? EL_REST, ...tr.from };
        const to = { ...from, ...tr.to };
        els[tr.id] = {
          opacity: lerp(from.opacity, to.opacity, e),
          x: lerp(from.x, to.x, e),
          y: lerp(from.y, to.y, e),
          scale: lerp(from.scale, to.scale, e)
        };
        break;
      }
      case "layer":
        layers[tr.id] = p >= 1 ? { ...REST } : {
          ...REST,
          ...tr.via === "settleIn" ? settleIn(p) : revealUp(p, tr.opts)
        };
        break;
      case "cross": {
        const c = crossDepth(p, { depth: tr.depth, aperture: !!tr.aperture });
        layers[tr.out] = p >= 1 ? { ...HIDDEN } : { ...REST, ...c.out };
        layers[tr.in] = p >= 1 ? { ...REST } : { ...REST, ...c.in };
        if (tr.travel && p < 1) layers[tr.in].y = lerp(tr.travel, 0, ease(p));
        if (tr.travel && p < 1) layers[tr.out].y = lerp(0, -tr.travel * 0.45, ease(p));
        if (tr.aperture && p < 1) {
          const r = apertureOpen(p, tr.aperture.radius);
          clips[tr.in] = `circle(${r.toFixed(2)}px at ${tr.aperture.x}px ${tr.aperture.y}px)`;
        } else if (tr.aperture) delete clips[tr.in];
        break;
      }
      case "exit":
        layers[tr.id] = p >= 1 ? { ...HIDDEN } : { ...REST, ...recede(p, { depth: tr.depth }) };
        break;
      case "cam":
      case "focus":
        break;
      // resolved above, as a chain
      case "hold":
      case "sfx":
        break;
    }
  }
  return { layers, els, clips, camera, focus, t };
}
var bandCache = [];
function build(root, format2 = "vertical") {
  const F = FORMATS[format2];
  root.innerHTML = "";
  root.className = "stage";
  root.style.width = `${F.width}px`;
  root.style.height = `${F.height}px`;
  const forge = document.createElement("div");
  forge.className = "forge";
  root.append(forge);
  const wrap = document.createElement("div");
  wrap.className = "phoneWrap";
  wrap.style.transform = `translate(-50%, -50%) scale(${F.phoneScale})`;
  const cam = document.createElement("div");
  cam.className = "camera";
  cam.dataset.el = "camera";
  wrap.append(cam);
  root.append(wrap);
  const stageSpace = document.createElement("div");
  stageSpace.className = "stageSpace";
  stageSpace.style.width = `${F.width}px`;
  stageSpace.style.height = `${F.height}px`;
  root.append(stageSpace);
  const svgOf = (key) => {
    const host = document.createElement("div");
    host.className = "part";
    host.innerHTML = SCREENS[key];
    const svg = host.querySelector("svg");
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    return host;
  };
  for (const [id, def] of Object.entries(LAYERS)) {
    const layer = document.createElement("div");
    layer.className = "layer" + (def.space === "stage" ? " stageLayer" : "") + (def.box ? " boxed" : "");
    layer.dataset.layer = id;
    if (def.box) {
      layer.style.left = `${def.box.x}px`;
      layer.style.top = `${def.box.y}px`;
      layer.style.width = `${def.box.w}px`;
      layer.style.height = `${def.box.h}px`;
    }
    if (def.space === "phone") {
      const blur = document.createElement("div");
      blur.className = "dof dofBlur";
      const sharp = document.createElement("div");
      sharp.className = "dof dofSharp";
      for (const key of def.screens) {
        blur.append(svgOf(key));
        sharp.append(svgOf(key));
      }
      layer.append(blur, sharp);
    } else {
      for (const key of def.screens) layer.append(svgOf(key));
    }
    (def.space === "stage" ? stageSpace : cam).append(layer);
  }
  for (const [cls, el] of [["warmGlow", "warmGlow"], ["focusBloom", "focusBloom"]]) {
    const d = document.createElement("div");
    d.className = cls;
    d.dataset.el = el;
    cam.append(d);
  }
  const fade = document.createElement("div");
  fade.className = "filmFade";
  fade.dataset.el = "filmFade";
  root.append(fade);
  bandCache = [...root.querySelectorAll("[data-depth]")].map((node) => ({
    node,
    depth: +node.dataset.depth,
    phase: +node.dataset.phase
  }));
  return root;
}
function paint(frame) {
  const t = frame.t;
  const cam = document.querySelector('[data-el="camera"]');
  cam.style.transform = cameraTransform(frame.camera, t);
  for (const [id, s] of Object.entries(frame.layers)) {
    const el = document.querySelector(`[data-layer="${id}"]`);
    if (!el) continue;
    const vis = s.opacity > 1e-3;
    el.style.visibility = vis ? "visible" : "hidden";
    if (!vis) continue;
    el.style.opacity = String(s.opacity);
    const dx = s.x + drift(t, id.length * 0.9, 1.3, 10.1, 16.3);
    const dy = s.y + drift(t, id.length * 1.4 + 0.6, 2.9, 8.9, 14.7);
    el.style.transform = layerTransform({ ...s, x: dx, y: dy });
    el.style.clipPath = frame.clips[id] ?? "none";
    if (!el.classList.contains("stageLayer") && !el.classList.contains("boxed")) {
      const spread = 26 + 34 * s.lift;
      el.style.boxShadow = `0 ${(10 + 26 * s.lift).toFixed(1)}px ${spread.toFixed(1)}px rgba(44, 33, 20, ${(0.1 + 0.13 * s.lift).toFixed(3)})`;
    }
  }
  for (const b of bandCache) {
    const bx = drift(t, b.phase, 1.1 * b.depth, 9.3, 15.9);
    const by = drift(t, b.phase + 0.8, 2.6 * b.depth, 7.7, 12.1);
    b.node.style.transform = `translate(${bx.toFixed(2)}px, ${by.toFixed(2)}px)`;
  }
  for (const [id, s] of Object.entries(frame.els)) {
    for (const el of document.querySelectorAll(`[data-el="${id}"]`)) {
      el.style.opacity = String(s.opacity);
      el.style.transform = `translate(${s.x.toFixed(2)}px, ${s.y.toFixed(2)}px) scale(${s.scale.toFixed(4)})`;
    }
  }
  const f = frame.focus;
  const mask = focusMask(f);
  for (const el of document.querySelectorAll(".dofSharp")) {
    el.style.maskImage = mask;
    el.style.webkitMaskImage = mask;
  }
  for (const el of document.querySelectorAll(".dofBlur")) {
    el.style.filter = f.blur < 0.05 ? "none" : `blur(${f.blur.toFixed(2)}px)`;
  }
  const bloom = document.querySelector('[data-el="focusBloom"]');
  bloom.style.left = `${f.x}px`;
  bloom.style.top = `${f.y}px`;
}
function render(tracks, t) {
  paint(evaluate(tracks, t));
}
var css = `
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { background: #16140F; }
  .stage { position: relative; overflow: hidden; background: #E7E0D2; }
  /* the beige world reaches every edge; the forge sits low in frame */
  .forge {
    position: absolute; inset: 0;
    background:
      radial-gradient(115% 46% at 50% 112%,
        rgba(168,137,94,0.38) 0%, rgba(168,137,94,0.14) 40%, rgba(168,137,94,0) 70%),
      radial-gradient(90% 34% at 50% -6%,
        rgba(21,19,14,0.05) 0%, rgba(21,19,14,0) 62%);
  }
  .phoneWrap {
    position: absolute; left: 50%; top: 50%;
    width: ${PHONE_W}px; height: ${PHONE_H}px;
    perspective: 2400px;
  }
  .camera { position: absolute; inset: 0; transform-origin: 50% 50%; transform-style: preserve-3d; }
  .layer {
    position: absolute; inset: 0;
    border-radius: ${RADIUS}px; overflow: hidden;
    transform-origin: 50% 50%; will-change: transform, opacity;
  }
  .layer.boxed {
    inset: auto; border-radius: 0; overflow: visible;
    /* follows the banner's alpha, so the shadow is the pill's, not the box's */
    filter: drop-shadow(0 16px 34px rgba(44, 33, 20, 0.26));
  }
  .stageSpace { position: absolute; inset: 0; }
  .stageLayer { border-radius: 0; overflow: visible; }
  .dof { position: absolute; inset: 0; }
  .dofBlur { will-change: filter; }
  .part { position: absolute; inset: 0; transform-origin: 50% 50%; }
  .part svg { width: 100%; height: 100%; display: block; }
  [data-el="lock"], [data-el="lockShackle"], [data-el="lockCopy"], [data-el="finder"],
  [data-el="capture"], [data-el="statusLabel"], [data-el="chip0"], [data-el="chip1"],
  [data-el="chip2"], [data-el="mark"], [data-el="wordmark"], [data-el="tagline"],
  [data-el="toast"] {
    transform-box: fill-box; transform-origin: center;
  }
  .warmGlow {
    position: absolute; left: 215px; top: 330px;
    width: 620px; height: 620px; margin: -310px 0 0 -310px;
    pointer-events: none; opacity: 0; mix-blend-mode: screen;
    background: radial-gradient(circle at 50% 50%,
      rgba(214,176,116,0.62) 0%, rgba(168,137,94,0.30) 34%, rgba(168,137,94,0) 66%);
  }
  /* the brief highlight that lands on whatever the line is about */
  .focusBloom {
    position: absolute; width: 460px; height: 460px; margin: -230px 0 0 -230px;
    pointer-events: none; opacity: 0; mix-blend-mode: screen;
    background: radial-gradient(circle at 50% 50%,
      rgba(226,192,138,0.50) 0%, rgba(190,155,104,0.22) 38%, rgba(168,137,94,0) 70%);
  }
  .filmFade { position: absolute; inset: 0; background: #15130E; opacity: 0; pointer-events: none; }
`;

// src/frame.ts
var style = document.createElement("style");
style.textContent = css;
document.head.append(style);
var format = new URLSearchParams(location.search).get("format") ?? "vertical";
build(document.getElementById("root"), format);
render(film, 0);
window.setTime = (t) => render(film, t);
document.fonts.ready.then(() => {
  window.ready = true;
});
