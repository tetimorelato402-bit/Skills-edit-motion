#!/usr/bin/env bash
# Install everything the Stone Memory pipeline needs: ffmpeg + numpy + pillow.
# Safe to re-run. Works on Debian/Ubuntu (apt), macOS (brew), and any box that
# already has ffmpeg on PATH.
set -euo pipefail

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    (sudo -n true 2>/dev/null && SUDO=sudo) || SUDO=
    $SUDO apt-get update -q
    $SUDO apt-get install -y -q ffmpeg
  elif command -v brew >/dev/null 2>&1; then
    brew install ffmpeg
  else
    echo "ffmpeg not found and no apt-get/brew available: install ffmpeg manually, then re-run." >&2
    exit 1
  fi
fi

python3 -m pip install -q -r "$(dirname "$0")/requirements.txt"

echo "ffmpeg: $(ffmpeg -version | head -1)"
python3 -c "import numpy, PIL; print('numpy', numpy.__version__, '| pillow', PIL.__version__)"
echo "pipeline ready. Try: bash pipeline/test.sh"
