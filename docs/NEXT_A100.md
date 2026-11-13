# 下一步：A100 启动与实验交接

## 当前已验证的范围

本地已验证 SO-101 资产加载、确定性重置、RGB/六关节观测、关节目标执行、基础放置
判定和短视频/逐步日志导出。脚本轨迹是 plumbing smoke，不是 VLA 实验。

| 路线 | 当前状态 | A100 后需要什么 |
|---|---|---|
| OpenVLA 7B / LIBERO | 部署脚本和约束已整理，未在 A100 运行 | 安装、EGL、权重加载和官方 50-episode 冒烟 |
| SO-101 同体主实验 | 本地场景/观测/动作/几何判定通过 | 验证 SO-101 兼容策略、训练数据、归一化与动作单位 |
| ECCBF | 因子效应和校准代数原型 | Pilot 检验交互和准确率收益；不是已成立方法 |
| 查新 | 近邻核查与风险文档 | 阅读最接近工作的正文/代码并人工确认差异，尚未“查新通过” |
| 真机 | 沿用同一任务定义的设计 | 仿真证据成立后采购、标定、适配、同协议验证 |

## A100 平台部署时先做这一项

没有 clone/环境时，从 [A100_DEPLOYMENT.md](A100_DEPLOYMENT.md) 第 0–2 节开始。
已有 clone 时先 `git pull --ff-only origin main`，然后固定本次 commit，不在评测中途升级。

1. 确认分配到 A100，检查驱动与 `nvcc`；选择 CUDA 12.1 devel 工具链。
2. 按手册装独立 Python 3.10 OpenVLA 环境和约束依赖；不要安装 `requirements-sim.txt`。
3. 安装后运行 `pip check` 与 `scripts/a100_preflight.py`。
4. 实测 EGL，下载并记录 OpenVLA-Spatial 模型 revision。
5. 跑 10 个任务 × 5 episodes 冒烟；保存每任务日志、命令、环境、源码 commit 和视频。

回传物：preflight 文本/JSON、`pip check` 输出、首段模型加载日志、冒烟每任务结果及首条
视频路径。不要回传 Hugging Face token。

## 必须保持的接口边界

- LIBERO 的 OpenVLA 输出是 7 维 benchmark 动作；SO-101 场景接受六个关节 position
  targets，单位 rad，夹爪仍是模型 hinge。两者**不能直接互换**。
- LeRobot 的 gripper 0–100 与本模型 hinge 不是同一量纲。硬件实测映射和策略统计尚未确认。
- A100 仅改变计算位置，不会自动让 LIBERO checkpoint 学会 SO-101。SO-101 主线需要本体
  兼容的模型和动作适配；不得把部署适配失败解释为认知偏差。
- 四格 metadata 已给出相同布局、明确当前目标、旧计划干扰提示及 0/3 控制步延迟参数。
  延迟参数是待接入 runner 的协议，**生成 JSONL 不等于已经施加延迟或完成 rollout**。
- 基础 `evaluate_placement()` 检查稳定落在目标区域；完整 pick-and-place 成功还需要
  记录抓取、抬升和释放事件，不能靠预先把物体放入目标来计分。

## 数据交接

```bash
python -m probes.generators.eccbf_factorial \
  --num-scenes 10 --seed 42 --output /path/to/probes.jsonl
```

`scene_metadata.placements` 用于 evaluator 构造环境，`current_target_color` 用于评测。
策略只获取 `instruction`、RGB、机器人观测，不直接接收整个 metadata 记录。
每个 calibration variant 单独运行、单独合并；每 episode 只输出一条最终 result。
逐步 action/qpos trace 另存，不作为成功率的分母。

```bash
python -m analysis.scripts.merge_rollouts \
  /path/to/probes.jsonl /path/to/raw_results.jsonl --output /path/to/raw_merged.jsonl
python -m analysis.scripts.summarize_runs \
  /path/to/raw_merged.jsonl --output /path/to/raw_summary.csv
```

成功标签只接受布尔值或整数 0/1；合并与汇总拒绝逐步日志和 scripted smoke；输出不能
指向输入文件。跨任务、模型和仿真/真机标识存在时分别汇总。

## Pilot 前必须确认

按 [EXPERIMENT_VALIDITY.md](EXPERIMENT_VALIDITY.md) 区分合法目标变化与偏差：
不能把动作变化直接当错误，更不能把正确的新目标动作扣回旧目标。固定策略的输入完全
相同时，仅改变物理参数不会改变第一步预测；闭环效应要记录发生时刻、状态与反馈。

本地准备阶段到这里结束。实际模型 rollout、策略适配、作用大小、样本量修订和真机采购
决定要由 A100 上的证据推进，不预填论文数字。
