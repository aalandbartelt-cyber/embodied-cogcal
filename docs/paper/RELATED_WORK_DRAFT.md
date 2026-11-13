# 相关工作准备稿

用途：面向机器人/控制方法论文的相关工作素材，当前没有目标期刊与本项目实证结果。
模式：synthesis / algorithm + simulation + hardware / related work / bilingual。
引用键来自 [research.bib](../../references/research.bib)；`[@key]` 为准备稿标记。
本稿不是已经完成的论文，不填摘要结果或已成立贡献；新路线确定后应按其中心问题压缩重写。

## 中文稿

### 语言落地与任务意图变化

视觉—语言—动作策略把自然语言条件与视觉观测映射为机器人动作，OpenVLA 和 SmolVLA 为开放模型与低成本部署提供了代表性载体
[@kim2025openvla; @shukor2025smolvla]。语言输入的存在并不保证动作忠实于当前意图。
ICBench 使用与固定场景矛盾的指令检测语言忽视，IGAR 在推理阶段重新分配注意力；LIBERO-CF 则采用可行的替代任务，
通过 CAG 增强语言条件动作与无语言动作之间的差异 [@zhang2026igar; @fang2026cag]。
两类设置的评价对象不同：前者可通过停止错误执行改善语言一致性，后者要求完成新的合法目标。
SwitchVLA 进一步将接触与执行状态纳入在线意图切换，表明指令变化的时刻也是任务定义的一部分 [@li2025switchvla]。

### 扰动组合与动作校准

LIBERO-Plus 与 LIBERO-Pro2.0 已将鲁棒性评价从单因素扩展到组合条件和运行时干预
[@fei2026liberoplus; @zhou2026liberopro2]。组合性能下降需要结合所用尺度和零模型解释，不能直接等同于特定认知机制。
在修复层面，BAS-VLA 依据任务保持与任务改变条件校准冻结策略动作，IDR 则以反事实模态输入估计动态作用并采用门控残差融合
[@liu2026basvla; @zhang2026idr]。CorrectVLA 研究人工句子提供的方向、幅度与时间窗信息能修复何类执行失配
[@kwon2026correctvla]。这些工作共同要求后续方法把可用信息、参考动作与计算预算写清，
以相同预算的普通残差和单因素修复区分结构性增量。

### 执行时序与同体外部验证

动作分块策略的效果还取决于反馈年龄与重规划时序。SmolVLA 的异步栈和 RTC 分别从系统执行与推理算法角度处理延迟
[@shukor2025smolvla; @black2025rtc]。因此，校准收益需要与纯时序修复区分。
SIMPLER 和 SO-101 Bench 为模拟评测与现实表现之间的联系提供了实例，但迁移关系依赖具体本体、策略与环境
[@li2025simpler; @hickok2026so101bench]。对动作校准的研究还需直接比较同一任务中方法增益在两域是否保持，
并单列真机允许重新估计的几何量与冻结的语义参数。

### 失败诊断与研究问题定位

Sentinel 结合时间一致性与任务进展监测策略失效，RoboMD 主动搜索高风险条件，
Which Hand Was Late? 则展示被动观测不能区分部分复合失败的情况 [@agia2024sentinel; @sagar2024robomd; @whichhand2026]。
这些设置区分了发现失败、判断原因与选择修复三个问题。后续研究需要明确自身解决其中哪一个决策问题，
并以可识别条件、额外信息成本及修复结果支撑贡献。

## English draft

### Language grounding and changing intent

Vision–language–action policies translate visual observations and language instructions into robot actions.
OpenVLA and SmolVLA provide open implementations for studying these policies across deployment settings
[@kim2025openvla; @shukor2025smolvla]. However, language conditioning does not ensure that actions follow the current instruction.
ICBench examines contradictory instructions in fixed scenes, and IGAR modifies inference-time attention.
LIBERO-CF instead assigns feasible alternative goals and strengthens language conditioning through counterfactual action guidance
[@zhang2026igar; @fang2026cag]. These settings require different outcomes: preventing an invalid action and completing a valid alternative task.
SwitchVLA also conditions task switching on execution and contact states, making the timing of an instruction change part of the evaluation
[@li2025switchvla].

### Composed perturbations and action correction

LIBERO-Plus and LIBERO-Pro2.0 investigate robustness under composed perturbations and runtime interventions
[@fei2026liberoplus; @zhou2026liberopro2]. A composition gap requires an explicit reference model and measurement scale.
It does not alone identify a cognitive mechanism. For action correction, BAS-VLA distinguishes task-preserving and task-changing conditions.
IDR uses counterfactual modality inputs to guide gated residual refinement [@liu2026basvla; @zhang2026idr].
CorrectVLA studies a different information channel: retrospective human corrections specify action dimensions and time windows
[@kwon2026correctvla]. Comparisons among these methods must account for correction data, available observations, and inference cost.

### Execution and simulation–real evaluation

Action chunking couples policy behavior to observation age and replanning frequency.
SmolVLA and real-time chunking address this coupling through asynchronous execution and delay-aware inference
[@shukor2025smolvla; @black2025rtc]. Timing controls are therefore necessary when attributing improvements to action calibration.
SIMPLER and SO-101 Bench examine whether simulated evaluation reflects real policy behavior
[@li2025simpler; @hickok2026so101bench]. For calibration methods, the relevant comparison also includes the method-induced performance difference in each domain.
Matched tasks, action conventions, and parameter-freezing rules make this comparison interpretable.

### Diagnosis and repair decisions

Failure monitoring, cause identification, and repair selection impose different information requirements.
Sentinel monitors temporal consistency and task progress, while RoboMD searches for failure-inducing conditions
[@agia2024sentinel; @sagar2024robomd]. Which Hand Was Late? identifies cases where passive observations cannot separate multiple causes
[@whichhand2026]. This distinction motivates evaluating what a diagnostic observation changes about the repair decision, alongside its prediction accuracy and acquisition cost.

## 引用功能与作者待办

| 段落 | 引用作用 | 正式写作前的工作 |
|---|---|---|
| 模型/语言 | 背景与最近问题设置 | 保留实际选用载体和最相关近邻，删除无作用的模型罗列 |
| 组合/校准 | 最近方法与贡献边界 | 逐式检查 IDR/BAS/CAG，写出我们的不可替代增量；没有就换方案 |
| 时序/迁移 | 竞争解释与外部效度 | 用真实延迟和两域方法差值补证，不能借引文替代本项目结果 |
| 诊断 | 备选问题定位 | 若选 C 路线，补经典主动辨识与约束输入设计，重写为该问题主线 |

没有写“已有研究均未考虑……”或“本文首次……”。新路线未定前，这些段落是有来源的材料准备，
不把多个相邻问题拼接成一个已经成立的论文贡献。
