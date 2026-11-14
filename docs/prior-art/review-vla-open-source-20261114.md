# 用户开源盘点材料：哪些改变我们的实验与选题

日期：2026-11-14。输入为用户提供的 `docs/VLAkaiyuanxiangmu.md`，378行，原文保留。
**建议继续当前普通 SmolVLA 载体预实验；加入轻量强基线与更严格的模型契约核验，不因盘点而冻结新方向。**

实际核验15个原始仓库的固定revision与README；进一步读了MolmoAct2的SO100/101模型卡、
配置与normalizer、vendored LeRobot说明，TurboVLA动作头源码和LIBERO协议，以及τ₀高层入口。
记录在 [repository-inventory.json](../../experiments/so101/vla-open-source-audit/repository-inventory.json)、
[source-files.json](../../experiments/so101/vla-open-source-audit/source-files.json)、
[resource-contracts.json](../../experiments/so101/vla-open-source-audit/resource-contracts.json)。
这不是15篇论文全文查新、15套独立复现或性能排名；star数量不参与选题判断。

## 1. 最有用的四个结论

### MolmoAct2可以列为后续载体，但不能跳过SO101同体核验

[固定README](https://github.com/allenai/molmoact2/blob/6070080a20321b4f498ab30f28e1d09ac465edb7/README.md)
确实列出SO100/101模型和社区部署实现，但部署说明主要确认SO-100与Franka，且推荐标准SO-100腕部。
因此不能沿用“名字含SO101就证明与项目XML相同”的旧错误。

实际读取的 [SO100_101检查点](https://huggingface.co/allenai/MolmoAct2-SO100_101/tree/152569fe57914d97be91055800035f54e250d009)
有5,442,196,272参数，存储dtype为F32；BF16仅参数的理论下限约10.14GiB，不包含视觉token、激活、缓存等。
模型卡报告FP32约24GB（不开CUDA graph）或26GB（开启），BF16在其测试中低于16GB。
**这些数值不证明我们的12GB 5070Ti能装下；本轮没有加载或下载大权重。** A100更适合后续完整基线。

它使用q01/q99归一化、6维绝对关节动作、horizon=30、max_action_dim=32的内部padding，
需要`so100_so101_molmoact2`标签。模型卡示例状态含shoulder_lift约189°、elbow约181°，
不能直接送入项目当前XML角度范围。必须追溯零位/校准和夹爪，不能靠线性压缩范围消除差异。
也不能把当前SmolVLA normalizer或全六角度adapter直接复用给它。

### TurboVLA是必须考虑的轻量对照，尚不是可直接部署的SO101 checkpoint

[固定源码/协议](https://github.com/H-EmbodVis/TurboVLA/tree/650a288f829f549bea18e2173d3f51e77d3fbb74)
提供实际训练与评估入口；读到的LIBERO方案是DINOv3双视角、BERT、7D动作、chunk=12，
动作头直接生成连续chunk。这与我们SmolVLA的6关节、chunk=50不同，不能直接替换权重。
其32Hz和约0.9GiB是作者在4090上的特定推理结果，不是我们本机的端到端控制频率。

如果研究收益只相当于更短chunk、更小模型或更快推理，必须先与这类轻量方法比较。
具体实验要匹配执行窗口、任务数据、调参预算，并分别报告推理时间与物理控制时间。
它的LIBERO参考环境含较旧CUDA/PyTorch，不能覆盖安装到当前sm_120策略环境。

### 统一评测能省工作，但不会替我们定义成功与同体契约

[allenai/vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness/tree/505ae54c1c9ba07cb3aec82ce2808402acd43035)
已有模型/环境分离、隔离运行、LeRobot桥接与重现报告。
盘点的机构标题和正文署名存在不一致，后续引用以原始仓库和作者声明为准。
README区分已重现与仅集成状态，不能把全部支持格子当作已验证成绩。
我们的自定义TPSC场景仍需adapter、任务谓词、配对身份和分叉证据，不能由框架名称代替。

[StarVLA固定README](https://github.com/starVLA/starVLA/blob/13d8ad43eb4128554c57227507055ecf9c3a62a2/README.md)
有丰富可更换模块，但SO101列表项仍未勾选。它可供架构/对照参考，当前不是省去SO101适配的捷径。

### 世界模型与快慢系统已经是强近邻，不能作我们的核心新意

[τ₀-VLA高层入口](https://github.com/sii-research/tau-0-vla/blob/d804047f7b2d61c45077daada3183703aeed8cf5/high_level/README.md)
已有带记忆的高层提案和生成目标图像的世界模型，二者使用独立环境；
[OpenWAM](https://github.com/OpenWAM-Official/OpenWAM/tree/1dcaeea76501f2431286b511284a671778645996)
已系统比较世界模型与动作模型的耦合方案；
[InternVLA-A1.5](https://github.com/InternRobotics/InternVLA-A-series/tree/e6fc904f9edbfb14532e97095fc2372202517f76)
已使用训练期未来动态监督、推理期去除视频分支。
因此“快动作＋慢思考”“加世界模型纠错”“训练时预测未来、部署时省掉预测器”均不足以单独立项。
这些仓库并没有自动否证窄的TPSC命题，但增加了必须比较的既有机制。

## 2. 15项筛选表

下表“没有验证”限于本轮读取范围，不代表项目永远不支持。固定revision均保存在inventory。

| 项目与原始入口 | 本轮能核到的开放范围 | 对本项目的用途与限制 |
|---|---|---|
| [GR00T N1.7](https://github.com/NVIDIA/Isaac-GR00T) | 代码、权重入口、训练部署；代码与权重许可分别说明 | 跨本体强基线；README推理建议16GB+、微调40GB+，部分骨干需访问授权；不作为本地12GB首选 |
| [Ψ₀](https://github.com/physical-superintelligence-lab/Psi0) | 模型、SIMPLE、人形全身训练评估入口 | 快慢分层与本体适配近邻；当前SO101桌面问题不需要切换全身控制栈 |
| [LingBot-VLA 2.0](https://github.com/Robbyant/lingbot-vla-v2) | 6B权重、canonical动作、RoboTwin后训练 | 统一动作/未来动态近邻；未验证SO101部署与12GB运行 |
| [MolmoAct2](https://github.com/allenai/molmoact2) | 模型、数据、训练、SO100/101入口 | 后续A100载体候选；本轮核到校准、dtype、normalizer差异，不能即插即用 |
| [Qwen-VLA](https://github.com/QwenLM/Qwen-VLA) | 固定源码归档仅README与媒体，没有Python训练推理文件 | 研究近邻；当前不当作可运行策略。不是对尚未公开能力的否定 |
| [Xiaomi-Robotics-1](https://github.com/XiaomiRobotics/Xiaomi-Robotics-1) | `xr1/`后训练/部署入口及权重链接 | 数据迁移近邻；不复现大规模预训练，SO101契约本轮未验收 |
| [UnifoLM-VLA-0](https://github.com/unitreerobotics/unifolm-vla) | 训练推理、LIBERO与真机入口 | 人形/通用策略参考；没有本项目SO101能力证据 |
| [InternVLA-A1.5](https://github.com/InternRobotics/InternVLA-A-series) | 模型、训练、多仿真协议 | 未来监督近邻；README为CC BY-NC-SA 4.0，不能统一写成Apache；不安装到当前环境 |
| [Hy-Embodied-0.5-VLA](https://github.com/Tencent-Hunyuan/Hy-Embodied-0.5-VLA) | 数据、训练/后训练与执行入口 | UMI/历史记忆强近邻；README建议16GB+，未证明12GB或SO101适配 |
| [OpenWAM](https://github.com/OpenWAM-Official/OpenWAM) | 耦合架构、训练、权重、benchmark入口 | 世界—动作模型机制比较来源；不把框架集成本身当创新 |
| [TurboVLA](https://github.com/H-EmbodVis/TurboVLA) | 真正的训练与评估代码、权重入口 | 轻量强对照；7D LIBERO与本项目6D关节契约不同 |
| [τ₀-VLA](https://github.com/sii-research/tau-0-vla) | 低层、提案、世界模型、LIBERO入口 | 长程分层/记忆/世界模型测试时计算近邻；不等于SO101现成策略 |
| [StarVLA](https://github.com/starVLA/starVLA) | 多骨干、多动作头、多benchmark | 研究工作台；README中的SO101仍待支持 |
| [vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness) | 评测隔离、LeRobot桥、记录与重现报告 | 借用协议规范；自定义SO101任务仍要独立接入验收 |
| [verl-vla](https://github.com/verl-project/verl-vla) | 分布式采集、SFT/RL、人工干预；列LIBERO/Arena/Piper | 系统基础设施参考；不把“闭环/人工参与/云边”当算法贡献，也不声称已支持SO101 |

GitHub API递归tree部分请求触发403限流，未无限重试；Qwen使用固定commit的源码zip复核，
确认仅README与媒体。其余项目的“代码存在”不自动等于我们运行通过。许可证metadata为
NOASSERTION或空时保留未确认，不自动补成MIT/Apache。

## 3. 对当前路线的具体影响

1. 继续现有固定seed、20k终点的普通SmolVLA训练；不另开大模型训练，不挑中途最优checkpoint。
2. 最终checkpoint先跑20条目标任务能力screen。公开载体只有green→container单任务，不能预设它懂中文红块左右分支。
3. 只有能力和正确共享前缀成立，才按[损失忠实性更正](tpsc-loss-fidelity-correction.md)比较明确布局的BAS目标；
   同时排除chunk长度/执行窗口、轻量模型、阶段条件、相机和校准等替代解释。
4. 若载体未就绪，优先修任务数据与物理抓取。MolmoAct2留为后续A100替代载体，TurboVLA留为轻量对照；
   两者都先做接口验收，换模型不能代替机制证据。
5. 若忠实基线没有可重复前缀伤害，停止当前TPSC方法主张，转向真实观测到的失效重新查新。

这些材料扩大了可用载体和对照，尚未给出“查新通过”的研究方向。完整目标保持active。
