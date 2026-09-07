#!/bin/bash
# Anvil: screens -> slideshow. Both steps are cheap (seconds, not hours).
set -e
cd "$(dirname "$0")"
python3 source/shoot.py --out outputs/screens
python3 source/slideshow.py --out outputs/anvil-slideshow.mp4
