#!/bin/bash
# ============================================================================
#  Build "It isn't moving yet" end to end.
#
#  The film is THREE legs now, not two, because it closes into a loop:
#
#    A  bars  1-11   Blender   Act I: the dark room, the growth, the petal drop
#    B  bars 12-23   Chromium  the studio barrage, and the break
#    C  bars 24-27   Blender   the last petal, falling back into the jar
#
#  Blender frames are numbered off the FILM's clock, not each leg's, so leg C
#  starts at f01027 and there is nothing to renumber. Legs are conformed
#  separately and concatenated — never filtered together (see BUILD.md).
#
#  Every stage is resumable: each pass counts what is already on disk and
#  carries on. The container restarts under sustained load, and a three-hour
#  render that cannot resume is a three-hour render that never finishes.
# ============================================================================
set -e
cd /home/user/Skills-edit-motion/projects/003-it-isnt-moving-yet
P=$(pwd)
BEAT=$(python3 -c "print(60/129)")
A_END=$(python3 -c "print(round(44*60/129*24))")      # 491
C_BEG=$(python3 -c "print(round(92*60/129*24))")      # 1027
C_END=$(python3 -c "print(round(108*60/129*24))")     # 1206
B_N=$(python3 -c "print(round((92-44)*60/129*120))")  # 2679

mkdir -p outputs/plant_hi source/frames120

# ---------------------------------------------------------------------------
#  RESUME IS ONLY SAFE IF THE FRAMES ON DISK CAME FROM THIS TIMELINE.
#
#  Every stage below resumes by counting files, which cannot tell "already
#  rendered" from "rendered under a DIFFERENT structure". It bit immediately:
#  the first run of this script found 369 Act I frames and 2304 studio frames
#  left over from the 18-bar cut at 125 BPM, counted them as progress, and
#  cheerfully set about finishing a film half of which was the previous edit.
#  Nothing errors. The frames are all valid PNGs of plausible pictures.
#
#  So each frame directory carries a signature of the constants that produced
#  it, and a mismatch wipes the directory rather than resuming into it. Stale
#  frames are worth less than nothing: they cost a whole render to discover.
# ---------------------------------------------------------------------------
SIG=$(python3 - <<'PY'
import sys, hashlib
sys.path.insert(0, "source/blender")
import plant
print(hashlib.sha1(repr((
    plant.BPM, plant.DARK, plant.CLIMB, plant.BUD, plant.OPEN, plant.HOLD,
    plant.DETACH, plant.FALL, plant.ACT_I_END, plant.ENDFALL, plant.ENDDIE,
    plant.FILM_END, plant.GLITCH_AT,
)).encode()).hexdigest()[:16])
PY
)
for d in outputs/plant_hi source/frames120; do
  if [ ! -f "$d/.sig" ] || [ "$(cat $d/.sig)" != "$SIG" ]; then
    n=$(ls $d 2>/dev/null | grep -c '^f' || true)
    [ "${n:-0}" -gt 0 ] && echo "  $d holds $n frames from a different timeline — clearing"
    rm -f $d/f*.png
    echo "$SIG" > $d/.sig
  fi
done

echo "=== leg A: Act I, frames 0-$A_END at 24fps ==="
for p in $(seq 1 40); do
  n=$(ls outputs/plant_hi 2>/dev/null | grep -c '^f' || echo 0)
  have=$(python3 -c "
import glob,re
f=[int(re.findall(r'\d+',x)[-1]) for x in glob.glob('outputs/plant_hi/f*.png')]
print(len([i for i in f if i < $A_END]))")
  [ "$have" -ge "$A_END" ] && { echo "  leg A complete"; break; }
  (cd source/blender && python3 render_plant.py --fps 24 --res 540 --samples 24 \
     --out ../../outputs/plant_hi --t0 0 --t1 $(python3 -c "print(44*60/129)") \
     --start "$have" 2>&1 | grep -E "s/frame|Error|Traceback" | tail -2)
done

echo "=== leg C: the loop back, frames $C_BEG-$C_END at 24fps ==="
for p in $(seq 1 40); do
  have=$(python3 -c "
import glob,re
f=[int(re.findall(r'\d+',x)[-1]) for x in glob.glob('outputs/plant_hi/f*.png')]
f=[i for i in f if i >= $C_BEG]
print($C_BEG + len(f))")
  [ "$have" -ge "$C_END" ] && { echo "  leg C complete"; break; }
  (cd source/blender && python3 render_plant.py --fps 24 --res 540 --samples 24 \
     --out ../../outputs/plant_hi --t0 $(python3 -c "print(92*60/129)") \
     --t1 $(python3 -c "print(108*60/129)") --start "$have" 2>&1 \
     | grep -E "s/frame|Error|Traceback" | tail -2)
done

echo "=== the question, composited over Act I ==="
python3 source/render_overlay.py --html source/question.html \
        --frames outputs/plant_hi --fps 24

# The glitch pass and the whole studio composite the plate, so it is copied in
# here rather than by hand — the same class of mistake as the stale frames
# above, and it fails the same silent way.
echo "=== syncing the extracted textures ==="
cp outputs/handoff/handoff.png source/tex/act1_last.png
cp outputs/handoff/poppy.png   source/tex/poppy.png

echo "=== the fall's two glitch frames, substituted in ==="
python3 source/render_glitch.py --frames outputs/plant_hi --fps 24

echo "=== leg B: the studio, $B_N frames at 120fps ==="
for p in $(seq 1 40); do
  n=$(ls source/frames120 2>/dev/null | grep -c '^f' || echo 0)
  [ "$n" -ge "$B_N" ] && { echo "  leg B complete"; break; }
  (cd source && python3 render.py --out frames120 --fps 120 --start "$n" 2>&1 \
     | grep -E "s/frame|frames in|Error" | tail -2)
done

echo "=== conform and assemble ==="
bash assemble.sh
