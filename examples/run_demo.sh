#!/usr/bin/env bash
# Offline end-to-end demo: synthetic frames -> vertical reel MP4.
# No network, no other earthwatch repos needed.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== survey-animate offline demo =="
survey-animate check
echo
survey-animate demo --out examples/demo-reel.mp4 --preset preview
echo
ls -la examples/demo-reel.mp4 examples/demo-reel.mp4.provenance.json
echo "done."
