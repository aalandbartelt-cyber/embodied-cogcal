# 2026-11-16 方向裁决与新问题搜索

## 新增候选已查并 no-go：认知偏差探针基准

- 源位置可见偏移 20 mm：baseline 19/20 → **1/20**；19/20 夹爪更靠近旧训练源。
- 物体透明遮挡：baseline 17/20 → **0/20**；16/20 完全未抬升。
- 分离现象确实存在：视觉是抓取的“存在门控”，但可见位置没有更新抓取点。
- **但 CorrectVLA 2026** 的 failure taxonomy 已覆盖 perception/target failure；
  **SO-101 failure/recovery benchmark 2606.08881v2** 已有 State Mismatch、
  Grasp Instability、semantic/execution 分解和 recovery（真实 SO-101/ACT）。
- 该候选最多是已有 taxonomy 下的细粒度诊断，不是新基准/新方向；**no-go**。
- 候选 memo：`docs/prior-art/cognitive-bias-probe-candidate-20261116.md`。

## 演示顺序线：已 no-go（只读审计完成）

- 同一 24 条示教、同一 seed/20k/最终 checkpoint，只改 episode 顺序；canonical
  官方 17/20、同环境重训 19/20；reverse/random 各 13/20。
- canonical-retrain vs reverse/random 单侧 McNemar p=0.0352，但双侧 **p=0.0703**；
  合并 Fisher p=0.0145 是事后合并，不是确认性检验。
- 独立审计重建训练采样器：从第 1 步起在全部 **6,840 帧**上均匀采样，episode
  存储顺序只重标固定的随机索引流，不是 curriculum/primacy/recency；24 条等长
  episode 不改变相位序列；teacher descriptor 未显示 canonical 与难度/阶段对应。
- reverse/random 引用的旧 `train_order.py` 正文未保留，存在 provenance gap；
  checkpoint/evaluation hash 匹配不等于训练源等价。
- **不预注册 order-robust 训练；不再用 12900–12919。** 证据：
  `experiments/discovery/demo-order-audit-20261116/`、
  `docs/DEMO_ORDER_MECHANISM_20261116.md`。

## 当前裁决

**没有方向通过选题门槛。** 演示顺序线已 no-go，不再是例外。本轮排除：

- 广义 post-completion / post-success：Temporal Aliasing（AJoSR 2026）已有
  release/retreat/stability/collision 证书；GR-BC（CoRL 2026）已对成功轨迹内
  regressive chunks 做后果加权。
- action-chunking 执行/截断：PACE（2026）、Mixture of Horizons、Revisiting
  Open-Loop Execution 已覆盖 phase-aware horizon/开环执行；execute30/10/6 在
  12600–12619 为 19/20、7/20、0/20，全局缩短 horizon 反而破坏抓取/抬升；
  chunk 重叠/边界跳变/跟踪误差不能预测失败，简单执行证书也不成立。
- TPSC（shared-prefix vs uniform task separation）：CMTA（2023）已用
  contrastive modules + temporal attention 处理负迁移/任务内冲突；Sigma-Agent（2024）
  与 AtomSkill（2025）已做多任务对比模仿与语义-时序一致性。
- 早期 ECCBF、RCBT、WAIG、动态证书、VFD、指令必要性等：前轮已否决/降级。
- **problem-rescreen 新增 no-go**：SO-101 actuator/dynamics/payload 被
  NeuralActuator（RSS 2026）与 so101-rt-control 覆盖；action-interface 被 Silent
  Interface（离线 detection/localization，repair 0/10、simulated mitigation fail）
  与 ActionABI/ActionShift（在线有限 probe）覆盖；伺服 load/current + tube insertion
  已有 SO-101 配对 A/B；failure/recovery 有 2606.08881v2；经典 drive-gain 有
  Gautier & Briot ICRA 2012。详见
  `experiments/discovery/problem-rescreen-20261116/RESULT.md`。

ACT 载体完成资格检查（18/20，独立审计通过），但**载体不是方向**。

## 新候选的准入条件

1. 有一个**具体、可测、可复现**的现象或失败模式，不是新模块名；
2. 最近邻（含上述 2026 工作）不能直接解释，或解释后仍留下可测增量；
3. 能在本地 SO-101/ACT/MuJoCo 上做，fresh seeds，固定预算，不依赖 A100；
4. 与工业精度/认知偏差有实质联系，但不把比喻当证据；
5. 先写预注册和失败判据，再训练；no-go 就停。

## 可选的新问题（仅作决策矩阵示例，均未查新通过）

下表不是推荐，也不表示这些任务比已关闭的线更有希望；problem-rescreen 已把
actuator/payload、action-interface、servo-current insertion、failure/recovery 关闭。

| 候选 | 具体现象 | 最近邻风险 | 本地可行性 |
|---|---|---|---|
| 接触丰富装配/轴孔 | ACT 在间隙/姿态误差下卡阻或勉强插入；释放后稳定性 | **已很拥挤**：CompVLA 2026、TLA/UniTacVLA/TacVLA、Tactile-Force Alignment、Learning to Leverage Compliance、大量 peg-in-hole IL | 需新场景/力/接触谓词；中高 |
| 相机/外参标定漂移 | 同一策略在相机偏移下放置误差/失败模式改变 | 域随机化、test-time adaptation、标定 | 可改渲染相机；中 |
| 多物体/遮挡目标选择 | 语言/视觉线索下的错误抓取或目标混淆 | 视觉 grounding、clutter | 需新场景/数据；中 |
| 长时序记忆/阶段切换 | 多阶段任务中忘记已完成阶段 | MemoryClock、Stage-Aware VLA 等 | 任务太短；高 |
| 扰动后恢复 | 执行中被推/滑落后是否恢复 | ProbeAct/RESCUE/恢复学习 | 需新协议；高 |
| 低成本本体反向间隙/摩擦 | 学习策略是否隐式补偿方向相关误差 | **已覆盖**：NeuralActuator、so101-rt-control、TeAR、经典 sysid | 不作为新方向 |

这些只是候选，不是立项建议；每个都必须先做原文查新和小规模可行性探测。
就当前检索看，**接触丰富装配也没有清楚空白**；其余候选同样有强近邻。

## 更严格的裁决

- 当前问题空间（SO-101/ACT 单任务 pick-place 上的 post-completion、action-horizon、
  TPSC、接触丰富装配、相机标定、多物体、长时序、恢复）**都没有找到可立项的空白**。
- 继续在这些线上换模块名、换损失、换任务名，不会产生新方向。
- **下一步不是再跑一个 20k 训练，也不是继续在同平台换任务名**；而是平台级决策：
  第二只 SO-101、低成本触觉/力传感，或先交付阶段报告。
- 在平台决策前，停止同平台搜索与训练；保留 ACT 载体、数据、评测和负结果作为平台/对照。
- 裁决详见 `docs/RESEARCH_DIRECTION_DECISION_20261116.md`。

## 建议的下一步

1. **不要**再训练 post-completion、action-horizon、TPSC、demo-order、actuator/
   payload、action-interface、servo-current insertion 或 failure/recovery 变体。
2. **换任务矩阵已填并 no-go**：动态抛掷/接取、颗粒/液体舀取/倾倒、DLO 布线
   均已有直接近邻，且需要双臂/高速、专用传感或可变形仿真/夹具；当前单 SO-101
   不是 capable carrier。详见
   `experiments/discovery/task-change-20261116/DECISION_MATRIX.md`。
3. 本轮不选任务、不做 1–2 天可行性检查；若未来出现单臂桌面新问题，再按矩阵
   7 条准入条件筛选。
4. 若没有任务能过矩阵，明确报告“当前资源下没有可行方向”，不要用训练量或改名
   掩盖 no-go，也不要把第二只机械臂/专用传感器/新仿真器当隐含前提。
5. 当前 ACT 载体、数据、评测和负结果全部保留，作为新问题的对照/平台。
6. **默认行动：整理阶段报告/负结果，不训练。** 平台变更（第二只 SO-101、
   低成本触觉/力传感）需明确硬件/预算授权后重新预注册；在此之前不再搜索
   单臂模块变体。

## 一句话

当前单臂平台的方向空间已 no-go；继续换任务名/模块名不会产生新方向。下一步是
**平台级决策或阶段报告**，不是再跑一个单臂实验。
