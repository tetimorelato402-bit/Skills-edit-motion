#!/usr/bin/env python3
"""Sound for Study 001 — a beat, and a sound for every motion.

There is no music. This file IS the soundtrack: nothing gets added in Instagram.

Tempo. At 75 BPM counted from frame 0 the film is exactly six bars of 4/4
(19.2 s = 24 quarter notes of 0.8 s). That is not a coincidence we planned, but it
is one we keep: the snap into the title (1.6), the centre of the ease drag (9.6),
the end-card name (16.0) and the loop point (19.2) all sit on quarter notes, and
every cut (4.2, 8.2, 12.2) lands exactly one sixteenth after a quarter — a pushed
kick, the same push every time, which is what makes it read as a groove and not
as drift. Drums live on the grid; the sounds of motion live on the motion.

Every cue time below is derived from the same constants and easing curves as
video.html (the bezier solver is ported verbatim), so if a beat moves in the film
the sounds move with it. Run it after any timing change:

    python3 sound.py              # writes sound.wav next to this file
    python3 sound.py out.wav

Underneath, very low, there is a jazz bed — teti's ask after hearing v7. An upright
bass walks the six bars, a Rhodes comps rootless voicings (Dm9, Gm9, C9, Bbmaj9,
Em7b5, A7b9, Dm6/9) on pushed beats, and a soft ride marks the quarters while the
hats sit on the swung skip — so the beat swings rather than fights it. The harmony
is a descending minor line (Dm — Gm — C — Bb — A7) that resolves V→i on the downbeat
of bar 4, which is 9.6: the bend lands on a chord change, not just a beat.

Instruments are synthesised from noise and sines — there are no samples. The
palette is deliberately warm and dry (the film is an oil painting, not a screen):
kicks are round, hats are paper-dry, the "bend" is a saturated sawtooth whose
pitch follows the exact easeInOut of the drag. An ease made audible.
"""
import numpy as np, wave, os, sys

SR   = 48000
DUR  = 19.2
N    = int(SR*DUR)
rng  = np.random.default_rng(7)
L    = np.zeros(N); R = np.zeros(N)

# ---- the film's own timeline (mirror of video.html) ------------------------
B1=(0.0,1.6); B2=(1.6,4.2); B3=(4.2,8.2); B4=(8.2,12.2); B5=(12.2,15.8); B6=(15.8,19.2)
PRE=0.26; PRES=[0,0.40,0.44,PRE,PRE,PRE]

def bez(x1,y1,x2,y2):
    cx=3*x1; bx=3*(x2-x1)-cx; ax=1-cx-bx
    cy=3*y1; by=3*(y2-y1)-cy; ay=1-cy-by
    fx=lambda t:((ax*t+bx)*t+cx)*t; fy=lambda t:((ay*t+by)*t+cy)*t
    dfx=lambda t:(3*ax*t+2*bx)*t+cx
    def f(x):
        if x<=0: return 0.0
        if x>=1: return 1.0
        t=x
        for _ in range(8):
            e=fx(t)-x
            if abs(e)<1e-6: break
            d=dfx(t)
            if abs(d)<1e-6: break
            t-=e/d
        return fy(t)
    return f
easeOut  =bez(0.16,1,0.3,1)
easeInOut=bez(0.65,0,0.35,1)
antic    =bez(0.6,-0.42,0.32,1.5)     # pull back, then launch
backOut  =bez(0.28,1.42,0.44,1)       # beat 4 layers
backOut5 =bez(0.22,1.36,0.36,1)       # MOVE. in the hero line
backOut6 =bez(0.24,1.52,0.4,1)        # name morph and the joke
EAS      =(0.14,0.96,0.32,1.0)        # the ease the cursor drags the curve to
fE       =bez(*EAS)

def first_at(f,thr,lo=0.0):
    """first x in [lo,1] where f(x)>=thr — 'when does this ease arrive'"""
    for x in np.linspace(lo,1,4001):
        if f(x)>=thr: return float(x)
    return 1.0
def min_at(f):
    xs=np.linspace(0,1,4001); v=[f(x) for x in xs]; return float(xs[int(np.argmin(v))])
def peak_at(f):
    xs=np.linspace(0,1,4001); v=[f(x) for x in xs]; return float(xs[int(np.argmax(v))])

ANTIC_DIP  =min_at(antic)                        # 0.156  the pull-back is deepest
ANTIC_GO   =first_at(antic,0.0,ANTIC_DIP)        # 0.278  it leaves
ANTIC_HIT  =first_at(antic,1.0,ANTIC_DIP)        # 0.645  it reaches the mark
BACK_HIT   =first_at(backOut,1.0)                # 0.347
BACK5_HIT  =first_at(backOut5,1.0)               # 0.327
BACK6_HIT  =first_at(backOut6,1.0)               # 0.276

# ---- dsp helpers -----------------------------------------------------------
def ma(x,k):                       # moving average = cheap low-pass
    if k<2: return x
    return np.convolve(x, np.ones(k)/k, mode='same')
def hp(x,k):  return x - ma(x,k)   # high-pass
def env_exp(n,tau): return np.exp(-np.linspace(0,1,n)/tau)
def secs(d): return int(SR*d)
def tvec(n): return np.arange(n)/SR
def mix(*sigs):                    # sum signals of different lengths
    n=max(len(s) for s in sigs); out=np.zeros(n)
    for s in sigs: out[:len(s)]+=s
    return out
def place(buf,sig,t):
    i=int(round(t*SR)); j=min(N,i+len(sig))
    if i>=N or j<=i: return
    buf[i:j]+=sig[:j-i]
def put(sig,t,pan=0.0,gain=1.0):
    """equal-power pan, -1 left … +1 right"""
    a=(pan+1)*np.pi/4
    place(L,sig*gain*np.cos(a),t); place(R,sig*gain*np.sin(a),t)
def put_st(l,r,t,gain=1.0): place(L,l*gain,t); place(R,r*gain,t)

# ---- instruments -----------------------------------------------------------
def click(dur=0.035,tau=0.12,k=6,gain=1.0):
    n=secs(dur); x=rng.standard_normal(n)*env_exp(n,tau)
    return hp(x,k)*gain
def tick(gain=1.0):                # small UI tick, bright and short
    return click(0.018,0.09,4,gain)
def thud(f0=95,f1=52,dur=0.34,tau=0.16,gain=1.0):
    n=secs(dur); f=np.linspace(f0,f1,n); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env_exp(n,tau)*gain
def kick(gain=1.0,f0=170,f1=43,dur=0.46,tau=0.22):
    """round, dry, a little saturated — the film is a painting, not a club"""
    n=secs(dur); t=tvec(n)
    f=f1+(f0-f1)*np.exp(-t*34)                       # the pitch drops fast
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*env_exp(n,tau)
    s=mix(body, click(0.007,0.3,3,0.45))
    return np.tanh(s*1.7)/np.tanh(1.7)*gain
def snare(gain=1.0):
    n=secs(0.17); t=tvec(n); x=rng.standard_normal(n)
    nz=hp(x,3)*env_exp(n,0.17)
    body=np.sin(2*np.pi*185*t)*env_exp(n,0.09)*0.7+np.sin(2*np.pi*330*t)*env_exp(n,0.05)*0.3
    return (nz*0.75+body)*gain
def rim(gain=1.0):
    n=secs(0.05); t=tvec(n)
    return (click(0.05,0.08,3,0.7)[:n]+np.sin(2*np.pi*880*t)*env_exp(n,0.05)*0.5)*gain
def hat(gain=1.0,open_=False):
    n=secs(0.15 if open_ else 0.034); x=hp(rng.standard_normal(n),2)
    return x*env_exp(n,0.32 if open_ else 0.24)*gain
def sub(freq,dur,gain=1.0,atk=0.012):
    """the bass note under a kick — a sine with a touch of octave so phones hear it"""
    n=secs(dur); t=tvec(n)
    s=np.sin(2*np.pi*freq*t)+0.38*np.sin(2*np.pi*2*freq*t)
    e=np.minimum(1,t/atk)*np.exp(-t/(dur*0.42))
    return s*e*gain
def pluck(freq,dur=0.55,gain=1.0,bright=0.55):
    n=secs(dur); t=tvec(n); s=np.zeros(n)
    for h in range(1,7):                                  # upper partials die first
        s+=np.sin(2*np.pi*freq*h*t+rng.random()*6.28)*(bright**(h-1))*np.exp(-t*(2.2+h*2.4))
    return s*np.minimum(1,t/0.0025)*gain
def type_tick(freq,gain=1.0):
    """a felt hammer on paper: click plus a short resonant body"""
    n=secs(0.07); t=tvec(n)
    body=np.sin(2*np.pi*freq*t)*env_exp(n,0.11)
    return (click(0.07,0.05,5,0.55)[:n]+body*0.9)*gain
def shutter(gain=1.0,firm=False):
    """two tiny clicks 9 ms apart — a carriage return, a camera shutter"""
    a=click(0.012,0.10,3,1.0); b=click(0.014,0.12,4,0.8)
    n=secs(0.04); s=np.zeros(n); s[:len(a)]+=a; i=secs(0.009); s[i:i+len(b)]+=b[:n-i]
    if firm: s=mix(s,thud(320,130,0.04,0.25,0.6))
    return s*gain
def whoosh(dur=0.32,rise=True,gain=1.0,tilt=(90,10)):
    n=secs(dur); x=rng.standard_normal(n)
    dark, bright = ma(x,tilt[0]), hp(x,tilt[1])
    u=np.linspace(0,1,n); u = u if rise else u[::-1]
    body = dark*(1-u) + bright*u
    e=np.sin(np.pi*np.linspace(0,1,n))**1.6
    return body*e*gain
def brush(dur,gain=1.0):
    """a loaded brush dragged across canvas: dark noise with bristle jitter"""
    n=secs(dur); x=rng.standard_normal(n)
    jit=np.abs(ma(rng.standard_normal(n),9))*3.2            # the bristles
    body=ma(x,7)*jit
    u=np.linspace(0,1,n); e=np.sin(np.pi*u)**1.1*(0.6+0.4*u)  # heavier as it arrives
    return body*e*gain
def slide(dur,gain=1.0):
    """the mouse moving on a desk: soft, dark, almost nothing"""
    n=secs(dur); x=ma(rng.standard_normal(n),46)
    return x*np.sin(np.pi*np.linspace(0,1,n))**2*gain*7
def draw(dur,gain=1.0):
    """a rule drawn with a pen: thin bright noise, thinning as it goes"""
    n=secs(dur); x=hp(rng.standard_normal(n),3)
    e=np.linspace(1,0.35,n)*np.minimum(1,np.arange(n)/secs(0.012))
    return x*e*gain
def crackle(dur,gain=1.0):
    """the grain dissolve: the frame breaks up through the tooth of the canvas"""
    n=secs(dur); u=np.linspace(0,1,n); dens=u**2
    imp=(rng.random(n)<dens*0.03)*rng.standard_normal(n)
    return (ma(imp,3)*2.5 + hp(rng.standard_normal(n),4)*dens*0.14)*gain
def suck(dur,gain=1.0):
    """a reverse whoosh with a rising pitch — something collapsing to a point"""
    n=secs(dur); u=np.linspace(0,1,n); x=rng.standard_normal(n)
    body=ma(x,30)*(1-u)+hp(x,6)*u
    f=240*2**(u*2.4); ph=2*np.pi*np.cumsum(f)/SR
    return (body*0.7+np.sin(ph)*0.3)*(u**1.6)*gain
def pop(gain=1.0):
    n=secs(0.09); f=np.linspace(980,360,n); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env_exp(n,0.17)*gain
def bloom(freqs,dur=1.4,gain=1.0):
    """a soft warm chord — the mark arriving"""
    n=secs(dur); t=tvec(n); s=np.zeros(n)
    for f in freqs:
        s+=np.sin(2*np.pi*f*t+rng.random()*6.28)+0.25*np.sin(2*np.pi*2*f*t)
    e=np.minimum(1,t/0.05)*env_exp(n,0.36)
    return ma(s,2)*e*gain/len(freqs)
def squash(gain=1.0):
    """the ball lands: a deep thud and a pitch-dropping squelch"""
    n=secs(0.5); t=tvec(n)
    f=58+(220-58)*np.exp(-t*24); ph=2*np.pi*np.cumsum(f)/SR
    boing=np.sin(ph)*env_exp(n,0.22)
    return mix(boing*0.8, thud(85,40,0.5,0.26,0.9), click(0.02,0.2,4,0.3))*gain
def room(dur,gain=1.0):
    n=secs(dur); x=ma(rng.standard_normal(n),400)
    e=np.clip(np.sin(np.pi*np.linspace(0,1,n))*3,0,1)
    return x*e*gain
def pad(freqs,dur,gain=1.0,atk=0.9,rel=1.2):
    """barely-there warmth under the beat; the film is dry, this is the room"""
    n=secs(dur); t=tvec(n); s=np.zeros(n)
    for f in freqs:
        for det in (-3.5,3.5):                              # cents
            ff=f*2**(det/1200)
            s+=np.sin(2*np.pi*ff*t+rng.random()*6.28)*(1+0.25*np.sin(2*np.pi*0.27*t+rng.random()*6))
    e=np.clip(np.minimum(t/atk,(dur-t)/rel),0,1)
    return ma(s,3)*e*gain/len(freqs)
# ---- the jazz bed ----------------------------------------------------------
def rhodes(freqs,dur,gain=1.0):
    """an electric piano: sine plus bell partials that die first, a little bark on the
    attack, and a slow stereo tremolo — returns (left, right)"""
    n=secs(dur); t=tvec(n); s=np.zeros(n)
    for f in freqs:
        ph=2*np.pi*f*t+rng.random()*6.28
        s+=np.sin(ph)+0.32*np.sin(2*ph)*np.exp(-t*3.2)+0.10*np.sin(3*ph)*np.exp(-t*5)+0.05*np.sin(4*ph)*np.exp(-t*7)
    e=np.minimum(1,t/0.010)*np.exp(-t/(dur*0.42))
    s=s*e*gain/len(freqs)
    lfo=np.sin(2*np.pi*4.3*t+rng.random()*6.28)
    return s*(1+0.45*lfo)*0.72, s*(1-0.45*lfo)*0.72
def upright(freq,dur=0.9,gain=1.0):
    """a plucked upright: a warm fundamental, partials fading fast, the finger on the string"""
    n=secs(dur); t=tvec(n); ph=2*np.pi*freq*t
    body=np.sin(ph)+0.5*np.sin(2*ph)*np.exp(-t*4)+0.22*np.sin(3*ph)*np.exp(-t*6)+0.08*np.sin(4*ph)*np.exp(-t*9)
    e=np.minimum(1,t/0.006)*np.exp(-t/(dur*0.36))
    finger=hp(rng.standard_normal(secs(0.022)),3)*env_exp(secs(0.022),0.3)*0.22
    return mix(body*e,finger)*gain
def ride(gain=1.0):
    """a ride cymbal, played light: inharmonic partials with a long shimmer"""
    n=secs(1.0); t=tvec(n); s=np.zeros(n)
    for f,a,d in [(3050,1.0,1.7),(4620,0.7,2.1),(6280,0.5,2.7),(8870,0.3,3.4),(1740,0.35,1.3),(5510,0.4,2.4)]:
        s+=np.sin(2*np.pi*f*t+rng.random()*6.28)*a*np.exp(-t*d)
    s+=hp(rng.standard_normal(n),2)*env_exp(n,0.04)*0.9
    return s*np.minimum(1,t/0.002)*gain/3.3
def brush_swirl(dur=0.75,gain=1.0):
    """brushes circling on a snare head: a soft band of noise that swells and goes"""
    n=secs(dur); x=hp(ma(rng.standard_normal(n),3),14)
    return x*np.sin(np.pi*np.linspace(0,1,n))**1.5*gain

def glide(f0,f1,t_glide,sustain,release,gain=1.0,curve=easeInOut,sat=1.8,vib=0.006):
    """THE BEND. Pitch travels f0→f1 along `curve` over t_glide seconds — the exact
    easing the cursor drags the ease curve to — then holds with a slow vibrato and
    lets go. A sawtooth-ish stack, saturated: the closest a sine can get to a guitar."""
    n=secs(t_glide+sustain+release); t=tvec(n)
    k=np.array([curve(x) for x in np.clip(t/t_glide,0,1)])
    semis=12*np.log2(f1/f0); f=f0*2**(semis*k/12)
    arrived=np.clip((t-t_glide)/0.30,0,1)
    f=f*(1+vib*np.sin(2*np.pi*5.4*t)*arrived)
    ph=2*np.pi*np.cumsum(f)/SR
    s=np.zeros(n)
    for h,a in [(1,1.0),(2,0.55),(3,0.36),(4,0.22),(5,0.13),(6,0.08),(7,0.05)]:
        s+=np.sin(ph*h)*a
    s=np.tanh(s*sat)/np.tanh(sat)
    e=np.minimum(1,t/0.05)
    rs=t_glide+sustain
    e=e*np.where(t>rs,np.exp(-(t-rs)/(release*0.38)),1.0)
    return s*e*gain
def sine_glide(f0,f1,dur,gain=1.0,curve=fE,span=1.0):
    """the quiet echo of the bend: a pure tone riding an ease"""
    n=secs(dur); t=tvec(n)
    k=np.array([curve(x) for x in np.clip(t/(dur*span),0,1)])
    f=f0*2**(12*np.log2(f1/f0)*k/12)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)
    e=np.minimum(1,t/0.08)*np.minimum(1,(dur-t)/0.25)
    return s*np.clip(e,0,1)*gain

# ---- notes -----------------------------------------------------------------
A1=55.0; Bb1=58.27; D2=73.42; E2=82.41; F2=87.31; G2=98.0; A2=110.0; Bb2=116.54; Bn2=123.47   # Bn = B natural (B2, B3 are the beats)
C3=130.81; Cs3=138.59; D3=146.83; E3=164.81; F3=174.61; G3=196.0; A3=220.0; Bb3=233.08; Bn3=246.94
C4=261.63; Cs4=277.18; D4=293.66; E4=329.63
F4=349.23; G4=392.0; A4=440.0; C5=523.25; D5=587.33; F5=698.46

# ============================================================================
# THE BEAT — 75 BPM, six bars, grid from frame 0.  q(bar,beat) → seconds
# ============================================================================
Q=0.8
def q(bar,beat): return (bar-1)*4*Q+(beat-1)*Q      # bar 1 beat 1 = 0.0

K=0.92; S=0.55; HH=0.15; HO=0.19; SUBG=0.50
def drum_kick(t,g=1.0,note=D2,pan=0.0):
    put(kick(K*g),t,pan); put(sub(note,0.7,SUBG*g),t)
def drum_snare(t,g=1.0): put(snare(S*g),t,0.05)
def drum_hat(t,g=1.0,open_=False,pan=0.35): put(hat((HO if open_ else HH)*g,open_),t,pan)

# bar 1 (0.0–3.2) — two beats of silence, then the film starts moving
drum_kick(1.60); drum_snare(1.60,0.8)                  # THE SNAP: kick and snare together
drum_kick(2.596,0.95)                                  # MOTION lands (the "e" of 4)
# bar 2 (3.2–6.4) — the anatomy: the groove fills in
drum_kick(3.20,0.8)
drum_kick(4.20)                                        # the paint wipe lands: pushed kick
# the hats sit on the swung skip (beat + 2/3), the jazz way, so they ride with the bed
SW=Q*2/3
for t in [4.0+SW,5.6+SW,7.2+SW]: drum_hat(t)
drum_snare(4.80); drum_snare(8.00)
drum_kick(6.417,0.9,Bb1)                               # bar 3 downbeat IS the ball's second bounce
# bar 3 (6.4–9.6) → the editor's hand: thin it out so the clicks read
drum_kick(8.20,1.0,A1)                                 # the match cut (over the A7)
drum_kick(8.80,0.55,A1)
# bar 4 (9.6–12.8) — the bend on the downbeat, then the layers fly
drum_kick(9.60,1.0)
for t in [10.4+SW,12.0+SW]: drum_hat(t)
drum_snare(11.20)
put(rim(0.35),11.40,-0.2)                              # "THIS IS THE JOB"
drum_kick(12.20)                                       # the curve fills the frame
# bar 5 (12.8–16.0) — the hero line
drum_kick(12.80,0.9,Bb1); drum_kick(13.60,0.55,Bb1); drum_kick(14.80,0.7,Bb1)
drum_hat(12.8+SW); drum_hat(13.6+SW,1.0,True); drum_hat(14.4+SW)
drum_snare(14.40)
drum_kick(15.80,0.9)                                   # the page lands ("a" of 4)
# bar 6 (16.0–19.2) — the end card; the beat resolves and stops before the loop
drum_kick(16.00,1.0)
for t in [16.0+SW,16.8+SW]: drum_hat(t)
drum_snare(17.60,0.9)                                  # the cursor selects MOVE.
# the ride marks the quarters where the kick and the film leave room
RD=0.040
for t in [4.0,4.8,5.6,7.2,8.0,10.4,12.0,13.6,15.2,16.8,17.6]: put(ride(RD),t,0.45)
# (18.0 and 18.3 belong to the joke — see beat 6 below)

# the room: a warm, quiet bed so the dry hits have somewhere to land
put(pad([D3,A3,F4],  8.0, 0.024), 1.6)                 # D minor, bars 1–3 (the Rhodes carries the harmony now)
put(pad([D3,A3,F4],  3.3, 0.034), 9.5)                 # bar 4 — opens a little under the bend
put(pad([Bb2,F3,D4], 3.3, 0.034), 12.7)                # bar 5 — the lift
put(pad([D3,A3,F4],  2.9, 0.028,0.6,1.0), 15.9)        # bar 6 — home, gone before the loop

# ---- THE JAZZ BED — very low, under everything -------------------------------
# harmony, one descending line home: | Dm9 | Gm9  C9 | Bbmaj9  A7b9 | Dm9 | Gm9  Em7b5 A7b9 | Dm6/9 |
# the V (A7b9, 8.0) resolves to the i (Dm9) on 9.6 — the bend arrives on a chord change.
KEYS=0.052
CH={ 'Dm9'  :[F3,A3,C4,E4],  'Dm11' :[A3,C4,E4,G3*2], 'Gm9':[Bb3,D4,F3*2,A3*2],
     'C9'   :[E3,Bb3,D4,A3*2],'Bbmaj9':[A3,C4,D4,F3*2], 'Em7b5':[G3,Bb3,D4,E4],
     'A7b9' :[G3,Bb3,Cs4,E4], 'Dm69' :[F3,A3,Bn3,E4],   'Dm9hi':[C4,E4,F3*2,A3*2] }
for t,name,dur,g in [
    (1.60,'Dm9',  1.4,1.0),  (3.00,'Gm9',  1.6,0.9),   # pushed into bar 2
    (4.80,'C9',   1.5,0.9),  (6.40,'Bbmaj9',1.5,0.9),
    (8.00,'A7b9', 1.5,1.0),  (9.60,'Dm9',  2.0,1.0),   # the resolution, under the bend
    (11.40,'Dm11',1.2,0.8),  (12.80,'Gm9', 1.5,0.9),
    (14.40,'Em7b5',0.8,0.9), (15.20,'A7b9',0.8,0.9),
    (16.00,'Dm69',1.8,1.0),  (17.60,'Dm9hi',1.1,0.7),
]:
    l,r=rhodes(CH[name],dur,KEYS*g); put_st(l,r,t)

# the upright walks in quarters, rests where the film wants quiet, and takes
# three chromatic pickups on the swung skip
UB=0.15
WALK=[(1.6,D2,1.0),(2.4,F2,0.8),
      (3.2,G2,1.0),(4.0,Bb2,0.9),(4.0+SW,Bn2,0.5),(4.8,C3,1.0),(5.6,E2,0.9),
      (6.4,Bb2,1.0),(7.2,F2,0.9),(8.0,A2,1.0),(8.0+SW,C3,0.5),(8.8,Cs3,0.9),
      (9.6,D2,1.0),(10.4,A2,0.9),(11.2,F2,0.9),(12.0,E2,0.9),
      (12.8,G2,1.0),(13.6,Bb2,0.9),(13.6+SW,F2,0.5),(14.4,E2,1.0),(15.2,A2,1.0),
      (16.0,D2,1.0),(16.8,A2,0.9),(17.6,F2,0.9),(18.298,D2,0.7)]
for t,f,g in WALK: put(upright(f,0.9 if g>0.6 else 0.3,UB*g),t,-0.15)

# brushes on the snare head through the hero line — the ballad half of the film
for t in [12.8,14.4,16.0]: put(brush_swirl(0.9,0.030),t-0.05,0.2)

# ============================================================================
# THE SOUNDS OF MOTION — every cue sits on the frame where the motion happens
# ============================================================================

# ---- beat 1 (0.0–1.6): STILL. -----------------------------------------------
put(room(1.60,0.030),0.00)                             # the uncomfortable quiet
put(tick(0.10),0.53); put(tick(0.10),1.06)             # the caret blinks off, on
put(crackle(PRES[1],0.20),B2[0]-PRES[1],0.0)           # the frame breaks up through the canvas (1.20→1.60)
put(click(0.05,0.10,5,0.42),1.60,0.15)                 # the snap into the title

# ---- beat 2 (1.6–4.2): the study title -----------------------------------
u2=lambda u:B2[0]+u*(B2[1]-B2[0])
put(draw(0.30,0.16),u2(0.00),-0.3)                     # the rule draws in
put(whoosh(0.22,True,0.09),u2(0.04)-0.05,-0.2)         # WHY DO WE NEED rises
put(whoosh(0.34,True,0.14,(70,8)),u2(0.16)+0.20,0.0)   # MOTION falling: air
put(thud(90,48,0.42,0.15,0.36),2.596)                  # MOTION lands
put(click(0.03,0.08,4,0.22),2.596)
put(tick(0.10),2.596+0.162)                            # the little settle-bounce
put(whoosh(0.22,True,0.09),u2(0.30)-0.05,0.2)          # EDITORS? rises
put(brush(PRES[2],0.55),B3[0]-PRES[2],-0.6)            # PAINT WIPE: the brush crosses (3.76→4.20)
put(click(0.04,0.09,5,0.30),4.20,0.4)                  # …and the paint lands

# ---- beat 3 (4.2–8.2): the anatomy, three studies ---------------------------
STUDY=(B3[1]-B3[0])/3                                  # 1.333 s each
def study_t(k,p): return B3[0]+(k+p)*STUDY
for k in range(3):                                     # each label: pull back, then whip in
    s0=study_t(k,0)
    put(whoosh(0.12,False,0.10,(50,6)), s0+0.20*STUDY*ANTIC_DIP-0.03, -0.5)   # the pull-back
    put(whoosh(0.10,True,0.13),          s0+0.20*STUDY*ANTIC_GO,          -0.4)   # the launch
    put(click(0.03,0.08,4,0.30),         s0+0.20*STUDY*ANTIC_HIT,         -0.4)   # it hits its mark
    put(tick(0.10),                      s0+0.14*STUDY,                    -0.4)   # the caption

# 01 SPACING: a mark is dropped at every even slice of time; the marks crowd where the
# head is slow. The ticks are even in time and pitched by the head's speed —
# low where the marks are close, high where they are far apart. The chart, heard.
eS=bez(0.5,0,0.5,1); NG=15
pos=[eS(i/(NG-1)) for i in range(NG)]
for i in range(NG):
    dx=(pos[i]-pos[i-1]) if i>0 else (pos[1]-pos[0])
    f=520*2**(dx/0.14*1.6)                             # 0.007→0.14 spans ~1.6 octaves
    put(type_tick(f,0.20), study_t(0,0)+ (i/(NG-1))*0.78*STUDY, -0.6+1.2*i/(NG-1))

# 02 WEIGHT: it accelerates, squashes, bounces lower, taps, settles
per=0.92*STUDY; w0=study_t(1,0)
put(whoosh(0.34*per,True,0.16,(120,12)), w0, 0.0)      # the fall — air rushing
put(squash(0.85), w0+0.34*per)                         # CONTACT (5.950)
put(thud(120,60,0.22,0.15,0.30), w0+0.72*per)          # second contact (6.417) — the bar-3 kick sits on it
put(click(0.02,0.1,4,0.12), w0+0.72*per)
put(whoosh(0.16,True,0.07,(120,12)), w0+per, 0.0)      # the next fall begins, then the cut

# 03 RHYTHM: seven bars leave the floor one after the other and slam past their mark.
# Each arrival is a pluck a step higher — the stagger is, literally, the music.
r0=study_t(2,0); NOTES=[D4,F4,G4,A4,C5,D5,F5]
for i in range(7):
    arrive=r0+(0.055*i+0.36*ANTIC_HIT)*1.05*STUDY
    put(pluck(NOTES[i],0.5,0.30), arrive, -0.55+1.1*i/6)
    put(click(0.02,0.1,4,0.10), arrive, -0.55+1.1*i/6)

put(whoosh(0.30,False,0.20,(60,8)), B4[0]-PRE, 0.3)    # the band folds into the panel
put(click(0.03,0.07,4,0.26), B4[0])

# ---- beat 4 (8.2–12.2): the editor's hand ---------------------------------
u4=lambda u:B4[0]+u*(B4[1]-B4[0])
put(room(4.0,0.012),B4[0])                             # workspace bed
put(slide(0.40,0.10),u4(0.00),0.3)                     # the cursor comes in
put(click(0.03,0.09,5,0.40),u4(0.09),0.2)              # click — the frame is selected
put(slide(0.56,0.08),u4(0.14),-0.1)                    # …and down to the graph editor
put(tick(0.28),u4(0.16)); put(pluck(D5,0.25,0.10),u4(0.16))              # keyframe one
put(tick(0.26),u4(0.16+0.035)); put(pluck(A4,0.25,0.10),u4(0.16+0.035))  # keyframe two
put(draw(0.26,0.14),u4(0.20),-0.2)                     # the curve is drawn between them
put(tick(0.20),u4(0.22),-0.3)                          # the handle appears
put(tick(0.14),u4(0.28),-0.4)                          # "DRAG THE EASE"

# THE BEND. The drag runs 9.32→9.96 on easeInOut; so does the pitch.
DRAG0=u4(0.28); DRAGD=0.16*(B4[1]-B4[0])
put(glide(F4,A4,DRAGD,0.62,0.55,0.30), DRAG0, 0.0)
put(glide(F4/2,A4/2,DRAGD,0.62,0.55,0.13,sat=1.2,vib=0.004), DRAG0, 0.0)
put(whoosh(0.7,True,0.08,(120,14)), DRAG0-0.05, 0.4)   # air under it

# the post comes apart into its layers (9.72→10.22), then they snap home one by one
put(suck(0.50,0.22), u4(0.38), -0.2)
for i in range(5):
    home=u4(0.38)+(0.36+i*0.055+0.40*BACK_HIT)*0.42*(B4[1]-B4[0])
    put(click(0.03,0.08,4,0.36), home, -0.4+0.8*i/4)
    put(pluck([D4,F4,A4,D5,F5][i],0.35,0.22), home, -0.4+0.8*i/4)
put(tick(0.12),u4(0.38))                               # "IT IS MADE OF LAYERS"
put(tick(0.16),u4(0.80))                               # "THIS IS THE JOB" (with the rim)

put(whoosh(0.34,True,0.17), B5[0]-PRE, 0.3)            # the curve grows out of the editor
put(click(0.04,0.09,5,0.24), B5[0], 0.2)

# ---- beat 5 (12.2–15.8): the hero line --------------------------------------
u5=lambda u:B5[0]+u*(B5[1]-B5[0])
HERO=['SOMEONE','HAS TO DECIDE','HOW THINGS','MOVE.']
LINEF=[1180,1040,920]                                  # each line a little lower
for i,h in enumerate(HERO):
    base=0.05+i*0.055
    for k,ch in enumerate(h):
        if ch==' ': continue
        on=u5(base+k*0.016)
        if i<3:
            put(type_tick(LINEF[i]*(1+0.04*(k%3)),0.18), on, -0.5+1.0*k/max(1,len(h)-1))
        else:                                          # MOVE. overshoots — the hit is the landing
            land=on+0.16*(B5[1]-B5[0])*BACK5_HIT
            put(thud(110,58,0.30,0.16,0.34), land, -0.3+0.6*k/4)
            put(click(0.025,0.08,4,0.18), land)
put(click(0.03,0.09,5,0.26),u5(0.46),0.3)              # handles snap around MOVE.
# the dot rides the curve: the bend's quiet echo, once the type has settled
DOT0=B5[0]+2.2                                          # the dot's second run starts on the bar-5 snare
put(sine_glide(F5,A4*2,B6[0]-DOT0,0.085,fE,span=(0.78*2.2)/(B6[0]-DOT0)), DOT0, 0.0)

put(whoosh(0.28,True,0.17), B6[0]-PRE, 0.0)            # the page turns up
put(click(0.04,0.09,5,0.22), B6[0], 0.1)

# ---- beat 6 (15.8–19.2): the end card ---------------------------------------
u6=lambda u:B6[0]+u*(B6[1]-B6[0])
put(draw(0.45,0.14),u6(0.00),-0.3)                     # the rule
for d,g in [(0.04,0.14),(0.16,0.12),(0.22,0.12),(0.34,0.09)]:   # name, two lines, footer
    put(thud(160,90,0.10,0.2,g),u6(d),-0.2); put(click(0.02,0.1,5,g*0.8),u6(d),-0.2)
put(draw(0.85,0.06),u6(0.30),0.0)                      # the thin rule

# the name tries on eleven typefaces; the holds lengthen, so the shutter slows down
NAMEHOLD=[0.060,0.058,0.062,0.066,0.072,0.080,0.090,0.102,0.116,0.134,0.200]
c=B6[0]+0.10
for i,d in enumerate(NAMEHOLD[:-1]):
    c+=d
    put(shutter(0.30 if i<9 else 0.42, firm=(i==9)), c, -0.25)   # the last one is Inter: firmer

# it collapses to a point and the mark opens out of it
put(suck(0.16,0.26), u6(0.375), -0.1)
put(pop(0.30), u6(0.40+0.075*BACK6_HIT), -0.1)
put(bloom([D4,F4,A4],1.3,0.09), u6(0.40+0.075*BACK6_HIT), 0.0)

# the joke: the cursor comes back, selects MOVE., and it moves
J0=u6(0.46); JD=0.42*(B6[1]-B6[0])
def jt(j): return J0+j*JD
put(slide(0.26,0.10), jt(0.00), 0.4)                   # the cursor slides in
put(click(0.03,0.09,5,0.40), jt(0.14), 0.3)            # click: handles
put(whoosh(0.09,False,0.12,(50,6)), jt(0.26+0.26*ANTIC_DIP)-0.02, 0.2)   # it pulls back…
put(whoosh(0.14,True,0.16), jt(0.26+0.26*ANTIC_GO), 0.3)                  # …and goes
drum_kick(jt(0.26+0.26*ANTIC_HIT),0.85)                                     # lands right (17.975 ≈ the 8th)
put(click(0.03,0.08,4,0.30), jt(0.26+0.26*ANTIC_HIT), 0.5)
put(slide(0.14,0.09), jt(0.56), 0.2)                                        # back it comes
drum_kick(jt(0.56+0.34*BACK6_HIT),0.5)                                      # and settles (18.298)
put(click(0.025,0.08,4,0.22), jt(0.56+0.34*BACK6_HIT), 0.1)
put(slide(0.12,0.05), jt(0.90), -0.3)                                       # the cursor leaves

# the canvas turns back over: the last frame matches the first, so the Reel loops
put(whoosh(0.34,False,0.22,(80,10)), u6(0.855), 0.0)
put(thud(80,44,0.15,0.2,0.40), u6(0.955))
# silence to 19.2 — and beat 1 opens in silence, so the loop point is inaudible

# ============================================================================
# master
# ============================================================================
out=np.stack([L,R])
out-=out.mean(axis=1,keepdims=True)
fade=secs(0.02)
out[:, :fade]*=np.linspace(0,1,fade); out[:,-fade:]*=np.linspace(1,0,fade)
peak=np.abs(out).max()
out=out/peak
out=np.tanh(out*1.25)/np.tanh(1.25)                     # a little glue on the loud hits
out=out/np.abs(out).max()*0.80                          # ≈ −1 dBTP after the inter-sample peaks
pcm=(np.clip(out.T,-1,1)*32767).astype('<i2')

P=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'sound.wav')
with wave.open(P,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", P, round(os.path.getsize(P)/1024), "KB")
