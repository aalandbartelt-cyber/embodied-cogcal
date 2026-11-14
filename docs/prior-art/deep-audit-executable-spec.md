# 候选 D 深审：动态可执行策略规范与同体等价证书

日期：2026-11-14。状态：定向查新/红队，不是正式机构查新，不是本项目结果。
约束：低成本 SO-101、A100、同体 MuJoCo—真机；冻结或轻量适配 VLA；不预设新增力觉/温度/电流传感器。

## 结论

**候选 D 目前是最值得继续一轮验证的方向，但尚未通过查新。** 它有一条清晰的技术边界：
从已有的静态 action-metadata mismatch certificate，推进到包含 action chunk、控制频率/保持、时延、限幅和关节跟踪的**组合式动态 executable-equivalence certificate**，并用证书决定受限补偿或拒绝部署。

这不是把 `Same Weights`、FAN、TeAR、PolicyIK、RTC/RACE/PACT 拼接成流程。若最终实现只是这些组件并列，或传统系统辨识/鲁棒控制已经给出同样的组合证书与风险预测，候选 D 应淘汰。当前报告只证明存在一个原论文明确留下的边界和可否证问题，不证明边界无人解决。

## 1. 直接最近工作：Same Weights 的精确范围

[Same Weights, Different Robot: A Deployment Safety View of VLA Policies，2606.03724v1](https://arxiv.org/html/2606.03724v1) 把可执行 VLA 写成

\[
(f_\theta,\mathcal I,\mathcal Z,\mathcal U_k,\mathcal C),
\]

其中 \(\mathcal U_k\) 是 metadata 选择的 action unnormalizer，\(\mathcal C\) 是控制器语义。论文对 quantile unnormalizer 定义

\[
\mathcal U_k(z)_i=q_{01,i}^{(k)}+z_i(q_{99,i}^{(k)}-q_{01,i}^{(k)}),
\]

并证明相同 mask 下替换 metadata 的单维位移为

\[
\Delta_i(z;k_c,k_w)=q_{01,i}^{(w)}-q_{01,i}^{(c)},
\]

再用校准动作集定义均值/尾部 drift certificate。该证书不需要模型推理或 rollout，且论文的 LIBERO replay witness 显示静态 metadata 错配可以翻转成功率。

这篇论文同时明确限定了结论：阈值是 reporting scale，不是普适安全裕度；certificate 不是完美预测器；实验只在 LIBERO replay，不能替代真实硬件。它的未来工作明确列出 task-specific margins、contact-sensitive safety metrics、hardware-specific action units，以及 image preprocessing、camera orientation、gripper convention、control frequency 和 action chunk execution 等 normalization 之外的 executable semantics。

因此我们不能声称“发现 checkpoint 之外还有接口”或“第一次做 certificate”。可继续的问题必须严格落在**动态执行链的可验证证书与同体物理结果**。

## 2. 近邻逐项排除

| 工作 | 已覆盖 | 候选 D 不能重复的部分 |
|---|---|---|
| [FAN](https://arxiv.org/html/2609.21358v1) | 任务流中的 action normalization consistency/coverage/causality，固定统计量减少坐标漂移 | 它不是仿真—真机 command-to-achieved 动态映射，也不给接触/时延/限幅证书 |
| [TeAR](https://arxiv.org/html/2609.36182v1) | 冻结策略+telemetry 条件动作整流；SO-ARM101物理评估 | 它是 test-time rectifier，主要用 OSC/温度电流电压；不提供 rollout 前 executable equivalence certificate |
| [PolicyIK](https://arxiv.org/html/2611.05372v1)；[代码](https://github.com/Tinaliu0123/PolicyIK) | q/pose feedback、误差相关增益、高精度 IK/holding，仿真和真实机械臂 | 上游 VLA action metadata、chunk timing、控制器约定和 sim-real policy identity 不在其问题内 |
| [RTC](https://arxiv.org/abs/2506.07339)、[RACE](https://arxiv.org/abs/2610.05719)、[PACT-VLA](https://arxiv.org/abs/2610.28019) | 处理异步推理、长chunk transition timing、pre-commit observation 的候选选择 | 它们改变运行时 chunk 执行/选择；不等于组合静态+动态物理语义证书，候选 D必须把它们作为强基线 |
| [SO-101 Bench](https://arxiv.org/html/2610.36420v1)；[代码](https://github.com/5hadytru/so101_bench) | 数字孪生、真实策略排序保持、仿真成功率偏乐观 | 相关性/排名不是逐 action 执行等价；无证书指导拒绝/补偿 |
| [TeAR 的执行退化模型] | state/history-dependent friction/backlash/compliance/gravity-like execution error | 候选 D不能重新提出“执行误差存在”或“残差可补偿”；必须提供可预部署的接口风险证书 |
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

新意若成立，应来自**可检验的组合等价性对象和证书—任务 margin 映射**，而不是“先校准再验证”的流程。

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

## 7. 深审结论

候选 D 的最强依据是最近论文自己公开的边界：static normalization certificate 不能覆盖 dynamic controller/chunk/contact/hardware。最强反对意见是：工业系统辨识、DOB、TeAR、PolicyIK、RTC/RACE/PACT 和已有 deployment manifests 可能已足够解决。下一阶段必须先做经典 baseline 和无模型反例，再决定是否值得写设计文档；在此之前不命名算法、不采购传感器、不宣称新颖性。

## 8. 本仓库的无模型可行性预检

在现有 MuJoCo 场景上运行了只读的六关节 position-target 预检，共 6 个关节 × 2 个方向 × 6 个执行窗 = 72 条记录。命令增量为 ±0.08 rad，执行窗为 1、5、10、25、50、100 个仿真步；结果写入 [dynamic-interface-precheck.json](../../experiments/so101/dynamic-interface-precheck.json)。

观察到：1步窗的最大绝对跟踪误差为 0.079734 rad，25步窗的平均绝对误差为 0.011424 rad，100步窗的最大绝对误差为 0.000829 rad。该结果只证明当前仿真接口中“命令时刻—实际 q—窗口长度”是可记录且早期存在非零动态误差；它不是硬件传递函数、不是 sim-real 差异、不是VLA成功率，也不证明候选 D 的证书有效。它给出了一个无需大模型即可否证 D 的最小起点。
