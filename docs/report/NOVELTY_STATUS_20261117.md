# 查新执行记录与新颖性判定（2026-11-17）

对象：`DIRECTION_ANCHOR_AUDIT_20261116.md` 定义的唯一保留候选——"示教支撑决定定位增益曲线，支撑外增益亏缺可在输入侧补偿"。

本文件只回答一件事：**这个方向现在能不能过查新**。结论先行：**不能声称通过；但也没有找到直接覆盖**。三通道（Scholar / arXiv API / Semantic Scholar）本轮全部失效，可用的 OpenAlex 与 GitHub 只做到短语级与标题级排除，做到的是"没有被撞上"，不是"证明没人做"。

## 1. 实际执行的检索（可复现命令即 URL）

| # | 通道 | 检索式 | 命中 | 判定 |
| --- | --- | --- | --- | --- |
| 1 | OpenAlex fulltext | `imitation learning spatial generalization demonstrations` | 10,432 | 噪声大；前 3 为 SFCrP（ICRA 2026，arXiv 2602.10594，场景流条件化、跨实例空间泛化）、IL 泛化保证（Ren 2020）、BC-Z。均不把示教空间支撑当自变量 |
| 2 | OpenAlex title+abstract | `"demonstration support"` | 260 | 前 10 全为无关义（软件演示、食品救助、装备论证）。**该短语在机器人学习中未被使用** |
| 3 | OpenAlex title+abstract | `"input remapping"` | 9 | 全部为 VR / 神经科学 / IoT，无机器人策略学习。**该术语在领域内空缺** |
| 4 | OpenAlex fulltext | `"input remapping" imitation policy` | 6 | 无关；最近义为特权教师→学生策略的输入变换 |
| 5 | OpenAlex fulltext | `test-time adaptation visuomotor policy distribution shift` | 3,239 | **命中机制近邻**：Agentic Test-Time Control for Robust Visuomotor Diffusion Policies（2026）、UMI-on-Air: Embodiment-Aware Guidance（ICRA 2026，26 引）、Domain Adaptation of Visual Policies with a Single Demonstration（ICRA 2024）、Gated Memory Policy（2026） |
| 6 | OpenAlex fulltext | `"insufficient adjustment" robot` | 99 | 全为手术/康复/设计固化；唯一沾边者为机器人设计决策中的 design fixation（DETC 2023）。**Kahneman 式偏差进入机器人学习的通道基本空着** |
| 7 | Semantic Scholar API | `visuomotor policy spatial generalization`；`demonstration coverage ...` | — | HTTP 429（两次），未取得数据 |
| 8 | arXiv API（export.arxiv.org） | `abs:"demonstration support" AND abs:imitation` | — | 30 s 超时；http→https 跨域重定向被拒 |
| 9 | Google Scholar | `"demonstration support" imitation learning robot` | — | 被重定向到 www.google.com，工具不跟随跨域重定向，未取得结果页 |
| 10 | GitHub repo search | `imitation learning spatial coverage` | 0 | — |
| 11 | GitHub repo search | `robot precision compensation` | 1 | 1 星 PID/摩擦补偿仓库，无同类研究代码 |
| 12 | OpenAlex title+abstract（AND，按引用排序） | `coverage` ∧ `demonstrations` ∧ `imitation` | 90 | 前 15 无一篇以"固定条数下的覆盖宽度"为自变量：AirExo-2 是采集硬件、RoboWheel 是数据引擎、instruction augmentation 改的是指令。**变量级空缺得到支持（弱）** |
| 13 | DuckDuckGo HTML | `"demonstration support" visuomotor policy gain` | — | HTTP 202 + 人机验证（选鸭子），无结果 |
| 14 | Bing | 同式 | 96,400 | 返回亚航值机页面，检索式未被尊重；记为渠道失效 |

访问受限的三项（7–9）记为**渠道失败**，不充作覆盖证据；沿用 11-16 的同一判定口径。

## 2. 近邻对比：它们变的是什么，我们变的是什么

| 工作 | 改的东西 | 与本候选的差别 |
| --- | --- | --- |
| UMI-on-Air（ICRA 2026） | 推理期给具身无关策略加"具身感知引导" | 引导的来源是具身差异，不是示教空间支撑；不测增益曲线 |
| Agentic Test-Time Control（2026） | 推理期用 agent 增强扩散策略鲁棒性 | 无支撑变量、无补偿律；属通用鲁棒化 |
| Single-Demo Visual Domain Adaptation（ICRA 2024） | 单条示教做视觉域适应 | 变的是视觉域，不是空间覆盖宽度 |
| Gated Memory Policy（2026） | 上下文记忆与适应 | 无支撑—增益关系的可测曲线 |
| SFCrP（ICRA 2026, 2602.10594） | 场景流条件化跨实例泛化 | 泛化对象是物体实例，不是位移幅度 |
| 2611.17658（本体锚） | 噪声维度上的读数权重 α=V/(V+s²) | 已核：$s=0$ 时 α=1，对位移无定义，见审计报告 §1 |

"推理期改输入"这一族已被 2024–2026 的工作占满，**不能**把"输入侧适应"当新颖点。可辩护的差异只剩三点同时成立：①自变量是示教空间支撑宽度（同一示教条数下变化）；②产出是实测增益曲线 $g(\delta)$ 及其塌陷位置，而不是成功率数字；③补偿是可由该曲线直接算出的重映射，且在支撑内不退化。三点缺一，就退化成上述近邻的重新包装。

## 3. Kahneman 绑定与工业补偿类比的位置

- 机制绑定：策略把本体锚 $m(C)$ 当先验、按斜率 α 向当前读数调整，α<1 即"调整不足"（anchoring and insufficient adjustment）；$g>1$ 的远端读数更像"回归均值"方向的过度外推。**绑定只用于解释 $g(\delta)$ 的形状来源，不作为新颖性主张**——心理学概念本身不构成贡献。
- 类比绑定：工业机器人的位置相关误差图 + 软件补偿，对应"支撑外亏缺是系统性、位置相关的偏差，可标定后补偿"。类比提供的是**方法与评价口径**（先测误差图、再补偿、补偿后需验证不破坏已覆盖区），不是新理论。

## 4. 判定与去留

| 项 | 状态 |
| --- | --- |
| 短语级新颖 | 空（`demonstration support`、`input remapping` 在领域内均无对应用法）|
| 机制级新颖 | **被占**（推理期输入适应已有 4 篇 2024–2026 近邻）|
| 变量级新颖 | **未发现覆盖（弱证据）**：查询 12 的 90 条中前 15 无一篇以"固定条数下的支撑宽度"为自变量测 $g(\delta)$；只覆盖标题+摘要层 |
| 综合判定 | **部分通过**——只有把主张收缩到"支撑→增益曲线→可算补偿"才成立；不能主张"输入侧适应"本身 |

因此方向不去掉，但表述必须按 §2 的三条同时成立来写；任何一条在 P0/P1 中被否，方向即降级为"诊断/测量工具"而非方法贡献。

## 5. 未跑完的检索与重跑条件

- 需在可用网络下补跑：`"gain" + "demonstration support"`、`"policy" + "under-tracking"`、`"spatial generalization" + "demonstration spread"`、`"coverage" + "demonstrations" + manipulation`、`"error map" + "policy"`。
- 渠道：Semantic Scholar 有 key 后重试；arXiv 走 `arxiv.org/list` 或本地镜像；Scholar 走学校网络（本机验证页不可绕）。
- GitHub 侧仍需查：官方 ACT 仓库的 chunk 执行、indy7 覆盖实验，确认无同款重映射；本轮两次查询均为 0/1 命中，不构成排除。

## 6. 与平台决策的关系

本候选不需要新采购（复用 SO-101），与 17:55 选定的 B2（触觉/力传感，1 万元）不冲突也不自动取代。若 P0/P1 在仿真内否掉本方向，回退顺序为：B2 平台按原计划推进；本方向的测量口径（三层增益 + 协议闸门）保留为诊断工具。

## 7. 下一步（按成本排序）

1. 复算 5 mm 位移点（P0 前置），成本最低，且决定 P1 是否直接失败。
2. P0 协议闸门：遮挡/无位移对照 + 同 episode 后续 query 归一化。
3. P1：$|\delta|\le5$ mm 时 $g_\mathrm{plan}$ 是否 ≈0.9–1.0。
4. 三项都过，再补 §5 剩余检索式，此时才可写"查新待确认（渠道受限）"以外的表述。
