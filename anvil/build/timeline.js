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
var STAGE = { fps: 30 };
var LOCK = { x: 215, y: 330 };
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
var duration = filmEnds;
export {
  FORMATS,
  LAYERS,
  LEAD,
  LOCK,
  SECTION,
  STAGE,
  SUBJECT,
  VO,
  VO_AT,
  act1,
  act2,
  act3,
  act4,
  act5,
  duration,
  ending,
  film
};
