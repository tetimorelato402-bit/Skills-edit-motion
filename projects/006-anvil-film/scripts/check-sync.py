#!/usr/bin/env python3
"""Assert video.html and sound.py are still cut to the same grid.

sound.py duplicates the film's event times, because the alternative — parsing
JavaScript from Python — is worse. Duplication is fine as long as drifting apart
is LOUD, and a timing change that only lands in one of the two files is the most
expensive mistake available here: it is inaudible in a still, invisible in the
log, and only shows up as a soft, wrong-feeling cut once the film is assembled.

The film is the authority. This drives video.html in the same headless Chromium
render.py uses, reads the real EDITS array out of the page, runs sound.py to a
throwaway wav, and diffs the two.

    python3 scripts/check-sync.py       # exit 0 = in sync
"""
import os, sys, runpy, tempfile
from playwright.sync_api import sync_playwright

HERE=os.path.dirname(os.path.abspath(__file__))
HTML=os.path.join(HERE,'..','source','video.html')
SND =os.path.join(HERE,'..','sound.py')
CHROME="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# every kind in the film, and the name it answers to in sound.py.
# None means DELIBERATELY SILENT — the frame moving is not an event the ear
# needs told about, and a film where every edit has a sound has no accents.
MAP={'card':'CARDS','photo':'PHOTOS','flash':'FLASH','invert':'INVERT',
     'bars':'LETTERBOX','wipe':'WIPE',
     'punch':None,'jump':None,'ghost':None,'split':None}

def film():
    errs=[]
    with sync_playwright() as p:
        br=p.chromium.launch(executable_path=CHROME)
        pg=br.new_page(viewport={"width":1080,"height":1920})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://"+os.path.abspath(HTML))
        pg.wait_for_function("window.renderFrame!==undefined")
        d=pg.evaluate("""()=>({
            edits:EDITS.map(e=>[e.k,+e.t.toFixed(6)]),
            bleed:BLEED.map(b=>+b[0].toFixed(6)),
            pages:PAGES.map(p=>[+p.t.toFixed(6),p.cps,
                     p.lines.reduce((a,l)=>a+l.reduce((b,t)=>b+t.s.length,0),0)]),
            marks:{GO:GO,REDACT:REDACT,PAUSE:PAUSE,PAYOFF:PAYOFF,CUT:CUT,
                   DUR:DUR,BPM:BPM}})""")
        br.close()
    if errs: sys.exit("video.html threw: "+errs[0])
    return d

def score():
    tmp=os.path.join(tempfile.gettempdir(),'_sync_check.wav')
    argv=sys.argv[:]; sys.argv=[SND,tmp]
    try: ns=runpy.run_path(SND, run_name='__main__')
    finally: sys.argv=argv; os.path.exists(tmp) and os.remove(tmp)
    return ns

def near(a,b,tol=1e-4): return abs(a-b)<tol
def cmp_list(name, film_ts, snd_ts, bad):
    f=sorted(round(x,6) for x in film_ts); s=sorted(round(x,6) for x in snd_ts)
    if len(f)!=len(s) or any(not near(x,y) for x,y in zip(f,s)):
        bad.append(f"{name}: film {f}\n{' '*(len(name)+2)}sound {s}")

d=film(); ns=score(); bad=[]

byk={}
for k,t in d['edits']: byk.setdefault(k,[]).append(t)
for k,ts in sorted(byk.items()):
    if k not in MAP: bad.append(f"{k}: in the film, not in the map — sounded or silent?")
    elif MAP[k] is None: pass
    elif MAP[k] not in ns: bad.append(f"{k}: sound.py has no {MAP[k]}")
    else: cmp_list(k, ts, ns[MAP[k]], bad)

cmp_list('bleed', d['bleed'], ns['BLEED'], bad)

fp=d['pages']; sp=ns['PAGES']
if len(fp)!=len(sp): bad.append(f"pages: film {len(fp)}, sound {len(sp)}")
else:
    for i,(a,b) in enumerate(zip(fp,sp)):
        if not near(a[0],b[0]) or a[1]!=b[1] or a[2]!=b[2]:
            bad.append(f"page {i+1}: film t={a[0]} cps={a[1]} chars={a[2]}  "
                       f"sound t={b[0]} cps={b[1]} chars={b[2]}")

for k,v in d['marks'].items():
    if k not in ns: bad.append(f"{k}: missing from sound.py")
    elif not near(float(v), float(ns[k])): bad.append(f"{k}: film {v}, sound {ns[k]}")

if bad:
    print("OUT OF SYNC — sound.py and video.html disagree:\n")
    for b in bad: print("  "+b)
    sys.exit(1)
print(f"in sync: {len(d['edits'])} edits, {len(fp)} pages, "
      f"{len(d['marks'])} marks, {sum(1 for k in byk if MAP.get(k) is None)} kinds silent by design")
