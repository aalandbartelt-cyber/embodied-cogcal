生成式AI的出现从根本上改变了机器人智能，使人形机器人在物理世界中“感知、推理和行动”的方式取得了重大进展。这一巨大进步主要归功于决策能力方面的进步，这得益于LLM和VLM的预训练实现的泛化能力。VLA 不再依赖于传统的复杂策略（这些策略必须针对单个低级任务精心设计，才能实现细粒度的操作），而是能够结合视觉和语言知识，实现更佳的推理能力，从而实现机器人控制。

Embodied AI指的是集成到物理实体（主要是机器人）中的智能系统（VLM）。类似于人类从自身经历、周围环境和所处环境中学习的方式，Embodied AI通过与环境的互动以及对观察场景的视觉线索进行学习，从而能够有效地处理现实世界中的动态场景，这与人类大脑的工作方式相似。

![图片](https://mmbiz.qpic.cn/mmbiz_gif/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCskQyWBhuxXgiczdiajS3icbTyWq219Dibdic56bnpg69Gicpic0pmYRGgic4hg/640?wx_fmt=gif&from=appmsg)

截至 2025 年 4 月，SOTA VLA采用双层专家系统，结合视觉语言模型（VLM）和diffusion decoders，例如英伟达的 Groot N1 和 FigureAI 的 Helix，或者采用类似物理智能中的 π0（Pi-Zero）的基础通用策略。

- **系统 2**（“慢思考”）：VLM将视觉和文本作为上下文输入，以对复杂场景和中间任务进行系统决策。这指导了机器人的整体行为，因为它们对机器人的世界有着出色的了解。它们作为高级规划器，通过推理多模态输入并生成轨迹，将主要目标分解为多个中间子任务来实现。
- **系统 1**（“快思考”）：transformer decoder或diffusion model作为低级控制和灵巧运动的动作专家。扩散模型具有丰富的图像先验，系统利用其卓越的语义场景关系，将系统 1 指导的路径或指令翻译并执行，以执行敏捷且精细的运动动作。

这两个系统共同模拟了丹尼尔·卡尼曼（Daniel Kahneman）的双重过程理论，结合了高级规划器和低级快速执行。**
**

**![图片](https://mmbiz.qpic.cn/mmbiz_jpg/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribC0yFkCpia7zAXQGd6nzWfEoWSIH5jrWjdC3Rqe8s5oDrTLBdb9qqX1Vg/640?wx_fmt=jpeg&from=appmsg)“快思考与慢思考”**

在本文中，我们将深入探讨 VLA 在 后GPT 时代的发展，并使用 LeRobot 框架演示。

## **机器人中的策略是什么？**

在机器人学中，策略是一组规则，指导机器人在给定环境中根据当前状态采取行动以实现目标。

主要有两种类型的策略：

- **确定性策略**：将特定动作映射到环境的每个状态。
- **随机策略**：对于每个状态，在所有可能的动作上有一个概率分布。

机器人可能根据其最终目标经历一个或多个episode。episode是指机器人代理与其周围环境从初始状态到终止状态的一系列交互。这涉及一系列步骤，例如：

- **状态（s）**
- **动作（a）**
- **奖励（r）**
- **下一个状态（s’）**

这些agents通常通过强化学习方法进行训练，给定一个起点和终点，通过在剧集中最大化奖励来学习最优行为。通过这种方式，模型通过试错学习最优行为。

这些机器人策略表现出行为克隆或模仿学习的特点，即给定观察和动作对的轨迹，目标是训练模型以预测正确的动作。

传统上，为每个低级任务和特定的机器人硬件配置创建单独的策略或复杂的启发式规则。然而，现实世界的数据是复杂的，训练这些策略既耗时又昂贵，且需要大量数据。如果我们能够利用大语言模型（LLM），并创建能够在动态场景中泛化的系统，那会怎样？这意味着机器人可以观察周围环境，理解口头或书面指令，并独立执行现实世界中的任务，表现出泛化能力。

### **通用机器人策略（GRP）**

机器人中的通用策略指的是一种单一的、统一的模型，能够解决多个下游任务或适应新任务，而无需针对特定任务进行微调。与传统策略不同，传统策略必须针对多个子任务或特定平台或硬件进行训练，通用策略正如其名，模型能够发展出新兴行为，以泛化到未见任务、新场景或任何硬件设置中。例如，RT-2、π0（Pi-Zero）和 Groot N1 等模型。这些 GRP 不仅仅局限于预编程或硬编码的指令，而是通过其“观察、理解和行动”的特性，自我探索和导航任务或问题，并设置中间目标。

## **为什么我们需要 VLA？**

尽管LLM在基于文本的任务中表现出色，但它们对机器人所操作环境的物理约束的理解有限或受到限制。由于仅凭文本无法完全解释最终期望的目标，且 LLM 并不总是描述精细的低级行为，因此它们生成的子目标可能不可行。但是图像或视频可以创建精细的策略和行为。

VLM具有出色的泛化能力，因为它们是在包含图像和视频的大型多模态数据集上训练的。对于有效的机器人控制和操作而言，仅拥有 VLM 表示是不够的，动作数据也很重要。VLA 在 VLM 的基础上增加了额外的动作和观察状态标记。

**状态**：这是一个单一标记，代表机器人的观察，例如传感器值、夹持器位置和角度等。

**动作**：这个标记代表要执行的电机命令序列，以沿着轨迹进行精确控制。

**“VLA”**这一术语最初是在谷歌的 RT-2 论文中提出的，该论文使用 PaLI-X 和 PaLM-E 作为骨干网络，将“像素转换为动作”。

### ***\*VLA 的类型：\****

- `类型 1`：使用 VLM/LLM 作为高级规划器，低级控制由单独的策略处理，例如 **SayCan**、PaLM-E。
- `类型 2`：使用图像或视频生成模型作为高级规划器，例如伯克利的 **SuSIE**。
- `类型 3`：结合类型 1 和类型 2 的混合方法，用于规划中间任务。例如：**HybridVLA**
- `类型 4`：使用单一 VLM 进行端到端控制，包括感知、规划和控制。
- `类型 5`：使用 VLM 进行高级规划，扩散模型执行这些指令。例如：**Groot N1**、Octo

## **1. 谷歌的 RT-2**

**RT-2**是由谷歌 Deepmind 机器人团队开发的一种新型视觉语言行动模型，它是闭源的。该模型不仅仅记忆，它理解上下文并运用链式思考推理，使其能够将学到的概念应用于新情境。

![RT-2 Google Co Finetuning in a Closed loop control for robot actions](https://mmbiz.qpic.cn/mmbiz_png/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCXkTv0EzjVo024icwIDic61hKnDapkPHE3swiaDKPvCSrDV4RaU68JXPnA/640?wx_fmt=png&from=appmsg)

它包含预训练的 PaLI-X（55B）作为视觉模型和 PaLM-E（12B）具身模型作为骨干网络，与视觉数据共同训练，并对机器人动作数据进行加权。它接收机器人的摄像头输入（图像）和自然语言处理（NLP）查询，并输出离散的动作标记，这些标记随后被解码为基于文本的指令，可以像大语言模型（LLM）的文本响应一样控制机器人。

![RT-2 takes in images as patches through a ViT Encoder and language instruction with a LLM to generate Robot action](https://mmbiz.qpic.cn/mmbiz_png/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCRERup97sZFMM6pM1RfgUpA9JP24ywSlLA95jjtGce4vARX5271icdQQ/640?wx_fmt=png&from=appmsg)

输出是一个动作标记序列，作为描述机器人末端执行器位置和方向的字符串，用于进行操作，形成闭环控制。

![Sequence of robot action include the translation and rotational changes](https://mmbiz.qpic.cn/mmbiz_jpg/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCZTdiaZO6wQnZyCOZvjrbNicSfsuptWPcg3WlwzxMXmVAkGichwFHtvhsw/640?wx_fmt=other&from=appmsg)

研究发现，该模型学会了新兴属性，解决了模型未经过训练的全新任务，例如人脸识别、符号理解和推理。这种泛化能力是前所未有的，这都归功于其使用网络规模数据进行训练。由于该模型直接执行可操作的行为，同时摒弃了特定任务的策略，这在具身人工智能领域是一个重大突破。

![RT-2 working examples](https://mmbiz.qpic.cn/mmbiz_png/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribC3ibictUaZIHLpgUvCJ3JMibR1lvCibjTib1ROBokibZcJgHbIySyD9EGQibdA/640?wx_fmt=png&from=appmsg)

## **2. 加州大学伯克利分校的 Octo**

Octo（93M）是一个基于开源 Transformer 的通用策略，它在 OpenX-具身数据集的 800,000 个机器人演示上进行了训练，其性能与庞大的模型如 RT-2（55B）相当。所有的机器人数据都被转换为输入标记序列，并通过 Octo Transformer 传递。

![Octo Transformer working where it takes the visual observation and task tokens to predict a meaningful actions from a noise](https://mmbiz.qpic.cn/mmbiz_jpg/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCaJ37oRicCEuqYLggNEzHCpvtAHzcw1n0ibWLr7rw80GdL8T6XE0lyVyg/640?wx_fmt=jpeg&from=appmsg)

首先，输入指令作为任务标记传递给语言编码器，同时将带有补丁的图像传递给 CNN 编码器作为观察标记。然后，Octo Transformer 的嵌入被解码以使用扩散头输出动作标记。作者报告称，与离散动作标记不同，基于扩散的解码器效果最佳。

Octo 的独特之处在于其灵活且能够适应不同的观察输入，例如手腕和第三人称相机视图。为了将 Octo 适配到我们的机器人配置或动作空间，我们只需要在少量演示数据集上对其进行微调。

Octo 有三个变体：

- Octo-Tiny
- Octo-Small
- Octo-Base（约 93M）

### **Octo 推理代码指南**

```
# 下载仓库
!git clone https://github.com/octo-models/octo.git
%cd octo
# 安装仓库
!pip3 install -e .
!pip3 install -r requirements.txt

# 修复：https://docs.scipy.org/doc/scipy-1.12.0/reference/generated/scipy.linalg.tril.html
!pip install scipy==1.11.0

# 修复：jaxlib 和 jax 版本不匹配
# !pip install jaxlib==0.4.20
```

从 Hugging Face 加载预训练检查点

```
from octo.model.octo_model import OctoModel

model = OctoModel.load_pretrained("hf://rail-berkeley/octo-small")
print(model.get_pretty_spec())
```

该模型使用窗口大小为 2 进行训练，预测未来 4 步的 7 维动作。

观察和任务符合以下规范：

```
观察：{
    image_primary: ('batch', 'history_window', 256, 256, 3),
    image_wrist: ('batch', 'history_window', 128, 128, 3),
}
任务：{
    image_primary: ('batch', 256, 256, 3),
    image_wrist: ('batch', 128, 128, 3),
    language_instruction: {
        attention_mask: ('batch', 16),
        input_ids: ('batch', 16),
    },
}

在推理时，您可以传递这些观察和任务键的任何子集，历史窗口最多可达 2 个时间步。
```

### **加载数据集**

接下来，我们将从桥接数据集中加载一个轨迹以测试模型。这使用了 Open X-具身数据集。

```
# 创建 RLDS 数据集构建器
builder = tfds.builder_from_directory(builder_dir='gs://gresearch/robotics/bridge/0.1.0/')
ds = builder.as_dataset(split='train[:1]')

# 采样剧集 + 调整大小为 256x256（默认第三人称相机分辨率）
episode = next(iter(ds))
print(episode)

steps = list(episode['steps'])
images = [cv2.resize(np.array(step['observation']['image']), (256, 256)) for step in steps]

# 提取目标图像和语言指令
goal_image = images[-1]
language_instruction = steps[0]['observation']['natural_language_instruction'].numpy().decode()

# 可视化剧集
print(f'指令：{language_instruction}')
media.show_video(images, fps=10)

"""{'steps': <_VariantDataset element_spec={'action': {'open_gripper': TensorSpec(shape=(), dtype=tf.bool, name=None), 'rotation_delta': TensorSpec(shape=(3,), dtype=tf.float32, name=None), 'terminate_episode': TensorSpec(shape=(), dtype=tf.float32, name=None), 'world_vector': TensorSpec(shape=(3,), dtype=tf.float32, name=None)}, 'is_first': TensorSpec(shape=(), dtype=tf.bool, name=None), 'is_last': TensorSpec(shape=(), dtype=tf.bool, name=None), 'is_terminal': TensorSpec(shape=(), dtype=tf.bool, name=None), 'observation': {'image': TensorSpec(shape=(480, 640, 3), dtype=tf.uint8, name=None), 'natural_language_embedding': TensorSpec(shape=(512,), dtype=tf.float32, name=None), 'natural_language_instruction': TensorSpec(shape=(), dtype=tf.string, name=None), 'state': TensorSpec(shape=(7,), dtype=tf.float32, name=None)}, 'reward': TensorSpec(shape=(), dtype=tf.float32, name=None)}>}
指令：将罐子放在锅的左边。"""
```

### **对完整轨迹运行推理**

现在，是时候使用加载的模型对剧集中的图像运行推理了。在这个演示中，我们将提供目标条件和语言条件的训练。

```
WINDOW_SIZE = 2

# 创建 `task` 字典
task = model.create_tasks(goals={"image_primary": goal_image[None]})   # 对于目标条件
task = model.create_tasks(texts=[language_instruction])                # 对于语言条件
# 运行推理循环，此模型仅使用单个图像观察用于桥接
# 收集预测和真实动作
pred_actions, true_actions = [], []
for step in tqdm.tqdm(range(0, len(images) - WINDOW_SIZE + 1)):
    input_images = np.stack(images[step : step + WINDOW_SIZE])[None]
    observation = {
        'image_primary': input_images,
        'timestep_pad_mask': np.array([[True, True]]),
    }

    # 这返回 *归一化* 的动作 --> 我们需要使用数据集统计信息进行反归一化
    norm_actions = model.sample_actions(observation, task, rng=jax.random.PRNGKey(0))
    norm_actions = norm_actions[0]   # 去掉批次
    actions = (
        norm_actions * model.dataset_statistics["bridge_dataset"]['action']['std']
        + model.dataset_statistics["bridge_dataset"]['action']['mean']
    )

    pred_actions.append(actions)
    true_actions.append(np.concatenate(
        (
            steps[step+1]['action']['world_vector'],
            steps[step+1]['action']['rotation_delta'],
            np.array(steps[step+1]['action']['open_gripper']).astype(np.float32)[None]
        ), axis=-1
    ))

"""
{'image_primary': Traced<ShapedArray(uint8[1,2,256,256,3])>with<DynamicJaxprTrace(level=1/0)>, 'timestep_pad_mask': Traced<ShapedArray(bool[1,2])>with<DynamicJaxprTrace(level=1/0)>}
"""
```

任务指令：**将罐子放在锅的左边。**

### **可视化预测动作和真实动作**

最后，让我们比较预测动作和真实动作。

```
import matplotlib.pyplot as plt

ACTION_DIM_LABELS = ['x', 'y', 'z', 'yaw', 'pitch', 'roll', 'grasp']

# 构建图像条以显示上述动作
img_strip = np.concatenate(np.array(images[::3]), axis=1)

# 设置 plt 图表
figure_layout = [
    ['image'] * len(ACTION_DIM_LABELS),
    ACTION_DIM_LABELS
]
plt.rcParams.update({'font.size': 12})
fig, axs = plt.subplot_mosaic(figure_layout)
fig.set_size_inches([45, 10])

# 绘制动作
pred_actions = np.array(pred_actions).squeeze()
true_actions = np.array(true_actions).squeeze()
for action_dim, action_label in enumerate(ACTION_DIM_LABELS):
# 动作具有批次、地平线、维度，在此示例中，我们仅取第一个动作以简化
  axs[action_label].plot(pred_actions[:, 0, action_dim], label='预测动作')
  axs[action_label].plot(true_actions[:, action_dim], label='真实动作')
  axs[action_label].set_title(action_label)
  axs[action_label].set_xlabel('剧集中的时间')

axs['image'].imshow(img_strip)
axs['image'].set_xlabel('剧集中的时间（抽样）')
plt.legend()
```

## **3. 斯坦福大学的 OpenVLA**

OpenVLA 是一个开源的 7B 参数模型，它在 Open X-具身数据集的 970K 个剧集上进行了训练，用于通用机器人操作任务。

它包含三个主要组成部分：

- **视觉编码器**：采用双视觉编码器方法，使用 DINOv2（约 300M）和 SigLIP（约 400M）。它接收图像并创建扁平化的补丁嵌入。DINOv2 擅长空间关系，而 SigLIP 提供强大的语言对齐属性。为了将视觉编码器适配到新任务（如动作预测），解冻并训练这些模型层是很重要的。
- **投影器**：使用 MLP 投影器将视觉嵌入映射到 LLM 的共享嵌入空间。
- **LLM**：Llama2 7B 模型接收语言指令并进行标记化。视觉嵌入和文本标记一起作为序列传递给 LLM，以生成动作，例如位置变化、旋转和夹持器状态，这些动作可以直接用作控制机器人末端执行器的连续信号。

![OpenVLA Model Architecture using Llama 2 7B with Dual Vision Encoder Dinov2 and SIgLIP to predict 7D Robot Action including position orientation and gripper state](https://mmbiz.qpic.cn/mmbiz_jpg/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCV0b8VgES6EfazUjSn1gtiaSzAJIvEsthZpEP40mWyTTEDPdFT9ogVjw/640?wx_fmt=jpeg&from=appmsg)

使用 Franka Emika Panda 7 自由度机器人臂作为测试平台，以 5Hz 的频率进行评估和基准测试。该项目还增加了对LoRA参数高效微调技术的支持，实验结果表明，这些 PEFT 模型的性能与原始模型相当。

作者建议我们可以像训练 LLM 一样通过下一个标记预测和交叉熵损失来训练 VLA。我们只需要 255 个动作标记来表示给定视觉观察和语言指令的机器人整个动作空间。

实验研究表明，OpenVLA 尽管参数数量比 RT-2-X（55B）少 7 倍，但其性能却优于 RT-2-X。然而，OpenVLA 本身在未见数据集（分布外）上的表现不如 RT-2，因为它没有像 RT-2 那样在网页数据上进行训练。因此，在未见数据分布上进行微调有助于模型快速适应新剧集。

### **OpenVLA 代码指南**

```
!git clone https://github.com/openvla/openvla.git
%cd openvla
!pip install -e .

!pip install packaging ninja
!ninja --version; echo $?  # 验证 Ninja --> 应返回退出代码 "0"

!pip install -r https://raw.githubusercontent.com/openvla/openvla/main/requirements-min.txt

# 安装最小依赖项（`torch`、`transformers`、`timm`、`tokenizers`等）
# > pip install -r https://raw.githubusercontent.com/openvla/openvla/main/requirements-min.txt
from transformers import AutoModelForVision2Seq, AutoProcessor
from PIL import Image

import torch

# 加载处理器和 VLA
processor = AutoProcessor.from_pretrained("openvla/openvla-7b", trust_remote_code=True)
vla = AutoModelForVision2Seq.from_pretrained(
    "openvla/openvla-7b",
    # attn_implementation="flash_attention_2",  # [可选] 需要 `flash_attn`
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")

# 获取图像输入并格式化提示
image: Image.Image = get_from_camera(...)
prompt = "In: What action should the robot take to {<INSTRUCTION>}?\nOut:"

# 预测动作（7 自由度；为 BridgeData V2 反归一化）
inputs = processor(prompt, image).to("cuda:0", dtype=torch.bfloat16)
action = vla.predict_action(**inputs, unnorm_key="bridge_orig", do_sample=False)

# 执行...
robot.act(action, ...)
```

## **4. MiLAB 的 QUAR-VLA：四足机器人**

QUAR-VLA 是一种针对四足机器人的视觉语言行动模型，主要用于在复杂地形中导航和执行各种任务。四足机器人需要复杂的多关节协调和步态管理，而 QUAR-VLA 能够高效地处理这些任务。

QUAR-VLA 在包含复杂地形导航和运动的数据集上进行训练，这些数据集既包括真实世界的数据，也包括合成数据。

QUART-2 接收一组观察图像和用户语言指令。这些指令被标记化并连接起来，然后传递给预训练的 VLM 以生成离散的动作标记，频率为 2Hz。输出将四足机器人的连续动作空间离散化为 255 个区间，以便于有效的学习和执行。

![Quart model for 4 legged robots especially rescue mission or complex terrains](https://mmbiz.qpic.cn/mmbiz_jpg/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCS9JRiaS1TdX8AquR4nSmct9zVzj51mHjOkRCVXYy6EL8kJicbJLMSfBQ/640?wx_fmt=jpeg&from=appmsg)

## **5. 谷歌 Deepmind 的 ALOHA**

ALOHA（一种低成本开源硬件系统，用于双臂遥操作）旨在以大约 20,000 美元的可承受成本推进机器人遥操作的研究。ALOHA 团队完全开源了硬件设计、3D 打印说明等，以便任何个人都能构建自己的内部副本。它基本上是一个用于机器人操作任务的硬件平台，使用人类进行遥操作，而原始的 ALOHA 并没有原生集成任何 VLA。

![Aloha teleoperation with human in the loop bimanual as colloborator.](https://mmbiz.qpic.cn/mmbiz_png/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCdT0BiaGIfKYTuxSSu5Arh6J1oEVxEcnyfms02jYwggL7W8KKOk2ib2dg/640?wx_fmt=png&from=appmsg)

然而，研究社区将 ALOHA 用作测试平台，以基准测试和评估他们的 VLA 模型在双臂操作任务中的表现，特别是移动 ALOHA、OpenVLA-OFT、π0、RDT-1B 等。

## **6. π0：Physical Intelligence**

π 是Physical Intelligence开发的一种基础视觉语言行动流模型，用于通用机器人控制，有两个变体：π0（Pi-Zero）和 π0 Fast（最新发布了π0.5）。它包含一个约 3B 参数的预训练 Paligemma VLM 模型作为基础骨干网络，以及一个额外的 300M 扩散模型作为动作专家，该动作专家在 π 跨具身机器人数据集上进行训练。VLA 在图像和文本标记的末尾增加了额外的动作和状态标记。该模型使用大规模、多样化的数据集进行预训练。**
**

**![π0: Physical Intelligence Model architecture with a pretrained VLM for vision encoder and diffusion model as action expert](https://mmbiz.qpic.cn/mmbiz_png/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCKNpvLtt6J9qsiczF5icgJACRAJNnUydicfCoXjSWo7lOxMAXIcwlW7Ciaw/640?wx_fmt=png&from=appmsg)**

**VLM**：VLM 使用 SigLIP 作为图像编码器，Gemma 用于语言指令。VLM 无法看到未来的机器人状态/动作标记，防止模型从其预训练知识中对视觉信息产生任何混淆。通过适应这种 VLM，还增加了动作专家，它与 VLM 紧密合作。

**动作专家**：动作专家关注所有之前的视觉/语言/机器人状态标记，这些标记代表了整个场景，以产生上下文条件的动作。与其生成单个离散动作标记不同，它通过使用**条件流匹配**生成连续的动作标记序列（H = 50），以实现平滑且逼真的动作。

动作是n维向量的动作表示，具有大小和方向，可以进行标记化。类似于图像生成扩散模型，流匹配从随机噪声开始（），并迭代地收敛到一系列有意义的运动动作（接近目标：），以产生平滑的运动动作，以适应精巧的手部动作。新动作旧动作步长

大多数现有的VLA使用离散动作标记化，将连续动作转化为自动回归生成的离散标记。但它们在高频实时控制（如50Hz下的π0中效率低下。这使得机器人能够以更高的效率和适应性执行多种任务。**
**

![图片](https://mmbiz.qpic.cn/mmbiz_png/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCtxaKQo8PKD2dPcTciaeiaIajqAWTF7dyQWlMguAoj4NYoZKiavVv8wBibQ/640?wx_fmt=png&from=appmsg)

**π0**-FAST 是 π0 的扩展，与 π0 不同，它以自回归方式工作，并引入了**频率空间动作序列标记化（FAST）**，这是一种使用离散余弦变换（DCT）的新型时间序列压缩方法。FAST 减少了冗余，提高了效率，并增强了动作保真度。

使用 DCT 的连续动作标记从时间域转换到频率域。得到的稀疏矩阵包含低频和高频系数列表，其中低频是缓慢且平滑的变化，而高频成分是快速且突然的变化。对于现实场景，我们通常只需要包含有意义信息的低频成分，而高频成分可以被忽略或进一步压缩。

在基准测试中，即使是 π0 的较小变体，在从简单到复杂的任务中，其性能也大大优于现有的 VLA。

### **π0 代码指南**

克隆 LeRobot 仓库并安装与 π0 相关的依赖项。

```
!git clone https://github.com/huggingface/lerobot.git
%cd lerobot
!pip install -e .

!pip install -e ".[pi0]"
!pip install -e ".[aloha, pusht]"
```

我们需要使用 Hugging Face 登录以访问 PaliGemma，因为这是一个受限制的仓库。

### **推理**

```
from lerobot.common.policies.pi0.modeling_pi0 import PI0Policy
policy = PI0Policy.from_pretrained("lerobot/pi0")
```

在 pusht 或 aloha 上评估预训练的 π0 模型，

```
!python lerobot/scripts/eval.py \
    --policy.path=lerobot/pi0  \
    --env.type=pusht \
    --eval.batch_size=10 \
    --eval.n_episodes=10

"""
{'env': {'episode_length': 300,
         'features': {'action': {'shape': (2,),
                                 'type': <FeatureType.ACTION: 'ACTION'>},
                      'agent_pos': {'shape': (2,),
                                    'type': <FeatureType.STATE: 'STATE'>},
                      'pixels': {'shape': (384, 384, 3),
                                 'type': <FeatureType.VISUAL: 'VISUAL'>}},
         'features_map': {'action': 'action',
                          'agent_pos': 'observation.state',
                          'environment_state': 'observation.environment_state',
                          'pixels': 'observation.image'},
         'fps': 10,
         'obs_type': 'pixels_agent_pos',
         'render_mode': 'rgb_array',
         'task': 'PushT-v0',
         'visualization_height': 384,
         'visualization_width': 384},
 'eval': {'batch_size': 1, 'n_episodes': 1, 'use_async_envs': False},
 'job_name': 'pusht_pi0',
 'output_dir': PosixPath('outputs/eval/2025-04-10/18-27-10_pusht_pi0'),
 'policy': {'adapt_to_pi_aloha': False,
            'attention_implementation': 'eager',
            'chunk_size': 50,
            'device': 'cuda',
            'empty_cameras': 0,
            'freeze_vision_encoder': True,
            'input_features': {},
            'max_action_dim': 32,
            'max_state_dim': 32,
            'n_action_steps': 50,
            'n_obs_steps': 1,
            'normalization_mapping': {'ACTION': <NormalizationMode.MEAN_STD: 'MEAN_STD'>,
                                      'STATE': <NormalizationMode.MEAN_STD: 'MEAN_STD'>,
                                      'VISUAL': <NormalizationMode.IDENTITY: 'IDENTITY'>},
            'num_steps': 10,
            'optimizer_betas': (0.9, 0.95),
            'optimizer_eps': 1e-08,
            'optimizer_lr': 2.5e-05,
            'optimizer_weight_decay': 1e-10,
            'output_features': {},
            'proj_width': 1024,
            'resize_imgs_with_padding': (224, 224),
            'scheduler_decay_lr': 2.5e-06,
            'scheduler_decay_steps': 30000,
            'scheduler_warmup_steps': 1000,
            'tokenizer_max_length': 48,
            'train_expert_only': False,
            'train_state_proj': True,
            'use_amp': False,
            'use_cache': True,
            'use_delta_joint_actions_aloha': False},
 'seed': 1000}"""
```

在自定义数据集上进行微调，

```
!python lerobot/scripts/train.py \
--policy.path=lerobot/pi0 \
--dataset.repo_id=danaaubakirova/koch_test
```

## **7. Figure AI 的 Helix**

Helix 是 Figure AI 开发的一种用于人形控制的闭源通用 VLA 模型，它在约 500 小时的高质量、多机器人数据集上以监督学习的方式进行训练。它提出了一个类似于开源 Groot N1 的首创解耦双系统架构，其中系统 2 负责高级规划，系统 1 负责处理高频低级任务。

尽管 Helix 没有公开的研究论文，但 FigureAI 的公告博客让我们了解了 Helix 如何集成到 Figure F02 人形机器人中。由于 F02 具有人类双足形式因子，这使得机器人能够自然地开门、使用工具、爬楼梯和搬运箱子。

最初，Figure 机器人由 GPT-4o 提供动力，运行如此庞大的模型并不是一个可行的选择，因此团队决定结束与 OpenAI 的合作关系，并开发了自己的内部 VLA 模型。**
**

![图片](https://mmbiz.qpic.cn/mmbiz_png/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCy1xodHgzblIB4OFRgAPbDwZErpsXs2PS6YGqhWI3P8v5OyESyFD4xw/640?wx_fmt=png&from=appmsg)

**单一神经网络**：与以往的方法不同，Helix 使用单一的神经网络权重来学习所有行为——抓取和放置物品、使用抽屉和冰箱以及跨机器人互动——而无需针对特定任务进行微调。

**来自 Helix 公告帖**“该系统包含两个主要组成部分，分别是 S2，一个 VLM 骨干网络，以及 S1，一个潜在条件的视觉运动 Transformer。S1 是一个快速模型，运行频率为 200Hz，能够快速适应合作机器人的实时动作，而 S2 是一个慢速思考模型，处理场景的视觉线索和语义目标。

- S2 基于一个 7B 参数的开源、开放权重 VLM，该 VLM 在互联网规模的数据上进行预训练。它处理单目机器人图像和机器人状态信息（包括手腕姿势和手指位置），在将它们投影到视觉语言嵌入空间后。结合指定期望行为的自然语言命令，S2 将所有语义任务相关信息提炼成一个连续的潜在向量，传递给 S1 以调节其低级动作。
- S1 是一个 80M 参数的交叉注意力编码器 - 解码器 Transformer，处理低级控制。它依赖于一个全卷积、多尺度的视觉骨干网络进行视觉处理，该网络完全在仿真环境中进行预训练。虽然 S1 接收与 S2 相同的图像和状态输入，但它以更高的频率处理这些输入，以实现更具响应性的闭环控制。来自 S2 的潜在向量被投影到 S1 的标记空间，并沿着序列维度与 S1 视觉骨干网络的视觉特征连接起来，提供任务调节。”

Helix 以一种方式接受训练，即将视觉场景的原始像素和文本命令映射到连续动作，并使用标准回归损失进行训练。

### **Helix 的亮点：**

- 像 Helix 这样的 VLA 模型允许多个机器人协同工作，并实现与以往任何 VLA 模型相比更精确的灵巧动作和无缝实时协调。
- Helix 是第一个能够控制整个人形机器人上半身的 VLA 模型，包括头部凝视、手腕、躯干姿势和各个手指，且频率很高。
- 即使在分布外的情况下，Helix 也表现出色，无需针对特定任务进行微调。
- 它完全在机器人上运行，功耗低，并且已经在宝马等工厂中商业化部署。

## **8. 英伟达的 GR00T N1**

遵循 Helix 的相同架构和设计原则，英伟达发布了 GR00T N1，这是一个用于通用人形推理和控制的开放基础模型。N1 是一个 2B 参数模型（`eagle2_hg_model`骨干网络），基于 Omniverse 和 Cosmos 的海量合成数据以及人形机器人数据集的真实捕获数据进行训练。预训练策略可以无缝适配跨实体系统。

观察、语言指令和机器人状态被编码为标记，并传递给系统 2 和系统 1 以预测动作标记，这些动作标记可以直接控制机器人。

**系统 2**：VLM 通过视觉和语言指令解释物理世界，通过推理来规划正确的动作。

**系统 1**：一个Diffusion Transformer，它遵循系统 2 的指令，通过去噪以 120Hz 的频率产生有意义的平滑且精确的运动动作。

![Working of GR00T N1 with llama and diffusion transformer with a dual system, System 1 and System 2](https://mmbiz.qpic.cn/mmbiz_jpg/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCMNFubduLhX4pDTk11xW1y0OY5FaZVuibhOE5pKfZdtfqz2xsHpgicicicQ/640?wx_fmt=jpeg&from=appmsg)

### **GR00T N1 推理代码演示**

首先，克隆仓库并安装必要的依赖项。

```
git clone https://github.com/NVIDIA/Isaac-GR00T
cd Isaac-GR00T

conda create -n gr00t python=3.10
conda activate gr00t
pip install --upgrade setuptools
pip install -e .
pip install --no-build-isolation flash-attn==2.7.1.post4
```

将 `nvidia/GR00T-N1-2B` 模型加载到 GPU。

```
import os
import torch
import gr00t

from gr00t.data.dataset import LeRobotSingleDataset
from gr00t.model.policy import Gr00tPolicy

# 更改以下路径
MODEL_PATH = "nvidia/GR00T-N1-2B"

# REPO_PATH 是 pip install gr00t 仓库的路径，再上一级
REPO_PATH = os.path.dirname(os.path.dirname(gr00t.__file__))
DATASET_PATH = os.path.join(REPO_PATH, "demo_data/robot_sim.PickNPlace")
EMBODIMENT_TAG = "gr1"

device = "cuda"if torch.cuda.is_available() else"cpu"
```

加载 `gr1_arms_only` 配置的预训练策略，使用 `gr` 具身。

```
from gr00t.experiment.data_config import DATA_CONFIG_MAP

data_config = DATA_CONFIG_MAP["gr1_arms_only"]
modality_config = data_config.modality_config()
modality_transform = data_config.transform()

policy = Gr00tPolicy(
    model_path=MODEL_PATH,
    embodiment_tag=EMBODIMENT_TAG,
    modality_config=modality_config,
    modality_transform=modality_transform,
    device=device,
)

# 打印策略模型架构
print(policy.model)
GR00T_N1(
  (backbone): EagleBackbone(
    (model): Eagle2ChatModel(
      (vision_model): SiglipVisionModel(
        (vision_model): SiglipVisionTransformer(
          (embeddings): SiglipVisionEmbeddings(
            (patch_embedding): Conv2d(3, 1152, kernel_size=(14, 14), stride=(14, 14), padding=valid)
            (position_embedding): Embedding(256, 1152)
          )
          (encoder): SiglipEncoder(
            (layers): ModuleList(
              (0-26): 27 x SiglipEncoderLayer(
                (self_attn): SiglipFlashAttention2(
                  (k_proj): Linear(in_features=1152, out_features=1152, bias=True)
                  (v_proj): Linear(in_features=1152, out_features=1152, bias=True)
                  (q_proj): Linear(in_features=1152, out_features=1152, bias=True)
                  (out_proj): Linear(in_features=1152, out_features=1152, bias=True)
                )
                (layer_norm1): LayerNorm((1152,), eps=1e-06, elementwise_affine=True)
                (mlp): SiglipMLP(
                  (activation_fn): PytorchGELUTanh()
                  (fc1): Linear(in_features=1152, out_features=4304, bias=True)
                  (fc2): Linear(in_features=4304, out_features=1152, bias=True)
                )
                (layer_norm2): LayerNorm((1152,), eps=1e-06, elementwise_affine=True)
              )
            )
          )
          (post_layernorm): LayerNorm((1152,), eps=1e-06, elementwise_affine=True)
          (head): Identity()
        )
      )
      (language_model): LlamaForCausalLM(
        (model): LlamaModel(
          (embed_tokens): Embedding(49164, 2048, padding_idx=2)
          (layers): ModuleList(
            (0-11): 12 x LlamaDecoderLayer(
              (self_attn): LlamaFlashAttention2(
                (q_proj): Linear(in_features=2048, out_features=2048, bias=False)
                (k_proj): Linear(in_features=2048, out_features=2048, bias=False)
                (v_proj): Linear(in_features=2048, out_features=2048, bias=False)
                (o_proj): Linear(in_features=2048, out_features=2048, bias=False)
                (rotary_emb): LlamaRotaryEmbedding()
              )
              (mlp): LlamaMLP(
                (gate_proj): Linear(in_features=2048, out_features=8192, bias=False)
                (up_proj): Linear(in_features=2048, out_features=8192, bias=False)
                (down_proj): Linear(in_features=8192, out_features=2048, bias=False)
                (act_fn): SiLU()
              )
              (input_layernorm): LlamaRMSNorm((2048,), eps=1e-05)
              (post_attention_layernorm): LlamaRMSNorm((2048,), eps=1e-05)
            )
          )
          (norm): LlamaRMSNorm((2048,), eps=1e-05)
          (rotary_emb): LlamaRotaryEmbedding()
        )
        (lm_head): Identity()
      )
      (mlp1): Sequential(
        (0): LayerNorm((4608,), eps=1e-05, elementwise_affine=True)
        (1): Linear(in_features=4608, out_features=2048, bias=True)
        (2): GELU(approximate='none')
        (3): Linear(in_features=2048, out_features=2048, bias=True)
      )
    )
    (linear): Linear(in_features=2048, out_features=1536, bias=True)
  )
  (action_head): FlowmatchingActionHead(
    (model): DiT(
      (timestep_encoder): TimestepEncoder(
        (time_proj): Timesteps()
        (timestep_embedder): TimestepEmbedding(
          (linear_1): Linear(in_features=256, out_features=1536, bias=True)
          (act): SiLU()
          (linear_2): Linear(in_features=1536, out_features=1536, bias=True)
        )
      )
      (transformer_blocks): ModuleList(
        (0-15): 16 x BasicTransformerBlock(
          (norm1): AdaLayerNorm(
            (silu): SiLU()
            (linear): Linear(in_features=1536, out_features=3072, bias=True)
            (norm): LayerNorm((1536,), eps=1e-05, elementwise_affine=False)
          )
          (attn1): Attention(
            (to_q): Linear(in_features=1536, out_features=1536, bias=True)
            (to_k): Linear(in_features=1536, out_features=1536, bias=True)
            (to_v): Linear(in_features=1536, out_features=1536, bias=True)
            (to_out): ModuleList(
              (0): Linear(in_features=1536, out_features=1536, bias=True)
              (1): Dropout(p=0.2, inplace=False)
            )
          )
          (norm3): LayerNorm((1536,), eps=1e-05, elementwise_affine=False)
          (ff): FeedForward(
            (net): ModuleList(
              (0): GELU(
                (proj): Linear(in_features=1536, out_features=6144, bias=True)
              )
              (1): Dropout(p=0.2, inplace=False)
              (2): Linear(in_features=6144, out_features=1536, bias=True)
              (3): Dropout(p=0.2, inplace=False)
            )
          )
          (final_dropout): Dropout(p=0.2, inplace=False)
        )
      )
      (norm_out): LayerNorm((1536,), eps=1e-06, elementwise_affine=False)
      (proj_out_1): Linear(in_features=1536, out_features=3072, bias=True)
      (proj_out_2): Linear(in_features=1536, out_features=1024, bias=True)
    )
    (state_encoder): CategorySpecificMLP(
      (layer1): CategorySpecificLinear()
      (layer2): CategorySpecificLinear()
    )
    (action_encoder): MultiEmbodimentActionEncoder(
      (W1): CategorySpecificLinear()
      (W2): CategorySpecificLinear()
      (W3): CategorySpecificLinear()
      (pos_encoding): SinusoidalPositionalEncoding()
    )
    (action_decoder): CategorySpecificMLP(
      (layer1): CategorySpecificLinear()
      (layer2): CategorySpecificLinear()
    )
    (position_embedding): Embedding(1024, 1536)
  )
)
import numpy as np

modality_config = policy.modality_config

print(modality_config.keys())

for key, value in modality_config.items():
    if isinstance(value, np.ndarray):
        print(key, value.shape)
    else:
        print(key, value)

"""
dict_keys(['video', 'state', 'action', 'language'])
video delta_indices=[0] modality_keys=['video.ego_view']
state delta_indices=[0] modality_keys=['state.left_arm', 'state.right_arm', 'state.left_hand', 'state.right_hand']
action delta_indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] modality_keys=['action.left_arm', 'action.right_arm', 'action.left_hand', 'action.right_hand']
language delta_indices=[0] modality_keys=['annotation.human.action.task_description']
"""
```

使用 LeRobot 兼容的数据架构加载数据集

```
# 创建数据集
dataset = LeRobotSingleDataset(
    dataset_path=DATASET_PATH,
    modality_configs=modality_config,
    video_backend="decord",
    video_backend_kwargs=None,
    transforms=None,  # 我们将通过策略单独处理转换
    embodiment_tag=EMBODIMENT_TAG,
)

"""已使用 gr1 初始化数据集 robot_sim.PickNPlace
"""
import numpy as np

step_data = dataset[0]

print(step_data)

print("\n\n ====================================")
for key, value in step_data.items():
    if isinstance(value, np.ndarray):
        print(key, value.shape)
    else:
        print(key, value)
"""

# step_data.items():

video.ego_view (1, 256, 256, 3)
state.left_arm (1, 7)
state.right_arm (1, 7)
state.left_hand (1, 6)
state.right_hand (1, 6)
action.left_arm (16, 7)
action.right_arm (16, 7)
action.left_hand (16, 6)
action.right_hand (16, 6)
annotation.human.action.task_description ['pick the squash from the counter and place it in the plate']
"""
import matplotlib.pyplot as plt

traj_id = 0
max_steps = 150

state_joints_across_time = []
gt_action_joints_across_time = []
images = []

sample_images = 6

for step_count in range(max_steps):
    data_point = dataset.get_step_data(traj_id, step_count)
    state_joints = data_point["state.right_arm"][0]
    gt_action_joints = data_point["action.right_arm"][0]


    state_joints_across_time.append(state_joints)
    gt_action_joints_across_time.append(gt_action_joints)

    # 我们也可以获取图像数据
    if step_count % (max_steps // sample_images) == 0:
        image = data_point["video.ego_view"][0]
        images.append(image)

# 尺寸为 (max_steps, num_joints == 7)
state_joints_across_time = np.array(state_joints_across_time)
gt_action_joints_across_time = np.array(gt_action_joints_across_time)

# 绘制随时间变化的关节角度
fig, axes = plt.subplots(nrows=7, ncols=1, figsize=(8, 2*7))

for i, ax in enumerate(axes):
    ax.plot(state_joints_across_time[:, i], label="state joints")
    ax.plot(gt_action_joints_across_time[:, i], label="gt action joints")
    ax.set_title(f"Joint {i}")
    ax.legend()

plt.tight_layout()
plt.show()

# 以行形式绘制图像
fig, axes = plt.subplots(nrows=1, ncols=sample_images, figsize=(16, 4))

for i, ax in enumerate(axes):
    ax.imshow(images[i])
    ax.axis("off")
```

右手状态关节

```
predicted_action = policy.get_action(step_data)
for key, value in predicted_action.items():
    print(key, value.shape)

"""
action.left_arm (16, 7)
action.right_arm (16, 7)
action.left_hand (16, 6)
action.right_hand (16, 6)

### 理解动作输出

动作输出中的每个关节形状为 (16, N)，其中 N 是关节的自由度。
- 16 表示动作地平线（对时间步 t, t+1, t+2, ..., t+15 的预测）

对于每个手臂（左和右）：
- 7 个手臂关节：
  - 肩部俯仰
  - 肩部翻滚
  - 肩部偏航
  - 肘部俯仰
  - 腕部偏航
  - 腕部翻滚
  - 腕部俯仰

对于每只手（左和右）：
- 6 个手指关节：
  - 小指
  - 无名指
  - 中指
  - 食指
  - 拇指旋转
  - 拇指弯曲

对于腰部：
- 3 个关节：
  - 躯干腰部偏航
  - 躯干腰部俯仰
  - 躯干腰部翻滚
"""
```

## **9. 谷歌 Deepmind 的 Gemini Robotics**

谷歌 Deepmind 推出了 Gemini Robotics，它由强大的 Gemini 2.0 多模态驱动。这使得机器人能够以 20Hz 的频率进行高频电机控制，执行灵巧任务，并精确完成复杂的日常任务。

该系列包含两个主要模型：

- **Gemini Robotics-ER（具身推理）**：该模型使用原生 Gemini 2.0，而无需在任何机器人动作数据上进行微调。它完全依赖于对机器人概念的卓越空间关系和广泛的互联网预训练知识。
- **Gemini Robotics**：通过在动作数据上进行微调以实现直接机器人控制，扩展了 Gemini Robotics-ER。它是一个单一的统一模型，负责处理感知、推理和动作生成，而无需单独的扩散。

（传统方法：场景理解 → 任务规划 → 运动规划 → 控制 Gemini Robotics 方法：统一模型处理感知、推理和动作）

![Gemini Robotics -ER working with spatial reasoning , pointing etc,](https://mmbiz.qpic.cn/mmbiz_jpg/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCp6EmrgA7dp4w85hgjaRjPWeibWTqmPHcZKAfkva6icXaHejtGx9qo6IA/640?wx_fmt=jpeg&from=appmsg)**架构**：对于高级推理和感知，Gemini Robotics-ER 的精简版本托管在云端。然而，为了补偿网络延迟并生成低级动作序列，动作解码器在机器人的机载计算机上运行。

Gemini 在新情境和环境中表现出良好的泛化能力。

![Performance of Gemini Robotics-ER on 2D Pointing Benchmarks compared with GOT-4o , Claude and Molmo](https://mmbiz.qpic.cn/mmbiz_jpg/TzZ7x6Qk8P2gibLO7h3TU2BHW2XuY9ribCYCkypFYPKz27C6w8Y3zUQWBZkWJ6Ak9wZ4RFic7nVSK66YDZELsu4jg/640?wx_fmt=jpeg&from=appmsg)

## **尾声**

虽然LLM能够帮助完成诸如回答问题或创建内容等数字任务，但视觉语言行动（VLA）模型更进一步。它们使机器人能够执行诸如抓取物体、在复杂环境中导航以及协助家务等活动。这种数字智能与物理行动的结合，使 VLA 模型比单独的 LLM 更具影响力。随着我们迈向一个机器人集成的世界，了解这些技术将如何融入我们的日常生活至关重要。

VLA 是真正的游戏规则改变者，传统机器人一直局限于在结构化环境中执行特定任务，需要为每个任务进行大量的策略训练。然而，经过通用机器人策略（GRP）训练的模型在未见环境中表现出色，并发展出了新兴属性，这主要归功于利用视觉语言模型（VLM）的卓越泛化能力和扩散标记化器的平滑运动。

# **References**

1. https://x.com/shreyasgite/status/1909571659461165057
2. https://github.com/DelinQu/awesome-vision-language-action-model
3. https://www.youtube.com/watch?v=bCkl9hIEb6k
4. https://www.youtube.com/watch?v=-0s0v3q7mBk