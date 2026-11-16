#!/usr/bin/env bash
# E2 yaw sweep: five yaw conditions x 20 paired seeds at delta ~ U(0.5,1.5) mm.
set -euo pipefail
cd "$(dirname "$0")"
PY=/home/mary/miniconda3/envs/cogcal-sim/bin/python
for yaw in 0 2 5 10 15; do
  out="runs/e2-y${yaw}-d1"
  if [ -e "$out" ]; then
    echo "refusing to overwrite $out" >&2
    exit 2
  fi
  "$PY" rollout_e2.py --yaw-deg "$yaw" --delta-center-mm 1 --tag e2 \
    --seed-count 20 --out "$out" --physics "runs/e2-y${yaw}-d1-physics" 2>&1 | tail -1
done
