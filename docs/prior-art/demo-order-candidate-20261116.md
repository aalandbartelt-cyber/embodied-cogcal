# Demonstration-order bias：候选（已 superseded，no-go）

> **状态（2026-11-16 17:30）：已 superseded，no-go。** 本文件保留候选形成时的
> 记录，不再代表当前判断。独立只读审计发现：训练器从第 1 步起在全部 6,840 帧上
> 均匀采样，episode 存储顺序只重标固定的随机索引流，不是 curriculum/primacy/
> recency；24 条等长 episode 不改变相位序列；reverse/random 引用的旧
> `train_order.py` 正文未保留，存在 provenance gap；单侧 p=0.0352 对应双侧
> p=0.0703，合并 Fisher p=0.0145 是事后合并，不是确认性检验。**不要预注册
> order-robust 训练，不要再用 12900–12919。** 当前判断见
> [`../DEMO_ORDER_MECHANISM_20261116.md`](../DEMO_ORDER_MECHANISM_20261116.md)、
> [`demo-order-scan-20261116.md`](demo-order-scan-20261116.md) 与
> [`../../experiments/discovery/demo-order-audit-20261116/README.md`](../../experiments/discovery/demo-order-audit-20261116/README.md)。

日期：2026-11-16。原状态：reverse/random 20k 训练进行中；不是方法/方向/查新结论。

## 假设

同一 24 条演示、同一 normalizer、同一 seed、同一 20k 更新和最终 checkpoint，
只改变演示在训练集中的顺序（canonical / reverse / fixed random permutation），
ACT 的成功率或行为是否改变？这是 **primacy/recency-like data-order bias**。

## 试点状态

- canonical（现有官方 checkpoint）在 fresh seeds 12900–12919：**17/20**。
- reverse / random 两个 20k 训练于 10:47 并行启动；预计 12:10 左右完成。
- 预注册：`experiments/discovery/demo-order-20261116/PREREG.md`。
- 评估：`rollout_order.py`；分析：`analyze_order.py`；结果将写 `RESULT_ORDER.md`。

## 最近邻（需读全文）

| 工作 | 年份 | 关系 | 可能覆盖 | 未必覆盖 |
|---|---:|---|---|---|
| Curriculum Offline Imitation Learning (COIL) | 2021 | 离线 IL 的 curriculum/experience picking | 按难度/回报选择训练经验 | 同一演示集合的**顺序置换**；primacy/recency |
| SGD order/generalization 文献 | 2017– | 采样顺序影响优化/泛化 | 随机顺序、噪声、泛化 | 演示级顺序对 BC 行为/任务成功的影响 |
| Curriculum learning surveys | 2020– | 训练顺序/课程 | 从易到难、数据排序 | 同一数据的 reverse/random 置换 |
| Behavior cloning robustness / dataset bias | 2019– | 数据分布/质量 | 数据质量、分布偏移 | 演示顺序作为独立变量 |

本轮标题/摘要级检索**未找到**直接研究“同一演示集合、仅改顺序、对 ACT 任务成功/行为影响”的工作；
但这不是查新通过，且 SGD 顺序效应是已知的，必须谨慎区分“优化噪声”与“可复现的演示顺序偏差”。

## 判定（待结果）

- 若 reverse/random 与 canonical 的成功率差 ≥2/20，或最终误差分布明显分离，
  报告 data-order effect；再查是否已有直接工作，并考虑作为**数据顺序鲁棒性**诊断。
- 若三者统计上不可区分，报告 order invariance，停止该线。
- 不训练新方法；不声称认知理论或新算法。

## 风险

- 20k/24 episodes 的样本小，成功率差异可能是噪声；需要配对 seeds 和重复训练。
- 顺序效应可能只反映 SGD 优化噪声，不是“认知偏差”；必须用固定 seed/数据/预算
  和多顺序重复来区分。
- 即使有差异，也可能只是 **优化超参数/数据量** 的结果，不能直接外推到 VLA 或真机。
