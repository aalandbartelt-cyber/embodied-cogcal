#!/usr/bin/env bash
# E4: four appearance/contact conditions x 20 paired seeds at delta ~ U(0.5,1.5) mm.
set -euo pipefail
cd "$(dirname "$0")"
PY=/home/mary/miniconda3/envs/cogcal-sim/bin/python
for cond in deg0 visual collision both; do
  out="runs/e4-${cond}"
  if [ -e "$out" ]; then
    echo "refusing to overwrite $out" >&2
    exit 2
  fi
  "$PY" rollout_e4.py --condition "$cond" --tag e4 \
    --out "$out" --physics "runs/e4-${cond}-physics" 2>&1 | tail -1
done
