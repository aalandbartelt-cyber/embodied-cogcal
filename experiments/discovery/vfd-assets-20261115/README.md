# VFD线的可行性与近邻后续裁决

2026-11-15。承接[四阶段解析检查](../vfd-quadrature-20261115/README.md)。
**裁决：当前VFD路径误差线降为待核机制线索，移出主推荐；本轮没有确定新的研究方向。**
完整目标仍是有实质查新增量、可实现，并在SO-101仿真和真机检验同一命题。
本轮新增的是版本核对和实际公开记录资格检查，不是新增算法、训练或策略成功率复现。

## 为什么降低优先级

1. 上轮数值结果仍成立，但经典求积和充分优化已能解释/解决部分现象。
2. [UQ当前v2](https://arxiv.org/html/2606.18043v2)仍明确Gaussian OT条件和learned场近似；
   C.7已有评分flow-time子集消融，不能把少取节点或选后期时间当新核心。
3. [CFM/NLL分析](https://arxiv.org/html/2608.28010v1)§6.2/A.5已用反对称旋转场保持整个高斯边缘分布，
   同时改变CFM比率。其目标不是直接VFD，但“路径代理变化不代表末端分布变化”的一般原理已有直接近邻。
4. 本次未取得同数据独立训练且任务能力已验证的SO-101 flow ensemble，也没有测得评分引发的任务损失。

这些结论不证明该研究空间不存在，也不是正式查新报告；它们不足以支持继续以当前构造立项。
不再增加纯解析反例或从原先0/20载体中解释VFD风险。

## 公开资产的有范围核查

| 入口 | 本轮实际取得/读取 | 能支持什么 | 尚缺什么 |
|---|---|---|---|
| `learnsyslab/uq_vla` bcc2433；论文v2 | 新读v2 §4/A.2/§7/C.7，与已固定代码说明对应 | 确认定理/近似与既有节点消融边界 | 官方说明不提供ensemble checkpoint或实机代码；不是现成SO-101载体 |
| `mcobzarenco/flow-matching` ebaa8e0 | 固定tree、README、架构/真机runbook的相关段落；两个HF模型库metadata与一份model card | 确有公开raw checkpoint入口及作者的低显存推理测量 | 本轮未验证匹配的独立flow训练成员、任务评估/场景；多draw与AR seed不是所需ensemble |
| `Advaitic/drishti` eeaaaf4 | 固定源码、许可证、SQLite数据库及tree；运行本项目只读审计 | 检查公开telemetry字段/标签/完整性 | 不含完整chunk/ODE序列、独立ensemble及可绑定的原策略hash；不能直接重算VFD |

Bijou两个HF库固定metadata revision分别为`2578852b026b4812d32125c6f3060d08490db676`
和`0806a456b58c11d17a7183f8e72de55e08bdf818`。
其低显存测量来自作者runbook，不是本机复现或训练内存下限；架构文档的主要指标是open-loop MAE。
第二个模型库根README请求404保留在来源记录中，不由此推断整个模型库不可用。
本轮没有下载任何策略权重、安装或执行上游代码。

## Drishti数据库：真正读到的范围

[下载前资格计划](data-contract-plan.md)先于数据库读取保存。
`obs.db`经Git blob SHA1/字节数核对，SQLite只读打开、完整性检查为ok；读取前后SHA256相同。
原始第三方数据库仅留在data忽略目录，不复制入本项目公开仓库。

[完整结果](recording-contract.json) / [审计程序](audit_recordings.py)：

| 核查项 | 实际值 |
|---|---:|
| 全部run / step | 63 / 4,607 |
| 原始成功 / 失败标签 | 35 / 28 |
| 有embedding文件的run（仅核tree，未下载embedding） | 60，标签34 / 26 |
| embedding文件数 / 保留图像行 | 756 / 546 |
| 保留图像的run | 6 |
| 六维q / 六维执行action | 均4,607步 |
| action-head mean/std | 805步，均32维摘要 |
| 成功标签且少于20步 | 7 |
| 声明步数不符 / 非连续step-index | 0 / 0 |

模型字符串分两类：20条`smolvla_ft@4500 (nas=6)`、43条`smolvla_ft@4500 · Fleet 1`。
这些是记录中的字符串，不是训练seed、权重hash或两个模型成员。
所有63条的`t`都等于step index，不能当真实秒数计算控制频率/预警时长。

原始源码hook对action head在chunk维求mean/std，且每个denoise step覆盖上次结果；
保存的32维摘要不保留完整chunk、生成时间或在同一点交叉求值的速度场。
因此不能从它恢复VFD，也不能当多次采样分歧。

录制源码的成功谓词只检查物体xy进入区域且z<6cm，没有持物抬升、释放及接触时长条件。
数据库不含逐步cube pose/contact，故本轮只能统计原标签，不能独立复算物理抓放成功。
接续[初态诊断](initial-zone-crosscheck.json)发现3条成功标签仅1步，记录初态xy已在当前谓词区域。
这是读取后的诊断，不作预注册确认；初态xy已被round且缺z，历史完整状态不明，不改写原标签。
当前录制源码已经说明并限制此类spawn，但不能据当前代码倒推出所有历史记录的采集版本。

README的0.995 AUC是作者结果；作者也明确标注含样本内拟合/评分。
本轮未重训检测器、复算AUC或把它当held-out性能。
该数据仍有离线记录检查价值；它未提供我们需要的合格VLA ensemble或物理成功因果证据。

## 其余近邻与下一动作

[FlowEval](https://arxiv.org/html/2611.11650v1)的附录A.2已具体记录：
将笛卡尔示范事后改为测得的下一关节状态，会弱化/破坏部署差异检测；不能再把
“重建标签与真实控制命令不同”或“用hold-position强对照”作为本项目新发现。
本轮只定向阅读其摘要、方法目录和A.2等相关段落，不声称复现或全文审阅。

SO-101 Bench此次检索再次命中，但仓库此前已有原文/Isaac资源审查，不算新发现，也不重复移植。

下一轮恢复**具体任务失效问题发现**，最多同时深审两项。优先选能用现成观测、动作与任务后果
检验的问题；将最近邻的直接方法、强简单基线和同题真机测量放在启动新训练之前。
若再考虑VFD，必须有真实任务决策代价和超出既有理论/传统对照的增量证据；当前资产检查不满足。
不把“没有取得公开权重”写成科学问题不存在，亦不因工程成本替用户选一个缺乏创新的题。

## 保存和复核

来源URL、固定revision、读取范围对应hash在本目录`*-sources.json`及`*-source.json`。
完整架构文档虽缓存，但仅上述相关段落用于判断；缓存存在不等于全文已读。
第三方原文/源码/数据库都留忽略目录；本项目仅提交自身审计、来源元数据和结论。

```bash
/home/mary/miniconda3/envs/cogcal/bin/python \
  experiments/discovery/vfd-assets-20261115/audit_recordings.py \
  --out /tmp/drishti-contract-fresh.json
```

输出必须为新路径；缺缓存或hash不符明确失败，不自动换成上游新版本。
