# 查新包（NOVELTY PACKAGE）

日期：2026-11-16（本地）。状态：**内部检索完成，外部权威查新未执行。**
本文不主张"空白"，只主张"在已检索范围内未发现同构工作"，并列出把它变成
可发表声明的剩余步骤。

---

## 1. 主张句（三档，投稿时按证据选一档）

**C-strong（若 E2 塌缩 + E0 预测都成立）**
> The success of a frozen visuomotor policy is predicted by one dimensionless number:
> the plan residual over the geometric grasp tolerance, `r/τ`.

**C-mid（若只有 E0/E4 成立）**
> A frozen imitation policy's failures are dominated by a repeatable, state-conditioned bias field;
> whether that bias can be compensated is decided by its type (geometric offset vs gating),
> not by its magnitude.

**C-soft（若只有审计流程成立）**
> A ~20-rollout audit yields a deployment envelope for a frozen policy, computable before execution.

三档的共同点：**产物是判据/协议/工具，不是网络。** 这一点决定了它不会掉进
"又一个 test-time corrector"的比较框架。

---

## 2. 关键词（供外部检索逐条粘贴）

组 1 · 误差结构
`policy error budget` · `systematic error of imitation policy` · `state-conditioned bias field`
· `repeatability vs accuracy robot policy` · `error decomposition behavior cloning`

组 2 · 容差
`grasp tolerance` · `tolerance-normalized failure` · `task tolerance margin`
· `success envelope prediction` · `tolerance-guided manipulation`

组 3 · 补偿边界
`compensability of policy error` · `correctable vs uncorrectable error robot`
· `gating failure vs geometric offset` · `boundary of test-time correction`

组 4 · 预测与审计
`deployment envelope` · `pre-deployment audit robot policy` · `failure prediction from first action chunk`
· `calibrated abstention robot`（**风险项**，2602.22474 可能已占）

组 5 · 认知框架
`anchoring effect robot policy` · `System 1 System 2 robot control`
· `cognitive bias visuomotor policy`（预期噪声大，只作框架引用）

中文（CNKI / 万方）
模仿学习 系统误差 · 抓取容差 · 误差可补偿性 · 部署包络 · 重复性与准确度 · 认知偏差 机器人操作

---

## 3. 已执行检索（本轮实际跑过的）

工具限制（已付代价，记录在案）：shell 无外网，只有 `web_fetch` 能出网；Semantic Scholar API 返回 429；
`web_search` 结果是不可排序的 PDF 碎片，**不能**作查新主工具。以下全部经 arXiv API / GitHub API 直查。

| 日期 | 源 | 查询 | 命中 | 判读 |
|---|---|---|---:|---|
| 11-16 | arXiv | `all:"systematic error" AND all:"visuomotor"` | 0 | 术语可能不同（bias/offset/drift） |
| 11-16 | arXiv | `all:"error budget" AND cat:cs.RO` | 1 | 2601.20776（T-RO，医疗持械，49/291 μm），非策略、非塌缩 |
| 11-16 | arXiv | `all:"grasp tolerance" AND all:"policy"` | 0 | 容差文献存在，但与 policy 组合为空 |
| 11-16 | arXiv | `all:"task-space error" AND all:"behavior cloning"` | 0 | — |
| 11-16 | arXiv | `all:"anchoring" AND cat:cs.RO` | 多 | 2107.03038、SAILOR 2303.08204 均为**感知锚定**，语义不同 |
| 11-16 | GitHub | `robot policy error budget` | 0 | 名字空位（弱证据） |
| 11-16 | GitHub | `test-time correction robot policy` | 1 | `afinitus/awesome-hill-climbing` |
| 11-16 | GitHub | `lerobot calibration so101` | 14 | `fport/so101-calibrator` 等，工程挂点 |

---

## 4. 最近邻逐条对账

| 工作 | 机制 | 它留下的剩余差 | 风险 |
|---|---|---|---|
| **2611.17658**（锚定/观测折扣） | 观测折扣 → 事后 α 低 ↔ 成功率低 | 只给机制，无补救、无定量预测、无容差 | 中（仅读摘要） |
| **RTCF 2608.04527** | 检索式 test-time 修正，PMA 对齐执行历史 | 无误差结构、无容差、无边界；+2% 量级 | 高（修正器簇） |
| **APEX**（NTU MARS） | 弥合 policy 指令与黑盒控制器执行差 | 需黑盒控制器；不产出"部署前可算的预测" | 高 |
| **Active Vision**（ICCAS 2026） | 主动移动相机对齐训练分布 | 只处理观测侧 | 高 |
| **2108.02303** tolerance-guided insertion | 把容差当策略输入 | 不审计冻结策略、无塌缩定律 | 中 |
| **2606.00383** BC-of-MPC | 报告严格容差下的精度差距 | 只报告现象，无定律、无预测 | 中 |
| **2606.08881** SO-101 failure benchmark | 失败分类学 | 分类不预测，无几何容差量 | 中 |
| **2601.20776** error budget（T-RO） | 医疗持械误差预算 49/291 μm | 单系统、非学习策略、无跨容差塌缩 | 低 |
| correction 簇（2608.29967 / 2611.15011 / CoC 2603.12480 / ORPA） | 各类修正器 | 都默认"修正总是好的"，不讨论边界 | 高（若以"修正"为卖点） |

**结论**：没有一条同时具备 (a) 容差归一化、(b) 跨容差塌缩、(c) 部署前预测、(d) 可补偿性二分。
四条里任意单独一条都有近邻；组合起来没有。这正是本方向必须**四条一起讲**的原因——
少一条就会被归入某个已有簇。

---

## 5. GitHub 版图（开源侧的空白在哪）

| 类别 | 代表 | 判读 |
|---|---|---|
| **修正/steering 目录** | `afinitus/awesome-hill-climbing`（2★，MIT，2026-11-09）| "last-mile improvement"（RL 微调、residual/steering、RECAP、人类纠正、test-time verifier）已被**命名成类**。不要再以"加一个修正器"为卖点 |
| **标定工具** | `fport/so101-calibrator`（MIT，2★）、`ayushgawai/so101-lerobot`、`TusharBajaj07/so101-lerobot-setup` | 工程挂点：审计可做成 LeRobot 的 deployment check 插件 |
| **审计/预算** | 无 | `error budget` / `tolerance audit` 在 LeRobot 生态里没有对应仓库 |

开源侧的空白在**审计**，不在**修正**。这决定了工具形态：`peb` 是一个"读 trace → 出 r/τ → 出审计卡"
的检查器，而不是控制器。

---

## 6. 待执行的外部查新（必须做，否则不能写成"首次"）

| 项 | 具体动作 | 判据 |
|---|---|---|
| Google Scholar | 上述组 1–4 共 14 条串，每条看前 2 页 | 出现"tolerance-normalized / deployment envelope / compensability"同构文献 → 降级 |
| IEEE Xplore / WoS | `repeatability accuracy policy`、`error budget manipulation` | 同上 |
| CNKI / 万方 | 4 条中文串 | 国内若有同题，需在引言中对话 |
| 引文网络 | 对 2601.20776、2606.00383 做前向/后向引文 | 找"误差预算 + 学习策略"的交叉 |
| 专利（可选） | 工业补偿类专利 | 只影响工程化章节，不影响论文新颖性 |
| 全文 | 2611.17658 全文（目前仅摘要） | 若它已给出容差或预测，直接冲击 C-mid |

诚实边界：**"名字为 0"不等于"问题未研究"。** "systematic error" 检索为 0 更可能是术语差异。
因此本轮结论只能写成"在 arXiv/GitHub 范围内未发现同构工作"。

---

## 7. 标题候选

1. *Tolerance-Normalized Error Budget Predicts the Deployment Envelope of Frozen Visuomotor Policies*
2. *Repeatable but Not Accurate: Systematic Error Structure and the Limits of Test-Time Compensation*
3. *When Can a Frozen Policy Be Fixed? A Compensability Criterion for Visuomotor Bias*

摘要一句话（英文，投稿用）：
> We show that a frozen visuomotor policy's success is governed by the ratio of its plan residual
> to the task's geometric grasp tolerance, that this ratio is computable before execution, and that
> compensation helps only for geometric bias — never for gating failures.

---

## 8. 与上一轮裁决的关系（必须写进稿件，否则等于无视 no-go）

上一轮排除的是"**精度/鲁棒性**"作为**目标陈述**。本文档的形态是：
不训练、不改模块、不换任务；测量的是**冻结策略误差的结构**，产物是**判据与协议**。
证据是 `r/τ` 的预测力（可被证伪的定量预测），不是"成功率提升 x%"。
若 E0 的留出 AUC < 0.80，本方向立即回到 no-go，不解释、不补救。

---

## 9. 2026-11-17 复核（第二轮内部查新）

**新增检索（本轮实际跑过的）**

| 源 | 查询 | 命中 | 判读 |
|---|---|---:|---|
| arXiv | `abs:"tolerance" AND abs:"frozen" AND cat:cs.RO` | 8 | 无一条做"容差归一化 + 冻结策略审计"；最接近的是 Auriga（运行时容差检查） |
| GitHub | `"error budget" robot policy` | 0 | 与 11-16 一致；名字空位仍在 |
| arXiv | `abs:"deployment envelope"` | 1 | 仅 2605.02801（LLM 多智能体 RL），非机器人；机器人侧 0 |
| arXiv | `abs:"compensability"` | 17092 松散命中 | 引号未生效，前 5 条全为 AGI 评价/多准则决策/剪枝，无机器人策略；**只记"未发现"，不记"0 命中"** |
| arXiv | `abs:"grasp tolerance" AND abs:"policy"`（11-16 已跑） | 0 | — |

**全文级核对（上一轮遗留项）：2611.17658**

摘要页已核对：该文测得 `α = V/(V+s²)`（V 为策略自身的本体锚方差，可一次测出）后，
**在任何 rollout 之前**预测成功率（diffusion/Can 两个新噪声水平，误差 0.03，95% ±0.08），
并明确写下：**"training noise predicts it equally well"**。

- 风险：由"中"上调为 **高（形态层面）**——"部署前预测成功率"这个卖点已被它占住。
- 它没有的：几何容差 τ、跨尺寸塌缩、可补偿性二分；且是单任务、感知噪声轴。
- 对本文的约束：(a) 不能单卖"预测律"，必须带几何 τ 与边界；(b) 审稿人会照它的标准问
  "δ 不也能预测吗"——我们 E1′ 的 ΔAUC CI 含 0 已诚实承认，答案只能落在塌缩与二分上。

**新近邻 2：2610.06921《Learned Corrector vs Simple Retreat》**

冻结 π0.5、3,888 配对、同种子 placebo 重跑；结论：学习修正的增益大量来自基策略自身波动，
脚本化"退回"在两个轮次内与学习管线无可测差异（等价判据未持续满足）。

- 对 E5′ 的直接约束：**必须加 placebo 重跑 + 脚本化退回**两个对照，
  否则"补偿有效"会被归因为抖动。
- 它占的是"修正是否值得"，不是"何时可补偿"；前提条件仍可讲，但不能宣称"我们让成功率提升"。

**新近邻 3：2611.01112 Auriga**

agent harness 在执行中检查**声明的阶段容差与抓取边界**，越界即停并把差异回传。
→ 容差已作为运行时准入判据出现；"拿容差当阈值"不再是新颖点。

**新近邻 4：2610.17114 D-World**

世界模型修正仅在残差不超过容差时被接受——容差是**接受判据**，仍在闭环修正框架内，非冻结策略审计。

**本轮结论（内部）**

四元合取（容差归一化 / 跨容差塌缩 / 部署前预测 / 可补偿性二分）在 arXiv + GitHub 检索范围内
仍无同构工作；但"预测律""容差检查""修正边界"三个子形态在 2026-10/11 均已出现强近邻，
**单独任一条都不足以支撑新颖性**。这反过来确认 C-mid 的写法：四条一起讲，
且 E5′ 必须带 placebo 与退回对照。

**外部查新待办（不变，需你账号）**：Google Scholar 组 1–4 共 14 条串、IEEE Xplore / WoS、
CNKI / 万方、对 2601.20776 与 2606.00383 的引文网络。
