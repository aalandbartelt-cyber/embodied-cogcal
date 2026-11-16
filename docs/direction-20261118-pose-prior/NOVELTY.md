# 查新预检：方向 A 的主张边界、近邻矩阵与重定位

日期：2026-11-18 · 状态：**预检完成；正式查新须由机构在 Scholar/CNKI/WoS 复跑**
关联：[DIRECTION.md](DIRECTION.md) · 证据：[E4 RESULTS](../../experiments/discovery/e4-appearance-contact-20261118/RESULTS.md)、
[ANCHOR_PROBE](../../experiments/discovery/e2-size-tolerance-20261118/ANCHOR_PROBE.md)、
[E2 RESULTS](../../experiments/discovery/e2-size-tolerance-20261118/RESULTS.md)

> 本文件只做一件事：判定**哪些句子可以写、哪些已被占、还差什么证据**。
> 它不改变任何实验结论，也不把"没搜到"当成"不存在"。

## 0. 一页结论

**三条裁决**

1. **"锚定"解释线已被占。** Malili 2026（[arXiv 2611.17658](https://arxiv.org/abs/2611.17658)）
   已给出"本体锚 + 可靠性加权 + 闭环放大"的完整解释与预测律；Zhao 2025
   （[arXiv 2509.18644](https://arxiv.org/abs/2509.18644)）已给出"本体状态捷径导致空间泛化差"；
   GAP（[arXiv 2602.12032](https://arxiv.org/abs/2602.12032)）已给出"本体梯度压制视觉学习"的机制与缓解。
   → **不能把"发现策略锚定""解释闭环放大"写成贡献**；只能引用，并把差异写死（§7 Q1–Q2）。
2. **方法侧拥挤。** 等变策略/等变扩散头：EquiBim（[IROS 2026](https://github.com/ZhangZhiyuanZhang/lerobot-equibim)）、
   E3Flow（[CVPR 2026 Highlight](https://github.com/zql-kk/E3Flow)）、VISTA（[CoRL 2026](https://github.com/Kenn3o3/Vista)）、
   Pix2Act（[arXiv 2607.11167](https://arxiv.org/abs/2607.11167)）、KeyGen（[arXiv 2609.28818](https://arxiv.org/abs/2609.28818)）；
   规范化/物体系动作框架（[Oriented Affordance Frames, arXiv 2410.12124](https://arxiv.org/abs/2410.12124)）；
   测试期纠偏：RTCF（[arXiv 2608.04527](https://arxiv.org/abs/2608.04527)）、ARC（[arXiv 2610.37547](https://arxiv.org/abs/2610.37547)）、
   TATE（[标定侧取向校正](http://agentic-intelligence-lab.org/files/TATE.pdf)）。→ **不做新架构、不做通用纠偏器。**
3. **仍可守的四块空白**（按证据强度排序）：

| 编号 | 空白 | 最近邻 | 本轮判定 |
|---|---|---|---|
| **T1** | **位精确孪生归因**：同一 RGB、只改碰撞几何（及反向），把失败归因到接触几何 | causal confusion（数据集级）、sim2real 外观随机化；未见"字节级同图 + 物理单变量"设计 | **clear（本轮未命中）**；E4 已有 20/20 vs 0/20，Fisher p=7.25e-12 |
| **T2** | **通道分辨的取向增益**：γ_rot≈0.004 与 g≈1 的数量级各向异性，纯 FK、无成功标签 | 增益比探针已存在（2611.17658，位置/噪声通道） | **adjacent**：方法不新，通道与各向异性对照新 |
| **T3** | **(δ,θ) 二维容差包络 + 两通道阶段分解**：15° 硬悬崖（全 δ ≤0.10）、θ\*≈11.7–12.6°（δ≤10 mm）、δ≈14 mm 由可达余量接管（0° 基线 0.50）；交互 d<0 仅在可达区成立（GEE −0.27，E3 全窗口为正的 δ=14 天花板伪影） | LIBERO-Plus（[CVPR 2026](https://www.openaccess.thecvf.com/content/CVPR2026/papers/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR_2026_paper.pdf)，7 类扰动/21 子维、L1–L5 阶梯、聚合成功率）；抓取/装配容差解析文献 | **adjacent（已测 2026-11-17 凌晨，E3/E3b）**：阶梯≠二维边界，聚合≠阶段归因；但 θ\* 五点斜率 CI 跨零（INCONCLUSIVE），只能主张"边界形状 + 两通道"，不主张"平滑收缩" |
| **T4** | **由增益导出的单参数指令侧补偿**：q5 偏置，dφ/dq5=1.0000；无记忆、无重训、无新增演示 | RTCF（检索成功轨迹、低频残差）、ARC（人类纠正残差）、TATE（标定侧取向校正） | **adjacent**：需 E5′ 过 50% 才成立；须与"naive 固定偏置"对照 |

**方向 A 判定：有条件通过预检。** 条件缺一即降级（§8）：

- **E5′** 在 θ=15° 把成功率拉过 50%，且 θ=0° 不降 → 否则 C4 删除，只剩诊断论文；
- **E3** 交互项 d<0 且 ΔAIC 支持 → **半触发（2026-11-17 凌晨）**：全窗口 d>0 是 δ=14 天花板伪影，
  剔除后可达区 d<0，但 θ\* 五点斜率 CI 跨零 → T3 降级为"边界形状 + 两通道失败"，
  不主张"二维交互/平滑收缩"；
- **至少一个外部效度点**（第二物体或第二 seed 重训）→ 否则单策略/单物体是硬伤；
- 论文自我定位为**测量—归因—补偿的校准研究**：不是基准、不是架构、不是"发现认知偏差"。

**术语避碰（必须执行）**：本文把取向响应增益记作 **γ**（gamma），不再用 α——α 已被
2611.17658 用作噪声-读数增益比；`anchoring` 只作为他人术语引用（本体锚、ResVLA 的生成锚定
[arXiv 2604.21391](https://arxiv.org/abs/2604.21391)），不用于命名本文方法。

## 1. 检索记录（通道、式、命中）

通道：平台 web 检索（DeepSeek 检索端点）、arXiv HTML 全文、GitHub REST API。
**限制**：Google Scholar 在本机仍为验证拦截（与 2026-11-16 记录一致）；CNKI/WoS 不可达；
GitHub 代码搜索需登录，只查了仓库。因此本文件是"预检"，不是查新报告；正式查新用 §10 的式复跑。

| # | 检索式（摘要） | 通道 | 关键命中 | 对本文的用途 |
|---|---|---|---|---|
| 1 | rotation equivariance imitation learning manipulation | web | SEIL、Pix2Act、KeyGen、EfficientFlow | 确认方法侧拥挤 |
| 2 | "object orientation" generalization behavior cloning failure | web | LIBERO-Plus、TATE | 确认"取向泛化"已有基准化 |
| 3 | manipulation policy tolerance envelope robustness | web | LIBERO-Plus、KIT 位姿容差实验 | 确认"容差"多为离散阶梯/硬件设计 |
| 4 | industrial robot precision error compensation | web | [IEEE 综述 11131700](https://ieeexplore.ieee.org/abstract/document/11131700)、[MDPI 标定](https://www.mdpi.com/2313-7673/11/3/171) | 工业补偿的类比锚点 |
| 5 | "Thinking, Fast and Slow" cognitive bias robot policy | web | Fast-in-Slow（[NeurIPS 2025](https://papers.neurips.cc/paper_files/paper/2025/hash/8cf3760422b9d4505589a97c8f9569e7-Abstract-Conference.html)） | 确认 System 1/2 已被架构化 |
| 6 | test-time orientation canonicalization ACT SO-101 | web | TATE、Oriented Affordance Frames | 确认"推理侧校正"已有先例 |
| 7 | "response gain" / "input sensitivity" frozen policy | web | **2611.17658**、2509.18644、GAP | 最关键近邻，逐条核原文 |
| 8 | "anchoring effect" imitation learning robot prior | web | 2611.17658、ResVLA | 术语已被占 |
| 9 | LIBERO-Plus perturbation dimensions | web | LIBERO-Plus 论文 PDF | 确认 7 类/21 子维、L1–L5 |
| 10 | test-time action correction frozen policy | web | RTCF、ARC | 确认纠偏侧拥挤 |
| 11 | github equivariant manipulation policy | **GitHub API** | EquiBim、E3Flow、VISTA、SO(3) Transformer | 确认工程生态成熟 |
| 12 | orientation sensitivity / yaw behavior cloning | web | 无直接命中；DSP、Oriented Affordance Frames | 取向增益的直接测量仍空 |

全文核读：2611.17658（摘要、§1–§5.4、附录说明；与
[DIRECTION_ANCHOR_AUDIT](../report/DIRECTION_ANCHOR_AUDIT_20261116.md) 的逐条核对一致）。
LIBERO-Plus 只读了摘要与正文片段，**"是否包含物体位姿子维"待正式查新时核对原表**（§7 Q3）。

## 2. 近邻矩阵

| 工作 | 它做了什么 | 与本文重叠 | 本文必须写出的差异句 | 威胁 |
|---|---|---|---|---|
| **Malili 2026**（2611.17658） | 噪声观测下策略学本体锚；α=V/(V+s²) 预测十个噪声档；闭环 ρ>α；α 低→成功率低 | "策略对视觉读数打折"、增益比探针、闭环响应 | "该文处理**噪声**与位置通道，s=0 时预测 α=1；本文处理**确定性取向变化**，测得 γ≈0.004 且不随闭环回升，失败由接触几何而非读数权重解释" | **高**（解释线被占） |
| **Zhao 2025**（2509.18644） | 本体状态输入导致轨迹记忆与空间泛化差；提出 state-free | "策略忽略视觉、按训练轨迹行动" | "该文用**去掉本体输入**证明捷径存在；本文不训练、不改输入，用**增益与孪生**定位取向通道并给出补偿" | 高（现象解释被占） |
| **GAP**（2602.12032） | 本体梯度压制运动过渡段的视觉定位；梯度调节缓解 | "视觉定位被压制" | "该文在学习侧改梯度；本文在**推理侧**测增益并补偿，不重训" | 中 |
| **LIBERO-Plus**（CVPR 2026） | 7 类扰动/21 子维、L1–L5、10,030 实例；聚合成功率排名 | 受控扰动评测 | "该文是**模型排名基准**，扰动离散分级、只报成功率；本文给**连续二维边界 + 阶段归因 + 机制解耦**，并给补偿" | 中高（易被说成"更细的鲁棒性评测"） |
| **RTCF**（2608.04527） | 冻结 VLA 外挂检索+低频残差纠偏，LIBERO 86.4→88.4 | 测试期纠偏、冻结策略 | "RTCF 需要**成功轨迹记忆**、纠的是运动残差；本文只需**一次增益标定**，补的是解析关节偏置，且给出补偿量预测" | 中高 |
| **ARC**（2610.37547） | 人类纠正定义时间/动作支撑，残差 RL | 测试期纠正 | "ARC 需要**人类在环**；本文无人类、无 RL、无新数据" | 中 |
| **EquiBim/E3Flow/VISTA/Pix2Act/KeyGen** | 等变网络/等变扩散/规范化表示 | 旋转泛化 | "它们**改架构**使策略等变；本文测量**冻结非等变策略**的取向增益并补偿，回答'不重训能救多少'" | 中（占方法侧，不占诊断侧） |
| **Oriented Affordance Frames**（2410.12124） | 物体系动作框架提升 OOD 取向成功率 | 取向泛化 | "它换**动作坐标系**；本文不改坐标系，测的是同一坐标系内的响应增益与偏置" | 中 |
| **TATE** | 遥操作标定把 ego 视频映射到机器人动作，含任务级取向校正 | 标定侧取向校正 | "TATE 校的是**数据标签**；本文校的是**策略输出**，且补偿量由实测增益导出" | 低中 |
| **Fast-in-Slow**（NeurIPS 2025） | 双系统 VLA：慢推理+快执行 | System 1/2 叙事 | "它是**架构**；本文的 System 2 是**外部标定回路**，不进入策略" | 低（叙事撞车） |
| **工业误差补偿综述**（IEEE 11131700） | 几何/非几何误差分类；模型/数据/混合三类补偿 | 补偿范式 | "本文把策略的姿态先验当作**系统误差源**，走'辨识→建模→预补偿'同一范式；不声称工业级精度" | 类比合法性 |
| **抓取/装配容差文献** | 位姿误差容差、间隙迁移、factorial 设计 | 容差实验 | "工程侧容差研究针对**硬件/规划**；本文针对**学习策略的行为**，且用阶段分解定位失败" | 低中 |

## 3. 主张阶梯 v2（含查新状态与降级写法）

| 编号 | 主张 | 最近邻 | 查新判定 | 现有证据 | 降级写法（若审稿人压） |
|---|---|---|---|---|---|
| **C1′** | 冻结策略的**取向**响应增益 γ≈0.004，与位置增益 g≈1（支撑内）/0.19（支撑外）形成数量级各向异性；纯 FK、无需成功标签 | 2611.17658（位置/噪声增益比） | **adjacent** | E1′/E2 七档偏航一致；0°→45° 闭合轴 0.17° | "我们把已有的增益探针**扩展到取向通道**，得到首个通道分辨的各向异性数字"——不写"首次测量策略敏感性" |
| **C2′** | θ=15° 的失败由**接触几何**承担：只改碰撞体 0/20，只改外观 20/20；配对种子逐条确定 | causal confusion、sim2real 随机化 | **clear（待正式查新确认）** | E4：18/20、20/20、0/20、1/20；p=7.25e-12；842 项校验；RGB 逐 seed 等式 | "我们用**位精确孪生**做单变量归因"——不写"首次解耦外观与物理" |
| **C3′** | 容差包络是 (δ,θ) 二维曲面：15° 对 δ=2–14 mm 全为硬悬崖（≤0.10）、θ\*≈11.7–12.6°（δ≤10 mm）、δ≈14 mm 由可达余量接管（0° 0.50）；失败阶段随 θ 从"抬升失败"移向"放置失败" | LIBERO-Plus 阶梯；工程容差 | **adjacent** | E3/E3b 已测（400 集）；θ\* 五点斜率 CI 跨零（INCONCLUSIVE）；GEE 交互可达区 −0.27 | "二维连续边界 + 阶段归因，比离散 severity 阶梯多出**形状与阶段**信息；但不主张边界随偏移收缩**" |
| **C4′** | 指令侧 q5 偏置（θ̂，dφ/dq5=1.0000）把 15° 成功率从 1/20 拉过 50%，0° 不降 | RTCF/ARC/TATE | **adjacent，未验** | ANCHOR_PROBE §5；E5′ 待跑 | 若 E5′ 失败：删 C4，论文只留 C1′–C3′ 诊断贡献，投 workshop/短文 |
| **C5′** | "测量→归因→建模→补偿"可复用的校准协议 + 位精确可复现工件（842 项校验） | 预注册/可复现性文献 | **clear-ish** | verify_e4 842/842；sha 链 | 作为**方法学贡献**而非主结果 |

## 4. 重定位后的方向陈述

**标题（候选）**

- EN: *Calibrating the Pose Prior: Measuring, Attributing, and Compensating a Frozen
  Visuomotor Policy's Orientation Blind Spot*
- EN（偏认知）: *System-2 Calibration for System-1 Policies: Gain-Based Diagnosis and
  Compensation of Orientation Failure*
- 中文：《冻结策略的姿态先验校准：取向响应增益、接触归因与指令侧补偿》

**一句话论点**

> 冻结 ACT 策略对物体朝向的响应比位置弱约两个数量级；它的偏航失败不是"没看见"，
> 而是"没转腕"导致的接触几何碰撞；用一个由实测增益解析导出的关节偏置即可把容差
> 拉回——姿态先验因此是一个**可测量、可归因、可补偿的系统误差源**，正好落在工业
> 精度补偿"辨识→建模→预补偿"的范式里，而外部的标定回路就是快策略所缺的"系统 2"。

**四条贡献（论文级）**

1. **通道分辨的增益测量**：γ 与 g 的各向异性；FK 直接测，不需要成功标签，预注册。
2. **位精确孪生归因**：同图异物理/同物理异图，字节级校验，把失败钉在接触几何上。
3. **(δ,θ) 包络 + 阶段模型**：交互项与失败阶段转移，给出"补偿应补哪一段"的预测。
4. **增益匹配的指令侧补偿**：单参数、无记忆、无重训；15° 拉回且 0° 不降（待 E5′）。

**图规划**：Fig.1 现象（γ vs g）→ Fig.2 孪生归因（20/20 vs 0/20）→ Fig.3 包络与阶段
→ Fig.4 补偿前后（15°、0°）→ Fig.5 协议/工件。

## 5. 《思考，快与慢》与工业补偿：怎么挂才不被打

- **System 1** = 冻结策略的快反应：把训练分布里的姿态先验直接当后验，看到但不更新。
- **System 2** = 本文的**外部标定回路**：测量增益 → 归因 → 建模 → 注入偏置。
  它不进入网络、不改权重，因此与 Fast-in-Slow 的"双系统架构"、RTCF 的"记忆纠偏"、
  ARC 的"人类纠正"都不同（§2）。
- **认知偏差**：只把 anchoring/WYSIATI 当作**解释性透镜**，不声称复现人类机制、
  不建"认知偏差基准"——该路线已被 CorrectVLA（[2608.29967](https://arxiv.org/abs/2608.29967)）、
  SO-101 failure/recovery benchmark（[2606.08881](https://arxiv.org/abs/2606.08881)）与
  本项目 2026-11-16 的 no-go 裁决占满（见
  [cognitive-bias-probe-candidate](../prior-art/cognitive-bias-probe-candidate-20261116.md)）。
- **工业补偿类比**：只借**范式**（误差源分类、辨识、预补偿），不借"精度保证"；
  明确写"仿真、单策略、单物体，不外推工业级"。

## 6. 可行性与成本（估计，未执行）

| 实验 | 规模 | 墙钟（估计） | 依赖 | 决策 |
|---|---|---|---|---|
| **E3** δ-only 网格 | θ∈{0,5,10,15}° × δ∈{2,8,14} mm × 20 seed ≈ 240 集 | ~20 min | 复用 E4 条件机制，去 yaw 维 | **已完成（2026-11-17）**，结论见 §4 T3：不主张 d<0 的"二维交互"，改"边界形状 + 两通道失败" |
| **E5′** 补偿 | θ=15°、δ~1 mm、20–40 集 | ~1 h 工程 + ~15 min 跑 | 改 `rollout_e2.py` 指令侧 | 过 50% 才保 C4 |
| **E7** 外部效度 | 第二物体（或第二 seed 重训后）4 条件 × 20 集 | ~15 min（换物体）/ ~1 天（重训+复验） | 资产 | 二选一，必做其一 |
| **E6** 随机偏航示范重训 | 20 示范 + 30k 步 × 3 seed | **≈4.5 GPU-h + ~1 h 人工 + ~1 天复验** | A100；ACT 20k 步曾以 3600 s 为上限 | **只估价，不执行**；列为 future work |

E6 的"贵"不在 GPU（按 3600 s/20k 步外推，30k 步≈1.5 h/seed），而在**换 checkpoint 会
失去冻结锚点**：E1′–E5′ 整套要在新策略上复跑，才是真实成本。故 E6 不应在论文 1 之前做。

## 7. 查新问答（预演，直接用于回复审稿人）

**Q1 与 2611.17658 的区别？**
它：噪声、位置通道、α=V/(V+s²)、闭环 ρ>α、预测成功率。本文：确定性取向、γ≈0.004、
闭环不回升、失败由接触几何承担、补偿由 γ 与 FK 解析导出。引用时只写"该文给出同一
'先验—读数折中'机制在噪声维度的独立证据"，**不得**写"与 α 一致"（g 与 α 方向相反）。

**Q2 与 2509.18644 / GAP 的区别？**
它们证明"本体捷径/梯度压制"存在并给出学习侧缓解；本文不训练、不改输入，测量**取向
通道的增益**并用孪生把失败归因到接触几何，再在推理侧补偿。

**Q3 与 LIBERO-Plus 的区别？**
它是模型排名基准：离散 L1–L5、聚合成功率、7 类扰动。本文是**单策略的机制研究**：
连续 (δ,θ) 边界、阶段分解、位精确孪生、补偿干预。另：需核对 LIBERO-Plus 是否含物体
位姿子维；若含，明确写"它测到成功率下降，本文解释下降发生在哪一段、由什么几何造成"。

**Q4 与 RTCF/ARC/TATE 的区别？**
RTCF 需成功轨迹记忆、纠运动残差；ARC 需人类纠正；TATE 校数据标签。本文只需一次增益
标定，补的是解析关节偏置，且补偿量由 γ 与 dφ/dq5 直接算出，可预测、可检验。

**Q5 与等变策略的区别？**
它们改架构使 π(g·x)=g·π(x)；本文测冻结非等变策略的 γ，并回答"不重训、只补一个
关节偏置能恢复多少容差"。二者是**互补**：等变是预防，本文是诊断+补救。

**Q6 "BC 不具旋转等变性是常识，这有什么新？"**
常识是定性断言；本文给**定量增益（γ≈0.004 vs g≈1）、包络形状（15° 硬悬崖、内区
θ\*≈12°、δ≈14 mm 可达接管）、阶段定位（抬升 vs 放置）、补偿增益（dφ/dq5=1.0000）**，
并证明失败可被"接近段碰撞"这一几何
机制解释（E4 孪生）。常识不能预测"补多少、补哪一段、补了之后失败移到哪"。

**Q7 为什么不是"认知偏差基准"？**
该生态位已被 CorrectVLA 的失败分类学与 SO-101 benchmark 占据；本项目 2026-11-16 已
裁决 no-go。本文只借 anchoring 作透镜，主张是**校准**，不是基准。

## 8. 风险与 kill criteria

| 风险 | 触发条件 | 处置 |
|---|---|---|
| C4 不成立 | E5′ 15° <50% | 删 C4；论文收缩为 C1′–C3′ 诊断（投 ICRA/CoRL workshop） |
| 包络退化 | E3 全窗口 d≥0（已触发）；ΔAIC 未做 | 删"二维交互/平滑收缩"，改写"二维边界 + 两通道失败"；T3 降级。事后：剔除 δ=14 后 d<0 只作机制解释，不作主张 |
| 单策略/单物体 | 无 E7 | 必须补第二物体或第二 seed；否则只投短文 |
| "更像鲁棒性评测" | 审稿人对比 LIBERO-Plus | 用孪生归因 + 阶段 + 补偿三点区分（§7 Q3） |
| 补偿被视为 trivial | 只报"加偏置有效" | 加 naive 固定偏置对照 + 补偿量预测 + 0° 不降 + 阶段转移（P5） |
| 认知叙事被视为装饰 | 审稿人问"System 2 在哪" | 明确 System 2 = 外部标定回路，并给出四步流程图与可复现工件 |

## 9. 下一步（按依赖排序）

1. **E3 runner**：复用 `rollout_e4.py` 的条件机制，去 yaw 维，补 12 格；先跑 2 seed smoke。
2. **E5′**：改指令侧 q5 偏置；加 naive 固定偏置对照；预注册 15°/0° 双条件。
3. **E7**：第二物体优先（成本低）；第二 seed 重训作为备选。
4. **论文骨架**：按 §4 图规划写 4 页提纲；Related Work 按 §2 矩阵写"差异句"。
5. **正式查新**：把 §10 的式交给机构复跑 Scholar/CNKI/WoS；回来只改 §3 判定列。

## 10. 给查新机构的检索式（EN/CN）

**EN（Scholar/Scopus/WoS）**

1. `"orientation" AND ("imitation policy" OR "behavior cloning") AND ("gain" OR "sensitivity")`
2. `"object rotation" AND ("manipulation policy" OR "visuomotor policy") AND ("success rate" OR "tolerance")`
3. `"counterfactual" AND ("simulator" OR "rendering") AND "robot policy" AND ("appearance" OR "collision")`
4. `"test-time" AND ("correction" OR "compensation") AND "frozen policy" AND "manipulation"`
5. `"pose prior" AND ("demonstration" OR "imitation") AND ("grasp" OR "manipulation")`
6. `"anchoring" AND ("imitation learning" OR "behavior cloning" OR "vision-language-action")`
7. `"error compensation" AND ("robot manipulator" OR "calibration") AND ("review" OR "taxonomy")`
8. `"dual-process" OR "System 1" AND "robot manipulation policy"`
9. `"tolerance envelope" OR "operating envelope" AND "manipulation"`

**中文（CNKI/万方）**

1. `姿态 泛化 模仿学习 抓取 容差`
2. `朝向 偏差 机器人 策略 补偿`
3. `操作 容差 包络 评测`
4. `认知偏差 机器人 操作 策略`
5. `工业机器人 精度补偿 标定 综述`

**判定口径**：若 1/2 命中"直接测量取向增益并与位置增益对照"的工作，T2 降为 adjacent-occupied；
若 3 命中"字节级同图异物理"的机器人策略归因，T1 降级；若 4 命中"单参数解析补偿 + 冻结策略"，
T4 降级。三者任一降级，论文主张按 §3 降级写法改写，不撤方向。
