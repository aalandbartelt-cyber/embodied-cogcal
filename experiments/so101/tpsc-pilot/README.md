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

## 最新learned pilot结果（2026-11-14）

本地RTX5070Ti完成固定20k普通carrier训练，并执行原20条manifest：**任务成功0/20、抬升0/20、放置0/20**。
全部20条/10对/600个chunk与实测q已核验，未扩展120条。当前是**载体未就绪**，
不能从动作差异推出正确共享前缀或uniform separation伤害；后者没有测试，TPSC方法未实现。
完整选题目标尚未完成。

结果入口：[一页go/no-go](runs/local-5070ti/go-no-go.md)、
[全部10对距离与分叉表](runs/local-5070ti/pilot-20k-prefix-report.md)、
[原始episode](runs/local-5070ti/pilot-20k/episodes.jsonl)、
[完成证据hash](runs/local-5070ti/completed-evidence-inventory.json)。
下文scripted结果与“未执行”段落保留历史，不代表当前状态。

## 三族任务

- **shared_prefix**：红方块同一初始位置；左/右目标不同；抓取/抬升前缀相同。
- **no_common_prefix**：红/蓝目标物体位置不同；原脚本从第一帧起接近动作不同。
  这不是所有成功策略无共同前缀的证明；仍可能共同等待/开爪，见[支持集合更正](../../../docs/prior-art/tpsc-support-identifiability-correction.md)。
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

## 原scripted资产验证了什么

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

## 原scripted资产没有验证什么

- 没有 VLA/SmolVLA/BC 策略；scripted IK 只验证任务路径/前缀，不是策略行为。
- kinematic-carry 不是物理抓取；final 56/120 是释放/接触结果，不是抓取 benchmark。
- 可达性只是 5 cm 夹爪距离 proxy；IK 最大误差 8.6 mm，未证明抓取/放置或碰撞安全。
- **没有测到 learned policy 的 shared prefix**；TPSC 的科学问题仍需 VLA rollout。
- 没有证明 TPSC 的失效机制；`scene-smoke.json` 不是科学结果。
- qpos=0 渲染只用于检查场景布局，不代表机器人可达姿态。

## 恢复后的审阅与 learned pilot（历史启动记录）

先保存的原资产提交为 `af47281`，审阅限制见 [REVIEW.md](REVIEW.md)。
原 `scripted-prefix-*.json` 不覆盖；其 pair 表存在“最后重复覆盖”的限制。
新 `analysis/tpsc_prefix.py` 按 case/repeat 身份保留全部配对，拒绝重复/缺分支/种子不匹配，
且在任务能力或独立分叉时刻缺失时返回不可判定。原始 degree-assumption 的 SHA256 保持不变。

用户已选择本地 RTX 5070 Ti 进行选题实验。载体小型元数据/模型/视频已固定 revision 下载，
见 [carrier-assets.json](carrier-assets.json)；下载不等于策略运行。
`policy_worker.py` 和 `learned_rollout.py` 是待运行的真实 SmolVLA / MuJoCo 双环境入口，
每次要求新输出目录，完整保存 episode 和 chunk，不执行 kinematic carry。
下一步依实际 CUDA loader/forward/backward 结果更新训练与 20 条 rollout 状态。

本次实际运行更新：`runs/local-5070ti/carrier-cuda-smoke.json` 证明指定数据可解码，
SmolVLA strict load、CUDA前向/反向、有限[1,50,6] chunk通过。
`worker-contract.json` 证明跨Python环境真实模型IPC通过（黑图fixture，非episode）。
20-step资源试跑完成；20k固定终点训练已启动，持续日志为`runs/local-5070ti/training-20k.live.log`
（大模型/数据/实时日志留本地；提交startup快照与hash）。
当前裁决见 [`go-no-go.md`](runs/local-5070ti/go-no-go.md)。20条物理pilot尚未执行。

后续科学比较须先读[损失忠实性更正](../../../docs/prior-art/tpsc-loss-fidelity-correction.md)：
逐步records与展平chunk的margin并不相同，旧toy不支持一般的BAS前缀伤害断言。
只有能力和正确共享前缀成立，才比较明确布局、完整preset、归一化和匹配预算的分离干预。

复核已完成的正式输出（不会改写原JSONL；`--out`必须不存在）：

```bash
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/miniconda3/envs/cogcal/bin/python \
  experiments/so101/tpsc-pilot/audit_learned_run.py \
  --run experiments/so101/tpsc-pilot/runs/local-5070ti/pilot-20k \
  --manifest experiments/so101/tpsc-pilot/manifest-pilot.jsonl \
  --out /tmp/tpsc-completed-run-audit-fresh.json
```

进一步匹配物理任务的普通BC检查已在独立目录完成：teacher32/32，固定小BC测试0/20；
同权重验证集执行长度诊断6步0/8、30步4/8。
它们未使用或替换本pilot manifest，不提供TPSC/shared-prefix或补偿方法结论。
当前接续见[匹配能力记录](../../discovery/matched-bc-lowrate-20261114/README.md)与
[机制边界](../../../docs/prior-art/history-compensation-mechanism-screen.md)。

后续独立普通GRU/视觉特征能力对照已完成60条：carry11/20、reset4/20、
初始视觉特征15/20，均未达事前16/20；按计划停止继续微调该小模型，不进入TPSC/补偿干预。
本pilot原始文件未改，最新接续见handoff §14。
