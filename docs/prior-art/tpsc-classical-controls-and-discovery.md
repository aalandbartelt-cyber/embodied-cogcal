# 选题证据继续收紧：经典强对照、真实rollout与载体资格

2026-11-14。目标仍是确定可经查新、能做出核心增量与SO-101同题仿真—真机成果的研究方向。
《思考，快与慢》和精度补偿只作启发，不要求保留TPSC名称。**本轮仍没有可以冻结的新方法方向。**

## 1. 新增强对照改变了什么

| 原始来源 / 实际阅读范围 | 已有机制 | 对候选的约束 |
|---|---|---|
| [SupCon，NeurIPS2020 §3](https://proceedings.neurips.cc/paper_files/paper/2020/file/d89a66c7c80a29b1bdbab0f2a1a94af8-Paper.pdf) | 用标签构造多个正例，改变一正多负的训练关系 | “把伪负例改为正例”不是新原则；需要证明任务可行动作支持的定义和取得方式有增量 |
| [DCL，NeurIPS2020 §3–4](https://papers.neurips.cc/paper_files/paper/2020/file/63c3ddcc7b23daa1e42dc41f9a44a873-Paper.pdf) | 在潜在类混合假设下，估计并扣除负样本里的同类贡献 | 简单降权/去偏不足以立项；其随机采样假设也不能不加区分套到BAS的显式break pair |
| [FALCON v1 §2–3](https://arxiv.org/html/2505.11192v1) | 按anchor和训练状态调整负样本难度，以独立生成目标的改善作反馈 | “用另一种结果信号学负例选择”已有近邻；没有直接证明其能解决机器人成功续接判定 |
| [ECT v1 §5.1、F.1、K](https://arxiv.org/html/2609.39971v1) | 有效反事实示范、配对呈现、同一更新内的普通imitation损失；π0.5两分支还共享flow噪声与时间 | 增益可能来自有效数据、配对、平衡或噪声；候选必须比较同一数据池的独立BC与配对BC，而不只比较强制分离 |
| [IntentVLA v1](https://arxiv.org/html/2605.14712v1)及[官方仓库](https://github.com/ZGC-EmbodyAI/IntentVLA) | 用近期历史的短期intent稳定相邻chunk，研究观测混叠；仓库当期主要释放AliasBench | “加历史保持动作模式”不是新点；模型代码未完整开放不意味着机制空白 |
| [CompCPZ v1](https://arxiv.org/html/2608.17717v1) | 保留析取语言的多分支可行集合；理论有sound-set范围限制 | 不能把“多模态合法动作不能取中点”当首次；它也不自动覆盖普通VLA任意非sound输出 |
| [SOUL v1摘要](https://arxiv.org/abs/2610.09496v1) | 对未实现状态仍继续行动的state hallucination作稀疏特征分析和选择性遗忘 | “策略以为已经抓到”已有直接研究；本轮只核摘要，不伪称完整复现 |
| [R3L v1 §4.2/Algorithm1](https://arxiv.org/html/2601.03715v1) | 文本agent/reasoning的base/retry轨迹共享prefix，只更新pivot后的suffix | 保护共享前缀、只纠正分叉后错误不是新原则；与连续VLA不同，不声称直接覆盖所有动作支持估计 |
| [DEFLECT v3 §3/附录D](https://arxiv.org/html/2605.19294v3) | stale/future动作共享采样随机性；FM-DPO的候选、reference及SFT共享时间/噪声，并承认单样本非线性surrogate的Jensen间隙 | 共享噪声隔离条件变化、FM损失不等于精确likelihood等宽主张已有直接机器人近邻 |
| [TPC-FM v1 §3.1–3.2](https://arxiv.org/html/2602.04908v1) | 同路径配对flow时间并加入速度一致性项，研究方差/一致性 | 通用paired-time/noise降方差不足以立项；其目标含附加项，不能混称只改变普通BC的无偏采样 |

已缓存原论文快照和hash，阅读层级逐项记录在
[mechanism-primary-sources.json](../../experiments/so101/vla-open-source-audit/mechanism-primary-sources.json)。
Google Scholar本次请求仍为403；SciSpace只用于发现候选，再回到原论文核验。
39条搜索命中包含重复版本和仅摘要线索，不记成39篇全文阅读。

这些论文不等于“TPSC已被某一篇完全覆盖”。它们明确排除了过宽的创新描述，
并要求更强的简单对照。当前仍缺忠实前作的任务结果伤害，更缺超出这些对照的证据。

## 2. 一个窄的新问题线索，以及为什么暂不升级为方法

ECT附录K明确说，其配对收益混合了counterpart共呈现、样本平衡、共同flow噪声和共同flow时间，
优化机制尚未拆清。**这是可做机制分解的具体线索，不是作者已证明其方法失效。**

从这里提出“用antithetic噪声或分层时间减少方差”仍不足以成为新方法：
[BEHAVIOR2026原文 §5.1–5.4](https://arxiv.org/html/2611.14432v1) 已在机器人π0.5策略训练中使用
多flow样本、分层时间和正负噪声配对，保留边缘分布并分析方差/计算开销。
因此通用噪声降方差方向不立项。若以后验证“不同任务counterpart之间的耦合”有独立问题，
仍须固定数据/平衡/更新数/算力，分解同噪声、独立噪声、普通antithetic等因素，
并先得到任务损害证据；本轮没有运行该学习实验。

## 3. 实际读取的真实策略rollout

为从真实现象出发，单独读取了作者公开的MolmoAct2 candy rollout：

- [ID固定revision](https://huggingface.co/datasets/allenai/eval_molmoact_candy_sorting_in-distribution/tree/b68b2df889134d23751ee09f3abc00b2cb94be71)：50 episodes / 59,645帧。
- [OOD固定revision](https://huggingface.co/datasets/allenai/eval_molmoact_candy_sorting_ood/tree/0ebe2b5468a8e40d268c13bc87fccebc4de9332d)：25 episodes / 29,901帧。

它们是14通道双臂YAM，不是SO-101；独立存放在`data/discovery/`，没有混进TPSC任务对。
实查全部75条episode身份、帧区间、长度、14D有限值；读取固定前5条episode各6个固定时间点的顶部视频。
后段在箱体附近停留、桌上仍有多枚糖果是一个**可观察的停滞候选**；关节值仍有微小波动。

不能据此命名“状态幻觉”或计算失败率：

- 检查到的frame和episode文件没有success/failure/reward标签，也没有推理chunk边界、观测年龄或dispatch日志。
- 我们最初的严格tail-range比例规则实际标出0条；几乎静止关节的小量程会影响该maximum，
  因此保留原结果，不事后调阈值制造想要的失败率。
- 固定抽帧不能证明完整任务目标、物体接触状态或停滞根因；ID/OOD也不是配对干预。
- 原论文各平台的评分协议不完全相同；没有逐条标签时，不反推已发表表格的二元成功数。

源资格与全量episode描述值见
[source-qualification.json](../../experiments/discovery/molmo-rollout-screen-20261114/source-qualification.json)。
大视频、源parquet和本地contact sheet保存在被git忽略的数据目录，revision/hash可复核。
本轮只把它当问题发现线索，没有把公开数据当作我们的验证结果。

## 4. 物理teacher不能靠两处代码修正就算就绪

上一轮已发现旧脚本张合方向反置、IK追踪转轴而非TCP。随后实际做了5组、每组5个侧向offset的
定向物理debug，全部是**同一个初态episode的适配探索**，不是25个独立episode。

- 固定垂直approach/lift的版本，求解器未达到所设IK精度；这不是几何不可达证明。
- 放松approach/lift朝向后，位置IK可接近毫米量级，但没有得到稳定双指抬升。
- 显式测试更窄物体的几何控制、保持原质量以及更接近关节下限的夹爪命令，也没有得到合格teacher。
- 原XML、原manifest和正式20条learned pilot仍保持原样；没有传送、焊接或运动学carry物体。

全部脚本快照、原始trace和变体记录见
[physical-readiness-exploration](../../experiments/so101/tpsc-pilot/physical-readiness-exploration/README.md)。
它们说明当前teacher未验收，不能证明VLA失败或TPSC失效。先前低IK误差不能替代物理抓放能力。

另做了一个积极资格检查：固定外部SO101仓库`FERBIN12/so101-manipulation-eval`的b02b8b2，
在本机MuJoCo4.0.1实际完成一次接触抓放，悬停对照不通过放置判定；独立仪器化复跑记录双指同时接触且抬升
最长2.6365s。它添加盒状指垫、pinch-centre site和摩擦2.0，物体28mm/20g，与原TPSC场景不同。
这是有条件的teacher可行性证据，不是learned policy或同一接触模型已验收。
见[原始运行与接触核验](../../experiments/discovery/so101-upstream-contact-reproduction-20261114/README.md)。

也从ngocthuong2212的HF主页追溯作者直接链接的GitHub身份，定向检查3个公共仓库：
两个仅README，一个空仓库，尚未取到原录制scene/camera/calibration源码；没有声称穷尽其全部仓库。
见[来源记录](../../experiments/so101/vla-open-source-audit/carrier-author-source-scan.json)。

## 5. 当前决策与下一证据

1. 普通carrier训练已从最近完整18k状态续跑至固定20k终点，记录采样器恢复限制。
2. 最终checkpoint已执行原20条能力screen，任务成功0/20、抬升0/20；所有episode与失败均保留。
   [全部pair报告](../../experiments/so101/tpsc-pilot/runs/local-5070ti/pilot-20k-prefix-report.md)只描述动作差异。
3. 当前报告“载体未就绪”；在修好任务数据/teacher前，不从动作差异抽取语义损害结论，也不扩大120条。
4. 若能力合格，再识别正确共享前缀，并比较普通BC、同池配对BC、明确布局的完整BAS目标和经典强对照。
5. 只有忠实基线出现可重复且有实际后果的失效，才设计针对性方法；若普通成对BC等简单对照已解决，停止新方法主张。

选题门槛仍未满足，完整目标active。这里没有把文献增加、环境修复、teacher调试或自动队列启动
当作已找到研究方向，也没有将新发现的作者局限包装成新算法。
