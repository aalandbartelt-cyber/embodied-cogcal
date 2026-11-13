# A100 部署前置检查

正式安装和模型下载前，在 A100 节点的 `openvla` 环境中运行：

```bash
cd ~/research/embodied-cogcal
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0
export HF_HOME=$HOME/.cache/huggingface
export COGCAL_STORAGE_ROOT=$HOME/research
export COGCAL_MIN_FREE_GB=30

python scripts/a100_preflight.py
```

检查器不安装包、不联网、不修改文件。它会检查：

- Python 3.10；
- PyTorch、torchvision、transformers、tokenizers、timm、flash-attn 固定版本；
- CUDA 可用、GPU 名称包含 A100、Compute Capability 为 `(8, 0)`；
- `MUJOCO_GL=egl` 和 `MUJOCO_EGL_DEVICE_ID`；
- Hugging Face 缓存与实验存储路径；
- Git commit 和工作区是否干净；
- 存储盘剩余空间。

机器可读输出：

```bash
python scripts/a100_preflight.py --json > ~/research/a100-preflight.json
```

任何 `FAIL` 都先解决再运行模型。尤其不要在 GPU 不是 A100、工作区有未记录修改、
或 EGL 未配置时开始正式评测。
