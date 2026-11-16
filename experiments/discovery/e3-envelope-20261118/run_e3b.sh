#!/usr/bin/env bash
# E3b: 12 new cells (yaw x delta {4,6,10} mm) x 20 paired seeds, 12-way parallel.
# Delta in {2,8} is reused from E3; this script never touches runs/e3-*.
set -euo pipefail
cd "$(dirname "$0")"
PY=/home/mary/miniconda3/envs/cogcal-sim/bin/python
mkdir -p runs
for yaw in 0 5 10 15; do
  for d in 4 6 10; do
    out="runs/e3b-y${yaw}-d${d}"
    if [ -e "$out" ]; then
      echo "refusing to overwrite $out" >&2
      exit 2
    fi
  done
done
for yaw in 0 5 10 15; do
  for d in 4 6 10; do
    out="runs/e3b-y${yaw}-d${d}"
    OMP_NUM_THREADS=2 "$PY" rollout_e3b.py --yaw-deg "$yaw" --delta-mm "$d" --tag e3b \
      --out "$out" --physics "runs/e3b-y${yaw}-d${d}-physics" > "runs/e3b-y${yaw}-d${d}.log" 2>&1 &
  done
done
wait
for yaw in 0 5 10 15; do
  for d in 4 6 10; do
    echo "e3b-y${yaw}-d${d}: $(tail -1 "runs/e3b-y${yaw}-d${d}.log")"
  done
done
