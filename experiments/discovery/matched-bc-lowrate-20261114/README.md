# 匹配SO-101物理任务的普通BC能力检查

**结果：teacher 32/32；固定最终2000步BC在20个预定测试seed上0/20成功、0/20抬升。**
没有达到执行前规定的16/20能力门槛。不能据此论证TPSC、补偿伤害或新失效机制。
此检查移除了公开SmolVLA载体的单位/相机/任务不匹配，但没有证明当前小BC足以完成任务。

协议：[执行前计划](../../../docs/plans/2026-11-14-matched-bc-capability-screen.md)。
代码：`../matched_bc/`。固定外部源：FERBIN12/so101-manipulation-eval
`b02b8b2e300733dbe76cead4f3a57425c37955fe`，含指垫与摩擦修改，未做真机标定。
官方第三方XML、原TPSC manifest与原接口summary均未改。
35mm是基础抓放资格门槛，不是机械臂定位精度成果或精密操作指标。

## 数据与运行

- 单任务：初始source `[.2,-.075,.014]m`附近±5mm，goal固定 `[.2,.075,.014]m`。
- 24训练episode（4100–4123）、8验证episode（5100–5107），不采集测试示范；
  20个测试episode为6100–6119，每条285命令、9.5s仿真时间。
- 双相机128×128、5Hz；实测q历史8步、30Hz控制；预测30步、执行6步。
  输入仅RGB/q，指令恒定，不声称语言理解。真值只在teacher/evaluator使用。
- teacher由30Hz零阶保持重新资格检查后采集；全部32条成功，无失败样本丢弃。
  大数组在被忽略的 `data/discovery/matched-bc-lowrate-20261114/`，逐条SHA在collection中。
- 普通CNN/MLP chunk BC、412292参数，seed42、batch64、Adam lr .001、固定2000步最终权重。
  `training/updates.jsonl`中的验证误差仅首个验证episode前256帧，不能称完整验证集误差。
- checkpoint：`checkpoints/matched-bc-20261114/final-2000.pt`，SHA256
  `f49da6e9c82c55a2478bf580e049365fbde3e3bd8bff2a8fc1bfcbe33a23e237`。
  训练更新用时24.05s、阶段总用时52.23s；训练CUDA峰值分配709101568 bytes，不代表全管线峰值。

首次全30Hz图像采集的单条成功记录仍在 `../matched-bc-20261114/`，
软件渲染耗时183.50s后主动SIGINT；未混入本轮。EGL实际为Mesa llvmpipe。
本轮关闭阴影/反射/雾只影响渲染，物理未改；采集阶段295.64s，正常退出0。

## 闭环结果与解释边界

原始数据：`test/episodes.jsonl`，每episode全部命令、q与查询chunk在各自trace中。
20条均完整执行285命令，共5700命令、960个chunk。
成功0/20；双指且抬升最长时间均为0，全部失败原因为未建立双指抬升。
总计2828个命令向量发生限幅；episode平均绝对跟踪误差的均值0.06889rad。
不把帧或chunk作为独立重复，不将限幅2828次解释成2828个独立失败。

从首条trace可见策略早期偏离teacher，随后无法完成下降抓取。
这只是定位线索：尚未区分小模型欠拟合、闭环分布偏移、近静止阶段的观测混叠等原因。
teacher成功不推出任意学习器都会成功；低离线MSE不推出闭环任务能力。

原始流水线 `pipeline-events.jsonl` 三阶段均exit0，systemd服务已正常结束，
不存在需重复启动的未完成训练。
冻结失败权重的验证集执行长度诊断放在独立相邻目录，不改写这20条结果或挑选best checkpoint。

`evidence-audit.json`已逐条核对32份数据hash/形状/图像年龄、20条测试与16条val诊断的
chunk执行索引/限幅/完整q历史、7份运行源码hash及3份受保护原始文件。
复核命令（输出须为新路径）：

```bash
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/miniconda3/envs/cogcal/bin/python \
  experiments/discovery/matched_bc/audit_screen.py --out /tmp/matched-bc-evidence-audit-fresh.json
```

## 对选题的决定

**此BC能力载体未就绪，暂不运行执行补偿干预，不实现新方法。**
研究方向仍待近邻差异和合格策略上的机制证据。
下一步只允许先定位能力问题；任何改动都需新协议、新记录，以及新测试集或明确验证集诊断身份。
