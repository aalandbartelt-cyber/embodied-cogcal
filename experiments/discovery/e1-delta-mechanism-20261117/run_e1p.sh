#!/usr/bin/env bash
# E1' pilot driver: ten 3 mm bins, 20 fresh seeds each, sequential (single sim at a time).
set -euo pipefail
cd "$(dirname "$0")"
PY=/home/mary/miniconda3/envs/cogcal-sim/bin/python
mkdir -p runs logs
for b in 0 1 2 3 4 5 6 7 8 9; do
  if [ -e "runs/e1p-b${b}" ] || [ -e "runs/e1p-b${b}-physics" ]; then
    echo "bin ${b} already present, refusing to overwrite" >&2
    exit 2
  fi
  "$PY" rollout_e1p.py --delta-bin "$b" \
    --out "runs/e1p-b${b}" --physics "runs/e1p-b${b}-physics" \
    > "logs/e1p-b${b}.log" 2>"logs/e1p-b${b}.err"
  tail -1 "logs/e1p-b${b}.log"
done
echo "all bins complete"
