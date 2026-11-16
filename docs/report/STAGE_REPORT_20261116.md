# 机械臂研究选题与实验平台：阶段报告

日期：2026-11-16。项目：`embodied-cogcal`。

## 当前结论与执行边界

**当前资源下没有通过查新、可行性与核心增量门槛的研究方向。按用户最新决定，
停止同平台方向搜索与训练，本阶段交付已有证据、负结果和资产清单。**

既定研究平台为单臂 SO-101、ACT、MuJoCo 和本机 RTX 5070 Ti。
第二只 SO-101、触觉/力传感尚未被用户选为下一阶段平台，不作为可用资源假设。
本项目没有自有真机验证结果。外部论文/仓库的真机记录只属于相关工作。

完整目标仍是形成有核心科学增量、可在仿真与真机检验同一命题的研究方向。
《思考，快与慢》和工业精度补偿作为启发，不提供新颖性证明。
本报告不将阶段整理视为该研究目标已达成。

## 可直接用于汇报的摘要

> 本阶段建立了 SO-101 匹配数据、官方 ACT 模型实现的训练与评估载体，以及基于
> 逐物理步记录的独立审计。固定能力筛查达到 18/20，说明该单任务载体可以完成
> 基础抓放。随后完成了返回动作、执行长度、源位置/遮挡和演示顺序等诊断。
> 这些实验提供了机制线索和负结果，但未形成超过最近邻工作的核心增量。
> 演示顺序的独立审计还排除了“存储顺序就是课程”的解释，保留了历史源码缺口。
> 后续 actuator/payload、接口、伺服电流插入与换任务筛选亦未通过门槛。
> 因此目前不立项、不启动新训练；先保留平台与证据。重新开展选题须由用户明确
> 选择平台变更，再审查具体科学问题及同题仿真—真机的可行性。

## 1. 已有实验事实

下表读取已有 summary、独立审计和机制报告，没有执行新的策略或物理仿真。
不同实验组有不同测试 seed，不能直接把它们合成一个总体成功率。

| 实验与用途 | 已有结果 | 可以支持的解释 | 边界与记录 |
|---|---|---|---|
| 固定 ACT 能力筛查，12100–12119 | 18/20；独立审计 `passed=true` | 单一匹配抓放任务的能力门槛通过 | 不是新方法、真机结果或查新通过；[ACT_RESULT](../../experiments/discovery/official-act-20261116/ACT_RESULT.md) |
| 释放后返回诊断，12300–12319 | baseline 18/20；oracle `freeze_open` 20/20 | 该固定任务中，释放后的动作可以破坏已经完成的放置 | 干预使用仿真接触状态；[诊断结果](../../experiments/discovery/post-release-20261116/RESULT.md) |
| 命令状态机诊断，12400–12419 | baseline 18/20；command-only freeze 20/20 | 该任务固定的 close→open 命令模式可以触发停手 | task-specific 可行性诊断，未验证通用成功检测或新方法 |
| 执行长度诊断，12600–12619 | execute30/10/6 = 19/7/0（各 20 条） | 全局缩短执行长度没有修复该载体，且破坏抓取/抬升 | 不支持简单“越短越好”；[执行长度结果](../../experiments/discovery/execute-horizon-20261116/RESULT_EXECUTE.md) |
| 源位置可见偏移，12700–12719 | baseline 19/20 → shift 1/20 | 当前固定策略对该位置分布变化脆弱 | 不是已确立的认知偏差修正方法；[源偏移结果](../../experiments/discovery/source-shift-20261116/RESULT_SOURCE_SHIFT.md) |
| 物体透明遮挡，12800–12819 | baseline 17/20 → hidden 0/20 | 当前固定策略依赖被遮去的物体视觉信息 | 不能由失败自动推导新的感知机制；[遮挡结果](../../experiments/discovery/occlusion-20261116/RESULT_OCCLUSION.md) |
| 演示存储排列，12900–12919 | canonical 官方 17/20、重训 19/20；reverse/random 各 13/20 | 四个固定模型的描述性 pilot 差异 | 不确认课程优势或总体顺序效应；[独立机制审计](../DEMO_ORDER_MECHANISM_20261116.md) |

12200–12219 的全关节 freeze 属于实现检查：freeze 0/20，失败为释放未验证。
它与后续仅冻结手臂、夹爪继续张开的 `freeze_open` 不同，不混作方法成绩。

### 演示顺序审计的决定性修正

- 当前训练器从第一步起，在全部 24 × 285 = 6840 帧上均匀有放回采样。
  存储排列改变固定随机索引对应的示教身份，不改变抽样分布。
  等长示教的帧内时刻/指令阶段暴露序列亦不变，未实施课程操纵。
- canonical-retrain 对 reverse/random 的原单侧 p=0.035156，对应双侧
  p=0.070313。原预注册未指定这些单侧比较；未显著也不等于证明无效应。
- 池化 Fisher 的 p=0.014476 可算术复现，但忽略了重复测试状态和训练 fit 层次，
  不能作为确认性证据。
- reverse/random 合约记录的旧 `train_order.py` 正文未保存，存在训练来源缺口。
  checkpoint、评估源码、trace 和 physics 的身份匹配，不能补足该缺口。
- 旧报告中若干释放误差均值的计算口径不可追溯。审计另存了明确 landmark
  定义下的结果，未覆盖原值；本报告不把两种口径拼接使用。

## 2. 候选关闭清单与证据层级

下表汇总既有审查的投入裁决；本轮不重新开展文献检索。
每项依据的读取范围和局限保留在原记录中，不能据此声称已完成正式、穷尽查新。

| 路线 | 停止依据 | 当前状态与入口 |
|---|---|---|
| ECCBF/RCBT、动态执行证书等早期主张 | 经典控制、执行合同及后续近邻限制了原核心增量 | 已关闭；[早期路线裁决](../prior-art/ROUTE_DECISION.md) |
| TPSC / shared-prefix / 共享与私有表示 | 现有对比与时序一致性近邻；缺少合格 paired-task learned carrier | no-go；[TPSC 审查](../prior-art/tpsc-scan-20261116.md) |
| post-completion / action-horizon | 近邻覆盖；本地诊断未支持简单缩短执行长度或一致性证书 | no-go；[对应审查](../prior-art/post-completion-action-scan-20261116.md) |
| 源偏移/遮挡的认知偏差基准 | 已有 failure taxonomy、semantic/execution 分解与 recovery 研究 | no-go；[候选记录](../prior-art/cognitive-bias-probe-candidate-20261116.md) |
| demo-order / curriculum / order-robust | 均匀采样机制、统计限制、来源缺口及已有课程/采样/集成近邻 | no-go；[审查与边界](../prior-art/demo-order-scan-20261116.md) |
| actuator/dynamics/payload、接口、servo-current insertion、drive-gain | NeuralActuator、so101-rt-control、TeAR、Silent Interface、ActionABI/ActionShift、tube-insertion 记录及经典辨识近邻 | no-go；[problem-rescreen](../../experiments/discovery/problem-rescreen-20261116/RESULT.md) |
| 动态抛掷/接取、颗粒/液体舀取/倾倒、DLO 布线 | 最近邻覆盖与新增控制、传感、仿真或夹具需求；未建立合格载体 | 三项均 no-go；[换任务矩阵](../../experiments/discovery/task-change-20261116/DECISION_MATRIX.md) |

**证据层级须区分：** demo-order 有原始物理记录与独立 CPU 审计；
problem-rescreen 混合论文正文、代码/README 与仓库元信息，其中 tube-insertion
README 未成功取得，不能称已完成其全文比较；换任务矩阵明确主要依据摘要/元信息
及项目已有资源状态，没有执行三种任务的可行性实验。

当前停止裁决不变，但上述筛查不足以证明 SO-101 的全部潜在科学问题均不存在。
同样，“更换硬件”本身不构成新颖性，也不能保证下一题通过门槛。

## 3. 保留的资产与其用途

| 资产 | 当前位置 | 后续可用范围 |
|---|---|---|
| 24 train / 8 val 匹配示教及采集契约 | `data/discovery/matched-bc-lowrate-20261114/`；[collection contract](../../experiments/discovery/matched-bc-lowrate-20261114/collection/collection-contract.json) | 复核接口、同一基础任务的基线；不冒充新任务训练集 |
| 固定 ACT 权重 | `checkpoints/official-act-20261116/final-20000.pt` | 保留参考模型，不挑 best、不重训 |
| 权重身份 | SHA-256 `71439fda2a7ae13114f6930218a68280d3c7a51c857385907d21e4bfd3cb6f26` | 与 contract、processor、载体版本一起使用 |
| 成功谓词与物理/接口审计 | [独立审计](../../experiments/discovery/official-act-20261116/independent-audit-v1.json) | 保留逐物理步记录、命令消费、释放/抬升/穿透检查；旧能力分数不外推到新平台 |
| 原始正负结果 | `experiments/discovery/` 中各冻结实验目录及其 trace/physics/hash | 阶段报告、对照和追溯；不删失败或事后选 seed |
| demo-order CPU 审计 | [审计入口](../../experiments/discovery/demo-order-audit-20261116/README.md) | 核对统计与采样机制，保留原始结果及来源警告 |
| 候选与任务决策记录 | [方向裁决](../RESEARCH_DIRECTION_DECISION_20261116.md)、problem-rescreen、task-change | 作为下一阶段的排除清单与证据要求；不是执行许可 |

这些属于可复用的平台、证据与负结果。当前没有可写成新算法优势、查新通过、
自有真机补偿效果或同题 sim–real 成果的证据。

## 4. 当前停止清单与下一阶段入口

现在不执行：同平台继续查新筛题、训练、策略/仿真重放、order-robust 预注册、
旧队列恢复、阈值或 checkpoint 选择，以及新硬件采购/部署。
用户已冻结 12100–12919 的重跑；不利用区间内空段绕过停止决定。
13000–13019 此前记为未使用，本轮未动用，也不因此获得执行许可。

| 未来路径 | 用户当前是否已选 | 重新开展前必须明确的内容 |
|---|---|---|
| B1：第二只 SO-101 | 否 | 实际第二只机械臂与两臂角色、同步/数据采集条件、预算与工作区；随后重新审查具体机制和同题仿真—真机路径 |
| B2：低成本触觉/力传感 | 否 | 具体传感形式、可测量量与标定条件、机械/电气接口、预算；随后重新审查机制、简单强基线和同题仿真—真机路径 |
| 保持当前资源 | 当前默认 | 交付本阶段报告与证据，不继续同平台搜索或训练 |

平台变更以用户明确选择为前提。该选择之后仍须核对最近邻、能力载体、具体失效、
强简单对照和有限预算下的否决条件，完成新的预注册后才进入实验。
本报告不预先推荐某项硬件，不以新平台代替科研创新。

## 5. 本轮整理与验证

本轮按顺序读取了用户指定的 handoff、demo-order 机制报告、审计 README 和
problem-rescreen RESULT，并补读既有方向裁决及换任务矩阵。
只写阶段报告、证据清单和当前入口，不修改既有结果或冻结模型/源码。

验证文件保存于 [stage-evidence-20261116](stage-evidence-20261116/)：

- `inputs-before.json`：本轮整理前 552 个已有来源/结果文件的身份快照；
- `frozen-input-check.json`：既有只读 verifier 对 545 个受保护输入的复核输出；
- `stage-verification.json`：上述 552 个文件的前后身份、报告引用的 summary
  数值、报告本地链接及新增文档身份检查。

这些检查不执行策略、训练或仿真，不补造历史缺失源码，不更新旧审计输出。

## 最终状态

**阶段报告整理完成后，当前研究方向状态仍为“当前资源下没有可行方向”。**
后续方向搜索依赖用户明确选择平台变更；在此之前保持停止同平台搜索与训练的决定。
