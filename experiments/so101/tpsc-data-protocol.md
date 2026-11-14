# TPSC 项目自有 SO-101 数据采集协议

日期：2026-11-14。状态：**协议草案，未执行、未采集、未训练；不是 TPSC 立项依据。**
配套：[共享前缀候选审计](../../docs/prior-art/temporal-prefix-calibration-audit.md)、
[公开载体扫描](smolvla-interface-preflight/public-dataset-scan.md)、
[A100 交接](../../docs/NEXT_A100_TPSC.md)。

## 0. 目的与边界

本协议只解决一件事：为 **shared-prefix / no-common-prefix / multi-valid** 三类任务对
采集可审计的 SO-101 数据，使 Codex 能在 A100 上检验：

> 统一语义分离损失是否真的误伤“两个任务共享的正确动作前缀”，
> 以及 outcome-conditioned support 是否能减少这种误伤。

它不证明 TPSC 有效；不替代查新；不承诺样本量能检出某个成功率差值。
所有 episode 数都是 **pilot 资源上限**，不是功效计算。正式 n 由 pilot 方差和最小重要效应决定。

## 1. 三类任务对

### 1.1 Shared-prefix（共享前缀）

同一物体、同一初始位置、同一抓取/抬升前缀；只在放置目标上分叉。

- 指令 A：“把红色方块放到左边盒子。”
- 指令 B：“把红色方块放到右边盒子。”
- 正确动作前缀：接近 → 抓取 → 抬升（A/B 相同）；分叉点：转向左/右放置。
- 关键检查：两任务在当前 action chunk 内是否真的有相同正确动作；若没有，该 pair 不适用。

### 1.2 No-common-prefix（无共同前缀）

两个目标在相反方向，接近动作从第一帧就不同。

- 指令 A：“把红色方块放到前方盒子。”
- 指令 B：“把红色方块放到后方盒子。”
- 正确动作从接近方向就分叉；用于对照“shared-prefix 的收益不是来自任务难度/语言差异”。

### 1.3 Multi-valid（多正确解）

同一目标允许两条物理上成功的路线/抓取方式（例如绕左/绕右，或两种夹爪朝向）。

- 指令：“把红色方块放到盒子里。”
- 成功集合是多模态的；用于检验“相对单一示范定义偏差/分离”的伪负例。
- 关键检查：两条路线都成功；若只有一条成功，归入 shared-prefix 或 no-common-prefix，不混入 multi-valid。

每个 family 至少 2 个 pair（例如左/右、前/后，或两个不同物体），避免只靠一个 pair 下结论。

## 2. 硬件与软件前置

| 项 | 要求 |
|---|---|
| 机器人 | SO-101 follower；leader 遥操作；6 维 action/state |
| 控制 | 位置控制，30 Hz 记录；动作单位与项目 `so101_new_calib.xml` 对齐 |
| 相机 | 固定 top/front（或 side/wrist）；640×480；30 fps；曝光/白平衡锁定 |
| 场景 | 固定桌面、两个目标盒、可选障碍/挡片；物体尺寸/颜色/摩擦记录 |
| 软件 | LeRobot 固定 commit；数据集 v3.0；记录 `use_degrees`、校准文件 hash |
| 安全 | 低速、限位、急停；shadow mode 通过后再采正式数据 |

### 2.1 校准与单位契约

采数据前必须固定并记录：

```text
robot_type = so101_follower
use_degrees = true（旧版数据集兼容）或按实际 LeRobot 版本记录
homing_offset / range_min / range_max / drive_mode / resolution（逐电机）
gripper = 0..100
control_frequency = 30 Hz
```

- 用 [fport/so101-calibrator](https://github.com/fport/so101-calibrator) 或 LeRobot
  官方校准流程；保存 `calibration.json` 与 SHA256。
- 逐关节检查 action/state 范围：`shoulder_pan`、`shoulder_lift`、`elbow_flex`、
  `wrist_flex`、`wrist_roll`、`gripper`。
- **elbow 限位**：真实 SO-101 数据可出现 100°，项目 XML 的 `elbow_flex` 上界是
  96.83°（±1.69 rad）。采数据前决定：
  - 方案 A：所有示范限制在 XML 限位内（更安全，但与真实可达范围不一致）；
  - 方案 B：做显式 scene override 到 100°（记录来源、碰撞检查、标注“非官方默认”）；
  - 方案 C：采集时允许 100°，训练/评估时裁剪并计数（只作 smoke test）。
  三选一必须写进 `scene_manifest.json`，不能事后混用。
- **wrist_flex**：公开真实 SO-101 对照只到 86.1°，`svla` 的 99.49° 未复现；
  不要因为 `svla` 越界就放宽 wrist 限位。

### 2.2 相机与场景

- 相机位置、角度、焦距、曝光、增益固定；保存 `camera_calibration_id`。
- 每 episode 记录 object/goal/barrier 的位姿；仿真与真机使用同一坐标约定。
- 光照稳定；避免自动曝光在 episode 中途变化。
- 背景/桌面标记固定；不要把任务提示贴在相机视野内。

## 3. 数据字段

### 3.1 LeRobot 主数据集

```text
action                  float32[6]   关节目标（degrees 或按校准记录）
observation.state       float32[6]   关节实际位置
observation.images.top  video        俯视相机
observation.images.front video       前视相机
timestamp               float32      秒
frame_index             int64
episode_index           int64
index                   int64
task_index              int64
```

### 3.2 侧车 `episodes_meta.jsonl`（每 episode 一行）

```json
{
  "episode_id": "shared_left_0007",
  "pair_id": "shared_left_right_01",
  "family": "shared_prefix",
  "branch": "A",
  "task_text": "把红色方块放到左边盒子。",
  "task_index": 0,
  "object_pose": {"x": 0.12, "y": -0.12, "z": 0.036, "yaw": 0.0},
  "goal_pose": {"x": 0.28, "y": 0.0, "z": 0.003},
  "barrier_pose": null,
  "success": true,
  "failure_reason": null,
  "operator": "op01",
  "date": "2026-11-15",
  "calibration_id": "so101-cal-20261115-a",
  "robot_type": "so101_follower",
  "use_degrees": true,
  "elbow_limit_policy": "xml_96_83 | override_100 | clip_and_count",
  "camera_ids": ["top", "front"],
  "video_paths": ["videos/observation.images.top/..."],
  "n_frames": 420,
  "duration_s": 14.0,
  "rejected": false,
  "reject_reason": null
}
```

### 3.3 校准与场景清单

- `calibration.json` + SHA256：逐电机 `homing_offset`、`range_min/max`、`drive_mode`、
  `resolution`、`use_degrees`。
- `scene_manifest.json`：桌面/盒子/障碍尺寸、相机内外参、物体质量/摩擦、光照。
- `split.json`：按 `pair_id` / 初始 placement 划分 train/val/test；不能按帧随机划分。

## 4. 采集流程

1. **预热与校准检查**：连接、读校准、检查关节范围、相机画面、急停。
2. **放置场景**：按预生成 placement 表摆放物体/盒子；记录实际位姿（不要只记名义值）。
3. **开始录制**：30 Hz；先录 0.5 s 静止，再开始动作；episode 结束保留 0.5 s。
4. **遥操作执行**：按 A/B 分支指令操作；除安全停止外不中途干预。
5. **独立判定成功**：物体在目标盒内、稳定、未被人工扶正；记录 `success`/`failure_reason`。
6. **保存与自检**：帧数、时间戳、相机可见性、关节范围、动作-状态形状。
7. **随机化顺序**：A/B 分支、placement、family 交错采集；不要先采完 A 再采 B（避免漂移混杂）。
8. **定期复校**：每 30–50 episode 或每 30 分钟复测零位/限位；记录温度/漂移（若有）。

### 4.1 拒绝准则（保留原始文件，单独标记）

- 指令/分支错误、抓错物体、未抓稳、掉落、人工干预、超出任务定义；
- 相机遮挡/失焦/曝光跳变、时间戳断裂 >1 帧、帧率异常；
- 关节目标越界（超过所选 elbow 策略）、校准漂移、通信丢包；
- episode 长度 >3× 中位数或 <0.3× 中位数；
- 成功标签不确定（物体在盒边、需人扶）。

拒绝率 >20% 时先修载体/流程，不把拒绝样本算进成功率。

## 5. 质量检查

| 检查 | 频率 | 通过标准 |
|---|---|---|
| schema/字段/形状 | 100% | 6 维 action/state；相机键存在；timestamp 单调 |
| 关节范围 | 100% | 在所选 elbow/wrist 策略内；越界计数 |
| 相机可见性 | 100% | 非黑屏、物体/盒子在视野内 |
| 成功标签复核 | 10% 人工 | 与独立谓词一致 |
| pair 平衡 | 每批 | A/B 数量、placement 分布匹配 |
| 拒绝率 | 每批 | <20%；否则先修流程 |
| 数据泄漏 | 划分时 | test 的 pair/placement 不出现在 train |

## 6. 最小 pilot（2 周资源盒）

### 第 1 周：10 episodes/branch

- 3 families × 2 pairs × 2 branches × 10 episodes = **120 episodes**（上限，不是功效承诺）。
- 先做 1 个 family × 1 个 pair × 2 branches × 10 = 20 episodes 的管线试跑；
  通过后再扩到 120。
- 20/120 manifest 已生成：`experiments/so101/tpsc-pilot/manifest-pilot.jsonl` /
  `manifest-full.jsonl`；几何/场景 smoke 已通过，但**没有策略 rollout**。
- 同步做：LeRobot 加载、SmolVLA 前向、action 范围检查、相机可视化。

### 第 2 周：质量复核 + 决策

- 10% 人工复核成功标签；统计拒绝率、pair 平衡、关节越界。
- 冻结 `split.json` 与 `episodes_meta.jsonl`。
- 只决定“是否值得扩到正式采集”，不先训练 TPSC 方法。

### 6.1 Go/No-Go

- **Go**：schema/范围/相机/标签通过；shared-prefix 与 no-common-prefix 在动作上可区分；
  multi-valid 两条路线都成功；拒绝率 <20%。
- **No-Go（修载体）**：校准漂移、相机不稳、动作越界不可解释、成功标签不可靠。
- **No-Go（停 TPSC）**：shared-prefix 上根本不存在共享正确前缀，或统一分离损失
  不产生可重复的前缀损失；此时不要用更多数据“救”方法。

## 7. 训练/评估接口（给 Codex）

- 数据格式：LeRobot v3.0；固定 `dataset_revision`、`robot_type`、`use_degrees`、
  `calibration_id`。
- 基线：frozen/普通 BC、BAS-VLA 风格 uniform separation、action-only phase mask、
  Stage-Aware/progress-conditioned、RT-H（可复现时）。
- 候选：outcome-conditioned support（只有未来任务结果差异支持分叉时才施加 separation）。
- 主终点：新任务成功率、旧任务保持率、shared-prefix 动作误差、分叉后敏感性、
  错误纠偏率、延迟/额外推理。
- 统计单位：episode；按 pair/placement 聚类；报告配对差值与不确定性。
- **不要**把 action distance 变大当成成功；必须与任务结果相关。

## 8. 命令与工具

校准（示例，按实际 LeRobot 版本调整）：

```bash
python -m lerobot.calibrate \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower_so101
```

录制（示例，字段需按实际相机/任务调整）：

```bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower_so101 \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM1 \
  --teleop.id=leader_so101 \
  --dataset.repo_id=<user>/tpsc_so101_pairs \
  --dataset.num_episodes=120 \
  --dataset.single_task="把红色方块放到左边盒子。"
```

pilot 场景/manifest（不需要 A100，也不需要策略）：

```bash
cd /home/mary/research/embodied-cogcal
python3 -m probes.generators.tpsc_pairs --mode pilot --seed 42 \
  --output experiments/so101/tpsc-pilot/manifest-pilot.jsonl
python3 experiments/so101/tpsc-pilot/validate_manifest.py \
  --manifest experiments/so101/tpsc-pilot/manifest-pilot.jsonl --mode pilot

env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONPATH=. \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/tpsc-pilot/smoke_scene.py \
  --manifest experiments/so101/tpsc-pilot/manifest-pilot.jsonl --mode pilot
```

每次采集后：

```bash
# 记录校准/场景/数据 hash；具体脚本在采集前补齐
sha256sum calibration.json scene_manifest.json > hashes.txt
```

## 9. 角色与交接

| 角色 | 职责 |
|---|---|
| 用户 | 遥操作、场景摆放、成功标签、校准/安全 |
| Codex | A100 训练/评估、数据加载、方法实现 |
| Copilot | schema/质量审计、协议维护、公开载体对照 |

交接时必须附：`calibration.json`、`scene_manifest.json`、`episodes_meta.jsonl`、
`split.json`、拒绝样本清单、采集日志、数据 hash。

## 10. 不声称的事

- 不声称 120 episodes 足以证明 TPSC 有效或检出某个成功率差值；
- 不声称真实 SO-101 与 MuJoCo 完全同体（除非校准/运动学证据齐全）；
- 不把公开数据（`ngocthuong2212` / `kristaqp` / `svla`）混入 TPSC 的任务对；
- 不把“共享前缀”写成论文贡献；它只是待检验的失效条件；
- 不在接口/校准未解决时启动 A100 正式矩阵。
