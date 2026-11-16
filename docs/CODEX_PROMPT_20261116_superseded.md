# Codex 接续提示词（2026-11-16，13:10 后）

用途：Codex 额度恢复后，直接把下面“可粘贴提示词”交给线程
`01a1d541-f599-7ec0-8e72-e53e68ae6395`。交接事实与文件索引见
[`CODEX_HANDOFF_20261116.md`](CODEX_HANDOFF_20261116.md)。

## 可粘贴提示词

> 你是本项目的接续研究代理。先不要训练、不要改任何已有结果，按顺序完成下面任务。
> 项目目标仍是：找到一个能过查新、可行、有先进性的 SO-101 同题研究方向；
> “认知偏差/工业精度补偿”只是启发，不是新颖性证明。
>
> **0. 先读，不要先跑**
> 依次读：
> - `docs/CODEX_HANDOFF_20261116.md`
> - `experiments/discovery/official-act-20261116/ACT_RESULT.md`
> - `experiments/discovery/post-release-20261116/PREREG.md`
> - `experiments/discovery/post-release-20261116/PREREG_ADDENDUM.md`
> - `experiments/discovery/post-release-20261116/RESULT.md`
> - `experiments/discovery/post-release-20261116/paired-release.json`
> - `docs/RESEARCH_READINESS.md`
>
> **1. 只读核验已有结果**
> - 确认官方 ACT：20 条 fresh seeds 12100–12119，18/20，audit passed=true，
>   `successes_recomputed=18`，checkpoint SHA `71439fda...`。
> - 确认 post-release 主测试：fresh seeds 12300–12319，baseline 18/20，
>   `freeze_open` 20/20；逐 seed 首次释放误差完全相同（2.4–4.3 mm）；
>   最终误差 29.83→2.97 mm；释放后位移 30.35→0.65 mm；20/20 配对改善。
> - 确认 12400–12419 的夹爪命令状态机：baseline 18/20 → 20/20，最终
>   2.03–5.45 mm；这是 task-specific feasibility，不是通用方法。
> - 确认 12600–12619 的执行长度负结果：execute30/10/6 = 19/20、7/20、0/20；
>   全局缩短 horizon 没有消除释放后位移，反而破坏抓取/抬升。不要重复该实验。
> - 用你独立的脚本复算 `paired-release.json`、`paired-deploy.json` 的关键统计；
>   不要重跑 12100–12119、12200–12219、12300–12319、12400–12419、12600–12619 的策略，
>   不要用这些 seeds 调任何东西。
> - 明确写下：`freeze_open` 使用仿真接触，是 oracle；命令状态机是 task-specific；
>   ACT 通过只是载体资格，不是方向/查新结论。
>
> **2. 核验已完成的查新结论，只保留 action-chunking 窄线**
> 2026-11-16 已做标题/摘要级扫描，并读完两篇直接近邻：
> - **Temporal Aliasing**（AJoSR 2026）：六谓词
>   `lift ∧ cross ∧ release ∧ retreat ∧ stability ∧ ¬collision`；明确写
>   “到达目标不等于 release/retreat/stability/collision-free”；stability 在
>   re-grasp/push 时清零。
> - **GR-BC**（CoRL 2026，arXiv 2610.20504）：标准 SFT 会把成功轨迹里的
>   regressive chunks 当正样本；用 goal-reachability 后果加权压制。
>
> 你的任务不是重做广义扫描，而是：
> 1. 用原文核验这两条，确认引用、页码和覆盖边界；
> 2. 在 `docs/prior-art/post-completion-action-scan-20261116.md` 中把
>    **广义 post-completion 明确标为 no-go**；
> 3. 只查一个窄线：**action chunking 的测试时执行/截断**。必读
>    PACE（arXiv 2606.00537）、ChunkAct（2610.18874）、Mixture of Horizons（2511.19433）、
>    Revisiting Open-Loop Execution（2608.15938）和 ACT；查 GitHub 是否已有
>    success-aware chunk truncation/termination；
> 4. 给窄线 go/no-go。PACE 已做 phase-aware chunk execution；若它或上述工作已覆盖
>    阶段截断/success-aware 截断，窄线也 no-go，写 negative memo 并回到 TPSC/其他候选。
>    注意 execute30/10/6 = 19/20、7/20、0/20：全局缩短 horizon 不是修复；
>    chunk 重叠/边界跳变/跟踪误差也不能预测失败（execute6 指标更低是因为更早失败）。
>    PACE/GR-BC 已覆盖阶段截断/加权；**窄线已关闭**，不要写 12500 的预注册。
>
> **3. 窄线已关闭，不跑预注册实验**
> 不要做训练时 post-success mask（已被 GR-BC 覆盖），不要重复 12400–12419 的
> 夹爪命令检测器，也不要用 12500–12519 做 success-aware truncation。
> 当前没有需要执行的预注册实验；直接进入新问题搜索。
>
> **4. 若 no-go：TPSC 也已 no-go，进入新问题搜索**
> 先写一页 negative memo：最近邻是谁、覆盖了什么、为什么此线不能作为核心。
> **TPSC 已 no-go**：CMTA（2023）已用 contrastive modules + temporal attention
> 处理负迁移/任务内冲突；Sigma-Agent（2024）与 AtomSkill（2025）已做多任务对比模仿
> 与语义-时序一致性。不要构建 paired-task carrier，不要训练 TPSC。
> 当前 ACT 是单任务；TPSC 场景的 scripted physics grasp 仍 0/20。
> 执行长度诊断还显示：chunk 重叠/边界跳变/跟踪误差不能预测失败（execute6 指标更低
> 是因为更早失败），所以不要建“执行一致性证书”；action-chunking 窄线已关闭。
> 不要回到 TPSC/执行长度；直接进入新问题搜索。
> **认知偏差探针候选也已 no-go**：冻结 ACT 试点确实有源偏移 19/20 → 1/20、
> 遮挡 17/20 → 0/20 的分离现象；但 CorrectVLA（2026）的 failure taxonomy 已覆盖
> perception/target failure，SO-101 failure/recovery benchmark（2606.08881v2）已有
> State Mismatch、Grasp Instability、semantic/execution 分解和 recovery（真实
> SO-101/ACT）。该候选最多是已有 taxonomy 下的细粒度诊断，不是新基准/新方向。
> 读 `docs/prior-art/cognitive-bias-probe-candidate-20261116.md` 确认；不要构建
> benchmark、不要训练。接触丰富装配/力感知 VLA 也已拥挤（CompVLA、TLA、
> UniTacVLA、TacVLA 等）。
> **演示顺序探针（新候选，未查新通过）**：canonical 两次独立训练 17/20、19/20；
> reverse/random 各 13/20。canonical-retrain vs reverse/random McNemar 均
> **p=0.0352**；合并 canonical 36/40 vs 非 canonical 26/40，Fisher **p=0.0145**；
> 官方 vs 重训 p=0.3125。可能是数据顺序/课程效应，但 canonical 顺序或与收集/
> 难度相关；先查 COIL/SGD/curriculum，做 per-seed 示教属性/难度/最后 batch 机制
> 分析，并需更多 orders/seeds。不要直接训练“order-robust”方法；先写查新 memo。
> **当前没有已通过门槛的方向；这个顺序候选待查。** 查新/机制不过就报告
> “没有方向”，进入重新定义问题。
>
> **5. 收尾**
> 更新 `docs/RESEARCH_READINESS.md` 与 `docs/CODEX_HANDOFF_20261116.md`，
> 说明“哪条观察改变了判断”。在查新完成前，禁止写“方向成立/查新通过/精度补偿成功”。
>
> **硬约束**
> - 不重启旧训练/旧队列；不改 `third_party/SO-ARM100` 官方 XML、受保护 manifest 或旧结果。
> - 12100–12119、12200–12219、12300–12319、12400–12419、12600–12619、
>   12700–12719、12800–12819 已烧掉；新实验只用 12900–12919 或更新 seeds。
> - `freeze_open` 的 oracle detector 不能写成可部署方法；命令状态机是 task-specific；
>   20/20 不是新方法成绩。
> - **广义 post-completion 已 no-go**（Temporal Aliasing 2026 + GR-BC 2026）；
>   不要把它写回方向。窄线不过就停止，不要换措辞。
> - 不把 ACT 能力通过、post-release 诊断或任何单一 seed 结果当成方向/查新通过。
> - 所有新结果写 fresh 目录，保留 hash、stdout、失败原因和完整证据。

## 给用户的短版（如果只想发一段）

> 广义 post-completion 已因 Temporal Aliasing 2026（release/retreat/stability/collision
> 证书）和 GR-BC 2026（成功轨迹内 regressive chunk 加权）判为 **no-go**；不要重做广义扫描。
> 只核验这两篇，并把 `docs/prior-art/post-completion-action-scan-20261116.md` 收窄到
> **action-chunking 测试时截断**（必读 PACE、ChunkAct、Mixture of Horizons、Revisiting
> Open-Loop Execution）。PACE 已做 phase-aware chunk execution；若窄线也 no-go，写 negative
> memo；TPSC 也已 no-go（CMTA/Sigma-Agent/AtomSkill），不要转 TPSC 训练。
> 窄线已关闭，不要预注册 12500 的 success-aware chunk truncation。
> 不要训练 post-success mask，不要重复 12400–12419 检测器、12600–12619 执行长度、
> 12700–12719 源偏移或 12800–12819 遮挡实验；不要把 oracle/命令状态机写成新方法。
> **唯一新候选是演示顺序**：canonical 17/19 vs reverse/random 13/13，McNemar
> p=0.035、合并 Fisher p=0.0145；先查 COIL/SGD/curriculum、做 per-seed 属性/难度/
> 最后 batch 机制分析，再决定是否预注册 order-robust 训练；不要直接训练。

## 交接时最重要的三句话

1. ACT 18/20 只说明载体可用；不是方向。
2. post-release 诊断说明失败发生在释放后，不是放置精度；oracle 检测不可部署，
   夹爪命令状态机是 task-specific 可部署诊断，不是通用方法。
3. 广义 post-completion、action-horizon、TPSC 和认知偏差探针基准都已 no-go/拥挤；
   唯一新候选是**演示顺序**（canonical 17/19 vs reverse/random 13/13，
   McNemar p=0.035、合并 Fisher p=0.0145），但未查新/机制通过。先查
   COIL/SGD/curriculum、做 per-seed 属性/难度机制分析；不要直接训练。
