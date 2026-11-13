# 自强 5000 A100 部署指南

本指南用于 OpenVLA 7B + LIBERO-Spatial 主线。模型推理和正式评测放在 A100；本地
`cogcal` 环境不安装 torch、transformers 或模型权重。

OpenVLA 官方评测说明使用 Python 3.10.13、PyTorch 2.2.0、transformers 4.40.1 和
flash-attn 2.5.5，并在 A100 上报告结果；本项目按这个版本契约执行。

## 0. 平台侧准备

在自强平台申请：

- Ubuntu 22.04 或平台提供的 CUDA 镜像；
- 1 张 A100 40GB 起步，正式矩阵可使用双卡并行；
- 持久化磁盘，至少预留模型、环境、日志和视频空间；
- 进入节点后使用 `tmux`，避免 SSH 断开导致作业停止。

```bash
tmux new -s cogcal-a100
```

## 1. 建立环境

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda create -y -n openvla python=3.10
conda activate openvla

python -m pip install -U pip
python -m pip install \
  torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 \
  --index-url https://download.pytorch.org/whl/cu121

python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda:", torch.cuda.is_available())
print("cuda runtime:", torch.version.cuda)
print("device:", torch.cuda.get_device_name(0))
assert torch.cuda.is_available()
assert torch.cuda.get_device_capability(0) == (8, 0)
PY
```

## 2. 安装 OpenVLA 和 LIBERO

```bash
mkdir -p ~/research
cd ~/research

git clone https://github.com/openvla/openvla.git
cd openvla
python -m pip install -e .

python -m pip install packaging ninja
ninja --version
python -m pip install "flash-attn==2.5.5" --no-build-isolation

cd ~/research
git clone https://github.com/Lifelong-Robot-Learning/LIBERO.git
cd LIBERO
python -m pip install -e .

cd ~/research/openvla
python -m pip install -r experiments/robot/libero/libero_requirements.txt
```

不要在这里建立 LIBERO 自带的 torch 1.11 环境；LIBERO 作为 OpenVLA 环境中的 editable
package 安装。

## 3. 下载模型和设置缓存

```bash
export HF_HOME=$HOME/.cache/huggingface
export TRANSFORMERS_CACHE=$HF_HOME/transformers
mkdir -p "$HF_HOME" "$TRANSFORMERS_CACHE"

python - <<'PY'
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="openvla/openvla-7b-finetuned-libero-spatial",
    cache_dir=None,
)
print("checkpoint cached")
PY
```

网络不稳定时，先在平台允许的范围内配置镜像；不要把访问令牌写进仓库或实验日志。

## 4. 验证 MuJoCo EGL

```bash
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0

python - <<'PY'
import mujoco

xml = """
<mujoco>
  <option integrator="implicitfast"/>
  <worldbody><body name="box" pos="0 0 0"><geom type="box" size=".05 .05 .05"/></body></worldbody>
</mujoco>
"""
model = mujoco.MjModel.from_xml_string(xml)
data = mujoco.MjData(model)
renderer = mujoco.Renderer(model, height=128, width=128)
mujoco.mj_forward(model, data)
renderer.update_scene(data)
frame = renderer.render()
print("rendered:", frame.shape, frame.dtype)
PY
```

如果 EGL 失败，先检查节点是否分配了 GPU 和 `MUJOCO_EGL_DEVICE_ID`；不要立即改换
模型环境。必要时把 `MUJOCO_GL=osmesa` 作为诊断回退，但正式视频优先使用 EGL。

## 5. OpenVLA-Spatial 冒烟

```bash
cd ~/research/openvla
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0

mkdir -p ~/research/embodied-cogcal/experiments/runs/a100
git -C ~/research/embodied-cogcal rev-parse HEAD | tee \
  ~/research/embodied-cogcal/experiments/runs/a100/code_commit.txt

python experiments/robot/libero/run_libero_eval.py \
  --model_family openvla \
  --pretrained_checkpoint openvla/openvla-7b-finetuned-libero-spatial \
  --task_suite_name libero_spatial \
  --center_crop True \
  --num_trials_per_task 5 \
  --seed 0 \
  2>&1 | tee ~/research/embodied-cogcal/experiments/runs/a100/smoke_spatial_seed0.log
```

验收：10 个任务各 5 次完成、无持续 EGL/权重加载错误、至少导出一条 rollout 视频，
并填写 `experiments/LOG_TEMPLATE.md`。

## 6. 正式基线

正式 OpenVLA-Spatial 基线按 3 个随机种子、每任务 50 次运行：

```bash
cd ~/research/openvla
for seed in 0 1 2; do
  python experiments/robot/libero/run_libero_eval.py \
    --model_family openvla \
    --pretrained_checkpoint openvla/openvla-7b-finetuned-libero-spatial \
    --task_suite_name libero_spatial \
    --center_crop True \
    --num_trials_per_task 50 \
    --seed "$seed" \
    2>&1 | tee "$HOME/research/embodied-cogcal/experiments/runs/a100/spatial_seed${seed}.log"
done
```

OpenVLA 官方脚本默认是 10 个任务 × 50 episodes；正式论文结果需要记录 seed、
center crop、checkpoint、归一化统计和运行 commit，不能只保存最终成功率。

## 7. 与本项目同步

```bash
cd ~/research/embodied-cogcal
git pull --ff-only origin main
git rev-parse HEAD
git status --short
```

A100 上只提交小型日志、配置和汇总索引；模型权重、原始数据、完整视频和缓存不要推送到
公开 GitHub。正式探针和 ECCBF 运行器完成后，再以同样的 `MUJOCO_GL=egl`、seed 和日志
字段运行 Pilot。

## 8. 常见问题

- `flash-attn` 编译失败：确认 A100 环境、`ninja` 和 `packaging` 已安装；不要把失败的
  CUDA 编译产物复制到本机 Blackwell 环境。
- 显存不足：确认没有残留进程，使用 `nvidia-smi`；不要随意改 batch 或模型精度后把结果
  与官方 bf16 结果混合。
- 成功率异常低：先检查 `center_crop=True`、checkpoint、`unnorm_key`、任务套件和
  `num_steps_wait`，再判断模型或探针问题。
- EGL 失败：先检查 `MUJOCO_GL`、GPU ID 和节点分配；记录失败，不静默切换渲染后端。
