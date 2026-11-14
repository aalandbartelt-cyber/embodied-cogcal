# A100 上的 TPSC 载体预检

日期：2026-11-14。本文只建立可运行的 SO-101 SmolVLA 基线，不代表 TPSC 已立项或查新通过。
第一阶段的目标是确认“策略能在同体数据协议上运行”，第二阶段才检验 shared-prefix 失效。

## 已核验的公开载体

- 模型：[`lerobot/smolvla_base`](https://huggingface.co/lerobot/smolvla_base)，Hub revision
  `5e8d12a6e2975b0e5e5fce7c8caf47c371d257b6`，模型卡 Apache-2.0；HTTP 元数据记录在
  [`mechanism-first-sources-20261114.json`](prior-art/mechanism-first-sources-20261114.json)。
- 参考数据：[`lerobot/svla_so101_pickplace`](https://huggingface.co/datasets/lerobot/svla_so101_pickplace)，
  revision `f641879e22172be7e8161d5e6c1503c2d2feb657`，数据卡 Apache-2.0。
- 官方文档说明 SmolVLA 输入包含多相机、机器人状态和自然语言，输出 action chunk；其示例以
  20,000 steps 作为起点，并给出单 A100 的约 4 小时量级估计。实际时间以本次 A100 日志为准，
  不预填成功率或训练时长。

## 第一阶段：只跑普通基线

在 A100 节点建立独立 LeRobot 环境，固定 LeRobot commit、模型 revision、数据 revision 和本仓库
commit。不要把 `simulation/so101/scene.py` 的 6 个弧度关节目标直接当作 LeRobot 的归一化 action；
先从数据中的 `state/action` 元数据核对单位、顺序、相机字段和 gripper 处理。

示例命令（需根据实际数据字段检查 `rename_map`，不要盲目复制）：

```bash
set -euo pipefail
export DATASET_REPO_ID=lerobot/svla_so101_pickplace
export LOCAL_DATASET_ROOT="$PWD/data/svla_so101_pickplace"
export OUT="$PWD/outputs/train/smolvla-so101-baseline"
export LOG="$PWD/outputs/logs/smolvla-so101-baseline.log"
mkdir -p "$(dirname "$LOG")"
test ! -e "$OUT" && test ! -e "$LOG"

lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --dataset.repo_id="$DATASET_REPO_ID" \
  --dataset.root="$LOCAL_DATASET_ROOT" \
  --output_dir="$OUT" \
  --job_name=smolvla-so101-baseline \
  --batch_size=64 \
  --steps=20000 \
  --save_checkpoint=true \
  --save_freq=20000 \
  --wandb.enable=false \
  2>&1 | tee -a "$LOG"
```

若数据是 `observation.images.up/side` 或其他字段，先用 LeRobot 的 dataset metadata 读取工具确认
字段，再显式添加 `--rename_map` 和缺失相机处理。训练前保存：

```bash
python - <<'PY'
import json, os
from pathlib import Path
for p in [Path(os.environ['LOCAL_DATASET_ROOT'])/'meta/info.json',
          Path(os.environ['LOCAL_DATASET_ROOT'])/'meta/stats.json']:
    print(p, p.exists(), p.stat().st_size if p.exists() else 0)
PY
nvidia-smi
```

训练结束后只检查 checkpoint 完整性、loss 曲线、显存、吞吐和归一化配置；loss 下降不等于物理
成功。先在离线样本上确认 action chunk 的维度/单位，再接入 MuJoCo 或真机。

## 第二阶段：冻结失效检验，不先改方法

用同一 SmolVLA 载体建立三个成对任务族：

1. shared-prefix：同一物体抓取后分别放到左右目标；
2. no-common-prefix：从起始状态就需要不同接近方向；
3. multi-valid：同一目标存在两条物理上都成功的路线。

每条 episode 记录 `pair_id`、语言任务、action chunk、状态时间戳、独立物体结果、候选最早分叉时刻
和失败原因。第一轮只比较普通 BC/SmolVLA 与现成强基线；不把人工 phase mask 当方法结果。

只有在 shared-prefix 上出现可重复的“统一语义分离导致前缀动作或结果恶化”，并且能排除相机、
归一化、chunk 长度、语言理解和低层执行问题，才进入 outcome-conditioned support estimator。
若没有失效或人工 mask 已完全吸收收益，停止 TPSC 方法主张。

## 第三阶段：仿真—真机同命题

仿真和真机必须共享同一任务对、同一语言、同一 6 通道接口、同一分叉字段和同一物体终点谓词。
真机只在仿真完成载体和基线验收后进入；不能用教师轨迹或单段成功视频代替 VLA 结果。

相关依据：

- [LeRobot SmolVLA 官方文档](https://huggingface.co/docs/lerobot/v0.4.3/en/smolvla)
- [SmolVLA 公开 SO-101 训练示例](https://github.com/ArmDeveloperEcosystem/arm-learning-paths/blob/main/content/learning-paths/laptops-and-desktops/finetune-smolvla-lerobot/6-finetune-smolvla.md)
- [共享前缀候选审计](prior-art/temporal-prefix-calibration-audit.md)

