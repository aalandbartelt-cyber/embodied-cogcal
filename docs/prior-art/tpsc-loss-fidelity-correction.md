# TPSC 关键更正：先确认损失布局，再谈共享前缀伤害

2026-11-14。结论：**撤回“旧 toy 已给出针对 BAS-VLA 的一般反例”的解释；TPSC 仍未立项。**
这是公式与固定源码的 CPU 核算，没有训练新策略、没有测得机器人失败或成功率变化。

本轮按 ieee-experiment 的 baseline / overclaimed-results / audit 和 ieee-citation 的
citation-logic / preprint / closest-prior-work / authoritative-only 路由核验。

## 1. 前作实际约束什么

[BAS-VLA v2 §3、§4.2、C.2](https://arxiv.org/html/2609.23650v2) 将输出定义为单步动作或
action chunk 向量，分离项是

\[
L_{sep}=[m-\|B-C\|_2+\|U-C\|_2]_+.
\]

其中 C/U/B 分别是同一观测和上下文下的 clean/control/break 输出。
[固定源码 training.py](https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts/blob/51f0dab5b2edab6539f3bccda7a04b3cb1d52a6c/bas_vla/breaking/training.py)
按最后一个坐标轴求 L2，再对 records 求平均；
[官方训练说明](https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts/blob/51f0dab5b2edab6539f3bccda7a04b3cb1d52a6c/docs/training.md)
明确允许单步向量或显式展平的 chunk，要求不要混用布局。

因此不能把“对每条记录施加 margin”直接写成“对 chunk 内每个时刻施加 margin”。
代码里的 `paper_three_component` 和 `legacy` 也不是同一目标：后者还含 expert-margin 和 anchor。
本次核算使用前者，m=0.5 只为复核旧 toy，不是前作默认 m=0.15 或公开权重 m=0.3。

公开 [OpenVLA/LIBERO-10 artifact](https://huggingface.co/Shuaijun/BAS-VLA) 的固定 revision
`d5e05c8b74bc8d8f1a831151a432f73158831f85` 元数据确实是 `per_step` / `legacy`。
**这意味着逐步版本仍是合法比较对象，不能因 chunk 反例更正就把它移除。**
但该公开权重是 7D OpenVLA 离线动作约定，不能直接加载到 SmolVLA 的 SO-101 六关节接口。
其配置与来源哈希见 [source-contracts.json](../../experiments/so101/tpsc-loss-fidelity/source-contracts.json)。

## 2. 实际运行的固定源码核算

原 [shared-prefix-separation-audit.json](../../experiments/so101/shared-prefix-separation-audit.json) 保留不改。
令 C=U=(1,1,1,-1,-1,0)，B=(1,1,1,1,1,0)，m=0.5。

| 输入布局 / 条件 | 源码分离项 | 对完全共享的前三坐标的直接梯度 | 能支持什么 |
|---|---:|---:|---|
| 一个展平 6 步 chunk | 0 | 0 | 后半段距离 √8 已满足 margin，旧 toy 不构成这一布局的冲突 |
| 同样 6 步作为 6 条单步记录 | 1/3；求和为 2.0 | 0 | 复现旧 toy 的数值，但前作默认是 records 平均，且正损失不等于非零更新 |
| 整个 chunk 都在分叉前，C=U=B=(1,1,1) | 0.5 | 0 | 相同输出有正损失；PyTorch 在零范数点选择零次梯度 |
| margin 活跃、前缀完全相同，分叉差只有 0.05 | 约 0.42929 | 0 | 活跃 hinge 也不必直接推动完全相同的前缀坐标 |
| 前缀已有 0.01 差异、分叉差只有 0.05 | 约 0.42720 | 最大约 0.13736 | 非零小差异可以得到分离梯度；仍未证明会降低任务成功率 |

这些梯度针对 IdentityAdapter 的**输出坐标**，不是共享神经网络参数；网络参数耦合、imitation、
anchor、优化器和噪声仍可能改变前缀。零梯度结果不证明实际训练永远无伤害，正损失也不证明必然有伤害。

另核算固定每步差 0.1 时，展平 L2 随 H 为 0.1√H；H=1/4/25/50 的 hinge 分别为
0.4/0.3/0/0。同一个数值 margin 对不同 horizon / normalization 并不具有相同作用强度。
这先要求公平校准基线，不能立刻命名成新方法。

可重跑入口是 [audit_tpsc_loss_fidelity.py](../../scripts/audit_tpsc_loss_fidelity.py)，
结果是 [source-loss-audit.json](../../experiments/so101/tpsc-loss-fidelity/source-loss-audit.json)。
脚本先核对上游三个文件的 SHA256，再调用真实 `compute_losses`；所有计算在 CPU 执行。
它含数值和 autograd 断言，不加载上游权重或运行上游训练程序。

## 3. 候选支持定义也要更正

旧稿写“同一当前动作在两个任务下的未来损失分布相近，则支持保持”，这个条件不充分。
最小反例：任务 A 要放左边、B 要放右边；动作 drop 对两任务的损失均为 1，
但 A 的可行动作为 {left}，B 的为 {right}，共同可行动作集合为空。
相同的失败不能充当共享正确动作证据。

后续若研究支持，至少要区分：

- 同一当前状态下，执行候选动作后，两个任务分别存在成功续接的证据；
- 任务条件下的可行当前动作集合是否有交集，以及估计不确定性；
- “允许共用”与“必须输出相同向量”：前者不推出后者，多模态正确路径仍可不同。

这只是修正问题定义，不是一个已提出的新算法。viability、行为等价与世界模型近邻仍需审计；
不能把集合记号本身作为创新。

## 4. 当前主张—证据门槛

| 主张 | 必须有的证据 | 现有证据 | 缺项 / 风险 |
|---|---|---|---|
| learned policy 在两个任务上共享正确前缀 | 任务能力、共同输入条件、独立可行前缀或分叉标定、episode 配对 | scripted 路径结构；普通 carrier 训练在运行 | 无目标任务能力；Critical |
| 忠实 BAS 目标伤害正确前缀 | 明确 per_step/flattened_chunk、完整损失 preset、动作归一化、匹配预算的有/无分离对照与结果 | 本页 CPU 公式 / 梯度核算 | 没有 learned-policy 干预；Critical |
| outcome-conditioned support 有新意和优势 | 成功续接而非等损失、强简单基线、REFACTOR-VLA 等最近工作对照 | 只有修正后的证明义务 | 不实现新机制；Critical |
| SO-101 能同体复现该现象 | 相机 / 零位 / 动作契约与物理抓取能力均验收，同一任务谓词 | 数据 / 模型下载及 CUDA 链路通过 | 相机与夹爪来源未验证；Critical |

后续顺序：先完成固定 20k 载体训练与 20 条能力 screen；若载体未就绪，优先解决载体，
不从失败抽取 prefix 伤害。只有能力和共享正确前缀成立，才在**两种明确记录的损失布局**下
检验分离干预；手工逐步强分离不得冒称完整 BAS-VLA。

若忠实基线无可重复伤害，停止该 TPSC 方法主张，保留可复用载体和失效分析资产。
这不意味着已找到通过查新的替代方向，完整选题目标继续 active。
