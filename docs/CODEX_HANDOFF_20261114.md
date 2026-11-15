# Codex 交接：SmolVLA/SO-101 接口预检接续

日期：2026-11-14。交接对象：Codex 线程 `01a1d541-f599-7ec0-8e72-e53e68ae6395`。
**2026-11-15当前选题裁决见§21：尚无方向通过门槛，指令必要性发现已降为诊断工具。**
最新状态：**本地20k普通训练与原20条learned pilot已完成，任务成功0/20；载体未就绪，TPSC不进入方法实现。**
当前事实、文件与下一步见§12；§0–11保留接续历史，旧进程号不是当前运行状态。
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

## 9. 本地 GPU 接续（历史启动状态）

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

## 12. 已完成20k与20条pilot：接续时以本节为准

- 原训练和v2队列在用户中断轮次后均已消失；最近完整训练状态为018000。核实记录为
  `runs/local-5070ti/training-interruption-18000.json`。从该状态恢复模型/optimizer/scheduler/RNG，
  固定seed42、batch4、20k终点；数据采样器位置不恢复，因此不声称与不中断训练逐位等价。
- 恢复训练session3899正常退出0，日志20:38:16出现`End of training`；训练状态确认为20000。
  **不要重启训练或旧队列。** 选用精确`checkpoints/tpsc-carrier-20k/checkpoints/020000/pretrained_model`，
  不是事后挑best。权重SHA256：`af89ed56d0d804ac0acdd1ee7ed4008d8ec3ad4a24e7fa5fea6330c9dda6f257`。
- v3队列session15171退出0；20:38:28–20:44:24使用EGL执行原20条manifest，策略只接收RGB/q/语言/seed。
  全部20条、10个pair、600个chunk、6000个控制目标均已保存并核验，没有执行120条扩展。
- 实测任务成功**0/20**、抬升0/20、放置0/20；全部失败记录为`stable_placement_not_achieved`。
  55个控制目标向量被裁剪。左右初始q和seed相同，RGB与语言同时变化。
  首chunk平均距离0.202309–1.080547rad；每对实测q首次分叉只可定位到(0,10]控制步。
  这些描述值不能识别**正确**共享前缀或语义的因果伤害。
- 原始记录/核验/全部pair表/完成日志与hash在
  `experiments/so101/tpsc-pilot/runs/local-5070ti/`，入口为`go-no-go.md`与`completed-evidence-inventory.json`。
  正式原始JSONL不覆盖，checkpoint/data留在本地忽略目录；本轮不是A100结果。
- 明确限制：公开数据只有green→container单任务，与本项目红物体/中文左右任务不匹配；
  相机、零位与夹爪适配尚未源级核验。batch4×20k仅约1.33数据遍历，不能等同batch64×20k。
  训练loss是flow速度回归，不是解码动作误差；推理时仿真暂停，不声称真机实时性。
- **判定：载体未就绪；正确共享前缀不可识别；uniform separation未测试；不实现TPSC方法。**
  这不是TPSC被科学否证，也不是通过查新。完整选题目标继续active。
- 同期新增[支持集合更正](prior-art/tpsc-support-identifiability-correction.md)和
  [经典对照/问题发现](prior-art/tpsc-classical-controls-and-discovery.md)：共同可行动作存在不强制点态一致；
  需普通BC、同池配对BC、合理margin与多模态等强对照。ECT噪声耦合仅是机制分解问题，
  通用antithetic flow训练已非空白，不能直接升格为新方法。
- 物理teacher的25次单初态debug仍未得到合格双指抬升，不计独立样本或VLA失败率。
  新的选题证据必须来自有能力的策略/有效任务和具体可重复失效，不能继续从接口失败提炼创新。
- 新的独立载体线索：固定外部`FERBIN12/so101-manipulation-eval` b02b8b2，原样place成功、hover不算放置；
  独立双指接触记录复跑亦成立，双指且抬升最长2.6365s。该模型有盒状指垫、friction2和28mm物体，
  与原TPSC接触模型不同；只提供资格场景的可行路径，不替代原20条0/20或真机证据。
  证据与复现脚本：`experiments/discovery/so101-upstream-contact-reproduction-20261114/README.md`。
- 新核验的R3L已有文本轨迹共享前缀mask；DEFLECT v3已有机器人fresh/stale共同随机数和FM-DPO
  单样本surrogate范围说明；TPC-FM已有配对时间及速度一致性。不要再把通用prefix保护/噪声耦合包装成新核心。

## 13. 匹配物理teacher与小BC已跑完：最新接续入口

完整目标仍为确定可查新、有先进性、可产出且同题SO-101仿真—真机的研究方向。
用户最新资源选择是本地5070Ti先探索，A100后续使用；不把打通环境当方向。

- 外部b02b8b2载体的中央source资格0/10，事后发现HOME指垫初始穿透15.37mm；
  自适应避开后的10/10仅为物理运动资格，两目标55mm成功圆重叠，不是语义配对验证。
- 独立30Hz零阶保持teacher四例资格通过；固定单目标、35mm半径、双指持物抬升≥.5s、
  最终无机器人接触≥.1s、最大穿透≤1.5mm后，24train/8val匹配示范32/32通过。
- 5Hz双相机+30Hz实测q；小CNN chunk BC固定seed42、2000步最终权重，未挑best。
  测试6100–6119全部完整运行：0/20任务成功、0/20双指抬升，2828个命令向量限幅。
  这是独立小BC能力失败，不覆盖原SmolVLA20条，不构成TPSC或执行补偿失效证据。
- 原小BC流水线systemd `cogcal-matched-bc-20261114.service`已正常结束，三阶段exit0；
  不要再次启动。checkpoint SHA：
  `f49da6e9c82c55a2478bf580e049365fbde3e3bd8bff2a8fc1bfcbe33a23e237`。
- 同一冻结权重在既有val集诊断：执行6步0/8；执行30步4/8，后者8例均双指抬升及目标内放桌，
  4例未释放。该诊断在看到原测试失败后启动，不能当新测试或预注册机制验证。
  `cogcal-bc-horizon-diagnostic-20261114.service`亦已exit0。
- 全30Hz图像采集因llvmpipe成本主动SIGINT，首条及原源码快照保留，未复用进5Hz数据。
- 代码/证据入口：`experiments/discovery/matched_bc/`、
  `experiments/discovery/matched-bc-lowrate-20261114/README.md`、
  `experiments/discovery/matched-bc-horizon-diagnostic-20261114/README.md`。
- 查新入口：`docs/prior-art/history-compensation-mechanism-screen.md`，15份有界原文读取清单。
  SwitchVLA/MemoryClock/RePlanMem/EventVLA覆盖任务切换和事件记忆宽题；
  APEX/Tune to Learn/NADA/GAP/Mind the Gap/自补偿VLA强约束执行补偿与本体捷径；
  action-chunk非Markov/延迟集成/长历史/配对OL-CL探针及TRACT已有直接原文。
  GAP仓库存在但固定入口AST失败、未找到tracked license；未修复/复用或声称复现。

下一步先定位普通BC能力失败。不要盲目扩大训练、延长episode预算、放宽释放条件，
或从一个不会做任务的策略解释补偿伤害。若采用新基线/协议，原结果保留，另设记录和测试边界。
窄问题“精度改善是否破坏学到的阶段线索”仍未证实、未通过查新；通用gain/noise/历史解释若成立则降级。
尚未确定方向，完整目标保持active。

## 14. 进一步能力对照已完成：停止继续微调该小模型

本轮实际进展是60条完整learned rollout与新的原文约束，不是方向已确定。
旧章节的“下一步定位小BC”已经执行，接续不能再次启动相同基线。

- 同一GRU结构/初始化/参数量/采样序列、固定2000更新：carry11/20，reset4/20，
  新测试7100–7119。均未达16/20能力门槛。carry独成功9、reset独成功2，共同成功2、共同失败7；单训练seed不作总体优势主张。
- 全24train近似观测诊断发现短历史接近/未来动作不同，但没有完整输入严格相等，不能称不可辨识定理。
  首两条严格RGB筛选0命中及后续连续距离分析的事后性质有记录。
- carry8条抬升失败均在闭爪前已有物体>2mm XY位移。离线FK/颜色定位仅诊断，
  未把感知不足定为唯一根因。初始图像固定颜色定位val8条平均1.49mm不是硬件精度结果。
- 独立初始RGB颜色特征＋普通GRU、固定2000更新、新8100–8119：15/20完整成功、19/20抬升；
  4放置失败、1未抬升。仍未过门槛，不延长episode、不放宽条件、不挑checkpoint。
  按执行前计划停止继续微调此小模型架构。不是统计证明不可行，也不能把15/20近似算通过。
- 原SmolVLA0/20、普通CNN0/20、val16条及本轮60条均保留，不互相覆盖；补偿/TPSC干预仍为0。
- 权重SHA与完整记录：`experiments/discovery/recurrent-bc-20261114/README.md`、
  `experiments/discovery/anchor-bc-20261114/README.md`。
- systemd `cogcal-recurrent-bc-20261114.service` 与 `cogcal-anchor-bc-20261114.service`
  均inactive、MainPID0、ExecMainStatus0；不要从日志或计划误判仍在训练/需重启。
- `experiments/discovery/recurrent_bc/audit_evidence.py`核查60episode/17100命令/2880chunk、
  q历史连续、限幅、hidden reset/携带、初始缓存、最终权重和绑定源码。当前证据为 `evidence-audit-v2.json`。
- 新核到Copycat/因果混淆、CSA组合偏移、IMEP记忆干预评测，读取范围/限制在
  `docs/prior-art/feedback-memory-followup.md`。不把普通history/残差/组合补偿/记忆干预再当创新。

当前决定：暂停该小模型的架构/超参数试错，优先收窄值得验证的具体科学问题；
如未来需要新carrier，先审查成熟策略/匹配数据并写新资源边界，而非盲目增加训练步数。
“提高执行精度破坏阶段线索”仍是未证伪的问题，既未实测也未通过查新，不应写成主推荐。
完整目标不变，尚未达到完成条件；不把工程产物、普通BC成功或已否决方向数当科研成果。

### 新发现的优先查新/载体入口（本轮末）

NVIDIA官方SO101教程及SAGE/GapONet/Workshop已核到固定源码，见
`docs/prior-art/nvidia-so101-sage-gaponet-audit.md`。
这进一步排除“同动作测间隙＋神经补偿＋VLA后接补偿＋同体sim-real”的宽题新意，
同时提供匹配vial/rack场景、75条sim数据和N1.6检查点入口，值得先读而非继续自己调小BC。
SAGE revision `5b31cfa35416d1300b5099557049bd8e9cb4507d`；
GapONet `91eb8819c3156b46fdb3266a048600c67c9adf5d`；
Workshop `ce807d99724cb65671abec01f908a2fcb4a6eab7`。
只读缓存在被忽略的 `data/discovery/nvidia-so101-audit-20261114/`；三个git clone是no-checkout，
用git show固定revision读取19份指定源码，没有安装/执行它们。

注意：官方SO101 GapONet＋GR00T集成仍列future work，不能写成现成可运行策略。
SAGE的五轴rad＋gripper0–1与Workshop五轴原始−100…100＋gripper0…100不是同一契约。
N1.6检查点10000元数据含RELATIVE arm/ABSOLUTE gripper、processor16与config50的horizon边界，
需要完整解码核验。没有下载权重或迁移环境；每checkpoint权重文件约9.81GB，不能保证12GB装下。
官方数据行18250帧与页面18326行、co-train的5/50real条数不一致均保留未决。
下一步优先审查SAGE真实轨迹/单位/时钟与当前窄问题的实质差异；不把metadata核验当性能复现或查新通过。
资源边界另核到Isaac Sim5.1官方要求不支持无RT Cores的A100/H100、列16GB最低显存；
本机5070Ti Laptop12GB未验证该栈。SAGE绑定5.0.0的requirements地址404已记录，
不声称运行过或将5.1要求冒充5.0测试。仍保留MuJoCo，不自动转Isaac/A100渲染。

## 15. 用户再次提醒完整目标后的接续

优先看 [RESEARCH_READINESS 当前结论](RESEARCH_READINESS.md) 与
[本轮执行证据边界](prior-art/execution-evidence-followup.md)。未确定方向，目标仍 active；
后续最多同时深入两个具体问题，不能以工程/资料数量或全数否决替代正向选题。

SAGE 三类公开真实记录已读，共 16,840 行，来源及自有审计在
`experiments/discovery/sage-real-20261114/`。有离线建模入口，但没有 RGB/任务成功/匹配 sim。
命令和状态逐行同时间戳；当前 collector 是先发后逐电机读、同记循环起点，历史版本未知。
未估计纯机械延迟、sim-real gap 或补偿收益。原始源 CSV 留在忽略目录，不复制公开。

SimuGuard 已有假失败监测、精确重放和物理窗口干预；不能泛称新问题。
GapONet 作者页可核到出版条目，OpenReview 全文仍为浏览器验证，不能写成逐式深审完成。
“执行精度改善破坏阶段线索”仍未实测、未过查新。不要重启已结束的小 BC 试验或运行补偿干预，
也不自动下载 GR00T / 安装 Isaac。受保护原 JSON、manifest、官方 XML 未改。

## 16. 有效示范的新问题入口（只到前提核查）

`experiments/discovery/so101-retarget-screen-20261114/README.md` 记录本轮新增运动学证据、
CP-Gen / MoMaGen / Isaac Capture 强对照，以及作者博客资产不能复核的范围。
固定官方XML24配置的Jacobian均秩5，中心差分通过；配置不是任务episode，不能作任务失败率。
固定缺失工具轴的假定不适用于直接搬用到本项目模型；没有证明博客不同模型的实现错误。

保留的条件问题是：任务已有成功见证时，现有强约束示范增强是否仍错拒并损害覆盖/策略。
目前没有此证据；关键点/约束优化已经存在，不能改IK或换SO101便立项。
如继续先做同源/同场景/同预算的生成方法比较，并保留直接成功见证；强简单对照能解决则停止该核心。
不要为此重启小BC/下载大模型；本轮没有策略训练或真机结果。完整选题仍未完成。

## 17. 位姿重定向物理检查已完成，勿再把该线当待运行

`experiments/discovery/so101-retarget-physical-20261114/README.md` 为最新入口。
源与四目标的teacher见证5/5；两种identity2/2；完整位姿与简单方向IK各4/4。
共15条/4275个命令，正常exit0，全部trace/原始stdout/IK诊断/绑定源码与执行前计划保存。
独立audit从trace复算成功谓词及身份/时序/限幅，当前 `verification-v2.json` 通过；v1及原脚本保留。

**当前决定：本工作区未见候选任务损害，停止该核心，降为载体工具；不扩大扰动制造失败。**
源码在 `experiments/discovery/retarget_physical/`，非learned/VLA，也不是忠实CP-Gen实现。
最终物体误差6.38–33.34mm，不能称精度补偿成果；无真机/新方法/数据覆盖损害结果。
SciPy1.16.3只以 --no-deps补装到cogcal-sim，NumPy/MuJoCo未改；原source模型及受保护文件未改。
完整目标仍active，尚无可确定方向；下一步应寻找不同具体问题，不重启已结束BC或此15条筛查。

## 18. 11月15日VFD机制线索：有解析证据，尚未立项

最新入口：`experiments/discovery/vfd-quadrature-20261115/README.md`。
48条件的精确OT评分检查、6个有限路径偏差、72对OLS及同数据144拟合/216终点均已实际运行。
它们是低维解析/回归条件，不是VLA或SO101 episode；不与原有失败carrier混用。

- 固定原始源码默认评分11点产生20/1062个明确MI排序反转，连续定理仍成立；Gauss–Legendre20点解决这组反转。
- 终点相同的有限路径偏差可产生正分数，连续代理积分发散；该场违反人口最优OT假设，不作定理反例。
- 同数据不同初始化的两参数模型收敛后分歧降至约1e−30或更低，不隐去普通优化即可解决的强对照。
- 新近邻FM Geometry已明确终点数值污染/prefix，MMG/MINDE已有信息积分，flow_kl已有有符号演化；不再把去尾、换积分或修正恒等式当新核心。
- 解析图在`.research/figures/vfd_grid_analytic_20261115.*`，已实际查看；图d是按事后固定首反转规则展示的解释性例子。
- 本轮原始UQ源码只留data忽略目录，固定bcc2433；函数通过AST原样加载但未安装完整上游或运行检查点。Scholar429、SciSpace只作metadata发现。

下一证据必须来自同数据/不同seed且有任务能力的真实learned ensemble，以及冻结动作生成过程的评分/示教或转交后果。
目前无此证据，不自动启动神经网络训练或声称同题真机可行，也不把该解析线索当方向确定。

## 19. VFD版本与资产后续：当前线索移出主推荐

入口：`experiments/discovery/vfd-assets-20261115/README.md`；上轮属于progress，提交570ef7c。
补读UQ v2 §4/A.2/§7/C.7，连续OT条件仍保留且已有评分时刻消融；CFM/NLL 2608.28010v1
§6.2/A.5已有保持Gaussian边缘分布而改变CFM比率的构造，不把不同的一维例子当新原理。

- 新查Bijou ebaa8e0和两个公开HF权重库metadata：有raw checkpoint入口，但本轮未验证合格独立flow ensemble或任务成功。
- 固定Drishti eeaaaf4，实际只读SQLite63条/4607步/546图像行，tree有756embedding文件覆盖60条（34成功/26失败标签）。
- 六维q/action完整；805步32维head mean/std是压缩摘要、非完整action chunk/ODE，不可恢复VFD；t是步号，非物理秒。
- 3条仅1步的成功标签记录初态已在当前xy区域，逐步cube/contact缺失，不能复算物理抓放；不改标签、不作任务能力通过。
- Drishti官方AUC含样本内评分；本轮没有重训检测器/复算AUC，没有下载策略权重或执行上游。
- FlowEval A.2已描述事后重建动作标签与真实命令不一致及hold-position对照，不包装为新核心。

当前VFD路径线移出主推荐，停止扩大纯解析构造；下一动作恢复具体任务失效发现。
不是证明空间不存在，不是因无公开权重就否决科学问题；完整目标active，无候选通过立项门槛。

## 20. 指令必要性测量：组件反例与双物体物理见证

入口：`experiments/discovery/instruction-necessity-20261115/README.md`。上轮7e49b34属于progress。
当前新线索是静态多候选/唯一语言目标不自动保证完整轨迹评分需要语言；不是重启TPSC/VFD。

- 固定RoboOrchard f2e041e（2026-10-22），原样AST scorer/builder及episode loop，物理checker接受控事实。
- N=2/3/6正反扫描的原始累计评分全通过；informed-single仅单目标、no-op/reach-only无终态success、dwell边界正常。
- 原始loop对两目标在24/53步分别停止，同一policy忽略instruction；只改为56步、保留累计评分仍全成功。
- 另冻结本地MuJoCo物理计划，外部b02b8b2显式新增第二同参数cube，不改原XML。A→B/B→A均实际抬升两对象、每个最长1.241s；single A/B及no-op完整。5条1848命令，0clip，max penetration约.117mm，物体rollout无pose写入。
- fresh replay全部trace字节一致；audit v2核单目标和相应scan前231步命令/物理状态完全一致。不是随机独立重复或VLA能力通过。
- 原始ContactChecker含力阈值/法向，本地仅双指接触见证，不混成完整Isaac复现。代码4阶段0.25与论文v1 2阶段0.5不同。
- 已读InstructMove v1、One Word v2及Inner Monologue/Code as Policies原始终止对照；去oracle、严格首选择/commit均不能当新算法。若允许额外操作，扫描可合法，准确问题是成功率不足以识别语言依赖。
- Scholar HTTP200实际Verifying挑战页，result cards0，不算成功检索。SciSpace先发现8条metadata后工具被移除，不当全文证据。

保留为下一轮优先深审的测量问题；仍缺完整发布基准同预算攻击、成熟模型判断变化、独立核心增量与同题真机。
不继续堆纯组件反例替代这些门槛，不把首选择简单修正包装新方法。完整目标active，尚未确定方向。

## 21. 指令必要性后续：降为诊断工具，恢复任务问题发现

入口：`experiments/discovery/instruction-necessity-followup-20261115/README.md`。
§20的原始结果仍有效，但“下一轮优先深审”现被本节裁决更新。

- `2606.04233v1` §3/A.1/7–8已有shortcut-solvability审计；probe读取task index，不能称完全目标盲。
  其作者代码固定`a5ad04ab0f26d46680c4d1c24911c728d37f7d16`。
- `2611.08318v1` §3.2–3.4/4.2已有同episode双判据复评和优势变化；固定作者分支
  `62eb1ce1a9878512356a41631fba6c340f0a8db6`，只读入口，未运行其成绩。
- `1807.06757v1` PDF第3页§4已明确DONE时刻评分，反对到达目标即oracle成功；停止规则本身不能立新题。
- 新AST静态审计确认固定RoboOrchard环境step/reset返回terminated/truncated None，原loop把None当False。
  默认1000步/指定pick30Hz是代码默认，不是原论文预算；未运行完整Isaac/learned policy。
- “评分不忠实”与“合法共同轨迹使成功率无法识别语言依赖”不同；不把后者一律说成假成功。
  没有证据表明精确InstructMove反例已被同样发表，但当前也没有独立核心增量及成熟策略结论变化。

当前线暂移出主推荐，保留作载体诊断工具；不增加同类扫描或默认移植Isaac，不重启小BC。
只有完整原协议/同预算控制器证据改变成熟策略判断，并有独立贡献时，才重新开启该主张。
完整目标仍是确定可查新、可实现、有先进性的SO-101同题仿真—真机方向；尚未达成，不标complete/blocked。
