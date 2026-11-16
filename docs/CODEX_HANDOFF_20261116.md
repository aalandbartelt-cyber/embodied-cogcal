# Codex 交接：官方 ACT 能力筛查与下一步

**后续用户选择：B2（低成本触觉／力传感）已明确，新增预算 1 万元。**
暂按传感器、采集设备、夹具加工及独立校准参考全包含规划；预算不等于采购授权。
最新入口：[B2 预算与科学问题裁决](B2_BUDGET_DECISION_20261116.md)。SDI 已有接触力
实验的出版社预览；一般力反馈／门控、残差头建议和量化接触控制均有近邻。
没有候选取得 go；只保留微小力相关动作差异在哪一层消失的只读测量问题。
旧平台路线继续 no-go；仅恢复新传感平台的只读问题/来源审查。
见 [B2 首轮审查](B2_SENSOR_SCREEN_20261116.md)：材料/信息分离与一般力反馈宽题
已有覆盖；持续接触下的校准问题待核，未获 go。当前不采购、不改载体、不训练、
不重放 12100–12919、不预注册 order-robust；接口、近邻和信息条件仍待明确。
下文“未选择平台”的记录反映该次阶段报告之前的状态，不再描述本次选择。

**平台选择前的用户约束与交付（历史记录）：** 停止同平台搜索与训练，未选择平台变更。
本轮只整理 [阶段报告](report/STAGE_REPORT_20261116.md) 和既有证据；
不训练、不重跑 12100–12919、不预注册 order-robust。
后续须由用户明确选择第二只 SO-101 或低成本触觉/力传感，再审查问题与重新预注册。

日期：2026-11-16。交接对象：Codex 线程 `01a1d541-f599-7ec0-8e72-e53e68ae6395`。
Codex 额度再次用尽；本文件记录截至 **17:55** 的接续状态（含 13:29–14:27 的只读审计、
problem-rescreen 与换任务矩阵）。本文不是查新报告，不是 TPSC/补偿立项依据，也不是真机结果。

## 0. 当前状态（2026-11-16 17:30）

- 固定官方 ACT 能力筛查已完成：20 条 fresh seeds 12100–12119，**18/20 PASS**，
  独立物理审计 `passed=true`；最终 checkpoint 固定为 `final-20000.pt`。
- 事后机制诊断已完成：释放时 xy 误差仅 2.4–4.3 mm；失败由学到的成功后返回动作
  重新接触物体造成。oracle `freeze_open`（12300–12319）20/20；
  task-specific 夹爪命令检测器（12400–12419）也 20/20，最终 2.03–5.45 mm。
- **全文查新后，广义 post-completion / post-success 线 no-go：**
  Temporal Aliasing（AJoSR 2026）已有 release/retreat/stability/collision 证书；
  GR-BC（CoRL 2026）已对成功轨迹内 regressive chunks 做后果加权。
- **没有方向、没有查新通过、没有新方法、没有 TPSC/补偿/真机结论。**
- **action-chunking 窄线也已关闭**：PACE（2026）、Mixture of Horizons（2025）、
  Revisiting Open-Loop Execution（2026）已覆盖 phase-aware horizon/开环执行；
  execute30/10/6 的负结果和 chunk-consistency 证书也不成立。
- 额外负结果：execute30/10/6 在 12600–12619 上为 **19/20、7/20、0/20**；
  全局缩短执行步长没有消除释放后位移，反而破坏抓取/抬升。不要用“缩短 horizon”
  当修复，也不要重复该实验。
- **TPSC 也已 no-go**：CMTA（2023）已用 contrastive modules + temporal attention
  处理多任务负迁移；Sigma-Agent（2024）/AtomSkill（2025）已做多任务对比模仿与
  时序一致性。不要把共享/私有表示或对比分离当新方向。
- **认知偏差探针候选也已 no-go**：源偏移 19/20→1/20、遮挡 17/20→0/20 的试点
  确实存在，但 CorrectVLA 的 failure taxonomy 已覆盖 perception/target failure；
  SO-101 failure/recovery benchmark 已有 State Mismatch、Grasp Instability 和
  semantic/execution 分解（真实 SO-101/ACT）。该候选最多是细粒度诊断，不是新方向。
- **演示顺序线已 no-go**：canonical 17/19 vs reverse/random 13/13 只是 pilot；
  训练器从第 1 步起在全部 6,840 帧上均匀采样，换 episode 存储顺序只会重标固定的
  随机索引流，不是 curriculum/primacy/recency；reverse/random 的旧 `train_order.py`
  正文未保留，存在 provenance gap；双侧 p=0.0703，合并 Fisher p=0.0145
  不能作为确认证据。详见 `docs/DEMO_ORDER_MECHANISM_20261116.md` 与
  `experiments/discovery/demo-order-audit-20261116/`。
- **problem-rescreen 也已 no-go**：SO-101 actuator/dynamics/payload 被 NeuralActuator
  （RSS 2026）与 so101-rt-control 覆盖；action-interface 的离线检测/在线有限 probe
  被 Silent Interface（CoRL 2026 workshop）与 ActionABI/ActionShift 覆盖；伺服
  load/current + tube insertion 已有 SO-101 配对 A/B；failure/recovery 有 2606.08881v2；
  经典 drive-gain 有 Gautier & Briot ICRA 2012。详见
  `experiments/discovery/problem-rescreen-20261116/RESULT.md`。
- **2026-11-16 裁决：当前平台 no-go，停止同平台方向搜索与训练。**
  单臂 SO-101 + ACT + MuJoCo 的可行域已被反复覆盖；继续换模块/损失/任务名
  不会产生新方向。下一步是平台级决策（第二只 SO-101、低成本触觉/力传感，
  或先交付阶段报告），不是再跑一个单臂实验。详见
  [`RESEARCH_DIRECTION_DECISION_20261116.md`](RESEARCH_DIRECTION_DECISION_20261116.md)。
- **当前没有已通过门槛的方向。** 当前不要训练；不要重复 12100–12119、
  12200–12219、12300–12319、12400–12419、12600–12619、12700–12719、
  12800–12819、12900–12919 的实验。
- **不要重启训练或旧队列。** 终态以 `/proc`、`training/completed.json`、
  `pipeline-events.jsonl` 和实际输出文件为准，不以旧 WORKLOG/锁文件或历史 PID 重启。

## 1. 训练与管线状态

截至 09:44（本地）已完成：

- `train_act.py` 于 09:41:52 完成 20,000 updates，`training/completed.json` 已生成；
- `finish_pipeline.py` 自动执行评估与审计；
- `rollout.py` 20 条 fresh test 用时 96.97 s，`audit_act.py` 用时 1.37 s；
- `pipeline-events.jsonl` 的 `complete` 事件：`capability_gate=true`、`successes=18`；
- 最终 checkpoint：`checkpoints/official-act-20261116/final-20000.pt`（固定 final，不挑 best）；
  SHA256 `71439fda2a7ae13114f6930218a68280d3c7a51c857385907d21e4bfd3cb6f26`；
- `training/completed.json`：`training_step=20000`、`test_used=false`、`novelty=not_established`；
- 训练 2536.76 s；最终验证集 normalized L1 0.06602；CUDA 峰值 allocated 2.356 GB。

## 2. 结果

**Decision: PASS**（18/20，gate ≥16/20；独立审计 `passed=true`）。

- 测试 seeds 12100–12119，均为 fresh；未用训练/验证 seeds。
- 18/20 成功；失败为 12100（36.25 mm）与 12112（37.71 mm），
  两条均为 `placement_not_achieved`；20/20 均完成双指抬升与释放。
- 独立审计：`successes_recomputed=18`、`commands=5700`、`full_chunk_queries=200`、
  `audit_sha256=ee834970ea5d5fa10e347f8e55405b6369761c98dcb824938c98543504a8e478`。
- 逐 seed 表、失败原因和产物见
  [`experiments/discovery/official-act-20261116/ACT_RESULT.md`](../experiments/discovery/official-act-20261116/ACT_RESULT.md)。

这不是方向、不是查新通过、不是 TPSC/补偿证据，也不是真机结果；
它只说明该固定 ACT 配置在单一匹配任务上可作为可干预的 learned actor。

## 3. 固定配置与证据

- 官方 LeRobot 0.4.3，source revision `0b067df57d21d3a02d6c511f1609172fa39ac29b`。
- 数据：`data/discovery/matched-bc-lowrate-20261114/`，24 train seeds 4100–4123，
  8 val seeds 5100–5107；每条 285 步、30 Hz，双 RGB 128×128（5 Hz 采集、age 0–5 控制步），
  六维绝对关节 rad。
- 训练：ACT 51,597,190 参数；ResNet18 ImageNet1K_V1；dim 512、8 head、FF 3200、
  encoder 4、decoder 1、VAE latent 32/encoder 4、KL 10、dropout 0.1；
  n_obs_steps 1，horizon 100，execute 30；L1 + KL，AdamW lr 1e-5，weight_decay 1e-4，
  grad clip 10；固定 20k，无 AMP、无 LR search、无 temporal ensemble。
- 评估：策略只读当前双 RGB + measured q（rad），不读 GT object pose；
  每 30 控制步查询一次；query 时 RGB fresh；仿真在模型计算时暂停。
- 成功谓词：最终 xy ≤ 35 mm、z 容差 12 mm、释放 ≥ 0.1 s、双指持物抬升 ≥ 0.5 s、
  最大穿透 ≤ 1.5 mm。
- 审计：`audit_act.py` 复算谓词、检查 source/checkpoint/trace hash、控制/物理时钟、
  clip 与 object pose 写入；不依赖 episode 标签。

## 4. 判定规则

- **PASS**：`successes_recomputed >= 16/20` 且 audit `passed=true`。
  这只说明该固定 ACT 配置在单一匹配任务上可用，是可干预的 learned actor；
  **不是新方法、不是方向、不是查新通过，也不是 TPSC/补偿证据。**
- **NOT READY**：`<16/20`。停止该配置；不要在同一测试 seed 上调架构、horizon、seed
  或放宽成功谓词；不要从失败中提炼“执行精度/阶段线索”结论。
- 无论 PASS 还是 NOT READY，完整研究目标仍 active；尚未确定方向。

## 5. 下一步（按结果分支）

### 5.1 若 PASS

1. 把 ACT 作为**有能力载体**，固定 checkpoint/processor/contract；
2. 先读已完成的
   [`post-release-20261116/RESULT.md`](../experiments/discovery/post-release-20261116/RESULT.md)：
   该诊断发现 ACT 在首次释放时 xy 误差仅 2.4–4.3 mm，但学到的“放后返回”动作
   重新碰到物体，额外造成 15.6–161.3 mm 位移；冻结手臂、只让夹爪张开后，
   同 seeds 从 18/20 提升到 20/20，最终 xy 误差 1.97–3.94 mm。
3. **广义 post-completion 线已 no-go**：Temporal Aliasing 2026 已有
   release/retreat/stability/collision 证书并处理 re-grasp/push；GR-BC 2026 已有
   成功轨迹内 regressive chunk 的后果加权。不要再用“成功后动作被模仿”作为核心。
4. 原先考虑的窄差异是 **action chunking 的测试时执行/截断**：ACT 预测 100 步、
   执行 30 步，最后一个 query 的 chunk 已包含成功后返回；Temporal Aliasing 无 chunking，
   GR-BC 是离线权重而非测试时截断。但 PACE（2026）已做 phase-aware chunk execution，
   Mixture of Horizons/Revisiting Open-Loop Execution 已覆盖 horizon/开环执行。
   额外负结果：execute30/10/6 在 12600–12619 为 19/20、7/20、0/20；全局缩短
   horizon 不是修复，反而破坏抓取/抬升。
5. action-chunking 窄线已关闭：全局缩短 horizon 不是修复，简单的 chunk-consistency
   证书也不能预测失败；不要再用 12500–12519 做 success-aware truncation，除非能先
   给出一个新的、未被 PACE/GR-BC 覆盖的可测信号。不要做训练时 post-success mask。
6. **TPSC 也已 no-go**：CMTA 2023（contrastive modules + temporal attention）、
   Sigma-Agent 2024、AtomSkill 2025 已覆盖核心组合；不要构建 paired-task carrier。
7. 不把“ACT 通过”当方向成立，也不把“更早停止”或 task-specific 检测器直接当创新；
   更新 `RESEARCH_READINESS.md` 与 handoff。

### 5.2 若 NOT READY

1. 记录失败原因分布（placed/released/lift/penetration）；
2. 停止该配置，不调参；
3. 寻找不同的、有成功见证的能力载体或任务；
4. 不从失败中反推 TPSC/补偿假设。

## 5A. 2026-11-16 事后机制诊断（已完成）

### 5A.1 预注册与实现检查

- `experiments/discovery/post-release-20261116/PREREG.md`：在 12200–12219 之前冻结。
- 第一版 `freeze`（手臂和夹爪全部保持）在 12200–12219 得到 0/20，
  原因全是 `release_not_verified`：夹爪停在半闭位置，谓词要求 ≥0.1 s 无机器人接触。
  但最终 xy 误差仅 2.85–5.21 mm，说明释放位置本身很准；这是实现检查，不是主测试。
- `PREREG_ADDENDUM.md`：在看到 12200–12219 结果后、跑 12300–12319 之前冻结修正条件：
  **手臂关节 0–4 保持，仅夹爪继续张开**（`freeze_open`）。

### 5A.2 主测试（fresh seeds 12300–12319）

同 checkpoint、同物理、同谓词；基线 vs `freeze_open` 同 seed 配对：

| 指标 | baseline | freeze_open |
|---|---:|---:|
| 最终成功 | 18/20 | **20/20** |
| 最终 xy 误差均值 | 29.83 mm | **2.97 mm** |
| 最终 xy 误差范围 | 14.36–163.74 mm | **1.97–3.94 mm** |
| 首次释放时 xy 误差 | 3.39 mm | 3.39 mm（逐 seed 完全相同） |
| 释放后位移均值 | 30.35 mm | **0.65 mm** |
| 释放后位移范围 | 15.57–161.34 mm | **0.35–1.07 mm** |
| 配对最终误差改善 | — | **20/20 seeds** |

单侧符号检验 $p=2^{-20}\approx9.5\times10^{-7}$。基线失败为 12300（54.24 mm）
与 12307（163.74 mm），`freeze_open` 均成功。

### 5A.2b 可部署检测器（fresh seeds 12400–12419）

oracle 检测器不可部署，因此另写 `PREREG_DEPLOY.md` 并在跑 12400–12419 前冻结：
仅用**夹爪命令**，`command[5] <= 0.13` 连续 ≥20 步后，首次 `>=0.15` 触发；
随后保持手臂 0–4、夹爪继续张开。阈值来自合格 teacher 的 `CLOSE_Q=0.12`、
`APPROACH_Q=0.28`；close→open 模式在已用 12300–12319 轨迹上检查过，已披露。

同 checkpoint、同谓词、同 seed 配对：

| 指标 | baseline | deployable freeze |
|---|---:|---:|
| 最终成功 | 18/20 | **20/20** |
| 最终 xy 误差均值 | 26.89 mm | **3.68 mm** |
| 最终 xy 误差范围 | 16.00–44.06 mm | **2.03–5.45 mm** |
| 首次释放时 xy 误差 | 4.00 mm | 4.00 mm（逐 seed 相同） |
| 释放后位移均值 | 26.70 mm | **0.58 mm** |
| 配对最终误差改善 | — | **20/20 seeds** |
| 检测触发相对释放 | — | −1 到 +1 控制步 |

基线失败 12400（43.99 mm）与 12406（44.06 mm）在检测器下均成功。
这是 **task-specific feasibility diagnostic**，不是通用成功检测器、不是新方法、
不是查新通过；它只说明“仅用本体命令就足以在这个任务上触发停手”。

### 5A.3 解释与边界

- 两条件在释放前逐 seed 完全一致；释放时 xy 误差都是 2.4–4.3 mm。
  最终差异只能来自释放后的手臂行为，因此这是一个干净的因果诊断。
- 失败不是“放置精度不足”，而是**模仿了演示中的成功后返回动作**；
  该动作重新接触物体并把已完成的放置推走。
- 12300–12319 的 oracle 主测试使用仿真接触状态，不可部署；
  12400–12419 的夹爪命令状态机是 **task-specific 可部署诊断**，但不是通用成功检测器。
  没有训练时方法、没有新策略、没有 TPSC、没有精度补偿、没有真机。
- 候选研究方向只能是：**如何区分任务相关动作与成功后演示动作，
  以及如何在没有特权状态时检测任务完成**。**但全文查新后广义线已 no-go**：
  Temporal Aliasing 2026 已覆盖 release/retreat/stability/collision 证书；
  GR-BC 2026 已覆盖成功轨迹内 regressive chunk 的后果加权。
- 可部署检测器在 12400–12419 与 oracle 上界同为 20/20，说明该任务上
  **本体命令足够**；但这依赖演示的 close→open 模式，不能外推到其他任务。
  它是工程可行性，不是独立科学增量。
- 唯一可能的窄差异是 **action chunking 的测试时执行/截断**；但 PACE 已做
  phase-aware chunk execution，Mixture of Horizons/Revisiting Open-Loop Execution
  已覆盖 horizon/开环执行，窄线很可能 no-go，不能立项。

## 5B. 查新裁决（2026-11-16）

- **广义 post-completion：no-go。** 两篇直接近邻：
  - Temporal Aliasing（AJoSR 2026）：六谓词 `lift ∧ cross ∧ release ∧ retreat ∧
    stability ∧ ¬collision`，明确写“到达目标不等于 release/retreat/stability/
    collision-free”；stability 在 re-grasp/push 时清零。
  - GR-BC（CoRL 2026，arXiv 2610.20504）：标准 SFT 会把成功轨迹里的 regressive
    chunks 当正样本；用 goal-reachability 后果加权压制。
- **窄线已关闭：** action chunking 的测试时执行/截断。PACE（2026）已做 phase-aware
  chunk execution，Mixture of Horizons、Revisiting Open-Loop Execution 已覆盖
  horizon/开环执行。额外负结果（12600–12619）：execute30/10/6 = 19/20、7/20、0/20；
  全局缩短 horizon 没有消除返回，反而破坏抓取/抬升；chunk 重叠/边界跳变/跟踪误差
  也不能预测失败（execute6 指标更低是因为更早失败）。**窄线 no-go。**
- **TPSC 也已 no-go：** CMTA（2023）已用 contrastive modules + temporal attention
  处理负迁移/任务内冲突；Sigma-Agent（2024）与 AtomSkill（2025）已做多任务对比模仿
  与语义-时序一致性。不要构建 paired-task carrier 或训练 TPSC。
- 详见 [`prior-art/post-completion-action-scan-20261116.md`](prior-art/post-completion-action-scan-20261116.md)
  与 [`prior-art/tpsc-scan-20261116.md`](prior-art/tpsc-scan-20261116.md)。
- 在窄线查清前，不得训练、不得声称方向成立；窄线不过就做新问题搜索/换任务。

## 5C. 窄线也 no-go 之后：TPSC 已 no-go，需要新问题

- TPSC（shared-prefix vs uniform task separation）**已 no-go**：
  CMTA 2023 已用 contrastive modules + temporal attention 处理负迁移/任务内冲突；
  Sigma-Agent 2024 与 AtomSkill 2025 已做多任务对比模仿与语义-时序一致性。
- 当前 ACT 是单任务；TPSC 场景的 scripted physics grasp 仍 0/20。
  没有 paired-task learned carrier，也没有可复现的 TPSC 现象。
- **不要构建 paired-task carrier，不要训练 TPSC。**
- 当前诚实状态：**没有方向通过选题门槛；完整目标仍 active。**
- 当前问题空间（post-completion、action-horizon、TPSC、接触丰富装配、相机标定、
  多物体、长时序、恢复）均已找到强近邻；接触丰富装配还有 CompVLA/TLA/UniTacVLA/
  TacVLA 等 2026 工作。**继续换模块名/损失/任务名不会产生新方向。**
- **演示顺序线已 no-go，见 §5D**；它不是 curriculum 候选，也不再是“待核例外”。
- **认知偏差探针候选也已 no-go**：试点见
  [`RESULT_SOURCE_SHIFT.md`](../experiments/discovery/source-shift-20261116/RESULT_SOURCE_SHIFT.md)
  与 [`RESULT_OCCLUSION.md`](../experiments/discovery/occlusion-20261116/RESULT_OCCLUSION.md)。
  现象存在（视觉存在门控 vs 空间锚定），但 **CorrectVLA 2026** 的 failure taxonomy
  已覆盖 perception/target failure；**SO-101 failure/recovery benchmark** 已有
  State Mismatch、Grasp Instability 和 semantic/execution 分解。
- 该候选最多是已有 taxonomy 下的细粒度诊断，不是新方向；不要构建 benchmark、不要训练。
- 下一步是重新定义研究问题/任务；新问题候选与准入条件见
  [`NEXT_PROBLEM_SEARCH_20261116.md`](NEXT_PROBLEM_SEARCH_20261116.md)。

## 5D. 演示顺序线：no-go（只读审计完成）

- 问题：同一 24 条示教、同一 seed/20k/最终 checkpoint，只改训练顺序
  （canonical / reverse / random），ACT 的成功率是否改变？
- 观察：canonical 官方 17/20、canonical 同环境重训 19/20；reverse 13/20、
  random 13/20。canonical-retrain vs reverse/random 单侧 McNemar p=0.0352；
  合并 canonical 36/40 vs 非 canonical 26/40 Fisher p=0.0145。**但**：
  - 训练器从第 1 步起在全部 **6,840 帧**上均匀采样；episode 存储顺序只改变
    固定随机索引流的标签，不是 curriculum、primacy 或 recency；
  - 24 条 episode 等长（285 步），置换不改变相位序列；teacher descriptor
    没有显示 canonical 与难度/阶段的对应；
  - reverse/random 训练合同引用的旧 `train_order.py` 正文未保留，存在
    **provenance gap**；checkpoint/evaluation hash 匹配不等于训练源等价；
  - 单侧 p=0.0352 对应双侧 **p=0.0703**；合并 Fisher p=0.0145 是事后合并，
    不是确认性检验；canonical 17/19 vs 13/13 只是 pilot。
- **裁决：no-go。** 不预注册 order-robust 训练，不训练新方法，不再用
  12900–12919 做顺序实验。
- 证据：`experiments/discovery/demo-order-audit-20261116/`（`verify.py` 只读复跑
  `verification-final.json`，545 个冻结输入未变）；机制 memo
  `docs/DEMO_ORDER_MECHANISM_20261116.md`；查新
  `docs/prior-art/demo-order-scan-20261116.md`。

## 5E. Problem-rescreen 与换任务矩阵：no-go（2026-11-16 17:55）

在 demo-order 关闭后，Codex 于 14:18–14:27 启动
`experiments/discovery/problem-rescreen-20261116/`，抓取了 actuator/dynamics、
payload、action-interface、tube insertion、failure/recovery 与经典 drive-gain
来源；额度在写裁决前用尽。本轮接续完成只读裁决：

| 候选 | 最近来源 | 覆盖 | 裁决 |
|---|---|---|---|
| SO-101 actuator/dynamics/payload | NeuralActuator（RSS 2026，SO-101/OMX，450 任务，torque-label-free、external force）；so101-rt-control（payload RLS、static mass ID、200 Hz、sim-real gap）；TeAR（actuator degradation test-time adaptation） | 平台、payload、actuator 与 sim-real 问题均直接覆盖 | **no-go** |
| action-interface mismatch / closed-loop mitigation | Silent Interface（CoRL 2026 workshop：离线 detection/localization；exact repair 0/10；simulated mitigation fail）；ActionABI/ActionShift（离线等价类/校准拒绝 + 在线有限 probe，grammar 含 permutation/sign/scale/target/frame/lag/gripper）；Same Weights（部署合同/静态 drift certificate） | 在线 probe 已覆盖；“task success”只是评估扩展，不是新机制 | **no-go** |
| 伺服 load/current + tube insertion | FaithQin/so101-tube-insertion（Apache-2.0，2026-11-04）：servo load/current 是否帮助 SO-101 插入试管的 paired A/B + failure taxonomy | 问题与平台均已配对研究 | **no-go**（README 因 TLS 失败未读，只依 metadata/hash） |
| failure/recovery | SO-101 failure/recovery benchmark（2606.08881v2）；CorrectVLA taxonomy | 已有 State Mismatch、Grasp Instability、semantic/execution 与 recovery | **no-go** |
| demo-order | 独立审计 + 均匀采样重建 | 无 curriculum 操作；provenance gap；pilot 不确认 | **no-go** |
| classical drive gains | Gautier & Briot, ICRA 2012（known payload 的 drive-gain 全局辨识） | 经典 sysid 已覆盖 | **no-go** |
| 换任务：动态抛掷/接取 | AthenaZero（Science Robotics 2026）、Robot Juggling（2026） | 双臂/高速硬件与在线学习已覆盖 | **no-go** |
| 换任务：颗粒/液体舀取/倾倒 | RoboCAP、Matl et al. ICRA 2020、Alloy（2026） | 专用传感/材料推理/多材料仿真已覆盖 | **no-go** |
| 换任务：DLO 布线 | SILO（2026）、WireCraft（CoRL 2026 Spotlight） | sim-to-real、benchmark、ACT/VLA 评估已覆盖 | **no-go** |

- **结论：没有候选通过门槛；当前单臂 pick-place/insertion/assembly 问题空间已饱和。**
  继续换模块名、损失或任务名不会产生新方向。
- 下一步不是训练，也不是继续在同平台换任务名；而是**平台级决策**。新候选必须先过
  [`RESULT.md`](../experiments/discovery/problem-rescreen-20261116/RESULT.md)
  的 7 条准入条件（capable carrier、causal mechanism、非覆盖、强简单对照、
  同题 sim-real、bounded falsifier、先证据后命名）。
- **换任务矩阵已填并 no-go**：动态抛掷/接取被 AthenaZero（Science Robotics 2026）、
  Robot Juggling（2026）等双臂/高速工作覆盖；颗粒/液体舀取/倾倒被 RoboCAP、
  Matl et al. ICRA 2020、Alloy（2026）覆盖；DLO 布线被 SILO（2026）、WireCraft
  （CoRL 2026 Spotlight）等 sim-to-real/benchmark 覆盖。三者都要求双臂/高速、
  专用传感或可变形仿真/夹具，当前单 SO-101 不是 capable carrier。
- 矩阵与来源：
  [`DECISION_MATRIX.md`](../experiments/discovery/task-change-20261116/DECISION_MATRIX.md)、
  [`SOURCE_NOTES.md`](../experiments/discovery/task-change-20261116/SOURCE_NOTES.md)、
  [`FEASIBILITY.md`](../experiments/discovery/task-change-20261116/FEASIBILITY.md)。
  只作筛选，不是训练计划。
- **默认行动：阶段报告/负结果整理，不训练。** 第二只 SO-101（B1）或低成本
  触觉/力传感（B2）只是未来可选路径，需明确硬件/预算授权后重新预注册；不得把
  新硬件当隐含前提，也不得为了“有方向”给已覆盖问题改名。

## 6. 硬约束

- 不重启训练或旧队列；终态以实际进程/日志/输出为准。
- 不用测试 seed 调参或挑 checkpoint。
- 12100–12119（能力筛查）、12200–12219（实现检查）、12300–12319（主诊断）、
  12400–12419（可部署检测器）、12600–12619（执行长度诊断）、12700–12719（源偏移）、
  12800–12819（遮挡）、12900–12919（演示顺序）已经使用；不得再用它们调阈值、
  选 seed、挑 checkpoint 或做新方法测试。13000–13019 仍未使用。
- `freeze_open`（12300–12319）使用仿真接触，是 **oracle diagnostic**；
  `freeze_open_deploy`（12400–12419）是 **task-specific 命令状态机**，不是通用方法；
  两者都不得写成查新通过或新方法成绩。
- 不声称 TPSC 已立项/查新通过；不把 A100/VLA 失败归因于 TPSC。
- 不把 post-release 诊断当作方向成立；广义 post-completion、action-chunking 窄线、
  TPSC、认知偏差探针、demo-order、problem-rescreen 与换任务矩阵候选均已 no-go。
- **停止同平台方向搜索与训练**；下一步只在用户明确选择平台变更（第二只 SO-101、
  低成本触觉/力传感）后，重新预注册。不要把新硬件/新仿真器作为隐含前提。
- 不混用单任务 ACT 结果与 TPSC 的 shared-prefix 主张。
- 不要再用 actuator/dynamics/payload、action-interface、servo-current insertion、
  failure/recovery 或 drive-gain 作为“新方向”，除非能给出超出已读来源的
  具体机制与 falsifier；模块名/损失/任务名改写不算。
- 不改 `third_party/SO-ARM100` 官方 XML、受保护 JSON/manifest 或旧结果。
- 所有新结果写入 fresh 目录，保留原始 trace/physics/hash。

## 7. 当前文件

- `experiments/discovery/official-act-20261116/PLAN.md`：冻结计划。
- `training/contract.json`、`training.stdout.txt`、`training/updates.jsonl`。
- `finish_pipeline.py`、`rollout.py`、`audit_act.py`、`report_result.py`。
- 结果：`test/`、`independent-audit-v1.json`、`pipeline-events.jsonl`、`ACT_RESULT.md`。
- 事后诊断：`../post-release-20261116/PREREG.md`、`PREREG_ADDENDUM.md`、
  `PREREG_DEPLOY.md`、`RESULT.md`、`rollout_post_release.py`、`paired-release.json`、
  `paired-deploy.json`、`baseline-12300/`、`freeze-open-12300/`、`baseline-12400/`、
  `freeze-open-deploy-12400/`；12200–12219 的 `baseline/`、`freeze/` 是实现检查。
- 查新：`docs/prior-art/post-completion-action-scan-20261116.md`（广义 no-go）、
  `docs/prior-art/tpsc-scan-20261116.md`（TPSC no-go）。
- 执行长度负结果：`../execute-horizon-20261116/PREREG.md`、`RESULT_EXECUTE.md`、
  `rollout_execute.py`、`execute30/`、`execute10/`、`execute6/`。
- 认知偏差探针试点：`../source-shift-20261116/`、`../occlusion-20261116/`；
  候选 memo `docs/prior-art/cognitive-bias-probe-candidate-20261116.md`。
- 演示顺序探针：`../demo-order-20261116/PREREG.md`、`train_order.py`、
  `rollout_order.py`、`analyze_order.py`、`canonical/`、`reverse-solo/`、`random-solo/`、
  `canonical-retrain/`、`canonical-retrain-eval/`、`order-analysis-retrain.json`；查新
  `docs/prior-art/demo-order-scan-20261116.md`。
- 新问题搜索：`docs/NEXT_PROBLEM_SEARCH_20261116.md`。
- problem-rescreen：`experiments/discovery/problem-rescreen-20261116/README.md`、
  `source-fetch*.json`、`RESULT.md`（no-go，7 条准入条件）。
- task-change 矩阵：`experiments/discovery/task-change-20261116/`（no-go）。
- 方向裁决：`docs/RESEARCH_DIRECTION_DECISION_20261116.md`（停止同平台搜索，
  平台级决策）。
- 交接/提示词：本文件 + `docs/CODEX_PROMPT_20261116.md`。
