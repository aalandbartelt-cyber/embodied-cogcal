# ECCBF 论文结构与证据占位

**历史提纲：2026-11-14 深审后停止以 ECCBF 为核心投稿。** 下文不能作为当前论文写作任务；
新问题尚未冻结，先读 [方向裁决](prior-art/ROUTE_DECISION.md)。

**2026-11-14：本文件保留为候选结构，不是已选定论文方案。** 旧的“组合交互 + 冻结残差 + 真机”
不足以支撑当前创新定位，先执行 [查新/换题门槛](prior-art/ROUTE_DECISION.md)。
本轮可直接审阅的有来源材料见 [相关工作准备稿](paper/RELATED_WORK_DRAFT.md) 与
[主张—证据表](paper/CLAIM_EVIDENCE_MATRIX.md)。

本文只在实验完成后填入数值；所有 `<待测>` 保持为空，不能用预期结果替代。

## 暂定标题

**Embodiment-Conditioned Cognitive Bias Fields for Vision-Language-Action Policies**

副标题可根据查新结果改为：

**A Factorial Calibration Protocol from SO-101 Simulation to Real Execution**

## 一句话贡献

候选研究问题是：匹配条件下的语义×执行结构能否在相同预算下优于无结构 residual / additive 与纯时序修复，
并在同 SO-101 真机保持方法增量。标准四格公式、交互现象和闭环组织方式均不单独作为贡献。

## 研究问题

- **RQ1：** 语言—观测冲突是否导致可重复的任务成功率下降和动作偏移？
- **RQ2：** 机器人本体和执行条件是否改变该冲突效应？
- **RQ3：** 交互项校准是否优于语义单独校准、执行单独校准和无交互项加法校准？
- **RQ4：** 仿真中识别的语义校准方向能否在同一本体 SO-101 真机保持？

## 论文结构

### 1. Introduction

只保留三段逻辑：

1. VLA 的任务成功率会掩盖语言、观测和执行条件之间的耦合失效；
2. 现有工作已覆盖语言纠偏、门控残差、组合扰动与运行时执行；指出具体可检验的差异，不能笼统说只研究单项；
3. 在通过查新后，用同一本体仿真—真机检验所选中心命题的增量；当前不预填结果或贡献。

### 2. Related Work

- 语言落地与反事实诊断：ICBench、LIBERO-CF、SwitchVLA；
- 组合/运行时鲁棒性：LIBERO-Plus、LIBERO-PRO/Pro2.0、VLA-Gauge；
- 冻结 VLA 的动作校准与残差修正：BAS-VLA、IDR、CorrectVLA 等；
- 执行时序、监测与诊断：RTC、Sentinel、RoboMD；
- 跨域/跨本体适配：RAGu、SO-101 相关工作；
- 工业机器人误差分解与标定：只用于方法论来源，不声称部件本身新颖。

每个近邻工作必须填写 `docs/prior-art/prior-art-matrix.md`，不能只写泛泛 Related Work。

### 3. Method

1. SO-101 同体仿真—真机设置；
2. 2×2 语义×执行匹配因子设计；
3. `b_sem`、`b_exec`、`b_int` 定义；
4. 选择性 ECCBF 动作校准器；
5. 训练/校准集与 held-out 测试划分；
6. 不使用 privileged target pose 的运行时约束。

### 4. Experimental Setup

- 主模型、checkpoint、动作空间和相机；
- 任务选择规则和失败分类；
- 仿真 Pilot 与正式矩阵；
- SO-101 真机安全、标定和样本量；
- 统计检验、Wilson 区间、Holm 校正和排除规则。

### 5. Results

#### 5.1 偏差存在性

主表：四格条件的成功率、动作偏移、`b_sem`、`b_exec`、`b_int`。

#### 5.2 校准准确率收益

主表：Raw、Reflection、Semantic-only、Execution-only、Additive、ECCBF、Placebo、Oracle。
主指标为受扰任务成功率提升，次指标为中性任务保持率。

#### 5.3 Held-out 任务

只报告未参与校准的任务、布局和物体变体；不得把调参任务与测试任务混合。

#### 5.4 仿真—真机一致性

报告仿真和 SO-101 真机中交互项方向、成功率差值和失败类型的一致性；真机小样本不夸大
统计显著性。

#### 5.5 消融与失败边界

- 去掉交互项；
- 去掉选择性门控；
- 使用错误符号；
- 增大延迟/外参扰动；
- 任务成功率过低或过高时的失效边界。

## 图表计划

- **Fig. 1**：ECCBF 核心机制与 2×2 因子设计；
- **Fig. 2**：四格条件的成功率和动作偏差；
- **Fig. 3**：多对照组准确率提升与中性保持率；
- **Fig. 4**：`b_int` 在 held-out 任务和 SO-101 真机的方向一致性；
- **Fig. 5**：失败/补偿成功 MuJoCo 与真机视频关键帧；
- **Table 1**：查新差异矩阵；
- **Table 2**：主实验和统计契约；
- **Table 3**：对照组与消融；
- **Table 4**：仿真—真机迁移结果。

## 审稿人可能追问

- 交互项是否只是普通动作残差？→ 必须比较 Additive 和 Placebo；
- 是否使用了 privileged state？→ 审计运行时输入；
- 真机是否只是另一个演示？→ 复用同一任务、指标、校准接口和语义参数；
- 是否只挑选了有效任务？→ 预先登记任务选择规则并报告淘汰原因；
- 是否存在基准重叠？→ 投稿前复查查新矩阵并收缩主张。
