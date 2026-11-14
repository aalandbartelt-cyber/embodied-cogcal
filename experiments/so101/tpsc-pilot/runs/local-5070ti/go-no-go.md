# TPSC 一页 go/no-go：最终20k与原20条pilot

2026-11-14 20:44后。**载体未就绪；不进入TPSC方法实现，不扩展120条。完整研究选题目标仍active。**
本次结果不能否证TPSC，也没有支持其立项或查新通过。

| 选题门槛 | 实测结果 | 裁决 |
|---|---|---|
| 本地是否能跑普通SmolVLA？ | RTX5070Ti Laptop，batch4、seed42，训练状态20000；正常结束日志 | 可运行 |
| 策略是否会做当前任务？ | 原20条全部执行；任务成功0/20，抬升0/20，放置0/20 | 载体未就绪 |
| learned policy是否共享正确前缀？ | 10对首chunk均距0.202309–1.080547rad；均失败；必要分叉时刻未知 | 不可识别 |
| uniform separation是否造成实际伤害？ | 没有运行分离干预或匹配训练对照 | 未测试 |
| 是否值得立即实现outcome-conditioned support？ | 能力、机制、强对照和查新条件均未满足 | 当前no-go |

固定精确`020000/pretrained_model`，未挑best；权重SHA256：
`af89ed56d0d804ac0acdd1ee7ed4008d8ec3ad4a24e7fa5fea6330c9dda6f257`。
原训练受轮次中断影响，从最近完整18k恢复optimizer/scheduler/RNG至20k；采样器位置不恢复，
故不声称逐位复现不中断轨迹。batch4×20k约1.33数据遍历，不等同官方batch64×20k。

全部20条/10对、600个chunk、6000个控制目标已核验。55个目标向量被裁剪；实测q每10控制步记录，
每对初始q相同，首次实测q差异只能定位到(0,10]步。RGB和语言同时变化，不能单归因于语言。
每episode平均chunk推理耗时的中位数0.254276s；推理时仿真暂停，30Hz只是仿真时钟。
loss是flow速度回归；此前1.46GB显存仅单次smoke，本次没有全程峰值记录。

优先排除：公开单任务green→container与本项目红物体/中文左右任务的分布差异、相机标定、
关节零位与夹爪约定、teacher接触/抓放能力。当前不能将失败归因于某一项。
原物理teacher在25次单初态debug后仍不合格，不能提供成功续接标签。

科学更正：[忠实损失布局](../../../../../docs/prior-art/tpsc-loss-fidelity-correction.md)、
[共同支持不强制相同动作](../../../../../docs/prior-art/tpsc-support-identifiability-correction.md)。
逐步hinge与展平chunk不同；正loss不等于前缀梯度或任务伤害。存在正确共享动作也不代表
分离的两个动作一定错误。后续至少比较普通BC、同数据池配对BC、完整BAS preset、合理margin、
阶段控制与多模态合法动作，不能以单teacher偏离为损害。

下一步仅在合格任务上验证具体失效机制，再决定方法；不以增加训练预算替代选题判断。
ECT配对优化机制可继续深审，通用antithetic flow噪声已有机器人近邻，尚无新算法结论。

证据：[全部pair表](pilot-20k-prefix-report.md)、[原始episode](pilot-20k/episodes.jsonl)、
[轨迹完整性核验](pilot-20k/completed-run-audit.json)、[checkpoint](pilot-20k-checkpoint.json)、
[冻结日志与hash清单](completed-evidence-inventory.json)。大模型和数据留本地忽略目录，原始JSONL不覆盖。
