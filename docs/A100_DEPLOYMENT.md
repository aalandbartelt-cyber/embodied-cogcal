# 自强 5000 A100 部署指南

本指南用于 OpenVLA 7B + LIBERO-Spatial 启动冒烟和次级可比基准。研究主线仍是
SO-101 数字孪生与真实 SO-101 上的兼容策略，见 [ROADMAP.md](ROADMAP.md)。LIBERO
的 7 维末端动作不能直接作为 SO-101 的 6 维关节/夹爪命令；本指南不提供该适配。

以下是依据上游源码整理的待执行流程，尚未在自强 A100 节点实测。本地 `cogcal`
环境只做准备和分析，不安装这里的 GPU 推理依赖。

## 0. 平台侧准备

申请 Ubuntu/Linux、1 张 A100 40GB 起步、持久化存储，并使用 `tmux`。需要 NVIDIA
驱动和 CUDA **开发工具链**；本流程选择 CUDA 12.1 toolkit 配合 PyTorch cu121 wheel。
安装前只检查节点分配、驱动、磁盘和工具链，不要求模型依赖已齐全。

```bash
tmux new -s cogcal-a100
nvidia-smi
df -h
nvcc -V
```

`nvidia-smi` 的 CUDA 字段表示驱动能力；PyTorch wheel 提供其 CUDA 运行时，两者都
不代表系统已提供 `nvcc`。源码编译 flash-attn 需要开发工具链；若缺少 `nvcc`，先选择
平台的 CUDA 12.1 devel 镜像或加载相应 module。不要直接跳过工具链检查。

## 1. 首次获取本项目并建立环境

下面各节在同一个 Bash 会话中顺序执行。已有 clone 时先确认工作区干净，再决定本轮
使用的项目 commit；评测批次开始后不再 `git pull` 或升级依赖。

```bash
set -euo pipefail
mkdir -p "$HOME/research"
export COGCAL_REPO="$HOME/research/embodied-cogcal"
git clone https://github.com/aalandbartelt-cyber/embodied-cogcal.git "$COGCAL_REPO"

export COGCAL_STORAGE_ROOT="$HOME/research/cogcal-storage"
export COGCAL_RUN_DIR="$COGCAL_STORAGE_ROOT/runs/a100/$(date -u +%Y%m%dT%H%M%SZ)"
export HF_HOME="$COGCAL_STORAGE_ROOT/huggingface"
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0
export COGCAL_MIN_FREE_GB=30
mkdir -p "$COGCAL_RUN_DIR" "$HF_HOME"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda create -y -n openvla python=3.10.13
conda activate openvla
export PIP_CONSTRAINT="$COGCAL_REPO/constraints/openvla-a100.txt"

python -m pip install "numpy<2"
python -m pip install \
  torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 \
  --index-url https://download.pytorch.org/whl/cu121
```

所有后续 `pip install` 都保留 `PIP_CONSTRAINT`；它保护上游固定的
transformers 4.40.1、tokenizers 0.19.1、timm 0.9.10 等核心版本。`numpy<2` 用于维持
这个旧版 PyTorch 环境的 NumPy ABI 兼容性，参见 [NumPy 官方兼容说明](https://numpy.org/doc/stable/user/troubleshooting-importerror.html#downstream-importerror-attributeerror-or-c-api-abi-incompatibility)。
约束文件不是完整传递依赖锁。遇到解析冲突时保留错误日志并调查，不去掉约束或使用
`--upgrade` 强行升级；本地分析环境的 `requirements-lock.txt` 也不适用于此环境。

安装 flash-attn 前同时验证实际 GPU、NumPy 桥接和编译工具链：

```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path

import numpy as np
import torch
from torch.utils.cpp_extension import CUDA_HOME

print("torch:", torch.__version__, "runtime:", torch.version.cuda)
assert torch.cuda.is_available(), "GPU/CUDA runtime unavailable"
print("device:", torch.cuda.get_device_name(0))
assert "A100" in torch.cuda.get_device_name(0).upper()
assert torch.cuda.get_device_capability(0) == (8, 0)
assert int(np.__version__.split(".")[0]) < 2
print("numpy bridge:", torch.from_numpy(np.zeros(1, dtype=np.float32)))
assert CUDA_HOME, "Load the CUDA 12.1 development toolkit (nvcc) first"
nvcc = Path(CUDA_HOME) / "bin" / "nvcc"
output = subprocess.check_output([str(nvcc), "-V"], text=True)
print(output)
release = re.search(r"release (\d+\.\d+)", output)
assert release, "Cannot identify nvcc version"
assert release.group(1) == torch.version.cuda == "12.1", "This recipe requires toolkit/runtime 12.1"
PY
```

要求 12.1 一致是本部署流程的选择；flash-attn 2.5.5 上游最低 CUDA 要求是 11.6。
其 [构建脚本](https://github.com/Dao-AILab/flash-attention/blob/v2.5.5/setup.py) 也明确提示
开发镜像才提供 `nvcc`。若平台只有其他工具链，先另立配置并验证，不把它记录为本流程通过。

## 2. 安装 OpenVLA 和 LIBERO

本次源码核对固定在下面两个 commit。它们是安装输入快照，不代表已验证可在 A100
完成评测。上游依据：[OpenVLA README](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/README.md)、
[pyproject.toml](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/pyproject.toml)、
[LIBERO 额外依赖](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/experiments/robot/libero/libero_requirements.txt)。
上游明确固定核心模型依赖，并报告在 Python 3.10.13/A100 上的 LIBERO 结果。

```bash
export COGCAL_OPENVLA_COMMIT=c8f03f48af692657d3060c19588038c7220e9af9
export COGCAL_LIBERO_COMMIT=8f1084e3132a39270c3a13ebe37270a43ece2a01

cd "$HOME/research"
git clone https://github.com/openvla/openvla.git
git -C openvla checkout --detach "$COGCAL_OPENVLA_COMMIT"
python -m pip install -e "$HOME/research/openvla"

python -m pip install packaging ninja
ninja --version
MAX_JOBS=4 python -m pip install "flash-attn==2.5.5" --no-build-isolation

git clone https://github.com/Lifelong-Robot-Learning/LIBERO.git
git -C LIBERO checkout --detach "$COGCAL_LIBERO_COMMIT"
python -m pip install -e "$HOME/research/LIBERO"
python -m pip install -r "$HOME/research/openvla/experiments/robot/libero/libero_requirements.txt"
python -m pip check

git -C "$COGCAL_REPO" rev-parse HEAD > "$COGCAL_RUN_DIR/code_commit.txt"
git -C "$HOME/research/openvla" rev-parse HEAD > "$COGCAL_RUN_DIR/openvla_commit.txt"
git -C "$HOME/research/LIBERO" rev-parse HEAD > "$COGCAL_RUN_DIR/libero_commit.txt"
python --version > "$COGCAL_RUN_DIR/python_version.txt"
python -m pip freeze --all > "$COGCAL_RUN_DIR/environment-freeze.txt"
nvcc -V > "$COGCAL_RUN_DIR/nvcc_version.txt"
nvidia-smi > "$COGCAL_RUN_DIR/nvidia-smi.txt"
```

不要建立 LIBERO 自带的 torch 1.11 环境；它作为 OpenVLA 环境中的 editable package
安装。完整 freeze 用于记录本次实际解析的传递依赖（包括上游引入的 Git 依赖 commit）。
复现时连同三个仓库 commit、约束文件和 freeze 一起保存；更新任一项需新建运行记录。
日志和缓存放在仓库外，避免前检被运行产物造成的工作区改动阻断。

## 3. 安装后执行前检

依赖安装完成后、模型下载和正式评测前，执行 [A100_PREFLIGHT.md](A100_PREFLIGHT.md)。
它不替代上面的工具链检查、`pip check`、EGL 渲染和实际模型冒烟。

```bash
set -euo pipefail
cd "$COGCAL_REPO"
python scripts/a100_preflight.py | tee "$COGCAL_RUN_DIR/preflight.txt"
python scripts/a100_preflight.py --json > "$COGCAL_RUN_DIR/preflight.json"
```

`set -euo pipefail` 让 Python 失败能够停止流程，防止 `tee` 的成功退出掩盖错误。
磁盘默认门槛是 30 GiB，只是初始检查下限；完整环境、权重、缓存和视频需要按实际容量
增加空间，并在下载后、正式批次前再次前检。

## 4. 下载并记录模型快照

```bash
python - <<'PY'
import os
from pathlib import Path

from huggingface_hub import snapshot_download

checkpoint = snapshot_download(repo_id="openvla/openvla-7b-finetuned-libero-spatial")
run_dir = Path(os.environ["COGCAL_RUN_DIR"])
(run_dir / "checkpoint_path.txt").write_text(checkpoint + "\n")
print("checkpoint snapshot:", checkpoint)
PY
export COGCAL_CHECKPOINT="$(cat "$COGCAL_RUN_DIR/checkpoint_path.txt")"
```

后续使用这个含 revision 的本地快照路径，避免同一批次重复解析可变的模型仓库分支。
记录 checkpoint 的 Hugging Face commit、归一化统计和模型配置；访问令牌不写入仓库或日志。

## 5. 验证 MuJoCo EGL

```bash
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
renderer.close()
PY
```

若 EGL 失败，检查 GPU 分配、`MUJOCO_EGL_DEVICE_ID` 和平台 EGL 驱动库。OSMesa
可以用于诊断；更改渲染后端后另记配置，不静默混入正式 EGL 结果。

## 6. OpenVLA-Spatial 冒烟

```bash
set -euo pipefail
cd "$HOME/research/openvla"
python "$COGCAL_REPO/scripts/a100_preflight.py" --root "$COGCAL_REPO"

python experiments/robot/libero/run_libero_eval.py \
  --model_family openvla \
  --pretrained_checkpoint "$COGCAL_CHECKPOINT" \
  --task_suite_name libero_spatial \
  --center_crop True \
  --num_trials_per_task 5 \
  --seed 0 \
  --local_log_dir "$COGCAL_RUN_DIR/smoke" \
  2>&1 | tee "$COGCAL_RUN_DIR/smoke_spatial_seed0.log"
```

验收：10 个任务各完成 5 次、进程退出码为 0、无持续 EGL/权重加载错误、至少导出一条
rollout 视频，并填写 [实验日志模板](../experiments/LOG_TEMPLATE.md)。上游默认把视频写到
OpenVLA 的 `rollouts/`，需要另行归档。首次导入 LIBERO 若提示生成路径配置，先确认
其指向当前固定的 LIBERO clone，再继续；这一步成功也不等于 SO-101 适配已完成。

## 7. 次级基线批次

冒烟验收后，OpenVLA-Spatial 次级基线按本项目约定使用 seed 0/1/2、每任务 50 次。
这是 3 × 10 × 50 episodes；不要在环境未通过时扩展到校准或探针矩阵。

```bash
set -euo pipefail
cd "$HOME/research/openvla"
python "$COGCAL_REPO/scripts/a100_preflight.py" --root "$COGCAL_REPO"
python -m pip check
for seed in 0 1 2; do
  python experiments/robot/libero/run_libero_eval.py \
    --model_family openvla \
    --pretrained_checkpoint "$COGCAL_CHECKPOINT" \
    --task_suite_name libero_spatial \
    --center_crop True \
    --num_trials_per_task 50 \
    --seed "$seed" \
    --local_log_dir "$COGCAL_RUN_DIR/baseline" \
    2>&1 | tee "$COGCAL_RUN_DIR/spatial_seed${seed}.log"
done
```

保留每任务结果、失败类型、seed、center crop、checkpoint revision、归一化统计、三个
源码 commit、环境 freeze、渲染配置和视频索引。原始权重、缓存、完整视频不推送到
公开 GitHub；选定小型日志和汇总后再同步。本轮结束后如需 `git pull --ff-only`，下一
批次重新记录 commit 并执行前检。

## 8. 常见问题

- `flash-attn` 编译失败：核对 `CUDA_HOME/bin/nvcc -V`、PyTorch CUDA runtime、
  `ninja` 和 `packaging`；控制 `MAX_JOBS`，保留完整编译日志。
- 显存不足：确认没有残留进程。改变量化、精度或其他推理配置后另记实验配置。
- 成功率异常低：先检查 `center_crop=True`、模型快照、`unnorm_key`、任务套件和
  `num_steps_wait`，再判断模型或探针问题。
- 依赖冲突：保留 `PIP_CONSTRAINT`；修订部署配置并复查上游要求，不临时升级核心依赖。
