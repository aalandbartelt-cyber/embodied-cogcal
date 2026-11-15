# 准备阶段事实与边界

## 2026-11-15 真实记录与下一科学问题

[真实SO101失败检查](experiments/discovery/deployment-failures-20261115/README.md)
已固定同一π0.5套环任务12条，核5421行、72张顶视图。环位于不同最终位置是可见事实，
不是机械误差、抓持偏移或GRASP损害的因果证据；初态未配对，数据作者标签未独立复核。
旧20k的两个processor均与固定数据stats一致，外部issue的synthetic幅度演示不能解释本项目0/20。
下一项只优先核GRASP配对FK损失与CFM条件均值；penalty理论/RFM/预条件化已限制宽泛创新，
不能把普通Jacobian加权、物理loss或停梯度命名成新方法。当前尚未证明任务损害或新颖性。

## 2026-11-15 当前裁决更新

指令必要性候选从优先深审降为诊断工具，详见
[独立贡献门槛与源码复核](experiments/discovery/instruction-necessity-followup-20261115/README.md)。
新增2018 DONE规范、2026 shortcut审计及双judge近邻；不把无语言encoder但读task index混成目标盲。
RoboOrchard固定源码step返回两个done字段None，默认1000步/指定配置30Hz；这是静态事实，非原论文预算/完整攻击。
具体反例是否已发表尚未证明，也未验证对成熟VLA结论的影响；不宣布查新不通过或方向完成。
核心方法增量不足，停止将更多相同扫描、普通commit或Isaac移植当下一主任务。

## 新目标启动的实际检索（2026-11-14）

- 再次直接访问Scholar：VLA calibration/compensation 与 selective reasoning/uncertainty 两个查询均被工具返回不可访问；未看到Scholar结果列表。
- 当前全目标是确定方向；前轮文献准备已完成并不证明新方向成立。不得沿用旧目标complete状态替代新目标。
- 工作树基线87871e3，干净；旧ECCBF、迁移差值、主动诊断、接触补偿的宽题否决继续作为候选筛选约束。

- 用户已选择 A100 做模型运行，本地 `cogcal-sim` 仅验证物理资产和日志，不安装 OpenVLA 7B。
- 已有 SO-101 本体资产固定在 a758567c3978dfeefe282ede0500085a48fe8f78。
- 上一阶段审计起点的 `scene.py` 只有 load/reset；现已补齐基础观测/动作/放置接口并验收，完整任务历史判定仍待实现。
- OpenVLA LIBERO 输出为该 benchmark 的动作定义；不能直接替换 SO-101 六关节 position actuator。
- 当前 ECCBF 为待证假设和算法原型，尚无真实策略效应、泛化或成功率证据。
- 查新矩阵需核对一手原文；组合维度不同不能自动证明方法新颖。
- 已核六个主要近邻的原始来源；BAS-VLA 等已覆盖残差、门控和真机。ECCBF novelty 未通过。
- raw action 差可能包含合法任务目标变化。现有原型应基于目标相对残差才可能用于校准。
- 本地 EGL：16 项物理/渲染/短视频测试实际通过；分析环境 MuJoCo skip 另报。
- 本地 OSMesa 测试报缺少 libOSMesa 导致 OpenGL.glGetError 为 None；CI job 明确 apt 安装依赖后再验证。

## 文献准备阶段（2026-11-14）

- 直接访问两条 Google Scholar 检索页均被工具拒绝访问；没有看到 Scholar 结果列表，不能声称完成 Scholar 系统综述。
- 已尝试 Scholar 域检索及近邻题名检索，转向 arXiv、出版社、官方项目/代码核验，保留 Scholar 入口供人工复查。
- 新发现 ICBench/IGAR 的 Springer 正式出版记录，DOI `10.1007/978-3-032-37152-2_3`；后续直接核对出版页，修订只记录预印本的旧状态。
- LIBERO-Pro2.0（arXiv:2610.24587v1）§4.4 和附录 A.4 已直接研究静态/动态扰动的两两及三阶组合；只提出交互分析不足以构成方法创新。
- PRO2.0 附录 C 包含时序、latency spike、stale action chunk 和动态语言等干预；应作为执行语义主张的主要近邻。
- PRO2.0 arXiv v1 记 1,648 个 shifted instances，官网 README 记 1,646；汇报不混用规模数字，按版本分别记录。
- OpenVLA 正式 PMLR 2025 作者列表与 arXiv 不完全一致；文献库将按所引用的版本保留完整作者，不拼接版本元数据。
- 用户明确：查新不通过要换方案。当前将 ECCBF 保留为候选工作名，不把工程投入作为继续该核心主张的理由；备选问题也须检索，不能为换而换。
- 对当前生成器实际生成 100 场景/400 四格记录：只有 8 组物理 placements、16 组 placement-target 组合；两个 task_id 归一颜色后仅一个任务指令模板。证据已存 experiments/so101/protocol-audit.json。
- IDR §IV 已覆盖反事实视觉/本体感知、动态作用估计、门控残差；不再把该流程当新点。
- MetaFine §8 已把 PPI 用于少量真机/大量仿真评价；备选 B 不能仅把现成估计器改为方法差值。
- Which Hand Was Late? 已展示被动不可辨识与升级式修复；主动诊断备选须比较固定重试/全修复和传统输入设计。
- 当前建议：暂停扩大旧 ECCBF 正式矩阵；优先详查 C 主动辨识，再查 B 校准增益迁移可信性；均未通过创新门槛。

## 第二轮深审（初审过程，后续裁决见下）

- 用户要求进一步深入，初轮 C/B 的排序不能作为选题已确定依据。应用 dispatching-parallel-agents，三个独立域审计：ECCBF 红队、主动诊断、修复增益迁移评估。
- 根代理已直接打开 IMPACT-VLA（2609.15005v1），其原文包含闭环反事实重执行、跨阶段非加性与恢复分析；等待逐式比对，不能说所有准确实验都已被其覆盖。
- 根代理已直接打开 Fly-by-Code（2610.12549v1）：主动视觉/物理诊断确为原文机制，非仅二手摘要；故宽泛 C 仍有直接机器人近邻。
- 2601.21471 最新 v2 改题为 Designing Service Systems from Textual Evidence，摘要已覆盖有偏低价proxy+选择性昂贵审计的best-arm identification；不能混用v1题名与v2结论。
- UniSuperMimic 固定 d78a5e2 的源码确认 native MuJoCo backend；当前任务为 G1 motion tracking，依赖 MuJoCo 3.11.0，与本项目4.0.1隔离。仅静态核查，未安装运行。

## 第二轮裁决

- 独立公式级审计形成四份报告：ECCBF、迁移差值、主动诊断、接触适配；旧核心与三个宽泛替代都无可冻结新机制。
- 当前 ECCBF 在二元角点等于四格均值相对基线，在连续分数等于门控双线性条件残差；脚本实际验证1,000分数组误差<1e-12。
- 400/400生成提示仅凭显式Current task字段精确还原匹配中性指令，无隐藏目标；没有VLA成功率结论。
- IMPACT-VLA已有反事实闭环交互归因；其归因与动作修复仍须区分，不以宽泛相似误判完全重复。
- SIMPLER已关注相对性能/改进信号；PPI差值、AIPW和Ao v2差值残差协方差/选择直接覆盖备选B。
- Fly-by-Code已有物理Probe；Breese-Heckerman1996已有期望修复总成本实验选择，备选C宽题停止。
- 接触自适配也遇到经典training-signal hedging/anti-windup/deadzone；Self-comp已做抽屉任务，不能声称接触未覆盖。
- 当前建议只做残差监督有效边界的限时观测研究，先验收策略/时序再比较freeze/reset；无现象或简单基线吸收则淘汰。
- 新增补充31版本记录=30论文，Ao v1/v2同篇分开；abs v1漏Audits，全文标题核验并保存覆盖来源。PMLR作者自然顺序与arXiv逗号格式归一后逐人核对，不混淆作者变化。

## 用户确认的当前选题边界（2026-11-14）

- 保留低成本 SO-101、A100、同体仿真—真机；核心研究问题可以更换。
- 后续不以保留认知偏差/语言冲突/ECCBF为筛选前提；先找精确科学缺口，再判断同平台可实现性。
- 用户确认的是约束，不是选择接触适配或其他候选；此前四份否决审计继续有效。

## 新一轮候选发现：风险来源而非单一置信度（2026-11-14）

- 直接Scholar查询仍不可访问；GitHub/arXiv/项目原始页面可访问，未把搜索摘要当作正式查新结论。
- TeAR（arXiv:2609.36182v1）已做遥测条件动作整流和SO-ARM101五自由度物理评估；“热/电流/电压补偿”宽题淘汰。
- REMM（arXiv:2610.12710v1）已做证据链接、依赖撤回和恢复队列；“可修改具身记忆/错误结论撤回”宽题淘汰。
- CoVer（arXiv:2602.12281v1）已做语言重述×动作采样验证，Pre-VLA（2605.22446v1）已做候选动作的critic/安全预验证与重采样，DiVeR（2610.04933v1）已用动作表征离散度分配verifier学习权重，GeoAAC（2609.20776v1）已做按可靠性自适应action horizon；“慢推理/多采样/动作置信门控”宽题淘汰。
- VFD/UQ-VLA（2606.18043v1；官方代码 https://github.com/learnsyslab/uq_vla，Apache-2.0）已做流模型ensemble epistemic uncertainty、失败检测和主动示教；其明确局限是只用初始观测不确定性作任务难度proxy、未处理任务间信息依赖，真实机器人代码不公开。
- SO-101 failure/recovery benchmark（2606.08881v2）将失败分为semantic/execution两层，并报告恢复率很低；局限写明只覆盖单一SO-101和桌面任务，未来需要区分硬件特有因素与政策结构因素。官方SO-101 Bench（https://github.com/5hadytru/so101_bench，Apache-2.0）则证明仿真可能高估成功率但保持策略排名，不能替代风险校准。
- 一个仍值得公式级查新的窄候选是：同一失败表象下，策略生成不确定性和执行映射不确定性是否可被识别；在固定算力/动作预算下，按来源选择重采样、缩短chunk、执行整流或暂停，是否比单一verifier/单一rectifier更有效。它不是“把VFD+TeAR拼起来”的贡献；必须证明来源可辨识条件、干预映射和固定预算下的可证伪增量，否则淘汰。

## 风险来源候选的继续检索与降级

- PATCH（2606.16690v1）已做 action-chunk 条件 latent-patch innovation monitor 和暂停/恢复路由；CommitFlow（2609.21908v1）已做 semantic commitment monitor、物理条件验证和局部修正；ReTrace（2610.15814v1）已做跨阶段失败归因与后续修正。因此“策略风险 vs 执行风险监测/归因”不再是主推荐。
- RoboValue（2610.26663v1）和 RoboLongR（2610.33863v1）进一步覆盖 value consistency、有效执行顺序和因果进度奖励；不要把顺序敏感的进度模型改名为新记忆机制。
- `Same Weights, Different Robot`（2606.03724v1）给出静态 normalization metadata 的 ExecSpec certificate，但原文限制明确留下 control frequency、action chunk execution、controller convention、contact/hardware；这成为当前新的首要候选边界。
- PolicyIK（2611.05372v1，Apache-2.0 GitHub固定提交）已覆盖高精度IK/反馈残差；TeAR已覆盖telemetry动作整流，FAN已覆盖continual action normalization。新候选必须是动态 executable-equivalence certificate和证书指导的拒绝/受限补偿，不能是三者拼接。
- 当前推荐顺序改为：D 动态可执行策略规范/同体等价证书 > B 评测资产；风险来源分解降级为背景/强对照。D尚未查新通过。
- 现有MuJoCo场景只读预检：6关节×2方向×6执行窗共72条记录；1步窗最大跟踪误差0.079734rad，25步窗平均绝对误差0.011424rad，100步窗最大误差0.000829rad。证据 `experiments/so101/dynamic-interface-precheck.json`，仅证明可观测动态接口，不证明sim-real或VLA效果。
- 新查到 RACE（2610.05719）、PACT-VLA（2610.28019）和RTC（2506.07339）已覆盖长chunk transition/异步延迟/预提交候选选择；候选D不再包含chunk调度，改为组合式静态+动态 executable-equivalence certificate，并将三者列强对照。
- Provael开源Apache-2.0红队框架（主分支3ad892e）已在报告schema中记录实际加载的unnormalizer、chunk、clamp和controller convention digest；候选D不能把manifest字段记录当作核心创新，必须产生可计算的动态证书/任务margin结论。

## D / D′ 的最新深审裁决（取代以上推荐顺序）

- 用户选择继续深审动态 executable-policy 证书。SciSpace 提供新近邻线索后，根代理核对原始 arXiv 正文与固定 GitHub 源码；没有把生成的索引摘要当最终证据。
- **停止 D / D′ 现有核心主张。** ActionABI/ActionShift 覆盖契约等价类、拒绝和有限 probe；ForeReach（2608.02453v1）Algorithm 1 已有 sparse target transitions、residual envelope、task-projected reachable tube 与 margin 比较，缺少有效域外结构假设时必须拒绝。SO-101 真机范围差异本身不足以构成新机制。
- CARE（2610.08917v1）已有 VLA 整回合配对负迁移风险、FWER、序贯候选认证；不能以“局部误差认证升级为闭环统计认证”再次改名。经典 MTL/STL robustness、时序/时空 robustness 与 Vincent 等 rollout 风险界进一步压缩宽题。
- 更正实质性错误：Same Weights displacement 漏掉 z×量程差项，已按 Eq. (9) 修复；其 §4.4 已定义 local margin，不是完全未关联；RoboStress 的 friction/backlash/compliance 模型应归 Self-compensating VLA，不能归 TeAR。
- ActionABI 93cf1e1 与 ActionShift 9991595 已克隆到临时目录，读取 LICENSE、identifiability/converter、DualABI、held-action target-update-mask 源码；本次未构建、训练或复现其性能。
- 四个数学缺口：有限样本最大误差不等于全域上界；same-command 开环差异不等于视觉反馈闭环等价；q 接近不约束物体/接触；边际 conformal coverage 不等于选择后的接受风险。分析核算单独存档，未当机器人实验。
- 零失败 IID Bernoulli 完整回合的示例计算：95% 置信上界小于5%，单个固定候选需59回合；10候选简单Bonferroni示例每候选104回合。这不是普遍最小样本量或已执行结果。
- discovery sources 现为27条版本化arXiv记录、10项GitHub来源及1项经典作者机构来源；新增6篇原始元数据独立核对。主文献库50条未改动，不把二者数量混加为全文精读数。
- SO-101、A100、MuJoCo 与日志共用资产继续保留。尚未确定可立项主方向；不将“否决完毕/资料提交”作为持续研究目标完成。

## DeepSeek 提案与共享前缀候选的后续审计

- 用户提供了 DeepSeek 扫描；原稿保存在 `docs/prior-art/cognitive-compensation-scan-20261114.md`，独立复核见 `review-deepseek-rcbt.md`。没有把其关键词未命中和自评评分当作查新证据。
- RCBT 的“参考类＋分层 GP＋残差迁移”被 NIPS 2007 MTGP、AAAI 2010 AT-GP、UAI 2018 latent-GP meta-RL、ALPaCA 和 RA-L 2022 MRPL 直接约束；单示范均值偏差会破坏多模态正确动作，反例已存 JSON。
- BAS-VLA 原文 §4.2/C.2 已证明统一 semantic separation margin 的局部性质；构造了共享动作前缀任务的目标函数反例，但尚未测 BAS-VLA 训练/真实失效。
- One Word, Different Action（2609.05260）已提供真实机器人 Decision Invariance/Sensitivity 基准；RT-H 已共享语言动作层；Stage-Aware VLA 处理长任务 one-to-many；Acting While Understanding 处理 stale semantics；PHASER/Hide-and-Seek 处理 phase/failure onset。新候选不能宣称首次研究这些宽问题。
- 新候选单独报告：`docs/prior-art/temporal-prefix-calibration-audit.md`。核心只暂称 outcome-aligned temporal semantic calibration/TPSC，必须先证明 uniform separation 在 shared-prefix 上造成错误纠偏，并超过 action-only mask/阶段状态/层级语言等强基线。
- 新增分析核算 `experiments/so101/shared-prefix-separation-audit.json`：6 步 toy chunk、3 步共享前缀、分叉支持 2 步；统一 margin 的 toy penalty 2.0、只在分叉支持上施加分离时 penalty 0.0。这是目标函数几何，不是策略实验。
- `mechanism-first-sources-20261114.json` 已补齐 One Word、RT-H、Acting While Understanding、PHASER、Hide-and-Seek 和 Still Grounded 的 6 个版本化 arXiv 元数据；哈希只证明取到的 API 响应可追溯，不证明已完成全文复现。
- 新一轮原文审计加入 AtomSkill（2512.18368v2）、TRA（2502.05454v2）、Counterfactual Memory Audit（2609.27247v1）和 REFACTOR-VLA（2609.01215v1）。AtomSkill/TRA/REFACTOR-VLA 分别压缩语义时间对齐、组合表示和结果型行为等价的宽泛新意；TPSC 只能继续审计 paired-language 的逐时刻保持/分叉支持。
- CriticHack（2610.02527v1）已把视觉 reward 错误对象放大、总体指标掩盖语义误排和 task-specific verifier 修正做成闭环 MuJoCo 实验；完成判定线降为强对照/复现线，不再作为主创新候选。
- 载体可行性新增可核验证据：`lerobot/smolvla_base`（450M 级、Apache-2.0 模型卡）和 `lerobot/svla_so101_pickplace`（Apache-2.0 数据卡）均为公开、非 gated Hub 资产；官方文档给出 SO-101/多相机/状态/语言/action-chunk 微调路径。它只证明可启动基线，不证明本项目方法或仿真—真机一致性。
- 公开数据接口预检进一步确认：6 维字段顺序与本项目关节名一致，但 LeRobot 公共关节值按角度、夹爪按 0–100 表示；转换到当前 MuJoCo 后 `elbow_flex`、`wrist_flex` 范围越界。证据在 `experiments/so101/smolvla-interface-preflight/summary.json`；在解释策略结果前必须解决版本/校准/关节范围差异。
- 接续分析补上数据集时代证据：`svla_so101_pickplace` 创建于 2025-05-23，早于 LeRobot v0.3.2；旧版 `manipulator.py` 明确使用 degrees（[-180,180]）+ gripper 0–100，因此角度假设成立。`elbow_flex`/`wrist_flex` 真实越界 +3.17°/+4.49°；`robot_type=so100_follower`，不能声称 SO-101 同体。决策：只作 carrier smoke test，TPSC 同体实验需项目自有 SO-101 校准数据。详见 `experiments/so101/smolvla-interface-preflight/range-mismatch-analysis.md`。
- 公开数据集扫描补充：真实 `so101_follower` 数据 `kristaqp/so101-pick-place`（50 eps）elbow 也到 100.0°，复现 +3.17° 越界；说明 XML 96.83° 是保守限位，不是 SO-100 独有。`ngocthuong2212/so101_mujoco_follower_7_31`（200 eps、MuJoCo、SO-101、degrees）action 范围与 XML 逐关节吻合，作仿真载体首选；`kristaqp` 作真实参考；`svla` 保留 SO-100 负对照。证据 `real-so101-reference.json` / `public-dataset-scan.md`。
- TPSC pilot 的 scripted IK 检查：full 120 中 shared-prefix 的 target/executed prefix diff = 0；no-common 从 `above_object` 起 diff >1.2 rad；multi-valid prefix 0、route diff >1.15 rad。kinematic-carry `place_success=120/120`，物理抓取 pilot 0/20、final 56/120。它验证任务结构与路径，不是 learned policy 的 shared prefix，也不是物理抓取 benchmark。
- 完整研究目标仍 active；当前候选未查新通过、未实现、未获得 A100/VLA/真机结果。

## 2026-11-14 后续关键更正（优先于上文旧候选描述）

- 真正调用固定BAS-VLA源码后，旧6步toy的2.0只对应逐步hinge求和；展平chunk损失0。正惩罚不意味着非零输出梯度或任务伤害。公开artifact仍是per_step，必须区分布局与完整损失preset。
- 等未来损失不能作为shared-correct-action判据：同样失败也可等损失；需要分别成功续接的证据，且“允许共用”不等于强制多模态策略输出同一动作。
- 用户15项目盘点带来强对照与载体线索，没有自动带来新方法。MolmoAct2-SO100_101为5.44B、q01/q99、horizon30，与当前角度零位/normalizer不同；TurboVLA的公开LIBERO为7D、H12；StarVLA的SO101待支持。原始revision和hash已落盘。
- 原scripted物理teacher前提有具体错误：OPEN0/CLOSED1.4与实测张合相反；IK追踪转轴而不是官方TCP，相距8.207cm。原数学共享路径不能升级成成功物理共享前缀。
- 本地EGL实测通过，OSMesa库缺失；队列v1取消、v2等待训练完成后才执行20条。载体未就绪时科学结论仍不可辨识；完整选题目标active。

## 20k/20条正式能力screen的最新结论

固定20k checkpoint已完成原20条learned pilot，任务成功/抬升/放置均0/20，10对全部保留。
本轮只证明这套公开单任务训练与当前未验证适配的任务载体未就绪；不支持正确共享前缀、
语义因果作用或uniform separation伤害。后者未运行，TPSC不进入方法实现。

进一步修正：共同可行动作存在不强制点态一致，强制分离不一定伤害正确性；过大margin也不专属共享前缀问题。
ECT配对普通imitation是必须比较的简单强基线；通用antithetic flow训练已有机器人工作。
MolmoAct2公开75条双YAM rollout没有成功标签，不能从固定抽帧或停滞proxy宣称state hallucination。
当前仍没有通过选题门槛的方向，研究目标active。新证据必须来自合格策略的具体机制和超出强简单对照的结果。

新的积极可行性线索：固定外部SO101控制器b02b8b2在当前MuJoCo4.0.1实际抓放成功，hover负对照未通过，
独立双指接触记录复跑最长连续持物抬升2.6365s；其显式指垫/friction2/28mm物体不同于原TPSC，不能升级为本项目
learned能力或真机结论。R3L、DEFLECT-v3与TPC-FM进一步排除通用prefix mask、共享随机数、配对flow时间的宽创新。

## 匹配载体与非Markov近邻的新证据

匹配单任务的物理teacher32/32，但普通小BC固定2000步测试0/20，因此即使不再有公开数据接口混淆，
也不能从失败解释补偿伤害。同权重val诊断执行30步4/8、执行6步0/8，提示需要检查阶段推进/闭环偏离；
不是已确定根因。30步8/8持物抬升与放桌，失败4例未释放，不能修改成功谓词把它们算通过。

Why Does Action Chunking Improve…、Revisiting Open-Loop Execution、Measuring the Stability Assumption已有
非Markov表达、延迟集成、长历史和配对开环/闭环传播探针；TRACT已有未来phase路由与响应亏损积分。
因此不能把本次horizon诊断直接当新研究机制。APEX/Tune to Learn/NADA/GAP等同时要求
“精度改善破坏阶段线索”窄问题必须与传统gain/noise/contact及模态捷径解释区分；当前尚无证据。
原文/来源缓存与固定GAP源码实现问题详见 `docs/prior-art/history-compensation-mechanism-screen.md`。

## 普通循环BC与初始视觉特征的实际边界

相同初始化/采样/参数量的carry/reset在新20个相同初态上为11/20、4/20；
carry独成功9、reset独成功2，共同成功2、共同失败7。单训练seed只支持此设定下的观察，
不证明记忆含正确事实或旧CNN失败由非Markov性唯一导致。
固定初始RGB特征版本在另20个新初态为15/20，19/20持物抬升，仍未达16/20资格门槛。
不把15/20近似算通过；按计划停止继续微调此小模型，补偿干预仍未运行。

全24train最近的完整输入没有严格相等；近似输入/不同未来chunk不能冒充不可辨识证明。
初始固定颜色定位的val误差1.49mm只表明图像含位置信息，不是硬件/学习策略定位精度。
Copycat已有前动作捷径及目标条件对抗器；CSA已有单因素算子混合偏移和延迟顺序；
IMEP已有事实/同事实/重复/最小扰动对照与delivery、决策/执行分离，不能把这些机制包装成新方向。
见 `docs/prior-art/feedback-memory-followup.md` 及两组独立能力记录。

新增直接近邻SAGE/GapONet与官方SO101教程，固定源码和检查点契约见
`docs/prior-art/nvidia-so101-sage-gaponet-audit.md`。不能再把配对sim-real间隙采集、
历史执行模型、VLA后接神经补偿及同体展示当核心新意；官方SO101闭环集成本身仍为future work。
新入口有匹配场景/75sim示范/N1.6权重元数据，可作为下一步成熟基线审查对象，但本轮未加载或验证能力。

## 2026-11-15 VFD可行性后续：读取前的边界

- 上轮属于progress：四阶段解析/回归探针、强对照及提交570ef7c改变了下一动作；尚无真实任务损害。
- 当前只读资产资格检查：官方UQ仓库明确不提供checkpoint/实机代码，逐成员训练资源高于本地12GB，尚非即用SO101 ensemble；资源值仅为作者运行配置，不是硬最小值。
- 新发现需原文细读：2608.28010v1已经声称相同末端分布也可有不同CFM比率；2611.11650v1 FlowEval诊断部署/适配，并列post-transformed demos为局限。两者此时只完成摘要/目录读取，不能泛化其覆盖。
- 发现版本一致性问题：UQ当前仓库说明2026-10更新generalist版本，而上轮理论检查明确使用v1；需核最新正文是否新增路径/近似误差讨论。

- 已补核UQ v2 §4/A.2/§7/C.7：连续定理仍明确Gaussian OT条件；learned场评分仍作近似。v2已有子集flow-time消融，后期单点s=.8在四成员中不降balanced accuracy；不能把选时/省节点当新核心。
- 2608.28010v1 §6.2与A.5已读：用二维反对称旋转场保持整个Gaussian边缘分布不变，但CFM比率非零。该论文目标是CFM/NLL比率，不是直接VFD；它已占据路径无关性失效的一般原理，不可据我们的不同一维构造宣称首次。
- Bijou确有公开raw weights及本地低显存推理说明，但现有同seed对比多为AR或采样噪声多draw，不等于独立训练flow ensemble；完整许可/任务成功审查仍待后续，不安装其代码。
- 新的优先资产入口：Advaitic/drishti声称MuJoCo SO101 SmolVLA有带成功/失败标签rollout；SO101 Bench 2610.36420发现。此处仅检索命中，尚未将摘要数字采信为本项目证据。

## 2026-11-15 新问题发现：两条有边界的检索

- 上轮为progress：7e49b34实际审计公开63条/4607步、补核UQ v2并降低VFD优先级。当前新筛同步观测与语言任务可区分性，最多深审两项。
- 同步宽题已有UMI原始论文RSS2024 p045：按最慢流对齐、q插值/相机软同步、测观测及执行延迟并丢弃过期动作。Koide OAGM2019原稿已有robot-camera重投影时间偏置估计；不能把补时间戳或在线offset校准直接当新核心。此时仅检索命中/摘要范围，待定向阅读。
- SciSpace新发现InstructMove、One Word Different Action；CAST/CAG/ECT/CounterAlign也命中。当前仅摘要元数据，不用命中数量宣称查新覆盖或通过。任务成功集交叠可能造成语言诊断无区分力的假设尚无本项目新证据。

- 定向已读InstructMove v1 §3.1–3.4/4.3/5：已有多可行候选/唯一语言目标/同场景换指令和阶段分数；普通任务可区分性宽题不能立项。§4.3明确target-specific成功lift可提前结束，generic等运行全时域。拟核一个更窄问题：忽略语言但遍历候选的共同策略能否因目标特定停止而两边得分；尚未读实现，不能认定原基准有此漏洞。
- 已读One Word v1 §III：固定可执行动作集合，按唯一正确动作/集合/序列严格匹配，不仅比较action差异。它已有稳定/变化配对和排除/数量/顺序约束；不能把严格首选择/多约束配对称新贡献。
- 已读DAM-VLA v1 §3/5：已有异步modality buffers、q100Hz/视觉25Hz、独立gate、训练统一100Hz标签及执行延迟处理；局限是力尚未chunk内修正、视觉固定timer。宽泛异步或加力修正直接落入既有/直接下一步，停止该宽题。

- 固定RoboOrchard f2e041e（2026-10-22）原样AST定义+显式布尔checker适配器：共同scan正反顺序在N=2/3/6的累计success全通过，固定末时刻当前条件仅末对象通过；no-op/reach-only失败、single各1对象通过，14/15 dwell边界正常。不是Isaac/VLA结果；源码当前4阶段与论文v1 2阶段分开。
- 接续物理见证执行前另冻结PLAN-physical；同MuJoCo SO101显式新增第二同物理cube，5条固定测试全部保留。正反scan都实际持物抬升两个对象，各最长1.241s，单目标仅相应对象、no-op均无抬升；0限幅，最大穿透约.117mm，无rollout物体pose写入。没有真实VLA或原Isaac复现。
- 源码普通Evaluator._step_episode见target成功即break，counterfactual固定时域；单纯固定时域保留ever-score不能排除共同scan。此时原始loop组件对照仍待输出。
- 注意语义边界：若用户/任务本就允许额外操作，依次完成两对象可合法；问题是成功指标不能识别语言必要性，不是无条件错误标注。首目标或显式只选一个/commit规则是既有简单修正，不当新算法。

- 原始Evaluator._step_episode组件已实跑：正反共同序列在两目标绑定都成功，目标first-hit在24/53步分别停止；强制56步但保留累计评分也全成功。此为原样loop+显式假环境，未运行完整Isaac wrapper。
- 老近邻已检索定位：Inner Monologue CoRL2022已有oracle-vs-fixed termination对照；Code as Policies同类对照。需要细读后限制新颖性，不能把去oracle/固定horizon称新原理。SciSpace本轮先前发现8条，之后工具被移除，不尝试当全文来源。

- 查新补核Inner Monologue作者原稿§4.1、Code as Policies v4附录K：oracle和固定动作数/末状态评价早已对照；去oracle/显式停止不是新方法。新问题若有贡献，只能是多候选静态text-indispensability与整个轨迹验收语言必要性的区别及实际影响；当前尚无跨基准/learned排序影响。
- Scholar请求HTTP200但标题Verifying...，result cards=0；这是验证拦截，非成功检索或无相关文献。原响应/hash保留，不将HTTP状态当查新覆盖。
- 物理fresh replay五条轨迹逐字节一致，全部1848个命令；独立控制率接触检查每个实际抓取37连续样本，未抓对象为0。所有trace中的两对象均在TCP .2m内只是事后本场景距离诊断，非原Isaac行为统计。
