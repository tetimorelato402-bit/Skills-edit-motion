#!/bin/bash
# ============================================================================
#  Build "It isn't moving yet" end to end.
#
#  ONE LEG NOW. The whole film is Blender — Act I, the fall, the studio, the
#  loop back — 1206 frames at 24fps numbered off the film's own clock. The 2D
#  half is in source/attic/ and nothing here calls it.
#
#  Every stage is resumable: each pass finds the first frame actually MISSING
#  from its range (not the file count — see BUILD.md) and fills that gap. The
#  frame directory carries a signature of the timeline that produced it, and a
#  mismatch wipes it rather than resuming into somebody else's film.
#
#  This container renders at ~4-40s/frame on four cores. A GPU does the same
#  frames in well under a second. Same script either way.
# ============================================================================
set -e
cd "$(dirname "$0")"
P=$(pwd)

# WHICH PYTHON. Linux: python3. Windows (Git Bash): the venv gives `python`,
# and `python3` is often the Microsoft Store stub that opens a shop window.
# `PY=...` in the environment overrides both.
if [ -z "$PY" ]; then
  case "$OSTYPE" in
    msys*|cygwin*|win32*) PY=$(command -v python || command -v python3 || true) ;;
    *)                    PY=$(command -v python3 || command -v python || true) ;;
  esac
fi
[ -n "$PY" ] || { echo "no python found — install Python 3.11 and activate the venv"; exit 1; }
$PY -c "import sys; assert sys.version_info[:2] == (3, 11), sys.version" \
  || { echo "bpy 4.5 needs Python 3.11 exactly; $PY is $($PY -V)"; exit 1; }
export PY

# ONE BUILD AT A TIME, where the OS can enforce it. Two overlapping builds once
# wrote one mp4 that probed fine and would not decode. flock is Linux; Git Bash
# on Windows has no flock and the lock is simply skipped there.
exec 9>"${TMPDIR:-/tmp}/.build-003.lock"
if command -v flock >/dev/null 2>&1 && ! flock -n 9; then
  echo "another build is already running — refusing to start a second"
  exit 1
fi

RES=${RES:-540}
SAMPLES=${SAMPLES:-24}
FPS=24
N=$($PY -c "import sys; sys.path.insert(0,'source/blender'); import plant; print(round(plant.FILM_END*$FPS))")
mkdir -p outputs/film

SIG=$($PY - <<PY
import sys, hashlib
sys.path.insert(0, "source/blender")
import plant, inspect
src = inspect.getsource(plant)
print(hashlib.sha1((src + "$RES/$SAMPLES").encode()).hexdigest()[:16])
PY
)
if [ ! -f outputs/film/.sig ] || [ "$(cat outputs/film/.sig)" != "$SIG" ]; then
  n=$(ls outputs/film 2>/dev/null | grep -c '^f' || true)
  [ "${n:-0}" -gt 0 ] && echo "  outputs/film holds $n frames from different inputs — clearing"
  rm -f outputs/film/f*.png
  echo "$SIG" > outputs/film/.sig
fi

next_gap() {
  $PY -c "
import glob, re, sys
d, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
have = set(int(re.findall(r'[0-9]+', x)[-1]) for x in glob.glob(d + '/f*.png'))
s = next((i for i in range(a, b) if i not in have), b)
e = s
while e < b and e not in have: e += 1
print(s, e)" "$1" "$2" "$3"
}

echo "=== the film: $N frames at ${FPS}fps, ${RES}px, $SAMPLES samples ==="
for pass in $(seq 1 80); do
  read gs ge <<<"$(next_gap outputs/film 0 $N)"
  [ "$gs" -ge "$N" ] && { echo "  all $N frames present"; break; }
  echo "  filling frames $gs-$ge"
  (cd source/blender && $PY render_plant.py --fps $FPS --res $RES --samples $SAMPLES \
     --out ../../outputs/film --t0 0 --t1 $($PY -c "import plant; print(plant.FILM_END)") \
     --start "$gs" --end "$ge" 2>&1 | grep -E "s/frame|Error|Traceback" | tail -2)
done

echo "=== the question, composited over Act I ==="
$PY source/render_overlay.py --html source/question.html --frames outputs/film --fps $FPS

echo "=== conform and cut the track under it ==="
bash assemble.sh
