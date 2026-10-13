#!/usr/bin/env python3
"""Oil-paint plates + canvas weave for Study 001.

Built the way the portrait is: broad soft slabs first, medium strokes over them,
a few crisp accents last, then the whole thing lit from a height map so the paint
reads thick. Colour never leaves the warm family — only value moves.
"""
import numpy as np, os
from PIL import Image, ImageDraw, ImageFilter

OUT="/tmp/claude-0/-home-user-Skills-edit-motion/6f53a120-094f-50a3-8e5f-8ef8a3354c74/scratchpad/build/tex"
os.makedirs(OUT, exist_ok=True)
hx=lambda h:tuple(int(h.lstrip('#')[i:i+2],16) for i in (0,2,4))

def tone(base, ramp, rng, pull=0.30, val=0.075):
    """A colour near `base`: drift toward another ramp colour, then move value only."""
    o=np.array(ramp[rng.integers(len(ramp))],float)
    t=rng.uniform(0,pull)
    c=np.array(base,float)*(1-t)+o*t
    c*=rng.normal(1.0,val)
    return tuple(int(v) for v in np.clip(c,0,255))

def stamp(dr,dh,x,y,r,c,al,h):
    dr.ellipse([x-r,y-r*0.92,x+r,y+r*0.92],fill=c+(al,))
    dh.ellipse([x-r,y-r*0.92,x+r,y+r*0.92],fill=h)

def strokes(dr,dh,rng,w,h,ramp,base,n,wid,ln,alpha,tilt,bristle):
    """Each stroke is stamped along its path, so ends are round and edges breathe."""
    for _ in range(n):
        c0=tone(base,ramp,rng,pull=0.42,val=0.13)
        a=np.deg2rad(rng.normal(0,tilt)+ (90 if rng.random()<0.80 else 0))
        x0,y0=rng.uniform(-0.1*w,1.1*w), rng.uniform(-0.1*h,1.1*h)
        L=rng.uniform(*ln)*max(w,h); W=rng.uniform(*wid)
        dx,dy=np.cos(a),np.sin(a); px,py=-dy,dx
        al0=rng.uniform(*alpha)
        subs = max(2,int(W/14)) if bristle else 1
        for b in range(subs):
            off=(b/max(1,subs-1)-0.5)*W*0.9 if subs>1 else 0.0
            rad=(W/subs)*0.62 if subs>1 else W*0.5
            cb=tone(c0,ramp,rng,pull=0.14,val=0.07)
            ab=al0*rng.uniform(0.55,1.0)
            step=max(2.0,rad*0.55)
            k=0.0
            while k<L:
                u=k/L
                taper=np.sin(np.pi*np.clip(u,0,1))**0.35        # thin at both ends
                rr=rad*taper*rng.uniform(0.82,1.18)
                if rr>0.6:
                    wob=rng.normal(0,rad*0.10)
                    stamp(dr,dh,
                          x0+dx*k+px*off+px*wob, y0+dy*k+py*off+py*wob,
                          rr, cb, int(np.clip(ab*rng.uniform(0.75,1.0),0,255)),
                          int(np.clip(ab*0.55,0,255)))
                k+=step

def plate(w,h,ramp_hex,base_hex,seed,density=1.0,tilt=7,light=54.0):
    rng=np.random.default_rng(seed)
    ramp=[hx(c) for c in ramp_hex]; base=hx(base_hex)
    img=Image.new("RGB",(w,h),base)
    ht =Image.new("L",(w,h),0)
    D=max(w,h)/1920.0

    def layer(n,wid,ln,alpha,bristle,blur):
        nonlocal img,ht
        ov=Image.new("RGBA",(w,h),(0,0,0,0)); hv=Image.new("L",(w,h),0)
        strokes(ImageDraw.Draw(ov,"RGBA"),ImageDraw.Draw(hv,"L"),rng,w,h,ramp,base,
                int(n*density),wid,ln,alpha,tilt,bristle)
        if blur: ov=ov.filter(ImageFilter.GaussianBlur(blur)); hv=hv.filter(ImageFilter.GaussianBlur(blur))
        img=Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")
        ht =Image.fromarray(np.clip(np.asarray(ht,float)+np.asarray(hv,float)*0.8,0,255).astype(np.uint8))

    layer( 60,(150*D,340*D),(0.30,0.75),( 70,120),False,7.0)   # broad ground slabs
    layer(110,( 60*D,150*D),(0.18,0.48),( 55,105),True ,2.4)   # the body of the paint
    layer( 90,( 22*D, 60*D),(0.10,0.30),( 60,120),True ,0.8)   # working strokes
    layer( 40,(  7*D, 20*D),(0.05,0.16),( 70,140),False,0.0)   # final crisp accents

    H=np.asarray(ht.filter(ImageFilter.GaussianBlur(1.4))).astype(float)/255.0
    gy,gx=np.gradient(H)
    A=np.asarray(img).astype(float)+np.clip(-gx*0.75-gy*0.75,-1,1)[...,None]*light
    return Image.fromarray(np.clip(A,0,255).astype(np.uint8))

def weave(w,h,seed=11):
    rng=np.random.default_rng(seed)
    y,x=np.mgrid[0:h,0:w].astype(float)
    th=(np.sin(x*np.pi/3.0)*0.5+0.5)*0.5+(np.sin(y*np.pi/3.0)*0.5+0.5)*0.5
    n=rng.normal(0,1,(h,w))
    n=np.asarray(Image.fromarray(((n-n.min())/np.ptp(n)*255).astype(np.uint8))
                 .filter(ImageFilter.GaussianBlur(0.6))).astype(float)/255.0
    g=np.clip(0.50+0.085*(th-0.5)*2+0.075*(n-0.5)*2,0,1)*255
    return Image.fromarray(np.dstack([g,g,g]).astype(np.uint8))

W,H=1080,1920
plate(W,H,["#1E0B05","#2B100A","#3A1810","#48200F","#5D1E0F","#6B3A22","#54291A","#20100B"],"#2B100A",1,light=86.0)\
    .save(f"{OUT}/plate_ink.png")
plate(W,H,["#EFE3CC","#E4CBA0","#F6F0E0","#DED0B2","#CEA471","#EADCC2"],"#EFE3CC",2)\
    .save(f"{OUT}/plate_paper.png")
plate(W,760,["#B07A3F","#A67545","#935730","#C38E52","#B48B56","#8E5A2C"],"#B07A3F",3,
      density=1.15,tilt=9).save(f"{OUT}/plate_ochre.png")
weave(360,360).save(f"{OUT}/weave.png")

from PIL import Image as I
s=I.new("RGB",(1020,470),(232,232,232))
s.paste(I.open(f"{OUT}/plate_ink.png").resize((236,420)),(10,10))
s.paste(I.open(f"{OUT}/plate_paper.png").resize((236,420)),(256,10))
s.paste(I.open(f"{OUT}/plate_ochre.png").resize((236,166)),(502,10))
s.paste(I.open(f"{OUT}/weave.png").resize((236,236)),(502,186))
s.paste(I.open(f"{OUT}/plate_ink.png").crop((300,600,540,840)),(748,10))
s.paste(I.open(f"{OUT}/plate_paper.png").crop((300,600,540,840)),(748,254))
s.save(f"{OUT}/preview.png"); print("plates rebuilt")

# --- the paint wipe matte ---------------------------------------------------
# A mask whose left half is opaque and right half clear, with a ragged, bristled
# boundary. Sliding it across an element reveals that element as if a loaded brush
# were dragged over it.
# NOT used by video.html: headless Chromium will not paint an element masked with a
# url() image (see CLAUDE.md gotchas), so the film builds the same edge procedurally
# from a gradient mask + displacement filter. Kept because it is a ready-made matte
# for the same wipe in Resolve/Fusion.
def wipe_mask(w, h, seed=23):
    rng = np.random.default_rng(seed)
    y = np.arange(h)
    edge = (w/2
            + 74*np.sin(y*0.0122 + 1.1)
            + 42*np.sin(y*0.0339 + 0.4)
            + 19*np.sin(y*0.0871 + 2.7))
    # bristles: some rows carry paint much further than their neighbours
    fine = rng.normal(0, 1, h)
    fine = np.convolve(fine, np.ones(9)/9, mode='same')
    edge += fine * 46
    tips = rng.normal(0, 1, h)
    tips = np.convolve(tips, np.ones(3)/3, mode='same')
    edge += np.where(tips > 1.05, (tips - 1.05) * 150, 0)      # long dragged tips
    # feather varies per row: a real edge is crisp in places, dry-brushed in others
    feather = 14 + 30*(0.5 + 0.5*np.sin(y*0.0207 + 0.9)) + np.abs(fine)*16
    x = np.arange(w)[None, :]
    a = np.clip((edge[:, None] - x) / feather[:, None], 0, 1)
    # break up the trailing edge so it reads as bristle, not a gradient
    tex = rng.normal(0, 1, (h, w))
    tex = np.asarray(Image.fromarray(((tex - tex.min())/np.ptp(tex)*255).astype(np.uint8))
                     .filter(ImageFilter.GaussianBlur(1.1))).astype(float)/255.0
    band = 1 - np.abs(a - 0.5)*2                                # strongest mid-edge
    a = np.clip(a + (tex - 0.5) * 0.85 * band, 0, 1)
    alpha = (a*255).astype(np.uint8)
    rgb = np.full((h, w, 3), 255, np.uint8)
    Image.fromarray(np.dstack([rgb, alpha]), 'RGBA').save(f"{OUT}/wipe_mask.png")

wipe_mask(2160, 1920)
print("wipe mask written")
