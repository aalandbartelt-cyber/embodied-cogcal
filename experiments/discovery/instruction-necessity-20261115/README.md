# 多个可行目标，不等于评估过程需要语言

2026-11-15。**新得到原始评分组件的反例和SO-101物理共同轨迹见证；尚未确定研究方向。**
完整目标仍是核心贡献经有范围查新支持、可实现且同题仿真—真机可验证。
本轮先检查失效机制，不实现新VLA或把简单评分修正当新方法。

## 这次具体发现了什么

同一场景有A/B两个可行动作、指令唯一指定其中一个，仍不保证完整评估必须读取语言。
如果策略固定依次完成A再B，而评估分别在指定目标首次成功时停止，那么同一个无语言策略
可能在两条指令下都成功。即使统一时域，只要仍按“目标曾经完成”累计，现象也可以保留。

这并不意味着额外操作总是错误。若任务允许先操作其他对象再完成目标，共同轨迹可以合法。
准确的问题是：**这样的成功率不能单独证明策略依赖语言。**
多候选的静态任务描述与整个轨迹/验收过程的可区分性，需要分开检查。

### 证据一：固定源码组件

固定[HorizonRobotics/RoboOrchardSim](https://github.com/HorizonRobotics/RoboOrchardSim/tree/f2e041e5fabe354c1398ea97c934f603bb65d14d)
revision `f2e041e5fabe354c1398ea97c934f603bb65d14d`（2026-10-22），Apache-2.0。
在CPU原样AST加载`PickTask.build_validator`、`Validator`、`MetricStore`、相关selector和checker suite。
只有物理checker改接显式布尔事实适配器，不改评分规则；没有安装Isaac或加载VLA。

[执行前设计](PLAN-component.md) / [完整结果](component-results.json) / [程序](probe_components.py)：

| 候选数 | 共同序列 | 原始累计success通过目标数 | 末时刻所有当前条件同时成立的目标数 |
|---|---|---:|---:|
| 2 | 正序 / 反序 | 2 / 2；2 / 2 | 各1 |
| 3 | 正序 / 反序 | 3 / 3；3 / 3 | 各1 |
| 6 | 正序 / 反序 | 6 / 6；6 / 6 | 各1 |

每个候选依次提供15步reach、4步contact、4步grasp、4步lift；两候选之间2步全false。
每组所有目标用**同一条**事实序列，仅替换评估绑定，不是每个目标重编一条策略。
单目标正对照只让对应目标成功；no-op和reach-only没有终态success。
14/15步reach-dwell边界符合源码，未绕开时间门槛。

源码当前普通pick使用4个阶段、每阶段0.25，论文v1 §3.4则是Reach/Lift各0.5。
**本结果针对固定代码，不把两个版本的数字混同，也不声称复现原论文成绩。**

### 证据二：原始episode loop

[执行前设计](PLAN-loop.md) / [结果](loop-results.json) / [程序](probe_loop.py)。
另原样加载`Evaluator._step_episode`，用相同受控事实和递增动作index适配器：

- 正序扫描在A绑定下24步成功停止，B绑定下53步成功停止；反序互换。
- 强制统一56步但保留累计success，两个目标仍都成功。
- 简单首个完成对象匹配只能接受两个目标中的一个。

这证明固定评分/loop组件容许上述机制；完整环境的相机、接触检查、其他终止条件并未执行，
因此不能将其升级为整个Isaac benchmark已被物理策略攻破。
固定时域对照仅隔离停止时刻，不等于一套完整修正协议。

### 证据三：SO-101真实接触的物理共同轨迹

[物理执行前设计](PLAN-physical.md) / [完整结果](physical/summary.json) /
[实际模型与源码绑定](physical/contract.json) / [全部记录审计v2](physical-audit-v2.json)。
固定外部carrier `b02b8b2e300733dbe76cead4f3a57425c37955fe`，沿用已检查的指垫与接触参数。
显式scene override新增第二个同尺寸/质量/物理参数的立方体；原始官方及外部XML未改。
A/B初态为`(.2,−.075,.014)`和`(.2,+.075,.014)`m，间隔15cm。
已有特权IK事先生成“接近—夹紧—抬高—保持—放回—打开—回HOME”的时间序列。
运行时只发送固定关节命令，不读取语言、目标评分或物体真值。
物体真值仅供预先规划和独立结果记录；不能称RGB/q learned policy。

物理完成要求双指接触、物体高于初态5cm连续至少0.5秒，穿透不超过1.5mm。

| 固定序列 | 控制数 / 时长 | A最长双指抬升 | B最长双指抬升 | 首完成对象 |
|---|---|---:|---:|---|
| A→B | 462 / 15.4s | 1.241s | 1.241s | A |
| B→A | 462 / 15.4s | 1.241s | 1.241s | B |
| 仅A | 231 / 7.7s | 1.241s | 0 | A |
| 仅B | 231 / 7.7s | 0 | 1.241s | B |
| no-op | 462 / 15.4s | 0 | 0 | 无 |

共5条、1,848个命令，限幅0；最大物体—机器人穿透约0.117mm，物理rollout无物体pose写入、mocap或weld。
正向A/B首次满足物理完成门槛分别为4.744s/12.444s，反向互换。
最终两物体均已放回桌面，当前持物条件均false；不能把末状态单纯持物规则当不改变任务语义的万能修正。
单目标动作及全部物理状态与对应scan前缀逐字节相同。

这5条是确定性可行性见证，**不是5个随机独立重复、VLA成绩或真机结果**。
完整生成与执行在全新目录重复，命令、结果、全部物理trace逐字节一致；这验证可复现性，不增加统计n。
独立审计也检查所有控制时钟、命令、穿透及控制率的连续双指抬升记录（每次37样本）。
本MuJoCo的双指接触判据不等同Isaac原始ContactChecker的力/反向法向判据，不能跨引擎直接替代。

## 一个必要的判据，以及它不是什么创新

设同一初态下的指令随机变量为L、评估为S，定义给定预算下最好的无语言策略分数
`B = sup_{π不读取L} E[S(π,L)]`。若存在共同轨迹使B=1，即使目标各不相同，满分也不能说明读过语言。
这是标准信息价值/共同策略的推理，不声称新定理；本轮见证只覆盖上述组件和本地物理任务。

若明确限定一次互斥的首选择，且L独立于无语言策略可见的初态/随机数，则无语言正确率
至多为最大目标先验概率；均衡N目标为1/N。这要求真正互斥、明确处理并列和额外交互。
它是简单强对照，不能把收紧评分写成新算法，也不能把有限策略搜索所得下界当全策略上界。

## 查新已经排除了哪些宽泛贡献

| 一手近邻 / 已读范围 | 覆盖与本项目边界 |
|---|---|
| [InstructMove v1 §3.1–3.4/4.3/5](https://arxiv.org/html/2608.22990v1) | 已有多可行候选/唯一语言目标、同场景换指令和阶段评分；4.3明确target成功可早停。不能重新提出“语义任务对/加distractor” |
| [One Word v2 §III/V](https://arxiv.org/html/2609.05260v2) | 已有固定物理候选、严格动作/集合/顺序匹配、语义保持/变化和原子—组合对照。严格首选择/commit不是空白 |
| [Inner Monologue §4.1](https://sermanet.github.io/papers/huang-corl-22.pdf) | 2022年已有oracle与固定k步停止对照；去oracle本身不新 |
| [Code as Policies v4 附录K](https://arxiv.org/html/2209.07753v4) | 同样明确比较CLIPort固定10次动作/末状态与oracle停止；不能把固定时域评价当新原理 |
| [DAM-VLA v1 §3/5](https://arxiv.org/html/2606.12105v1) | 本轮另一条宽检索已有异步模态缓存/训练时序/独立gate；不将普通同步/异步融合再立题 |

Scholar这次HTTP200实际为`Verifying...`验证页，0个结果卡，不算成功检索；
[原访问与发现范围](scholar-discovery.json)。SciSpace先用于8项metadata发现后工具被移除；
重要结论均回到上述一手来源，不以第三方机器评论支持判断。
本轮没有进行完整引用链穷尽检索，不声称正式查新通过。

## go/no-go：值得继续深审的问题，不是已定方法

| 立项要求 | 当前证据 | 结论 |
|---|---|---|
| 明确失效机制 | 原始评分/loop共同序列 + 本地物理见证 | 有条件阳性，范围明确 |
| 影响现有学习方法的科学结论 | 没有完整基准攻击、成熟VLA配对或排序改变 | 未满足 |
| 独立核心增量 | 首选择/commit/去oracle等已有直接先例 | 未满足，暂不实现新算法 |
| SO-101可行性 | 简单本地物理见证已成；无真实硬件 | 只证明仿真端该命题可测 |
| 同题真机 | 应复测相同无语言序列及三类停止/评分，不能只展示成功抓放 | 待具备实机后验证 |

**保留为下一轮优先深审的测量问题；尚不能作为最终研究方向。**
有资格改变判断的下一项证据是：在完整已发布任务/协议与同预算下，真实无语言控制器取得
非偶然高分，并改变对成熟策略语言依赖性的判断；或证明该现象只是既有协议已解决的特例。
同时需要与本文之外的目标信息泄漏、语义评测与oracle停止近邻再核查，决定是否有独立研究贡献。
若普通首选择/显式commit已完整覆盖，降为诊断工具，不拼接模块或以换平台维持题名。

## 复核入口与保留范围

```bash
/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python \
  experiments/discovery/instruction-necessity-20261115/probe_components.py \
  --out /tmp/instruction-components-fresh.json
/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python \
  experiments/discovery/instruction-necessity-20261115/probe_loop.py \
  --out /tmp/instruction-loop-fresh.json
/home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/discovery/instruction-necessity-20261115/physical_witness.py \
  --out /tmp/instruction-physical-fresh
```

各输出路径必须不存在。物理审计用`audit_physical.py --replay <fresh目录> --out <新JSON>`。
物理模型/接触参数与原TPSC不同，未经真机校准；从历史失败VLA中解释语言损害的禁令仍有效。
原第三方源码/PDF只存忽略目录，来源hash和读取范围保留；派生scene许可证见[NOTICE](NOTICE.md)。
[adapter-diagnostic](adapter-diagnostic.json)记录首个AST加载遗漏helper的失败，补读/加载原函数后恢复，
没有改原source或删条件。审计v1在v2增强前保留，不覆盖。
