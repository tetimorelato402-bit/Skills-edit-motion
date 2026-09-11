#!/usr/bin/env python3
"""The texture layer — recorded objects under the synthesised cues.

`sound.py` is synthesised end to end, and that is deliberate: every cue is
derived from the film's own constants, so a re-timed beat re-scores itself.
This file does NOT change that. It adds a thin second layer at six moments
where a real recorded object makes the painted world feel physical:

    the grain dissolve · the paint wipe · the ball's two contacts ·
    the drag · the page turning up · the mark opening

Those six were chosen the same way everything else here was: the Source
Recordings half of Ocular Sounds' *Vector* (paper, wood, cloth, metal — real
objects, miked) belongs in this film. The DSGNSynth / UIData / UIGlitch half
is the cold generic post, sonically, and the film exists to argue against it.

TWO MODES.

  1. The library is present. Point OCULAR_LIB at it (or drop it in ./lib/):
         export OCULAR_LIB=/path/to/Vector
     Each cue names its candidate files; the first one found is loaded,
     resampled 96k->48k and TRANSIENT-ALIGNED, so `t` is when you hear it,
     not when the file starts. Library one-shots carry 10-80 ms of pre-roll
     and the film's cues are 120 ms apart at the tightest — unaligned, they
     flam against the drums.

  2. The library is absent. Every cue falls back to a synthesised stand-in
     built to the same character (`STAND_INS` below). These are NOT the
     library. They are here so the arrangement can be judged before anyone
     pays for or imports 1136 files.

Run `python3 texture.py` to see which mode each cue resolved to.
"""
import numpy as np, wave, os, glob

SR = 48000
_rng = np.random.default_rng(11)

LIB = os.environ.get('OCULAR_LIB') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'lib')

# ---- helpers borrowed in spirit from sound.py -------------------------------
def _ma(x, k):
    if k < 2: return x
    return np.convolve(x, np.ones(k)/k, mode='same')
def _hp(x, k): return x - _ma(x, k)
def _secs(d): return int(SR*d)
def _env(n, tau): return np.exp(-np.linspace(0, 1, n)/tau)


# ============================================================================
# reading the library
# ============================================================================
def _read_wav(path):
    """Any bit depth the library ships (it is 24-bit/96k) -> float mono."""
    with wave.open(path, 'rb') as w:
        ch, sw, fr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw == 2:
        a = np.frombuffer(raw, dtype='<i2').astype(np.float64)/32768.0
    elif sw == 3:                                   # 24-bit packed, sign-extended
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        v = np.where(v & 0x800000, v - 0x1000000, v)
        a = v.astype(np.float64)/8388608.0
    elif sw == 4:
        a = np.frombuffer(raw, dtype='<i4').astype(np.float64)/2147483648.0
    else:
        raise ValueError(f'{path}: unsupported sample width {sw}')
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)           # mono; put() does the panning
    return _resample(a, fr, SR)


def _resample(x, fr, to):
    """96k -> 48k. Average before decimating so the top octave does not alias."""
    if fr == to: return x
    if fr > to:
        k = max(2, int(round(fr/to)))
        x = _ma(x, k)
    n = int(round(len(x)*to/fr))
    return np.interp(np.linspace(0, len(x)-1, n), np.arange(len(x)), x)


def _align(x, thr=0.12):
    """Drop the pre-roll so the TRANSIENT lands on t, not the file's first sample.

    Finds the first sample past `thr` of peak, then backs up to where the
    envelope actually leaves the floor so the attack is not clipped off.
    """
    if len(x) == 0: return x
    pk = np.abs(x).max()
    if pk <= 0: return x
    e = _ma(np.abs(x), 24)
    hits = np.nonzero(e >= thr*pk)[0]
    if len(hits) == 0: return x
    i = hits[0]
    floor = 0.02*pk
    while i > 0 and e[i-1] > floor:
        i -= 1
    return x[i:]


def _find(names):
    """First candidate that exists under LIB. Names are matched loosely so the
    vendor's `_Ocular_Vector_02.wav` suffixes do not have to be typed out."""
    if not os.path.isdir(LIB): return None
    for name in names:
        stem = name.lower().replace('.wav', '')
        for p in glob.glob(os.path.join(LIB, '**', '*.wav'), recursive=True):
            if stem in os.path.basename(p).lower():
                return p
    return None


# ============================================================================
# the stand-ins — what each cue sounds like until the library is present
#
# These are written as RECORDINGS, not as synth cues: each one gets a noise
# floor and a short room tail, because that is most of what separates a miked
# object from a generated one at phone size.
# ============================================================================
def _recorded(x, room=0.10, floor=0.0016):
    """Give a generated signal the two tells of a real recording."""
    n = len(x)
    tail = _ma(_rng.standard_normal(n), 300)*np.exp(-np.linspace(0, 1, n)*5.0)
    return x + tail*room*np.abs(x).max() + _rng.standard_normal(n)*floor


def paper_drag(dur, gain=1.0):
    """PAPRFric — a fibrous edge dragged across a surface. Granular, not smooth:
    the grain is what separates paper from a noise sweep."""
    n = _secs(dur); u = np.linspace(0, 1, n)
    grain = np.abs(_ma(_rng.standard_normal(n), 5))**1.5      # fibre catching
    body = _hp(_rng.standard_normal(n), 9)*0.7 + _ma(_rng.standard_normal(n), 4)*0.3
    e = np.sin(np.pi*u)**0.9*(0.55 + 0.45*u)
    return _recorded(body*grain*3.0*e)*gain


def crumple(dur, gain=1.0):
    """PAPRHndl — sheet handled and released. Sparse sharp cracks with a tiny
    resonance each, densifying, over a bed of fibre rustle."""
    n = _secs(dur); u = np.linspace(0, 1, n); s = np.zeros(n)
    dens = 0.25 + 0.75*u**1.6
    for _ in range(52):
        i = int(np.clip(_rng.random()**0.7, 0, 1)*(n-1))
        if _rng.random() > dens[i]: continue
        d = _secs(0.004 + 0.010*_rng.random()); j = min(n, i+d)
        f = 1400 + 2600*_rng.random()
        t = np.arange(j-i)/SR
        crack = np.sin(2*np.pi*f*t)*_env(j-i, 0.14)*(0.3 + 0.7*_rng.random())
        crack += _hp(_rng.standard_normal(j-i), 3)*_env(j-i, 0.10)*0.8
        s[i:j] += crack
    rustle = _hp(_rng.standard_normal(n), 6)*_ma(np.abs(_rng.standard_normal(n)), 7)*dens*0.5
    return _recorded(s*0.55 + rustle)*gain


def ball_metal(f0=430.0, dur=0.9, gain=1.0):
    """METLImpt — a dampened tonal ball. Inharmonic partials, a noise attack,
    and a decay long enough to ring under the next bar."""
    n = _secs(dur); t = np.arange(n)/SR; s = np.zeros(n)
    for r, a, dec in [(1.00, 1.00, 3.2), (2.03, 0.52, 4.6), (3.41, 0.30, 6.4),
                      (4.72, 0.17, 8.8), (6.15, 0.09, 12.0)]:
        s += np.sin(2*np.pi*f0*r*t + _rng.random()*6.28)*a*np.exp(-t*dec)
    atk = _secs(0.005)
    s[:atk] += _hp(_rng.standard_normal(atk), 3)*_env(atk, 0.30)*1.4
    s *= np.minimum(1, t/0.0012)
    return _recorded(s*0.5, room=0.16)*gain


def friction_drag(dur, gain=1.0):
    """RUBRFric / WOODFric — something held and pulled. A slow stick-slip
    modulation, so it reads as effort rather than as a whoosh."""
    n = _secs(dur); u = np.linspace(0, 1, n)
    slip = 0.6 + 0.4*np.sin(2*np.pi*np.cumsum(np.full(n, 17.0/SR)) + 
                            _ma(_rng.standard_normal(n), 200)*9)
    body = _ma(_rng.standard_normal(n), 14)*0.8 + _hp(_rng.standard_normal(n), 22)*0.4
    e = np.minimum(1, u/0.06)*np.minimum(1, (1-u)/0.18)
    return _recorded(body*slip*2.2*e)*gain


def page_turn(dur, gain=1.0):
    """PAPRHndl — a sheet turning over. Broadband, with the flutter of the
    sheet passing rather than a clean filtered sweep."""
    n = _secs(dur); u = np.linspace(0, 1, n)
    flutter = 1 + 0.5*np.sin(2*np.pi*np.linspace(0, 9*dur, n))*np.sin(np.pi*u)
    dark, bright = _ma(_rng.standard_normal(n), 40), _hp(_rng.standard_normal(n), 7)
    s = (dark*(1-u) + bright*u)*flutter*np.sin(np.pi*u)**1.3
    return _recorded(s*1.6)*gain


def plastic_pop(gain=1.0):
    """PLASHndl / UIAlert_POPUP — a small lid releasing. A body mode plus the
    click of the release; short, dry, and clearly an object."""
    n = _secs(0.16); t = np.arange(n)/SR
    f = 620*np.exp(-t*30) + 190
    s = np.sin(2*np.pi*np.cumsum(f)/SR)*_env(n, 0.13)
    s += np.sin(2*np.pi*1830*t)*_env(n, 0.05)*0.35
    atk = _secs(0.003)
    s[:atk] += _hp(_rng.standard_normal(atk), 2)*_env(atk, 0.4)*1.1
    return _recorded(s*0.7, room=0.14)*gain


# ============================================================================
# THE SIX CUES
#
# Each names the library candidates it wants (in preference order) and the
# stand-in to use until one of them is on disk. `dur` is passed to the
# stand-in; a loaded file uses its own length.
# ============================================================================
CUES = {
    'dissolve': dict(
        files=['PAPRHndl_SOURCE RECORDINGS-Paper Crumple',
               'PAPRHndl_SOURCE RECORDINGS-Paper Handle',
               'PAPRHndl_SOURCE RECORDINGS-Paper'],
        stand_in=lambda d, g: crumple(d, g), kind='crumple()', dur=0.48, gain=0.16,
        note='the grain dissolve, bt(3)'),
    'wipe': dict(
        files=['PAPRFric_SOURCE RECORDINGS-Calendar Scraping 03',
               'PAPRFric_SOURCE RECORDINGS-Calendar Scraping',
               'UIMisc_FOLEY-Brushed Cards'],
        stand_in=lambda d, g: paper_drag(d, g), kind='paper_drag()', dur=0.48, gain=0.22,
        note='the paint wipe crossing, bt(7)'),
    'ball_1': dict(
        files=['METLImpt_SOURCE RECORDINGS-Tonal Chinese Balls Dampened Resonant 01',
               'METLImpt_SOURCE RECORDINGS-Tonal Chinese Balls Dampened'],
        stand_in=lambda d, g: ball_metal(430.0, d, g), kind='ball_metal()', dur=0.90, gain=0.13,
        note="the ball's first contact"),
    'ball_2': dict(
        files=['METLImpt_SOURCE RECORDINGS-Tonal Chinese Balls Dampened Resonant 03',
               'METLImpt_SOURCE RECORDINGS-Tonal Chinese Balls Dampened'],
        stand_in=lambda d, g: ball_metal(560.0, d, g), kind='ball_metal()', dur=0.55, gain=0.09,
        note="the ball's second, smaller contact"),
    'drag': dict(
        files=['RUBRFric_SOURCE RECORDINGS-Rubber',
               'WOODFric_SOURCE RECORDINGS-Wood'],
        stand_in=lambda d, g: friction_drag(d, g), kind='friction_drag()', dur=0.48, gain=0.10,
        note='the handle dragged, bt(23)->bt(24)'),
    'page': dict(
        files=['PAPRHndl_SOURCE RECORDINGS-Paper Page Turn',
               'PAPRHndl_SOURCE RECORDINGS-Paper Handle',
               'PAPRHndl_SOURCE RECORDINGS-Paper'],
        stand_in=lambda d, g: page_turn(d, g), kind='page_turn()', dur=0.30, gain=0.15,
        note='the page turns up into the end card'),
    'mark': dict(
        files=['UIAlert_POPUP-Clicky PopUp', 'PLASHndl_SOURCE RECORDINGS-Plastic'],
        stand_in=lambda d, g: plastic_pop(g), kind='plastic_pop()', dur=0.16, gain=0.18,
        note='the mark opens, bt(40)+0.24'),
}

_cache = {}
_report = []

def tex(key, gain=None):
    """The signal for one cue — the library file if it is on disk, else the
    stand-in. Cached, so a cue used twice costs one read."""
    if key in _cache:
        sig, g = _cache[key]
    else:
        c = CUES[key]
        p = _find(c['files'])
        if p is not None:
            sig = _align(_read_wav(p))
            sig = sig/max(1e-9, np.abs(sig).max())
            _report.append((key, 'LIBRARY', os.path.basename(p)))
        else:
            sig = c['stand_in'](c['dur'], 1.0)
            sig = sig/max(1e-9, np.abs(sig).max())
            _report.append((key, 'stand-in', c['kind']))
        g = c['gain']
        _cache[key] = (sig, g)
    return sig*(g if gain is None else gain)


def report():
    lines = [f'texture: LIB={LIB}' + ('' if os.path.isdir(LIB) else '  (not present)')]
    for k, mode, what in _report:
        lines.append(f'  {k:<9} {mode:<8} {what}')
    return '\n'.join(lines)


if __name__ == '__main__':
    for k in CUES: tex(k)
    print(report())
    print('\ncandidates per cue (first found wins):')
    for k, c in CUES.items():
        print(f'  {k:<9} {c["note"]}')
        for f in c['files']: print(f'             {f}')
