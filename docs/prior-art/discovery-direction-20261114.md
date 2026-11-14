# 研究方向发现：风险来源可辨识与干预选择

日期：2026-11-14。本文是第二轮候选发现，不是机构科技查新报告，也不是已证明的新方法。
固定约束：低成本 SO-101、A100、同体仿真—真机；研究问题可以更换。
《思考，快与慢》的“快判断/慢验证”与工业精度补偿只作问题启发，不把心理学名称或平台当成贡献。

## 先淘汰的三类新候选

| 表面想法 | 已核到的直接工作 | 结论 |
|---|---|---|
| 用温度、电流、电压修正动作 | TeAR（2609.36182v1）已提出遥测条件动作整流，并在 SO-ARM101 做物理评估；后续问题是跨机器人 telemetry response，不是空白 | **宽题淘汰** |
| 错误记忆/旧结论撤回 | REMM（2610.12710v1）已用证据链接、依赖撤回和恢复队列；其限制是固定谓词本体和任务编译器，不等于我们可以再做同样的 memory layer | **宽题淘汰** |
| 慢思考、多采样、动作置信度门控 | CoVer（2602.12281v1）、Pre-VLA（2605.22446v1）、DiVeR（2610.04933v1）、GeoAAC（2609.20776v1）分别覆盖候选采样/验证、预执行 critic 验证、决策关键状态和自适应 action horizon | **宽题淘汰** |

这些淘汰不表示具体方法逐行相同；它们说明只改平台、增加一个 verifier、加一个 residual 或把 System 1/System 2 改名，不能通过核心创新门槛。

## 正向机会卡：来源分解的风险校准

### 研究问题

在同一个 SO-101 任务和相同的失败表象下，失败风险可能来自两种性质不同的来源：

1. **策略/语义风险**：候选动作本身分歧大，目标绑定或场景解释不稳定；需要重采样、改写指令、额外验证或请求协助。
2. **执行/具身风险**：策略候选相对一致，但命令没有按预期实现；需要缩短 action chunk、调整执行映射、降低速度或暂停，而不是继续采样同一策略。

当前近邻大多把风险压成一个分数，或只针对其中一个来源。SO-101 的 failure/recovery benchmark 已把失败划分为 semantic-level 和 execution-level，并报告恢复率很低；但它主要是评测协议，尚未给出在固定在线预算下识别来源并选择不同干预的统一机制。

可检验的中心命题是：

> 在固定观测和固定额外计算/动作预算下，来源条件化的风险估计能否区分“重新采样有价值”和“重新采样无价值、应改执行”的两类状态，并在未见 SO-101 布局上提高风险—覆盖权衡或恢复率？

这不是把两个模块并排接上。要成为方法，必须证明：

- 单一风险分数在构造的同表象反例中不能决定正确干预；
- 两个风险坐标对应不同的受控干预结果，而不是相关性命名；
- 来源条件化决策在同样的候选数、推理时间、动作步数和真实失败标签下，超过 CoVer/Pre-VLA/VFD/TeAR 单独方案及标量融合；
- 结论在仿真与真机使用同一任务谓词、同一干预语义时保持方向。

暂不命名新算法。可用工作称呼“source-aware risk calibration”，在通过红队前不能写成论文贡献。

### 最接近工作与精确差异

| 工作 | 已经做了什么 | 仍未覆盖、但必须核实的差异 |
|---|---|---|
| [SO-101 failure/recovery benchmark](https://arxiv.org/html/2606.08881v2) | 在真实 SO-101 上评估多种策略，定义细粒度失败、semantic/execution 两层和 recovery rate；局限明确写出单平台、桌面任务和未来跨平台/更复杂任务 | 它是诊断性评测，不是固定干预预算下的来源后验和动作选择；不能把重新实现 taxonomy 当方法 |
| [VFD/UQ-VLA](https://arxiv.org/html/2606.18043v1)；[官方代码](https://github.com/learnsyslab/uq_vla) | 用 flow velocity-field disagreement 估计 epistemic uncertainty，做失败检测和主动示教；代码 Apache-2.0，仿真代码公开，真实机器人实验代码/权重不公开 | 主要是策略不确定性；论文明确把初始观测 uncertainty 当任务难度 proxy，未建执行映射残差来源，也未按来源选择整流/重采样 |
| [Post-hoc Epistemic Uncertainty](https://arxiv.org/html/2610.29730v1) | 单策略 embedding 上拟合 kernel-variance head，不改策略，可用于示教获取/转交强监督者 | 只验证 SmolVLA、LIBERO-10 仿真；论文限制写明未测真实机器人、未证明执行前预警、未处理 intervention cost；不做执行源分解 |
| [CoVer](https://arxiv.org/html/2602.12281v1) | 重述指令、重复采样动作、contrastive verifier 选候选；在 SIMPLER 与真实实验验证 test-time scaling | 选择的是候选质量，不判断候选一致但执行失败的来源；增加采样不能解决相同错误映射 |
| [Pre-VLA](https://arxiv.org/html/2605.22446v1) | 用 critic advantage/safety confidence 预验证 action chunk，低质量时重采样；论文局限承认 critic 在分布移位下可能有偏、反复重采样产生开销 | verifier 的信号来自 critic，不是命令—实际状态的执行映射；其 future work 正是 online self-calibrating boundary，不能直接声称我们填补了全部空白 |
| [TeAR](https://arxiv.org/html/2609.36182v1) | 冻结策略、使用温度/电流/电压等 telemetry 做动作整流，并做 SO-ARM101 物理实验 | 主要处理执行条件；没有策略候选语义风险后验，也没有在两类来源之间选择“采样/整流/暂停”的统一决策 |
| [Phys2Real](https://arxiv.org/html/2510.11689v2)；[代码](https://github.com/phys2real/phys2real) | 用 VLM 物理参数先验、在线交互估计和逆方差融合做 real-to-sim-to-real；真实实验是 T-block/锤子 planar pushing | 已覆盖“仿真物理不确定性+在线估计+不确定性融合”，但不是 VLA 候选动作风险与执行偏差的同一决策；若我们的方案只换任务/机械臂则淘汰 |
| [Stability-aware residual RL](https://arxiv.org/html/2609.21307v1) | DOB+残差RL、干扰状态估计及 ISS 状态相关动作界，含真实机械臂 | 已覆盖有界残差补偿与稳定性；不能把“给VLA加residual”作为独立创新，候选A必须是风险来源辨识/干预选择且不能依赖其 privileged disturbance context |
| [DiVeR](https://arxiv.org/html/2610.04933v1) | 用动作表示离散度估计 decision criticality，重加权 verifier 学习 | 关键性不等于风险来源；没有物理执行反馈和同失败表象的因果来源实验 |
| [GeoAAC](https://arxiv.org/html/2609.20776v1) | 依据 flow denoising trajectory geometry 自适应 action horizon | 已覆盖“可靠性→chunk长度”；不能把缩短 chunk 本身作为新方法 |

上述差异仍是**待查新差异**。不能从“分别没有某个关键词”推断新颖性；必须继续查引用链、后续版本、代码和经典 fault diagnosis/control。

### 核心机制的最小形式

令当前可观测历史为 (h_t=(o_{leq t},q_{leq t},a_{leq t},ell))，候选动作集为 (A_t)。计算两个来源量：

```text
u_policy(h_t, A_t)   # 候选动作/策略内部的不一致
u_exec(h_t)           # 命令与已实现状态、或 twin 预测与已实现状态的偏差
```

核心不是把两个数相加，而是学习/校准

```text
P(z_t = policy | h_t), P(z_t = execution | h_t), P(z_t = both | h_t)
```

并把 (z_t) 连接到**不同可观测干预的结果**：

```text
policy-risk      -> candidate resampling / language verification
execution-risk   -> shorter horizon / bounded rectification / pause
both             -> stop or human/teacher referral
```

需要用 matched interventions 验证来源，而不是用最终失败标签事后解释。仿真可以提供隐藏扰动真值做诊断上界；部署决策不能读取扰动真值。

### 最强简单对照

1. Frozen policy，固定 chunk 和不干预。
2. 标量候选 verifier：CoVer/Pre-VLA 风格，全部失败都重采样。
3. VFD 或 post-hoc kernel uncertainty 单一风险分数，只做阈值暂停。
4. TeAR 风格执行整流或传统 q-command residual，只有执行对照。
5. 固定计算预算下的随机候选/随机缩短 chunk/固定整流；确保“多算力”不是方法收益。
6. Oracle source label 只作上界；不能放入可部署方法。
7. 同样候选数和 wall-clock 的简单两维 logistic/树模型，防止复杂网络只是容量增益。

### 决定性否证实验

先不训练大模型，使用冻结的 SO-101 兼容策略和可控 wrapper，在相同初态构造成对条件：

- policy ambiguity：视觉/语言目标改变使合法候选动作分歧增大，但执行映射保持正常；
- execution mismatch：候选动作分歧保持低，加入关节增益、延迟、速度上限或接触执行映射改变；
- matched nuisance：两种条件调到相近的单一成功率和相近 scalar confidence，使单一门控无法靠阈值分开。

预注册主要终点为固定额外预算下的恢复成功率、风险—覆盖曲线和误干预率；同时报告 source confusion matrix、候选数、chunk步数、暂停时间、整流幅度、真实 reset 和推理成本。

如果两类条件不能在 RGB/q/命令历史下被识别，或 scalar verifier/固定缩短 chunk 已达到同样结果，立即淘汰该候选。若仿真能识别而真机不能，结论是观测不可辨识，不是算法成功。

### SO-101 同体实验设计

仿真与真机共享同一任务谓词，例如 SO-101 Bench 的 next-to/between/directional move 中选一个可由当前 MuJoCo 场景复现的任务；不直接依赖 Isaac Sim。

1. 先确认一个 SmolVLA/兼容策略在自由和轻接触任务上可完成；A100 只用于策略推理、候选采样和小型风险头训练。
2. 仿真以同一 matched layout 执行三类条件，记录 RGB、q、命令、实际 q、action chunk 和 episode 终点。
3. 真机不注入隐藏标签；使用已校准的控制周期、可见遮挡/目标布局和软件 action mapping 改变，记录同一字段。
4. 真机先验证执行风险坐标的可重复性，再验证来源条件决策；若 SO-101 无温度/电流接口，主方案只使用 q/RGB/命令，TeAR 仅作有遥测的附加对照。
5. 论文中心图应展示同一失败率下，scalar verifier 的干预方向错误，而 source-aware decision 在固定预算下减少错误干预；若数据不支持该图，不继续包装。

### A100、代码和可行性

- A100 足够支撑 SmolVLA/轻量VLA候选采样、两维风险头和仿真并行；不需要从头训练7B基础模型。
- 官方 [UQ-VLA](https://github.com/learnsyslab/uq_vla) 固定主分支 `bcc2433d2549afee27bf5d0a73ae528375bca686`，Apache-2.0；README明确真实机器人实验代码不在仓库、不提供checkpoint，仿真依赖LIBERO资产约6.4GB，不能把它直接当SO-101运行基线。
- 官方 [SO-101 Bench](https://github.com/5hadytru/so101_bench) 固定主分支 `470e09e2b66658049e1248378f20ce39bd134ad6`，Apache-2.0；需要 Isaac Sim 5.1/Isaac Lab 0.54/Python 3.11和约2GB USD资产，不应与本项目MuJoCo环境混装。它可提供任务、失败分类和现实对照思想，本项目保留MuJoCo以满足同体路线。
- [vla-uncertainty-probe](https://github.com/Giulia-Avanzato/vla-uncertainty-probe) 的公开仓库描述了一个重要可证伪线索：denoising dispersion能反映任务歧义，却可能不能反映输入有效性；仓库没有可核验的开放许可证，不能直接作为论文依赖或成果来源。
- 当前最大可行性风险不是A100，而是需要一个真正能在SO-101仿真和真机完成任务的策略、可靠的q/命令时间同步和足够的执行失败样本。没有这些不能用失败日志训练风险来源。

## 机会判断与红队门槛

### 当前排名

1. **候选 D（首要深审）**：动态 executable-policy specification 与同体等价证书，见下一节；与工业精度补偿自然相连，但仍需排除经典系统辨识和近邻拼接。
2. **候选 B（备选）**：SO-101失败/恢复评测的可复现MuJoCo扩展。可形成开源资产和数据，但benchmark本身不是核心机制，除非找到新的可验证评价对象；不作为论文方法首选。
3. **候选 A（降级）**：来源可辨识风险校准，已被 PATCH/CommitFlow/ReTrace 等直接近邻显著压缩，不再作为主推荐。
4. **候选 C（停止）**：记忆撤回、热补偿、慢推理、普通动作不确定性，均已有直接工作。

### 在主推荐前必须完成的三项检查

1. 逐式核查 Same Weights 的 static certificate、FAN、TeAR、PolicyIK、经典系统辨识/鲁棒控制，确认候选 D 的动态证书不是现成方法的改名。
2. 检查近两年 VLA 论文和 GitHub 是否已有 dynamic executable-equivalence certificate 或同一 checkpoint 的 action-chunk/controller mismatch 证书；若有，候选 D 立即淘汰或改成其未覆盖的精确条件。
3. 在 MuJoCo 先做不依赖大模型的 command-to-achieved dynamic mapping 反例；若静态 metadata、固定短chunk或普通线性补偿已经给出同等证书/收益，候选 D 不得立项。

特别要核对 Phys2Real 和稳定残差控制：它们使“物理参数不确定性融合”和“有界执行补偿”不能再被当作候选 D 的独立贡献。

### 暂定决定

候选 D 是目前最值得继续投入 1 个查新—否证周期的方向，**不是“查新通过”**。它比原 ECCBF 更贴近工业精度补偿与 SO-101 的真实部署障碍，中心证据是动态可执行等价证书和同体验证；但只要核心增量退化为 Same Weights+FAN+TeAR+PolicyIK 的模块拼接，就必须换题。

## 候选 D：动态可执行策略规范与同体等价证书（待深审）

### 中心问题

同一个 checkpoint、提示和场景，在仿真与真实 SO-101 上可能因反归一化、关节零点/单位、控制频率、action chunk 保留、延迟、限幅和机械跟踪而产生不同物理策略。研究目标是估计这种动态执行映射差异，给出 rollout 前可检查的偏差/风险证书，并在证书超界时执行受限补偿或拒绝部署。

它不是重新做坐标标定：论文的核心对象是**可执行策略的等价性**，主终点是证书对真实任务风险的预测覆盖和拒绝/补偿决策，而非单次成功率。

### 近邻边界

- [Same Weights, Different Robot](https://arxiv.org/html/2606.03724v1) 已给 quantile normalization metadata mismatch 的闭式 ExecSpec certificate，但正文把控制频率、action-chunk执行、controller convention、接触和硬件交互列为超出当前实验范围；其结果基于 LIBERO replay，不是 SO-101动态真机。
- [FAN](https://arxiv.org/html/2609.21358v1) 研究 continual learning 中固定动作坐标统计量，不给 dynamic command-to-achieved certificate。
- [TeAR](https://arxiv.org/html/2609.36182v1) 做 telemetry-conditioned rectification，并有 SO-ARM101实验；它是整流方法，不是 rollout 前等价证书，且主信号含 telemetry/OSC 设置。
- [PolicyIK](https://arxiv.org/html/2611.05372v1) 做高精度 IK/反馈补偿；它解决末端到关节控制，不审计上游 VLA 的 action metadata、chunk timing 与 sim-real executable semantics。
- [SO-101 Bench](https://arxiv.org/html/2610.36420v1) 证明仿真可保持策略排名但高估成功率；没有 certificate 或补偿机制。

### 最小可证伪实验

冻结一个能完成短任务的 SO-101 兼容策略，执行自由空间 reach、目标附近 approach 和轻接触 push 三类校准动作。记录归一化命令、q command/q achieved、RGB、时间戳、控制频率、chunk 保留步数、限幅事件；仿真和真机使用相同初始几何和任务谓词。

令 (G_s) 和 (G_r) 分别为仿真和真实控制链，在安全低幅度轨迹上估计 \hat G_r，并给出

```text
e_exec = q_real[t:t+H] − q_sim[t:t+H; same command, same initial state]
certificate = bound(e_exec, delay, gain, clip, measurement noise)
```

对照必须包括：原始冻结策略、静态 metadata/零点检查、固定短 chunk、经典线性系统辨识或 DOB、受限补偿和拒绝部署。TeAR/PolicyIK只在信息和接口匹配时作为附加对照；oracle 映射只作上界。

候选 D 在以下任一情况立即淘汰：静态 ExecSpec 已预测全部风险；固定短 chunk/零点校准/经典 DOB 同样有效；证书在未见布局失效；真机差异主要来自策略不会做而非执行接口；或动态证书只是把已有系统辨识输出换一个名字。

### 可行性

- 证书和低阶映射估计不需要大规模训练；A100用于冻结VLA推理、并行MuJoCo和少量校准头，主要难点是可复现的SO-101命令—状态同步。
- 没有温度/电流接口时，主实验只使用RGB、q、命令和时间戳，不假装复现TeAR的telemetry条件；仿真中的gain/delay/clip注入只称执行映射改变。
- [PolicyIK代码](https://github.com/Tinaliu0123/PolicyIK) 固定 `22f3a5cddc674e88995cae18b93cd5a5cb3ddb86`，GitHub报告Apache-2.0，可作IK/反馈对照；不把它作为新方法依赖。
- Same Weights 未发现官方代码；其动态边界需自行实现并与原静态证书公平对比。

### 当前状态

**继续一轮公式级查新和无模型仿真否证；暂不写方法名、暂不采购新传感器、暂不启动大规模训练。** 若 D 通过经典系统辨识/控制和最近VLA action-interface红队，再形成设计文档；否则继续换题。
