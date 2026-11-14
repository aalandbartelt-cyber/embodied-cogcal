# TPSC 本轮 go/no-go（阶段状态）

结论：**Go：本地载体训练。No-go：当前进入 TPSC 方法实现。** 后者由证据尚缺导致，不表示候选已被科学否证。

**公式更正：**已调用固定 BAS-VLA 源码核算：旧 toy 逐步 hinge 求和为2.0，而同一轨迹按展平 chunk
求距为0；公开 artifact 又确实是 per_step / legacy。后续必须明确两种布局与完整目标，不能默认
“前作会逐时刻推开整个 chunk”。正损失也不等于非零更新或任务伤害。详见
[`tpsc-loss-fidelity-correction.md`](../../../../../docs/prior-art/tpsc-loss-fidelity-correction.md)。

| 问题 | 实测证据 | 当前判定 |
|---|---|---|
| 原未提交资产是否已保全？ | `af47281`，原 degree-assumption SHA256 不变；review 单列限制 | 是 |
| 5070 Ti 是否能运行 SmolVLA？ | 指定 carrier 实际视频解码；严格加载 450M 权重；99,880,992 参数产生有限梯度 | 是，入口 smoke |
| 有限 action chunk / 时延 / 显存？ | `[1,50,6]`；一次推理约0.316s；torch峰值分配1.46GB；单次前反向16.38s含冷启动 | 是，非长期统计 |
| 普通训练是否可行？ | batch=4 的20-step资源试跑完成并保存checkpoint；固定20k基线已启动 | 进行中，完整20k未完成 |
| learned policy 是否能完成 TPSC 左右任务？ | 未获得完整20k checkpoint后的20条物理rollout；carrier只有green→container单任务 | 未验证 |
| learned policy 是否共享正确前缀？ | 只有scripted任务结构；自然场景RGB也随目标变化；独立分叉时刻未标定 | 不可判定 |
| uniform separation 是否伤害前缀？ | 尚未进行统一分离干预或匹配训练预算对照 | 未测试 |
| 是否实现 outcome-conditioned support？ | 当前能力、机制和查新条件均未齐全 | 暂不实现 |

后续固定读取20k最终checkpoint，先20条manifest能力试验；不挑best seed/checkpoint。若策略不会做任务或适配未验证，记录载体未就绪；不得把失败归因于TPSC。
夹爪全六通道degree→rad仍是明确记录的模拟载体假设；相机top/front到本项目视角的标定未验证。后续rollout即使执行，也只作带这些限制的能力screen。

已保存：原始失败日志、成功CUDA smoke JSON、环境版本、asset SHA256、20-step训练日志。20k原始日志在同目录持续写入；其是否仍运行必须通过进程/会话核实，不以本页替代运行状态。
