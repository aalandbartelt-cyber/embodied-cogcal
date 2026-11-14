# UniSuperMimic：MuJoCo 原生支持与本项目适用性

根据用户提供的“unisupermimic 尝鲜支持 mujoco 原生引擎”线索核验，日期 2026-11-14。
结论：**有明确的 native MuJoCo 后端入口，当前可参考其工程设计；不直接替换 SO-101 语言条件操作主线。**
这是源代码静态评估，未安装其训练环境、未下载 G1 运动库、未跑出训练或真机结果。

## 身份与论文

- 原始工作：[SuperMimic: Scaling Humanoid Whole-Body Control with One Differentiable World Model](https://arxiv.org/abs/2610.28480v2)，Qiayuan Liao 等，2026。
  原始作者代码是 [HybridRobotics/supermimic](https://github.com/HybridRobotics/supermimic)。
- 用户线索对应 [Motphys/Uni-SuperMimic](https://github.com/Motphys/Uni-SuperMimic)，说明其为基于 UniLab 的**独立下游复现**，
  面向 Unitree G1 全身运动跟踪；不能把它当论文作者原始代码。
- 原论文的可微世界模型从刚体模拟器日志学习动力学，再通过想象 rollout 优化跟踪策略。
  这不表示把 MuJoCo 求解器本身变成可微引擎，也不表示它是现成的语言条件 SO-101 操作策略。

## 固定源码证据

核查提交：`d78a5e2bc26ee26c3a94ae10418b7fb9018836ee`。临时只读源码位于 `/tmp/cogcal-unisupermimic-audit`。
逐文件哈希/论文完整作者见 [补充元数据](../../references/supplement-supermimic-metadata.json)。

| 问题 | 直接检查到的内容 | 对本项目的含义 |
|---|---|---|
| 是否真的有 MuJoCo 入口 | [env.py](https://github.com/Motphys/Uni-SuperMimic/blob/d78a5e2bc26ee26c3a94ae10418b7fb9018836ee/src/unisupermimic/tasks/motion_tracking/g1/supermimic/env.py) 导入 `MuJoCoBackend`，支持三后端，统一工厂构造 | 支持证据超出 README 宣传，但尚未由本项目运行验收 |
| 如何选后端 | [mujoco.yaml](https://github.com/Motphys/Uni-SuperMimic/blob/d78a5e2bc26ee26c3a94ae10418b7fb9018836ee/src/unisupermimic/conf/supermimic/task/g1_super_mimic/mujoco.yaml) 设 `training.sim_backend: mujoco` | 其 Hydra 任务可切换后端，不能据此假定不同后端训练成绩相同 |
| 目标任务 | 配置与 `manager_terms.py` 使用 G1 运动库、G1 运动学、关节/身体状态及参考动作 | 当前未见 SO-101 task owner、夹取 evaluator、语言/RGB VLA 适配 |
| 依赖 | `pyproject.toml` 约束 `mujoco~=3.11.0`，依赖 `unilab[mjwarp,mujoco,motrix]>=1.5.1` | 与本地 MuJoCo 4.0.1、A100 OpenVLA 的旧依赖不能混装 |
| 锁文件 | 固定提交 `uv.lock` 中 MuJoCo 3.11.0、UniLab 1.5.1、torch 2.14.1 | 如后续试验，应建立独立环境并记录该锁文件；本轮没有同步依赖 |

原始仓库 [README](https://github.com/Motphys/Uni-SuperMimic/blob/d78a5e2bc26ee26c3a94ae10418b7fb9018836ee/README_zh.md)
提供 `task=g1_super_mimic/mujoco` 与 `unisupermimic-eval --backend mujoco` 入口。
这里只核实命令入口存在，未承诺这些命令在我们机器上已经跑通。

## 值得借鉴的部分

统一后端/任务契约、策略 I/O 和资产身份校验、确定性整段评估、动作库调度及吞吐测量，都能帮助设计可靠实验。
如果后续核心研究需要模型式控制或跨引擎动力学试验，可以单独评估底层 UniLab/UniSim。
目前我们的 SO-101 原生 MuJoCo 场景已经存在，首先需要解决选题与策略/任务能力，增加框架不自动补足这些证据。

若转向使用 SuperMimic 做新研究，须另查“可微学习世界模型、策略想象优化与跟踪”的最近工作；
只更换到 SO-101 或新的模拟器不作为创新。BONES-SEED 跟踪回报也不能与抓取放置任务 SR 横比。

## 后续是否接入的验收条件

只在新选题明确需要后再安排独立 smoke：固定 commit/lock → 小型资产验证 → native MuJoCo 1 环境 →
单段确定性评估 → 比较动作单位、步长、末端/关节响应和真实 wall-clock。
如迁移 SO-101，需要实际实现对应运动学/动作契约、操作任务/终止谓词、数据及策略接口，不能改一个 robot 名称就视作适配。

补充文献导入：[supplement-supermimic.bib](../../references/supplement-supermimic.bib)。它独立于已冻结的 50 条主库，
包含原始论文和下游代码两个条目，避免混淆来源身份。
