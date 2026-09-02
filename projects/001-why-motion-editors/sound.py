#!/usr/bin/env python3
"""Sound for Study 001 — a house beat, and the film cut to it.

There is no licensed music. This file IS the soundtrack: nothing gets added in
Instagram. It is synthesised from sines and noise; there are no samples — unless
`--texture` is passed, which layers six recorded objects under six of the cues
(see texture.py). The default build is still sample-free.

THE BEAT. Written in the temperament of Kungs' "I Feel So Bad" (feat. Ephemerals)
— 123 BPM, A minor, four-on-the-floor with the offbeat open hat and a plucked
riff carrying the hook. This runs at **125 BPM**, the same room, chosen because
it divides the film exactly: a beat is 0.48 s, a bar 1.92 s, and the film is
eleven bars, so the loop point lands on a downbeat.

MATCHED MOTION. `video.html` was re-cut onto this grid — this is the point, and
it is why the film was re-rendered rather than just re-scored. Every motion in
focus lands on the beat:

    bar  1   STILL.        the caret blinks on the beat
    bar  2   the title     MOTION falls on 2 and LANDS ON 3
    bars 3-5 the anatomy   one study per bar: the spacing chart drops a mark on
                           every SIXTEENTH, the ball contacts on 2 and taps on 4,
                           the seven bars stagger up the EIGHTHS
    bar  6   the setup     click, keyframe, keyframe, grab — one per beat
    bar  7   THE DROP      the ease is dragged onto the downbeat and the post
                           comes apart; its five layers snap home on the eighths
    bars 8-9 the hero      one line per beat; MOVE. is home on the downbeat
    bars10-11 the end card the type cycle plays sixteenths and lands on Inter on
                           the last downbeat; MOVE. slides out on 3, home on 4

So the drums do not sit under the film — they are the same events. Cue times
below are derived from the film's own constants and easing curves (the bezier
solver is ported verbatim from video.html), so a re-timed beat re-scores itself.

TWO STYLES, ONE GRID. The film's cut never changes; only the kit and the groove do.

    python3 sound.py                      # house   -> sound.wav
    python3 sound.py --afro               # afro    -> sound_afro.wav
    python3 sound.py out.wav [--afro]

  house  Kungs, "I Feel So Bad" — four on the floor, clap on 2 and 4, offbeat
         open hats, an A-minor i-VI bass vamp and a two-bar pluck riff.
  afro   HUGEL & SOLTO, "Jamaican (Bam Bam)" — Afro House, 122 BPM in the
         original. It is built here at the film's own 125 (the genre lives at
         120-126, so nothing has to move) with the parts that actually make the
         style: a rolling conga tumbao between the kicks, a shaker on every
         sixteenth, a 3-2 clave, a bouncing syncopated bass, a marimba hook in
         A Dorian, and a two-tom "bam bam" answering every second bar.

Both styles play the same motion cues at the same frames, because those come
from the film, not from the genre.
"""
import numpy as np, wave, os, sys

ARGV    = [a for a in sys.argv[1:] if not a.startswith('--')]
STYLE   = 'afro' if '--afro' in sys.argv else 'house'
TEXTURE = '--texture' in sys.argv or os.environ.get('TEXTURE') == '1'

SR   = 48000
BPM  = 125.0
BEAT = 60.0/BPM                     # 0.48
BAR  = 4*BEAT                       # 1.92
BARS = 11
DUR  = BARS*BAR                     # 21.12
N    = int(SR*DUR)
rng  = np.random.default_rng(7)
L    = np.zeros(N); R = np.zeros(N)

def bt(n):  return n*BEAT           # beat n counted from frame 0
def bar(n): return (n-1)*BAR        # the downbeat of bar n (1-indexed)

# ---- the film's own timeline (mirror of video.html) ------------------------
B1=(bt(0),bt(4)); B2=(bt(4),bt(8)); B3=(bt(8),bt(20))
B4=(bt(20),bt(28)); B5=(bt(28),bt(36)); B6=(bt(36),bt(44))
PRE=BEAT/2; PRES=[0,BEAT,BEAT,PRE,PRE,PRE]
STUDY=(B3[1]-B3[0])/3               # one bar per study

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
easeInOut=bez(0.65,0,0.35,1)
antic    =bez(0.6,-0.42,0.32,1.5)
backOut  =bez(0.28,1.42,0.44,1)
backOut6 =bez(0.24,1.52,0.4,1)
EAS      =(0.14,0.96,0.32,1.0)      # the ease the cursor drags the curve to

def first_at(f,thr,lo=0.0):
    for x in np.linspace(lo,1,4001):
        if f(x)>=thr: return float(x)
    return 1.0
def min_at(f):
    xs=np.linspace(0,1,4001); v=[f(x) for x in xs]; return float(xs[int(np.argmin(v))])
ANTIC_DIP=min_at(antic)
ANTIC_GO =first_at(antic,0.0,ANTIC_DIP)
ANTIC_HIT=first_at(antic,1.0,ANTIC_DIP)      # the label/bar reaches its mark
BACK_HIT =first_at(backOut,1.0)
BACK6_HIT=first_at(backOut6,1.0)

# ---- dsp helpers -----------------------------------------------------------
def ma(x,k):
    if k<2: return x
    return np.convolve(x, np.ones(k)/k, mode='same')
def hp(x,k):  return x - ma(x,k)
def env_exp(n,tau): return np.exp(-np.linspace(0,1,n)/tau)
def secs(d): return int(SR*d)
def tvec(n): return np.arange(n)/SR
def mix(*sigs):
    n=max(len(s) for s in sigs); out=np.zeros(n)
    for s in sigs: out[:len(s)]+=s
    return out
def place(buf,sig,t):
    i=int(round(t*SR)); j=min(N,i+len(sig))
    if i>=N or j<=i: return
    buf[i:j]+=sig[:j-i]
def put(sig,t,pan=0.0,gain=1.0):
    a=(pan+1)*np.pi/4
    place(L,sig*gain*np.cos(a),t); place(R,sig*gain*np.sin(a),t)
def put_st(l,r,t,gain=1.0): place(L,l*gain,t); place(R,r*gain,t)

# ---- the kit ---------------------------------------------------------------
def kick(gain=1.0,dur=0.42):
    """a house kick: a click, a fast pitch drop, a round tail, driven a little"""
    n=secs(dur); t=tvec(n)
    f=44+(210-44)*np.exp(-t*46)
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7.5)
    s=mix(body, hp(rng.standard_normal(secs(0.006)),3)*env_exp(secs(0.006),0.25)*0.5)
    return np.tanh(s*2.1)/np.tanh(2.1)*gain
def clap(gain=1.0):
    """three noise taps 11 ms apart into a short room — the house clap"""
    n=secs(0.30); s=np.zeros(n)
    for i,a in enumerate([0.9,1.0,0.75]):
        k=secs(i*0.011); b=hp(rng.standard_normal(secs(0.02)),3)*env_exp(secs(0.02),0.16)*a
        s[k:k+len(b)]+=b
    tail=hp(rng.standard_normal(n),4)*env_exp(n,0.13)*0.5
    return ma(s+tail,2)*gain
def hat(gain=1.0,open_=False):
    d=0.16 if open_ else 0.030
    n=secs(d); x=hp(rng.standard_normal(n),2)
    e=env_exp(n,0.42 if open_ else 0.22)
    if open_: e*=np.minimum(1,tvec(n)/0.004)
    return x*e*gain
def bass(freq,dur,gain=1.0):
    """sub plus a touch of saw so it survives a phone speaker"""
    n=secs(dur); t=tvec(n); ph=2*np.pi*freq*t
    s=np.sin(ph)+0.30*np.sin(2*ph)+0.12*np.sin(3*ph)
    e=np.minimum(1,t/0.006)*np.exp(-t/(dur*0.5))
    return np.tanh(s*e*1.4)/np.tanh(1.4)*gain
def pluck(freq,dur=0.34,gain=1.0,bright=0.5):
    """the riff voice: short, filtered, plucky — the catchy thing"""
    n=secs(dur); t=tvec(n); s=np.zeros(n)
    for h in range(1,7):
        s+=np.sin(2*np.pi*freq*h*t+rng.random()*6.28)*(bright**(h-1))*np.exp(-t*(4.0+h*3.6))
    return s*np.minimum(1,t/0.003)*gain
def stab(freqs,dur=0.26,gain=1.0):
    """a chord stab, panned wide, filtered down as it decays"""
    n=secs(dur); t=tvec(n); s=np.zeros(n)
    for f in freqs:
        ph=2*np.pi*f*t+rng.random()*6.28
        s+=np.sin(ph)+0.30*np.sin(2*ph)*np.exp(-t*9)+0.12*np.sin(3*ph)*np.exp(-t*14)
    e=np.minimum(1,t/0.004)*np.exp(-t*7.5)
    s=s*e*gain/len(freqs)
    lfo=np.sin(2*np.pi*3.1*t+rng.random()*6.28)
    return s*(1+0.35*lfo)*0.75, s*(1-0.35*lfo)*0.75
def riser(dur,gain=1.0):
    """filtered noise climbing into a landing"""
    n=secs(dur); u=np.linspace(0,1,n); x=rng.standard_normal(n)
    body=ma(x,60)*(1-u)+hp(x,4)*u
    return body*(u**2.2)*gain
def downlift(dur=0.9,gain=1.0):
    """the exhale after a drop — noise falling away"""
    n=secs(dur); u=np.linspace(0,1,n); x=rng.standard_normal(n)
    return (hp(x,4)*(1-u)+ma(x,50)*u)*np.exp(-u*3.2)*gain
def impact(gain=1.0):
    """the landing itself: a sub boom under a short crash"""
    n=secs(1.1); t=tvec(n)
    f=38+(150-38)*np.exp(-t*22)
    boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.4)
    crash=hp(rng.standard_normal(n),2)*np.exp(-t*4.2)*0.45
    return np.tanh((boom+crash)*1.5)/np.tanh(1.5)*gain

# ---- the afro kit ----------------------------------------------------------
def conga(freq=310,open_=True,gain=1.0):
    """a hand drum: a pitched body that snaps down, plus the slap of the palm"""
    dur=0.30 if open_ else 0.13
    n=secs(dur); t=tvec(n)
    f=freq*(1+0.9*np.exp(-t*90))
    ph=2*np.pi*np.cumsum(f)/SR
    body=np.sin(ph)*np.exp(-t*(9 if open_ else 26))+0.32*np.sin(ph*2.6)*np.exp(-t*24)
    slap=hp(rng.standard_normal(secs(0.012)),3)*env_exp(secs(0.012),0.2)*0.55
    return mix(body,slap)*gain
def shaker(gain=1.0,accent=False):
    """the sixteenth-note engine of the groove — soft attack, no click"""
    n=secs(0.075 if accent else 0.05); x=hp(rng.standard_normal(n),2)
    return x*np.minimum(1,tvec(n)/0.006)*env_exp(n,0.19 if accent else 0.12)*gain
def clave(gain=1.0):
    """two hardwood sticks — the 3-2 pattern that holds the bar together"""
    n=secs(0.09); t=tvec(n)
    s=np.sin(2*np.pi*2450*t)*np.exp(-t*46)+0.5*np.sin(2*np.pi*3700*t)*np.exp(-t*70)
    return mix(s,click(0.01,0.08,3,0.35))*gain
def tom(freq=110,gain=1.0,dur=0.34):
    n=secs(dur); t=tvec(n)
    f=freq*(1+0.7*np.exp(-t*30)); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)*np.exp(-t*7.5)+hp(rng.standard_normal(n),3)*np.exp(-t*30)*0.18)*gain
def marimba(freq,gain=1.0,dur=0.50):
    """wood: the fundamental plus the tuned fourth partial, and the mallet"""
    n=secs(dur); t=tvec(n); ph=2*np.pi*freq*t
    s=np.sin(ph)*np.exp(-t*5.5)+0.42*np.sin(4*ph)*np.exp(-t*16)+0.15*np.sin(10*ph)*np.exp(-t*30)
    mallet=hp(rng.standard_normal(secs(0.008)),3)*env_exp(secs(0.008),0.2)*0.22
    return mix(s*np.minimum(1,t/0.002),mallet)*gain
def deepkick(gain=1.0,dur=0.50):
    """rounder and longer than the house kick — afro sits lower and looser"""
    n=secs(dur); t=tvec(n)
    f=41+(165-41)*np.exp(-t*38)
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6.0)
    return np.tanh(mix(body,click(0.005,0.3,3,0.30))*1.8)/np.tanh(1.8)*gain

# ---- the sounds of motion --------------------------------------------------
def click(dur=0.035,tau=0.12,k=6,gain=1.0):
    n=secs(dur); x=rng.standard_normal(n)*env_exp(n,tau)
    return hp(x,k)*gain
def tick(gain=1.0): return click(0.018,0.09,4,gain)
def thud(f0=95,f1=52,dur=0.34,tau=0.16,gain=1.0):
    n=secs(dur); f=np.linspace(f0,f1,n); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env_exp(n,tau)*gain
def whoosh(dur=0.32,rise=True,gain=1.0,tilt=(90,10)):
    n=secs(dur); x=rng.standard_normal(n)
    dark, bright = ma(x,tilt[0]), hp(x,tilt[1])
    u=np.linspace(0,1,n); u = u if rise else u[::-1]
    e=np.sin(np.pi*np.linspace(0,1,n))**1.6
    return (dark*(1-u)+bright*u)*e*gain
def brush(dur,gain=1.0):
    """a loaded brush dragged across canvas — bristles, getting heavier"""
    n=secs(dur); x=rng.standard_normal(n)
    jit=np.abs(ma(rng.standard_normal(n),9))*3.2
    u=np.linspace(0,1,n)
    return ma(x,7)*jit*np.sin(np.pi*u)**1.1*(0.6+0.4*u)*gain
def slide(dur,gain=1.0):
    n=secs(dur); x=ma(rng.standard_normal(n),46)
    return x*np.sin(np.pi*np.linspace(0,1,n))**2*gain*7
def draw(dur,gain=1.0):
    n=secs(dur); x=hp(rng.standard_normal(n),3)
    e=np.linspace(1,0.35,n)*np.minimum(1,np.arange(n)/secs(0.012))
    return x*e*gain
def crackle(dur,gain=1.0):
    """the grain dissolve: the frame breaking up through the tooth of the canvas"""
    n=secs(dur); u=np.linspace(0,1,n); dens=u**2
    imp=(rng.random(n)<dens*0.03)*rng.standard_normal(n)
    return (ma(imp,3)*2.5 + hp(rng.standard_normal(n),4)*dens*0.14)*gain
def suck(dur,gain=1.0):
    n=secs(dur); u=np.linspace(0,1,n); x=rng.standard_normal(n)
    f=240*2**(u*2.4); ph=2*np.pi*np.cumsum(f)/SR
    return ((ma(x,30)*(1-u)+hp(x,6)*u)*0.7+np.sin(ph)*0.3)*(u**1.6)*gain
def pop(gain=1.0):
    n=secs(0.09); f=np.linspace(980,360,n); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env_exp(n,0.17)*gain
def squash(gain=1.0):
    n=secs(0.5); t=tvec(n)
    f=58+(220-58)*np.exp(-t*24); ph=2*np.pi*np.cumsum(f)/SR
    return mix(np.sin(ph)*env_exp(n,0.22)*0.8, thud(85,40,0.5,0.26,0.9),
               click(0.02,0.2,4,0.3))*gain
def shutter(gain=1.0,firm=False):
    a=click(0.012,0.10,3,1.0); b=click(0.014,0.12,4,0.8)
    n=secs(0.04); s=np.zeros(n); s[:len(a)]+=a; i=secs(0.009); s[i:i+len(b)]+=b[:n-i]
    if firm: s=mix(s,thud(320,130,0.04,0.25,0.6))
    return s*gain
def room(dur,gain=1.0):
    n=secs(dur); x=ma(rng.standard_normal(n),400)
    return x*np.clip(np.sin(np.pi*np.linspace(0,1,n))*3,0,1)*gain
def glide(f0,f1,t_glide,sustain,release,gain=1.0,curve=easeInOut,sat=1.9,vib=0.006):
    """THE BEND. Pitch travels f0→f1 along the exact easing the cursor drags, so the
    sound and the curve on screen are the same curve. It lands on the downbeat."""
    n=secs(t_glide+sustain+release); t=tvec(n)
    k=np.array([curve(x) for x in np.clip(t/t_glide,0,1)])
    f=f0*2**(12*np.log2(f1/f0)*k/12)
    arrived=np.clip((t-t_glide)/0.25,0,1)
    f=f*(1+vib*np.sin(2*np.pi*5.4*t)*arrived)
    ph=2*np.pi*np.cumsum(f)/SR
    s=np.zeros(n)
    for h,a in [(1,1.0),(2,0.55),(3,0.36),(4,0.22),(5,0.13),(6,0.08),(7,0.05)]:
        s+=np.sin(ph*h)*a
    s=np.tanh(s*sat)/np.tanh(sat)
    e=np.minimum(1,t/0.05); rs=t_glide+sustain
    return s*e*np.where(t>rs,np.exp(-(t-rs)/(release*0.38)),1.0)*gain

# ---- notes (A minor) -------------------------------------------------------
A1=55.0; C2=65.41; D2=73.42; E2=82.41; F2=87.31; G2=98.0; A2=110.0
C3=130.81; D3=146.83; E3=164.81; F3=174.61; G3=196.0; A3=220.0
C4=261.63; D4=293.66; E4=329.63; F4=349.23; G4=392.0; A4=440.0
Bn3=246.94; Bn4=493.88; Fs5=739.99      # Bn = B natural: B1..B6 are the film's beats
C5=523.25; D5=587.33; E5=659.26; F5=698.46; A5=880.0

# ============================================================================
# THE ARRANGEMENT — eleven bars, in two styles
#   1 intro · 2 the beat lands · 3-5 the groove · 6 the build · 7 THE DROP
#   8-9 the hero · 10-11 the end card, thinning to the last hit
# ============================================================================
def groove_house():
    """Kungs, "I Feel So Bad" — four on the floor, offbeat open hats, a pluck riff."""
    KICK=[]                      # bars that get four-on-the-floor
    FULL=range(2,12)
    for b in range(1,12):
        if b==1:   KICK+= [bar(1)+0*BEAT, bar(1)+2*BEAT]      # intro: 1 and 3 only
        elif b==6: KICK+= [bar(6)+i*BEAT for i in range(3)]   # the build drops beat 4
        elif b==11:KICK+= [bar(11)+i*BEAT for i in range(4)]
        else:      KICK+= [bar(b)+i*BEAT for i in range(4)]

    KG=0.86
    for t in KICK:
        g=KG*(0.30 if t<BAR else 1.0)
        if t>=bar(7) and t<bar(8): g*=1.06                    # the drop bar hits hardest
        put(kick(g),t,0.0)

    # clap on 2 and 4 from bar 2; none in the build's second half
    for b in range(2,12):
        for beat in (1,3):
            t=bar(b)+beat*BEAT
            if b==6 and beat==3: continue                     # hold it back into the drop
            if b==11 and beat==3: continue                    # the film has ended by then
            put(clap(0.34),t,0.04)

    # hats: closed on the beat-eighths, OPEN on the offbeat — the house signature
    for b in range(2,12):
        if b==11: continue
        for i in range(8):
            t=bar(b)+i*(BEAT/2)
            if b==6 and t>=bar(6)+3*BEAT: continue            # the build empties out
            if i%2==0: put(hat(0.085),t,0.30)
            else:      put(hat(0.115,True),t,0.34)

    # bass: A minor vamp, i–VI. Root on the downbeat, then the offbeats push it along
    VAMP={1:A1,2:A1,3:F2,4:A1,5:F2,6:A1,7:A1,8:F2,9:A1,10:F2,11:A1}
    for b in range(2,12):
        root=VAMP[b]; fifth=root*1.5
        if b==11:
            put(bass(root,BEAT*2,0.34),bar(11)); continue
        put(bass(root,BEAT*0.9,0.34),bar(b)+0*BEAT)
        if b==6: continue                                     # the build takes the bass out
        put(bass(root,BEAT*0.45,0.27),bar(b)+1.5*BEAT)
        put(bass(root,BEAT*0.45,0.27),bar(b)+2.5*BEAT)
        put(bass(fifth,BEAT*0.45,0.24),bar(b)+3.5*BEAT)

    # the pluck riff — two bars long, offbeat-led, the thing that stays in your head
    RIFF_A=[(0.5,E5),(1.0,C5),(1.5,A4),(2.0,C5),(2.5,E5),(3.0,D5),(3.5,C5)]
    RIFF_B=[(0.5,F5),(1.0,C5),(1.5,A4),(2.0,C5),(2.5,F5),(3.0,E5),(3.5,C5)]
    RIFF_BARS=[(3,RIFF_A),(4,RIFF_B),(5,RIFF_A),(7,RIFF_A),(8,RIFF_B),(9,RIFF_A),(10,RIFF_B)]
    for b,riff in RIFF_BARS:
        g=0.20 if b!=7 else 0.24
        for off,f in riff:
            put(pluck(f,0.34,g),bar(b)+off*BEAT,-0.5+1.0*(off/3.5))

    # chord stabs on the offbeat of 2 and 4
    AM7=[A3,C4,E4,G4]; FM7=[F3,A3,C4,E4]
    for b in range(3,11):
        ch=AM7 if VAMP[b]==A1 else FM7
        for beat in (1.5,3.5):
            l,r=stab(ch,0.26,0.085); put_st(l,r,bar(b)+beat*BEAT)

    # risers into the two landings that matter, and the exhale after the drop
    put(riser(BAR,0.16), bar(1),0.0)                          # into the beat at 1.92
    put(riser(BAR*0.9,0.30), bar(7)-BAR*0.9,0.0)              # into THE DROP at 11.52
    put(impact(0.55), bar(7),0.0)
    put(downlift(1.0,0.13), bar(7)+BEAT*0.5,0.2)
    put(riser(BEAT*3,0.13), bt(33),0.0)                       # into the end card
    put(impact(0.26), bt(36),0.0)

def groove_afro():
    """HUGEL & SOLTO, "Jamaican (Bam Bam)" — Afro House. The original is 122 BPM;
    the genre lives at 120-126, so it is built at the film's own 125 and nothing
    in the picture has to move. Everything below is written in SIXTEENTHS of a
    bar, because that is where this groove actually lives."""
    S=BEAT/4                                       # a sixteenth: 0.12 s
    def at(b,i): return bar(b)+i*S                 # bar b, sixteenth i

    # the rolling conga tumbao — it plays BETWEEN the kicks, which is the style
    TUMBAO=[(3,'h'),(6,'l'),(7,'h'),(10,'l'),(11,'h'),(14,'l'),(15,'h')]
    CLAVE_A=[0,6,12]; CLAVE_B=[4,10]               # 3-2 son clave across two bars
    BASSFIG=[0,6,10,14]
    # the marimba hook, A Dorian — minor, but with the bright sixth the style wants
    MAR_A=[(0,A4),(3,C5),(6,D5),(8,E5),(11,D5),(14,C5)]
    MAR_B=[(0,G4),(3,Bn4),(6,D5),(8,E5),(11,C5),(14,Bn4)]
    VAMP={1:A1,2:A1,3:A1,4:G2,5:A1,6:G2,7:A1,8:G2,9:A1,10:G2,11:A1}
    PAD ={'A':[A3,C4,E4,Bn4],'G':[G3,Bn3,D4,E4]}

    for b in range(1,12):
        A = VAMP[b]==A1
        intro, build, last = b==1, b==6, b==11

        # kick — four on the floor, deeper and longer than the house kit
        for i in (0,4,8,12):
            if intro and i in (4,12): continue      # bar 1: 1 and 3 only
            if build and i==12: continue            # the build drops beat 4
            put(deepkick(0.30 if intro else 0.92), at(b,i))

        # shaker on every sixteenth, accented on the offbeats — the engine
        if not intro:
            for i in range(16):
                if build and i>=12: continue
                put(shaker(0.075 if i%4==2 else 0.048, accent=(i%4==2)), at(b,i), 0.38)

        # congas between the kicks
        if not intro and not last:
            for i,k in TUMBAO:
                if build and i>=12: continue
                g=0.30 if k=='h' else 0.26
                put(conga(430 if k=='h' else 232, k=='h', g), at(b,i), -0.42 if k=='l' else 0.30)

        # clave, and the clap on 2 and 4
        if b>=3 and not last:
            for i in (CLAVE_A if b%2 else CLAVE_B): put(clave(0.10), at(b,i), -0.30)
        if b>=2 and not last:
            for i in (4,12):
                if build and i==12: continue
                put(clap(0.30), at(b,i), 0.04)

        # the bass bounces off the beat rather than sitting on it
        if b>=2 and not build:
            root=VAMP[b]
            if last:
                put(bass(root,BEAT*2,0.34), at(b,0))
            else:
                for n,i in enumerate(BASSFIG):
                    put(bass(root*(1.5 if i==14 else 1.0), BEAT*(0.8 if i==0 else 0.4),
                             0.34 if i==0 else 0.26), at(b,i))

        # the marimba hook, in from bar 3, out through the build
        if b>=3 and not build and not last:
            for i,f in (MAR_A if A else MAR_B):
                put(marimba(f,0.155 if b!=7 else 0.185), at(b,i), -0.45+0.9*(i/15))

        # a warm pad, very low
        if b>=2 and not last:
            l,r=stab(PAD['A' if A else 'G'],BAR*0.8,0.030); put_st(l,r,bar(b))

        # "BAM BAM" — two toms answering every second bar, and the name of the track
        if b in (4,6,8,10):
            put(tom(126,0.34), at(b,13), -0.25); put(tom(104,0.40), at(b,15), 0.25)

    # a tom fill runs the build into the drop, and the drop lands hardest
    for n,i in enumerate((8,10,12,13,14,15)):
        put(tom(150-n*11, 0.22+0.05*n), at(6,i), -0.5+1.0*n/5)
    put(riser(BAR*0.9,0.26), bar(7)-BAR*0.9, 0.0)
    put(impact(0.50), bar(7), 0.0)
    put(downlift(1.0,0.12), bar(7)+BEAT*0.5, 0.2)
    put(riser(BEAT*3,0.11), bt(33), 0.0)
    put(impact(0.22), bt(36), 0.0)


{ 'house': groove_house, 'afro': groove_afro }[STYLE]()

# ============================================================================
# THE SOUNDS OF MOTION — every cue on the frame where the motion happens,
# which is now also a beat, an eighth or a sixteenth
# ============================================================================

# ---- bar 1 · STILL. --------------------------------------------------------
put(room(BAR,0.030),0.00)
for n in (1,2,3): put(tick(0.09),bt(n))                   # the caret blinks on the beat
put(crackle(BEAT,0.20),bt(3),0.0)                         # the grain dissolve, one beat

# ---- bar 2 · the title -----------------------------------------------------
put(draw(0.24,0.15),bt(4),-0.3)                           # the rule draws
put(whoosh(0.20,True,0.08),bt(4)-0.04,-0.2)               # WHY DO WE NEED rises
put(whoosh(BEAT*0.9,True,0.13,(70,8)),bt(5),0.0)          # MOTION falls
put(thud(90,48,0.42,0.15,0.30),bt(7))                     # …and LANDS on beat 3
put(click(0.03,0.08,4,0.20),bt(7))
put(tick(0.08),bt(7)+BEAT*0.34)                           # the settle bounce
put(whoosh(0.18,True,0.07),bt(6.5),0.2)                   # EDITORS? rises
put(brush(BEAT,0.50),bt(7),-0.6)                          # THE PAINT WIPE crosses
put(click(0.04,0.09,5,0.26),bt(8),0.4)                    # …and the paint lands

# ---- bars 3-5 · the anatomy ------------------------------------------------
for k in range(3):                                        # each label snaps onto the &
    s0=B3[0]+k*STUDY
    put(whoosh(0.10,False,0.09,(50,6)), s0+0.1938*STUDY*ANTIC_DIP-0.03, -0.5)
    put(whoosh(0.09,True,0.12),         s0+0.1938*STUDY*ANTIC_GO,       -0.4)
    put(click(0.03,0.08,4,0.26),        s0+0.1938*STUDY*ANTIC_HIT,      -0.4)

# 01 SPACING — a mark on every sixteenth. They are even in time and the chart
# crowds where the head is slow, so the ticks ARE the hi-hat grid.
NG=15; eS=bez(0.5,0,0.5,1)
posn=[eS(i/(NG-1)) for i in range(NG)]
for i in range(NG):
    dx=(posn[i]-posn[i-1]) if i>0 else (posn[1]-posn[0])
    kf=int(round(9-6*dx/0.14))                            # slow = dull, fast = bright
    put(click(0.012,0.10,kf,0.15), B3[0]+i*(BEAT/4), -0.6+1.2*i/(NG-1))

# 02 WEIGHT — it contacts on beat 2 and taps on beat 4 of its bar
w0=B3[0]+STUDY
put(whoosh(BEAT,True,0.15,(120,12)), w0, 0.0)
put(squash(0.80), w0+0.25*STUDY)                          # CONTACT, on the beat
put(thud(120,60,0.22,0.15,0.26), w0+0.75*STUDY)           # the second, smaller contact
put(click(0.02,0.1,4,0.10), w0+0.75*STUDY)

# 03 RHYTHM — seven bars arrive one eighth apart, marching up the offbeats
r0=B3[0]+2*STUDY; NOTES=[A4,C5,D5,E5,F5,A5,C5*2]
for i in range(7):
    arrive=r0+(0.125*i+0.1938*ANTIC_HIT)*STUDY
    put(pluck(NOTES[i],0.30,0.20), arrive, -0.55+1.1*i/6)
    put(click(0.02,0.1,4,0.09), arrive, -0.55+1.1*i/6)

put(whoosh(0.24,False,0.18,(60,8)), B4[0]-PRE, 0.3)       # the band folds into the panel
put(click(0.03,0.07,4,0.22), B4[0])

# ---- bar 6 · the setup, one move per beat ---------------------------------
put(room(BAR*2,0.010),B4[0])
put(slide(BEAT,0.09),bt(20),0.3)                          # the cursor comes in
put(click(0.03,0.09,5,0.36),bt(21),0.2)                   # click — the frame is selected
put(tick(0.24),bt(22)); put(pluck(D5,0.22,0.09),bt(22))   # keyframe one
put(tick(0.22),bt(22.5)); put(pluck(A4,0.22,0.09),bt(22.5))  # keyframe two
put(draw(0.22,0.12),bt(22.2),-0.2)                        # the curve is drawn
put(tick(0.16),bt(23),-0.4)                               # the handle is grabbed

# THE BEND — the drag runs bt(23)→bt(24), and so does the pitch, on the same ease
put(glide(A4,E5,BEAT,BEAT*1.2,0.5,0.34), bt(23), 0.0)
put(glide(A3,E4,BEAT,BEAT*1.2,0.5,0.15,sat=1.2,vib=0.004), bt(23), 0.0)

# ---- bar 7 · the drop: the post comes apart and rebuilds on the eighths ----
put(suck(BEAT,0.20), bt(24), -0.2)
for i in range(5):
    home=bt(24)+(0.163+i*0.125+0.25*BACK_HIT)*BAR         # 12.00 12.24 … 12.96
    put(click(0.03,0.08,4,0.30), home, -0.4+0.8*i/4)
    put(pluck([A4,C5,E5,A5,C5*2][i],0.28,0.15), home, -0.4+0.8*i/4)
put(whoosh(0.24,True,0.15), B5[0]-PRE, 0.3)               # the curve fills the frame
put(click(0.04,0.09,5,0.22), B5[0], 0.2)

# ---- bars 8-9 · the hero line, one line a beat ----------------------------
HERO=['SOMEONE','HAS TO DECIDE','HOW THINGS','MOVE.']
for i,h in enumerate(HERO):
    t0=bt(28+i); st=(BEAT/2)/max(1,len(h)-1)
    for k,ch in enumerate(h):
        if ch==' ': continue
        if i<3: put(click(0.010,0.08,4+(i%2),0.075), t0+k*st, -0.5+1.0*k/max(1,len(h)-1))
    if i==3:                                              # MOVE. is home on the downbeat
        put(thud(110,58,0.30,0.16,0.30), bt(32), 0.0)
        put(click(0.025,0.08,4,0.16), bt(32))
put(click(0.03,0.09,5,0.22),bt(33),0.3)                   # handles snap around MOVE.

put(whoosh(0.24,True,0.15), B6[0]-PRE, 0.0)               # the page turns up
put(click(0.04,0.09,5,0.20), B6[0], 0.1)

# ---- bars 10-11 · the end card --------------------------------------------
put(draw(0.24,0.12),bt(36),-0.3)
for b,g in [(36,0.12),(37,0.10),(38,0.10),(40,0.08)]:     # the card sets itself
    put(thud(160,90,0.10,0.2,g),bt(b),-0.2); put(click(0.02,0.1,5,g*0.8),bt(b),-0.2)

# the name tries on eleven faces: eight sixteenths, then two beats, landing on
# Inter on the last downbeat — the cycle is played, not drifted
NAMEHOLD=[0.12,0.12,0.12,0.12,0.12,0.12,0.12,0.12,0.48,0.48]
c=B6[0]
for i,d in enumerate(NAMEHOLD):
    c+=d
    put(shutter(0.26 if i<8 else 0.34, firm=(i==9)), c, -0.25)

put(suck(0.16,0.22), bt(40), -0.1)                        # it collapses to a point…
put(pop(0.26), bt(40)+0.24, -0.1)                         # …and the mark opens

# the joke: the cursor comes back, MOVE. slides out on 3 and springs home on 4
put(slide(0.24,0.09), bt(41), 0.4)
put(click(0.03,0.09,5,0.34), bt(41.5), 0.3)
put(whoosh(0.09,False,0.11,(50,6)), bt(42.6), 0.2)        # it pulls back…
put(whoosh(0.12,True,0.15), bt(42.85), 0.3)               # …and goes
put(click(0.03,0.08,4,0.26), bt(43), 0.5)                 # out, on beat 3
put(kick(0.55), bt(43))
put(click(0.025,0.08,4,0.20), bt(44), 0.1)                # home, on beat 4
put(thud(90,46,0.30,0.18,0.30), bt(44))

# the canvas turns back over: the last frame matches the first, so the Reel loops
put(whoosh(0.30,False,0.20,(80,10)), bt(43.25), 0.0)
put(thud(80,44,0.15,0.2,0.34), bt(43.75))
# silence into the loop point — and bar 1 opens quiet, so the seam is inaudible

# ---- the texture layer -----------------------------------------------------
# Six recorded objects under the synthesised cues (see texture.py). Off by
# default: `python3 sound.py --texture out.wav` turns it on. Every time below
# is an existing cue time, so nothing is re-timed and the grid is untouched.
if TEXTURE:
    import texture as TX
    put(TX.tex('dissolve'), bt(3),        0.0)   # under crackle()
    put(TX.tex('wipe'),     bt(7),       -0.6)   # under brush(), same pan
    put(TX.tex('ball_1'),   w0+0.25*STUDY, 0.1)  # under squash()
    put(TX.tex('ball_2'),   w0+0.75*STUDY, 0.1)  # under the second thud()
    put(TX.tex('drag'),     bt(23),      -0.2)   # under the two glide()s
    put(TX.tex('page'),     B6[0]-PRE,    0.0)   # under the whoosh() page turn
    put(TX.tex('mark'),     bt(40)+0.24, -0.1)   # under pop()

# ============================================================================
# master
# ============================================================================
out=np.stack([L,R])
out-=out.mean(axis=1,keepdims=True)
fade=secs(0.02)
out[:, :fade]*=np.linspace(0,1,fade); out[:,-fade:]*=np.linspace(1,0,fade)
out=out/np.abs(out).max()
out=np.tanh(out*1.30)/np.tanh(1.30)                       # glue on the loud hits
out=out/np.abs(out).max()*0.80                            # ≈ −1 dBTP after AAC
pcm=(np.clip(out.T,-1,1)*32767).astype('<i2')

DEFAULT='sound.wav' if STYLE=='house' else 'sound_afro.wav'
P=ARGV[0] if ARGV else os.path.join(os.path.dirname(os.path.abspath(__file__)),DEFAULT)
with wave.open(P,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", P, round(os.path.getsize(P)/1024), "KB   ", STYLE, BPM, "BPM  ", BARS, "bars  ", round(DUR,3), "s")
if TEXTURE: print(TX.report())
