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
