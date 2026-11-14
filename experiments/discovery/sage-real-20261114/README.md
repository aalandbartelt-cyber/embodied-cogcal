# 公开 SO-101 执行轨迹：能支持什么研究判断

2026-11-14。**只读数据资格检查；不是本项目真机实验、VLA 失效或查新通过。**
它服务于“找到有核心增量、可实现、同题仿真—真机的研究方向”，不单独构成研究方向。

源为 [SAGE 固定 revision](https://github.com/isaac-sim2real/sage/tree/5b31cfa35416d1300b5099557049bd8e9cb4507d)。
在查看误差前，从目录中选定 pick_place、backlash_detection、actuator_bandwidth 三类记录；
这是本轮读取的选择顺序，不声称公开预注册。50 个可用目录名、12 个文件的 revision/hash/缓存位置在
[source-inventory.json](source-inventory.json)。原始文件仅留在被忽略的数据目录，未复制进公共仓库。

## 实际结果

| 记录 | 行数 | 描述性中位采样率 | 五个机械臂关节逐行 q−command RMSE（rad，按源关节顺序） |
|---|---:|---:|---|
| pick_place | 4,840 | 49.85 Hz | 0.02172 / 0.05339 / 0.03149 / 0.02147 / 0.00832 |
| backlash_detection | 6,000 | 49.85 Hz | 0.02087 / 0.04742 / 0.04181 / 0.02603 / 0.02489 |
| actuator_bandwidth | 6,000 | 49.85 Hz | 0.01733 / 0.05403 / 0.05207 / 0.02339 / 0.01946 |

合计 **3 段记录 / 16,840 行**。行数不当作独立重复数。结果与自有脚本 hash 在
[trajectory-audit.json](trajectory-audit.json)，不是动作补偿前后对照。
夹爪单独按归一化位置计算，不能混入五轴 rad 指标；电流换算值也不当作标定力传感器。

## 测量限制直接影响选题

三段记录的命令/状态时间戳逐行完全相同。当前固定源码的采集器先发送、再串行读取各电机，
把两者都标为循环起始时刻；但尚未证实历史记录由这版采集器生成。
因此，这里没有估计机械纯延迟，也不能把逐行残差全归因于机械参数。
这不排除在额外时序/系统假设下拟合有效输入—输出动态；它限制的是物理、发送和读取延迟的分别归因。
源码范围见 [SAGE / GapONet 来源审计](../../../docs/prior-art/nvidia-so101-sage-gaponet-audit.md)。

没有配对仿真输出、RGB、策略 chunk 或成功标签；pick_place 的目录名不证明抓放成功。
所以没有计算 sim-real gap、任务失败率、补偿收益或 VLA 认知偏差。

## 本轮 go / no-go

- **Go：**这些数据可作历史执行建模的离线资格入口；有明确固定来源，值得在具体问题成立后使用。
- **No-go：**不从残差大小推出任务损害，不用它证明“补偿破坏阶段线索”，不凭该数据启动新神经补偿方法。
- **查新影响：**SAGE / GapONet 已有直接执行测量和学习补偿近邻；一般仿真假失败审计也有 SimuGuard。
  具体范围及访问限制见 [后续近邻核查](../../../docs/prior-art/execution-evidence-followup.md)。

研究方向仍未确定。下一项能改变立项判断的结果，应是具体任务损害、可检验的触发条件和超出强简单对照的证据，
而不是更多数据文件、训练轮数或新方法名称。

## 可复核命令

使用含 NumPy 的分析环境，输出必须是新路径：

```bash
/home/mary/miniconda3/envs/cogcal/bin/python \
  experiments/discovery/sage-real-20261114/audit_trajectories.py \
  --out /tmp/sage-real-audit-recheck.json
```

该脚本先核对全部 12 份本地源文件 hash，再检查时间单调、字段形状、有限值及逐行匹配。
缓存不在时会明确失败，不下载替代版本。
