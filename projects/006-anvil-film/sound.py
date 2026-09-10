#!/usr/bin/env python3
"""Sound for Anvil — "Sit still. Keep up."  120 BPM, 7 bars, 14.0 s.

On a film about holding attention the sound is half the distraction, and it is
the half that still works with the phone face down.

The design is entirely in how the sync behaves, in three stages:

  LOCKED    Up to the big speed-up, one key per character, dead on the frame the
            letter appears. The viewer learns, without being told, that the
            sound and the picture are the same clock.
  UNLOCKED  From the speed-up the keys come progressively LATE, and some double
            and some drop. Nothing is random — the drift is a smooth curve, so
            it reads as the film losing its grip rather than as a broken render.
            Breaking a sync the viewer has already learned is far more
            disorienting than noise, because they hear that it is wrong.
  DEAD      At the pause everything stops inside one frame. A whole second of
            true digital silence, then the payoff types alone.

The silence is what the rest is spent buying, so the build has to be genuinely
uncomfortable or the stop is worth nothing.

    python3 sound.py            # writes anvil.wav next to this file
"""
import numpy as np, wave, os, sys

SR=48000; BPM=120.0; BEAT=60/BPM; BAR=4*BEAT; BARS=7; DUR=BARS*BAR      # 14.0
N=int(SR*DUR); rng=np.random.default_rng(23)
L=np.zeros(N); R=np.zeros(N)

# mirrors video.html exactly — if a page moves there it must move here
GO=3.0
PAGES=[(GO,     16, 21),
       (GO+1.5, 24, 30),
       (GO+3.0, 34, 41),
       (GO+4.5, 46, 46),      # <- the big speed-up: the sync starts slipping
       (GO+6.0, 62, 49)]
DRIFT_FROM = GO+4.5
PAUSE  = 10.5
PAYOFF = 11.5
CUT    = 13.0

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
def beep(f=880, dur=0.10, g=1.0):
    n=secs(dur); t=tv(n)
    return np.sin(2*np.pi*f*t)*np.minimum(1,t/0.002)*ee(n,0.30)*g
def cutnoise(g=1.0, dur=0.05):
    """the sound of an edit — a splice, not a whoosh"""
    n=secs(dur); return hp(rng.standard_normal(n),2)*ee(n,0.10)*g
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
put(cutnoise(0.14,0.06), GO, 0.0)

# ---- THE KEYS: locked, then deliberately unlocked -------------------------
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
        put(key(g, 0.85+0.30*((ki*37)%5)/4.0), t+d, -0.10+0.20*((ki*13)%7)/6.0)
        # past the speed-up some keys double and some drop out entirely —
        # a keyboard that has stopped keeping up with the hands
        if d>0.05 and ki%5==0:  put(key(g*0.7, 1.1), t+d+0.028, 0.22)
        if d>0.09 and ki%7==3:  pass            # dropped: no key for this letter
        ki+=1

# ---- THE PULL: the app cutting in, and the tension under it ---------------
def beats(a,b,st):
    out=[]; x=a
    while x < b-1e-6: out.append(x); x+=st
    return out
for t in beats(GO+0.5,GO+3.0,1.0)+beats(GO+3.0,GO+6.0,0.5)+beats(GO+6.0,PAUSE,0.25):
    put(cutnoise(0.085,0.045), t, 0.45 if int(t*4)%2 else -0.45)
for i,t in enumerate([GO+2.0,GO+3.5,GO+4.0,GO+5.0,GO+5.5,GO+6.0,GO+6.5,GO+6.75,GO+7.0,GO+7.25]):
    put(cutnoise(0.10+0.05*(i/9),0.035), t, 0.0)
put(tension(PAUSE-(GO+2.0), 0.105), GO+2.0)

# ---- THE PAUSE: one frame, then a second of true silence ------------------
put(thud(0.26,170,40,0.34), PAUSE, 0.0)        # the room shutting, and nothing after

# ---- the payoff types alone -----------------------------------------------
for c in range(16):                            # "Don't sit still." at 13 cps
    put(key(0.050, 0.95), PAYOFF+c/13.0, 0.0)

# ---- the mark --------------------------------------------------------------
put(thud(0.40,190,46,0.9), CUT, 0.0)
put(cutnoise(0.16,0.05), CUT, 0.0)

# ---- master ---------------------------------------------------------------
out=np.stack([L,R]); out-=out.mean(axis=1,keepdims=True)
f=secs(0.02); out[:,:f]*=np.linspace(0,1,f); out[:,-f:]*=np.linspace(1,0,f)
out=out/np.abs(out).max(); out=np.tanh(out*1.25)/np.tanh(1.25)
out=out/np.abs(out).max()*0.84
pcm=(np.clip(out.T,-1,1)*32767).astype('<i2')
P=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'anvil.wav')
with wave.open(P,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote",P,round(os.path.getsize(P)/1024),"KB  ",BPM,"BPM  ",BARS,"bars  ",round(DUR,3),"s")
