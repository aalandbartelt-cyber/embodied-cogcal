# 从实际部署失败恢复问题发现

2026-11-15。上一轮ed2f5b3完成了近邻与停止路径复核，属于改变下一动作的实际进展。
完整研究目标未完成，本轮不恢复已降级的扫描评测、VFD解析扩展或小BC微调。

本轮先审公开SO-101失败的证据资格，再决定最小机制实验：

1. 区分工程接口错误、作者未验证的报告与真正可复核的任务失败。
2. 新发现LeRobot #5082：先检查issue/评论/PR实际资产和因果证据；
   不将“换stats后动作幅度增大”直接等同任务恢复，也不把普通固定normalizer写成创新。
3. 新发现Warp最新v4（11月4日）：不能引用已改写v1的强表达。
   读取其真实SO101任务与控制器条件，比较已有Translation/Affine/MLP/强随机residual对照。
4. RoboColosseum的SO101分阶段失败仅用于发现具体任务入口；
   作者失效分析不等于我们的因果机制或已复现数据。检查公开同任务资产，而非假设可直接加载。
5. 同时深审至多两个具体问题。若最近邻/强简单对照已解决，直接换问题；
   不以更多文档/工程代替独立贡献，记录能够改变后续判断的证据。

目前仅完成来源缓存与限定章节读取，未启动新训练、策略推理或物理实验。

## 中途决策证据

- GitHub API实际只有5条#5082评论，没有搜索摘要所述10月26日作者“确认恢复”的评论；
  本轮不采用该摘要的因果结论。已读PR #5091明确只加warning，量化验证为synthetic numpy，
  未运行SmolVLA全管线，不能由PR将故障机制判为已证实。
- Warp已核最新v4，原v1强表达已改为有条件结论；其SO101任务是2mm间隙peg insertion，
  50在线episode训练与20评估，控制baseline是base-action-conditioned随机residual，
  不能用简单确定性平移冒充其真实硬件对照。
- 它明确保留elementwise/per-timestep限制，但一般多维flow/动态补偿已有近邻，
  不从作者一句限制直接发明新算法。
- 本地旧SmolVLA完整chunk已保存，可作只读幅度/processor绑定审计；
  不改stats、不换checkpoint、不启动训练，也不从0/20归因于当前任何候选。

本轮分析轴：control / reproducibility / overclaimed-results / audit，沿用IEEE实验证据技能。
本地只读复算已完成：20episode、600查询、30000预测行、6000控制行；
8组pre/post action/state mean/std均与数据stats转float32后完全一致。
原大权重仅流式SHA核对，没有导入模型或执行推理。幅度较窄不等于已识别的因果机制。

公开新任务入口已固定RoboColosseum SO101代码revision
`7733d412f45d634c10c297a9e86adcf7085d8162`；
cube-drawer pi05 `003b28426c9d5446ae7a636d5829763b2c89f104`、数据
`5d07c27a375fadc57132b76d2c13b3864a438e25`。
源码要求至少24GB GPU、真实SO101；不当本地12GB/MuJoCo已验证入口。
数据metadata为so_follower，不单凭该字段确认SO101同体。
