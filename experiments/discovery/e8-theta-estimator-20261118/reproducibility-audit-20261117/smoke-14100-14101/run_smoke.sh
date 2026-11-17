#!/usr/bin/env bash
set -u
set -o noclobber
cd /home/mary/research/embodied-cogcal || exit 1
base=experiments/discovery/e8-theta-estimator-20261118/reproducibility-audit-20261117/smoke-14100-14101
python=/home/mary/miniconda3/envs/cogcal-sim/bin/python
runner=experiments/discovery/e8-theta-estimator-20261118/rollout_e8.py
for entry in zero:0 half:-7.5; do
  arm=${entry%%:*}
  dose=${entry#*:}
  if MUJOCO_GL=egl timeout 180 "$python" "$runner" --tag smoke --yaw-deg -15 --bias-mode fixed --bias-deg "$dose" --seed-start 14100 --seed-count 2 --out "$base/runs/$arm" --physics "$base/physics/$arm" > "$base/$arm.stdout.txt" 2> "$base/$arm.stderr.txt"; then
    printf '%s\n' 0 > "$base/$arm.exit"
  else
    status=$?
    printf '%s\n' "$status" > "$base/$arm.exit"
    exit "$status"
  fi
done
