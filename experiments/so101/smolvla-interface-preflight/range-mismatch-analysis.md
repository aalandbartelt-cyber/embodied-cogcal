# SmolVLA/SO-101 接口预检：elbow/wrist 越界分析

日期：2026-11-14。状态：**接口审计结论，不是策略结果，也不是 TPSC 立项依据。**
本文接手 Codex 中断的 `smolvla-interface-preflight`，补上数据集时代单位证据、
越界量核算和“能否声称同体”的决策。原 `summary.json` 保留为
[`summary-degree-assumption.json`](summary-degree-assumption.json)，未覆盖。

## 1. 结论

1. **数据集时代单位是“角度”，不是 `RANGE_M100_100` 归一化。**
   `lerobot/svla_so101_pickplace` 创建于 2025-05-23；当时 LeRobot 的
   `lerobot/common/robot_devices/robots/manipulator.py:294-297` 明确写：
   “Rotations are expressed in degrees in nominal range of [-180, 180]，
   and linear motions (like gripper of Aloha) in nominal range of [0, 100]。”
   `feetech_calibration.py:490` 也写“Joints with rotational motions are expressed
   in degrees in nominal range of [-180, 180]”。
   `use_degrees=False` 是 2025-08-01 的 v0.3.2 才引入的 SO100 默认值；
   当前 `so_follower` 默认 `use_degrees=True`，注释明确说是为了兼容旧策略/数据集。
   因此原预检的“角度→弧度”假设对该数据集是成立的。

2. **elbow/wrist 越界是真实现象，不是单位错误。**
   转成弧度后：

   | 关节 | 公开数据范围（度） | 场景 actuator 范围（rad） | 场景上界（度） | 越界 |
   |---|---|---:|---:|---:|
   | `shoulder_pan` | -93.46 .. 88.01 | -1.91986 .. 1.91986 | ±110.00 | 无 |
   | `shoulder_lift` | -100.00 .. 8.13 | -1.74533 .. 1.74533 | ±100.00 | 无（下界正好贴边） |
   | `elbow_flex` | 12.97 .. **100.00** | -1.69 .. 1.69 | ±96.83 | **+3.17°** |
   | `wrist_flex` | 33.53 .. **99.49** | -1.65806 .. 1.65806 | ±95.01 | **+4.49°** |
   | `wrist_roll` | -92.77 .. -20.00 | -2.74385 .. 2.84121 | -157.2 .. +162.8 | 无 |
   | `gripper` | 0 .. 33.00 | -0.17453 .. 1.74533 | — | 无（0–100 百分比映射后） |

   精确数值在 `summary.json` 的 `range_overflow` 字段：
   `elbow_flex.high_rad=0.05532925199432959`（3.1701°），
   `wrist_flex.high_rad=0.07836830184101218`（4.4902°）。

### 1.1 真实 SO-101 对照（2026-11-14 新增）

为了避免把“SO-100 元数据”误当成 elbow 越界的唯一解释，我用一个明确
`robot_type=so101_follower` 的公开真实数据集做了同样核算：

| 项 | `kristaqp/so101-pick-place` |
|---|---|
| revision | `994aa6d4f68e33ac93c410085eca4beb9cc14aea` |
| 机器人 | `so101_follower` |
| 规模 | 50 episodes / 17,505 frames / 30 Hz |
| 任务 | “Pick the red object and place it in the box” |
| 相机 | `observation.images.side`、`observation.images.wrist.left` |
| 许可 | Apache-2.0 |
| 单位 | 旧版 LeRobot degrees（创建于 2025-06-14，早于 v0.3.2） |

50 集全量 action 范围（度）：

```text
shoulder_pan  -32.67 .. 33.78
shoulder_lift -100.00 .. 17.94
elbow_flex     16.10 .. 100.00
wrist_flex    -18.88 .. 86.10
wrist_roll    -65.03 .. -34.43
gripper         0.00 .. 44.37
```

与项目 SO-101 XML 对比：**elbow_flex 同样在 100.0° 触顶，越界 +3.17°**；
`wrist_flex` 最大 86.1°，没有复现 `svla` 的 99.49° 越界。

这意味着：

- **elbow 的 +3.17° 越界不是 SO-100 独有的证据**；真实 `so101_follower`
  也能到 100°，官方 XML 的 ±96.83° 更像是保守限位。把 XML 限位直接当成
  “真实 SO-101 不可达 100°”是不成立的。
- `wrist_flex` 的 +4.49° 仍然只在 `svla_so101_pickplace` 中出现，当前真实
  SO-101 对照没有复现；它更可能是该数据集的任务/校准差异，暂不能外推。
- 证据文件：[`real-so101-reference.json`](real-so101-reference.json)；
  复现脚本：[`audit_real_so101_range.py`](audit_real_so101_range.py)。

3. **不能声称这份 `svla` 数据是“同体 SO-101”。**
   数据集 `meta/info.json` 的 `robot_type` 是 **`so100_follower`**，不是
   `so101_follower`；数据集名称里的“so101”不能替代机械本体、校准和关节限位证据。
   §1.1 的真实 `so101_follower` 对照说明 elbow 100° 并非 SO-100 独有，因此不能把
   elbow 越界单独当作 SO-100 证据；但 `svla` 的 `robot_type` 和缺失校准文件仍不足以
   支持同体声明。wrist 99.49° 仍未在真实 SO-101 对照中复现。
   数据集不包含校准文件，因此无法把它的角度值精确映射到本项目 SO-101 的零位/量程。

4. **决策：**
   - **允许**：`svla_so101_pickplace` 作为 carrier smoke test，显式做角度→弧度、
     gripper 0–100→场景 hinge 的适配；任何裁剪/越界事件必须计数并报告；
     结果只能称“公开 SO-100 载体预检”，不能称 SO-101 同体。
   - **不允许**：用这份 `svla` 数据直接训练/评估 TPSC 的 SO-101 同体基线，或把
     A100/VLA 失败归因于 TPSC。接口未解决前，A100 结果没有可解释性。
   - **更好的公开载体**：
     - 仿真同模型：`ngocthuong2212/so101_mujoco_follower_7_31`（200 episodes、
       60,245 frames、30 Hz，MuJoCo，`so101`/`degree` 标签，action 范围与 XML
       逐关节吻合，top/front 相机，Apache-2.0）；适合做 SO-101 MuJoCo 的
       loader/SmolVLA 训练链路 smoke test，但只有单任务，不是 TPSC 的任务对。
     - 真实 SO-101：`kristaqp/so101-pick-place`（50 episodes、17,505 frames、
       `so101_follower`、side/wrist 相机、Apache-2.0）；适合做真实 SO-101
       参考/单位对照，但无校准文件，需先核对零位/量程。
   - **TPSC 前置**：采集本项目 SO-101 自有的 50+ 变体示范，记录校准文件/revision、
     `use_degrees`、关节限位和相机字段；或找到明确声明 `robot_type=so101_follower`
     且带校准元数据的公开数据。公开数据里目前没有现成的 shared-prefix 任务对。

## 2. 证据链

| 证据 | 来源 | 说明 |
|---|---|---|
| 数据集创建时间 | Hugging Face API `createdAt=2025-05-23T12:31:31Z` | 早于 LeRobot v0.3.2（2025-08-01） |
| 数据集 `robot_type` | `dataset-info.json` | `so100_follower`，不是 SO-101 |
| 旧版单位说明 | LeRobot commit `6163daaaa4fa193d0e37468a94d90e07ef3c95ce`，`manipulator.py:294-297` | 角度 [-180,180]，gripper [0,100] |
| 旧版校准说明 | 同 commit，`feetech_calibration.py:490` | 关节旋转用 degrees |
| v0.3.2 默认变化 | `src/lerobot/robots/so100_follower/config_so100_follower.py` | `use_degrees: bool = False`（2025-08-01 之后） |
| 当前默认 | `src/lerobot/robots/so_follower/config_so_follower.py` | `use_degrees: bool = True`，注释为兼容旧策略/数据集 |
| 场景限位 | `third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml` | 项目场景直接 include 该 XML |
| 公开范围 | `dataset-stats.json` | action/state min/max |

复现：

```bash
cd /home/mary/research/embodied-cogcal
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/smolvla-interface-preflight/audit_interface.py
```

脚本会重写 `summary.json`；原始结果已保留在 `summary-degree-assumption.json`。

## 3. 为什么不能靠“范围匹配”修掉

把公开角度范围线性缩放到场景 actuator 范围，可以让越界消失，但这是**循环论证**：
它假设公开数据的校准范围恰好等于场景关节范围，因而无法证明两套本体/校准等价。
正确的做法只有两类：

1. **拿到数据集校准文件**：用 `homing_offset`、`range_min/range_max`、resolution
   把公开角度还原到电机步数，再按本项目 SO-101 的校准映射到弧度；
2. **改用本项目自有数据**：在项目 SO-101 上采集示范，录制同一套校准/单位/相机字段，
   这样仿真—真机的“同体”才是可审计的。

在没有 1 或 2 之前，任何“裁剪后训练”的结果都只能作为 adapter smoke test，不能作为
TPSC 或 VLA 能力的证据。

## 4. 对 A100 计划的影响

- `docs/NEXT_A100_TPSC.md` 里的 20,000-step SmolVLA 基线**可以启动**，但必须满足：
  - 训练日志明确记录 `dataset_robot_type=so100_follower`、角度→弧度适配、gripper 映射；
  - 报告越界/裁剪计数；不把 loss 或成功率解释为 SO-101 同体性能；
  - 训练后先做离线 action chunk 维度/单位检查，再接入 MuJoCo。
- **TPSC 的 shared-prefix 失效实验不应使用这份数据**。它需要项目自有 SO-101 数据，
  否则“共享前缀”失败可能只是 SO-100/SO-101 接口差异。
- 如果 A100 时间有限，优先用这份数据验证 **LeRobot/SmolVLA 训练链路**（字段、相机、
  normalizer、checkpoint、显存/吞吐），不要用它验证科学假设。

## 5. 与 Codex 原记录的差异

| 项 | Codex 原记录 | 本文修正 |
|---|---|---|
| 单位 | 角度（正确） | 补充数据集时代证据：2025-05-23 旧版 degrees；v0.3.2 才改默认 |
| 越界 | “elbow/wrist 上界超出” | 量化为 +3.17° / +4.49°，并给出 `range_overflow` 字段 |
| 同体 | “不能声称同体” | 明确 `same_body_so101_claim=false`，给出允许/禁止用途 |
| 真实 SO-101 对照 | 无 | `kristaqp/so101-pick-place` 50 eps：elbow 100°，同样 +3.17°；wrist 86.1°，未复现 4.49° |
| 载体选择 | 只有 `svla` | 新增 `ngocthuong2212`（MuJoCo SO-101，200 eps）与 `kristaqp`（真实 SO-101，50 eps）两个更好载体 |
| 修法 | “先修正/解释范围与校准” | 给出两条可行路径：拿校准文件，或采集自有 SO-101 数据；拒绝范围匹配循环论证；elbow 限位可做显式 scene override，wrist 不一起放宽 |
| 原始 summary | `summary.json` | 保留为 `summary-degree-assumption.json`；新 `summary.json` 含证据/决策 |

## 6. 仍不确定的点

- 公开数据是否真的采自 SO-100，还是采自 SO-101 但 `robot_type` 标错；没有校准文件无法定论。
- 3–4.5° 越界是 SO-100 机械限位、校准范围，还是 SO-101 XML 的保守限位；需要本体/校准证据。
- 公开数据的 `shoulder_lift` 下界恰好 -100.0°、`elbow_flex` 上界恰好 100.0°，
  更像校准范围端点而非归一化；但这一点仍需原始校准文件确认。
- 本文没有加载模型权重，没有执行策略动作，也没有训练；所有结论只针对接口。

## 7. 下一步（给 Codex 的接续点）

1. 如果用户能提供 `svla_so101_pickplace` 的原始校准文件或采集配置：按 §3 路径 1 重算，
   再判断能否用于同体。
2. 否则按 §3 路径 2：在项目 SO-101 上采集 50+ 变体示范，记录校准/单位/相机，再跑
   `docs/NEXT_A100_TPSC.md` 的基线。
3. 在 A100 上只先验证 LeRobot/SmolVLA 训练链路；不要用公开数据跑 TPSC 失效实验。
4. 若要继续用公开数据做 smoke test，在训练/评估日志中写死：
   `dataset_robot_type=so100_follower`、`adapter=degrees_to_radians+gripper_0_100`、
   `clip_events=<count>`，并在结果表里标注“非 SO-101 同体”。
