# ECCBF 实验有效性与可证伪检查

日期：2026-11-13。**A100 尚未部署；本文是实验约束与待冻结清单，不是实证结果，也不表示全部字段已冻结。** 保留 semantic × execution 交互与同 SO-101 仿真—真机路线。文献事实见 [原始来源核验](prior-art/verified-sources.md)，其结论是 novelty 尚未通过。

2026-11-14 补核：当前候选暂停扩大正式矩阵，执行 [换方案门槛](prior-art/ROUTE_DECISION.md)。
当前 task_id 与实际任务覆盖的差异已实测，见 [协议审计](../experiments/so101/PROTOCOL_AUDIT.md)。
本文的两项校准任务/held-out 要求仍是待满足条件，现有两个 task_id 并未满足。

审计轴：control / baseline、ablation、statistical、real-world、reproducibility / overclaimed-results、unfair-comparison / planning 与 audit。

## 1. 隐藏物理变化不能改变相同输入的首步预测

```text
a_t = πθ(RGB_t, q_t, language, history_t; inference_rng_t)
z_(t+1) = F_E(z_t, applied_action_t, environment_rng_t)
```

E 若只改变策略不可见的动力学（摩擦、阻尼、负载），同一确定性 VLA 在**完全相同 RGB、关节/状态输入、语言、历史/缓存与推理配置**下，第一步 raw prediction 必须相同：对每个 S，`a_S0(first)=a_S1(first)`，因此 `b_exec(first)=b_int(first)=0`。chunk 模型相同输入下的整块预测也相同；执行并接收不同反馈后才可能改变下一块。随机策略需固定推理随机数或比较条件分布，不能把采样噪声当交互。

只有 E 已影响观测、状态、历史，或明确作为策略额外输入时，预测才可能随 E 改变。执行器变换/队列/限幅使 applied action 不同，也不等于 raw VLA prediction 不同。

**A100 第一个负对照是相同输入重放**：仅改隐藏物理参数，不执行动作，预测应相同。若非零，先查 RGB/预处理 hash、reset、缓存、RNG、模型模式或条件泄漏，不得解释为认知发现。

| E 类型 | 例子 | 解释边界 |
|---|---|---|
| 隐藏动力学 | 摩擦、阻尼、质量 | 首步预测不变；后续反馈/结果可变 |
| 可见状态 | 初始关节或物体姿态 | 输入和执行状态同时变化，不能声称全部输入匹配 |
| 观测/几何映射 | 相机外参、图像变换 | 观测变化，不能统称纯物理执行变化 |
| 时序/控制 | 观测延迟、命令延迟、重规划周期 | 反馈年龄/控制发生变化，需时间戳与匹配延迟对照 |

先冻结一种主 E 的注入位置与强度，其余作为外部条件验证；不把混合扰动平均称为统一具身机制。

## 2. 四格差分识别什么

对预定 episode 或对齐窗口统计量 Y：

```text
I_Y = E[Y|S=1,E=1] - E[Y|S=1,E=0]
      - E[Y|S=0,E=1] + E[Y|S=0,E=0]
```

这是标准 2×2 因子交互。**raw difference-of-differences 是行为对比；公式本身不是新方法，也不自动识别认知因果或人类式认知偏差。** 正确随机化、重置与测量可支持指定闭环系统的干预总效应交互，但它包含物理反馈、状态分布、低层控制与非线性限幅。

必须分开记录/解释：raw VLA prediction；校准/坐标映射/限幅后的 command；实测关节或末端运动与任务结果。首步、反馈后固定窗口、完整 episode SR 是不同估计对象，不可混用。不能平均长短不等轨迹后直接解释四格动作差，也不能把所有时间点当独立样本。

至少保存 initial state hash、RGB/preprocessed input hash、关节输入、policy/history reset、对象姿态、simulation/control dt、chunk/queue index、观测与执行时间戳、观测年龄、真实推理延迟、gate 触发、饱和/碰撞/安全停止。主分析使用固定控制时刻或预定物理时间窗；事件阶段对齐须预定规则并报告未到达阶段者。

状态匹配或 observation replay 可诊断状态分布解释，但状态若是 E 的中介，匹配后的直接效应不是原闭环总效应。不得只选择到达某状态的成功轨迹；无共同状态支持时报告不可比。若交互只在 clip 后、只因不同延迟或轨迹错位出现，解释为对应系统效应，不能归为 VLA 内部认知机制。

## 3. 合法目标变化不自动等于 bias

主终点是**当前可执行指令的任务成功率**。每个 S/E 格必须预定对象、目标区域/关系、容差、持续时间、时限、终止谓词，并用专家/脚本或人工验证可行性。E 不应直接把目标变成无解；模型失败不等于任务无解。

保存 `new_goal_success`、`old_goal_success` 与 `other/timeout`。若新旧目标可同时成立，先记录两个独立布尔谓词，再按预定规则生成互斥 outcome。触碰正确对象、停止旧行为与完成新目标是不同指标。

[ICBench §4.1](https://arxiv.org/html/2603.06001v2) 包含无解矛盾，其旧目标 SR 降低可以表示改善，不能作为需提高完成率的主任务；如保留，单列正确拒绝/不执行与错误执行率。主任务可参考 [LIBERO-CF](https://arxiv.org/html/2602.17659v3) 的可行替代目标思路，但本项目目标必须另行核验。

S 若改变目标，`a10−a00` 包含合理的任务切换，**不能自动命名为 bias，更不能直接减掉它当正确校准**。neutral 动作不是所有语义条件的真值。若报告动作误差，需相对各 S 自己的合法参考 `a*_(S,E,t)`：

```text
r_(S,E,t) = a_(S,E,t) - a*_(S,E,t)
```

参考需说明状态、时序、动作坐标和来源；无唯一正确动作时报告目标相对几何误差和任务谓词，不杜撰动作真值。离线特权参考可作训练/诊断，部署时不能访问。

`factorial_effects` / `FactorialCalibrator.from_factorial` 仅证明能计算/减去给定对比；合成测试通过不证明“减掉 raw action contrast”有益。真实拟合数据须标明是 action contrast 还是 target-relative error，校准符号和参考只在训练/开发集核对后冻结。

## 4. 两项校准任务与完整 held-out

最低切分：两项校准任务 `T_c1,T_c2`，至少一项完整未见任务 `T_h`。这些占位名不表示实际 task ID 已冻结。`T_h` 的 episode、失败录像、参考、残差、归一化、阈值/幅度选择均不得进入训练或调参。看过测试后改方法，应将其降为开发集并另建测试集。

同一任务换 scene/seed/实例/语言改写，不自动算 held-out task；须明确任务身份定义。开发集内部按 trajectory/scene reset group 切分，不允许相同轨迹帧跨集合。各方法调参信息与预算匹配。

冻结 `semantic_score` / `execution_score` 的来源、时刻、训练数据、阈值与误报率。部署禁止用 S/E 真值、未来状态、测试成功标签、oracle action 或测试失败后的人工幅度修正。真值 gate 只能作为 oracle 上界，不能混报运行时可观测 ECCBF。

## 5. 动作、夹爪、clip 与延迟

每个模型/本体冻结动作字典：向量顺序、joint/Cartesian、absolute/delta/velocity、坐标系、米/弧度/秒、normalization ID、chunk 与执行前缀。向量维度相同不代表语义和单位相同。

夹爪单列约定：可能是开度米、关节角、编码器值、归一化值或二值开合。**arm 与 gripper 不得混用同一 clip 阈值，或未经声明尺度直接做混合单位 L2**。用逐维物理限制或开发集预定尺度，核查开合方向。分别保存 raw、未限幅校准、最终 command 和实测 state。

各方法共用低层控制与限幅，报告 arm/gripper 饱和率及限幅前后交互。限幅可把独立加法项变成非线性交互，不是认知证据。

延迟同时报告控制/模拟时间和 wall-clock；冻结推理时仿真是否暂停、采样时刻、过期 queue 处理、动作频率与时限。新增校准改变反馈年龄，须有匹配延迟/等预算对照。不能让 Raw 推理时运动、ECCBF 推理时暂停后直接比较。[SO-101 Bench Limitations](https://arxiv.org/html/2610.36420v1) 也明确暂停会隐藏实时成本。

## 6. 必要对照与统计单位

最小对照：Raw、semantic-only、execution-only、无交互 additive、ECCBF、参数/信息/训练预算匹配的 generic residual、方向或符号 placebo。CAG / BAS-VLA 在代码和接口可匹配时再复现；不能直接横比作者数字。若 E 为初态/几何误差，加入简单状态返回/几何控制对照，排除纯可执行性恢复。

四格及方法共享 reset ID 和实测初始状态；seed 只是 RNG 设置，不能代替状态匹配。独立单位是独立抽样 reset/scene 或 episode 配对块，不能把重复同一状态或所有时间点当独立样本。

**paired environment seeds 不是 independent training seeds。** 单一冻结 checkpoint 在多环境种子上评估，只支持该 checkpoint 的性能。训练校准器时独立初始化/数据顺序才是训练种子。分别记录模型 checkpoint、训练/环境/推理种子与独立 reset 数；不以三行 seed 配置声称三个独立模型。

主终点预定为受扰可行条件下 ECCBF−Raw、ECCBF−additive 的 paired SR difference，给成功/总数、百分点差与配对 CI。单格 Wilson CI 不能替代方法差值配对 CI；用预定 exact McNemar 或 reset/scene 分块 bootstrap。连续量先形成 episode 统计量，投影轴/方向/尺度在开发集固定；预定主要多重比较集合与 Holm 等校正。

“提升 10 个百分点”是设计目标，不是保障。非劣效须预定单侧 CI 下界超过 −5 个百分点；“未显著下降”不证明非劣效。Pilot 不能保证 formal 功效；按配对不一致率定样本量或诚实报告区间过宽，不得显著即停。仅一个 held-out task 不支持对所有任务总体泛化。

## 7. A100 前冻结清单

| 项目 | 必须形成的记录 | 当前边界 |
|---|---|---|
| 模型 | 精确 checkpoint/revision、SO-101 训练来源、输入/动作规范、冻结范围 | family 名称不足，待真实权重部署核对 |
| 任务 | `T_c1,T_c2,T_h` task ID、合法目标、可行性、split/reset manifest 与 hash | 未经可行性验证不可称实验已就绪 |
| 因子与估计量 | 主 E 注入位置/强度、S 指令、first-step/feedback/episode 窗口 | 纯动力学首步零交互负对照必须保留 |
| 拟合信息 | 各 S 合法参考、offline/online 字段界限、gate 来源、阈值、变体名 | 禁止将合法目标变化当 bias 或用测试真值部署 |
| 预算与统计 | 配对键、独立 reset、各种 seed、每格 N、主比较/CI/停止规则 | `50 episodes` 是否乘 `3 seeds` 必须明确，不能含糊 |
| 动作与时序 | 逐维单位/clip、夹爪、dt/chunk、暂停与延迟规范 | 契约需用真实 VLA 验证 |
| 版本/故障 | git、资产/配置/权重 hash、技术终止/缺失日志定义、分母 | 系统错误单列，禁止悄悄删除失败 |
| 真机 | 允许重估的相机/本体变换、独立 neutral 开发集及预算、目标映射 | 语义/交互参数及 gate 不由测试结果重拟合 |

现在可完成：原始来源核验、协议/split 清单、数值/接口负对照、脚本可行性与可视化检查。现在不能证明：真实 VLA 交互、校准增益、A100 性能、held-out 或真机一致性。模拟数组、脚本 rollout、单元测试与可打开场景均不能填入论文 SR 结果表。

## 8. A100 可证伪检查顺序

| 阶段 | 所需证据 | 失败或不确定时的处理 |
|---|---|---|
| 0. 载体冒烟 | 权重实际加载、RGB/关节、动作单位、渲染、cache reset、日志 | SO-101 checkpoint/接口未通时先修，不能称偏差 |
| 1. 首步负对照 | 相同输入/RNG，仅改隐藏物理，raw action/chunk 相同；语言变化正对照 | 非零先查泄漏与输入变化，停止认知解释 |
| 2. Raw 四格 Pilot | 合法目标、旧/新计分、完整动作/状态/时间戳、反馈后预定量 | 无解、地板/天花板、评估器错或 E 破坏可达性则修协议 |
| 3. 交互存在 | 预定 I_Y 的量级/方向/区间，state/time/clip/latency 诊断 | 控制后消失或仅限幅/错位所致，不能称内部偏差场 |
| 4. 开发集校准 | 合法参考、可观测 gate、公平消融、减法符号验证 | 只抑制旧目标却不提高新 SR 不算恢复，不事后挑窗口 |
| 5. 封存 held-out | 对 Raw/additive/residual 配对增量与中性非劣效 | 无增量或 CI 不确定如实报告，不继续测试集调参 |
| 6. 同 SO-101 真机 | 同谓词/动作语义、neutral 几何适配后冻结、配对对照 | 收益反转或需语义重拟合则不声称迁移成立 |

## 9. 仿真与真机呼应的最低证据

共享任务谓词、目标定义、语义条件、E 的物理含义、模型/校准版本、动作语义和比较方法。同型号数字孪生不保证动力学、相机与延迟一致。真机需布局 reset ID、实测姿态偏差与方法顺序随机化，不能靠 seed 自动保证精确重置。

仅在独立 neutral 适配集重新估计预先列出的相机/本体变换，各方法共用变换与边界；语义参数、交互参数、gate 阈值不由真机测试再拟合。先 shadow/低速核对接口，安全停止和超时保留分母并另报原因。

并列给仿真/真机 `ΔSR(ECCBF−Raw)`、`ΔSR(ECCBF−additive)`、中性保持、CI、wall-clock 延迟及饱和率。方向一致只支持这些任务和此 SO-101 部署的外部效度，不能保证全任务、全本体、实时或通用 sim-to-real。交互为零、无额外 SR、held-out 失效和真机反转均为允许负结果，不靠换指标掩盖。
