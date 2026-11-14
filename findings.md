# 准备阶段事实与边界

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
