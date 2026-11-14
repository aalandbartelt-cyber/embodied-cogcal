#!/usr/bin/env bash
# Ordinary SmolVLA carrier training, not TPSC semantic calibration.
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_PYTHON="${TPSC_POLICY_PYTHON:-/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python}"
TASK_OUTPUT="${TPSC_TRAIN_OUTPUT:-$TASK_ROOT/checkpoints/tpsc-carrier-20k}"
TASK_STEPS="${TPSC_TRAIN_STEPS:-20000}"
TASK_BATCH="${TPSC_TRAIN_BATCH:-4}"
cd "$TASK_ROOT"
test ! -e "$TASK_OUTPUT"
test -s checkpoints/smolvla_base/model.safetensors
test -s data/tpsc-carrier/meta/info.json
export PYTHONNOUSERSITE=1
unset PYTHONPATH
export HF_HUB_DISABLE_XET=1
export WANDB_MODE=disabled
export ACCELERATE_MIXED_PRECISION=bf16
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
printf '%s\n' \
 'dataset=ngocthuong2212/so101_mujoco_follower_7_31' \
 'dataset_revision=de301f7afe016cef14ac46a238714f52e15bf932' \
 'dataset_robot_type=so_follower' \
 'adapter=simulation_all_6_degrees_to_radians_UNVERIFIED_SOURCE' \
 'clip_events=not_applicable_no_simulation_execution' \
 'claim=carrier_training_not_tpsc_result'
exec "$TASK_PYTHON" -u -m lerobot.scripts.lerobot_train \
 --policy.path="$TASK_ROOT/checkpoints/smolvla_base" \
 --policy.load_vlm_weights=false \
 --policy.device=cuda --policy.push_to_hub=false --policy.use_amp=true \
 --policy.empty_cameras=1 \
 --rename_map='{"observation.images.top":"observation.images.camera1","observation.images.front":"observation.images.camera2"}' \
 --dataset.repo_id=ngocthuong2212/so101_mujoco_follower_7_31 \
 --dataset.revision=de301f7afe016cef14ac46a238714f52e15bf932 \
 --dataset.root="$TASK_ROOT/data/tpsc-carrier" --dataset.video_backend=pyav \
 --output_dir="$TASK_OUTPUT" --job_name=tpsc-carrier-local \
 --seed=42 --num_workers=0 --batch_size="$TASK_BATCH" --steps="$TASK_STEPS" \
 --save_checkpoint=true --save_freq=1000 --log_freq=20 --eval_freq=0 \
 --wandb.enable=false
