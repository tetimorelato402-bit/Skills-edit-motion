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
var STAGE = {
  width: 1920,
  height: 1080,
  fps: 30,
  /** phone is 430×932; this puts it at 857 px tall in a 1080 frame */
  phoneScale: 0.92
};
var LOCK = { x: 215, y: 330 };
var CLANG_AT = ARRIVE.off;
var HEAD = 0.35;
var OPEN_IN = 0.535;
var CROSS_Q = 0.32;
var CROSS_T = 0.18;
var CROSS_ACT = 0.34;
var CROSS = 0.44;
var PUSH = 0.6;
var TOAST_IN = 0.26;
var SHACKLE = 0.18;
var UNLOCK = 0.396;
var CUT_PROOF = 0.24;
var CUT_SEEN = 0.2;
var CROSS_LONG = 0.26;
var openAt = HEAD;
var act1 = [
  { k: "hold", at: 0, dur: HEAD, note: "the beige world, empty, before the voice" },
  {
    k: "layer",
    id: "name",
    at: openAt,
    dur: OPEN_IN,
    via: "settleIn",
    note: "01 settles at 0.885"
  },
  {
    k: "hold",
    at: openAt + OPEN_IN,
    dur: NAME.off - (openAt + OPEN_IN),
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
var toastAt = ARRIVE.on - LEAD - TOAST_IN;
var act2 = [
  {
    k: "cross",
    out: "places",
    in: "home",
    at: toHome,
    dur: CROSS_ACT,
    depth: 400,
    note: "into Act 2 \u2014 the film slows here"
  },
  {
    k: "hold",
    at: homeIn,
    dur: HOME.on - homeIn,
    note: "act boundary: the lead is the hold"
  },
  {
    k: "hold",
    at: HOME.on,
    dur: HOME.off - HOME.on,
    note: "still under 'This is your word.'"
  },
  {
    k: "cross",
    out: "home",
    in: "locked",
    at: toLocked,
    dur: CROSS,
    depth: 400,
    note: "06_home \u2192 07_tab_camera"
  },
  {
    k: "cam",
    at: pushAt,
    dur: PUSH,
    to: { fx: LOCK.x, fy: LOCK.y, scale: 1.5, center: 0.68 },
    note: "focusPush into the lock \u2014 starts on silence, still moving at 10.307"
  },
  // 0.63 s of absolute stillness, landing while she is still speaking and
  // running past the end of the line. Nothing else in the film holds this
  // long. It is what the Act 4 snap releases from.
  {
    k: "hold",
    at: holdAt,
    dur: toastAt - holdAt,
    note: "the uncomfortable hold \u2014 0.812 s, dead still at full push"
  }
];
var releaseAt = ARRIVE.off;
var unlockAt = releaseAt + SHACKLE;
var opened = unlockAt + UNLOCK;
var act3 = [
  {
    k: "part",
    id: "toast",
    at: toastAt,
    dur: TOAST_IN,
    via: "revealUp",
    opts: { distance: 30, from: "above" },
    note: "arrival banner drops onto the still-locked screen"
  },
  {
    k: "hold",
    at: toastAt + TOAST_IN,
    dur: releaseAt - (toastAt + TOAST_IN),
    note: "still under 'Until you actually arrive.'"
  },
  { k: "sfx", at: releaseAt, src: "clang", gain: 0.9, note: "the strike, on top, never ducked" },
  {
    k: "el",
    id: "lockShackle",
    at: releaseAt,
    dur: SHACKLE,
    from: { y: 0 },
    to: { y: -7 },
    note: "the shackle lifts \u2014 the only thing moving"
  },
  {
    k: "el",
    id: "lock",
    at: unlockAt,
    dur: UNLOCK,
    from: { opacity: 1, scale: 1 },
    to: { opacity: 0, scale: 0.86 }
  },
  {
    k: "el",
    id: "lockCopy",
    at: unlockAt,
    dur: UNLOCK * 0.6,
    from: { opacity: 1 },
    to: { opacity: 0 }
  },
  {
    k: "cross",
    out: "locked",
    in: "opened",
    at: unlockAt,
    dur: UNLOCK,
    depth: 150,
    aperture: { x: LOCK.x, y: LOCK.y, radius: 660 },
    note: "07 \u2192 09, opening out of the lock's own centre; the banner rides out with the layer it belongs to"
  },
  // no track on #finder: the aperture opens out of the lock's centre, so the
  // viewfinder is already revealed from the middle outward.
  {
    k: "el",
    id: "warmGlow",
    at: unlockAt,
    dur: 0.52,
    from: { opacity: 0, scale: 0.4 },
    to: { opacity: 1, scale: 1 },
    note: "warm light shift, blooming out of the lock"
  },
  {
    k: "el",
    id: "warmGlow",
    at: unlockAt + 0.52,
    dur: 0.83,
    from: { opacity: 1 },
    to: { opacity: 0.32, scale: 1.16 },
    note: "and settling back \u2014 light that arrived, not a lamp left on"
  },
  {
    k: "cam",
    at: unlockAt,
    dur: UNLOCK,
    to: { fx: LOCK.x, fy: LOCK.y, scale: 1.06, center: 0.2 },
    note: "the frame opens up as the lock lets go"
  },
  {
    k: "cam",
    at: opened,
    dur: 0.82,
    to: { fx: 215, fy: 466, scale: 1, center: 0 },
    note: "the last of the pull-back, decelerating under the line"
  },
  { k: "hold", at: opened, dur: LEAD, note: "the aftermath \u2014 09 settled at 13.480" },
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
  locked: { space: "phone", screens: ["07_locked", "08_toast"] },
  opened: { space: "phone", screens: ["09_unlocked"] },
  proof: { space: "phone", screens: ["11_circle_live"] },
  seen: { space: "phone", screens: ["10_friend_arrived"] },
  routine: { space: "phone", screens: ["07_tab_routine"] },
  logo: { space: "stage", screens: ["logo"] }
};
var film = [...act1, ...act2, ...act3, ...act4, ...act5, ...ending];
var SECTION = {
  full: { from: 0, to: filmEnds },
  act1: { from: 0, to: HOME.on },
  act23: { from: PLACES.off, to: OPENS.off },
  act45: { from: OPENS.off, to: voiceEnds },
  end: { from: voiceEnds - 0.6, to: filmEnds }
};
var duration = filmEnds;
export {
  CLANG_AT,
  LAYERS,
  LEAD,
  LOCK,
  SECTION,
  STAGE,
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
