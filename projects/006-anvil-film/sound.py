#!/usr/bin/env python3
"""Sound for Anvil — "Sit still. Keep up."  120 BPM, 7 bars, 14.0 s.

On a film about holding attention the sound is half the distraction, and it is
the half that still works with the phone face down.

The design is entirely in how the sync behaves, in four stages:

  LOCKED    Up to the big speed-up, one key per character, dead on the frame the
            letter appears. The viewer learns, without being told, that the
            sound and the picture are the same clock.
  UNLOCKED  From the speed-up the keys come progressively LATE, and some double
            and some drop. Nothing is random — the drift is a smooth curve, so
            it reads as the film losing its grip rather than as a broken render.
            Breaking a sync the viewer has already learned is far more
            disorienting than noise, because they hear that it is wrong.
  REDACTED  At 9.75 the words on screen stop being words. The keys go with them:
            dull, wide, no click left in them, over a failing sweep. The sound
            of a machine that is still typing and no longer writing.
  DEAD      At the pause everything stops inside one frame. A whole second of
            true digital silence, then the payoff types alone.

The silence is what the rest is spent buying, so the build has to be genuinely
uncomfortable or the stop is worth nothing.

Every cue below is a MOTION in the film, not a musical event: a card landing, a
shutter, a letterbox slam, the negative, a wipe crossing frame. The lists are
mirrored from video.html and `python3 scripts/check-sync.py` fails if they have
drifted apart.

    python3 sound.py            # writes anvil.wav next to this file
"""
import numpy as np, wave, os, sys

SR=48000; BPM=120.0; BEAT=60/BPM; BAR=4*BEAT; BARS=7; DUR=BARS*BAR      # 14.0
N=int(SR*DUR); rng=np.random.default_rng(23)
L=np.zeros(N); R=np.zeros(N)

# ---- mirrors video.html exactly. If a time moves there it must move here. ----
GO=3.0
PAGES=[(GO,     16, 21),
       (GO+1.5, 24, 30),
       (GO+3.0, 34, 41),
       (GO+4.5, 46, 46),      # <- the big speed-up: the sync starts slipping
       (GO+6.0, 62, 49)]
DRIFT_FROM = GO+4.5
REDACT = GO+6.75              # 9.75 — the words stop being words
PAUSE  = 10.5
PAYOFF = 11.5
CUT    = 13.0

def beats(a,b,st):
    out=[]; x=a
    while x < b-1e-6: out.append(round(x,6)); x+=st
    return out

CARDS  = beats(GO+0.5,GO+3.0,1.0)+beats(GO+3.0,GO+6.0,0.5)+beats(GO+6.0,PAUSE,0.25)
PHOTOS = [GO+1.0,GO+2.5,GO+3.5,GO+4.25,GO+5.0,GO+5.75,GO+6.25,GO+6.75,GO+7.25]
FLASH  = [GO+2.0,GO+3.5,GO+4.0,GO+5.0,GO+5.25,GO+6.0,GO+6.5,GO+6.75,GO+7.0,GO+7.25]
INVERT = [GO+3.75,GO+5.5,GO+7.125]
LETTERBOX = [GO+5.0,GO+6.0,GO+7.25]
WIPE   = [GO+3.25,GO+5.375,GO+6.875]
BLEED  = [GO+6.0]
# LETTERBOX, not BARS: BARS is the film's length in bars and a list bound to that
# name silently replaced it. DUR was already computed so nothing rendered wrong,
# which is the dangerous kind of shadow — the same failure the jazz pass hit when
# a note constant took the name of a beat tuple.

def ma(x,k): return x if k<2 else np.convolve(x,np.ones(k)/k,mode='same')
def hp(x,k): return x-ma(x,k)
def secs(d): return int(SR*d)
def tv(n): return np.arange(n)/SR
def ee(n,tau): return np.exp(-np.linspace(0,1,n)/tau)
def place(b,s,t):
    i=int(round(t*SR)); j=min(N,i+len(s))
    if i>=N or j<=i: return
    b[i:j]+=s[:j-i]
def put(s,t,pan=0.,g=1.):
    a=(pan+1)*np.pi/4; place(L,s*g*np.cos(a),t); place(R,s*g*np.sin(a),t)

# ---- voices ---------------------------------------------------------------
def key(g=1.0, bright=1.0):
    """one keystroke: a hard click, a little body, gone in 40 ms"""
    n=secs(0.040); t=tv(n)
    clack=hp(rng.standard_normal(n),3)*ee(n,0.07)
    body=(np.sin(2*np.pi*(1150*bright)*t)*ee(n,0.05)*0.35
         +np.sin(2*np.pi*(440*bright)*t)*ee(n,0.09)*0.25)
    return (clack*0.9+body)*g
def deadkey(g=1.0):
    """the same stroke once the letters are blocks: wide, dull, no click left"""
    n=secs(0.075); t=tv(n)
    thump=ma(rng.standard_normal(n),9)*ee(n,0.16)*1.6
    body=np.sin(2*np.pi*130*t)*ee(n,0.12)*0.5
    return (thump+body)*g
def beep(f=880, dur=0.10, g=1.0):
    n=secs(dur); t=tv(n)
    return np.sin(2*np.pi*f*t)*np.minimum(1,t/0.002)*ee(n,0.30)*g
def cutnoise(g=1.0, dur=0.05):
    """the sound of an edit — a splice, not a whoosh"""
    n=secs(dur); return hp(rng.standard_normal(n),2)*ee(n,0.10)*g
def shutter(g=1.0):
    """a photo landing. Two clicks 55 ms apart so they FLAM rather than fuse —
       under ~35 ms the ear hears one event and the camera disappears."""
    n=secs(0.115); out=np.zeros(n)
    a=hp(rng.standard_normal(secs(0.018)),2)*ee(secs(0.018),0.09)
    b=hp(rng.standard_normal(secs(0.030)),4)*ee(secs(0.030),0.13)*0.8
    out[:len(a)]+=a; i=secs(0.055); out[i:i+len(b)]+=b
    return out*g
def slam(g=1.0):
    """the letterbox arriving: a wooden knock with a short noise skin"""
    n=secs(0.30); t=tv(n)
    f=np.linspace(220,68,n)
    knock=np.sin(2*np.pi*np.cumsum(f)/SR)*ee(n,0.13)
    skin=hp(rng.standard_normal(n),3)*ee(n,0.03)*0.55
    return (knock+skin)*g
def burst(g=1.0):
    """the negative: 34 ms of full band, hard in and hard out"""
    n=secs(0.034); return rng.standard_normal(n)*np.hanning(n)**0.35*g
def sweep(g=1.0, dur=0.145):
    """a wipe crossing frame — noise opening from dark to bright as it travels"""
    n=secs(dur); x=rng.standard_normal(n)
    out=np.zeros(n); k=np.linspace(40,2,n).astype(int)
    for i in range(0,n,64):
        kk=max(2,k[i]); seg=x[i:i+64]
        out[i:i+64]=hp(np.convolve(seg,np.ones(kk)/kk,mode='same'),2)
    return out*np.hanning(n)**0.4*g
def fail(g=1.0):
    """the redact: pitch falling out from under a quantised, breaking signal"""
    n=secs(0.55); t=tv(n)
    f=np.linspace(900,70,n)
    tone=np.sin(2*np.pi*np.cumsum(f)/SR)
    tone=np.round(tone*5)/5.0                      # crushed: it is breaking, not sliding
    grit=hp(rng.standard_normal(n),2)*np.linspace(0.05,0.5,n)
    return (tone*0.7+grit)*ee(n,0.42)*g
def sub(g=1.0, dur=0.6):
    n=secs(dur); f=np.linspace(90,32,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*ee(n,0.30)*g
def tension(dur, g=1.0, f0=48):
    n=secs(dur); t=tv(n)
    s=np.sin(2*np.pi*f0*t)+0.5*np.sin(2*np.pi*f0*1.5*t+0.7)+0.3*np.sin(2*np.pi*f0*2.49*t)
    return ma(s,3)*(np.linspace(0.2,1.0,n)**1.8)*np.minimum(1,t/0.4)*g
def thud(g=1.0,f0=170,f1=44,dur=0.7):
    n=secs(dur); f=np.linspace(f0,f1,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*ee(n,0.20)*g
def room(dur,g=1.0):
    n=secs(dur); return ma(rng.standard_normal(n),300)*g*5

# ---- the room, and it dies at the pause -----------------------------------
put(room(PAUSE,0.016),0.0)

# ---- GET READY: the countdown ---------------------------------------------
put(beep(660,0.09,0.20), 1.0, 0.0)
put(beep(660,0.09,0.20), 1.5, 0.0)
put(beep(660,0.09,0.20), 2.0, 0.0)
put(beep(1320,0.22,0.26), 2.5, 0.0)          # the go tone, an octave up
put(slam(0.20),           2.5, 0.0)          # and the cut to the reversed frame
put(cutnoise(0.14,0.06),  GO,  0.0)          # the cut into the test

# ---- THE KEYS: locked, then deliberately unlocked, then dead --------------
# drift(t) is a smooth curve rather than jitter. A viewer who has heard the
# sync be exact for four seconds hears a 150 ms lag as the film slipping, which
# is the intended feeling; random noise would just read as a bad render.
def drift(t):
    if t < DRIFT_FROM: return 0.0
    u = (t-DRIFT_FROM)/(PAUSE-DRIFT_FROM)
    return 0.165*(u**1.7)                      # up to ~165 ms late by the pause

ki=0
for t0,cps,chars in PAGES:
    for c in range(chars):
        t=t0+c/cps
        if t>=PAUSE: break
        d=drift(t)
        g=0.058 if c%7 else 0.040
        if t>=REDACT:
            # the picture has stopped making letters, so the keyboard stops
            # making letter sounds. Same rhythm, nothing left in it.
            put(deadkey(g*0.85), t+d, -0.14+0.28*((ki*13)%7)/6.0)
        else:
            put(key(g, 0.85+0.30*((ki*37)%5)/4.0), t+d, -0.10+0.20*((ki*13)%7)/6.0)
            # past the speed-up some keys double and some drop out entirely —
            # a keyboard that has stopped keeping up with the hands
            if d>0.05 and ki%5==0:  put(key(g*0.7, 1.1), t+d+0.028, 0.22)
            if d>0.09 and ki%7==3:  pass            # dropped: no key for this letter
        ki+=1

# ---- THE EDITS. Every one of these is a motion in the picture. -------------
for i,t in enumerate(CARDS):                   # the app landing
    put(cutnoise(0.085,0.045), t, 0.45 if i%2 else -0.45)
for i,t in enumerate(PHOTOS):                  # a person arriving
    put(shutter(0.115), t, -0.30 if i%2 else 0.34)
for i,t in enumerate(FLASH):                   # flash frames, escalating
    put(cutnoise(0.10+0.05*(i/9),0.035), t, 0.0)
for t in INVERT:                               # the negative
    put(burst(0.155), t, 0.0)
for i,t in enumerate(LETTERBOX):               # the letterbox
    put(slam(0.19+0.03*i), t, 0.0)
for i,t in enumerate(WIPE):                    # a wipe crossing frame, and it
    put(sweep(0.095), t, -0.55)                # travels: L to R, like the band
    put(sweep(0.075), t+0.055, 0.55)
for t in BLEED:                                # the full frame going to a photo
    put(sub(0.30), t, 0.0)

put(tension(PAUSE-(GO+2.0), 0.105), GO+2.0)
put(fail(0.20), REDACT, 0.0)                   # the signal, breaking

# ---- THE PAUSE: one frame, then a second of true silence ------------------
put(thud(0.26,170,40,0.34), PAUSE, 0.0)        # the room shutting, and nothing after

# ---- the payoff types alone -----------------------------------------------
for c in range(16):                            # "Don't sit still." at 13 cps
    put(key(0.050, 0.95), PAYOFF+c/13.0, 0.0)

# ---- the mark --------------------------------------------------------------
put(thud(0.40,190,46,0.9), CUT, 0.0)
put(cutnoise(0.16,0.05), CUT, 0.0)

# ---- master ---------------------------------------------------------------
# A LOOK-AHEAD LIMITER, not a tanh. This film is made almost entirely of
# transients — keystrokes, splices, a shutter — and driving them into a tanh
# hard enough to raise the integrated loudness rounds the front off every one of
# them, which is the only thing they have. The limiter rides a gain curve
# instead: it ducks 4 ms before a peak and lets go over 120 ms, so the clicks
# keep their edge and only the overshoot is taken.
#
# Why bother: Reels normalise to about -14 LUFS and this film reads QUIET,
# because a second of true silence and a 13 LU range drag the integrated figure
# down. Delivered at -19 the platform adds ~5 dB and squashes the transients
# through ITS limiter, which is not a limiter anyone here chose. Delivered near
# -14 under our own ceiling, nothing downstream has to touch it.
DRIVE=9.0                                    # tuned against ebur128, see below
CEIL =0.68                                   # sample ceiling, chosen for TRUE peak
# CEIL is a SAMPLE ceiling and the number that matters is the INTERSAMPLE one,
# after the AAC encode. Tuned by measuring the delivered mp4, not the wav:
# 0.68 lands at -14.3 LUFS integrated, -1.7 dBFS true peak, which is the target
# (Reels normalise to about -14 and true peak must stay under -1 dB or the AAC
# clips the transients). 0.74 measures 1 dB louder in the wav and +1.2 dBFS true
# peak in the mp4 — over the line. DRIVE past ~9 buys nothing; the limiter takes
# back everything it is given. Both numbers are only sane BECAUSE of lowpass()
# below: before the roof went on, chasing CEIL down made the delivered true peak
# WORSE, because the figure being measured was the codec's noise, not the mix.

def limit(x, ceil=CEIL, look=0.004, rel=0.12):
    """block-rate look-ahead limiter. A sample-rate sliding max over a 4 ms
    window is 780 MB of strides for no audible gain; 64-sample block maxima
    with a three-block window is the same curve at 1/64th the cost."""
    m=np.abs(x).max(axis=0)
    B=64; nb=(len(m)+B-1)//B
    pad=np.zeros(nb*B); pad[:len(m)]=m
    bm=pad.reshape(nb,B).max(axis=1)
    look_b=max(1,int(SR*look/B))
    bmx=bm.copy()
    for k in range(1,look_b+1):              # the peak that is COMING, not the one here
        bmx=np.maximum(bmx, np.roll(bm,-k))
    bmx=np.maximum(bmx, np.roll(bm,1))
    g=np.minimum(1.0, ceil/np.maximum(bmx,1e-9))
    a=np.exp(-B/(SR*rel)); cur=1.0
    for i in range(nb):                      # instant duck, slow release
        cur = g[i] if g[i]<cur else a*cur+(1-a)*g[i]
        g[i]=cur
    gs=np.interp(np.arange(len(m)), np.arange(nb)*B+B/2, g,
                 left=g[0], right=g[-1])
    return x*gs

def dcblock(x, win=0.06):
    """DC removal that is ZERO IN, ZERO OUT. Subtracting a global mean writes a
    constant into every sample of the film INCLUDING the pause — measured as
    -53 dBFS of pure DC (absmax == mean, so it was a flat line) sitting in the
    one place the film has to be a hole. A centred box average is a ~16 Hz
    high-pass and leaves exact zeros exactly zero. Cumsum, not convolve: a
    2880-tap box over 672k samples is 2 G multiply-adds for a running total."""
    K=int(SR*win); h=K//2
    pad=np.pad(x, ((0,0),(h,K-h)), mode='edge')
    c=np.concatenate([np.zeros((x.shape[0],1)), np.cumsum(pad,axis=1)], axis=1)
    return x - ((c[:,K:]-c[:,:-K])/K)[:, :x.shape[1]]

def lowpass(x, fc=15000.0, taps=63):
    """A gentle roof. Every voice here is a click, and a click made from
    numpy noise carries energy all the way to Nyquist — energy no phone
    reproduces, which nonetheless costs real headroom (it reconstructs as
    intersample peaks) and real bits (AAC spends them, then overshoots).
    Measured: the encode was reporting +1.1 dBFS true peak on the right channel
    while the left sat at -2.0, and lowering the limiter ceiling made it worse,
    not better, because the figure was the codec's noise and not the mix's."""
    n=(np.arange(taps)-(taps-1)/2)
    h=np.sinc(2*fc/SR*n)*np.hamming(taps); h/=h.sum()
    return np.stack([np.convolve(ch,h,mode='same') for ch in x])

out=np.stack([L,R]); out=dcblock(out); out=lowpass(out)
f=secs(0.02); out[:,:f]*=np.linspace(0,1,f); out[:,-f:]*=np.linspace(1,0,f)
out=out/np.abs(out).max()*DRIVE
out=limit(out)
pcm=(np.clip(out.T,-1,1)*32767).astype('<i2')
P=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'anvil.wav')
with wave.open(P,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote",P,round(os.path.getsize(P)/1024),"KB  ",BPM,"BPM  ",BARS,"bars  ",round(DUR,3),"s")
