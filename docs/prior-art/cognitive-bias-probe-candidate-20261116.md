# 认知偏差探针基准：候选（未查新通过）

日期：2026-11-16。状态：**两个冻结 ACT 探针的试点结果 + 候选方向**；
不是新方法，不是立项，不是查新通过。

## 试点现象

同一官方 ACT checkpoint、同一载体/物理/谓词、fresh seeds：

| 探针 | 条件 | 成功率 | 关键量 |
|---|---|---:|---|
| 源位置偏移（12700–12719） | baseline | 19/20 | — |
| 源位置偏移 | 物体可见地 +20 mm | **1/20** | 19/20 夹爪更靠近**旧训练源**；4/20 距旧源 1.6–6.0 mm |
| 物体遮挡（12800–12819） | baseline | 17/20 | — |
| 物体遮挡 | 物体不可见、仍在标准源 | **0/20** | 16/20 完全未抬升 |

两条合起来是一个**分离现象**：

> 视觉是抓取的“存在门控”（看不见物体就不抓），但可见物体的**位置**没有被用来
> 更新抓取点（物体可见地移开，夹爪仍去训练源）。

这是一个可量化的失败模式，不是泛泛的“策略脆弱”。它对应原始文档中的
**锚定效应**（空间锚定）与 **WYSIATI/先验依赖**（视觉存在门控）两个探针。

## 候选方向

**面向 VLA/ACT 的认知偏差探针基准**：用受控任务变体测量
“看见但不定位”“看不见仍按先验行动”“频率偏差”“风险回避”等偏差，
每个探针给出**偏差特异指标**，而不是只用最终成功率。

### 试点指标

- `baseline_success`；
- `shift_success` 与 **anchoring index**
  `A = (d_new − d_old)/(d_new + d_old)`（>0 表示靠近旧源）；
- `hidden_success` 与 **presence dependence**（视觉缺失下的成功率下降）；
- 夹爪到旧源/新源的最小距离、抬升/放置失败类型。

### 可能的扩展探针

- **Availability/frequency**：训练源分布偏斜，测策略是否过度选择高频源；
- **Loss aversion/risk**：可恢复失败前的动作保守度；
- **Recovery**：偏移/遮挡后是否重新定位（需要闭环视觉/搜索）。

## 最近邻（必须先读）

1. **CorrectVLA: What Can One Sentence Fix? A Failure Taxonomy and a Minimal
   Language Correction for Frozen VLA Policies**（2026）——VLA 失败分类学与语言纠正；
   需要确认它是否已覆盖“空间锚定/视觉存在门控”的受控探针与指标。
2. **SO-101 failure/recovery benchmark**（arXiv 2606.08881v2）——真实 SO-101 的
   细粒度失败、semantic/execution 两层与 recovery rate；可能覆盖部分失败分类。
3. 域随机化/位置泛化/robustness 的 VLA 工作：需要确认“物体可见地移动后仍去旧源”
   是否已被报告为 positional overfitting，以及是否已有 anchoring index。
4. Causal confusion / copycat / object-centric bias：确认视觉存在门控是否已被解释。
5. 认知偏差在 HRI/机器人中的分类学：确认是否已有系统探针基准。

## 全文核查（2026-11-16）

### CorrectVLA（arXiv 2608.29967v2）

- 四类失败：task misunderstanding、perception failure、execution misalignment、
  multi-step planning。
- execution misalignment 的定义是“right target is reached but how far or how hard is
  miscalibrated”；源偏移属于 **perception/target failure**，不是它可一句话修正的
  execution misalignment。
- 它没有测“视觉存在门控 vs 空间锚定”的分离，也没有 anchoring index；但它的
  failure taxonomy 已覆盖“目标/感知错误”这一大类。

### SO-101 failure/recovery benchmark（arXiv 2606.08881v2）

- 真实 SO-101，评测 π0.5、SmolVLA、Wall-X、ACT；四个任务，20 episodes/model-task。
- 失败分类包含 **State Mismatch**（“policy continues executing subsequent actions
  based on an incorrect internal assumption without detecting or correcting the
  discrepancy”）、Grasp Instability、Precision Misalignment；还有 semantic/execution
  分解和 recovery 指标。
- 源偏移现象对应 **State Mismatch**；遮挡后不抓对应 **Grasp Instability**；
  已有真实平台、ACT 基线和 recovery 评测。

### 裁决

- 该候选最多是已有 failure taxonomy 下的**细粒度诊断**（presence vs localization
  dissociation + anchoring index），不是新的核心问题或新基准。
- 作为方向 **no-go**；不要构建 benchmark、不要训练。
- 若未来只作为诊断工具，必须明确它是 State Mismatch/Grasp Instability 的子类，
  不能声称新基准或新方向。

## 初步判断与风险

- **支持点**：两个探针给出了一个** dissociation**（presence vs localization），
  不是单一成功率；有明确的偏差特异指标；可用现有 ACT 载体低成本复现。
- **风险**：可能被审稿人视为“已知位置泛化/遮挡鲁棒性 + 认知偏差标签”。
  必须证明：
  1. 该分离不能被普通域随机化/数据增强基线解释；
  2. anchoring index 与最终成功率提供独立信息；
  3. 至少一个干预（如扩大源分布、视觉 servoing）只修正其中一个偏差，
     从而证明两个探针测的是不同机制。
- 当前只有一个策略/任务；作为基准需要至少第二个策略或第二个任务，
  否则证据规模不足。

## 下一步（未执行）

1. 读 CorrectVLA 与 SO-101 benchmark 全文，确认覆盖边界；
2. 查 positional overfitting / visual presence gating 的 VLA 近邻；
3. 若未直接覆盖：预注册一个小型基准（2 个探针 × 2 个策略/任务），
   加一个数据增强/视觉 servoing 干预，证明两个偏差可分离；
4. 若已覆盖：写 no-go，停止该候选。

**在完成上述查新前，不训练、不声称方向成立。**
