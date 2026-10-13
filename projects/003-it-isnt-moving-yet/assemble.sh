#!/bin/bash
# One leg: 24fps Blender frames -> 1080x1920 at 30, blended (Cycles was not
# asked for motion blur), grained, with Luifer's "Gracias a Ti" cut in at
# 46.555s — the offset that puts its hard silence exactly on the petal's fall.
set -e
cd "$(dirname "$0")"
if [ -z "$PY" ]; then
  case "$OSTYPE" in
    msys*|cygwin*|win32*) PY=$(command -v python || command -v python3) ;;
    *)                    PY=$(command -v python3 || command -v python) ;;
  esac
fi
FF=$($PY -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
DUR=$($PY -c "import sys; sys.path.insert(0,'source/blender'); import plant; print(plant.FILM_END)")
AUDIO_IN=46.555
"$FF" -y -loglevel error -framerate 24 -start_number 0 -i outputs/film/f%05d.png \
  -ss $AUDIO_IN -i audio/gracias-a-ti-129.mp3 \
  -filter_complex "[0:v]scale=1080:1920:flags=lanczos,framerate=fps=30:interp_start=0:interp_end=255,noise=alls=2:allf=t+u,setsar=1,format=yuv420p[v]" \
  -map "[v]" -map 1:a -t $DUR \
  -c:v libx264 -profile:v high -crf 16 -preset slow \
  -af "loudnorm=I=-14:TP=-1.2:LRA=11" -c:a aac -b:a 192k \
  -movflags +faststart -shortest outputs/it-isnt-moving-yet.mp4
"$FF" -v error -i outputs/it-isnt-moving-yet.mp4 -f null - && echo "  decodes clean"
"$FF" -hide_banner -i outputs/it-isnt-moving-yet.mp4 2>&1 | grep -E "Duration|Stream"
echo "ASSEMBLED"
