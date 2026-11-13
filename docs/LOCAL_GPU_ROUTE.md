# 本机 RTX 5070 Ti 路线与 A100 路线

## 当前机器实测

2026-11-13 在 WSL 中检测到：

```text
GPU: RTX 5070 Ti Laptop GPU
显存: 12227 MiB（按这个数规划，不按宣传的 16GB 规划）
驱动: 617.42
Compute Capability: 12.0（Blackwell）
```

## 结论

### 本机可以做

- ECCBF 指标、校准器、JSONL 分析和图表；
- MuJoCo/SO-101 数字孪生的轻量仿真；
- SmolVLA/LeRobot 级别的小模型推理和 Pilot；
- 小规模任务、少量 episode、动作校准器和数据管线调试；
- SO-101 真机的本地控制端和相机采集端。

### 本机不作为主线做

- OpenVLA 7B 官方 PyTorch 2.2/固定依赖环境；
- OpenVLA 7B 的正式全矩阵复现实验；
- OpenVLA 7B LoRA 训练；
- 依赖 Flash-Attention 2.5.5 的完整训练链路。

OpenVLA 官方仓库固定在 PyTorch 2.2.*、transformers 4.40.1、timm 0.9.10 和
flash-attn 2.5.5；其 LoRA 说明还指出较小 GPU 需要约 27GB 显存才能按示例运行。这个
环境与本机 Blackwell/12GB 余量不匹配，不能把本机结果与 A100 官方基线混写。

## 推荐的本机实验环境

不要污染已有的 `cogcal` 分析环境，单独创建 `cogcal-sim`：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda create -y -n cogcal-sim python=3.12
conda activate cogcal-sim

# 本机驱动已高于 LeRobot 文档要求的 Linux NVIDIA 驱动下限。
conda install -y -c conda-forge ffmpeg

mkdir -p ~/research
cd ~/research
git clone https://github.com/huggingface/lerobot.git
cd lerobot

# 本机 SO-101/SmolVLA 开发与推理依赖
python -m pip install -U pip
python -m pip install -e ".[core_scripts,smolvla,feetech]"

python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    print("capability:", torch.cuda.get_device_capability(0))
PY
```

如果 PyTorch 默认 CUDA wheel 与本机出现兼容问题，先不要改动 `cogcal`；按 LeRobot
官方安装页选择匹配的 CUDA wheel，再重新安装 LeRobot。

## 本机与 A100 的分工

| 工作 | 本机 5070 Ti | A100 |
|---|---:|---:|
| ECCBF 代码和统计 | 主力 | 可选 |
| SO-101 小模型 Pilot | 主力 | 可选 |
| OpenVLA 7B 官方 LIBERO 基线 | 不建议 | 主力 |
| 大规模正式矩阵 | 不建议 | 主力 |
| 视频剪辑和结果整理 | 主力 | 可选 |
| SO-101 真机控制端 | 主力 | 远程推理可选 |

## 对论文口径的影响

- 如果完全不用 A100：论文主模型应改为 SO-101 兼容的 SmolVLA/LeRobot 策略，不能继续
  把 OpenVLA 7B 官方 LIBERO 数字当作主结果。
- 如果保留 A100：本机做 ECCBF/SmolVLA Pilot，A100 做 OpenVLA/OpenVLA-OFT 或正式大矩阵，
  论文可以同时报告同体 SO-101 结果和 LIBERO 可比结果。
- 本机 4-bit/8-bit OpenVLA 试验只能标记为“非官方量化 Pilot”，不能与 bf16 官方基线直接
  合并统计。
