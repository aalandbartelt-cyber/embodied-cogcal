# 研究方向裁决：当前平台 no-go，停止同平台搜索

日期：2026-11-16。裁决对象：`embodied-cogcal` 当前单臂 SO-101 + ACT + MuJoCo/5070 Ti 平台。
本文是**方向裁决**，不是新方法、不是查新通过、不是真机结果。

## 裁决

**在当前平台约束下，没有研究方向通过选题门槛。停止继续在同一单臂任务上换模块、
损失、任务名或训练配置。**

这不是“再想一个点子”能解决的问题。连续关闭的线已经覆盖了当前平台的主要可行域：

- ECCBF、RCBT、WAIC/动态证书、VFD、指令必要性；
- TPSC / 共享-私有表示；
- 广义 post-completion / post-success；
- action-horizon / chunk 截断；
- 认知偏差探针（源偏移、遮挡）；
- demo-order / curriculum；
- SO-101 actuator/dynamics/payload、action-interface、servo-current insertion、
  failure/recovery、经典 drive-gain；
- 换任务：动态抛掷/接取、颗粒/液体舀取/倾倒、DLO 布线。

每条线都在接近立项时被 2025–2026 的直接近邻覆盖，或者被当前载体/硬件排除。
继续在同一平台搜索的边际信息已经很低。

## 为什么不是“努力不够”

当前筛选同时要求：

1. 新机制，而不是工程组合；
2. 单只 SO-101、30 Hz ACT、MuJoCo/5070 Ti；
3. 同题 sim–real；
4. 强于 2026 直接近邻；
5. 有突破性/可投稿。

这个交集在当前资源下接近空集。最近的三次裁决已经说明了这一点：

- **demo-order**：均匀采样、无 curriculum、provenance gap、双侧 p=0.0703；
- **problem-rescreen**：actuator/payload、interface、servo-current insertion、
  failure/recovery、drive-gain 均有直接近邻；
- **task-change**：动态/颗粒/DLO 均需要双臂/高速、专用传感或可变形仿真/夹具，
  当前单 SO-101 不是 capable carrier。

因此，正确的动作不是再跑一个 20k，而是**改变约束**。

## 当前可保留的资产

- 固定 ACT 载体：18/20，独立审计通过；checkpoint/contract/评测流程可复用。
- 严格的成功谓词、物理审计、trace/physics/hash 保留流程。
- post-release 诊断：释放时 xy 2.4–4.3 mm，成功后返回动作导致 14–164 mm 最终误差；
  oracle freeze 20/20，command-only 检测 20/20。
- demo-order 只读审计：545 个冻结输入未变，证明“顺序效应”是 pilot 而非 curriculum。
- 一组干净的负结果和最近邻边界；可作为阶段报告/工程报告，但不能冒充方向。

这些资产足以支撑**平台级下一步**或**诚实的阶段报告**，不足以支撑继续换模块名。

## 两条未来路径（不是当前方向）

### B1. 加第二只 SO-101，做双臂协调

- 需要：第二只 SO-101、双臂工作区、同步遥操作/数据采集、双臂碰撞与协调谓词。
- 可能的问题：双臂交接、共同搬运、一只臂固定/另一只臂操作时的角色分配。
- 风险：ALOHA/ACT、bimanual manipulation、dynamic handover 等已很拥挤；必须先找到一个
  具体的、未被覆盖的失败机制，再预注册。
- 这是**平台项目**，不是当前单臂实验的增量。

### B2. 加低成本触觉/力传感器，做接触丰富任务

- 需要：可集成的低成本的触觉/力传感、标定、接触谓词、真实硬件数据。
- 可能的问题：接触状态估计、滑移检测、力感知的抓取/插入。
- 风险：tactile VLA、insertion、RoboCAP、NeuralActuator 等已覆盖很多；
  仍需要具体的未覆盖机制。
- 这也是**平台项目**，不是当前 ACT checkpoint 的增量。

### 不推荐的路径

- 继续在单臂 pick-place/insertion/assembly 上换 loss、module、horizon、order、
  detector 或 prompt；
- 把“单臂低成本/vision-only”当作新机制；
- 把已经覆盖的 actuator/interface/insertion/failure 问题改名；
- 在没有新平台的情况下再训练 13000–13019。

## 重新开启方向搜索的条件

只有满足以下全部条件，才重新开启：

1. **新平台或新传感**已经可用（第二只臂/触觉/力/可变形仿真），不是隐含假设；
2. 有一个**具体的、可测的失败机制**，不是“精度/鲁棒性”；
3. 最近邻原文已给出**未覆盖的剩余差异**；
4. 有强简单基线（经典控制/sysid、oracle、no-correction、task-specific safety）；
5. 有 1–2 天可执行的 bounded falsifier；
6. 先预注册，再训练；no-go 就停。

## 默认行动（已决定）

- **默认走 D：整理阶段报告/负结果，不训练。** 保留 ACT 载体、成功谓词/审计流程、
  post-release 诊断、demo-order 审计和 rescreen 边界，作为阶段报告/工程报告资产。
- **B1（第二只 SO-101）和 B2（低成本触觉/力传感）是未来可选路径，不是当前计划。**
  只有在用户明确授权硬件/预算后，才重新预注册；不得把新硬件当隐含前提。
- **不再搜索单臂模块变体。** 若没有平台变更，当前项目的研究方向状态就是
  “当前资源下没有可行方向”，而不是“还在找”。

## 当前状态

- **没有方向通过查新门槛。**
- **停止同平台方向搜索和训练。**
- **不声称任何方法/补偿/真机结论。**
- 默认行动是阶段报告；平台变更属于下一阶段决策，不是本轮继续搜索。
