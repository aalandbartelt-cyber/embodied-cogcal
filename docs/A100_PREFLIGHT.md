# A100 评测前检查

按 [部署指南](A100_DEPLOYMENT.md) 完成环境安装后，在 A100 节点的 `openvla` 环境中
执行检查，再下载模型和开始评测。它不是安装前要求所有包就绪的检查。下载模型后、
正式批次前再次运行，以确认剩余空间和运行配置。本地开发机无需获得 A100 PASS。

```bash
set -euo pipefail
cd "$HOME/research/embodied-cogcal"
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0
export COGCAL_STORAGE_ROOT="$HOME/research/cogcal-storage"
export HF_HOME="$COGCAL_STORAGE_ROOT/huggingface"
export COGCAL_MIN_FREE_GB=30
mkdir -p "$COGCAL_STORAGE_ROOT" "$HF_HOME"

python scripts/a100_preflight.py
```

检查器不安装包、不联网、不修改文件。它会检查：

- Python 3.10；
- PyTorch 2.2.0、torchvision 0.17.0、transformers 4.40.1、tokenizers 0.19.1、
  timm 0.9.10、flash-attn 2.5.5；`2.2.0+cu121` 等本地构建后缀符合对应公开版本约束；
- CUDA 可用、首个可见 GPU 名称包含 A100、Compute Capability 为 `(8, 0)`；
- `MUJOCO_GL=egl` 和非负整数 `MUJOCO_EGL_DEVICE_ID`；
- Hugging Face 缓存与实验存储变量是否配置；
- 本项目 Git commit 和工作区是否干净；
- 存储盘剩余空间，阈值必须为有限正数，`NaN`/无限值/非法文本会报告 `FAIL`。

机器可读输出和日志放到仓库外，避免运行产物造成工作区变脏：

```bash
set -euo pipefail
python scripts/a100_preflight.py --json > "$COGCAL_STORAGE_ROOT/a100-preflight.json"
python scripts/a100_preflight.py | tee "$COGCAL_STORAGE_ROOT/a100-preflight.txt"
```

任一检查失败时脚本返回 1，通过时返回 0；`pipefail` 保留管道失败，避免 `tee` 掩盖
Python 错误。先解决 `FAIL` 再评测。工作区改动需要审查并记录为明确 commit；不要为了
通过检查删除有效修改。30 GiB 是默认检查下限，需按权重、缓存和视频规模调整。

PASS 只表示这些静态契约通过：它不会验证实际 EGL 渲染、LIBERO 导入、flash-attn
内核运行、上游仓库 commit、NumPy ABI、所有传递依赖或模型效果。继续执行部署指南中的
`nvcc`/NumPy 桥接检查、`pip check`、上游 commit 与环境记录、EGL 和真实模型冒烟。
PyTorch 的 cu121 wheel 不包含 `nvcc` 开发工具链；应在安装 flash-attn 前完成该项检查。
本指南尚未提供 A100 实测通过记录。
