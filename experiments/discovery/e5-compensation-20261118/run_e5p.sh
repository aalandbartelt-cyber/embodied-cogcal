#!/usr/bin/env bash
# E5-prime: two registered arms x 20 paired seeds at delta ~ U(0.5,1.5) mm.
# A: theta=15 deg, q5 bias +15 deg (matched compensation, primary).
# B: theta=0 deg,  q5 bias +15 deg (naive fixed offset, specificity control).
# Arms run in parallel; each arm writes a fresh directory and refuses to overwrite.
set -euo pipefail
cd "$(dirname "$0")"
PY=/home/mary/miniconda3/envs/cogcal-sim/bin/python
for spec in "15 15 e5p-y15-b15" "0 15 e5p-y0-b15"; do
  set -- $spec
  yaw=$1; bias=$2; name=$3
  out="runs/$name"
  if [ -e "$out" ] || [ -e "${out}-physics" ]; then
    echo "refusing to overwrite $out" >&2
    exit 2
  fi
done
"$PY" rollout_e5p.py --yaw-deg 15 --delta-center-mm 1 --q5-bias-deg 15 --tag e5p \
  --seed-start 12850 --seed-count 20 --out runs/e5p-y15-b15 \
  --physics runs/e5p-y15-b15-physics > runs/e5p-y15-b15.log 2>&1 &
pid_a=$!
"$PY" rollout_e5p.py --yaw-deg 0 --delta-center-mm 1 --q5-bias-deg 15 --tag e5p \
  --seed-start 12850 --seed-count 20 --out runs/e5p-y0-b15 \
  --physics runs/e5p-y0-b15-physics > runs/e5p-y0-b15.log 2>&1 &
pid_b=$!
wait "$pid_a"; wait "$pid_b"
tail -1 runs/e5p-y15-b15.log
tail -1 runs/e5p-y0-b15.log
