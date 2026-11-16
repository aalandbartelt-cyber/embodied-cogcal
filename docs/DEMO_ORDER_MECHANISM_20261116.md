# Demo-order pilot：只读机制审计与 negative memo

日期：2026-11-16。裁决：**no-go；当前仍没有通过选题门槛的研究方向。**

本轮没有训练、策略推理或仿真重放。没有修改原始 `RESULT_ORDER.md`、JSON、
trace、physics、checkpoint、official-ACT 源码或受保护 manifest。
全部新分析在 `experiments/discovery/demo-order-audit-20261116/`。
本文纠正解释，不回写历史结果。查新对照见
[demo-order scan](prior-art/demo-order-scan-20261116.md)。

## 1. 可核验的事实与追溯缺口

四个评估都包含 12900–12919，逐行 `episodes.jsonl` 与 summary 一致。
这 20 个 seed 与有记录的 train 4100–4123、val 5100–5107 不相交，并在原
`PREREG.md` 中作为测试集指定；只能据此确认相对已记录训练/验证的数据隔离，
不能证明不存在未记录使用。它们现已使用，不能再当作 fresh seeds。

| 按路径区分的条件 | checkpoint | 成功 | 最终 xy 均值 / 中位数 mm | validation normalized L1 |
|---|---|---:|---:|---:|
| `canonical/`，官方既有 fit | `official-act-20261116/final-20000.pt` | 17/20 | 26.576 / 28.098 | 0.06602 |
| `canonical-retrain-eval/`，canonical 重训 | `demo-order-20261116/canonical-retrain.pt` | 19/20 | 23.754 / 20.836 | 0.05902 |
| `reverse/` | `demo-order-20261116/reverse-solo.pt` | 13/20 | 32.922 / 31.281 | 0.06493 |
| `random/` | `demo-order-20261116/random-solo.pt` | 13/20 | 32.265 / 32.437 | 0.06209 |

checkpoint 均位于仓库根目录 `checkpoints/`。两种 canonical 的 summary label
都叫 `canonical`，本审计始终用路径区分。四个 checkpoint 的实际 SHA-256、
对应 training contract、config、32 个数据文件、80 个 trace 和 80 个 physics
文件均与各自记录相符；所有物理成功谓词从 19,000 tick/episode 的数组独立复算，
结果与标签一致。四个 config hash 相同；normalizer 另用 CPU 从 24 条训练数据
按三个排列重算，float32 结果完全相同。

**不能把这些检查概括为“全部训练来源一致”。** reverse/random 合约记录的
`train_order.py` hash 为 `94d32707…`，当前文件及 canonical-retrain 合约为
`543cbd5b…`。本轮未改这个文件，但现有输入中没有该旧版本正文，无法审阅其差异。
official `act_interface.py` 和四组评估依赖的运行源码 hash 均匹配。
因此数值/产物身份已核验，reverse/random 的完整训练源码追溯仍有缺口；
不能从相同 config 反推“严格只有顺序不同”。本轮不修合约，也不补写旧来源。

## 2. 统计复算改变了证据强度

| 配对比较 A vs B | A-only / B-only | 单侧，A 更好 | 双侧 exact McNemar |
|---|---:|---:|---:|
| official canonical vs reverse | 6 / 2 | 0.144531 | 0.289063 |
| official canonical vs random | 7 / 3 | 0.171875 | 0.343750 |
| canonical retrain vs reverse | 7 / 1 | 0.035156 | 0.070313 |
| canonical retrain vs random | 7 / 1 | 0.035156 | 0.070313 |
| official canonical vs canonical retrain | 1 / 3 | 0.937500 | 0.625000 |

旧记录 official-vs-retrain 的 0.3125 是**重训更好**方向的单侧尾概率。
原分析函数采用 discordant 两项的较小项求尾概率，读者必须同时看方向，
不能把该数值无条件解释为表中 A 更好。

原预注册只写描述性决策，没有提前指定这些单侧方向、两次比较的多重性规则，
也没有把后加的 canonical-retrain 作为预定确认性分析。
原 `p=0.0352` 算术正确，但不能升级为已预注册确认的顺序优势。
双侧未过 0.05 也不证明没有效应或等效。

合并 Fisher 的 `[[36,4],[26,14]]` 可复算为双侧 `p=0.0144757`。
**该池化不是有效的确认性推断**：同 20 个测试初态重复出现在四个 fit 中，
还把两次 canonical fit 与各一次其他排列的训练层次差异忽略了。
这些不是 80 个独立的训练重复或独立场景。配对检验至多比较这几个固定模型在
这批测试状态上的表现，不能估计“canonical 顺序”跨训练运行的总体优势。

可保留的事实是 **canonical 两次 17/19，reverse/random 13/13**。
这是 pilot；没有足够独立训练重复把排列、随机样本流和其他运行差异拆开。

## 3. 存储顺序并非课程：实现层面的区别

当前 `train_order.py` 先排列 episode，再构建拼接后的 `TrainingData`；
`TrainingData` 对每条示教单独构建 future targets，未跨 episode 拼接动作目标。
训练每一步调用：

```python
generator = np.random.default_rng(42)
indices = generator.integers(6840, size=32)
batch = train_data.batch(indices)
```

24 × 285 = 6840 帧从一开始全部可用。任意存储排列 π 下，若索引 I 均匀有放回抽样，
则 `P(π(I)=i)=1/6840`；任意有限批次序列的抽样分布也保持不变。
这里是索引重标记，不存在训练时间随课程难度逐步变化的安排。
这个分布结论适用于实际采用上述采样机制的实现；旧源码缺失使其对历史
reverse/random fit 的逐行追溯仍受 §1 的限制。

**固定 seed 下的实际样本流会改变。** 对同一个整数索引，canonical/reverse/random
映射到不同示教。CPU 重建 20k × 32 个索引后，最后 batch 的前五个示教为：

- canonical：4115、4109、4120、4100、4113；
- reverse：4108、4114、4103、4123、4110；
- random：4110、4111、4105、4109、4117。

所以不能说“最后 batch 与 episode 顺序无关”。准确表述是：**抽样概率不变，
实现的 batch 身份改变**。三个条件的最后 batch 平均源位置分别约
(199.450, −74.382)、(199.857, −75.251)、(199.848, −75.011) mm；
最后 1000 updates 平均位置则约为 (199.617, −74.877)、(199.640, −74.878)、
(199.623, −74.886) mm。不能拿一个末批次解释最终策略的因果差异。

示教等长还带来更强的不变量：索引对 285 的余数不变，因而**每次抽样的帧内时刻、
指令阶段序列完全相同**。三个排列改变示教身份，未改变阶段暴露时序。
两次 canonical 的重建样本流相同而结果不同，说明还存在样本流以外的运行差异；
现有日志不能识别其具体来源。没有原始 batch-ID 日志，重建不能冒充训练时记录。

## 4. 24 条 teacher 没有显示 canonical 是课程

逐示教表见 `teacher-descriptors.csv`：保存 seed、canonical position 0–23、
source x/y、成功、goal error、max z、动作路径长度、夹爪时序和九阶段动作路径。
24/24 teacher 成功；最终误差 17.577–25.268 mm；max z 83.507–83.528 mm。
teacher 最终误差是结果描述，不是独立定义的任务难度。

| 与 canonical position 的 Spearman 相关 | rho | 探索性、未校正 p |
|---|---:|---:|
| source x | −0.237 | 0.266 |
| source y | −0.042 | 0.846 |
| teacher final error | +0.310 | 0.140 |
| max object z | +0.177 | 0.407 |
| 总动作路径长度 | +0.047 | 0.828 |

固定 teacher 的指令阶段为 home/approach/descend/close/lift/carry/place/open/retreat，
时长分别 0.4/1.0/1.3/1.0/1.3/1.6/1.2/0.8/0.9 s。
所有 teacher 夹爪指令第一次低于 0.20 rad 在 step 91，重新高于该中点在 step 242。
这些是固定指令日程的描述，不能当成实际接触或任务完成时间。
没有观察到按源位置或已测结果单调排序的证据；样本量也不足以排除所有潜在难度因素。
即使静态数组相关，均匀采样也不会自动把它转成 easy-to-hard 课程。

## 5. 策略差异集中于释放后的位移，但不是新的失效机制

初始 RGB hash 和 q 在同 seed 的四条件间完全匹配。只比较这个共同输入下的
首个 chunk，后续闭环轨迹不同后不把 action 差异当作同输入的策略差异。

| 比较 | 初始 chunk 平均 L1 rad | 首动作平均 L1 rad |
|---|---:|---:|
| official vs retrain | 0.001424 | 0.001287 |
| official vs reverse | 0.003098 | 0.001346 |
| official vs random | 0.003521 | 0.005343 |
| retrain vs reverse | 0.003413 | 0.001335 |
| retrain vs random | 0.003837 | 0.004629 |

物理 landmark 明确定义为：已经出现连续 0.5 s 双指抬升之后，首次完整
0.1 s 无任何机器人接触的**窗口结束时**。它只用于读取已有物理数组，是 oracle
描述，未用来干预、调整成功阈值或提出新方法。

| 条件 | 释放误差均值 mm | 释放后净 xy 位移均值 mm | 最终 bias x/y 均值 mm |
|---|---:|---:|---:|
| official canonical | 3.271 | 26.620 | +15.36 / −21.46 |
| canonical retrain | 3.013 | 24.448 | +11.09 / −20.60 |
| reverse | 4.107 | 32.311 | +18.44 / −26.83 |
| random | 3.339 | 32.295 | +19.76 / −25.04 |

**与旧记录的差异必须保留**：旧 `RESULT_ORDER.md` 写 3.59/4.36 和
26.98/32.77 mm，但其三个分析脚本没有保存相应 landmark 的计算。
本审计没有复现这些精确释放均值，不能称其已核验；也没有改写旧值。
另存的 `control-grid-release-metrics.csv` 把同一窗口结束映射到控制步末端，
结果基本相同，仍不能解释旧均值。这里只使用上述可重算定义，避免混用口径。

全部 80 条均建立了抬升，最终释放/穿透检查符合原记录；所有失败为 placement。
失败 seed 与原记录相同，重训唯一失败为 **12916**。
逐条 source、release/post displacement、final bias、35 mm 判据余量见
`test-episode-metrics.csv` 和 `mechanism-extra.json`，包含所有成功与失败，未挑子集。

- official 三次失败最终误差 37.44、43.23、35.55 mm。
- reverse 失败为 12902/05/06/07/12/13/14：最终误差分别
  81.02/39.85/35.58/37.38/35.09/38.51/39.40 mm。
- random 失败为 12904/05/11/12/14/17/19：最终误差分别
  38.96/37.43/38.70/50.65/37.22/52.06/36.73 mm。
- canonical-retrain 的 12916 达 79.87 mm，尽管释放误差仅 2.52 mm。

因此部分分类变化在 35 mm 附近，但不能把所有失败概括为阈值边缘噪声。
81 mm 和 80 mm 事件在不同训练 fit 中均出现。失败源位置横跨源区域，
不存在当前四条件共同复现的简单源位置失败分区。
source x/y 与 final error 的相关是 20-episode 探索性分析；重训的 source-x
rho=−0.523（未校正 p=0.0179）没有在 reverse/random 重现，不能据此事后挑区域。
释放后位移较大与既有返回阶段问题相容，但未分离出由 data-order 独有的新机制。

## 6. 裁决与保留价值

当前现象与固定随机索引在不同存储排列下映射为不同 SGD 样本流相容，
也混有其他运行差异；**不能断言“已经证明纯 SGD 噪声”，也不能断言课程/首因/近因**。
因果来源没有拆开，并不妨碍否决目前的方法主张：

1. 从一开始已均匀抽样，仅再排列 episode 不改变训练分布；若改为无放回逐 epoch
   重排，则进入已有随机重排问题，不能单靠该改动构成新方法。
2. 真正的质量/难度课程已有 COIL 及其 return-ordered BC 对照；本数据没有显示
   一个额外机制，让新课程超出这些强近邻。
3. 多 fit 聚合属于已有 ensemble 思路。普通神经网络预测集成不等于 ACT 闭环动作
   平均已验证有效；也不能把未经验证的权重平均当可用修复。

这不是“搜不到完全同题论文所以存在空白”，也不是“p>0.05 所以没有现象”。
**no-go 是选题投入裁决：当前 pilot 没有支撑一个区别于已有采样/课程/集成方法的
核心创新。** 不训练 order-robust、curriculum、TPSC 或其他已关闭线路；
不创建 13000–13019 的新实验，保留这些 seed 未使用状态。

保留本轮作为负结果、采样机制澄清和统计/来源追溯案例。继续寻找研究方向需要
新的突出科学问题及其近邻差异，不能把本线改名重启。

**哪条观察改变了判断？** 训练器从第一步就在全部等长示教帧上均匀有放回采样，
episode 排列只重映射固定随机样本流，连阶段暴露序列都没改变；它没有实施原先
猜测的课程或首因/近因操纵。
