# 候选 D 深审：动态可执行策略规范与同体等价证书

日期：2026-11-14。状态：定向查新/红队，不是正式机构查新，不是本项目结果。
约束：低成本 SO-101、A100、同体 MuJoCo—真机；冻结或轻量适配 VLA；不预设新增力觉/温度/电流传感器。

## 当前结论：停止以 D / D′ 的现有表述立项

**本次深审否决了此前“首要候选”的推荐。** ActionABI/ActionShift 覆盖契约识别与适配；
ForeReach 进一步覆盖“稀少目标系统数据→动态误差集合→任务安全距离→执行前认证或拒绝”。
因此，D′ 的“任务 margin 校准的物理 fidelity 证书”也没有留下已证实的核心增量。
SO-101、VLA 和真机验证是实验条件，不能单独修复机制重叠。
它可以服务部署与工程验证，但目前不满足用户要求的单一核心研究创新。

第 1–8 节保留候选形成时的论证以便追溯，均受本结论约束；其中的实验安排不是继续投入 D 的建议。
第 9 节是本次新增的决定性审计、数学边界与资源判断。没有将 D′ 再改名为 D″。

## 1. 直接最近工作：Same Weights 的精确范围

[Same Weights, Different Robot: A Deployment Safety View of VLA Policies，2606.03724v1](https://arxiv.org/html/2606.03724v1) 把可执行 VLA 写成

\[
(f_\theta,\mathcal I,\mathcal Z,\mathcal U_k,\mathcal C),
\]

其中 \(\mathcal U_k\) 是 metadata 选择的 action unnormalizer，\(\mathcal C\) 是控制器语义。论文对 quantile unnormalizer 定义

\[
\mathcal U_k(z)_i=q_{01,i}^{(k)}+z_i(q_{99,i}^{(k)}-q_{01,i}^{(k)}),
\]

并证明相同 mask 下替换 metadata 的**被归一化维度**位移为（未归一化维度为零）

\[
\Delta_i(z;k_c,k_w)=q_{01,i}^{(w)}-q_{01,i}^{(c)}
+z_i\left[(q_{99,i}^{(w)}-q_{01,i}^{(w)})-(q_{99,i}^{(c)}-q_{01,i}^{(c)})\right],
\]

再用校准动作集定义均值/尾部 drift certificate。该证书不需要模型推理或 rollout，且论文的 LIBERO replay witness 显示静态 metadata 错配可以翻转成功率。

更正：初稿漏写了上式的 \(z_i\) 乘量程差项；这是实质性公式错误，已按原文 Eq. (9) 更正。
原文 §4.4 / Eq. (16) **已经定义局部 action margin 并讨论 displacement 越界**，只是没有部署时可得的 margin 估计。
因此其 future work 不能被解读为“尚未把误差与任务 margin 关联”。

这篇论文同时明确限定了结论：阈值是 reporting scale，不是普适安全裕度；certificate 不是完美预测器；实验只在 LIBERO replay，不能替代真实硬件。它的未来工作明确列出 task-specific margins、contact-sensitive safety metrics、hardware-specific action units，以及 image preprocessing、camera orientation、gripper convention、control frequency 和 action chunk execution 等 normalization 之外的 executable semantics。

因此我们不能声称“发现 checkpoint 之外还有接口”或“第一次做 certificate”。可继续的问题必须严格落在**动态执行链的可验证证书与同体物理结果**。

## 2. 近邻逐项排除

| 工作 | 已覆盖 | 候选 D 不能重复的部分 |
|---|---|---|
| [FAN](https://arxiv.org/html/2609.21358v1) | 任务流中的 action normalization consistency/coverage/causality，固定统计量减少坐标漂移 | 它不是仿真—真机 command-to-achieved 动态映射，也不给接触/时延/限幅证书 |
| [TeAR](https://arxiv.org/html/2609.36182v1) | 冻结策略+telemetry 条件动作整流；SO-ARM101物理评估 | 它是 test-time rectifier，主要用 OSC/温度电流电压；不提供 rollout 前 executable equivalence certificate |
| [PolicyIK](https://arxiv.org/html/2611.05372v1)；[代码](https://github.com/Tinaliu0123/PolicyIK) | q/pose feedback、误差相关增益、高精度 IK/holding，仿真和真实机械臂 | 上游 VLA action metadata、chunk timing、控制器约定和 sim-real policy identity 不在其问题内 |
| [RTC](https://arxiv.org/abs/2506.07339)、[RACE](https://arxiv.org/abs/2610.05719)、[PACT-VLA](https://arxiv.org/abs/2610.28019) | 处理异步推理、长chunk transition timing、pre-commit observation 的候选选择 | 它们改变运行时 chunk 执行/选择；不等于组合静态+动态物理语义证书，候选 D必须把它们作为强基线 |
| [Provael](https://github.com/provael/provael) | Apache-2.0开源红队框架已在报告中记录实际 unnormalizer、chunk、clamp 和 controller convention 的 deployed-policy digest | 说明“把接口字段记录进manifest”已是工程实践；D不能以新增manifest字段作为核心贡献，必须提供可计算证书/覆盖或任务margin结论 |
| [ActionABI](https://github.com/Archerkattri/actionabi) / [ActionShift](https://github.com/Archerkattri/actionshift) | MIT 开源；离线等价类/校准拒绝与在线有限 probe 适配，grammar含 permutation/sign/scale/target/frame/lag/gripper | 直接否决“恢复隐藏 action contract/在线适配”宽题。D′必须不做通用契约识别，而研究任务/接触 margin 对真实物理差异的覆盖校准；两项目的主实验是 ManiSkill/仿真，不等于SO-101真机证书 |
| [SO-101 Bench](https://arxiv.org/html/2610.36420v1)；[代码](https://github.com/5hadytru/so101_bench) | 数字孪生、真实策略排序保持、仿真成功率偏乐观 | 相关性/排名不是逐 action 执行等价；无证书指导拒绝/补偿 |
| [Self-compensating VLA](https://arxiv.org/abs/2609.37334) 的 RoboStress 执行退化模型 | state/history-dependent friction/backlash/compliance/gravity-like execution error | 该模型不能归给 TeAR；候选 D不能重新提出“执行误差存在”或“残差可补偿” |
| 经典系统辨识、DOB、feed-forward、工业机器人标定 | 动力学/伺服误差估计、跟踪补偿和稳定性边界 | 这是最大红队；如果只需低阶 sysid + 误差阈值，D不构成VLA研究创新。 |

另有 [Phys2Real](https://arxiv.org/html/2510.11689v2) 的物理参数先验+在线交互估计和 [Stability-aware residual RL](https://arxiv.org/html/2609.21307v1) 的 DOB+有界残差，说明“仿真物理不确定性融合”“残差补偿”“稳定性约束”都不能当 D 的独立贡献。

## 3. 候选 D 的精确科学命题

给定冻结 VLA 输出的 normalized action chunk (u_{t:t+H})，定义仿真和真实执行链

\[
q^s_{t:t+H}=G_s(u_{t:t+H},x_t),\qquad
q^r_{t:t+H}=G_r(u_{t:t+H},x_t).
\]

\(G\) 包含 unnormalization、zero/scale、hold/replan、delay、clipping、servo tracking 和已登记的 observation/action timing。短安全校准集只用可逆、低幅度动作，估计 \(\widehat G_r\) 及不确定区间。

中心命题为：

> 在未见任务布局上，动态接口证书是否能在执行前预测“同 checkpoint 在 sim 与 real 的物理动作语义会越过任务/接触 margin”，并优于静态 metadata 检查、固定短 chunk 和普通 residual；当证书超界时，受限补偿或拒绝部署是否降低风险且不损害可执行任务覆盖？

新意若成立，应来自**可检验的任务 margin—物理 fidelity 映射和独立覆盖**，而不是 action contract 恢复、manifest记录或“先校准再验证”的流程。

一个可被经典方法直接击穿、但能明确检验的组合式候选是

\[
\Gamma_W(Z)=\sup_{u\in Z}\left\|W\left[C_rU_r(u)-C_sU_s(u)\right]\right\|,
\]

其中 (U) 是归一化/零点/单位映射，(C) 是 chunk 保持、时延、限幅和伺服响应的有限窗口算子，(W) 是关节或末端任务权重。用短校准轨迹得到 \(\hat\Gamma\) 和不确定半径 \(b_\delta\)，再与任务/接触 margin (m(x)) 比较：

```text
certificate_safe if Γhat + bδ < m(x)
otherwise reject or use a bounded correction
```

这不是已成立定理。它只有在能定义可测的 (m(x))、独立的校准/测试轨迹和覆盖保证时才有科学意义；否则只是把系统辨识误差换成符号。经典鲁棒控制/诱导范数界、DOB 和在线 system identification 是必须先击穿它的强对照。

## 4. 最小反例和强基线

先不加载大模型，使用 MuJoCo 中的固定 action sequence 构造：

1. 静态 metadata 一致、动态 delay/gain 不同；
2. metadata 一致、action hold/replan 语义不同；
3. 动态映射相同、任务/策略本身失败；
4. 接触 margin 很小但全局均方误差相同的两条轨迹。

强基线：

- Same Weights 的静态 drift certificate；
- 仅 zero/scale/normalizer 校准；
- 固定 horizon、固定频率、固定 latency 的工程对照；
- 经典低阶 system identification + DOB/feed-forward；
- TeAR（有 telemetry 时）与 PolicyIK（需要 IK 时）；
- 无补偿、受限补偿、证书拒绝三种决策；oracle (G_r) 只作上界。

候选 D 必须被以下任一结果淘汰：静态 certificate 已解释全部风险；固定 chunk/传统 sysid 同等有效；certificate 在未见布局失效；或任务失败主要来自模型语义能力而非接口。

## 5. 同体仿真—真机实验

选一个已有 SO-101 可达短任务和一个轻接触任务，冻结模型、normalizer、task predicate、初始姿态、控制周期和 chunk 协议。校准轨迹记录 normalized command、unnormalized command、q command、q achieved、RGB、时间戳、hold/replan、clip 和 reset。

仿真先注入可控 delay/gain/clip 作为执行映射 ground truth，只称 software execution-map perturbation；真机再用同一字段评估真实映射，不把仿真注入叫作真实齿隙或热退化。

主终点不是单一成功率，而是：

- certificate 对未见动作窗的 coverage/violation rate；
- 证书超界与真实任务 failure/contact-margin crossing 的关系；
- 在固定校准动作、额外 wall-clock、候选动作步数和 reset 预算下，拒绝/受限补偿相对强基线的风险—覆盖曲线；
- 仿真中预测方向是否在 SO-101 真机保留。

如果没有可靠 q/command 时间对齐，或者只有模型不会做任务而没有接口误差，不能把失败记为 D 的支持证据。

## 6. 可行性和开源资产

- A100 只需运行冻结 VLA、并行 MuJoCo 和轻量估计器，不需要从头训练 7B。
- 本仓库已经有 SO-101 MuJoCo、观测/动作日志和确定性 reset；可先完成不含 VLA 的动态映射反例。
- [PolicyIK](https://github.com/Tinaliu0123/PolicyIK) 主分支固定 `22f3a5cddc674e88995cae18b93cd5a5cb3ddb86`，GitHub报告 Apache-2.0；作为控制/IK强对照，不能作为本项目新贡献。
- [SO-101 Bench](https://github.com/5hadytru/so101_bench) 主分支 `470e09e2b66658049e1248378f20ce39bd134ad6`，Apache-2.0，但依赖 Isaac Sim 5.1/Isaac Lab 0.54；保留其任务/评测思想，继续使用本项目 MuJoCo。
- Same Weights 没找到官方实现；其静态公式可按论文重写，必须在报告中标为独立实现而非复现代码。

## 7. 初步判断（已被第 9 节取代）

D′ 的最强依据是 Same Weights 明确留下 task-specific margin/contact/hardware 边界；最强反对意见是 ActionABI/ActionShift、DVIDIA paired-trace gate、工业系统辨识、DOB、TeAR、PolicyIK、RTC/RACE/PACT 可能已足够解决。下一阶段必须先做无模型 margin 反例、经典 baseline 和 SO-101 轨迹分割；在此之前不命名算法、不采购传感器、不宣称新颖性。

## 8. 本仓库的无模型可行性预检

在现有 MuJoCo 场景上运行了只读的 position-target 预检，SO-101 的 5 个臂关节加夹爪共 6 个目标通道，
每通道 2 个方向 × 6 个执行窗，共 72 条记录。命令增量为 ±0.08 rad，执行窗为 1、5、10、25、50、100 个仿真步；结果写入 [dynamic-interface-precheck.json](../../experiments/so101/dynamic-interface-precheck.json)。

观察到：1步窗的最大绝对跟踪误差为 0.079734 rad，25步窗的平均绝对误差为 0.011424 rad，100步窗的最大绝对误差为 0.000829 rad。该结果只证明当前仿真接口中“命令时刻—实际 q—窗口长度”是可记录且早期存在非零动态误差；它不是硬件传递函数、不是 sim-real 差异、不是VLA成功率，也不证明候选 D 的证书有效。它给出了一个无需大模型即可否证 D 的最小起点。

## 9. 最终深审：直接覆盖与证明缺口

审查轴：control；baseline/statistical/real-world；missing-traditional-baseline/overclaimed-results；audit。
检索使用 SciSpace 发现线索、原始论文核验、GitHub 固定提交读源码；不以索引生成的总结代替原文。
本次没有运行第三方算法，也没有新增本项目 VLA/真机结果。

### 9.1 ForeReach 已有与 D′ 对应的核心判据

[Certifying Plans under Model Mismatch: A Trilemma for Reachability from Scarce Data,
2608.02453v1](https://arxiv.org/html/2608.02453v1)，§2–4、Algorithm 1、§5.3：

- 目标动力学写成 nominal model 加 residual，使用有限 one-step target observations；
- 必须另行提供认证域内有效的逐分量 residual Lipschitz 上界，数据只能驳倒它，不能验证未观测区域；
- 构造 set-membership residual envelope，传播 reachable tube；
- Algorithm 1 第 20–23 行比较任务投影 tube 半径与 unsafe-set clearance；其他步骤还检查认证域，任一检查不通过则拒绝；
- §5.3 已认证 learned-policy action chunks。实验是 point-mass/dynamic-bicycle，没有 SO-101 真机，也不是完整视觉 VLA。

**本项目判断：**它没有完成我们所有硬件条件，但已经覆盖“少数据动态误差界＋任务 margin＋预执行拒绝”的方法骨架。
把 obstacle clearance 换成夹爪任务距离，再接一个标准补偿器，不足以支撑当前创新主张。
更关键的是，它证明了缺少域外结构假设时的认证障碍；不能用几条安全校准轨迹的最大误差绕过。

### 9.2 任务 margin、时序 margin 和统计认证也各有直接解法

| 原始来源与阅读范围 | 已覆盖的对象 | 不能据此夸大的范围 |
|---|---|---|
| [Fainekos–Pappas 2006，作者机构记录/摘要](https://asu.elsevierpure.com/en/publications/robustness-of-temporal-logic-specifications/) | 距离不满足的 robustness，足够接近的 timed trace 保持同一 MTL 谓词 | 本次未逐式重审该全文；不能称“首次把轨迹误差与任务裕度关联” |
| [Temporal Robustness，2203.15661v1，§3–6](https://arxiv.org/html/2203.15661v1) | 同步/异步时间平移的任务鲁棒性与控制 | 增加 latency margin 本身不是新原理 |
| [Spatiotemporal Robustness，2603.29868v1，§2–4](https://arxiv.org/html/2603.29868v1) | 联合空间/时间扰动的多目标鲁棒语义 | 不能简单把“空间＋时间联合证书”当空白；作者没有声称 SO-101 硬件认证 |
| [Stochastic Simulation-Gap Functions，2603.20672v1，§II–IV](https://arxiv.org/html/2603.20672v1) | 数据驱动状态/输入相关模型差异及带假设的规范控制 | 其基本 gap 针对随机演化的**期望**，不能直接当单条随机轨迹的 pathwise tube；实验是随机仿真 |
| [Vincent–Feldman–Schwager，2309.10874v2，§III/VI–VIII](https://arxiv.org/html/2309.10874v2)；[代码](https://github.com/StanfordMSL/performance_guarantees) | 有限 rollout 的性能/失败率上界、给定分布移位的稳健界、多候选校正 | 依赖模拟分布/目标分布关系与独立样本，不能从 simulator 自动推出现实保证 |
| [CARE，2610.08917v1，§3/A.5–A.6](https://arxiv.org/html/2610.08917v1) | 固定候选族的 VLA 加速选择；对齐初始条件的整回合负迁移风险、FWER、序贯采样 | 不是 sparse-transition 的物理管道证书；也不自动解决真机重复性、时变硬件或任意在线适配 |

### 9.3 GitHub 从 README 核对到源码

| 项目/固定提交 | 本次实际读取 | 审计结论 |
|---|---|---|
| [ActionABI `93cf1e1`](https://github.com/Archerkattri/actionabi/tree/93cf1e154c949565a0069441fc05ed5ef9e311c0) | `src/identifiability.cpp` 的 retained hypothesis set、字段一致性、split-conformal rank；`src/converter.cpp` 的歧义拒绝 | 不是只有宣言，相关机制确有源码。`calibrated_coverage` 同时是接口传入值，不能仅凭输出字段断言真实覆盖成立；本次未复现其校准 |
| [ActionShift `9991595`](https://github.com/Archerkattri/actionshift/tree/999159581e2d3a30d899a53b4ada386122c6d806) | `src/actionshift/adaptation/dualabi_adapter.py` 的 task-regret probe；`src/actionshift/envs/wrapper.py` 的 held-action/target-update mask | 在线探针、任务相关识别、部分状态化执行语义已有实现。Unknown-ACK 轨道已有“命令未应用时不推进 target memory”，不能重新包装成我们的发现 |

两个仓库均读取了 MIT LICENSE；本次只克隆至临时目录并读代码，没有安装依赖/训练或复现其性能。
ActionShift 的部分 task-regret preview 是执行动作误差近似，并非真实任务价值的精确 oracle；保持这个边界，不能为否决候选而夸大近邻。

### 9.4 原候选的四个数学缺口

下面是本项目的逻辑审计，不是新的定理或物理实验。

**有限校准最大值不是全域误差界。** 例如有限数据位置为 \(z\in\{-1,0,1\}\)，
两种 residual 为 \(r_0(z)=0\) 和 \(r_K(z)=Kz^2(z-1)^2(z+1)^2\)。
它们在全部数据上相同，\(z=1/2\) 处却相差 \(9K/64\)。缺少正则性/幅值或分布假设时，
不能把样本最大误差加一个任意半径称为 uniform certificate。这与 ForeReach 的信息限制一致，不是绕过它的机制。

**同一命令的开环接近不等于闭环策略等价。** 两个 plant 完全相同也可能因视觉观测不同而输出不同动作。
标量例子：\(x^+=x+u\)，冻结策略 \(u=\operatorname{sign}(o)\)，同初态 \(x=0\)，
观测分别为 \(+\epsilon\)、\(-\epsilon\)，则 same-command dynamics gap 为零，而下一状态相差 2。
因此必须覆盖 observation、policy feedback 和控制器/时延历史。连续可微/有界增益条件下可以传播反馈误差，
但这正是经典 closed-loop reachability/incremental stability 的范围；真实视觉策略和接触切换不能无证据假定这些条件成立。

**关节轨迹接近不等于任务/接触状态接近。** 相同 q 和夹爪开度可以对应“物体夹住”或“物体滑落”；
关节误差零不约束物体位姿。若任务谓词用物体、接触或抓取状态，证书必须包含它们的可观测估计与误差，
不能用 q 到末端的运动学 Jacobian 替代全部对象状态。

**边际覆盖不能直接用于选择后的部署。** 如果漏覆盖只发生在占总体 1% 的接受区域，
总体覆盖仍为 99%，而接受后的漏覆盖率为 100%。这说明 split-conformal 边际覆盖不自动等于 selective risk。
用同一数据选补偿器/阈值再报告风险还需独立审核或有效的多重/序贯校正；CARE/LTT 已处理相应固定候选选择问题。

此外，rad、米、秒和接触谓词 margin 不能未经映射直接比较。任务权重 \(W\) 及裕度必须使用一致度量；
给关节误差随意乘权重并不提供物体/接触状态误差的可靠上界。

### 9.5 真机成本与证据要求

在独立同分布 Bernoulli 完整回合、固定策略、零次失败的简化条件下，单侧置信上界为
\(p_U=1-\delta^{1/n}\)。要以 95% 置信度证明失败率低于 5%，至少需要 59 个**完整独立回合**，
而不是 59 帧。若对 10 个候选使用简单 Bonferroni 分配，则每个候选对应的零失败需求为 104 回合。
这是采样规模计算，不是本项目真实结果，也不是任何序贯/配对设计的普遍最小样本量。
条件风险/保留率还可能需要更多有效样本；热状态、适配记忆或不完整 reset 会破坏上述 IID 前提。
反例代数及上述样本量的数值核算存于 [executable-spec-logic-audit.json](../../experiments/so101/executable-spec-logic-audit.json)，
明确标记为分析核算，不能记入机器人 rollout/成功率。

| 主张 | 必需证据 | 当前证据 | 缺口/裁决 |
|---|---|---|---|
| D 的接口识别机制有创新 | 超出有限 grammar/等价类/主动探针 | ActionABI/ActionShift 源码直接覆盖宽表述 | **停止当前方法主张** |
| D′ 的任务裕度证书有创新 | 超出 ForeReach/STL/已有风险认证的核心机制 | 当前只提出误差界与 margin 比较 | **停止当前方法主张** |
| 能认证真实 SO-101 闭环任务 | 完整状态/观测误差、适用假设、独立硬件测试 | 72 条无模型仿真 tracking 记录 | **尚无该证据** |
| A100 与 SO-101 可承载研究 | 可用策略、native action、任务、日志 | 场景/动作接口已有；尚无本项目策略成功证据 | 共用工程载体可保留，不能据此立项 D |

### 9.6 本次裁决后的动作

撤回 D / D′ 主推荐，停止为这个表述扩展大模型训练或真机认证矩阵；保留 MuJoCo、日志和动态 tracking 预检作为共用工程工具。
研究领域仍有未解决问题，但重启必须指出**具体不可用的信息条件、现有方法的必要假设为何破坏、一个不同的核心机制**。
“部分可观测”“接触”“在线”“低成本”这些限定词本身不能恢复新颖性；需要重新做最近工作比较。

本次仍未确定可立项主方向。SO-101、A100、同体仿真—真机约束不变，完整研究选题目标继续。
