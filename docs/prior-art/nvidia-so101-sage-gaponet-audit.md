# 新核到的SO-101执行间隙近邻与成熟载体入口

2026-11-14。只读核查，没有安装Isaac、下载权重、运行真实机械臂或宣称复现。
这一发现影响后续选择：停止继续调当前小BC，先审查现有执行模型/匹配数据，
同时继续寻找不能被现有方法解释的具体问题。完整选题目标未完成。

## 1. 与我们的宽题直接重合的公开路线

[NVIDIA官方SAGE＋GapONet教程](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html)
已经介绍同动作的仿真/真实采集、逐关节间隙测量、执行模型，以及SO-101实例。
但教程明确写GapONet集成仍在进行，SO-101的GR00T＋GapONet闭环列为后续工作；
不能把教学概念图当已发布的SO-101补偿checkpoint或任务成功率。

固定源码：

| 来源 | revision | 本轮核到的范围 |
|---|---|---|
| [SAGE](https://github.com/isaac-sim2real/sage/tree/5b31cfa35416d1300b5099557049bd8e9cb4507d) | `5b31cfa35416d1300b5099557049bd8e9cb4507d` | README、SO101采集器、分析入口、模型配置；Apache-2.0 |
| [GapONet](https://github.com/jiemingcui/gaponet/tree/91eb8819c3156b46fdb3266a048600c67c9adf5d) | `91eb8819c3156b46fdb3266a048600c67c9adf5d` | 实际humanoid operator环境/历史输入/训练配置；根目录有BSD-3-Clause LICENSE及MIT LICENCE，需逐组件确定 |
| [SO-101 Workshop](https://github.com/isaac-sim/Sim-to-Real-SO-101-Workshop/tree/ce807d99724cb65671abec01f908a2fcb4a6eab7) | `ce807d99724cb65671abec01f908a2fcb4a6eab7` | vial-to-rack任务、仿真/真实评估、显式关节映射；Apache-2.0 |

仅取19份指定源码/说明/许可作只读缓存；不把整个vendor树当已审计。
没有执行仓库内安装脚本或技能文件，也没有下载大USD/权重。
来源/hash：[源码清单](../../experiments/so101/vla-open-source-audit/nvidia-so101-source-audit.json)。

SAGE采集器的前五轴为校准中心下的rad、gripper为0–1；current×固定系数只是估算torque，
不能当校准的关节力矩或F/T传感器。GapONet源码已有历史输入，operator branch读取sensor序列、
trunk读取当前目标；训练critic还含real轨迹与质量等特权量。
不能把它简化为无历史MLP，也不能直接将该humanoid环境称SO-101部署版本。

**对创新的约束**：同动作配对测误差、神经执行模型、将补偿器接在VLA后面、
在仿真中学习更真实执行行为，这些宽泛组合均不能作为我们的核心贡献。

## 2. 有匹配数据和检查点入口，但契约不同

[官方数据/模型表](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/datasets-and-models.html)
提供75条sim示范与已微调GR00T N1.6入口。
本轮HF固定到：

- 数据 `sreetz-nv/so101_teleop_vials_rack_left`：`69802873f4a26bffb716fca1f4fb1bb0e3d2a07a`。
  meta为`so101_follower`、75episode、18250帧、30Hz、ego/external_D455双640×480 RGB、六维state/action。
  页面预览显示18326行，与meta总帧不一致，未读parquet逐条核对，不替它裁决。
- 模型 `aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left`：
  `7efab50dfd58cd8f1831035fd86b65410b98c448`。
  明确只读`checkpoint-10000`元数据，未择优或下载权重；每个checkpoint的safetensors约9.81GB，
  不含推理激活/视觉token/缓存，不能由此保证本机12GB能加载。
- config的action_horizon50，而`new_embodiment` processor只列16个action delta indices；
  `single_arm`标RELATIVE、gripper标ABSOLUTE，front/wrist相机。须检查完整processor解码和运行时裁切，
  不能直接将原始网络输出当绝对关节命令。
- Workshop显式把前五轴原始−100…100与gripper0…100按各轴USD限位映射为rad。
  这不是旧SmolVLA的五轴degrees，也不是SAGE的gripper0…1；不能复用现有all-six-degrees adapter。

数据不是现有红块TPSC任务；vial-to-rack资产、视角、标定、关节零位和成功谓词仍需独立核验。
使用这个入口不能直接补齐TPSC的正确共享前缀证据。
官方表的co-train数据行写5条real、模型行写50条real，本轮未核清，不合并成确定样本数。
以上是元数据与源码证据，没有本地模型加载、仿真能力或真机实验。

## 3. 不把未完成路线当即插即用系统

[Isaac Capture SO-101页面](https://nvidia.github.io/IsaacCapture/main/integrations/lerobot/index.html)
的待办仍包括sim导出、N1.7训练与sim-to-real更新；
[训练子页](https://nvidia.github.io/IsaacCapture/main/integrations/lerobot/training_groot.html)
也明确为在写状态并指向N1.6教程。
Workshop README列出实测RTX6000Pro/5090/RTX6000Ada，未给本机5070Ti或A100上的本项目资源证据。
Isaac工程栈切换有成本，本轮不据此自动安装/迁移，更不把官方演示当我们的结果。

[Isaac Sim 5.1官方要求](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html)
明确不支持无RT Cores的A100/H100，并列16GB最低显存。
本机5070Ti Laptop为12GB；不能保证本机能同时承担该仿真与模型推理。
SAGE README绑定5.0.0，但该版本requirements地址本轮404，未把5.1要求说成5.0实测。
因此A100训练计算与Isaac RTX渲染的资源角色须区分；目前仍保留MuJoCo路线，
不能因A100显存更大就计划直接在它上面运行这个RGB仿真栈。
官方要求缓存/hash见 `isaacsim-requirements-source.json`。

## 4. 后续优先顺序

1. 查清SAGE现有SO-101真实轨迹和时间/单位/标定信息，判断能否形成执行建模强基线；
   不含任务结果的轨迹不能用于认知偏差或VLA伤害归因。
2. 对窄科学问题明确其超出SAGE/GapONet、APEX、Tune to Learn和NADA/GAP之处；
   没有差异就换问题，不能靠移植到MuJoCo或SO101起新题。
3. 只有选定问题确需成熟VLA时，才比较现有固定MuJoCo栈和这个匹配资产/数据/权重路线的资源代价。
   不将当前小BC15/20升级为通过，不继续无上限架构试错。

缓存和元数据分别记录在`nvidia-official-pages.json`、`nvidia-so101-hub-metadata.json`、
`nvidia-checkpoint-10000-metadata.json`，位于 `experiments/so101/vla-open-source-audit/`。
