#!/usr/bin/env bash
# End-to-end check of the pipeline on synthetic assets (no OpenArt credits used):
#   synth -> cue -> render -> verify
# Small frame size and short piece so it runs in well under a minute.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=pipeline/test-assets
DROP=21.5

python3 pipeline/synth.py --out "$OUT" --size 540x960 --drop $DROP --length 30

echo; echo "== cue candidates (the drop must be #1 at ${DROP}s) =="
python3 pipeline/cue.py "$OUT/song.wav" --fps 30 --top 3
python3 pipeline/cue.py "$OUT/song.wav" --fps 30 --snap $DROP

echo; echo "== render =="
python3 pipeline/render.py \
  --image "$OUT/stone.png" --mask "$OUT/mask.png" \
  --audio "$OUT/song.wav" --cue $DROP \
  --preset pipeline/presets/default.json \
  --size 540x960 --duration 8 --reveal-at 5 \
  --x264-preset veryfast --crf 20 \
  --out "$OUT/out/test.mp4"

echo; echo "== verify =="
python3 pipeline/verify.py "$OUT/out/test.mp4" --mask "$OUT/mask.png"
