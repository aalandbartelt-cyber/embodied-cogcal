# B 路线：ECCBF 具身条件化认知偏差场

## 主张

本路线的核心创新不是“测量—建模—补偿—验证”这条工程闭环，而是检验：

> VLA 的语言—观测冲突偏差会随机器人本体和执行条件改变；这种交互项可以被识别，
> 并用于提高受扰任务成功率。

任务成功率是第一主结果，偏差交互项是机制证据。完整定义见
[CORE_HYPOTHESIS.md](CORE_HYPOTHESIS.md)。

## 主实验链

1. **同一本体仿真**：SO-101 MuJoCo/MJCF 数字孪生。
2. **同一策略接口**：SO-101 兼容 SmolVLA/LeRobot 策略，策略在校准阶段冻结。
3. **四格因子任务**：语义中性/冲突 × 标准/扰动执行。
4. **因子化校准**：分别估计语义项、执行项和交互项。
5. **真机复现**：在 SO-101 follower 上使用相同任务定义、动作接口、主指标和对照逻辑。

OpenVLA/OpenVLA-OFT 作为 LIBERO 次级对照，不作为 SO-101 同体主证据。这样可以避免
把 VLA 本体不匹配误判成认知偏差。

## 对照组

Raw VLA、通用反思、固定动作残差、语义单独校准、执行单独校准、无交互项加法校准、
ECCBF、随机伪校准和 oracle 上界。仿真使用完整矩阵，真机至少保留 Raw、语义单独、
执行单独、加法校准、ECCBF 和伪校准。

## 主要门槛

- 查新矩阵不能发现同时覆盖“语义×执行交互 + 选择性动作校准 + 同一本体仿真—真机”的近邻工作；
- ECCBF 相比 Raw 在受扰任务上提高至少 10 个百分点；
- ECCBF 优于无交互项加法校准；
- 正常任务性能下降不超过 5 个百分点；
- 至少一个未见任务保持提升方向；
- SO-101 真机复现相同任务和相同校准接口。

如果交互项不显著，改写为“语义—执行误差分解与校准迁移”；如果真机无法及时到位，
仿真结果仍可独立形成投稿包，但不得声称真机验证已经完成。

## 关键文件

- `configs/so101.yaml`：模型、仿真、真机和指标配置；
- `probes/definitions/eccbf_factorial.yaml`：四格匹配 episode 定义；
- `analysis/contracts/calibration_v1.yaml`：统计和排除规则；
- `src/cogcal/metrics.py`：因子效应、成功率和 Wilson 区间；
- `src/cogcal/calibration.py`：冻结 ECCBF 动作校准器；
- `analysis/scripts/summarize_runs.py`：从 JSONL 生成汇总表。
