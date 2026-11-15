# 从真实SO-101失败发现问题：本轮证据与下一项核查

2026-11-15。**已读固定真实rollout与视频；没有确定研究方向或识别出因果机制。**
目标仍是有独立贡献、可查新、可实现的研究方向，SO-101仿真和真机验证同一命题。
不恢复已降级的“指令必要性”主张，不重启旧小BC微调。

## 实际新增的证据

### 同一真实策略、同一套环任务的成功与失败

固定[Armnet单臂数据revision](https://huggingface.co/datasets/armnet/armnetbench_v01_lerobot_so101/tree/1db69c82b589c7172ee31a6b8f7ef58d1fc2c663)。
读取2499条episode metadata与任务表，按[事前选择规则](PLAN-real-rollouts.md)冻结：
同一`pi0.5` checkpoint、ring_insert，母池30条为14 successful/16 failure；
分别取episode_index最早6条，得到225–236共12条。没有按轨迹误差或视频表现挑样本。

[选择清单](real-rollout-selection.json)绑定原始metadata SHA。
这12条来自同一策略，不是本项目新运行的12条，也不是初始物体位置配对实验。
标签来自数据作者的单一操作员，尚未独立复标。6+6分层样本不能估计总体成功率。

实际读取一个361776字节parquet，核对12条共5421行的长度、全局index、frame_index、
20Hz名义timestamp与finite值。对固定前1秒/3秒逐关节复算命令—状态差和运动增量。
例如，前3秒shoulder_lift同帧绝对差的episode中位数为成功组3.664、失败组3.664；
使用下一采样状态则为2.540、2.552。**均为原生数值单位，不称degrees、定位误差或纯机械延迟。**
这说明成功记录也存在命令—状态差；不证明两组等价、不可分或执行误差与失败无关。
实际采样只有episode级12条，帧没有增加独立n。详见[完整数值](real-prefix-audit.json)。

### 读取指定视频，区分可见事实与根因

下载固定top视频110353625 bytes，实际SHA与HF LFS SHA一致。
按metadata和视频PTS提取每条0/1/3/6/9秒与末帧，共72张；
末帧受作者成功裁剪影响，只帮助描述结局，不用于公平性能或失败预测。

[第1页](visual/contact-sheet-1.png) / [第2页](visual/contact-sheet-2.png) / [第3页](visual/contact-sheet-3.png)
及[原始采样manifest](visual-samples-manifest.json)、[逐项观察边界](visual-review-notes.json)。

- ep225的末帧21.25s：黄环看起来位于中央木桩上，机械臂已退开。
- ep233：0s黄环在左侧凹槽，9s及末帧28.55s看起来位于右侧凹槽，没有套在中央木桩上。
- ep226：6s、9s和末帧可见黄环仍在左侧凹槽附近。

这些是稀疏顶视图的可见现象。遮挡和高度信息不足，不能判定持续空抓、掉落、
抓持姿态变化、接触力、真实TCP误差或失败发生时刻，也没有把其余episode硬分成细致阶段。
特别是：不能把前3秒的关节差与较晚的错误放置拼成“机械跟踪导致失败”的因果链。

## 排除了一个未经验证的快捷解释

[LeRobot #5082](https://github.com/huggingface/lerobot/issues/5082)报告SmolVLA动作幅度收缩。
固定API只返回5条评论，未能复核搜索摘要中所述10月26日作者“保留pretrained stats后恢复”的评论；
这不证明该评论从未存在，但本轮不采用该摘要的因果断言。
[PR #5091](https://github.com/huggingface/lerobot/pull/5091)明确只加warning，量化依据是synthetic numpy，
未运行SmolVLA完整管线。因此它不能证明训练更换stats必然导致任务失败或保留stats必然修复。

本地按[执行前计划](PLAN-local-audit.md)只读旧20k checkpoint及其原20条trace：

- 7份checkpoint文件与原manifest逐项SHA一致，包括大权重的流式hash；未导入模型。
- pre/post两个processor中，action/state的mean/std共8组与固定数据stats转float32后完全相同。
- 复算600次查询、30000个完整chunk行与6000个实际目标，原20条仍0成功。
- 完整chunk的episode标准差/全数据标准差中位数，六通道为
  `0.172/0.390/0.435/0.319/0.620/0.371`。包含未执行tail，不能当实测运动。

较窄幅度可能与任务/状态/分布不同有关，未设置collapse阈值。
**本轮未发现processor与本地训练数据不一致，未识别原0/20的原因；不换stats放大动作。**
原仿真接口六通道数值degrees→rad仍是未完成同体资格验证的适配，不由这项审计补证。
见[全部只读结果](local-policy-audit.json)。

## 最近邻与资源约束改变了什么

| 已读一手依据 | 本轮有效结论 |
|---|---|
| [Warp最新v4 §III–V](https://arxiv.org/html/2606.31043v4) | 已有输出分布适配与多种强对照；真实SO101为2mm peg insertion，基线是有base-action上下文及可学习方差的随机residual。不能拿确定性平移冒充其硬件对照，不能沿用v1过强表述 |
| [Self-Adaptive VLA v1 §III–IV](https://arxiv.org/html/2609.30092v1) | 已有故障rollout压成context、动作偏置/encoder offset与跨试次修正；不能将失败记忆加补偿作为新核心 |
| [RoboColosseum v1 §4.3/8.1](https://arxiv.org/html/2611.02497v1)及[固定SO101源码](https://github.com/RoboColosseum/robocolosseum-finetune-so101/tree/7733d412f45d634c10c297a9e86adcf7085d8162) | 有实际任务、分阶段结果和公开模型入口。README要求至少24GB GPU与真实SO101；本地12GB/MuJoCo尚未资格验证。baseline_results的0–4平均分不能除4当成功率 |
| [FAN v1 §IV](https://arxiv.org/html/2609.21358v1) | 固定task-independent统计量的归一化方案已有先例，不能将普通freeze normalizer立为核心 |
| [GRASP v1 §III-A](https://arxiv.org/html/2610.23123v1) | 已有在各噪声level的clean-action估计上加FK/TCP/相对位姿损失；普通物理损失或Jacobian加权不是新点 |
| [经典抓持/运动规划教材的transition配置小节](https://motion.cs.illinois.edu/RoboticSystems/AdvancedTopicsInPlanning.html) | 任务执行要考虑object-to-gripper变换及后续任务可行性已有明确处理；不能把估计抓持偏移本身称为空白 |

公开cube-drawer pi05与数据已固定revision，但model训练配置指向原`Jiamo0912/...`且dataset revision为None；
本轮未逐项证明RoboColosseum镜像与实际训练数据完全相同，也没有原机器人校准或匹配MuJoCo场景。
已读40k配置是作者baseline说明所用step，不是按本机效果选择best checkpoint；没有下载大模型/安装新平台。

## 下一项优先科学核查：物理监督的条件均值问题

这是**独立来自GRASP公式的新待检验假设**，不是上述Armnet失败的原因。
Armnet的π0.5没有被认定为使用GRASP，不能从其视频推断GRASP损害。

具体问题：CFM的最优向量场是条件均值。若同一观测下存在多种合法未来动作，
在带噪输入上构造的clean-action估计可能是多种动作的条件均值；
非线性FK作用于这个均值，与FK作用于各个真实动作再平均，一般不同。
因而配对的几何辅助损失是否改变了原CFM的总体最优场，以及这种改变是否真的伤害任务，值得先核。

不能把一般“正则项可能引入bias”当新理论。
[When do explicit penalties improve flow matching? v1 的约束定义、式11–12/25–26及讨论](https://arxiv.org/html/2610.15689v1)
已分析约束满足与生成分布误差、bias/variance和曲面余项；
[原始FM §3.2](https://arxiv.org/html/2210.02747v2)与Riemannian/预条件化FM也必须作为方法近邻。
本轮尚未证明这些文献未覆盖上述配对几何损失问题，**不实现新算法或宣布查新通过**。
预条件化FM已核最新[v5](https://arxiv.org/html/2603.02337v5)而非停留在v1，当前只读其讨论，
最新方法/证明仍待深审；[RFM正式论文](https://proceedings.iclr.cc/paper_files/paper/2024/hash/d1f9936d3be6997ffffab692977eebe6-Abstract-Conference.html)
及[官方代码](https://github.com/facebookresearch/riemannian-fm)目前只完成发现，不能算完整覆盖审查。

下一步的最小判定：先比较“配对非线性FK监督”与“固定约束残差”的数学对象；
核对最近邻后，再检查CFM总体最优场处辅助损失梯度，包含线性FK/条件单解等零效应对照。
即使梯度非零，也只证明目标偏置，不能推出任务损害或独立方法贡献。
只有出现实际任务后果、强简单对照不能完全吸收且贡献清楚，才进入策略/硬件方法实验。

| 立项要求 | 本轮状态 |
|---|---|
| 真实任务问题入口 | 已有固定12条真实记录与可见结局差异；根因未知 |
| 可重复科学机制 | 未满足，不能以日志差或视频猜测替代 |
| 独立核心增量与查新 | 未满足；普通补偿、冻结normalizer、FK损失已有直接近邻 |
| 本机仿真与真机同命题 | 尚未匹配新任务载体；不因公开checkpoint存在就假定可运行 |

## 复核与保留

用现有策略环境执行四个程序，各输出路径必须不存在：
`audit_saved_policy.py --out <新JSON>`、`select_real_rollouts.py --out <新JSON>`、
`audit_real_prefixes.py --out <新JSON>`、`extract_visual_review.py --out <项目内新目录>`。
程序只读取固定本地资产，不执行策略、机器人、仿真或训练。
所有原文/原始数据缓存都在忽略目录，来源URL/SHA在本目录source manifests；
读取范围见[reading-scope.json](reading-scope.json)，新载体的未决条件见[资格记录](task-asset-qualification.json)。
原生72张帧图仍在忽略目录，公开仓库只保留三张缩略审阅图与完整采样记录。
图像来自Armnet数据（数据卡Apache-2.0），许可/改动说明见[NOTICE](NOTICE.md)，派生审阅图不宣称原创实机结果。

首次视频提取因相对输出路径与绝对ROOT混用而中止，已保留单张partial及[诊断](visual-extraction-diagnostic.json)，
定位后只修路径解析，在全新v2目录运行成功，源视频与选择时刻未改。
PATH无ffmpeg/ffprobe CLI，使用已安装PyAV，不新增依赖。
本轮没有新的成功Google Scholar结果页，不声称穷尽查新；工具访问RoboColosseum首页/教材find有失败，
相应信息回到成功缓存的作者代码/教材正文，不以访问失败否定论文或资产。

[验证记录](verification.json)：49份来源SHA、3份数值/选择审计的全新输出逐字节一致，
72张抽帧及3张审阅图在全新目录重放hash一致；98份既有tracked资产与HEAD逐字节不变。
Ruff、diff检查与原始TPSC指定hash通过。重放不增加真实episode数，也不证明新方向成立。
