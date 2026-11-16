#!/usr/bin/env bash
# E3: 12 cells (yaw x exact lateral offset) x 20 paired seeds, 6-way... 12-way parallel.
set -euo pipefail
cd "$(dirname "$0")"
PY=/home/mary/miniconda3/envs/cogcal-sim/bin/python
mkdir -p runs
for yaw in 0 5 10 15; do
  for d in 2 8 14; do
    out="runs/e3-y${yaw}-d${d}"
    if [ -e "$out" ]; then
      echo "refusing to overwrite $out" >&2
      exit 2
    fi
  done
done
for yaw in 0 5 10 15; do
  for d in 2 8 14; do
    out="runs/e3-y${yaw}-d${d}"
    OMP_NUM_THREADS=2 "$PY" rollout_e3.py --yaw-deg "$yaw" --delta-mm "$d" --tag e3 \
      --out "$out" --physics "runs/e3-y${yaw}-d${d}-physics" > "$out.log" 2>&1 &
  done
done
wait
for yaw in 0 5 10 15; do
  for d in 2 8 14; do
    tail -1 "runs/e3-y${yaw}-d${d}.log"
  done
done
