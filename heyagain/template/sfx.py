"""hey again. — the sound bank.

The first pass reused one identical clack for every letter, which is what made it read as
a machine rather than a person. Here each strike is drawn from a bank of variants with
different body pitch, wood resonance and decay, then given its own velocity, so no two
keystrokes in a reel are the same sample at the same level.
"""
import math, random, struct, wave

SR = 44100


def _norm(buf, peak):
    m = max(1e-9, max(abs(v) for v in buf))
    return [v * peak / m for v in buf]


def _key(rng, bright=1.0):
    """One typewriter key: a filtered strike, a wooden resonance, a low thock.

    The strike is low-passed rather than differentiated. A differentiated noise burst is
    what gave the old version its harsh plasticky edge.
    """
    dur = 0.085
    n = int(SR * dur)
    f_body = rng.uniform(148, 236)          # the mechanism
    f_res = rng.uniform(760, 1480)          # the wood around it
    bw = rng.uniform(90, 220)               # how ringy that resonance is
    d_strike = rng.uniform(210, 360)
    d_body = rng.uniform(58, 115)
    lp_a = rng.uniform(0.28, 0.46)          # lower = duller strike

    r = math.exp(-math.pi * bw / SR)
    w0 = 2 * math.pi * f_res / SR
    a1, a2 = 2 * r * math.cos(w0), -r * r

    out, lp, y1, y2 = [], 0.0, 0.0, 0.0
    for i in range(n):
        t = i / SR
        lp += lp_a * (rng.uniform(-1, 1) - lp)
        strike = lp * math.exp(-d_strike * t)
        y0 = strike + a1 * y1 + a2 * y2
        y2, y1 = y1, y0
        body = math.sin(2 * math.pi * f_body * t) * math.exp(-d_body * t)
        out.append(0.58 * bright * strike + 0.14 * y0 + 0.46 * body)
    return _norm(out, 1.0)


def _space(rng):
    """The space bar: broader, duller, no bite."""
    dur = 0.075
    n = int(SR * dur)
    f_body = rng.uniform(96, 138)
    d_body = rng.uniform(48, 84)
    d_strike = rng.uniform(150, 240)
    out, lp = [], 0.0
    for i in range(n):
        t = i / SR
        lp += 0.22 * (rng.uniform(-1, 1) - lp)
        out.append(0.30 * lp * math.exp(-d_strike * t)
                   + 0.70 * math.sin(2 * math.pi * f_body * t) * math.exp(-d_body * t))
    return _norm(out, 1.0)


def _thud(f0, decay):
    n = int(SR * 0.34)
    out, prev = [], 0.0
    rng = random.Random(int(f0 * 100))
    for i in range(n):
        t = i / SR
        env = math.exp(-decay * t)
        body = math.sin(2 * math.pi * f0 * t * (1 - 0.25 * t))
        prev += 0.3 * (rng.uniform(-1, 1) - prev)
        out.append(body * env + prev * math.exp(-230 * t) * 0.22)
    return _norm(out, 1.0)


def _swell():
    dur, n = 0.55, int(SR * 0.55)
    out = []
    for i in range(n):
        t = i / SR
        env = math.sin(math.pi * min(1, t / dur)) ** 2
        out.append(math.sin(2 * math.pi * (220 + 520 * (t / dur)) * t) * env)
    return _norm(out, 1.0)


def _pop():
    n = int(SR * 0.16)
    out = []
    for i in range(n):
        t = i / SR
        out.append(math.sin(2 * math.pi * (520 + 900 * math.exp(-26 * t)) * t) * math.exp(-34 * t))
    return _norm(out, 1.0)


def _chime():
    n = int(SR * 1.5)
    out = []
    for i in range(n):
        t = i / SR
        out.append(math.sin(2 * math.pi * 784 * t) * math.exp(-3.0 * t)
                   + 0.55 * math.sin(2 * math.pi * 1176 * t) * math.exp(-4.0 * t)
                   + 0.30 * math.sin(2 * math.pi * 1568 * t) * math.exp(-5.5 * t))
    return _norm(out, 1.0)


class Bank:
    """Level balance lives here, so one number moves the whole track."""

    def __init__(self, seed=5, keys=14, master=0.58,
                 key_level=0.21, space_level=0.13,
                 thud_level=0.60, swell_level=0.17, pop_level=0.22, chime_level=0.20):
        rng = random.Random(seed)
        self.keys = [_key(rng, bright=rng.uniform(0.78, 1.06)) for _ in range(keys)]
        self.spaces = [_space(rng) for _ in range(5)]
        self.thuds = {"thud": _thud(92, 17.0), "thud2": _thud(104, 19.0), "thud3": _thud(116, 22.0)}
        self.swell, self.pop, self.chime = _swell(), _pop(), _chime()
        self.master = master
        self.level = dict(key=key_level, space=space_level,
                          thud=thud_level, thud2=thud_level * 0.62, thud3=thud_level * 0.38,
                          swell=swell_level, pop=pop_level, chime=chime_level)
        self.rng = random.Random(seed + 1)

    def pick(self, kind):
        if kind == "key":
            return self.rng.choice(self.keys)
        if kind == "space":
            return self.rng.choice(self.spaces)
        if kind in self.thuds:
            return self.thuds[kind]
        return {"swell": self.swell, "pop": self.pop, "chime": self.chime}[kind]

    def velocity(self, kind):
        # a person does not hit every key with the same force
        if kind in ("key", "space"):
            return self.rng.uniform(0.74, 1.06)
        return 1.0


def render(events, total, path, bank=None, extra_jitter=0.010):
    """events: [(time, kind)]. Writes a mono 16-bit wav."""
    bank = bank or Bank()
    buf = [0.0] * int(SR * (total + 1.8))
    jit = random.Random(99)
    for t, kind in events:
        s = bank.pick(kind)
        amp = bank.level[kind] * bank.velocity(kind)
        tt = t + (jit.uniform(-extra_jitter, extra_jitter) if kind in ("key", "space") else 0.0)
        off = int(max(0.0, tt) * SR)
        for i, v in enumerate(s):
            j = off + i
            if j < len(buf):
                buf[j] += v * amp
    buf = _norm(buf, bank.master)
    with wave.open(path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in buf))
    return path
