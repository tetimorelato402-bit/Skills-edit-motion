#!/usr/bin/env python3
"""Sound for Anvil — "Sit still. Keep up."  120 BPM, 16 bars, 32.0 s.

On a film about holding attention, the sound is not decoration — it is half the
distraction, and it is the half that works even when the phone is face down.

Three layers, and the whole design is in how they end:

  THE TYPE     a key per character, at the same ramping rate the type is set at,
               so what you hear is literally the reading speed increasing.
  THE PULL     everything trying to take the viewer away: notification chimes,
               swipes, a low unease that builds under the last four bars.
  THE STOP     at bar 13 all of it cuts inside one frame. Not a fade — a cut.
               Six beats of near silence with only the keys left, then the mark.

The silence is the point. Everything before it is spent earning it, so if the
build is not genuinely uncomfortable the stop is worth nothing.

    python3 sound.py            # writes anvil.wav next to this file
"""
import numpy as np, wave, os, sys

SR=48000; BPM=120.0; BEAT=60/BPM; BAR=4*BEAT; BARS=16; DUR=BARS*BAR   # 32.0
N=int(SR*DUR); rng=np.random.default_rng(19)
L=np.zeros(N); R=np.zeros(N)
def bt(n): return n*BEAT
def bar(n): return (n-1)*BAR

# THE STOP and the payoff are not the same moment. Everything that pulls dies at
# STOP; the payoff does not start typing for another beat. That gap is the film.
STOP   = bar(12.5)
CLOSE  = bar(14.5)
CTA    = bar(15.25)
CUT    = bar(15.25)+bt(2.5)

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
    body=(np.sin(2*np.pi*(1100*bright)*t)*ee(n,0.05)*0.35
         +np.sin(2*np.pi*(430*bright)*t)*ee(n,0.09)*0.25)
    return (clack*0.9+body)*g
def chime(g=1.0):
    """a notification — the most trained reflex there is"""
    n=secs(0.75); t=tv(n); s=np.zeros(n)
    for f,a,d in [(1568,1.0,5.0),(2093,0.7,6.0),(3136,0.35,8.0)]:
        s+=np.sin(2*np.pi*f*t)*np.exp(-t*d)*a
    return s*np.minimum(1,t/0.004)*g*0.5
def swipe(dur=0.30,g=1.0,up=True):
    n=secs(dur); u=np.linspace(0,1,n); u=u if up else u[::-1]
    x=rng.standard_normal(n)
    return (ma(x,50)*(1-u)+hp(x,5)*u)*np.sin(np.pi*np.linspace(0,1,n))**1.5*g
def unease(dur,g=1.0,f0=52):
    """a low tone that will not resolve — it is what the stop switches off"""
    n=secs(dur); t=tv(n)
    s=np.sin(2*np.pi*f0*t)+0.5*np.sin(2*np.pi*f0*1.5*t+0.7)+0.25*np.sin(2*np.pi*f0*2.51*t)
    ramp=np.linspace(0.25,1.0,n)**1.6
    e=np.minimum(1,t/0.6)
    return ma(s,3)*ramp*e*g
def tick(g=1.0):
    n=secs(0.020); return hp(rng.standard_normal(n),2)*ee(n,0.08)*g
def thud(g=1.0,f0=120,f1=44,dur=0.5):
    n=secs(dur); f=np.linspace(f0,f1,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*ee(n,0.20)*g
def room(dur,g=1.0):
    n=secs(dur); return ma(rng.standard_normal(n),300)*g*5

# ---- the room -------------------------------------------------------------
put(room(DUR,0.020),0.0)

# ---- THE TYPE: a key per character, at the film's own ramping rate ---------
# mirrors PAGES in video.html: (bar, cps, characters). What you hear is the
# reading speed going up, which is the test happening in another sense.
PAGES=[(2.0,15, 29+31+17+21),
       (5.0,17, 21+25+13),
       (7.5,19, 30+22+18+29),          # the slot teti is writing
       (10.5,22, 21+26)]
PAYOFF=(13.0,20, 16+31)
CLOSEP=(14.5,22, 12+20)
CTAP  =(15.25,26, 15)
for b,cps,chars in PAGES+[PAYOFF,CLOSEP,CTAP]:
    t0=bar(b)
    for i in range(chars):
        t=t0+i/cps
        if t>=DUR: break
        # spaces and line ends fall a touch softer; a real keyboard is not even
        g=0.055 if i%7 else 0.038
        put(key(g, 0.85+0.3*((i*37)%5)/4.0), t, -0.10+0.20*((i*13)%7)/6.0)

# ---- THE PULL: everything trying to take the viewer away ------------------
# the drifting dots, from bar 2 — barely there, but there
for i in range(7):
    put(tick(0.030), bar(2)+i*0.55, -0.5+i*0.16)
# slabs crossing the frame, bars 4+
for i in range(5):
    at=bar(4)+i*bt(3)
    if at<STOP: put(swipe(0.40,0.17,i%2==0), at, -0.55 if i%2 else 0.55)
# the notification — the loudest single pull in the film, and the most familiar
put(chime(0.34), bar(6)+bt(1), 0.30)
put(swipe(0.22,0.12,True), bar(6)+bt(1)-0.06, 0.30)
# the decoy stream types too, quieter and drier, off to one side
for i in range(62):
    t=bar(8)+i/15.0
    if t<STOP: put(key(0.020,1.35), t, 0.62)
for i in range(37):
    t=bar(10)+bt(2)+i/13.0
    if t<STOP: put(key(0.018,1.25), t, -0.62)
# a second chime, closer in, while the decoy is already running
put(chime(0.26), bar(9)+bt(2), -0.35)
# the colour washes land as dry ticks — they are seen more than heard
for f in [bar(5), bar(6)+bt(2), bar(8)+bt(1), bar(9)+bt(3), bar(11), bar(11)+bt(2), bar(12)+bt(1)]:
    if f<STOP: put(tick(0.10), f, 0.0)
# and under all of it, from bar 9, something that will not resolve
put(unease(STOP-bar(9), 0.115), bar(9))
for i in range(14):                                   # bars 11-12 crowd in
    t=bar(11)+i*bt(0.5)
    if t<STOP: put(tick(0.055+0.05*(i/13)), t, -0.7+1.4*((i*5)%7)/6.0)
put(chime(0.20), bar(11)+bt(3), 0.5)
put(swipe(bt(4),0.20,True), STOP-bt(4), 0.0)          # the last inhale

# ---- THE STOP -------------------------------------------------------------
# One frame. Everything above is written to end before STOP, so the cut happens
# by construction rather than by a fade someone has to remember to draw.
put(thud(0.24,150,40,0.9), STOP, 0.0)                 # the room closing
put(room(CUT-STOP, 0.012), STOP)                      # and then only the keys

# ---- the mark -------------------------------------------------------------
put(thud(0.42,180,46,1.1), CUT, 0.0)
put(swipe(0.5,0.16,False), CUT-0.16, 0.0)

# ---- master ---------------------------------------------------------------
out=np.stack([L,R]); out-=out.mean(axis=1,keepdims=True)
f=secs(0.02); out[:,:f]*=np.linspace(0,1,f); out[:,-f:]*=np.linspace(1,0,f)
out=out/np.abs(out).max(); out=np.tanh(out*1.25)/np.tanh(1.25)
out=out/np.abs(out).max()*0.70
pcm=(np.clip(out.T,-1,1)*32767).astype('<i2')
P=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'anvil.wav')
with wave.open(P,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote",P,round(os.path.getsize(P)/1024),"KB  ",BPM,"BPM  ",BARS,"bars  ",round(DUR,3),"s")
