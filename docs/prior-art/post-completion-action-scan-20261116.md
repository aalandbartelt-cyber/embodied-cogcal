# Post-completion / post-success action：初步检索 + 两篇全文核查

日期：2026-11-16。状态：**非穷尽查新；广义线初步 no-go，窄线待核**。
本页用于给后续原文核查提供起点；没有读到的全文一律标“待核”。

## 检索记录

- Google Scholar：本轮仍不可用（前序 403/429）；未声称穷尽。
- Semantic Scholar API：2026-11-16 尝试 7 条查询，全部 429；未取得结果。
- OpenAlex API：8+8 条查询式，2026-11-16。
- arXiv API：8 条精确短语查询，2026-11-16。
- 未做 GitHub 代码检索、未做前向/后向引用追踪、未读全文。

查询式包括：

- `post-success actions imitation learning robot`
- `post-completion behavior cloning robot`
- `early termination imitation learning`
- `causal confusion imitation learning`
- `retraction planning pick and place robot`
- `success detection imitation learning robot`
- `outcome-aware imitation learning robot manipulation`
- `post-release object displacement robot gripper`
- `all:"post-success"`、`all:"post-completion" AND all:"imitation"`
- `all:"early termination" AND all:"imitation learning"`
- `all:"causal confusion" AND all:"robot"`
- `all:"action masking" AND all:"imitation"`
- `all:"retraction" AND all:"manipulation"`
- `all:"object displacement" AND all:"gripper"`
- `all:"placement" AND all:"retreat" AND all:"robot"`

## 最近邻（标题级）

| 工作 | 年份 | 与本现象的关系 | 它可能覆盖什么 | 它未必覆盖什么 | 状态 |
|---|---:|---|---|---|---|
| Causal Confusion in Imitation Learning | 2019 | 最近的理论近邻之一 | 策略利用虚假相关/非因果线索 | 成功后返回动作被模仿并 undo 任务；释放后碰撞评测 | 待核 |
| Object-Aware Regularization for Causal Confusion | 2021 | 因果混淆的正则化 | 用对象信息缓解因果混淆 | post-success 动作 mask；VLA/ACT | 待核 |
| Robot Policy Learning from Demonstration Using Advantage Weighting and Early Termination | 2022 | 最近的“early termination”近邻 | 优势加权 + 早停 | BC/VLA 中对成功后演示动作的 mask；释放后位移 | 待核 |
| Neural Task Success Classifiers for Robotic Manipulation from Few Real Demonstrations | 2021 | 成功检测近邻 | 少样本任务成功分类 | 仅用 RGB/q 的释放检测；停止后的最终稳定性 | 待核 |
| HYDRA: Hybrid Robot Actions for Imitation Learning | 2023 | 动作表示近邻 | 混合动作/技能 | post-success 返回动作；释放后碰撞 | 待核 |
| Waypoint-Based Imitation Learning for Robotic Manipulation | 2023 | 轨迹表示近邻 | 关键点/航点监督 | 成功后动作 mask；release-vs-final 评测 | 待核 |
| Pick and Place Planning is Better Than Pick Planning Then Place Planning | 2024 | 工业抓放规划近邻 | 抓放联合规划 | 学习策略的释放后回撤碰撞 | 待核 |
| Diagnosing Temporal Aliasing in Behavior Cloning for Verified Multi-Stage Robotic Manipulation | 2026 | **直接覆盖评测/现象** | 六谓词 release/retreat/stability/collision；re-grasp/push 清零 | ACT/VLA/action chunking；本文任务 | **已读全文，直接近邻** |
| Graph-Reweighted Behavior Cloning with Human Interventions for Precise Robotic Manipulation | 2026 | **直接覆盖方法** | 成功轨迹内 regressive chunks 的后果加权；VLA post-training | 测试时 chunk 截断；ACT 执行层 | **已读全文，直接近邻** |
| Interactive Post-Training for Vision-Language-Action Models | 2025 | VLA 后训练近邻 | 交互式后训练 | post-success 动作 mask；释放后碰撞 | 待核 |
| ChunkAct: Action Chunking for Agentic Robotics | 2026 | action chunking 近邻 | chunk 化动作 | 成功后终止；释放后稳定性 | 待核 |
| Mixture of Horizons in Action Chunking | 2025 | action chunking 近邻 | 多 horizon 混合 | 成功后终止；post-success 动作 | 待核 |
| RECON: Reducing Causal Confusion with Human-Placed Markers | 2024 | 因果混淆近邻 | 人工标记缓解混淆 | post-success 动作；释放后碰撞 | 待核 |
| CIVIL: Causal and Intuitive Visual Imitation Learning | 2025 | 因果视觉模仿近邻 | 因果视觉表征 | post-success 动作 mask；release-vs-final | 待核 |
| CoPRE: Improving Sensitivity in Proprioceptive Contact Detection for Low-Cost Robot Arms | 2026 | 可部署接触检测近邻 | 本体接触检测 | 成功/释放检测与停止策略 | 待核，优先读 |

## 全文核查（2026-11-16）：两个直接近邻

### 1. Diagnosing Temporal Aliasing in Behavior Cloning for Verified Multi-Stage Robotic Manipulation

- 全文：AJoSR 2026，PDF 已下载并抽取 1039 行（`/tmp/priorart/temporal-aliasing.txt`，
  本地临时文件，不作为项目证据提交）。
- 六谓词严格证书：
  `Cstrict = Clift ∧ Ccross ∧ Crelease ∧ Cretreat ∧ Cstable ∧ ¬Ccollision`。
- 原文明确写：“Reaching the target is therefore not evidence of release, retreat,
  stability, or collision-free execution.”
- stability 计数在“earlier re-grasp or push”时清零；失败标签包含 missing release、
  missing retreat、unstable placement；collision 记录首次接触相对 crossing 的时序。
- 任务为 Panda pick–cross–place（有屏障），策略为 MLP/GRU BC，不是 ACT/VLA/action
  chunking；但**释放后回撤、稳定性、碰撞的评测**已经被它覆盖。

### 2. Graph-Reweighted Behavior Cloning with Human Interventions

- 全文：CoRL 2026（arXiv 2610.20504），PDF 已下载并抽取。
- 原文明确写：标准 SFT “naively treats every action chunk as a positive target,
  thereby inadvertently cloning undesired behaviors from expert demonstrations”。
- GR-BC 用 goal-reachability graph 计算 remaining steps，并按 chunk 的后果加权，
  “down-weights locally regressive chunks even inside successful trajectories”。
- 这覆盖了“成功后/回归动作应被降权或不被克隆”的**方法**；简单的 mask/relabel
  很可能被视为它的特例。

## 初步裁决：广义 post-completion 线 no-go，窄线也很拥挤

- **现象/评测**：Temporal Aliasing 2026 已有 release/retreat/stability/collision 证书，
  且明确处理 re-grasp/push 导致的 stability 清零。
- **方法**：GR-BC 2026 已有成功轨迹内 regressive chunk 的后果加权。
- 因此“post-success actions 被 BC 模仿并 undo 任务”作为**核心方向不成立**；
  当前的 task-specific 夹爪命令检测器只是工程可行性，不是独立科学增量。
- 窄线 **action-chunking 测试时执行/截断** 也很拥挤：
  - PACE（2026，arXiv 2606.00537）：training-free phase-aware chunk execution，
    用预测速度剖面的低速谷选择执行 horizon；50-task RoboTwin2.0、LIBERO、真机。
    它不专门做 success stop，但已覆盖“按阶段边界截断/重规划”的机制。
  - Mixture of Horizons（2025）、Revisiting Open-Loop Execution（2026）、ChunkAct（2026）
    已覆盖 execution horizon/开环执行。
  - Selective Residual Action Chunking（2026）已是 multi-task ACT；RAIN（2026）是
    adaptive chunk refinement。
- 所以“success-aware chunk truncation”只能算 PACE/early termination 的小变体；
  除非能证明 success-specific 信号带来独立且可测的增量，否则窄线也 **no-go**。
- **当前没有可立项方向。** 下一步应回到 TPSC 或其他候选做查新，而不是继续训练。

## 下一步（必须做）

1. 读 ChunkAct（arXiv 2610.18874）、Mixture of Horizons（arXiv 2511.19433）、
   Revisiting Open-Loop Execution（arXiv 2608.15938）以及 ACT 原始工作，
   确认是否已有“成功对齐的 chunk 截断/终止”。
2. 查 GitHub：ACT/LeRobot/VLA 仓库是否有 success-aware chunk truncation、
   early stop within chunk、release-triggered termination 的实现或 issue。
3. 若窄差异也被覆盖：写 negative memo，停止 post-completion 线，回到 TPSC 或其他候选。
4. 若窄差异成立：先写预注册，再在全新 seeds 上做一个最小实验；不得复用
   12100–12119、12200–12219、12300–12319、12400–12419 调参。
5. 本页不能作为查新通过；它目前的结论是**广义线 no-go、窄线待核**。
