# 初始RGB颜色特征＋普通GRU BC：15/20，未过资格门槛

[执行前计划](../../../docs/plans/2026-11-14-initial-visual-feature-bc.md)
在看到前一carry11/20后写下；使用新测试seed8100–8119，固定2000步最终权重。
**完整成功15/20，双指抬升19/20；4例放置失败、1例未抬升。**
没有达到16/20门槛，不把15四舍五入成通过，不放宽35mm放置或释放条件。
按计划停止进一步微调此小模型架构，转回载体/数据选择与研究问题审查；补偿干预未运行。

输入只为当前双RGB、实测8步q历史、从episode初始RGB提取并缓存的6个固定颜色特征。
无时间/phase/物体或goal真值；只在train24条上计算初始特征统计，沿用train-only q/action统计。
网络是普通GRU BC，投影层多6个输入，285956参数；固定颜色/相机和单一任务，不声称通用VLA或新方法。
双相机5Hz、控制30Hz、chunk30执行6、285命令预算及全部物理/成功条件与原匹配载体相同。

权重 `checkpoints/anchor-bc-20261114/final-2000.pt` SHA256：
`c73f669e7e8f8d74bb37fdef463d00e20a7a35887bdcd9ddea06415ee9cc2dc7`。
训练CUDA峰值分配364711424 bytes、更新用时17.58s；不是全管线峰值或实时控制指标。
采样索引hash与前一GRU对照相同，但表示/参数/测试初态不同，新旧15/20与11/20不能当纯记忆因果效应。

所有20条和960查询chunk保留于 `test/`；共5700命令、43限幅向量。
平均episode跟踪误差0.006824rad不代表定位精度或任务能力。物理模型仍未真机校准。
`grasp-diagnostic.json`只做离线FK，不能证明感知失败根因。
`pipeline-events.jsonl`训练/测试正常exit0，服务 `cogcal-anchor-bc-20261114.service`已结束。
绑定源码未修改，证据核验见相邻recurrent目录 `evidence-audit-v2.json`。
