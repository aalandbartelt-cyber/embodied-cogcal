# 当前研究准备度与剩余工作

**后续更新：用户已选 B2（低成本触觉／力传感），新增预算 1 万元。**
暂按传感器、采集设备、夹具加工与独立校准参考全包含；尚无实际完整报价。
[预算与科学问题裁决](B2_BUDGET_DECISION_20261116.md)：目前不锁主传感器，不采购；
持续接触漂移、微小动作修正、视觉力表示三个问题均未取得方法 go。
[B2 首轮审查](B2_SENSOR_SCREEN_20261116.md)只核物理量、原文与信息条件，
没有确定方法、采购或启动实验。旧路线的 no-go 与旧结果继续保留。
以下“未选平台”表述是本次选择前的阶段状态。

**平台选择前的执行记录：只交付[阶段报告](report/STAGE_REPORT_20261116.md)，不继续同平台
搜索或训练。** 当前资源下无通过门槛的方向；第二只 SO-101、低成本触觉/力传感
均待用户明确选择，不视为已可用或已授权的平台。

## 2026-11-16 更新：ACT 能力通过；当前平台方向搜索 no-go

- 官方 ACT 固定能力筛查在 fresh seeds 12100–12119 上 **18/20 PASS**，独立物理审计
  `passed=true`；只说明单任务载体可用，不是方向或查新结论。
- 事后诊断（预注册 + 修正 addendum，fresh seeds 12300–12319）：ACT 在首次释放时
  xy 误差仅 **2.4–4.3 mm**；未干预基线最终误差 14.4–163.7 mm，释放后位移
  15.6–161.3 mm。冻结手臂、只让夹爪继续张开后，同 seeds **20/20**，最终
  **1.97–3.94 mm**；配对改善 20/20（符号检验 $p\approx9.5\times10^{-7}$）。
- 失败机制因此不是“放置精度不足”，而是**模仿了演示中的成功后返回动作**：
  该动作重新接触物体并把已完成的放置推走。释放检测使用仿真接触状态，是
  oracle diagnostic，不是可部署方法。
- 进一步把检测器换成**仅用夹爪命令**的状态机（闭合 ≤0.13 连续 ≥20 步后首次 ≥0.15），
  在 fresh seeds 12400–12419 上 baseline 18/20 → **20/20**，最终
  **2.03–5.45 mm**，配对改善 20/20。它仍是 task-specific feasibility diagnostic，
  不是通用成功检测器、不是新方法。
- **广义 post-completion 线已 no-go**：Temporal Aliasing（AJoSR 2026）已有
  lift/cross/release/retreat/stability/collision 六谓词证书，并明确处理 re-grasp/push；
  GR-BC（CoRL 2026）已对成功轨迹内 regressive chunks 做后果加权。
  因此“成功后动作被 BC 模仿并 undo 任务”不能作为核心方向；task-specific 检测器
  只是工程可行性。
- **action-chunking 窄线也已关闭**：ACT 预测 100 步、执行 30 步，最后一个 query 的
  chunk 已跨过成功点；但 PACE（2026）已做 phase-aware chunk execution，Mixture of
  Horizons、Revisiting Open-Loop Execution 已覆盖 horizon/开环执行。不要再把
  success-aware truncation 或执行一致性证书当新方向。
- 额外负结果（12600–12619）：execute30/10/6 = **19/20、7/20、0/20**；
  全局缩短执行步长没有消除释放后位移，反而破坏抓取/抬升。chunk 重叠/边界跳变/
  跟踪误差也不能预测失败（execute6 指标更低是因为更早失败），所以简单的
  “执行一致性证书”也不成立。**action-chunking 窄线关闭。**
- **TPSC 也已 no-go**：CMTA（2023）已用 contrastive modules + temporal attention
  处理负迁移/任务内冲突；Sigma-Agent（2024）与 AtomSkill（2025）已做多任务对比模仿
  与语义-时序一致性。当前 ACT 是单任务，TPSC 场景 scripted grasp 仍 0/20；
  不要构建 paired-task carrier 或训练。
- **认知偏差探针候选也已 no-go**：冻结 ACT 试点确实有
  源偏移 **19/20 → 1/20**、遮挡 **17/20 → 0/20** 的分离现象，但
  CorrectVLA（2026）的 failure taxonomy 已覆盖 perception/target failure；
  SO-101 failure/recovery benchmark（2606.08881v2）已有 State Mismatch、
  Grasp Instability、semantic/execution 分解和 recovery（真实 SO-101/ACT）。
  该候选最多是已有 taxonomy 下的细粒度诊断，不是新方向。
- **演示顺序线已 no-go**：canonical 官方 17/20、同环境重训 19/20；reverse/random
  各 13/20。canonical-retrain vs reverse/random 单侧 McNemar p=0.0352，但双侧
  **p=0.0703**；合并 Fisher p=0.0145 是事后合并，不是确认性检验。独立只读审计
  重建了训练采样器：从第 1 步起在全部 **6,840 帧**上均匀采样，episode 存储顺序
  只重标固定的随机索引流，不是 curriculum/primacy/recency；24 条等长 episode
  也不改变相位序列；teacher descriptor 未显示 canonical 与难度/阶段对应；
  reverse/random 引用的旧 `train_order.py` 正文未保留，存在 provenance gap。
  **不再预注册 order-robust 训练，不再用 12900–12919。**
- **problem-rescreen 也已 no-go**：SO-101 actuator/dynamics/payload 被
  NeuralActuator（RSS 2026）与 so101-rt-control 覆盖；action-interface 的离线
  detection/localization 被 Silent Interface（CoRL 2026 workshop）覆盖，在线有限
  probe 被 ActionABI/ActionShift 覆盖，且 Silent Interface 的 exact repair 0/10、
  simulated mitigation fail；伺服 load/current + tube insertion 已有 SO-101 配对
  A/B；failure/recovery 有 2606.08881v2；经典 drive-gain 有 Gautier & Briot
  ICRA 2012。详见 `experiments/discovery/problem-rescreen-20261116/RESULT.md`。
- **当前没有任何方向通过选题门槛。** 不要训练；不要复用 12100–12119、
  12200–12219、12300–12319、12400–12419、12600–12619、12700–12719、
  12800–12819、12900–12919。13000–13019 仍未使用。
- 下一步不是再换模块名/损失，而是换任务/载体或换科学问题；新候选必须先过
  problem-rescreen 的 7 条准入条件（capable carrier、causal mechanism、非覆盖、
  强简单对照、同题 sim-real、bounded falsifier、先证据后命名）。
- **换任务矩阵也已 no-go**：动态抛掷/接取（AthenaZero、Robot Juggling）、
  颗粒/液体舀取/倾倒（RoboCAP、Matl ICRA 2020、Alloy）、DLO 布线（SILO、
  WireCraft CoRL 2026）都已有直接近邻，且需要双臂/高速、专用传感或可变形
  仿真/夹具；当前单 SO-101 不是 capable carrier。详见
  `experiments/discovery/task-change-20261116/DECISION_MATRIX.md`。
- **2026-11-16 方向裁决：停止同平台搜索与训练。** 单臂 SO-101 + ACT + MuJoCo
  的可行域已被反复覆盖；下一步是平台级决策（第二只 SO-101、低成本触觉/力传感，
  或先交付阶段报告），不是再跑一个单臂实验。详见
  `docs/RESEARCH_DIRECTION_DECISION_20261116.md`。
- 下一步是重新定义研究问题/任务；候选与准入条件见
  [`NEXT_PROBLEM_SEARCH_20261116.md`](NEXT_PROBLEM_SEARCH_20261116.md)。
- 详见 [`post-release-20261116/RESULT.md`](../experiments/discovery/post-release-20261116/RESULT.md)
  与 [`CODEX_HANDOFF_20261116.md`](CODEX_HANDOFF_20261116.md)。

## 当前结论：研究方向尚未确定

2026-11-15 更新。用户要求的结果是：**有查新依据、有核心科学增量、经过努力可实现，
且 SO-101 仿真和真机验证同一命题的研究方向**。先发现具体失效，再提出针对性方法；
认知偏差与工业补偿是启发来源，题名不必保留。

本地 5070 Ti 的 SmolVLA 和普通 BC 能力检查已经运行；最新普通模型为 15/20，
未达到事前 16/20 门槛，停止继续微调该小模型。补偿/TPSC 干预尚未执行，不能声称其受损或有效。
三段公开 SO-101 真实轨迹仅通过离线数据资格检查，没有任务损害或 VLA 因果证据。
新一手近邻与实际边界见 [执行证据后续核查](prior-art/execution-evidence-followup.md)。

接下来以具体问题的证据、最近邻差异、强简单对照和同命题真机可测性筛选，最多同时深审两项。
“提高执行精度破坏阶段线索”只是未实测的问题，未立项；一般补偿与仿真假失败审计已有直接近邻。
**目前没有通过选题门槛的主方法，完整目标 active。**

11月16日[固定阶段复核](../experiments/discovery/real-stage-screen-20261116/README.md)已完成12条327帧/7页。
失败不是单一抓取前问题，成功也可包含中途偏离；日志/稀疏视频不能因果归类提前release、失持或几何错位。
ProbeAct/RESCUE已有同步检测、失败位置CBF及干预价值主张，通用恢复思路不作为本项目新核心。
本轮停止继续堆同类图，公开两组小ACT还缺原生环境绑定；未下载权重或训练。
下一步先核本地官方ACT与已合格teacher数据的接口及一次固定能力检查，不重启旧小模型微调。
以下11月15日记录保留当时顺序；当前接续见handoff §24。

当前新增[真实失败检查与下一问题](../experiments/discovery/deployment-failures-20261115/README.md)：
固定同一π0.5/SO101套环任务，事前取6成功/6失败，实际核对5421行和72张指定顶视图；
看到了正确套环与环移到另一侧凹槽的可见差异，尚不能归因于机械/感知/决策。
旧20k SmolVLA的pre/post stats与固定数据一致；不因外部issue猜测就换stats或重训。
[配对几何监督与CFM最小检查](../experiments/discovery/geometric-supervision-20261115/README.md)已完成：
原权重下受限单坐标的总体梯度非零，负对照/独立FK/求解核验通过。
10步非对称采样有一个确定性分位数点离开预定合法带；100/1000步差异消失。
没有实际机器人任务损害或独立方法增量，**该线降为诊断储备，停止扩展解析反例或训练修正模块**。
这不是Armnet真实失败的解释，也不是否定GRASP。接着按事前选择核真实失败的多视角过程。
该[多视角复核](../experiments/discovery/deployment-failures-20261115/process-review.md)现已完成306帧/7页：
成功记录也有取环区域停留，失败后段仍在该区域且日志命令/状态并非恒定；
没有据此识别滑移、机械误差或记忆缺失。下一步先分清抓持前/后失败，再检查可区分的干预。

位姿重定向线已实际完成15条物理回放：两种普通IK各4/4，本工作区没有任务损害，停止当前核心。
新检查的[flow分歧测量机制](../experiments/discovery/vfd-quadrature-20261115/README.md)
有48条件的有限网格排序反转、末端相同路径误差的解析边界以及有限数据/同数据优化对照。
但传统Gauss–Legendre20点解决第一组排序反转，同数据两参数模型收敛后分歧消失。
因此只保留为待验证线索；没有真实learned VLA的风险/示教选择损害，也未证明新方法超出已有prefix/数值积分/校准。
下一轮先审最近邻与真实ensemble资产资格，不自动开始神经模型训练，亦不因该反例就确定方向。

该资产审查已完成，见[后续裁决](../experiments/discovery/vfd-assets-20261115/README.md)。
实际读Drishti 63条/4607步，未取得完整ODE/chunk与可绑定独立ensemble；公开标签也不足以复算物理抓放。
UQ v2和CFM/NLL新近邻进一步缩小核心空间。当前VFD线已移出主推荐，保留为待核线索；继续寻找具体任务问题。

新测到[多个可行目标与语言必要性的区别](../experiments/discovery/instruction-necessity-20261115/README.md)：
原始评分/停止组件有共同扫描反例，SO-101实际双对象抬升见证与单目标/空动作对照已完成。
目前仅是有条件的测量失效证据；没有完整Isaac/VLA成绩复现、成熟策略排名改变或真机结果。
首选择/commit及oracle停止已有先例，独立核心贡献仍待查新深审，完整选题尚未完成。

进一步[近邻与停止路径复核](../experiments/discovery/instruction-necessity-followup-20261115/README.md)
已核2018 DONE规范、2026 shortcut/同episode复评研究。具体共同扫描与这些近邻有区别，
但现有证据尚无独立核心增量；当前降为诊断工具、暂移出主推荐。
不继续堆同类反例或默认移植Isaac；重启须有完整协议下成熟策略结论变化与清楚贡献。

以下保留早期准备阶段记录；其中“等待 A100”“未跑模型”等状态不代表当前进度。

## 历史准备阶段记录

日期：2026-11-14。当前可以汇报“工程接口与文献准备进展”，还不能汇报 VLA 方法有效或查新通过。
用户要求：若核心查新不通过，应换方案。执行规则见 [路线决策](prior-art/ROUTE_DECISION.md)。
**第二轮裁决：当前 ECCBF 和两个宽泛替代方法均停止作为核心。**
现在推进的是 [有限观测研究草案](prior-art/EXPLORATION_PROTOCOL.md)，不是已确定的新算法。

## 已经形成的可审查材料

- [文献库](../references/README.md)、[研究现状](literature/RESEARCH_STATUS.md)、[近邻阅读卡](literature/READING_GUIDE.md)与实际检索记录。
- [汇报逐页提纲](report/PROGRESS_REPORT.md)、[相关工作准备稿](paper/RELATED_WORK_DRAFT.md)和[主张—证据表](paper/CLAIM_EVIDENCE_MATRIX.md)。
- 本地 SO-101 reset/RGB/六关节控制/基础几何判定与视频 smoke；这不证明自主抓取。
- [100 场景 metadata 审计](../experiments/so101/PROTOCOL_AUDIT.md)：只有 8 组物理 placements，两个 task_id 是一种任务模板。

## 不用 A100 仍应推进的事项

| 优先级 | 具体工作 | 完成判据 | 当前状态 |
|---|---|---|---|
| P0 | 中心机制查新与路线筛选 | 逐项说明近邻已做/未核实/可检验差异 | 四份独立深审已形成否决依据；目前没有可冻结的新机制 |
| P0 | 探索问题进入检查 | 核原文/代码有无同构污染研究，明确经典强基线 | 方案已有；并未执行模型/代码复现 |
| P0 | 真正的任务身份与覆盖 | 合法目标谓词、可达性、独立 reset/split manifest | 已定位伪跨任务/重复布局风险；尚待具体任务实现与可行性验证 |
| 历史暂停 | 旧 S 操作定义 | 作废计划提示可直接清理，不再作为默认科学实验 | 400/400精确文本还原已审计，不启动旧矩阵 |
| 历史暂停 | 旧 E 的扰动协议 | 不继续为旧四格方案开发专用 runner | 0/3步metadata仍未施加；工程时序日志需求保留 |
| P1 | evaluator 完整事件历史 | 抓取/抬升/释放、稳定保持和错目标计分 | 当前只有基础几何放置判定 |
| P1 | 真机可观察谓词与容差 | 同任务判定可由视频/相机和关节记录实现 | 不假定仿真物体坐标真值能直接在真机获得 |
| P1 | 无模型可行性与动力学量 | 典型布局可达、碰撞/夹爪几何、控制响应测量 | 场景可加载与动作响应已测；完整任务可解待测 |
| P1 | 论文图表证据合同 | 每图对应一条主张、数据字段、比较与不确定性 | 已在汇报和论文材料列明；不画假结果曲线 |
| P2 | 人工 Scholar 前向/后向追踪 | 阅读前五近邻的被引/相关论文并登记 | 本环境 Scholar 不可访问，提供逐题名入口；替代检索已做 |

这些是后续任务清单，不把写出清单当作已经实现。路线可能更换，先解决最高优先级的科学问题，避免为旧方案扩展大量专用代码。

## A100 到位后才能给出证据的事项

| 顺序 | 实际操作 | 要保存的证据 |
|---|---|---|
| 1 | 独立环境、权重加载、标准 baseline smoke | preflight、pip check、模型 revision、视频与原始 episode 结果 |
| 2 | SO-101 兼容策略核对与试跑 | 相机键/次序、关节顺序/单位、normalizer、动作 chunk 与实际控制响应 |
| 3 | 输入重放和语言正对照 | input hash、RNG/cache、同输入 raw action 不变性、可行不同指令的行为差 |
| 4 | 冻结探索协议后检验现象 | 接触/自由暴露、前后测、完整适配状态、全部失败与排除记录 |
| 5 | 只有简单强基线无法解释时再建新假设 | 同预算freeze/reset/hedging/replay、开发与确认隔离、资源成本 |

LIBERO/OpenVLA 能验证计算环境和辅助比较，但不能替代同 SO-101 研究主线。基础模型没有 SO-101 的
动作统计和任务能力时，优先解决适配/示教，不用失败轨迹包装“认知偏差”。

## 真机安排必须与科学问题绑定

采购/报销说明可先准备用途和组成：follower、可选 leader、同规格相机/支架、电源与控制器、打印件/夹爪、
标定板、相同红蓝物体/目标区。以官方 BOM 和购买时实际报价为准，本轮没有捏造价格或报销承诺。
来源：[SO-101 官方装配资料](https://huggingface.co/docs/lerobot/so101)。

仿真和真机必须共享目标谓词、干扰含义、相机/动作语义、冻结的模型/校准版本、超时和失败分类。
真机不是重新造一个简单演示：至少复现中心对比或直接测试新路线的核心预测；如果换方案，该中心对比一并更新。
当前没有权限/连接去部署真机，也没有真实设备参数；这些状态不能由本地准备材料补造。
