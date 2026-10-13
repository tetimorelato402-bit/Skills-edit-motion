#!/usr/bin/env python3
"""Sound design for The Room — 128 BPM, 16 bars, 30.0 s.

THE SONG IS NOT IN HERE, and must never be. Instagram licenses "Good Girl" only
when it is added inside the app; burning it into the export risks a mute or a
takedown. This file is the room itself — crowd, air, the deck, the impacts — plus
a quiet CLICK on every beat whose only job is alignment: in the Reel editor, slide
the track until its kick sits on the click, then drop original audio to taste.
Both are metronomic, so once aligned they stay aligned for the whole 30 s.
"""
import numpy as np, wave, os, sys

SR=48000; BPM=128.0; BEAT=60/BPM; BAR=4*BEAT; BARS=16; DUR=BARS*BAR
N=int(SR*DUR); rng=np.random.default_rng(11)
L=np.zeros(N); R=np.zeros(N)
def bt(n): return n*BEAT
def bar(n): return (n-1)*BAR
SEC={'booth':(bar(1),bar(4)),'room':(bar(4),bar(8)),'specimen':(bar(8),bar(10)),
     'paint':(bar(10),bar(14)),'wave':(bar(14),bar(17))}

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

def click(g=1.):                       # the alignment guide — small and dry
    n=secs(0.014); return hp(rng.standard_normal(n),3)*ee(n,0.10)*g
def thump(g=1.):                       # the room's own low end, felt not heard
    n=secs(0.30); t=tv(n); f=38+(96-38)*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)*g
def crowd(dur,g=1.):                   # a room full of people, filtered to a murmur
    n=secs(dur); x=ma(rng.standard_normal(n),90)
    wob=1+0.35*np.sin(2*np.pi*0.23*tv(n))+0.2*np.sin(2*np.pi*0.11*tv(n)+1.3)
    return x*wob*g*6
def air(dur,g=1.):                     # the PA's hiss
    n=secs(dur); return hp(rng.standard_normal(n),8)*g
def cue(g=1.):                         # a deck button
    n=secs(0.03); t=tv(n)
    return (hp(rng.standard_normal(n),4)*ee(n,0.09)+np.sin(2*np.pi*1650*t)*ee(n,0.05)*0.4)*g
def riser(dur,g=1.):
    n=secs(dur); u=np.linspace(0,1,n); x=rng.standard_normal(n)
    return (ma(x,70)*(1-u)+hp(x,4)*u)*(u**2.4)*g
def impact(g=1.):
    n=secs(1.4); t=tv(n); f=34+(140-34)*np.exp(-t*20)
    boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.9)
    return np.tanh((boom+hp(rng.standard_normal(n),2)*np.exp(-t*4.5)*0.4)*1.6)/np.tanh(1.6)*g
def splat(g=1.):                       # a stroke of paint thrown at the frame
    n=secs(0.26); x=rng.standard_normal(n); u=np.linspace(0,1,n)
    return (ma(x,5)*np.abs(ma(rng.standard_normal(n),11))*3.0)*np.exp(-u*7)*g
def sweep(dur,g=1.,up=True):
    n=secs(dur); u=np.linspace(0,1,n); u=u if up else u[::-1]; x=rng.standard_normal(n)
    return (ma(x,60)*(1-u)+hp(x,5)*u)*np.sin(np.pi*np.linspace(0,1,n))**1.4*g

# ---- the room, the whole way through -------------------------------------
put(crowd(DUR,0.020),0.0,-0.15); put(crowd(DUR,0.018),0.0,0.15)
put(air(DUR,0.010),0.0)

# ---- the alignment guide: one click per beat, quiet, all the way through ----
for n in range(BARS*4):
    put(click(0.085 if n%4 else 0.125), bt(n), 0.0)
    put(thump(0.085 if n%4 else 0.115), bt(n))        # what a kick feels like in a room

# ---- booth: the deck is being worked -------------------------------------
for n in (2,5,7,10):  put(cue(0.16), bt(n)+BEAT*0.5, -0.35)
for n in (3,8,11):    put(cue(0.13), bt(n)+BEAT*0.25, 0.35)

# ---- the build: the room empties out and a riser takes over ---------------
a,b=SEC['specimen']
put(riser(b-a,0.30), a, 0.0)
put(sweep(BEAT*2,0.16,False), b-BEAT*2, 0.25)

# ---- the drop: the paint erupts, then a stroke on every kick --------------
a,b=SEC['paint']
put(impact(0.62), a, 0.0)
put(splat(0.34), a, 0.0)
n0=int(round(a/BEAT))
for n in range(n0, int(round(b/BEAT))):
    if n%2==0: put(splat(0.15+0.06*((n//2)%3)), bt(n), -0.4+0.8*((n%5)/4))

# ---- the wave: the room resolves and the beat thins out ------------------
a,b=SEC['wave']
put(sweep(BEAT*3,0.20,True), a-BEAT*1.5, 0.0)
put(impact(0.30), a, 0.0)
put(sweep(BEAT*4,0.16,False), b-BEAT*4, 0.0)

# ---- master ---------------------------------------------------------------
out=np.stack([L,R]); out-=out.mean(axis=1,keepdims=True)
f=secs(0.02); out[:,:f]*=np.linspace(0,1,f); out[:,-f:]*=np.linspace(1,0,f)
out=out/np.abs(out).max(); out=np.tanh(out*1.2)/np.tanh(1.2)
out=out/np.abs(out).max()*0.72                       # it sits UNDER the track
pcm=(np.clip(out.T,-1,1)*32767).astype('<i2')
P=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'room.wav')
with wave.open(P,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote",P,round(os.path.getsize(P)/1024),"KB  ",BPM,"BPM  ",BARS,"bars  ",round(DUR,3),"s")
