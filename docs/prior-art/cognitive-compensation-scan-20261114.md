# 认知偏差修正 × 工业精度补偿：方向扩展扫描

日期：2026-11-14。状态：**候选发现与预筛，不是机构科技查新报告，也不是已选定方向。**
本文独立于 codex 正在维护的 D/D′ 可执行证书与风险来源路线；不推翻
[路线裁决](ROUTE_DECISION.md) 的既有否决结论，只提出一个尚未被同一门槛审计的新候选。
旧 ECCBF、迁移差值、主动诊断、接触补偿、动态证书均不因本文恢复。

固定约束沿用：低成本 SO-101、单/双 A100、同体仿真—真机；核心研究问题可更换；
《思考，快与慢》与工业机器人精度补偿只作问题启发，不把心理学名称、平台或
“测量—建模—补偿—验证”流程本身当作创新。

---

## 0. 结论先行

| 排序 | 候选 | 一句话 | 当前判断 |
|---|---|---|---|
| **主推荐** | **参考类偏差场迁移（RCBT）** | 冻结 VLA 的系统性动作偏差是否可沿**因果任务结构**跨任务迁移，并用稀疏标定安全补偿？ | 最值得做 2 周否证实验 |
| 备选 1 | 外部视角决策校准（OVDC） | 用参考类历史结果校正 VLA 的基率忽视与过度自信，决定行动/弃权/求助 | 认知链路最纯，但偏离“动作补偿” |
| 备选 2 | 偏差—噪声预算分配（BNBA） | 固定测试时预算下，何时补偿系统性偏差、何时聚合噪声？ | 核心观察已被 2026-10 论文部分占据 |
| 备选 3 | 具身评测噪声审计（EENA） | 报告的性能差异有多少来自任务/种子/环境/评审噪声？ | 可行且有用，但偏方法学，且与 codex 统计工作重叠 |
| 不推荐 | WYSIATI 信息缺口主动补全（WAIG） | 检测“未表征的缺失信息”并触发查看/探测 | 与主动诊断、主动感知近邻过密 |

**方向谱系：**

| 候选 | 卡尼曼概念 | 工业类比 | 对应的 VLA 问题 |
|---|---|---|---|
| RCBT | 外部视角、参考类、代表性启发、基率忽视 | 误差相似性、误差场插值、补偿参数迁移 | 新任务标定昂贵、负迁移、部署可靠性 |
| OVDC | 外部视角、基率忽视、过度自信 | 历史误差先验/参考工件 | 置信校准在任务类别移位下失效 |
| BNBA | 偏差 vs 噪声、系统 2 审议 | 系统误差补偿 vs 随机重复性 | 测试时算力该花在补偿还是采样 |
| EENA | 噪声审计、小数定律、回归均值 | Gage R&R/测量系统分析 | benchmark 差异是否真 |
| WAIG | WYSIATI、“眼见即全部” | 未知区域探测 | 遮挡/未知约束下的错误重采样 |

**核心判断：不要再做一个“校准器/残差补偿器”。**
2025–2026 年，VLA 的置信校准、任务语义动作校准、选择性修正、残差适配、执行遥测整流
都已有直接工作。真正还空着、且能承载项目主线的科学对象是：

> **策略偏差的跨任务结构**——它是不是一个可测量、可迁移、可组合的场，
> 而不是每个任务各自拟合的一堆残差。

RCBT 把这个问题变成可证伪命题：如果 VLA 的动作偏差能沿因果任务结构迁移，
就能用少量标定把旧任务的“误差场”借给新任务；如果只能沿视觉相似性迁移，
那就是被“代表性启发”骗了；如果完全不能迁移，那么“偏差场”只是任务局部残差，
应停止该主张。

---

## 1. 检索口径与限制

### 1.1 实际通道

| 通道 | 状态 | 用途 |
|---|---|---|
| Google Scholar | 直接查询返回 **429**，未看到结果列表 | 不伪造 Scholar 结果；保留人工复查入口 |
| OpenAlex API | 可用 | 主题面、标题/摘要精确检索、被引与 DOI |
| arXiv API | 可用 | 2025–2026 最新预印本，弥补索引滞后 |
| GitHub API | 可用 | 开源实现、许可证、活跃度、README 机制核对 |
| DOI/出版社页 | 按需 | 工业误差补偿经典来源的题名/DOI 核验 |

这不是穷尽检索。OpenAlex 的相关度排序会把宽词命中放大；下文的“未命中”只表示
**当前关键词组合下没有直接同题工作**，不表示查新通过。关键近邻必须继续读全文、
追引用链和后续版本。

**Scholar 人工复查入口**（本次 API 返回 429，以下链接供人工点开核对）：

- https://scholar.google.com/scholar?q=%22action+bias+field%22+robot
- https://scholar.google.com/scholar?q=%22reference+class+forecasting%22+robot
- https://scholar.google.com/scholar?q=%22vision-language-action%22+calibration+bias
- https://scholar.google.com/scholar?q=%22cross-task%22+%22calibration+transfer%22+robot

**GitHub 检索入口**：

- https://github.com/search?q=VLA+calibration&type=repositories
- https://github.com/search?q=robot+error+compensation&type=repositories
- https://github.com/search?q=SO-101+SmolVLA&type=repositories

### 1.2 主要检索词

- VLA 侧：`vision-language-action calibration`、`action bias`、`systematic action error`、
  `test-time correction`、`residual policy adaptation`、`failure prediction`。
- 认知侧：`cognitive bias`、`bias blind spot`、`base rate neglect`、`reference class forecasting`、
  `outside view`、`decision noise`、`noise audit`、`bias-noise decomposition`。
- 工业侧：`error similarity`、`error field compensation`、`transferability of error compensation`、
  `Gaussian process error compensation`、`compliance error parameters`。
- 迁移侧：`cross-task calibration transfer`、`hierarchical Gaussian process`、`partial pooling`、
  `negative transfer`、`task similarity`。

### 1.3 一个必须记住的负面结果

`Paraphrase Consensus Is Not Self-Consistency`（arXiv:2610.19438）已经明确写出：

> 对同一指令的多次采样做聚合，能降低方差，但**不能消除释义共享的偏差**。

这直接压缩了“偏差—噪声分解”作为全新观察的空间。本文因此不把 BNBA 作为主推荐；
RCBT 的贡献必须落在**跨任务迁移结构**，而不是“发现聚合不降偏差”。

---

## 2. 已被占据的空间：十二项直接近邻

| 工作 | 已经覆盖的机制 | 对候选的约束 |
|---|---|---|
| [Confidence Calibration in VLA](https://arxiv.org/abs/2507.17383)；[代码](https://github.com/thomaspzollo/vla_calibration) | VLA 置信校准基线；prompt ensembles；action-wise Platt scaling；随时间的校准漂移 | 不能把“校准 VLA 置信度”当新点 |
| [BAS-VLA](https://arxiv.org/abs/2609.23650)；[代码](https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts) | 任务保持变化下的动作漂移 vs 语义破坏变化下的轨迹惯性；残差校准器 + 选择性保持辅助 | 不能把“任务语义动作校准/残差修正”当新点 |
| [ACR-VLA](https://github.com/anonymous-nlp-2026/knowing-when-not-to-correct-calibrated-uncertainty-gating-vision-language-action-model-refinement)（无许可证） | 用校准不确定性门控“何时不该修正”，避免在自信步上做有害修正 | 不能把“选择性修正/何时不修正”当新点 |
| [Residual Policy Adaptation for VLA](https://doi.org/10.6084/m9.figshare.31329868) | 冻结 VLA + 任务专属 SE(3) 残差头；有界修正；小样本装配 | 不能把“任务专属残差补偿”当新点 |
| [ORPA](https://arxiv.org/abs/2608.17323) | 在线、反馈条件化的关节空间残差适配，不改策略参数 | 不能把“在线残差适配”当新点 |
| [Self-compensating VLA](https://arxiv.org/html/2609.37334v1)；[项目页](https://github.com/sohyun-l/SelfCompensatingVLA_project_page) | 用执行残差形成自监督目标；任务边界清空适配状态；真实抽屉任务 | 接触/执行残差自补偿已被覆盖；旧接触题不恢复 |
| [TeAR](https://arxiv.org/abs/2609.36182) | 遥测条件动作整流；SO-ARM101 物理评估 | 不能把“遥测/热/电流补偿”当新点 |
| [Paraphrase Consensus](https://arxiv.org/abs/2610.19438) | 释义聚合降方差但不消除共享偏差；指令依赖诊断 | 不能把“聚合不降偏差”当全新发现 |
| [Policy-Induced Hand Priors](https://arxiv.org/abs/2608.11769) | 初始位姿依赖的双手先验；HandPriorScore；数据增广缓解 | 单一系统性偏差的诊断/缓解已有先例 |
| [Evidence-Guided Counterfactual Learning](https://arxiv.org/abs/2610.12861) | 长尾任务中的 head-task 动作偏差；反事实视觉证据增强 | 动作偏差的存在已被领域识别 |
| [Marginal Calibration Does Not Compose](https://arxiv.org/abs/2609.23731) | 模块级校准不保证组合后校准；需联合协方差 | 任何“组合式偏差”主张必须处理相关性 |
| [Audit Before You Commit](https://arxiv.org/abs/2609.30608) | 置信门控通过≠决策正确；校准覆盖不修复观测模型偏差 | 不能把“加 conformal/置信门控”当核心 |

说明：TeAR、Self-comp 的机制判断沿用项目既有深审（见 [路线裁决](ROUTE_DECISION.md) 等）；
本次重新核对了其题名/摘要/项目页，未重读全文。其余条目本次读取了 arXiv 摘要或 GitHub README。

**共同结论：**
1. “VLA 有系统性偏差”不是新发现；
2. “给 VLA 加残差/校准/门控”不是新方法；
3. 仍然空着的是：**偏差作为任务结构的函数，是否可跨任务迁移/组合**，
   以及**如何选择参考任务才不产生负迁移**。

---

## 3. 主推荐：参考类偏差场迁移（RCBT）

### 3.1 一句话

> 把冻结 VLA 的系统性动作偏差视为任务条件化的**偏差场**；用少量标定测量它，
> 用**因果任务结构**而不是视觉相似性构造参考类，把旧任务的偏差场分层迁移到新任务，
> 只在迁移风险可接受时补偿，否则弃权或退回任务局部标定。

工作名：**Reference-Class Bias-field Transfer（RCBT）**。
中文：**参考类偏差场迁移**。名称只作工作称呼，查新前不写成“首次”。

### 3.2 研究问题

主问题：

> 在冻结策略、固定观测和固定标定预算下，VLA 的动作偏差能否沿**因果任务结构**
> 从参考任务迁移到未见任务，并在迁移不安全时被识别和拒绝？

四个可分别否证的子命题：

- **H1（可测量）**：同一任务、同一上下文重复执行时，动作偏差的**系统性分量**
  大于其随机分量；偏差场可以被稳定估计。
- **H2（可迁移）**：留一任务预测中，因果参考类对未见任务偏差场的预测
  优于零偏差预测和任务局部少样本标定。
- **H3（因果而非外观）**：因果任务描述子预测偏差场相似性的能力，
  显著优于视觉/语言嵌入的浅层相似性；按视觉相似选参考类会产生可测的负迁移。
- **H4（安全补偿）**：带后验不确定性的分层补偿在低标定预算下提高成功率，
  且在后验不确定或迁移风险高时弃权，避免负迁移。

如果 H1 不成立，偏差场在这个策略/尺度上不可测，停止。
如果 H2 不成立，跨任务迁移不存在，退回任务局部标定或外部视角决策校准。
如果 H3 不成立，“代表性启发导致错误参考类”的故事不成立，方法退化为普通相似性迁移。
如果 H4 不成立，补偿有收益但无法安全门控，不能作为部署方法。

### 3.3 为什么现在值得做

1. **部署现实**：VLA 在分布移位下仍脆弱；每个新任务都重新标定/微调代价高。
   工业机器人早已用“误差相似性 + 稀疏测量 + 插值补偿”降低逐台标定成本；
   据当前检索，VLA 尚未见到成熟的“跨任务误差复用”机制。
2. **文献空隙**：当前 VLA 校准/残差工作几乎都是**任务局部**的
   （BAS-VLA、Residual Policy Adaptation、ORPA、ACR-VLA）。
   在 OpenAlex 标题/摘要精确检索中，`"bias field" robot policy`、`"systematic action bias" robot`
   均无直接命中；当前检索未见跨任务偏差场迁移的直接同题工作。
3. **认知理论**：卡尼曼的“外部视角/参考类预测”正是用同类历史结果校正当前判断；
   “代表性启发”正是用表面相似性代替因果相似性。据当前检索，机器人参考类选择尚未被这样形式化。
4. **工业理论**：误差相似性、误差场插值、补偿参数可迁移性在工业机器人中成熟
   （见 §3.6），但迁移对象是几何/柔顺误差，不是学习策略的动作偏差。
5. **项目主线**：它保留“测量—建模—补偿—验证”和“偏差场”的长期资产，
   但把旧 ECCBF 的“四格交互”升级为“跨任务结构”，不再是条件残差的改名。

### 3.4 最小机制

对任务 $t$、上下文 $c$（物体位姿、目标关系、障碍/接触条件、指令），令
$a_t(c)$ 为冻结策略的动作，$a_t^{\ast}(c)$ 为该上下文的任务一致参考动作。定义

$$
b_t(c)=\mathbb{E}[a_t(c)-a_t^{\ast}(c)],\qquad
\Sigma_t(c)=\operatorname{Var}[a_t(c)].
$$

$b_t$ 是**系统性偏差场**，$\Sigma_t$ 是**噪声场**。RCBT 不假设 $b_t$ 是常数，
而假设它可以分解为参考类共享分量与任务特异偏差：

$$
b_t(c)=b_{\mathcal R(t)}(c;z_t)+\delta_t(c),
$$

其中 $z_t$ 是**因果任务描述子**（物体功能、目标关系、接触模式、运动基元），
$\mathcal R(t)$ 是由 $z_t$ 选出的参考任务集，$\delta_t$ 是任务特异偏离。
用分层高斯过程/混合效应模型做部分池化：

$$
b_{\mathcal R}\sim\mathcal{GP}\big(0,k_z(z,z')\,k_c(c,c')\big),\qquad
\delta_t\sim\mathcal{GP}(0,k_\delta).
$$

给定新任务的 $n_t$ 个标定 episode，得到后验均值 $\hat b_t(c)$ 与方差 $\sigma_t^2(c)$。
补偿规则：

$$
a'_t(c)=a_t(c)-\hat b_t(c)
\quad\text{仅当}\quad
\sigma_t(c)\le\tau\ \text{且}\ \widehat{\text{risk}}_{\text{transfer}}(t)\le\rho,
$$

否则弃权或退回任务局部标定。这里的“风险”是统计迁移风险，不是 codex 已否决的
可执行策略证书；两者对象、假设和验证方式不同。

**与旧 ECCBF 的关键区别：**
旧 ECCBF 的 $b_{\text{int}}=a_{11}-a_{10}-a_{01}+a_{00}$ 只是 2×2 条件残差；
RCBT 的对象是**跨任务的偏差场相似结构**，核心证据是留一任务预测和因果/外观参考类对比，
不是四格交互是否显著。

### 3.5 与最近邻的精确差异

| 最近邻 | 它做了什么 | RCBT 必须证明的不同 |
|---|---|---|
| BAS-VLA | 同一任务内，任务保持变化 vs 语义破坏变化的动作校准 | RCBT 跨任务迁移偏差统计；BAS-VLA 不回答“旧任务的偏差能否借给新任务” |
| Residual Policy Adaptation | 任务专属 SE(3) 残差头，小样本装配 | RCBT 不训练任务头；它估计可迁移的偏差场并做风险门控 |
| ORPA | 在线反馈条件残差，关节空间适配 | RCBT 是部署前/少样本的跨任务先验，不是在线反馈控制器 |
| Policy-Induced Hand Priors | 诊断初始位姿依赖的双手先验，数据增广缓解 | RCBT 是一般偏差场迁移框架；该文只做一个偏差且靠训练数据缓解 |
| Evidence-Guided Counterfactual Learning | 长尾任务 head-task 动作偏差，反事实训练 | RCBT 冻结策略、部署时补偿；不依赖重训练 |
| Paraphrase Consensus | 聚合降方差但不消除共享偏差 | RCBT 不聚合；它用参考类估计并补偿共享偏差 |
| 检索增强 VLA（RICL/RAGu/R2A） | 检索示范、轨迹或运动基元来条件化动作生成 | RCBT 检索的是历史偏差统计/结果，不是动作示范；对象是误差场 |
| 工业误差相似性 | 几何/柔顺误差的空间插值与补偿参数迁移 | RCBT 把“空间相似”换成“因果任务相似”，对象是策略动作偏差 |
| 外部视角/参考类预测 | 用同类历史结果校正项目预测 | RCBT 把它用于具身策略的偏差场与动作补偿（是否首见需查新确认） |

**与 codex 当前路线的边界（避免并行冲突）：**

| 维度 | codex 当前 D/D′ | RCBT |
|---|---|---|
| 对象 | 可执行策略契约、动态误差集合、任务 margin | 跨任务动作偏差场的统计迁移 |
| 数据 | action metadata、chunk timing、controller convention、rollout | 重复标定 episode、任务因果描述子、偏差统计 |
| 输出 | 部署前接受/拒绝/受限补偿证书 | 偏差场预测、补偿/弃权、迁移风险 |
| 验证 | 同体 executable equivalence、覆盖率 | 留一任务预测、因果 vs 视觉参考类、负迁移 |
| 关系 | 可作 RCBT 的执行层前置检查 | 不重复证书；不声称 executable equivalence |

### 3.6 工业与认知映射

| 工业精度补偿 | RCBT | 认知对应 |
|---|---|---|
| 激光跟踪仪稀疏测量 | 少量标定 episode 测量偏差 | 外部视角取样 |
| 误差相似性/空间插值 | 因果任务相似度 + 分层 GP | 参考类预测 |
| 几何误差 vs 随机重复性 | 偏差场 $b_t$ vs 噪声场 $\Sigma_t$ | 偏差 vs 噪声 |
| 逐台标定表 | 逐任务偏差场 | 个案直觉 |
| 补偿参数跨相似机器人迁移 | 偏差场跨相似任务迁移 | 从同类任务学习 |
| 补偿后 residual 验证 | 后验方差/留出验证 | 慢系统复核 |
| 按外观选相似机床（错误） | 按视觉相似选参考任务（错误） | 代表性启发 |

工业侧可引用的直接先例（题名/DOI 已核，全文待读）：

- [Error compensation of industrial robot based on deep belief network and error similarity](https://doi.org/10.1016/j.rcim.2021.102220)
- [A positional error compensation method combining error similarity and RBF](https://doi.org/10.1088/1361-6501/ab3311)
- [Error Similarity Analysis and Error Compensation with TCP Calibration Uncertainties](https://doi.org/10.3390/app13042722)
- [Transferability of compliance error compensation parameters in articulated robots](https://doi.org/10.1016/j.cirp.2025.03.018)

这些来源证明“误差相似性 + 稀疏测量 + 参数迁移”在工业上成立；
**它们不证明 VLA 动作偏差也如此**——这正是 RCBT 要检验的经验命题。

### 3.7 最小可证伪实验（2 周 pilot）

**载体**：SO-101 MuJoCo；冻结 SmolVLA 或 OpenVLA 兼容策略；单 A100 推理。
不先上真机，不训练大模型。

**任务族**：用 3 个二值任务因子构造 8 个任务（避免 16 个以上）：

- 物体功能：抓取 vs 推动；
- 目标关系：左/右或前/后；
- 障碍/接触：无遮挡 vs 轻接触约束。

每个任务采 6–10 个上下文（物体初始位姿/目标位置），每上下文重复 5 次固定随机流。
用脚本化控制器或 IK 参考给出 $a_t^{\ast}(c)$；若参考不可得，用“同上下文重复均值
相对规范上下文的位移”作为偏差代理，并明确其局限。

**测量**：

1. 估计 $b_t(c)$ 与 $\Sigma_t(c)$；检查系统性分量是否大于重复噪声（H1）。
2. 计算 8×8 偏差场距离矩阵；与因果任务描述子距离、视觉嵌入距离分别做
   Mantel/回归比较（H3）。
3. 留一任务：用其余 7 个任务拟合分层 GP，预测被留出任务的偏差场；
   比较零偏差、任务局部 GP（只用该任务 0/1/3/5 个标定 episode）、
   视觉参考类 GP、因果参考类 GP、oracle（H2）。
4. 在留出任务上做闭环补偿，测成功率/终点误差/负迁移率（H4）。

**强基线**：

- 不补偿；
- 任务局部 GP/线性残差（与 BAS-VLA/Residual Policy Adaptation 同信息预算）；
- 视觉相似参考类；
- 全局单任务 GP（无分层）；
- 直接微调/任务头（若算力允许，单列，不作为同预算对照）；
- oracle 偏差场（上界，不作部署比较）。

**预注册主终点**：H1–H3（偏差可测、留一任务可迁移、因果相似性优于视觉相似性）。
H4 的闭环补偿只作最小检查：留出任务 3 个标定 episode 下的成功率/终点误差、
负迁移率、后验覆盖率；不在 2 周内做正式功效承诺。

**2 周 go/no-go**：

- 第 1–3 天：策略可运行性、动作/观测时序、参考动作可得性；
- 第 4–6 天：偏差场测量与重复性；
- 第 7–9 天：8×8 相似性矩阵与因果/视觉对比；
- 第 10–12 天：留一任务迁移与补偿；
- 第 13–14 天：强基线、失败案例分析、是否进入真机的决定。

若第 6 天偏差场不可重复，停止；若第 9 天因果相似性不优于视觉相似性，
改写为“外观参考类也会失败”的诊断论文或转 OVDC；若第 12 天迁移收益被
任务局部 3-shot 标定完全吸收，停止方法主张。

### 3.8 真机怎么接

真机只验证同一个命题，不换成“展示视频”：

- 选 2 个任务（一个高相似、一个低相似），在同一 SO-101、同一低层位置控制、
  同一相机/频率下测偏差场；
- 用 [SO-101 标定工具](https://github.com/fport/so101-calibrator) 固定关节零点/量程；
- 用 [SO-101 SmolVLA 复现包](https://github.com/Shaibk/so101-smolvla-thesis) 作为
  可行性参照（其公开报告在简单抓取任务上 62%–73% 成功率，说明载体可达）；
- 真机必须分别记录命令、实际关节、夹爪、物体终点和任务谓词；
  不能把低层跟踪误差直接当成策略偏差场；
- 若真机偏差主要由机械回差/温漂解释，先修载体或把主张限制在仿真，
  不把执行误差包装成认知偏差。

### 3.9 理论增量（不是“加一个 GP”）

RCBT 要能写成论文，至少需要以下之一：

1. **可迁移性判据**：给出偏差场迁移风险的界，说明它由因果任务相似度、
   参考类样本量、任务特异常数和噪声方差共同决定；给出负迁移发生的充分条件。
2. **参考类选择定理/反例**：证明按视觉相似性选参考类在何种任务结构下
   会系统性劣于因果相似性（代表性启发的形式化）。
3. **可识别性**：说明偏差场与噪声场、共享分量与任务特异分量在什么观测条件下可分离；
   没有重复测量/参考动作时不可识别。
4. **样本复杂度**：分层迁移相对任务局部标定的样本效率收益，以及收益消失的边界。

如果只能做“分层 GP + 实验”，没有上述任何一条，则它仍是工程组合，
不应作为核心创新主张。

### 3.10 可行性

- **策略**：SmolVLA（约 0.5B）在单 A100 可推理；OpenVLA 7B 需 bf16/量化。
  [LeRobot](https://github.com/huggingface/lerobot) Apache-2.0；
  [OpenVLA](https://github.com/openvla/openvla) MIT。
- **SO-101 资产**：项目已有 MuJoCo 场景与资产固定版本；本地/云端 CI 已跑通渲染与短轨迹。
- **标定工具**：[fport/so101-calibrator](https://github.com/fport/so101-calibrator) MIT。
- **可行性参照**：[Shaibk/so101-smolvla-thesis](https://github.com/Shaibk/so101-smolvla-thesis)
  Apache-2.0，公开了 SO-101 + SmolVLA 的数据采集、标定、A100 训练命令与真机结果。
- **不确定性基线**：[learnsyslab/uq_vla](https://github.com/learnsyslab/uq_vla) Apache-2.0，
  可作 VFD/epistemic uncertainty 对照；其真实机器人代码不公开，不能当 SO-101 基线。
- **算力**：偏差场测量是重复推理，不需要大训练；A100 足够 pilot。

### 3.11 主要风险

| 风险 | 表现 | 处理 |
|---|---|---|
| 偏差不可测 | 重复噪声大于系统性偏差 | 先做 H1；不可测则停止或换更结构化的任务 |
| 偏差不可迁移 | 留一任务预测不如零偏差 | H2 失败；转任务局部标定或 OVDC |
| 外观相似性也有效 | H3 不成立 | 放弃“代表性启发”故事，退回普通相似性迁移 |
| 执行误差混淆 | 真机偏差主要来自低层跟踪/回差 | 仿真先做机制；真机分离命令/实际/物体终点 |
| 任务局部 3-shot 已足够 | 迁移收益被吸收 | 停止方法主张；把迁移矩阵作为诊断资产 |
| 与 BAS-VLA/Residual 太近 | 审稿人说“又一个校准器” | 论文主线必须是“可迁移性规律”，不是补偿器 |
| 组合式主张被相关性击穿 | 模块校准不组合 | 引 [Marginal Calibration Does Not Compose](https://arxiv.org/abs/2609.23731)，用联合协方差/留出验证 |

### 3.12 查新关键词（给机构查新用）

中文：

> 具身智能；视觉-语言-动作模型；系统性动作偏差；偏差场；误差相似性；
> 参考类预测；外部视角；跨任务迁移；分层贝叶斯；部分池化；负迁移；
> 机器人精度补偿；误差场插值；任务因果结构。

英文：

> vision-language-action; action bias field; systematic action error;
> reference class forecasting; outside view; cross-task calibration transfer;
> error similarity; hierarchical Gaussian process; partial pooling;
> negative transfer; task-conditioned bias; causal task similarity.

组合式：

```text
("vision-language-action" OR VLA) AND ("bias field" OR "systematic action error")
  AND ("transfer" OR "reference class" OR "cross-task")

("robot policy" OR "manipulation policy") AND ("calibration transfer" OR "error similarity")
  AND ("hierarchical" OR "partial pooling" OR "meta-learning")

("embodied" OR "robot") AND ("representativeness heuristic" OR "base rate neglect")
  AND ("calibration" OR "decision")
```

需要人工复核的数据库：Google Scholar、IEEE Xplore、ScienceDirect、SpringerLink、
CNKI/万方（中文“具身智能 认知偏差 补偿”“机器人 误差场 迁移”“参考类预测 机器人”）。

### 3.13 三条门槛的自评

| 门槛 | 当前证据 | 还缺什么 | 判断 |
|---|---|---|---|
| **查新** | OpenAlex 精确检索 `"bias field" robot policy`、`"systematic action bias" robot` 为 0；跨任务偏差场迁移无直接命中；最近邻是任务局部校准/残差 | 全文精读 BAS-VLA/ACR-VLA/Policy-Induced/Evidence-Guided；CNKI/万方；引用链与后续版本 | **有候选空间，未通过** |
| **可行性** | SO-101 MuJoCo 已通；SmolVLA/OpenVLA 单 A100 可推理；SO-101 SmolVLA 复现包公开；偏差测量只需重复推理 | 冻结策略能否稳定出偏差；参考动作/重复性；2 周 pilot | **高，但需预检** |
| **先进性** | 把“任务局部校准”升级为“跨任务偏差场可迁移性”的科学命题；有工业误差相似性与卡尼曼参考类两条理论支撑 | 迁移风险界/参考类选择定理/可识别性；否则只是分层 GP 工程 | **有潜力，取决于理论增量** |
| **当下突出问题** | VLA 分布移位脆弱、逐任务标定昂贵、负迁移风险 | 证明迁移收益不被 3-shot 局部标定吸收 | **对口** |
| **突破条件** | 若 H2+H3 成立：偏差场沿因果任务结构可迁移，可用少量标定借用旧任务经验 | 真机同命题验证；跨策略/跨本体外推 | **有机会，但不保证** |

---

## 4. 备选 1：外部视角决策校准（OVDC）

### 4.1 一句话

> 给具身策略一个“外部视角”：用因果参考类的历史结果估计任务基率，
> 校正 VLA 的过度自信与基率忽视，决定行动、弃权还是求助。

### 4.2 研究问题

> 在任务类别移位下，参考类结果基率能否比标量置信校准（temperature/Platt/conformal）
> 更好地校正 VLA 的成功预测与弃权决策？

### 4.3 机制

- 情节记忆：任务指令、初始场景、执行轨迹、结果、上下文变量；
- 参考类：因果任务描述子检索 K 个历史任务/情节；
- 分层贝叶斯：参考类基率 + 当前任务少量结果 → 后验成功概率；
- 决策：接受/弃权/求助，按代价权衡。

### 4.4 与最近邻的差异

- `When Does Retrieval Help?`（2610.05492）、RAGu（2611.10894）、R2A（2610.37215）
  检索的是**示范/动作/轨迹**；OVDC 检索的是**历史结果基率**，用于校准决策。
- Confidence Calibration in VLA 校准的是策略自己的分数；OVDC 补的是分数看不到的
  任务基率与参考类偏差。
- RADAR（2610.22139）在 LLM 上分解置信风险；OVDC 把它移到具身决策并引入因果参考类。

### 4.5 评价

认知链路最纯（外部视角、基率忽视、代表性），但“动作补偿”弱，且容易被看成
“检索 + 校准”。适合作 RCBT 失败后的备选，或 RCBT 的第二篇论文（决策层）。

---

## 5. 备选 2：偏差—噪声预算分配（BNBA）

### 5.1 一句话

> 固定测试时预算下，先判断当前错误是**可补偿的系统偏差**还是**可聚合的噪声**，
> 再决定补偿、多次采样还是弃权。

### 5.2 为什么降级

`Paraphrase Consensus` 已明确“聚合降方差但不消除共享偏差”。
BNBA 的新意只剩**可识别性 + 预算分配**，容易被审稿人视为该文的扩展。
如果要做，必须证明：

- 偏差/噪声比可从可观测数据识别；
- 标量不确定性无法区分两种状态；
- 分配规则在匹配预算下优于固定策略，并有 crossover 实验。

### 5.3 与 RCBT 的关系

BNBA 可以作为 RCBT 的**干预选择层**：RCBT 估计偏差场，BNBA 决定是否值得补偿；
但论文主线仍应是 RCBT 的迁移规律，而不是“又一个测试时策略”。

---

## 6. 备选 3：具身评测噪声审计（EENA）

### 6.1 一句话

> 用方差成分/Gage R&R 审计 VLA 评测：报告的性能差异有多少来自任务采样、
> 环境随机性、策略种子、评审噪声，而非策略本身？

### 6.2 价值与问题

- 价值：当前 benchmark 样本小、方差大；“噪声审计”能改变实践，符合卡尼曼《噪声》。
- 问题：偏方法学，不是动作补偿方法；与 codex 正在做的统计功效/置信区间工作重叠；
  benchmark 类贡献可能被 LIBERO-Pro/LIBERO-X 等竞品贬值。
- 建议：作为 RCBT 的实验规范附件，不单独作为主方向。

---

## 7. 不推荐：WYSIATI 信息缺口主动补全（WAIG）

### 7.1 一句话

> 检测 VLA 的失败是否来自“未表征的缺失信息”（遮挡、未知约束），
> 触发查看/探测动作，而不是继续重采样。

### 7.2 为什么不推荐

- 与主动诊断（Fly-by-Code 等）、主动感知/下一最佳视角、POMDP 信息收集高度重叠；
- 项目已否决主动诊断宽题；WYSIATI 命名不足以构成新机制；
- 真机需要可控视角/探测动作，工程复杂度高于 RCBT。

---

## 8. 评分与建议

| 维度（1–5） | RCBT | OVDC | BNBA | EENA | WAIG |
|---|---:|---:|---:|---:|---:|
| 与已有工作的区分度 | 4 | 4 | 2 | 3 | 2 |
| 科学性/可证伪性 | 5 | 4 | 4 | 3 | 3 |
| 与项目主线（认知标定）契合 | 5 | 4 | 4 | 3 | 4 |
| 工业补偿类比契合 | 5 | 2 | 4 | 2 | 2 |
| SO-101/A100 可行性 | 4 | 4 | 5 | 4 | 2 |
| 2 周内能否得到否证信号 | 4 | 4 | 4 | 5 | 2 |
| 论文上限 | 高 | 中高 | 中 | 中 | 中 |

**建议：**
1. 以 **RCBT** 作为主候选，先做 2 周 pilot；只回答 H1–H3，不先写完整方法。
2. 若 H2/H3 成立，再投入真机与 H4；若失败，转 **OVDC**（同一参考类资产，改决策层）。
3. **BNBA** 只作为 RCBT 的干预选择层，不单独立项。
4. **EENA** 作为实验规范，不作为主方向。
5. **WAIG** 不启动。

**不能说的话：**
- 不能说“首次校准 VLA”“首次补偿 VLA 动作偏差”“填补具身认知空白”；
- 不能说“工业精度补偿已迁移到具身智能”；
- 不能说“查新通过”；本文只是预筛；
- 不能把“测量—建模—补偿—验证”流程本身当创新；
- 不能把动态证书/可执行等价性重新包装进 RCBT。

---

## 9. 下一步（建议顺序）

1. **全文精读 6 篇**：BAS-VLA、ACR-VLA、Paraphrase Consensus、Policy-Induced Hand Priors、
   Evidence-Guided Counterfactual Learning、Residual Policy Adaptation；
   逐段核对它们是否已有跨任务偏差迁移或参考类选择。
2. **追引用链**：上述 6 篇的施引文献 + 2026 年 arXiv 最新版本；
   重点搜 `bias field`、`cross-task calibration transfer`、`reference class`。
3. **中文查新**：CNKI/万方按 §3.12 关键词检索，记录命中与差异。
4. **工程预检**：确认 SO-101 MuJoCo 场景能稳定跑冻结策略；
   测重复性、动作/观测时序、参考动作可得性。
5. **冻结 pilot 协议**：8 任务、每任务 6–10 上下文、每上下文 5 次重复；
   先注册主终点与分析规则，再跑。
6. **2 周后裁决**：H1/H2/H3 的证据是否支持继续；不支持则按 §3.11 停止或转 OVDC。

---

## 附录 A：主要来源清单（按核验程度）

**已读摘要/README，机制较确定：**

- Confidence Calibration in VLA — arXiv:2507.17383；TMLR；代码 `thomaspzollo/vla_calibration`
- BAS-VLA — arXiv:2609.23650；NeurIPS 2026；代码 `NEBULIS-Lab/Beyond-Appearance-Shifts`
- ACR-VLA — GitHub `anonymous-nlp-2026/...`（无许可证）
- Paraphrase Consensus Is Not Self-Consistency — arXiv:2610.19438
- Policy-Induced Hand Priors — arXiv:2608.11769
- Evidence-Guided Counterfactual Learning — arXiv:2610.12861
- Residual Policy Adaptation for VLA — figshare DOI 10.6084/m9.figshare.31329868
- ORPA — arXiv:2608.17323
- When Does Retrieval Help? — arXiv:2610.05492
- R2A — arXiv:2610.37215
- RAGu — arXiv:2611.10894
- Marginal Calibration Does Not Compose — arXiv:2609.23731
- Audit Before You Commit — arXiv:2609.30608
- RADAR — arXiv:2610.22139
- GUARD — arXiv:2608.04510
- VLA-Tug — arXiv:2611.08425
- Deployment-Time Reliability of Learned Robot Policies — arXiv:2603.11400
- Temporal Difference Calibration — arXiv:2604.20472
- Hume — arXiv:2505.21432
- DP-VLA — arXiv:2410.15549
- RFST — ICRA 2024, DOI 10.1109/ICRA57147.2024.10611525

**题名/DOI 已核，全文待读：**

- Error compensation based on DBN and error similarity — DOI 10.1016/j.rcim.2021.102220
- Positional error compensation combining error similarity and RBF — DOI 10.1088/1361-6501/ab3311
- Error Similarity Analysis with TCP Calibration Uncertainties — DOI 10.3390/app13042722
- Transferability of compliance error compensation parameters — DOI 10.1016/j.cirp.2025.03.018
- A method for the assessment and compensation of positioning errors in industrial robots — DOI 10.1016/j.rcim.2023.102622

**工程来源：**

- LeRobot — `huggingface/lerobot` Apache-2.0
- OpenVLA — `openvla/openvla` MIT
- UQ-VLA — `learnsyslab/uq_vla` Apache-2.0
- SO-101 SmolVLA thesis repro — `Shaibk/so101-smolvla-thesis` Apache-2.0
- SO-101 calibrator — `fport/so101-calibrator` MIT

## 附录 B：检索记录（可复核）

- 2026-11-14：Google Scholar 两条查询均返回 429；未使用 Scholar 摘要或引用数。
- OpenAlex：`vision-language-action policy calibration`、`robot manipulation policy error compensation`、
  `action bias correction imitation learning`、`spatial error field compensation robot`、
  `Gaussian process error compensation robotic manipulator`、`policy residual correction VLA`、
  `test-time calibration robot policy`、`systematic error learning robot manipulation`。
- OpenAlex 精确标题/摘要：`"vision-language-action" bias/calibration`、`"embodied" "cognitive bias"`、
  `"dual-process" robot`、`"System 1" "System 2" robot`、`"debiasing" embodied`、
  `"anchoring bias" vision-language`、`"decision noise" machine learning`、
  `"reference class forecasting"`、`"noise audit"`、`"bias-variance" policy robot`、
  `"error field" manipulation`、`"Gaussian process" residual policy`。
- OpenAlex 迁移/结构：`cross-task error prediction`、`transferable error model`、
  `task-conditioned residual`、`meta-learning residual compensation`、
  `few-shot calibration robot`、`task similarity transfer policy calibration`、
  `hierarchical Gaussian process multi-task`、`compositional bias robot`、
  `compositional error model robot`、`error composition robot calibration`。
- arXiv API：`all:"vision-language-action" AND all:"bias"/"noise"`、
  `all:"robot policy" AND all:"systematic"`、`all:"test-time" AND all:"robot" AND all:"policy"`、
  `all:"calibration" AND all:"vision-language-action"`、
  `all:"error compensation" AND all:"learning" AND all:"robot"`、
  `all:"reference class" AND all:"decision"`、`all:"outside view" AND all:"forecast"`、
  `all:"bias" AND all:"noise" AND all:"decision"`。
- GitHub API：`VLA calibration`、`robot policy calibration`、`vision language action uncertainty`、
  `action correction VLA`、`robot error compensation`、`test-time adaptation robot manipulation`、
  `bias correction robot learning`、`Gaussian process robot compensation`、
  `SO-101 calibration`、`SmolVLA calibration`。
- 说明：OpenAlex 宽词命中量很大；本文只把**题名/摘要高度相关**的条目列入近邻表，
  未把搜索摘要当作全文结论。
