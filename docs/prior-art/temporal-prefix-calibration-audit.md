# 共享前缀与语义分叉：机制级查新审计

日期：2026-11-14。状态：**新候选的公式级/近邻级审计，尚未立项、尚未查新通过、尚未测得 VLA 失效。**
固定约束：SO-101、A100、同体 MuJoCo—真机；先验证失效机制，再决定是否实现针对性方法。

## 当前判断

这是目前比 DeepSeek 的 RCBT 更清晰的正向候选，但仍不能冻结为论文方向。

候选科学问题是：

> 当两个语言任务在当前状态下具有相同的正确动作前缀、只在之后的目标分支上必须不同，
> 以动作距离为核心的语义校准/分离损失会不会把共享前缀误当成负例，造成过早纠偏；
> 用任务结果和时间分叉支持约束它，是否能减少语义错误而不破坏正确共享动作？

工作描述暂称 **outcome-aligned temporal semantic calibration**，名称不代表新颖性结论。
核心对象是**语义分叉的时间支持**，不是另一个残差补偿器、置信门控或动作 chunk 调度器。

## 1. 数学反例：动作分离要求可能与正确性冲突

设两个任务的正确 action chunk 为

\[
A^A=(1,1,1,-1,-1,0),\qquad
A^B=(1,1,1,+1,+1,0).
\]

前三步是共同的接近/抓取前缀，第四、五步才是左/右目标分支，最后一步是共享释放动作。
若训练对每个时刻都要求语义变化产生至少 \(m=0.5\) 的动作距离，则相同动作时每步得到
\(\max(0,m-\|a^A_t-a^B_t\|)\) 的惩罚，总和为 2.0。
如果使用任务结构给出的 divergence support \(d=(0,0,0,1,1,0)\)，只在必须分叉的时刻要求分离，总和为 0。

该核算记录在 [shared-prefix-separation-audit.json](../../experiments/so101/shared-prefix-separation-audit.json)。
它是目标函数几何反例，不是 BAS-VLA 训练错误、不是策略成功率，也不是新方法结果。
若两个任务从一开始就要求不同动作，或任务正确动作集合本来不允许共享前缀，该反例不适用。

还有一个更基本的限制：不同正确动作模式可能都成功。相对一条示范动作求均值再补偿会把多模态行为推向失败，
见 [RCBT 参考动作反例](../../experiments/so101/rcbt-reference-counterexample.json)。

## 2. 近期近邻与边界

| 来源 | 已经覆盖 | 本候选必须避开的表述 |
|---|---|---|
| [BAS-VLA，2609.23650v1 §4.1–4.3、C.2](https://arxiv.org/html/2609.23650v1) | frozen VLA 上 clean/control/break triplet、动作 residual、semantic separation margin、选择性 preserving gate；附录给出 margin implication | 不能声称“首次做语义动作校准/保持—破坏分离”；候选要检验其逐时刻分离是否误伤共享前缀，并以结果/时间支持作不同对象 |
| [One Word, Different Action，2609.05260v1](https://arxiv.org/html/2609.05260v1) | 真实机器人 Decision Invariance / Decision Sensitivity；物理决策状态下任务保持和任务改变指令对 | 不能声称首次研究语言变化导致动作保持/改变；它是基准/诊断，候选的窄差异是时间分叉支持和训练损失机制 |
| [Stage-Aware VLA](https://icloud.eurekamag.com/research/112/001/112001979.php) | 长任务中多个有效子任务顺序造成 one-to-many supervision，显式 progress state 消歧 | 不能把“加阶段状态解决一对多”当新点；需要比较其阶段条件与分叉支持是否解决同一误伤 |
| [RT-H，2403.01823v1](https://arxiv.org/html/2403.01823v1) | 用 language motion 作为高层任务与低层动作之间的共享结构，支持人类语言干预 | 不能把共享低层动作/层级语言表示当新点；RT-H 未直接等同本候选的 triplet 分叉损失，但必须列强基线 |
| [Acting While Understanding，2606.15285v1](https://arxiv.org/html/2606.15285v1) | stale semantic cache、历史动作条件、时间错位训练；真实 SO100 | 不能把“时间错位会伤害动作”当新点；其问题是异步推理刷新，候选关注语义对照的监督支持 |
| [PHASER，2606.03598v1](https://arxiv.org/html/2606.03598v1) | phase boundary、阶段中心经验回放、自动动作信号+VLM分段 | 不能把阶段分段或 phase-aware replay 直接包装为新机制；可作 phase-label/分叉时刻强基线 |
| [Hide-and-Seek，2605.30834v1](https://arxiv.org/abs/2605.30834) | 轨迹级标签下用 inter/intra trajectory contrastive loss 定位 failure onset，无逐步标签 | 不能把“从粗标签定位时间窗口”当首次；可借其 onset 评估，但本候选需证明语义共享前缀的正例约束不同 |
| [Generative Failure-to-Success Bridging](https://junhahyung.github.io/FailureToSuccess/) | 失败 prefix 与成功 suffix 的语义阶段对齐、恢复窗口选择 | 不能把 prefix/suffix 对齐术语当新点；该线是恢复数据生成，不是 semantic calibration loss |

目前未发现上述来源已经明确提出“任务语义分叉时刻支持的动作分离/保持损失”，但这只是本轮定向检索结论，
不是机构查新或穷尽证明。

## 3. 候选核心机制（只有在失效复现后才可设计）

对成对任务 \(x^A,x^B\) 和时刻 \(t\)，不要固定要求全程分离，而定义三类支持：

1. **shared support**：在当前状态和动作窗口内，两个任务有共同的任务可行动作集合；要求保持等价或允许小距离。
2. **branch support**：从该时刻起，若任务目标不同，动作/结果必须出现可验证差异。
3. **irrelevant support**：动作差异不影响当前任务谓词，不能作为语义校准的主要监督。

令 \(d_t\in\{0,1,?\}\) 是由任务结构、状态转移或独立可行性检查得到的支持标签；问号表示信息不足，
不能强制保持或分离。候选损失的概念形式为

\[
L_{\rm div}=\sum_t d_t\,[m-\|a^A_t-a^B_t\|]_+,
\qquad
L_{\rm inv}=\sum_t(1-d_t)\,w_t\|a^A_t-a^B_t\|^2,
\]

但这两个式子本身不是创新。真正需要证明的是：

- \(d_t\) 能在部署信息下获得或安全拒绝，不能读取不可用的 oracle 任务真值；
- 支持标签与最终任务结果相关，而非只由动作差异反推；
- 只在必须分叉的时刻施加分离，相比 BAS-VLA 的全时刻/统一 margin，能减少错误纠偏；
- 在 no-common-prefix、shared-prefix、multi-valid-action 三类任务上都不产生新的错误。

如果最终只是给每个时刻乘一个人工 mask，方法贡献不足；需要从可观测状态和任务约束推导其适用条件，
或者把它限定为一项经过验证的失效分析/数据标注协议，而非新算法。

## 4. 最小否证实验

### 4.1 仿真任务族

先用 SO-101 同一 body、同一相机和同一 6 通道弧度动作接口构造三个族：

- **Shared-prefix**：抓取同一物体后分别放到左/右目标；接近、抓取和抬升前缀相同，放置方向才分叉。
- **No-common-prefix**：两个目标在相反方向，初始接近动作也必须不同。
- **Multi-valid**：同一目标允许左绕/右绕或不同合法接近方向；用于检验单一参考动作造成的伪负例。

场景任务谓词必须独立记录物体终点、稳定性和目标关系；动作距离只作中介指标。
若没有可完成的冻结策略，先用脚本/教师轨迹验证标签和分叉时刻，但不把教师轨迹算作 VLA 结果。

### 4.2 评价对象和强基线

固定任务对、初始状态、语言改动、推理预算和 action chunk 协议；按 episode 而非帧做统计。

| 组 | 方法 | 目的 |
|---|---|---|
| 0 | frozen/普通 BC | 基础能力和自然共享前缀 |
| 1 | BAS-VLA uniform triplet separation | 最近强基线 |
| 2 | action-only phase mask | 判断收益是否只是手工 mask |
| 3 | Stage-Aware/progress-conditioned | 排除显式阶段状态已足够 |
| 4 | RT-H/共享 primitive（可复现时） | 排除层级语言共享结构 |
| 5 | oracle divergence support | 只作上界，不能当部署方法 |
| 6 | 候选机制 | 只有在 1–5 已测后实现 |

主终点：新任务成功率、旧任务错误保持率、共享前缀动作误差、分叉后动作/结果敏感性、错误纠偏率、延迟和额外推理。
必须报告 action distance 与 outcome success 的相关性；若动作分离变大但结果没有改善，不能算成功。

### 4.3 关键否证条件

- shared-prefix 上 uniform triplet 不出现可重复的前缀损失，或者候选机制不改善结果：停止。
- action-only mask 与候选机制同等有效：停止新机制主张。
- Stage-Aware 或 RT-H 已完全解决且无额外监督成本：转为评测/失效分析，不命名新方法。
- 候选机制提升只来自更长推理、更短 chunk 或更多数据：按匹配预算否决。
- 任务成功率变化无法与语言理解、视觉错误和低层执行分离：结论限于不可辨识，不宣称修正有效。

## 5. 仿真—真机一致性

真机只验证同一个支持标签与错误纠偏命题：

1. 选一对 shared-prefix 任务和一对 no-common-prefix 任务；保持 SO-101、相机、低层控制周期和动作单位一致。
2. 仿真和真机使用同一任务谓词、同一语言对、同一“分叉前/分叉后”记录字段。
3. 真机先测冻结/BAS-VLA 或可运行的最强基线，再测候选；不把一段成功视频当支持证据。
4. 记录完整 chunk、分叉时刻、实际关节、物体终点、停止/重规划原因和真实成本。

若真机没有可运行的 VLA/适配器，先报告载体未就绪；不要用教师控制器结果替代 VLA 语义校准结果。

## 6. 当前裁决

**候选 TPSC（暂称）比 RCBT 更接近一个单一机制，但仍未通过查新。**
它有明确的数学反例和可执行的 SO-101 任务族；同时被 BAS-VLA、One Word、Stage-Aware、RT-H、PHASER、Hide-and-Seek 等近邻强约束。
下一步应先做小规模、只测失效机制的仿真预检；不先训练大模型、不先采购新传感器、不把“共享前缀”写成论文贡献。

