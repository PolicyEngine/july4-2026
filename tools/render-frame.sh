#!/bin/sh
n=$(printf "%04d" "$1")
D="$(cd "$(dirname "$0")/.." && pwd)"
[ -s "$D/tools/frames/f$n.png" ] && exit 0
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --force-device-scale-factor=2 --window-size=1200,675 --virtual-time-budget=600 \
  --screenshot="$D/tools/frames/f$n.png" \
  "file://$D/index.html?record=1&frame=$1" >/dev/null 2>&1
