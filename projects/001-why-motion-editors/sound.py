#!/usr/bin/env python3
"""Sound design for Study 001 — frame-exact, sparse, sits under a blues ballad."""
import numpy as np, wave, os

SR   = 48000
DUR  = 19.2
N    = int(SR*DUR)
rng  = np.random.default_rng(7)
L    = np.zeros(N); R = np.zeros(N)

def ma(x,k):                       # moving average = cheap low-pass
    if k<2: return x
    return np.convolve(x, np.ones(k)/k, mode='same')
def hp(x,k):  return x - ma(x,k)   # high-pass
def env_exp(n,tau): return np.exp(-np.linspace(0,1,n)/tau)
def place(buf,sig,t):
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N: return
    buf[i:j]+=sig[:j-i]
def stereo(sig,t,width=0.0,gain=1.0):
    s=sig*gain
    if width<=0: place(L,s,t); place(R,s,t); return
    place(L,s*(1-width*0.5),t); place(R,s*(1+width*0.5)*0.98,t)

def click(dur=0.035,tau=0.12,k=6,gain=1.0):
    n=int(SR*dur); x=rng.standard_normal(n)*env_exp(n,tau)
    return hp(x,k)*gain
def tick(gain=1.0):                # small UI tick, bright and short
    return click(0.018,0.09,4,gain)
def thud(f0=95,f1=52,dur=0.34,tau=0.16,gain=1.0):
    n=int(SR*dur); t=np.arange(n)/SR
    f=np.linspace(f0,f1,n); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env_exp(n,tau)*gain
def whoosh(dur=0.32,rise=True,gain=1.0,tilt=(90,10)):
    n=int(SR*dur); x=rng.standard_normal(n)
    dark, bright = ma(x,tilt[0]), hp(x,tilt[1])
    u=np.linspace(0,1,n); u = u if rise else u[::-1]
    body = dark*(1-u) + bright*u
    e=np.sin(np.pi*np.linspace(0,1,n))**1.6
    return body*e*gain
def shimmer(dur=1.6,gain=1.0):
    n=int(SR*dur); t=np.arange(n)/SR; s=np.zeros(n)
    for f,a in [(1860,1.0),(2790,0.5),(3720,0.28),(5580,0.12)]:
        s+=np.sin(2*np.pi*f*t+rng.random()*6.28)*a
    atk=np.clip(np.linspace(0,1,n)/0.06,0,1)
    return s*atk*env_exp(n,0.30)*gain
def room(dur,gain=1.0):            # near-silent workspace tone
    n=int(SR*dur); x=ma(rng.standard_normal(n),400)
    e=np.clip(np.sin(np.pi*np.linspace(0,1,n))*3,0,1)
    return x*e*gain

# ---- the cue sheet -------------------------------------------------------
stereo(room(1.60, 0.020), 0.00)                       # b1: the uncomfortable quiet
stereo(tick(0.05), 0.53); stereo(tick(0.05), 1.06)    # the caret blinking

stereo(click(0.05,0.10,5,0.42), 1.60, 0.2)            # THE SNAP into the title
stereo(thud(120,60,0.40,0.13,0.30), 1.60)
stereo(whoosh(0.26,True,0.16), 1.40, 0.5)

stereo(thud(90,48,0.42,0.15,0.34), 2.60)              # MOTION lands
stereo(click(0.03,0.08,4,0.20), 2.60)

stereo(whoosh(0.34,True,0.24), 4.16, 0.6)             # b3: the band opens
for i,t0 in enumerate([4.60,4.78,4.96,5.14,5.32]):    # five specimens
    stereo(tick(0.16-0.012*i), t0, 0.35)

stereo(whoosh(0.30,False,0.20,(60,8)), 7.94, 0.4)     # band folds into the panel
stereo(click(0.03,0.07,4,0.26), 8.20)
stereo(tick(0.22), 8.68)                              # the click on the frame
stereo(tick(0.20), 9.00); stereo(tick(0.20), 9.28)    # two keyframes land
stereo(room(4.00, 0.012), 8.20)                       # workspace bed

stereo(whoosh(0.80,True,0.13,(120,14)), 9.56, 0.7)    # THE DRAG — air only,
stereo(thud(70,44,0.55,0.22,0.13), 9.90)              # the guitar owns this moment

stereo(whoosh(0.34,True,0.15), 11.94, 0.5)            # the curve fills the frame
stereo(thud(100,52,0.50,0.18,0.26), 12.20)
stereo(click(0.04,0.09,5,0.22), 12.20, 0.2)
stereo(tick(0.14), 12.96)                             # MOVE. lands

stereo(whoosh(0.28,True,0.17), 15.54, 0.5)            # the page turns up
stereo(click(0.04,0.09,5,0.20), 15.80, 0.2)
stereo(shimmer(1.70, 0.030), 15.86, 0.6)              # the study closes

# ---- master --------------------------------------------------------------
out=np.stack([L,R])
out-=out.mean(axis=1,keepdims=True)
fade=int(0.03*SR)
out[:, :fade]*=np.linspace(0,1,fade); out[:,-fade:]*=np.linspace(1,0,fade)
peak=np.abs(out).max()
out=out/peak*0.60 if peak>0 else out                  # headroom for the music
pcm=(np.clip(out.T,-1,1)*32767).astype('<i2')

P="/tmp/claude-0/-home-user-Skills-edit-motion/6f53a120-094f-50a3-8e5f-8ef8a3354c74/scratchpad/build/sound.wav"
with wave.open(P,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", P, round(os.path.getsize(P)/1024), "KB   peak", round(float(peak),4))
