# ECCBF 查新与证据链审计（2026-11-13）

## 审计结论

当前 ECCBF 主张仍有可保留空间，但只能把创新收紧为一个非常具体的机制假设：

> 在同一本体、同一任务和匹配初始状态下，语言—观测冲突对动作的影响会随执行条件改变，
> 其交互项可以被识别，并且交互项校准能带来任务成功率提升。

“认知偏差探针”“语言—视觉冲突”“冻结 VLA 残差补偿”“SO-101 仿真—真机”分别都已有
近邻。查新目前支持的是“交互项定义 + 因子实验 + 选择性校准 + 同一本体验证”的组合性
科学命题，尚不足以支持“首次提出具身认知偏差”或“首次做 SO-101 仿真—真机”。

正式查新不能由一次网络检索保证；本文件用于在 A100 实验前冻结风险，不替代学校或机构的
正式科技查新报告。

## 逐项重叠风险

| 近邻 | 已覆盖内容 | 对 ECCBF 的风险 | 必须保留的差异 |
|---|---|---|---|
| [ICBench](https://arxiv.org/abs/2603.06001) | LIBERO 上控制语言—动作耦合的 OOD 指令矛盾，验证 VLA 的视觉偏置 | “语言冲突导致动作错误”本身不能作为新问题 | 不把冲突诊断当主贡献；测量冲突×执行条件交互，并以成功率恢复为主结果 |
| [LIBERO-CF](https://vla-cf.github.io/) | 同一视觉场景下替换可行语言任务，并提供 CAG 缓解方案；已含仿真和真机 | “反事实语言探针 + 纠偏”高度重叠 | 不重新构造语言冲突基准；使用四格匹配设计，并显式估计 `b_int` |
| [LIBERO-Plus](https://openaccess.thecvf.com/content/CVPR2026/papers/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR_2026_paper.pdf) / LIBERO-Pro | 多维扰动、位置偏置、语言/视觉/环境变化诊断 | 单纯扰动基准或偏差排行榜已拥挤 | 把现有基准作为外部对照，避免新建泛化 benchmark |
| [BAS-VLA](https://nebulis-lab.com/BAS-VLA/) | 冻结 VLA 上的任务语义动作校准、选择性证据门控和残差校正 | “冻结策略 + 动作校准 + 成功率提升”不能单独作为创新 | 必须加入语义项、执行项和交互项的因子分解，并比较无交互项加法校准 |
| [CorrectVLA](https://correctvla.github.io/) | 失败分类和最小语言纠正映射为冻结 VLA 的动作偏置，含真机验证 | “语言纠正→动作偏置”与普通语义校准近似 | 不依赖事后人工句子；使用预登记、运行时可观测分数和匹配条件 |
| [RAGu](https://arxiv.org/abs/2611.10894) | 检索引导、几何校准、跨域和跨本体 VLA 适配 | 跨域几何校准和真机迁移已出现 | ECCBF 的语义校准参数从仿真冻结，只重新估计本体变换；不使用轨迹检索作为主方法 |
| [SO-101 Bench](https://arxiv.org/abs/2610.36420) | SO-101 Isaac 数字孪生、真实 SO-101、仿真—真机排名一致性 | “SO-101 数字孪生 + 真机”已经被系统研究 | 不声称数字孪生本身创新；将其作为同一本体平台，核心放在偏差交互项和校准效应 |

## 可保留的核心主张

### 主张 A：机制层

保留“具身条件化交互项”作为核心假设，但必须满足：

- 四个条件使用相同 `task_id + scene_id + seed` 配对；
- 语义冲突和执行扰动分别可控；
- `b_int = a11 - a10 - a01 + a00` 在至少一个 held-out 任务上有稳定方向；
- 交互项的置信区间和效应量被报告；
- 移除交互项后性能显著下降，证明它不是普通残差的重命名。

### 主张 B：结果层

任务成功率必须是第一主结果：

- ECCBF 相比 Raw 在受扰任务上提高至少 10 个百分点；
- ECCBF 优于 semantic-only、execution-only 和 additive calibration；
- 正常任务保持率下降不超过 5 个百分点；
- 至少一个任务不参与校准拟合，仍保持提升方向。

### 主张 C：外部效度层

SO-101 真机可以支持“同一本体外部效度验证”，但不能单独证明通用 sim-to-real：

- 真机复用相同任务定义、条件命名、动作接口和校准接口；
- 语义校准参数在真机测试集上冻结；
- 只允许重新估计相机/本体变换；
- 报告真实延迟、动作误差、安全停止和失败原因。

## 必须补的对照组

仿真完整矩阵应包含：

1. Raw VLA；
2. generic reflection/re-prompt；
3. fixed global residual；
4. semantic-only calibration；
5. execution-only calibration；
6. additive calibration without interaction；
7. ECCBF interaction-aware calibration；
8. placebo calibration（随机方向或错误符号）；
9. oracle upper bound（仅诊断，不作为部署方法）。

如果外部方法代码和接口可复现，至少增加一个 BAS-VLA 或 CorrectVLA 对照；如果无法做到，
必须报告不可比原因，不要把论文数字直接横向比较。

## 必须补的证据

- **效应存在性**：四格 Pilot 不只看平均成功率，还要保存动作序列和失败原因；
- **排他性**：证明 ECCBF 不是 generic reflection 或 fixed residual 的等价实现；
- **非劣效**：中性任务性能不能通过牺牲正常能力换取；
- **跨任务**：至少一个完全未参与校准的任务；
- **跨条件**：未见冲突强度或未见执行扰动；
- **真机一致性**：仿真中交互项的方向在 SO-101 上至少保持方向一致；
- **负结果边界**：交互项为零、校准不提升或真机方向反转时，必须停止强主张。

## 明天 A100 前可完成的查新任务

1. 把上述近邻逐篇加入 `prior-art-matrix.md`，补充年份、代码、任务、真机和校准位置；
2. 对每个近邻记录一个“最接近实验”和一个“不可比点”；
3. 在正式运行前冻结 `claim-boundary.md`，禁止使用“首次”“填补空白”；
4. 为每个对照组建立可复现的 `calibration_variant` 名称；
5. 选定一个主模型和一个 SO-101 兼容模型，避免模型切换造成额外查新问题；
6. 为四格 Pilot 写下预登记表：任务、seed、episode 数、成功率主指标、交互项公式、
   排除规则和停止规则；
7. A100 只运行环境冒烟和 Raw baseline，不在环境未通过前扩展探针或校准方法。

## 投稿时的安全表述

推荐表述：

> We study whether language–observation conflict effects in a frozen VLA depend on execution
> conditions. We introduce a matched factorial protocol that estimates semantic, execution,
> and interaction components, and evaluate an interaction-aware action calibrator on a shared
> SO-101 simulation–real setup.

避免表述：

- “first cognitive-bias benchmark for VLAs”；
- “first action calibration method for frozen VLAs”；
- “solves VLA visual bias”；
- “general sim-to-real guarantee”。
