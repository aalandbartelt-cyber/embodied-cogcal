# 近邻阅读卡与阅读顺序

完整作者、年份、固定版本和 Scholar 入口见 [目录](CATALOG.md)。以下按对选题决策的影响排序，
不是被引量排名。正文定位只表示相关段落已读；代码均未在本项目独立复现实验。

**检索追加后的优先级调整：先读下方新增的 IDR，再读 PRO2.0、BAS-VLA、Plus、CAG。**
以下编号保留本轮阅读过程，新路线选择另见 [路线决策](../prior-art/ROUTE_DECISION.md)。

## 第一轮：先判断题目是否站得住

### 1. LIBERO-Pro2.0 — `zhou2026liberopro2`

- 原文：[v1 §3、§4.4、Appendix A.4/C](https://arxiv.org/html/2610.24587v1)；[官方资源](https://github.com/LIBERO-Pro-Team/LIBERO-Pro2.0)。
- 问题/方法：静态与运行时干预，包括执行时序、过期动作、语言更新；比较组合扰动与恢复。
- 最近重叠：已经包含执行状态、语言干预和两两/三阶组合，不能说它只做单因素鲁棒性。
- 必须区分：weakest-single gap 不是标准加性四格交互，也不是“认知机制”证明。
- 要带走的实验：统一事件时刻、反馈年龄、重规划窗口和实际干预日志；校准收益必须超出 hold/retry/时序修复。
- 边界：论文 v1 是 1,648 shifted instances，仓库 README 是 1,646；不跨版本混用规模数字。资源页可读不等于已跑通。

### 2. LIBERO-Plus — `fei2026liberoplus`

- 原文：[arXiv v3 §5、Appendix F](https://arxiv.org/html/2510.13626v3)；正式出版题名见 [CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR_2026_paper.html)。
- 问题/方法：多维扰动与组合泛化，已经报告 pairwise compositionality。
- 最近重叠：多扰动交互现象已经出现；不能把更换符号后的四格差当新算法。
- 必须区分：该 arXiv 版组合实验排除了语言因子；这限定重叠范围，不证明其他工作没有语言×执行分析。
- 要带走的实验：报告四格原始成功/总数、独立失败零模型与固定尺度；避免只展示一个 gap 热图。
- 边界：正式版 PDF 本次 403；方法卡依据 arXiv，出版元数据依据 CVF HTML。

### 3. BAS-VLA — `liu2026basvla`

- 原文：[v2 §3–5、§4.1–4.4](https://arxiv.org/html/2609.23650v2)；[官方代码](https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts)。
- 问题/方法：任务保持/任务改变的匹配条件；冻结策略上残差校准与选择性证据门控。
- 最近重叠：残差、匹配、门控、正常性能保持和真机都已覆盖；它是方法创新最重要的近邻之一。
- 要带走的实验：相同可用输入、示教/校准数据、参数量和调参预算的 generic residual；正常条件非劣效。
- 可比性：已有发布 adapter 的载体和动作规范不能直接替换为 SmolVLA/SO-101；改写版应明确标成 adaptation，不能冒充作者官方复现。
- 边界：代码状态沿用上轮固定提交静态核查；NeurIPS 声明本轮未另核正式会议录，库中仍按已核 arXiv 版本引用。

### 4. LIBERO-CF / CAG — `fang2026cag`

- 原文：[v3 §4–7、Table 6](https://arxiv.org/html/2602.17659v3)；[官方代码](https://github.com/yuffish/VLA-CF)。
- 问题/方法：同场景可行替代目标；有语言/无语言动作分支差的引导。
- 最近重叠：冻结策略语言纠偏与真实任务成功率恢复已有直接基线。
- 要带走的实验：新目标完成率和旧目标完成率分开；TF-CAG/VA-CAG 的额外推理与训练预算分开。
- 可比性：同载体、同动作字典且能实现无语言条件时才做数值比较；额外分支成本应计入 wall-clock。
- 边界：本轮读原文，未运行其代码或把作者数字移入我们的主表。

### 5. SwitchVLA — `li2025switchvla`

- 原文：[v1 §3–4、Appendix B.3–B.4](https://arxiv.org/html/2506.03574v1)。
- 问题/方法：历史/当前指令、接触状态、forward/rollback/advance 行为模式共同支持任务切换。
- 最近重叠：语义与执行状态耦合并非无人研究，不能用“execution-aware”词组直接宣称新颖。
- 要带走的实验：若做在线切换，按预接触/接触/释放后阶段分别登记事件；静态旧计划文字不充当在线切换。
- 可比性：其训练和额外监督不同于冻结后校准；不要只比较论文结果后宣称我们更省数据。

## 第二轮：把接口、负对照和真机验证定实

### 6. RTC 与 SmolVLA — `black2025rtc`, `shukor2025smolvla`

- 原文：[RTC §2–4](https://arxiv.org/html/2506.07339v2)、[SmolVLA §3.2–3.3](https://arxiv.org/html/2506.01844v1)。
- 最近重叠：异步推理与 chunk 执行已能改善反馈和延迟问题；SmolVLA 还指出相机命名/次序的重要性。
- 要带走的实验：观察时间、推理结束、命令入队/生效、chunk 索引与控制频率；Raw 与校准方法共用暂停规则。
- 可比性：RTC 面向 diffusion/flow 载体，不能未经验证套用到任意离散解码 OpenVLA；简化调度基线仍可用于所有兼容接口。

### 7. SO-101 Bench — `hickok2026so101bench`

- 原文：[v1 §3.3–3.7、§4–5、Limitations](https://arxiv.org/html/2610.36420v1)；[项目](https://so101-bench.github.io/)。
- 最近重叠：同体数字孪生与同权重真机比较已有工作；当前平台是 Isaac Lab，不能当本仓库 MuJoCo 的验证。
- 要带走的实验：共享任务谓词、相机/关节约定和版本；报告仿真/真机方法差值与失败类型，而非仅视频或排名。
- 边界：小范围真机与绝对成功率偏乐观限制外推；其等算力微调方案并非我们单卡最小 Pilot 的既定预算。

### 8. SO-101 示教规模比较 — `cowling2026demonstrations`

- 原文：[v1 §1.1、§3、§7](https://arxiv.org/html/2610.37170v1)。
- 价值：在低成本真机上比较 ACT、Diffusion、SmolVLA、π0.5 的数据量配方，可指导小预算试验。
- 要带走的实验：记录空闲开头、训练曝光量、测试照明、操作员和重置顺序；先审数据再加模型。
- 边界：单任务、单臂、单操作者、固定步数使模型与数据量排名不能普遍外推。

### 9. ICBench / IGAR — `zhang2026igar`

- 原文：[arXiv v2 §3–5](https://arxiv.org/html/2603.06001v2)；[正式版](https://link.springer.com/chapter/10.1007/978-3-032-37152-2_3)。
- 价值：受控矛盾指令与推理注意力校准；已有 Franka 真机。
- 要带走的实验：将无解指令的正确不执行单列；不能把旧任务 SR 降低解释成我们可行任务 SR 提升。
- 边界：若主模型内部注意力不开放，需记录不可复现原因，不能用随意调 prompt 的方法叫 IGAR。

### 10. CorrectVLA — `kwon2026correctvla`

- 原文：[v2 §3–5、§7–8](https://arxiv.org/html/2608.29967v2)。
- 价值：诊断可修复模式，再把事后人工句子转换成动作方向/幅度/时间窗；不是所有目标或规划失败都可用幅度修好。
- 要带走的实验：加入固定偏置、重试、时间预算匹配；将观察测试失败后的人为调整单列信息预算。
- 边界：原文自己列出缺少某些简单基线、单标注员和经验幅度等限制；项目代码状态未构成已可复现的 SO-101 baseline。

### 11. RAGu — `kim2026ragu`

- 原文：[v1 §IV–V](https://arxiv.org/html/2611.10894v1)。
- 价值：几何变换、策略兼容检索与推理引导都已用于跨域适配。
- 要带走的实验：如果我们声称不依赖检索，必须明确校准器实际使用的数据；额外轨迹访问不是免费信息。
- 边界：flow-matching 引导接口与本项目六关节后校准接口不同，本轮未核实并运行完整官方代码。

### 12. Sentinel 与交互统计 — `agia2024sentinel`, `knol2012interaction`

- 原文：[Sentinel §3–4](https://arxiv.org/html/2410.04640v2)、[交互报告原则](https://pmc.ncbi.nlm.nih.gov/articles/PMC3324457/)。
- 价值：gate 应来自运行时可观测历史；交互应说明加性/乘性尺度和每格结果。
- 要带走的实验：gate 的触发率/误报率/检测时延与控制成功率分开；配对统计以 episode/reset 块为单位。
- 边界：检测论文不是任务修复保证；统计原则不是机器人机制证据。

## 基础补读与引用作用

### 新增主要近邻：IDR、MetaFine 与失败可辨识性

- **IDR — `zhang2026idr`**：[§IV-A/IV-B](https://arxiv.org/html/2607.25516v1)。
  将视觉/本体感知分别置零，比较冻结 VLA 的动作偏移，估计动态模态作用并门控残差融合。
  该近邻使“反事实探针—作用估计—动作修正”流程难以作为创新；物理执行干预与输入模态干预有区别，
  但需要证据证明这种区别产生新能力。下一步逐式比较信息、时序与控制预算，而非仅关键词。
- **MetaFine — `xu2026metafine`**：[§8.1–8.4](https://arxiv.org/html/2605.19986v1)。
  用少量真实配对结果校正大量仿真预测，应用 PPI 估计与区间；备选 B 不能仅把这个估计器改成方法差值。
  先比较估计目标、抽样/选择规则与仿真失配假设，再判断是否有新问题。
- **Which Hand Was Late? — `whichhand2026`**：[§4.3/§5/§7](https://arxiv.org/html/2610.37533v1)。
  被动观测无法区分部分复合失败，升级式修复可绕开精确诊断。备选 C 必须比较固定重试、
  固定探针、被动监测及“修法全上”的等成本方案。该工作是脚本双臂仿真；不能据此声称单臂真机已解决。
- **RoboMD / FIERL**：[RoboMD 固定版](https://arxiv.org/abs/2412.02818v4)、[FIERL](https://arxiv.org/abs/2405.04938v1)。
  本轮只核原始元数据/摘要。主动搜索失败空间与主动输入辨识已有工作；不能把 active diagnosis 名称当新点。
- **VLA-Gauge / DEFLECT / Leap-VLA**：固定版见目录；本轮只核摘要/结构。
  分别覆盖组合扰动驱动改进、延迟反事实偏好学习与陈旧语义缓存条件化，保留作下一轮定向精读对象。

| 主题 | 文献键 | 读完要回答的问题 |
|---|---|---|
| VLA/动作头 | `kim2025openvla`, `kim2025oft`, `black2024pi0` | 当前到底用哪个 checkpoint，输出何种单位和坐标？ |
| 传统控制/残差 | `hutchinson1996servo`, `johannink2018residual` | 收益是否只来自视觉伺服/追踪修复或普通残差？ |
| 模仿学习 | `zhao2023act`, `chi2023diffusion` | 无语言策略能否验证任务可解？chunk 会怎样改变反馈？ |
| sim-to-real | `peng2017dynamics`, `tobin2017domain` | 哪些几何/动力学量要测，哪些参数允许真机重估？ |
| 统计 | `wilson1927`, `mcnemar1947`, `efron1979`, `agarwal2021precipice` | 独立单位、配对不一致率、CI 和训练随机性如何区分？ |
| 概念/综述 | `tversky1974`, `wang2026survey` | 哪些只是术语/阅读导航，哪些必须回到原文提供证据？ |

## 每篇精读后的固定记录

记录：版本/正文定位 → 研究对象 → 干预与可用信息 → 方法公式或算法位置 → 数据/本体 →
评价谓词/分母 → 最强简单基线 → 作者自述局限 → 与本项目最近重叠 → 一项必须补的对照。
后续人工 Scholar 工作优先对前五项执行 Cited by / Related articles，记录检索日期和真正打开的文献；
不要只复制二手站点给出的引用或模型生成摘要。
