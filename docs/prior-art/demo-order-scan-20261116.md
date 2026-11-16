# Demonstration-order / data-order effect：初步检索（未完成查新）

日期：2026-11-16。状态：初步扫描，不是 go/no-go，不是方向结论。

## 问题

同一批 24 条示教、同一 normalizer/seed/20k/最终 checkpoint，只改变训练集中
episode 的顺序（canonical / reverse / random permutation），ACT 的成功率或
placement precision 是否改变？这是 primacy/recency 类的 data-order 探针。

## 试点（进行中）

- canonical（既有官方 checkpoint）：17/20，最终误差均值 26.58 mm。
- reverse：13/20，最终误差均值 32.92 mm；相对 canonical 少 4 个成功。
- random permutation：**13/20**，均值 32.26 mm；与 reverse 同分但失败 seeds 不同。
- 配对统计：canonical vs reverse McNemar p=0.1445、t p=0.121、Wilcoxon p=0.154；
  canonical vs random McNemar p=0.1719；均不显著。初始 chunk L1 0.0031–0.0035 rad；
  训练/验证损失几乎相同。
- **同环境 canonical 重训：19/20**（官方 canonical 17/20）；reverse/random 各 13/20。
  canonical-retrain vs reverse/random McNemar 均 **p=0.0352**；合并 canonical
  36/40 vs 非 canonical 26/40，Fisher **p=0.0145**；官方 vs 重训 p=0.3125
  （run-to-run 差 2/20）。
- 释放误差 canonical 3.59 mm vs reverse 4.36 mm；释放后位移 26.98 vs 32.77 mm，
  差异主要在返回阶段。
- canonical 是既有 checkpoint，不是同环境重训；正差异可能含训练噪声。

## 检索记录

- Google Scholar：前序 403/429。
- arXiv API：2026-11-16 精确短语查询遇到 429/timeout，未取得结果。
- OpenAlex：`demonstration order imitation learning robot`、`data order behavior
  cloning robot`、`primacy recency robot learning demonstrations`、
  `curriculum learning imitation learning demonstration order`、
  `sample ordering stochastic gradient descent generalization`、
  `training data order vision language action`。
- 未读全文、未做引用追踪、未查 GitHub。

## 最近邻（标题级）

| 工作 | 年份 | 关系 | 覆盖 | 未必覆盖 |
|---|---:|---|---|---|
| Curriculum Offline Imitation Learning (COIL) | 2021 | 数据/课程顺序近邻 | 从混合质量数据按课程挑选经验 | 同一批示教的 permutation；ACT/VLA |
| SGD order/generalization 文献 | 2017– | 一般训练顺序 | 样本顺序影响优化/泛化 | 机器人示教级顺序；成功/placement 指标 |
| Curriculum learning surveys | 2020– | 课程顺序 | 由易到难/数据组织 | 固定示教的 reverse/random 顺序 |
| Continual/sequential imitation | 2018– | 任务顺序 | 灾难遗忘/持续学习 | 同一任务内 episode 顺序 |
| Data-centric AI / data ordering | 2020– | 数据顺序 | 样本排序、去噪、重加权 | ACT 的 episode 顺序与 placement 精度 |

## 初步判断

- 标题级检索没有找到直接研究“同一批机器人示教、只改 episode 顺序，对 ACT/VLA
  成功率或 placement precision 的影响”的工作；但 SGD/课程/持续学习已覆盖一般
  “顺序会影响训练”的观念。
- 若 reverse/random 与 canonical 的差异可被同环境 canonical 重训复现，
  贡献只能是**数据顺序偏差的测量与训练协议**（如每 epoch 重排 episode），
  不是新架构；审稿人可能视为训练噪声/超参数问题。
- 若三者相近，则是 order-invariance 负结果，不构成方向。

## 下一步

1. random 已完成 13/20；canonical-retrain **19/20**，官方 canonical 17/20。
2. 统计：canonical-retrain vs reverse/random McNemar p=0.0352；合并 canonical
   36/40 vs 非 canonical 26/40 Fisher p=0.0145；官方 vs 重训 p=0.3125。
3. 这是**顺序效应候选**，不是方向：canonical 顺序或与数据收集/难度相关；
   `order-robust training`（每 epoch 重排/多顺序聚合）方法很简单。
4. 先读 COIL、SGD order、curriculum/continual 近邻全文；再做 per-seed 示教属性、
   难度、最后 batch/source-position 机制分析；若没有超出 curriculum/SGD 的增量，
   写 no-go。
5. 若候选成立，先预注册更多 orders/seeds（不是 12900–12919）和 order-robust
   训练对照，不直接训练。
