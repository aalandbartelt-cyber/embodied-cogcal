# Codex 交接：SmolVLA/SO-101 接口预检接续

日期：2026-11-14。交接对象：Codex 线程 `01a1d541-f599-7ec0-8e72-e53e68ae6395`。
状态：**接口审计接续完成，未提交；等待 Codex/用户 review。**
本文不是查新报告，不是 TPSC 立项依据，也不是 A100/VLA 结果。

## 0. 为什么有这份交接

- 线程 `01a1d541...` 在 2026-11-14 **16:56:33 / 16:57:48（本地）** 两次撞到 Codex 额度上限；
  `goals_1.sqlite` 中 goal 状态为 `usage_limited`，错误提示重试时间 **21:08（本地）**。
- 最后一次提交：`bff44d3`（16:50:32，`research: narrow temporal support candidate and A100 carrier`）。
- 额度切断前，Codex 正在做 `experiments/so101/smolvla-interface-preflight/`：
  发现公开数据转成 MuJoCo 弧度后 `elbow_flex`、`wrist_flex` 越界，结论是“先修正/解释范围与校准映射，再跑 SmolVLA”。
- 本次由 GitHub Copilot 接续该接口问题；**没有改 Codex 的原始 `summary.json`**，
  而是把它保留为 `summary-degree-assumption.json`，并新增分析/决策/交接。
- 另一个 goal `01a1d85c...`（ARM-ERROR-COMP）也是 `usage_limited`；两个 goal 会互相抢额度，
  不需要同时跑时建议先暂停一个。

## 1. 一句话结论

> `lerobot/svla_so101_pickplace` 的元数据声明为 **`so100_follower`**，创建于 **2025-05-23**，
> 早于 LeRobot v0.3.2；旧版明确用 **degrees（[-180,180]）+ gripper 0–100**。
> 角度假设成立；`elbow_flex` / `wrist_flex` 越界 **+3.17° / +4.49°** 是真实范围差异，
> 不是 `RANGE_M100_100` 归一化误读。**不能声称 SO-101 同体**（机械本体尚未独立验证）。

决策：

- 这份公开数据只允许作 **carrier smoke test**，显式做角度→弧度、gripper 0–100→场景 hinge 的适配，
  并计数/报告 clip 事件。
- **不允许**用它直接训练/评估 TPSC 的 SO-101 同体基线，或把 A100/VLA 失败归因于 TPSC。
- TPSC 同体实验需要：项目自有 SO-101 示范（记录校准文件/revision、`use_degrees`、关节限位），
  或明确声明 `robot_type=so101_follower` 且带校准元数据的公开数据。
- **更好的公开载体（2026-11-14 新增）**：
  - 仿真同模型：`ngocthuong2212/so101_mujoco_follower_7_31`（200 eps、60,245 frames、
    MuJoCo、`so101`/`degree` 标签、action 范围与 XML 逐关节吻合、top/front 相机、
    Apache-2.0）；适合 loader/SmolVLA 训练链路 smoke test，但只有单任务。
  - 真实 SO-101：`kristaqp/so101-pick-place`（50 eps、17,505 frames、
    `so101_follower`、side/wrist 相机、Apache-2.0）；真实 SO-101 的 elbow 也到 100°，
    说明 XML 的 96.83° 是保守限位，不是 SO-100 独有；但无校准文件。
  - `svla_so101_pickplace` 保留为 SO-100/异构负对照，不再作为主载体。
- **XML 限位提醒**：真实 SO-101 可到 elbow 100°；不要直接改 `third_party` 的官方 XML。
  若要支持 100°，做显式 scene override（记录来源/碰撞检查），或在 smoke test 中裁剪并计数。
  `wrist_flex` 的 4.49° 越界仍未在真实对照中复现，不能一起放宽。

### 1.1 Codex 恢复时的 5 步

1. `git status` + `git diff` review；**不要覆盖** `summary-degree-assumption.json`。
2. 读 `range-mismatch-analysis.md` §1/§1.1/§3、`public-dataset-scan.md` §3/§4，
   以及 `experiments/so101/tpsc-data-protocol.md` §1/§4/§6。
3. 先做 P1：拿 `svla` 的原始校准文件，或改用 `ngocthuong2212`（仿真）/
   `kristaqp`（真实）这两个更好的公开载体。
4. 若上 A100：优先用 `ngocthuong2212/so101_mujoco_follower_7_31` 跑 loader/SmolVLA
   训练链路 smoke test；日志写死 §5/P2 的四个字段。
5. P1 完成前，不启动 TPSC 的 shared-prefix 失效实验。

## 2. 证据链

| 证据 | 来源 | 说明 |
|---|---|---|
| 数据集创建时间 | `https://huggingface.co/api/datasets/lerobot/svla_so101_pickplace` → `createdAt=2025-05-23T12:31:31Z` | 早于 LeRobot v0.3.2（2025-08-01） |
| 数据集 `robot_type` | `dataset-info.json` | `so100_follower`，不是 `so101_follower` |
| 旧版单位说明 | [LeRobot `6163daaa...` 的 `manipulator.py:294-297`](https://github.com/huggingface/lerobot/blob/6163daaaa4fa193d0e37468a94d90e07ef3c95ce/lerobot/common/robot_devices/robots/manipulator.py#L294-L297) | “Rotations are expressed in degrees in nominal range of [-180, 180]”；gripper [0,100] |
| 旧版校准说明 | [同 commit 的 `feetech_calibration.py:490`](https://github.com/huggingface/lerobot/blob/6163daaaa4fa193d0e37468a94d90e07ef3c95ce/lerobot/common/robot_devices/robots/feetech_calibration.py#L490) | “Joints with rotational motions are expressed in degrees…” |
| v0.3.2 默认变化 | [`config_so100_follower.py`](https://github.com/huggingface/lerobot/blob/v0.3.2/src/lerobot/robots/so100_follower/config_so100_follower.py) | `use_degrees: bool = False`，2025-08-01 之后才改 |
| 当前默认 | [`config_so_follower.py`](https://github.com/huggingface/lerobot/blob/fe1c54594f6ba275fccf210b9f7b11f0e2324b89/src/lerobot/robots/so_follower/config_so_follower.py) | `use_degrees: bool = True`，注释为兼容旧策略/数据集 |
| 场景限位 | `third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml` | 项目场景直接 include 该 XML |
| 公开范围 | `dataset-stats.json` | action/state min/max |

### 2.1 越界量

| 关节 | 公开范围（度） | 场景范围（rad） | 场景上界（度） | 越界 |
|---|---|---:|---:|---:|
| `shoulder_pan` | -93.46 .. 88.01 | -1.91986 .. 1.91986 | ±110.00 | 无 |
| `shoulder_lift` | -100.00 .. 8.13 | -1.74533 .. 1.74533 | ±100.00 | 无（下界贴边） |
| `elbow_flex` | 12.97 .. **100.00** | -1.69 .. 1.69 | ±96.83 | **+3.17°** |
| `wrist_flex` | 33.53 .. **99.49** | -1.65806 .. 1.65806 | ±95.01 | **+4.49°** |
| `wrist_roll` | -92.77 .. -20.00 | -2.74385 .. 2.84121 | -157.2 .. +162.8 | 无 |
| `gripper` | 0 .. 33.00 | -0.17453 .. 1.74533 | — | 无（百分比映射后） |

精确值在 `summary.json` 的 `range_overflow`：

- `elbow_flex.high_rad = 0.05532925199432959`（3.1701°）
- `wrist_flex.high_rad = 0.07836830184101218`（4.4902°）

## 3. 本次改动

| 文件 | 状态 | 内容 |
|---|---|---|
| `experiments/so101/smolvla-interface-preflight/audit_interface.py` | 修改（未跟踪目录内） | 新增 `DATASET_PROVENANCE`、`range_overflow`、`decision`；更新 `required_adapter`/`limitations` |
| `experiments/so101/smolvla-interface-preflight/summary.json` | 重新生成 | 含 provenance / overflow / decision |
| `experiments/so101/smolvla-interface-preflight/summary-degree-assumption.json` | 新增 | **Codex 原始 summary 的备份**，不要覆盖 |
| `experiments/so101/smolvla-interface-preflight/range-mismatch-analysis.md` | 新增 | 完整证据链、越界表、真实 SO-101 对照、决策、复现命令 |
| `experiments/so101/smolvla-interface-preflight/public-dataset-scan.md` | 新增 | 公开 SO-101/SmolVLA 数据集扫描、候选对比、载体决策 |
| `experiments/so101/smolvla-interface-preflight/audit_real_so101_range.py` | 新增 | 下载 50 集真实 SO-101 parquet 并计算 action/state 范围 |
| `experiments/so101/smolvla-interface-preflight/real-so101-reference.json` | 新增 | `kristaqp/so101-pick-place` 的 50 集范围证据 |
| `experiments/so101/tpsc-data-protocol.md` | 新增 | 项目自有 SO-101 三族任务对采集协议、字段、拒绝准则、2 周 pilot |
| `experiments/so101/tpsc-pilot/` | 新增 | 20/120 manifest、`validate_manifest.py`、`smoke_scene.py`、MuJoCo scene smoke、6 张渲染 |
| `experiments/so101/smolvla-interface-preflight/README.md` | 修改 | 追加 2026-11-14 接续分析，指向新分析 |
| `docs/NEXT_A100_TPSC.md` | 修改 | 修正接口段落：degrees 证据、+3.17/+4.49°、SO-100 非同体、只作 carrier smoke test |
| `docs/prior-art/ROUTE_DECISION.md` | 修改 | 在载体接口段追加“真实范围差异、非同体”的结论 |
| `findings.md` | 修改 | 追加一条接续结论 |
| `progress.md` | 修改 | 追加一条接续进度 |
| `task_plan.md` | 修改 | 追加接口前置条件与接续结论 |
| `docs/CODEX_HANDOFF_20261114.md` | 新增 | 本文件 |

**未提交。** 这些改动与 Codex 原有的未提交改动混在同一工作树；建议先 `git diff` + `git status` review，
再决定是否一起提交。`experiments/so101/smolvla-interface-preflight/` 整个目录仍是 untracked。

## 4. 复现

```bash
cd /home/mary/research/embodied-cogcal
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/smolvla-interface-preflight/audit_interface.py
```

检查关键字段：

```bash
python - <<'PY'
import json
d=json.load(open('experiments/so101/smolvla-interface-preflight/summary.json'))
print(d['mapped_range_inside_scene'])
print({k:v for k,v in d['range_overflow'].items() if v['high_rad'] or v['low_rad']})
print(d['decision'])
PY
```

文档测试：

```bash
cd /home/mary/research/embodied-cogcal
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 conda run -n cogcal python -m pytest tests/test_docs.py -q
```

## 5. 下一步（建议顺序）

### P1：决定公开数据的用途

- **优先换载体**：
  - 仿真：`ngocthuong2212/so101_mujoco_follower_7_31`（200 eps，MuJoCo，SO-101，
    action 范围与 XML 吻合）用于 loader/字段/单位/SmolVLA 训练链路 smoke test；
  - 真实：`kristaqp/so101-pick-place`（50 eps，`so101_follower`）用于真实 SO-101
    单位/范围参考；
  - `svla_so101_pickplace` 只作 SO-100/异构负对照。
- 如果仍要用 `svla`：先拿它的**原始校准文件/采集配置**，按 `homing_offset`、
  `range_min/range_max`、resolution 还原电机步数，再映射到项目 SO-101；
  重新跑 `audit_interface.py`，用真实校准范围判断是否仍在场景限位内。
- **elbow 限位**：真实 `so101_follower` 数据也到 100°，官方 XML 的 96.83° 是保守限位。
  不要直接改 `third_party/SO-ARM100` 的官方 XML；若要支持 100°，做显式 scene override
  （记录来源、碰撞检查、标注“非官方默认”），或在 smoke test 中裁剪并计数。
  `wrist_flex` 的 4.49° 越界尚未在真实对照中复现，不能一起放宽。
- **不要**把公开角度范围线性缩放到场景范围来“消除越界”；这是循环论证，不能证明同体。

### P2：A100 上只验证训练链路

优先用 `ngocthuong2212/so101_mujoco_follower_7_31` 跑 `docs/NEXT_A100_TPSC.md` 的
20,000-step SmolVLA 基线；它的 action 范围与 XML 吻合，不需要 elbow 裁剪。
训练/评估日志写死：

```text
dataset=ngocthuong2212/so101_mujoco_follower_7_31
dataset_revision=de301f7afe016cef14ac46a238714f52e15bf932
dataset_robot_type=so_follower
adapter=degrees_to_radians+gripper_0_100
clip_events=<count>
claim=sim_same_model_carrier_smoke_test_not_policy_result
```

如果改用 `kristaqp/so101-pick-place` 做真实参考，日志写死：

```text
dataset=kristaqp/so101-pick-place
dataset_revision=994aa6d4f68e33ac93c410085eca4beb9cc14aea
dataset_robot_type=so101_follower
adapter=degrees_to_radians+gripper_0_100
elbow_clip_events=<count>
claim=real_so101_carrier_smoke_test_not_calibration_equivalence
```

只看：字段、相机、normalizer、checkpoint、显存、吞吐。**不要**用任何公开数据跑 TPSC
失效实验，也不要把 loss/成功率解释为 SO-101 同体或真实机器人能力。

### P3：TPSC 同体实验

前置条件：

1. 项目自有 SO-101 示范（建议 50+ 变体），记录校准文件/revision、`use_degrees`、关节限位、相机字段；
2. 或找到明确 `robot_type=so101_follower` 且带校准元数据的公开数据；
3. shared-prefix / no-common-prefix / multi-valid 三类任务对，先冻结任务谓词与分叉字段；
4. 先测普通 BC/SmolVLA 与 BAS-VLA/阶段状态等强基线，再决定是否实现 outcome-conditioned support。

采集协议已写成 `experiments/so101/tpsc-data-protocol.md`：
- 先做 1 个 pair × 2 branches × 10 episodes = 20 episodes 的管线试跑；
- 通过后扩到 3 families × 2 pairs × 2 branches × 10 = 120 episodes（资源上限，不是功效承诺）；
- 每 episode 记录 `episodes_meta.jsonl`、校准 hash、场景 placement、成功谓词；
- 拒绝率 >20% 先修载体；shared-prefix 不存在共享正确前缀则停止 TPSC 方法主张。

已落地的 pilot 资产：`experiments/so101/tpsc-pilot/` 有 20 条 pilot 和 120 条 full manifest，
`validate_manifest.py` 通过配对/几何检查，`smoke_scene.py` 在 MuJoCo 4.0.1 上逐条 reset 并验证
目标物体从“不在 goal”到“放入 goal 后评估器为 true”。`check_reachability.py` 用 20k 关节采样
确认 240 个目标物体/goal 点都在夹爪 5 cm 内（最差约 3.5 cm），但这是几何 proxy，不证明抓取/
放置/碰撞安全。

`scripted_prefix.py` 已用数值 IK 跑 full 120：
- shared-prefix 的 target/executed prefix diff = **0.0**；
- no-common 从 `above_object` 起 diff > **1.2 rad**；
- multi-valid prefix diff = 0、route diff > **1.15 rad**；
- kinematic-carry `place_success=120/120`，但物理抓取 pilot 0/20，final 56/120。
这验证的是**任务结构/路径**，不是 learned policy 的 prefix，也不是物理抓取 benchmark。
下一步必须用 VLA/BC 策略复测同一 prefix 命题。

## 6. 给 Codex 的注意事项

- **不要覆盖** `summary-degree-assumption.json`；它是 Codex 原记录的审计备份。
- **不要修改** `third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml` 的官方限位来迁就公开数据；
  若要改，必须另有本体/校准证据，并单独记录。
- **不要把 elbow 与 wrist 越界混为一谈**：真实 `so101_follower` 数据也到 elbow 100°，
  所以 +3.17° 不等于 SO-100 证据；`wrist` 的 +4.49° 尚未在真实对照中复现。
- **不要把 `use_degrees` 的当前默认当成数据集时代默认**：数据集创建于 2025-05-23，
  早于 v0.3.2；旧版 `manipulator.py` 明确用 degrees。
- **不要把 `robot_type=so100_follower` 当成笔误**：在拿到机械本体/校准证据前，按 SO-100 处理。
- **不要把“范围对齐后能跑通”当成同体证明**：范围匹配是 adapter，不是 calibration。
- TPSC 仍是未立项候选；本次只解决载体接口，不改变 TPSC 的查新/失效验证状态。

## 7. 建议的提交信息（若 review 后一起提交）

```text
research: resolve SmolVLA/SO-101 unit provenance and range blocker

- Confirm the public dataset is a 2025-05-23 SO-100-era degrees recording.
- Quantify elbow/wrist overflow (+3.17°/+4.49°) against the SO-101 XML.
- Reject same-body claim; restrict the public data to carrier smoke tests.
- Preserve the original preflight summary and add the range-mismatch analysis.
```

## 8. Codex 恢复后的当前状态（覆盖前文“未提交”状态）

- 已完成 review 并提交 `af47281`（按用户建议消息）；原始 degree-assumption 与全部 manifest/JSON 保留。
- review 发现的范围限制见 `experiments/so101/tpsc-pilot/REVIEW.md`，尤其是 pair 汇总仅保留最后重复。
- 用户最新明确：研究方向尚在预实验阶段，先用本机 RTX 5070 Ti，不等待 A100。
- 本机 torch sm_120 GPU 矩阵计算已实际通过；独立 policy 环境建立中。
- 指定 carrier 的原始 gripper 范围 -10..64.45，不能直接继承 SO-100 0–100 夹爪适配。

## 9. 本地 GPU 接续（当前）

- 用户已明确先用5070Ti；源资产提交af47281并已推送。
- 真实CUDA smoke和资源试跑结果：`experiments/so101/tpsc-pilot/runs/local-5070ti/`。
- 20k carrier训练session74436 / PID87789，日志`training-20k.live.log`；先检查进程和日志再继续，观察超时不能据此重启。
- 固定最终20k checkpoint：`checkpoints/tpsc-carrier-20k/checkpoints/last/pretrained_model`，不使用资源试跑checkpoint作TPSC正式结果。
- 20条能力screen入口`learned_rollout.py` / `policy_worker.py`；尚未执行，先完成训练并核查单位/相机适用范围。
- 当期go/no-go页在上述runs目录；shared-prefix与uniform separation伤害均为不可判定/未测试。

## 10. 接续时先读的科学更正

- `docs/prior-art/tpsc-loss-fidelity-correction.md`：固定上游源码实际CPU/autograd核算。
- 原toy 2.0仅为逐步hinge求和；展平chunk对应0，公开BAS权重为per_step/legacy，两者不得混称。
- 在完全相同动作点，PyTorch范数次梯度为0；正目标值不证明会产生前缀更新，更不证明任务伤害。
- “等未来损失→支持保持”已撤回，因为两任务可能同样失败；需要分别成功续接的证据。
- 原toy与degree-assumption JSON均保留；新计算写入`experiments/so101/tpsc-loss-fidelity/`。
- 用户新材料`docs/VLAkaiyuanxiangmu.md`已读取，原文不改；15个原始仓库revision/README哈希见
  `experiments/so101/vla-open-source-audit/repository-inventory.json`。模型/框架开放不等于SO101即插即用。

## 11. 训练完成后的自动能力screen

- 当前是队列v2：session57985 / PID2595058，启动契约`runs/local-5070ti/pilot-queue-v2-start.json`。
  `/tmp/tpsc-final-pilot-queue-v2.py`等待原训练PID退出，不重启/终止训练；核`End of training`、
  `020000/training_state/training_step.json=20000`、manifest哈希与模型文件，再哈希checkpoint并运行20条。
- 输出目录预定`runs/local-5070ti/pilot-20k/`，输出日志`pilot-20k.live.log`；队列状态`pilot-queue.live.log`。
  目前仅排队，是否已运行必须核进程/日志/输出，不能把启动快照当完成。
- v1因本地没有OSMesa，在episode开始前取消；原记录保留。v2使用刚实测通过的EGL。
- 新机械检查：旧scripted OPEN/CLOSED与渲染张合方向相反；IK追踪夹爪转轴body原点，
  与官方gripperframe相距8.207cm。证据`experiments/so101/tpsc-pilot/gripper-readiness-audit/`。
  旧脚本不是可用物理teacher，8.6mm不是指尖对物误差；不覆盖原代码或旧JSON。
