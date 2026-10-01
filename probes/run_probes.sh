#!/usr/bin/env bash
# Paid probes before the dry run (facilitators only). About 6.80 $ in total.
#   1. One fictional presenter start frame (0.14 $)
#   2. Three 15 s H3 takes in German with real banking vocabulary (3 x 1.95 $)
#   3. One Veo Fast 4 s and one Seedance 4 s at 480p, to confirm the OpenRouter payloads (~0.81 $)
# Then: VG_USER=probes python3 .claude/skills/video-gen/scripts/vg.py wait
# and check the German with: python3 probes/check_de.py
set -euo pipefail
cd "$(dirname "$0")/.."
export VG_USER=probes CLAUDE_PROJECT_DIR="$PWD"
VG=".claude/skills/video-gen/scripts/vg.py"

python3 "$VG" image --prompt-file templates/A_teaser/prompts/frame_presenter_A.md --out probes/presenter_probe.png

for n in 1 2 3; do
  python3 "$VG" submit h3 --prompt-file "probes/de_$n.md" --dur 15 --first-frame probes/presenter_probe.png \
    --label "de_$n" --yes
done

python3 "$VG" submit veo-fast --prompt-file templates/A_teaser/prompts/s1.md --dur 4 --resolution 720p --seed 11 \
  --label veo_payload --yes
python3 "$VG" submit seedance --prompt-file templates/A_teaser/prompts/s2.md --dur 4 --resolution 480p \
  --label seedance_payload --yes

echo "submitted. Now: VG_USER=probes python3 $VG wait"
