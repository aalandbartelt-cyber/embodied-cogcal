# 深审阅读入口与补充文献

日期：2026-11-14。先读 [方向裁决](../prior-art/ROUTE_DECISION.md)，再按下表核原文。
本轮以核心公式、观测条件、估计对象和强简单替代审查方案，不以文献数量决定新颖性。

| 优先级 | 原文/报告入口 | 本轮核对的内容 |
|---|---|---|
| 1 | [ECCBF 深审](../prior-art/deep-audit-eccbf.md) | IDR/BAS/CAG/Plus/PRO2.0及IMPACT-VLA的方法式；当前实现的等价性与提示清理 |
| 2 | [迁移差值深审](../prior-art/deep-audit-transfer-effects.md) | SIMPLER正式版、MetaFine §8、PPI家族、主动统计推断、Ao v2差值协方差与选择 |
| 3 | [主动诊断深审](../prior-art/deep-audit-active-diagnosis.md) | Which Hand、FIERL、Fly-by-Code；经典排障、可达集与贝叶斯风险输入设计 |
| 4 | [接触适配深审](../prior-art/deep-audit-contact-adaptation.md) | Self-comp §3/B.6、传感/模型可辨识性、FACE/RoboPace、传统hedging/deadzone/anti-windup |
| 5 | [探索草案](../prior-art/EXPLORATION_PROTOCOL.md) | 先验证现象与简单强基线，之后才谈新方法；并未开始注册或运行 |

正文阅读指相应报告明确标注的章节，不是所有论文通读；未独立复现外部实验。
根代理还核对 Instruction–Action Binding §2及Limitations、SALT §3–4/J、FAN §III–V相关段、ViTaR Method，
它们分别约束语言解释、伪目标有效范围、动作坐标漂移和接触残差调制的贡献表述。
Continual VLA 的 ICML2026/PMLR出版页及摘要已核实，未把本轮摘要阅读说成全文精读。

## 补充库口径

主库仍为50条；以下补充31条版本记录、30篇新增论文（Ao v1/v2是同篇不同题名版本）。
两条历史版本保留用于审计，不是多算一篇成果。BibTeX/RIS可单独导入，勿同时导入两格式。
完整作者、原始元数据、版本、响应哈希与Scholar链接见
[supplement metadata](../../references/supplement-deep-audit-metadata.json)，
[BibTeX](../../references/supplement-deep-audit.bib)、[RIS](../../references/supplement-deep-audit.ris)。

Ao v1的abs页citation title省略末尾Audits，而原始全文题名完整；两者来源与覆盖依据保留。
其v2为另一个题名，不将v2公式误引为v1。其余正式录用状态未逐项核对；arXiv按固定版本引用。
经典来源另由四份审计给出原始出版社/作者稿与章节，未假填DOI。

## 新增论文的可追溯版本目录

本表仅说明库里有什么，实际阅读层级以具体审计报告为准。没有报告明确标注的正文内容，不声称精读。

| 固定版本 | 原始题名 | 引用键 |
|---|---|---|
| [1703.01250v1](https://arxiv.org/abs/1703.01250v1) | Virtual vs. Real: Trading Off Simulations and Physical Experiments in Reinforcement Learning with Bayesian Optimization | `deep1703_01250v1` |
| [2111.00765v3](https://arxiv.org/abs/2111.00765v3) | Validate on Sim, Detect on Real -- Model Selection for Domain Randomization | `deep2111_00765v3` |
| [2303.17476v1](https://arxiv.org/abs/2303.17476v1) | Differentiable Environment Primitives for Contact State Estimation | `deep2303_17476v1` |
| [2309.16598v2](https://arxiv.org/abs/2309.16598v2) | Cross-Prediction-Powered Inference | `deep2309_16598v2` |
| [2311.01453v2](https://arxiv.org/abs/2311.01453v2) | PPI++: Efficient Prediction-Powered Inference | `deep2311_01453v2` |
| [2401.05782v1](https://arxiv.org/abs/2401.05782v1) | Online input design for discrimination of linear models using concave minimization | `deep2401_05782v1` |
| [2403.03208v3](https://arxiv.org/abs/2403.03208v3) | Active Statistical Inference | `deep2403_03208v3` |
| [2410.00371v1](https://arxiv.org/abs/2410.00371v1) | AHA: A Vision-Language-Model for Detecting and Reasoning Over Failures in Robotic Manipulation | `deep2410_00371v1` |
| [2502.09829v1](https://arxiv.org/abs/2502.09829v1) | Efficient Evaluation of Multi-Task Robot Policies With Active Experiment Selection | `deep2502_09829v1` |
| [2505.12224v5](https://arxiv.org/abs/2505.12224v5) | RoboFAC: A Comprehensive Framework for Robotic Failure Analysis and Correction | `deep2505_12224v5` |
| [2507.20068v3](https://arxiv.org/abs/2507.20068v3) | PERRY: Policy Evaluation with Confidence Intervals using Auxiliary Data | `deep2507_20068v3` |
| [2512.02787v3](https://arxiv.org/abs/2512.02787v3) | Diagnose, Correct, and Learn from Manipulation Failures via Visual Symbols | `deep2512_02787v3` |
| [2601.21471v1](https://arxiv.org/abs/2601.21471v1) | Best Arm Identification with LLM Judges and Limited Human Audits | `deep2601_21471v1` |
| [2601.21471v2](https://arxiv.org/abs/2601.21471v2) | Designing Service Systems from Textual Evidence | `deep2601_21471v2` |
| [2602.12405v2](https://arxiv.org/abs/2602.12405v2) | Self-Refining Vision Language Model for Robotic Failure Detection and Reasoning | `deep2602_12405v2` |
| [2603.03818v2](https://arxiv.org/abs/2603.03818v2) | Pretrained Vision-Language-Action Models are Surprisingly Resistant to Forgetting in Continual Learning | `deep2603_03818v2` |
| [2603.24584v1](https://arxiv.org/abs/2603.24584v1) | TAG: Target-Agnostic Guidance for Stable Object-Centric Inference in Vision-Language-Action Models | `deep2603_24584v1` |
| [2606.09740v1](https://arxiv.org/abs/2606.09740v1) | ProbeAct: Probe-Guided Training-Free Failure Recovery in Vision-Language-Action Models | `deep2606_09740v1` |
| [2607.08347v1](https://arxiv.org/abs/2607.08347v1) | Prediction-Powered Active Testing | `deep2607_08347v1` |
| [2608.15816v1](https://arxiv.org/abs/2608.15816v1) | ViTaR: Visuo-Tactile Residual Adaptation for Foundation VLA Manipulation | `deep2608_15816v1` |
| [2609.15005v1](https://arxiv.org/abs/2609.15005v1) | IMPACT-VLA: Interaction-aware Multimodal Propagation Attribution via Counterfactual Trajectories for Vision-Language-Action Policies | `deep2609_15005v1` |
| [2609.21358v1](https://arxiv.org/abs/2609.21358v1) | FAN: Foresight Action Normalization for Continual Adaptation of Vision-Language-Action Models | `deep2609_21358v1` |
| [2609.37334v1](https://arxiv.org/abs/2609.37334v1) | Taming VLAs under Robot Execution Errors: Self-Compensation and Stress Testing | `deep2609_37334v1` |
| [2609.39971v1](https://arxiv.org/abs/2609.39971v1) | When Instructions Retrieve Trajectories: Diagnosing and Mitigating Generalization Failures in VLA Models | `deep2609_39971v1` |
| [2610.07946v1](https://arxiv.org/abs/2610.07946v1) | Adapting Vision-Language-Action Models to Unknown Visual Disruptions During Execution | `deep2610_07946v1` |
| [2610.09533v1](https://arxiv.org/abs/2610.09533v1) | Contact-Aware Imitation Learning Through Contact Factorization | `deep2610_09533v1` |
| [2610.09696v1](https://arxiv.org/abs/2610.09696v1) | RoboPace: Contact-Aware Time-Optimal Retiming for Action-Chunk Policies | `deep2610_09696v1` |
| [2610.12332v1](https://arxiv.org/abs/2610.12332v1) | Prediction-Powered Data Fusion for Treatment Effect Estimation | `deep2610_12332v1` |
| [2610.12549v1](https://arxiv.org/abs/2610.12549v1) | Fly-by-Code: Embodied Coding Agents for Aerial Manipulation with Active Visual and Physical Feedback | `deep2610_12549v1` |
| [2610.27389v1](https://arxiv.org/abs/2610.27389v1) | Fixed-Size Active Statistical Inference | `deep2610_27389v1` |
| [2610.34681v1](https://arxiv.org/abs/2610.34681v1) | Pro-Active Inference | `deep2610_34681v1` |
