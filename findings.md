# 准备阶段事实与边界

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
