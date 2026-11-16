# B2：1 万元新增预算下的硬件与科学问题裁决

2026-11-16。用户已选择增加低成本触觉／力传感，预算答复为 `1w`，即人民币
10,000 元。暂按传感器、采集设备、夹具加工、校准参考和运税全包含规划，属于
原 SO-101 基础平台之外的新增额度；不据此认定基础机械臂已购入。

**当前结论：预算约束已经明确，但尚无可立项的科学问题。** 优先保留“可校准的
力测量 + 独立参考”的架构选择，暂不锁定主传感器。以下是有范围的前期审查，
不是查新通过、采购清单或实验预注册。旧平台及所有已关闭路线继续 no-go。

## 1. 硬件选择：先看要测什么，再决定买什么

| 配置 | 已核官方事实 | 成本证据与缺项 | 本轮建议 |
|---|---|---|---|
| 单轴应变式力测量 + USB 桥式采集 | Phidgets 3132_0 为 780g 单点载荷传感器；1046_1 为四通道 USB 采集。单输入最高 1200 samples/s，四输入最高 125 samples/s | 官方产品页分别列 USD 6、USD 105。合计 USD 111 仅为这两个器件，不含第二套参考、线材、校准、夹具与中国到手费用 | 若问题只依赖法向合力，优先审查这一类架构。3132 仅是公开可核例子，量程未选定；消费级称重器件不能直接宣布为力真值 |
| DIGIT 光学触觉 + 独立力参考 | 官方接口默认 VGA 640×480、30fps；输出图像，力需要另行标定 | GelSight 官方索引列 USD 355／只；直接归档访问 403，未核实结算与国内到手价。力参考、安装与备用表皮另计 | 只有假设确实依赖空间接触、形变或滑移信息时再考虑。不能仅为“有触觉”消耗预算 |
| KWR46A 小型六维 F/T + 配套采集 | 官方页：各力轴量程 50N，力矩 2Nm；约 60g、直径 46mm、高 20.4mm；精度指标 0.5%FS，部分采样／通信指标依配套采集模块 | 无公开完整价格；需询价，裸传感器不等于 USB 可用系统。安装偏置、支架重量和 SO-101 负载仍待核 | 仅当假设依赖方向力／力矩且完整报价满足预算时考虑；目前不能宣称买得起或已适配 |

来源：[3132_0](https://www.phidgets.com/?prodid=223)、
[1046_1](https://www.phidgets.com/?tier=3&catid=98&pcid=78&prodid=1270)、
[采集率说明](https://www.phidgets.com/docs/Load_Cell_Guide)、
[DIGIT 厂商页](https://www.gelsight.com/product/digit-tactile-sensor/)、
[DIGIT 接口](https://github.com/facebookresearch/digit-interface)、
[KWR46 官方规格](https://www.kunweitech.com/products/610.html)。价格为本次访问状态，
不换算为未经核实汇率的人民币报价。

低价替代采集板 DAQ1500_0 官方列 USD 35，但还需 VINT hub；单输入最高 50Hz、
全输入 10Hz。不能用其板价与完整 USB 采集器比较总价。
[官方产品页](https://www.phidgets.com/?tier=3&catid=64&pcid=57&prodid=957)。

AnySkin 暂不进入本轮型号推荐：官方开源接口可核，但完整装配报价未核；论文制造
还涉及模具、真空和脉冲磁化设备。若能取得成品或共享制造设备再比较，不把电子
元件价当成整套成本。[官方仓库](https://github.com/raunaqbhirangi/anyskin)。

## 2. 预算分配上限，合计 10,000 元

| 项目 | 暂留上限／元 | 放行前要落实什么 |
|---|---:|---|
| 主研究传感器及其采集／相机 | 4,000 | 假设所需物理量、量程、延迟和完整含税到手报价 |
| 独立参考传感器及参考采集 | 2,000 | 与被评估通道独立，装配后校准与不确定度可核 |
| 夹具、支架与加工 | 1,500 | 载荷路径、预紧、偏心及附加重量；同材料对照可实现 |
| 校准载荷、量具和连接工具 | 1,000 | 校准来源、加载／卸载、多位置与重复测量方案 |
| 运税、线材、备用件与余量 | 1,500 | 实际到手费用；不能用预留额冒充报价 |
| **合计** | **10,000** | **当前实际支出 0；未下单** |

这是筛选上限，不是已经验证的 BOM。若完整配置超额，调整配置或否决，而不是省掉
独立参考。若仅研究标量力，不必把主传感器额度全部花完；不能为了符合此表购买
不满足精度或带宽要求的器件。参考通道也需要单独核定漂移，不能默认无误差。

## 3. 查新更新：三个具体问题均未取得 go

### A. 持续接触时，校准会不会吞掉真实接触力？

首轮只把它列为待核。现在出版社预览明确：
[SDI（Neurocomputing 620, 129292）](https://doi.org/10.1016/j.neucom.2024.129292)
用 EM、Kalman smoothing 和稀疏 Bayesian identification，并有空载、加载及
接触力实验。全文仍未获得，精确条件未读清。因此“一直接触下分离漂移与力”
这一宽表述不能因我们没读到全文就算空白。

[Continuous F/T Bias Estimation](https://arxiv.org/pdf/2403.01068v1) 已有已知负载
模型下的 bias/drift observer。还必须对比固定标定、已知空载重置、温度／独立
参考通道及模型观察器。只有 `y=F+b` 的不可辨识性不是贡献，人工注入 bias 后
展示控制误差也不足以证明真实新机制。

**裁决：不立宽题；窄差异仍未证明，不预注册校准方法。**

### B. 传感器测到了微小力变化，策略学不到还是舵机执行不出？

[FR-VLA v1 §6](https://arxiv.org/pdf/2610.25981v1) 已明确指出：示教中力驱动的微小
动作差异可能被行为克隆中的整体轨迹尺度淹没，并建议残差头／过渡阶段目标。
不能把这些建议直接改名为本项目贡献。其 force admission 是 attention-logit
offset，原始测量力仍有独立通道；相位不确定时 offset 回到基线，不是切断力输入。

静态核对固定 LeRobot revision `0b067df57d21d3a02d6c511f1609172fa39ac29b`：
SO follower 的 STS3215 位置命令经过整数转换。DEGREES 模式按
`int(q_deg * 4095 / 360 + mid)` 映射，约 0.0879°／码；默认身体关节也可以采用
校准范围归一化，夹爪为 0–100。驱动表有 CW/CCW dead-zone 寄存器名称，但没有
本机硬件实际值。源码只证明命令离散，**不证明实际位置误差、最小可控力步长，
也没有证明某个 learned policy 因此失败**。
[归一化实现](https://github.com/huggingface/lerobot/blob/0b067df57d21d3a02d6c511f1609172fa39ac29b/src/lerobot/motors/motors_bus.py)、
[电机表](https://github.com/huggingface/lerobot/blob/0b067df57d21d3a02d6c511f1609172fa39ac29b/src/lerobot/motors/feetech/tables.py)、
[SO follower](https://github.com/huggingface/lerobot/blob/0b067df57d21d3a02d6c511f1609172fa39ac29b/src/lerobot/robots/so_follower/so_follower.py)。

量化／采样造成接触振荡、被动性限制早有控制文献，例如
[Abbott–Okamura 2005](https://mmrobotics.mech.utah.edu/wp-content/uploads/2023/01/Abbott_TRO05.pdf)
与 [Choi et al. 2022](https://elib.dlr.de/190181/1/Virtual_Inertia_as_an_Energy_Dissipation_Element_for_Haptic_Interfaces_elib.pdf)。
它们的 haptic force-output 系统与位置命令舵机有差别，不能直接等同，但足以排除
“首次发现量化伤害接触控制”的宽主张。
[Stolt et al. 2015](https://lup.lub.lu.se/search/files/21680538/5434005.pdf) 已用 torque
dither 减少静止时摩擦对力估计的影响；其力矩接口也不能假定在 SO-101 上可用。

**裁决：只保留测量问题，尚不是研究方向。** 必须先区分监督损失、命令映射和
真实机械响应；外层积分／顺应、合理重标度／加权、取整对照和可实现的有限振幅
命令对照均属于强简单基线。若这些足够，只是工程适配；不得借 B2 重开旧
NeuralActuator、接口检测或 payload 补偿路线。

### C. 视觉推断的力表示何时需要真实力测量？

[FD-VLA v2](https://arxiv.org/pdf/2602.02142v2) 蒸馏的是编码后的 latent force token，
不是以 N 为单位的力重建。不能用“隐藏物理状态不可辨识”反驳一个它没有提出的
测量准确性主张。真实测力与传感器移除可以作有效对照，但信息不足的一般结论
和“加力传感更好”不是新核心。

[ForceVLA2 §3、§5](https://openaccess.thecvf.com/content/CVPR2026/papers/Li_ForceVLA2_Unleashing_Hybrid_Force-Position_Control_with_Force_Awareness_for_Contact-Rich_CVPR_2026_paper.pdf)
已有原始力反应路径、混合位姿／力动作、模态路由，并比较顺应启发的 ACP 等策略。
“快力反馈 + 慢视觉语言规划”这一组合不能作为新方法。

**裁决：通用表述 no-go；没有发现足以支撑新核心的窄机制。**

## 4. 下一项证据：先核边界，不训练

当前唯一保留的窄检查是 B 的“力相关动作差异在何处消失”；它的优先级来自可被
清晰否决，而不是已经证明新颖。下一步只读审查现有公开力—动作配对数据、最近
方法及经典量化控制，记录是否有校准参考、发送前浮点动作、原始命令码和实测
响应。若数据只记录其中一层，就不能由它判断另一层的失败。

已完成一个数据契约检查：
[NAD 固定 revision 的数据卡](https://huggingface.co/datasets/frankzydou/NAD/blob/ac4e634128c8e1d92ddaf023339c374d4e5863f9/README.md)
明确说 SO-101 没有末端力传感器，`force_z` 是持物时的已知重量标签；真正 F/T
推压子集属于 OpenManipulator-X。它也不列策略浮点输出与原始发送整数码的成对
日志，视频与遥测非逐帧同步。因此不能用它回答 B 的学习—执行归因问题，更不能
把重量标签当动态接触力真值。本轮没有下载轨迹、视频或权重；缺失字段也不证明
科学问题新颖。FR-VLA 项目页本轮取得的 HTML 未发现数据下载链接，不作全网无
公开数据的结论。

进入新预注册前须同时满足：

1. **信息足够：** 传感输出、参考真值、原始命令与实测状态的物理量和时钟明确。
2. **有实际问题：** 在本平台可达工作区存在重复的、影响任务的差异；不能只由
   4096 分辨率或理想仿真推定。若缺实测数据，先报告未知，不制造故障结论。
3. **有科学差异：** 原文逐项核对后，剩余问题超出已关闭的 actuator/interface
   线及经典强基线；不能仅靠 SO-101、传感器更便宜或换任务名成立。
4. **可同题验证：** 新仿真与真机采用同一种量测、位置命令路径、参考误差定义和
   核心干预；硬件用来检验同一命题，不能只有抓取演示。
5. **成本可闭合：** 完整实际报价、参考测量与夹具均在 1 万元内。

这些是推进条件，**不是已冻结的实验数量、阈值、方法或 seed**。满足后才制定新
预注册；目前不改 XML、不启动新策略／仿真、不复用 12100–12919。

若需要法向力，仿真可对齐特定载荷路径的测量与接触法向合力，但必须区分传感
body 间力、接触力、工具重力与惯性载荷。光学／磁式原始触觉不能直接用 MuJoCo
穿透深度替代。[量测语义及旧审查](B2_SENSOR_SCREEN_20261116.md)。

## 5. 证据状态与可复核性

- 全文取得并按记录范围阅读：FD-VLA v2、FR-VLA v1、ForceVLA2、Stolt 2015、
  Choi 2022；Abbott 2005 本轮只读作者库索引／摘要与检索返回部分，未完成全文审查。
- SDI 只读元数据与出版社预览；正文不可得不是研究空白。部分硬件资料访问
  403／404 的记录均保留；DIGIT 价格来自官方索引，不冒充完成结算。
- [来源与读取记录](../experiments/discovery/b2-budgeted-screen-20261116/SOURCE_NOTES.md)
  及同目录 `source-fetch*.json` 保留 URL、状态和原始响应 hash。
  PDF/网页缓存位于忽略的 `data/discovery/b2-budgeted-screen-20261116/`，不公开再分发。
- 本次仅写审查文档和来源记录；旧原始结果、checkpoint、manifest 与场景保持冻结。
  本轮核验结果另存该目录 `verification.json`。

**仍未完成的目标是选题本身。** 增加预算使平台筛选可以继续，但没有把任何一个
尚未成立的问题变成论文创新点。
