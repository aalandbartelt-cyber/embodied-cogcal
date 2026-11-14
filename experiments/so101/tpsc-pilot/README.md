# TPSC pilot 场景与 manifest

日期：2026-11-14。状态：**场景/几何/评估器 smoke test，不是策略结果，也不是 TPSC 有效证据。**

配套协议：[`../tpsc-data-protocol.md`](../tpsc-data-protocol.md)。

## 文件

| 文件 | 作用 |
|---|---|
| `manifest-pilot.jsonl` | 20 条：1 个 shared-prefix pair × 2 branches × 10 episodes |
| `manifest-full.jsonl` | 120 条：3 families × 2 pairs × 2 branches × 10 episodes |
| `validate_manifest.py` | 纯 Python 校验数量、配对、几何、桌面边界 |
| `smoke_scene.py` | 用 MuJoCo 逐条 reset，检查物体/目标/barrier，并验证成功判定翻转 |
| `check_reachability.py` | 随机采样 20k 关节配置，检查目标物体/目标点的夹爪可达距离 |
| `scripted_prefix.py` | 数值 IK 生成 waypoint，比较 shared-prefix/no-common/multi-valid 的 prefix/route |
| `scene-smoke.json` | 最近一次 scene smoke 结果（`ok=true`）；不是策略结果 |
| `reachability.json` | 240 个目标/目标点的最小夹爪距离；`unreachable=0`（5 cm 阈值） |
| `scripted-prefix-report.json` | 物理模式 pilot：0/20；prefix target/executed diff = 0 |
| `scripted-prefix-kinematic.json` | kinematic pilot：place 20/20，final 17/20；prefix diff = 0 |
| `scripted-prefix-full-kinematic.json` | full 120：place 120/120，final 56/120；shared prefix 0，no-common >1.2 rad，multi route >1.15 rad |
| `scripted-traces/` | 前 4 条 pilot 的控制轨迹（可选） |
| `tpsc_*.png` | 三族各分支的 front camera 渲染；qpos=0 静态场景 |

场景：`simulation/so101/tpsc_scene.xml`；接口：`simulation/so101/tpsc_scene.py`；
生成器：`probes/generators/tpsc_pairs.py`；测试：`tests/test_tpsc_scene.py`。

## 三族任务

- **shared_prefix**：红方块同一初始位置；左/右目标不同；抓取/抬升前缀相同。
- **no_common_prefix**：红/蓝目标物体位置不同；从第一帧起接近动作就不同。
- **multi_valid**：红方块同一目标；中间 barrier；左/右两条路线都可成功。

## 复现

```bash
cd /home/mary/research/embodied-cogcal

# 生成 pilot / full manifest
python3 -m probes.generators.tpsc_pairs --mode pilot --seed 42 \
  --output experiments/so101/tpsc-pilot/manifest-pilot.jsonl
python3 -m probes.generators.tpsc_pairs --mode full --seed 42 \
  --output experiments/so101/tpsc-pilot/manifest-full.jsonl

# 几何/配对校验（无需 MuJoCo）
python3 experiments/so101/tpsc-pilot/validate_manifest.py \
  --manifest experiments/so101/tpsc-pilot/manifest-pilot.jsonl --mode pilot
python3 experiments/so101/tpsc-pilot/validate_manifest.py \
  --manifest experiments/so101/tpsc-pilot/manifest-full.jsonl --mode full

# MuJoCo 场景 smoke（无需策略）
env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONPATH=. \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/tpsc-pilot/smoke_scene.py \
  --manifest experiments/so101/tpsc-pilot/manifest-full.jsonl --mode full

# 可选：渲染每族每分支一张图（需要 EGL/OSMesa）
MUJOCO_GL=egl env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONPATH=. \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/tpsc-pilot/smoke_scene.py \
  --manifest experiments/so101/tpsc-pilot/manifest-full.jsonl --mode full --render

# 可达性 proxy（20k 关节采样，5 cm 阈值）
env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONPATH=. \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/tpsc-pilot/check_reachability.py \
  --manifest experiments/so101/tpsc-pilot/manifest-full.jsonl --samples 20000

# 数值 IK waypoint / prefix 检查（kinematic-carry 不是物理抓取）
env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONPATH=. \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/tpsc-pilot/scripted_prefix.py \
  --manifest experiments/so101/tpsc-pilot/manifest-full.jsonl --mode full \
  --kinematic-carry --out experiments/so101/tpsc-pilot/scripted-prefix-full-kinematic.json
```

## 当前验证了什么

- MuJoCo 4.0.1 能加载 TPSC 场景（SO-101 XML + 双物体 + 可移动 goal/barrier）。
- 20/120 条 manifest 的配对与桌面几何通过校验。
- 每条 episode reset 后，目标物体不在 goal；把目标物体放到 goal 中心后，评估器翻为 true。
- barrier 在 shared/no-common 中被移到 z=-0.5；在 multi-valid 中按 manifest 放置。
- 20k 关节采样下，240 个目标物体/goal 点均在夹爪 5 cm 内；最差约 3.5 cm（`reachability.json`）。
- Scripted IK full 120：shared-prefix 的 target/executed prefix diff = **0.0**；
  no-common 从 `above_object` 起 diff > **1.2 rad**；multi-valid prefix diff = 0、route diff > **1.15 rad**。
- Kinematic-carry full 120：`place_success=120/120`；释放/后退后 final success 56/120。
  物理模式 pilot 0/20，说明当前脚本的抓取姿态尚未解决；这不影响 prefix 结构检查。
- IK 最大误差 8.6 mm；720 个 waypoint 中 18 个未达到 4 mm 容差，已逐条记录。

## 没验证什么

- 没有 VLA/SmolVLA/BC 策略；scripted IK 只验证任务路径/前缀，不是策略行为。
- kinematic-carry 不是物理抓取；final 56/120 是释放/接触结果，不是抓取 benchmark。
- 可达性只是 5 cm 夹爪距离 proxy；IK 最大误差 8.6 mm，未证明抓取/放置或碰撞安全。
- **没有测到 learned policy 的 shared prefix**；TPSC 的科学问题仍需 VLA rollout。
- 没有证明 TPSC 的失效机制；`scene-smoke.json` 不是科学结果。
- qpos=0 渲染只用于检查场景布局，不代表机器人可达姿态。
