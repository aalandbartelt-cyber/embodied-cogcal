# Codex 接续提示词（2026-11-16 17:55，demo-order、rescreen 与换任务矩阵均 no-go）

用途：Codex 额度恢复后，直接把下面“可粘贴提示词”交给线程
`01a1d541-f599-7ec0-8e72-e53e68ae6395`。旧提示词已归档为
[`CODEX_PROMPT_20261116_superseded.md`](CODEX_PROMPT_20261116_superseded.md)，
不要再按旧提示词追演示顺序候选。

## 可粘贴提示词

> 你是本项目的接续研究代理。先不要训练、不要改任何已有结果、不要重跑已用 seeds。
> 项目总目标仍是：找到一个能过查新、可行、有先进性的 SO-101 同题研究方向；
> “认知偏差/工业精度补偿”只是启发，不是新颖性证明。
>
> **但当前已经作出裁决：单臂 SO-101 + ACT + MuJoCo 平台 no-go，停止同平台搜索。
> 你不要再自行寻找新方向/新任务/新模块；本轮只做只读核验、阶段报告/负结果整理，
> 并等待用户明确选择平台变更（第二只 SO-101、低成本触觉/力传感）后再重新预注册。**
>
> **0. 先读，不要先跑**
> 依次读：
> - `docs/CODEX_HANDOFF_20261116.md`（最新交接，含 §5D/§5E）
> - `docs/DEMO_ORDER_MECHANISM_20261116.md`
> - `experiments/discovery/demo-order-audit-20261116/README.md`
> - `experiments/discovery/problem-rescreen-20261116/RESULT.md`
> - `docs/RESEARCH_READINESS.md`
> - `docs/NEXT_PROBLEM_SEARCH_20261116.md`
>
> **1. 当前事实（不要重新争论）**
> - 官方 ACT 在 fresh seeds 12100–12119 为 18/20，独立审计 passed=true；
>   这只是**有能力载体**，不是方向，不是查新通过。
> - post-release 诊断：释放时 xy 2.4–4.3 mm，成功后返回动作导致 14–164 mm
>   最终误差；oracle freeze_open 20/20，夹爪命令状态机 20/20。广义
>   post-completion 已被 Temporal Aliasing 2026 / GR-BC 2026 覆盖，**no-go**。
> - action-horizon 窄线 **no-go**：execute30/10/6 = 19/20、7/20、0/20；
>   全局缩短 horizon 反而破坏抓取/抬升；PACE 等已覆盖 phase-aware 执行。
> - TPSC **no-go**：CMTA/Sigma-Agent/AtomSkill 已覆盖对比模块/时序一致性；
>   当前 ACT 是单任务，scripted paired-task grasp 仍 0/20。
> - 认知偏差探针 **no-go**：源偏移 19/20→1/20、遮挡 17/20→0/20 的现象存在，
>   但 CorrectVLA taxonomy 与 SO-101 failure/recovery benchmark 已覆盖。
> - **demo-order 线 no-go**：canonical 17/19 vs reverse/random 13/13 只是 pilot；
>   训练器从第 1 步起在全部 6,840 帧上均匀采样，episode 存储顺序只重标固定
>   随机索引流，不是 curriculum/primacy/recency；等长 episode 不改变相位序列；
>   旧 `train_order.py` 正文未保留，provenance gap；单侧 p=0.0352 对应双侧
>   p=0.0703，合并 Fisher p=0.0145 不是确认性检验。不要预注册 order-robust
>   训练，不要再用 12900–12919。
> - **problem-rescreen 也 no-go**：SO-101 actuator/dynamics/payload 被
>   NeuralActuator（RSS 2026）与 so101-rt-control 覆盖；action-interface 的
>   离线 detection/localization 被 Silent Interface（CoRL 2026 workshop）覆盖，
>   在线有限 probe 被 ActionABI/ActionShift 覆盖；Silent Interface 的 exact
>   repair 0/10、simulated mitigation fail；伺服 load/current + tube insertion
>   已有 SO-101 配对 A/B；failure/recovery 有 2606.08881v2；经典 drive-gain 有
>   Gautier & Briot ICRA 2012。**当前单臂 pick-place/insertion/assembly 问题空间
>   已饱和，继续换模块名/损失/任务名不会产生新方向。**
> - **当前没有方向通过门槛。** 完整目标仍 active。
>
> **2. 只读核验（不训练）**
> - 运行 `env -u PYTHONPATH PYTHONNOUSERSITE=1 /home/mary/miniconda3/envs/cogcal/bin/python \
>   experiments/discovery/demo-order-audit-20261116/verify.py`，确认 545 个冻结输入
>   未变、四张评分表可复算、provenance warnings=2；不要覆盖已有 JSON。
> - 抽查 `problem-rescreen-20261116/source-fetch*.json` 的 URL/SHA-256 与
>   `RESULT.md` 的候选表；不要下载权重、不要执行上游代码、不要跑策略。
> - 写下：`ACT 18/20`、`post-release`、`demo-order`、`rescreen` 都只是
>   载体/诊断/负结果，不是方向。
>
> **3. 换任务矩阵已完成，no-go；停止搜索**
> 先读：
> - `docs/RESEARCH_DIRECTION_DECISION_20261116.md`
> - `experiments/discovery/task-change-20261116/DECISION_MATRIX.md`
> - `experiments/discovery/task-change-20261116/SOURCE_NOTES.md`
> - `experiments/discovery/task-change-20261116/FEASIBILITY.md`
>
> 已筛的三个家族全部 no-go：
> - 动态抛掷/接取：AthenaZero（Science Robotics 2026）、Robot Juggling（2026）
>   等双臂/高速工作覆盖；当前单 SO-101 不是 capable carrier。
> - 颗粒/液体舀取/倾倒：RoboCAP、Matl ICRA 2020、Alloy（2026）覆盖；
>   需要专用传感或材料仿真。
> - DLO 布线：SILO（2026）、WireCraft（CoRL 2026 Spotlight）等 sim-to-real/
>   benchmark 覆盖；需要可变形仿真、夹具和线缆状态估计。
>
> **不要重做这三个矩阵，不要换名保留，也不要继续搜索单臂模块变体。**
> 当前裁决是：**停止同平台方向搜索与训练；下一步只在用户明确选择平台变更
> （第二只 SO-101、低成本触觉/力传感）后重新预注册。** 若用户没有选择平台变更，
> 直接报告“当前资源下没有可行方向”，并把阶段报告/负结果整理好。
>
> **4. 产出**
> 矩阵文件已存在；不要新建训练计划、不要下载权重、不要跑上游代码。最后更新
> `docs/CODEX_HANDOFF_20261116.md`、`docs/RESEARCH_READINESS.md`、
> `docs/NEXT_PROBLEM_SEARCH_20261116.md`，写清“方向裁决：当前平台 no-go，
> 等平台决策”。
>
> **硬约束**
> - 不重启旧训练/旧队列；不改 `third_party/SO-ARM100` 官方 XML、受保护 manifest、
>   冻结 contract/checkpoint 或旧结果。
> - 12100–12119、12200–12219、12300–12319、12400–12419、12600–12619、
>   12700–12719、12800–12819、12900–12919 已烧掉；13000–13019 仍未使用，
>   但本轮不训练。
> - `freeze_open` 是 oracle；夹爪命令状态机是 task-specific；20/20 不是新方法成绩。
> - 不把 ACT 能力通过、post-release 诊断、demo-order pilot 或任何单一 seed 结果
>   当成方向/查新通过。
> - 所有新结果写 fresh 目录，保留 hash、stdout、失败原因和完整证据。
>
> **一句话**：demo-order、problem-rescreen 和三个换任务家族都已 no-go；不要再在
> 单臂 pick-place/insertion/assembly 上换模块，也不要把双臂/专用传感/新仿真器
> 当隐含前提。没有新的单臂桌面机制，就诚实报告“当前资源下没有可行方向”。

## 给用户的短版（如果只想发一段）

> 先读 `docs/CODEX_HANDOFF_20261116.md`、`docs/DEMO_ORDER_MECHANISM_20261116.md`、
> `experiments/discovery/demo-order-audit-20261116/README.md` 和
> `experiments/discovery/problem-rescreen-20261116/RESULT.md`。
> demo-order 已 no-go（均匀采样、无 curriculum、provenance gap、双侧 p=0.0703）；
> problem-rescreen 也已 no-go（NeuralActuator/so101-rt 覆盖 actuator/payload，
> Silent Interface + ActionABI/ActionShift 覆盖 interface，SO-101 tube insertion
> 覆盖 servo-current，2606.08881v2 覆盖 failure/recovery）。不要训练、不要重跑
> 12100–12919、不要预注册 order-robust。换任务矩阵也已 no-go（动态抛掷/接取、
> 颗粒/液体舀取/倾倒、DLO 布线均被双臂/高速、专用传感或可变形仿真/benchmark
> 覆盖）。当前裁决是 **停止同平台搜索与训练**；下一步只在用户明确选择平台变更
> （第二只 SO-101、低成本触觉/力传感）后重新预注册，否则报告“当前资源下没有
> 可行方向”并整理阶段报告。

## 交接时最重要的三句话

1. ACT 18/20 只说明载体可用；post-release/demo-order/rescreen 都是诊断或负结果，
   不是方向。
2. demo-order 是均匀采样下的 pilot，不是 curriculum；双侧 p=0.0703，且有
   provenance gap，不能预注册 order-robust。
3. 单臂 pick-place/insertion/assembly 的 actuator、interface、servo-current、
   failure/recovery 都已有直接近邻；动态/颗粒/DLO 三个换任务家族也已 no-go。
   当前资源下没有可行方向；停止同平台搜索，下一步是平台决策或阶段报告。
