# TPSC 载体预检（当前先用本地 5070 Ti）

日期：2026-11-14。用户最新决定选题阶段先用本地 RTX 5070 Ti；A100 路径保留用于后续规模实验。本文只建立可运行的 SO-101 SmolVLA 基线，不代表 TPSC 已立项或查新通过。
第一阶段的目标是确认“策略能在同体数据协议上运行”，第二阶段才检验 shared-prefix 失效。

**当前结果：本地固定20k普通训练和原20条learned pilot均已完成，任务成功0/20。**
训练中断后从最新完整18k状态续跑到20k，未挑best checkpoint；采样器恢复限制有记录。
见[go/no-go](../experiments/so101/tpsc-pilot/runs/local-5070ti/go-no-go.md)。
当前判定载体未就绪；正确共享前缀不可识别，uniform separation未测试。
**先解决匹配任务数据/相机/关节约定及可执行teacher，不因本次失败直接迁移A100重跑或实现TPSC。**
下文安装/训练指令保留为可复用入口，不能当作正在运行或需立即重启的任务。

科学门槛更新：[固定源码损失审计](prior-art/tpsc-loss-fidelity-correction.md)已收回旧toy的一般性解释。
后续比较必须写明per_step或flattened_chunk、完整目标preset与normalization；
正margin惩罚不是已经测得的前缀伤害。现有本地普通载体训练不因这个更正而改名成TPSC方法实验。

## 已核验的公开载体

- 模型：[`lerobot/smolvla_base`](https://huggingface.co/lerobot/smolvla_base)，Hub revision
  `5e8d12a6e2975b0e5e5fce7c8caf47c371d257b6`，模型卡 Apache-2.0；HTTP 元数据记录在
  [`mechanism-first-sources-20261114.json`](prior-art/mechanism-first-sources-20261114.json)。
- 参考数据：[`lerobot/svla_so101_pickplace`](https://huggingface.co/datasets/lerobot/svla_so101_pickplace)，
  revision `f641879e22172be7e8161d5e6c1503c2d2feb657`，数据卡 Apache-2.0。
  注意：该 revision 的 `meta/info.json` 将 `robot_type` 标为 `so100_follower`；名称和字段兼容不等于
  与本项目 SO-101 网格/校准完全相同。它只作 SO-100/异构负对照。
- **仿真同模型载体（优先）**：[`ngocthuong2212/so101_mujoco_follower_7_31`](https://huggingface.co/datasets/ngocthuong2212/so101_mujoco_follower_7_31)，
  revision `de301f7afe016cef14ac46a238714f52e15bf932`，200 episodes / 60,245 帧 / 30 Hz，
  MuJoCo，标签含 `so101`、`degree`，top/front 双相机，Apache-2.0；action 范围与
  `so101_new_calib.xml` 逐关节吻合。适合 loader/字段/单位/SmolVLA 训练链路 smoke test；
  只有单任务，不是 TPSC 的 shared-prefix 任务对。
- **真实 SO-101 参考**：[`kristaqp/so101-pick-place`](https://huggingface.co/datasets/kristaqp/so101-pick-place)，
  revision `994aa6d4f68e33ac93c410085eca4beb9cc14aea`，50 episodes / 17,505 帧，
  `so101_follower`，side/wrist 双相机，Apache-2.0；50 集 action 的 elbow 最大 100.0°，
  说明 XML 的 96.83° 是保守限位，不是 SO-100 独有。无校准文件，不能声称完全同体。
- 官方文档说明 SmolVLA 输入包含多相机、机器人状态和自然语言，输出 action chunk；其示例以
  20,000 steps 作为起点，并给出单 A100 的约 4 小时量级估计。实际时间以本次 A100 日志为准，
  不预填成功率或训练时长。

## 第一阶段：只跑普通基线

在 A100 节点建立独立 LeRobot 环境，固定 LeRobot commit、模型 revision、数据 revision 和本仓库
commit。不要把 `simulation/so101/scene.py` 的 6 个弧度关节目标直接当作 LeRobot 的归一化 action；
先从数据中的 `state/action` 元数据核对单位、顺序、相机字段和 gripper 处理。

本地接口预检已确认：该数据集创建于 2025-05-23（早于 LeRobot v0.3.2），旧版 LeRobot 用
degrees（[-180,180]）+ gripper 0–100；转换到当前 MuJoCo 场景后，`elbow_flex` 上界超出
**+3.17°**、`wrist_flex` 超出 **+4.49°**。这不是单位误读，而是真实范围差异；且
`meta/info.json` 的 `robot_type=so100_follower`，不能声称 SO-101 同体。详见
[`range-mismatch-analysis.md`](../experiments/so101/smolvla-interface-preflight/range-mismatch-analysis.md)。

决策：优先用 `ngocthuong2212` 做仿真 smoke test（范围吻合，无需 elbow 裁剪）；
`kristaqp` 做真实 SO-101 单位/范围参考；`svla` 只作 SO-100 负对照。公开数据只作
**carrier smoke test**，显式做角度→弧度/gripper 适配并报告 clip（`kristaqp` 的 elbow
裁剪也要计数）。TPSC 的同体实验必须使用本项目 SO-101 自有数据（记录校准文件/revision、
`use_degrees`、关节限位），或使用明确声明 `robot_type=so101_follower` 且带校准元数据的
公开数据。未满足前，A100 只验证 LeRobot/SmolVLA 训练链路，不用公开数据跑 TPSC 失效实验，
也不把结果解释为 SO-101 同体性能。

> 命名提醒：下面的 `smolvla-so101-baseline` 只是原交接单的名字；按本次审计，建议改为
> `smolvla-so100-carrier-smoke`，并在日志中记录 `dataset_robot_type=so100_follower`、
> `adapter=degrees_to_radians+gripper_0_100`、`clip_events=<count>`、
> `claim=carrier_smoke_test_not_so101_same_body`。

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


## Codex 恢复后的本地执行入口

原资产已 review/提交为 `af47281`，保全和问题说明见
[`tpsc-pilot/REVIEW.md`](../experiments/so101/tpsc-pilot/REVIEW.md)。
本轮指定 carrier 固定为 `ngocthuong2212/so101_mujoco_follower_7_31` 的
`de301f7afe016cef14ac46a238714f52e15bf932`；旧 `svla` 只保留异构负对照。

- 数据/模型已下载到忽略目录 `data/tpsc-carrier` / `checkpoints/smolvla_base`，
  22 个文件的 SHA256 与 revision 见 `experiments/so101/tpsc-pilot/carrier-assets.json`。
- LeRobot 固定 tag v0.4.3 的 commit `0b067df57d21d3a02d6c511f1609172fa39ac29b`。
- 先运行 `scripts/tpsc_carrier_smoke.py --output <新的结果路径>`，验收真实视频解码、CUDA 前向/反向与 action chunk。
- 普通训练入口 `scripts/tpsc_train_local.sh`，默认 batch=4、seed=42、固定终点 20,000 steps；
  载体训练不等于 TPSC 任务对训练。尚未验证的运行项以实时日志为准。
- `learned_rollout.py` / `policy_worker.py` 用双进程保持原 MuJoCo 4.0.1；
  输入边界仅 RGB、六关节、指令与注册随机种子，物体/目标真值仅在 evaluator 中。
- 该 carrier 的 gripper 数据含 -10，旧 handoff 中 `gripper_0_100` 不适用；
  全六通道 degree 转 rad 当前仍标注为模拟载体假设。未核实 source/camera 对应前，不能提升为已验证同体适配。
- 当前只有程序与资产检查；20 条 learned-policy、物理任务能力和 uniform separation 对比尚未完成，
  不可预填 shared-prefix/伤害结论。

本地实际检查已完成：carrier视频解码、strict权重加载、CUDA有限前反向、[1,50,6] chunk与跨进程加载均通过。
20-step资源试跑完成，固定20k训练运行中。结果和限制见
[本轮go/no-go](../experiments/so101/tpsc-pilot/runs/local-5070ti/go-no-go.md)。
20条物理pilot、语言配对结果、uniform separation干预均未完成，不能由这些工程检查推出。
