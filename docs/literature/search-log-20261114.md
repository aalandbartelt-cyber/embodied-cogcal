# 文献检索执行记录（2026-11-14）

范围：VLA 语言落地与冲突、执行条件/时序、残差校准、因子交互、SO-101 同体仿真—真机、实验统计。
这是一轮有范围的研究准备检索，不是穷尽检索或机构科技查新报告。未收集 Scholar 引用量。

## Google Scholar 优先路径

直接请求以下两页，工具均返回不可访问，未获得结果列表：

- [VLA anchoring/bias/calibration](https://scholar.google.com/scholar?q=vision+language+action+anchoring+bias+robot+calibration)
- [SO101Bench / ICBench](https://scholar.google.com/scholar?q=SO101Bench+ICBench+robot)

又尝试 `site:scholar.google.com "vision language action" bias grounding calibration`，没有得到可供核验的
Scholar 列表。采用普通检索定位原始来源，并到 arXiv、正式会议录/出版社、官方项目与代码核验。
没有绕过验证码，也不把替代搜索标成 Scholar 检索成功。文献库逐项保留题名 Scholar 复查入口。

## 已执行检索

| 批次 | 检索式/动作 | 新证据与处理 |
|---|---|---|
| 1 | 精确题名：Restoring Linguistic Grounding…；Beyond Appearance Shifts；SO-101 Bench | 定位原始 arXiv/项目/代码；发现 IGAR Springer 正式出版记录，待直接核对 |
| 2 | `"vision language action" "language" "execution" "interaction" calibration robot`；`"VLA" "bias" "anchoring" robot` | 广义结果杂，不能用无结果证明创新 |
| 3 | `"LIBERO-Plus" "LIBERO-PRO" benchmark`；`"SmolVLA" "ACT" SO-101 simulation policy` | 发现 LIBERO-Pro2.0、SO-101 示教量比较研究，以及部分只有模型骨架的工程仓库；后者不当论文或可用策略证据 |
| 4 | 官方域检索 OpenVLA / LIBERO / SmolVLA / LIBERO-Plus | OpenVLA 正式 PMLR 年为 2025，勿与 2024 预印本混写；CVF 已有 Plus 2026 正式记录 |
| 5 | 打开 LIBERO-CF v3、BAS-VLA v2 正文和 PRO2.0 官方仓库 | 已有可行反事实动作引导、门控残差和运行时执行/语言干预；提高创新重叠风险 |
| 6 | 打开 CVF Plus PDF | 403；不伪称本次读到该文件，后续用 arXiv 原文交叉核查 |
| 7 | PRO2.0 仓库 Paper 链接；`SwitchVLA`；`Residual Reinforcement Learning for Robot Control`；`Real-Time Execution of Action Chunking` | PRO2.0 PDF 超工具大小限制，改开 abs/html；识别任务切换、残差控制和延迟调度近邻 |

## 纳入与排除

- 纳入：题名/作者/年份有原始记录；对本项目的问题、基线、平台或证据设计有明确作用。
- 主要近邻额外阅读方法、实验与局限段落，记录定位及未验证范围。
- 排除为证据：聚合站 AI 摘要、无法定位原始记录的标题、未执行的代码骨架、未核实榜单数字。
- 同一工作的预印本/正式版合并为一项，记录版本差异；不把发表年和首次提交年当两篇论文。
- 无法确认会议信息时按已核验预印本收录，不照抄项目页的录用声明。

## 后续核查进展

- 直接读取 arXiv 原始 citation meta，27 篇均获得完整题名/作者/提交日期，未出现失败；版本固定值和响应 SHA256 保存在 `references/metadata-arxiv.json`。
- Plus arXiv v3 §5 与附录 F 实际研究 pairwise compositionality；其组合分析排除了语言因子。正式 CVPR PDF 本次 403，题名/页码由 CVF HTML 核对，方法解释明确指向 arXiv 版本。
- PRO2.0 §4.4 与附录 A.4 实际研究两两/三阶组合，附录 C 明确 stale chunk、latency 和语言干预；PDF 超大后 HTML 可读。
- SmolVLA §3.3 已实现异步推理；RTC 研究动作分块时序。普通延迟补偿必须作为竞争解释和匹配基线。
- SO-101 示教规模比较论文的 §1.1/§7 自述单任务、单操作者、固定训练步数与照明变化；不将其政策排名推广成通用选型结论。
- Springer DOI resolver 路径失败，直接 `/chapter/10.1007/978-3-032-37152-2_3` 成功；按出版记录确认 IGAR 的正式版本。
- 补核 Sentinel（运行时失效监测）、π0.7（近期基础模型）和数据/基准/数据引擎综述；综述只作阅读地图，核心方法事实回到原始工作。
- Crossref 原始 API 八条元数据获取成功；与 arXiv 重复的 IGAR、LIBERO 合并，其余六篇补作统计/经典控制/认知概念来源。
- Holm 原始 JSTOR 页只返回脚本，原始 PDF（USP 托管）两种访问均 403，候选 JSTOR DOI 在 Crossref 404。
  不猜填 DOI，不将该项纳入本轮一手元数据核验通过的可导入库；保留在待复核表，现有协议中的 Holm 校正仍需原文复核。

## 用户要求查新不通过换方案后的定向检索

- 实际检索：`robot manipulation active diagnosis`、`VLA failure diagnosis intervention`、
  `vision-language-action causal diagnosis`、`sim-to-real treatment effect calibration`、
  `sim-to-real policy ranking evaluation`、`active fault diagnosis input design robot`。
- 新增原始来源：IDR（2607.25516）、VLA-Gauge（2610.16567）、MetaFine（2605.19986）、
  Which Hand Was Late?（2610.37533）、DEFLECT（2605.19294v3）、Leap-VLA（2611.01011）、
  Embodied Interpretability（2605.00321）、SIMPLER（2405.05941 / 正式 PMLR 2025）、
  RoboMD（2412.02818v4）、FIERL（2405.04938）、Prediction-Powered Inference（2301.09633v4）。
- IDR §IV 的反事实与门控残差、MetaFine §8 的 PPI、Which Hand §4.3/§7 的被动不可辨识与升级修复已读相关正文。
  其余新增项按摘要/元数据/结构登记，没有假称精读或复现。
- Google/聚合搜索也返回 VLA-Trace、其他主动故障辨识与仿真评价研究线索；尚未同等核验的项没有加入主库，
  无结果的窄关键词查询不作为“该方向没人做”的依据。
- 追加后三份 arXiv 元数据快照共有 41 篇；加 6 篇独立 Crossref 经典/方法论文，主库为 47 篇文献 + 3 项工程来源。
- 本轮没有完成全领域 citation snowballing，没有正式查新报告；候选 B/C 都保持未通过状态。

## 用户要求进一步深入后的第二轮

- 三个独立域分别审计ECCBF、增益迁移估计、主动辨因；后追加接触自适配，四份报告给出原文节/式与读取边界。
- 根代理复核IMPACT-VLA闭环干预、Fly-by-Code物理Probe、Ao v2改题和Self-comp §3/B.6；
  继续检索 `robot vision language action continual test time adaptation contact pseudo label drift negative transfer task switching`、
  `robot manipulation online adaptation contact catastrophic forgetting`、`robot execution residual pseudo adaptation contact`、
  `pseudo-control hedging contact robot adaptation`、`VLA adaptation training signal hedging`。
- 新增SALT、FAN、Continual VLA、ViTaR、Instruction–Action Binding等原始工作；前四者不支持把漂移/接触门控直接当新机制。
  控制理论引用链追到经典决策论排障、主动故障诊断、training-signal hedging、anti-windup和deadzone。
- 各审计继续实际尝试Scholar，仍未取得结果页；不能声称完成Scholar前向/后向引文网络或穷尽查新。
- 本轮补充31条arXiv固定版本记录、30篇新增论文（Ao v1/v2同篇分开），原始citation元数据全部成功获取。
  元数据核验与正文阅读不同，逐篇阅读范围见深审报告。
- 元数据异常：Ao v1 abs题名漏Audits，但原始全文题名完整；保存覆盖来源与hash。
  Continual VLA的PMLR正式出版页核实ICML2026、作者/页码；作者逗号格式归一比对后匹配。
- UniSuperMimic原始论文与独立下游repo单列补充；固定代码静态确认MuJoCo backend，未安装/训练。
- 当前科研裁决：停止旧ECCBF核心及两个宽泛备选；接触替代也没有通过的新方法。
  限时观测草案只检验是否值得继续研究，不以“没有找到完全同样标题”宣称创新。
