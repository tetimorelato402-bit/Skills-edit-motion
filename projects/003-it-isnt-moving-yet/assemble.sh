#!/bin/bash
# ============================================================================
#  Conform the three legs and cut the track under them.
#
#  Legs are conformed SEPARATELY and concatenated, never filtered together:
#  setsar=1 on all three or concat refuses them (a scaled leg reports 1600:1599
#  and an unscaled one 0:1). The Blender legs use framerate= (which blends)
#  rather than fps= (which duplicates and judders on a moving camera), because
#  Cycles was not asked for motion blur. Grain goes on every leg at the same
#  strength — a clean 3D leg butting a grained 2D one is a visible change of
#  stock at exactly the joins the film exists to hide.
#
#  The audio is Luifer's "Gracias a Ti" from 46.555s, which is the track's bar
#  25. That offset is not a taste decision: it is what puts the track's hard
#  silence (its beats 138-144) exactly on the petal's fall. See audio/README.md.
# ============================================================================
set -e
cd /home/user/Skills-edit-motion/projects/003-it-isnt-moving-yet
S=/tmp/_asm; mkdir -p $S
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
BLEND="framerate=fps=30:interp_start=0:interp_end=255"
GRAIN="noise=alls=2:allf=t+u"
A_T=$(python3 -c "print(44*60/129)")
C_T=$(python3 -c "print(16*60/129)")
AUDIO_IN=46.555
DUR=$(python3 -c "print(108*60/129)")

$FF -y -loglevel error -framerate 24 -start_number 0 -i outputs/plant_hi/f%05d.png \
  -vf "scale=1080:1920:flags=lanczos,$BLEND,$GRAIN,setsar=1,format=yuv420p" \
  -t $A_T -c:v libx264 -profile:v high -crf 16 -preset slow $S/a.mp4

$FF -y -loglevel error -framerate 120 -i source/frames120/f%05d.png \
  -filter_complex "[0:v]tmix=frames=3:weights='1 2 1',fps=30,$GRAIN,setsar=1,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -profile:v high -crf 16 -preset slow $S/b.mp4

$FF -y -loglevel error -framerate 24 -start_number 1027 -i outputs/plant_hi/f%05d.png \
  -vf "scale=1080:1920:flags=lanczos,$BLEND,$GRAIN,setsar=1,format=yuv420p" \
  -t $C_T -c:v libx264 -profile:v high -crf 16 -preset slow $S/c.mp4

printf "file '%s'\nfile '%s'\nfile '%s'\n" $S/a.mp4 $S/b.mp4 $S/c.mp4 > $S/list.txt
$FF -y -loglevel error -f concat -safe 0 -i $S/list.txt -c copy $S/silent.mp4

# The track, cut to the film, and normalised for Reels (~-14 LUFS, peak under
# -1dB or the AAC encode clips the kicks).
$FF -y -loglevel error -i $S/silent.mp4 -ss $AUDIO_IN -i audio/gracias-a-ti-129.mp3 \
  -map 0:v -map 1:a -t $DUR -c:v copy \
  -af "loudnorm=I=-14:TP=-1.2:LRA=11" -c:a aac -b:a 192k \
  -movflags +faststart -shortest outputs/it-isnt-moving-yet.mp4

$FF -hide_banner -i outputs/it-isnt-moving-yet.mp4 2>&1 | grep -E "Duration|Stream"
echo "ASSEMBLED"
