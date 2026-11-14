# 公开 SO-101 / SmolVLA 数据集扫描与载体决策

日期：2026-11-14。状态：**资产扫描与接口决策，不是策略结果，也不是 TPSC 立项依据。**
目的：解决 Codex 接口预检留下的 P1——“公开数据能否作为 SO-101 同体载体？”
结论是：**`svla_so101_pickplace` 不能；有两个更好的公开载体，但仍不能替代 TPSC 的任务对。**

## 1. 检索口径

- Hugging Face API：`/api/datasets?search=so101`、`so-101`、`smolvla`、
  `so101_follower`、`so101 pickplace`、`lerobot so101`。
- 逐个读取 `meta/info.json`、`meta/tasks.jsonl`、`meta/stats.json`（若存在）、
  README、许可证和 revision SHA。
- 动作范围用实际 parquet 计算，不只看 `stats.json`（部分 v2.1 数据集没有 stats）。
- 这是资产筛选，不是查新；不把“没搜到”当作不存在。

## 2. 候选对比

| 数据集 | revision | robot_type | 真实/仿真 | episodes | frames | 相机 | 单位 | 许可 | 判断 |
|---|---|---|---:|---:|---|---|---|---|---|
| `svla_so101_pickplace` | `f641879e...` | `so100_follower` | 真实（元数据） | 50 | 11,939 | up/side | degrees | Apache-2.0 | **SO-100 负对照**，非 SO-101 同体 |
| `kristaqp/so101-pick-place` | `994aa6d4...` | `so101_follower` | 真实 | 50 | 17,505 | side/wrist | degrees | Apache-2.0 | **真实 SO-101 参考候选**；无校准文件 |
| `ngocthuong2212/so101_mujoco_follower_7_31` | `de301f7a...` | `so_follower`（标签 `so101`/`mujoco`） | MuJoCo | 200 | 60,245 | top/front | degrees | Apache-2.0 | **仿真同模型载体首选**；单任务 |
| `jonhpark/so101_pick_place` | `5dbbd166...` | `so101` | 真实（元数据） | 50 | 29,792 | top/front | 待核 | Apache-2.0 | 备选真实载体；关节名有 `main_` 前缀 |
| `ankithreddy/so101_pickplace_uno` | `f47dcf21...` | `so101_follower` | 真实（元数据） | 50 | 43,311 | wrist/top | 待核 | Apache-2.0 | 备选真实载体；相机键名特殊 |
| `TekbotRobotics/svla_so101_pickplace_flags_sorting` | main | `so101_follower` | 真实（元数据） | 8 | 8,972 | laptop | 待核 | 无 | 太小、无许可证，不能作主载体 |

## 3. 关键发现

### 3.1 `kristaqp/so101-pick-place`：真实 SO-101 的 elbow 也到 100°

50 集全量 action 范围（度）：

```text
shoulder_pan  -32.67 .. 33.78
shoulder_lift -100.00 .. 17.94
elbow_flex     16.10 .. 100.00
wrist_flex    -18.88 .. 86.10
wrist_roll    -65.03 .. -34.43
gripper         0.00 .. 44.37
```

与项目 SO-101 XML 对比：

- `elbow_flex` 上界 **+3.17°**（100.0° vs 96.83°）；
- `wrist_flex` 最大 86.1°，**没有**复现 `svla` 的 99.49° 越界；
- 其余关节在 XML 范围内。

这说明 `svla` 的 elbow 越界不是 SO-100 独有：**官方 XML 的 ±96.83° 是保守限位**，
真实 SO-101 可以到 100°。`wrist` 的 4.49° 越界仍只在 `svla` 中出现，暂不能外推。

证据：[`real-so101-reference.json`](real-so101-reference.json)；
复现：[`audit_real_so101_range.py`](audit_real_so101_range.py)。

### 3.2 `ngocthuong2212/...mujoco...`：与项目 XML 逐关节吻合

该数据集标签含 `mujoco`、`so101`、`degree`、`real-leader`、`5x9-real-rule`、
`green-object`、`clean-camera`、`top-camera`、`front-camera`；200 episodes、60,245 帧、
30 Hz、top/front 双相机、Apache-2.0。`meta/matrix_random_placements.jsonl` 还记录了
每个 episode 的物体/容器位置，可用于 placement-conditioned 分析。

action/state 的关节顺序与项目一致，action 范围：

```text
shoulder_pan  -110.0 .. 102.8
shoulder_lift -100.0 .. 64.3
elbow_flex     -70.9 .. 96.83
wrist_flex     -39.5 .. 95.0
wrist_roll    -157.2 .. 162.8
gripper        -10.0 .. 64.5
```

`elbow_flex` 上界正好 96.83°、`wrist_flex` 正好 95.0°、`wrist_roll` 正好
-157.2..162.8°，与 `so101_new_calib.xml` 的 actuator 范围一致。它是**仿真数据**，
不能替代真实 SO-101；但适合做 MuJoCo loader、单位/字段、SmolVLA 训练链路的 smoke test。

### 3.3 `svla_so101_pickplace`：保留为负对照

`robot_type=so100_follower`，无校准文件；elbow 100° 与真实 SO-101 一致，但
`wrist` 99.49° 未在真实对照中复现。它不能作为 SO-101 同体载体，但可以作为
“SO-100/不同校准数据”的负对照，检验接口审计是否能识别错误载体。

## 4. 决策

1. **仿真载体**：优先用 `ngocthuong2212/so101_mujoco_follower_7_31` 做
   SO-101 MuJoCo 的 loader/字段/单位/SmolVLA 训练链路 smoke test。
   它只有单任务（green object → container），不是 TPSC 的 shared-prefix 任务对。
2. **真实载体**：用 `kristaqp/so101-pick-place` 做真实 SO-101 的单位/范围参考，
   但先确认其零位/量程；无校准文件前，不声称与本项目 SO-101 完全同体。
3. **负对照**：`svla_so101_pickplace` 保留为 SO-100/异构载体，专门测试接口审计
   能否拒绝错误数据。
4. **TPSC 任务对**：公开数据里没有现成的 shared-prefix/no-common-prefix/multi-valid
   三族任务对；仍需要项目自有 SO-101 采集，或在 MuJoCo 中生成受控任务对。
5. **XML elbow 限位**：真实 SO-101 可到 100°，官方 XML 的 ±96.83° 偏保守。
   不要直接改 `third_party` 的官方 XML；若要支持 100°，应做**显式的场景 override**
   （记录来源、碰撞检查、标注“非官方默认”），或在 carrier smoke test 中裁剪并计数。
   wrist 的 4.49° 越界仍未解决，不能一起放宽。

## 5. 复现

```bash
cd /home/mary/research/embodied-cogcal
# 真实 SO-101 参考范围（会下载 50 个小 parquet，不含视频）
/home/mary/miniconda3/envs/cogcal/bin/python \
  experiments/so101/smolvla-interface-preflight/audit_real_so101_range.py

# 原 svla/SO-100 接口审计
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/smolvla-interface-preflight/audit_interface.py
```

## 6. 未决问题

- `kristaqp` 和 `jonhpark`/`ankithreddy` 是否共享同一校准零位？没有校准文件无法确认。
- `ngocthuong2212` 的 MuJoCo 模型是否与项目 `so101_new_calib.xml` 逐 link 一致？
  动作范围吻合是强证据，但不是运动学/动力学等价证明。
- 真实 SO-101 的 wrist_flex 机械上限是否真的到 99.5°？当前真实对照只到 86.1°，
  需要更多真实数据或官方机械图。
- 公开数据均缺少 shared-prefix 任务对；TPSC 的任务对仍需自有采集或 MuJoCo 生成。
