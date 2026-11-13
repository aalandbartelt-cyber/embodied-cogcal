# SO-101 仿真路线

部署交接以 [NEXT_A100.md](NEXT_A100.md) 为准。本文件的模型加载和 scripted rollout
是接口验证；正式策略、动作映射和任务可行性仍需 A100 Pilot。

## 已放入本地环境的资产

本地 `third_party/SO-ARM100/` 已拉取官方仓库，但该目录被 `.gitignore` 忽略，不会把
第三方 CAD、STL、STEP 和模型文件复制进公开仓库。公开仓库只保存获取脚本和版本锁定：

```bash
./scripts/fetch_so101_assets.sh
```

当前固定资产版本：

```text
TheRobotStudio/SO-ARM100
a758567c3978dfeefe282ede0500085a48fe8f78
third_party/SO-ARM100/Simulation/SO101/scene.xml
```

官方模型包含 SO-101 follower 的 MJCF/XML、URDF、网格和两种标定约定。`scene.xml` 默认
引用 `so101_new_calib.xml`；切换旧标定时必须记录修改后的模型文件和 commit。

## 本地先做的三步

### 1. 环境和模型加载

在单独的 `cogcal-sim` 环境中安装 MuJoCo，避免污染只做分析的 `cogcal` 和 OpenVLA
旧版模型环境：

```bash
conda create -y -n cogcal-sim python=3.12
conda activate cogcal-sim
cd ~/research/embodied-cogcal
python -m pip install -r requirements-sim.txt
bash scripts/fetch_so101_assets.sh
python scripts/smoke_so101_mujoco.py
```

### 2. 离屏渲染

```bash
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0
python scripts/smoke_so101_mujoco.py \
  --render \
  --output results/figures/so101_smoke.png
```

本地渲染只用于模型和相机链路调试。正式 OpenVLA/LIBERO 视频仍在 A100 上运行。

### 3. 接入 ECCBF 四格实验

当前仓库提供一个最小桌面场景：

```text
simulation/so101/eccbf_factorial_scene.xml
```

它复用官方 SO-101 follower 模型，加入桌面、红/蓝两个候选物体、绿色目标区域和前视/俯视
相机。它是方法验证场景，不替代正式任务套件；正式实验前仍需把任务选择规则、物体尺寸、
相机参数和初始状态写入 episode metadata。

场景接口位于 `simulation/so101/scene.py`，目前提供：

- `load_scene()`：加载 MJCF 并创建 `MjData`；
- `reset_scene()`：重置机器人和红/蓝物体到确定位置；
- `ObjectPlacement`：显式记录 evaluator-side 物体初始位置；
- `freejoint_qpos()`：统一 free joint 位姿和单位四元数格式。
- `policy_observation()`：只返回 RGB 与六个机器人关节值，不返回物体真值；
- `step_joint_targets()`：只接受六维 rad 关节目标，拒绝 LIBERO 七维动作；
- `evaluate_placement()`：检查指定物体在目标区稳定放置，不推断抓取/抬升/释放历史。

该接口不调用 VLA，也不把成功标签或目标位姿传给策略；它只负责环境状态和评测器侧状态。
明天模型 runner 接入时，策略只能读取配置允许的 RGB、机器人状态和任务指令。

加载并渲染该场景：

```bash
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0
python scripts/smoke_so101_mujoco.py \
  --scene simulation/so101/eccbf_factorial_scene.xml \
  --render \
  --output results/figures/eccbf_factorial_scene.png
```

实验顺序固定为：

```text
SO-101 MJCF 加载
  → 固定相机/工作台场景
  → 生成中性×标准、冲突×标准、中性×扰动、冲突×扰动四格 metadata
  → 用控制器或策略生成 raw action
  → 记录 task_success、动作偏差、执行延迟和失败原因
  → 计算 b_sem、b_exec、b_int
  → 运行 Raw / Semantic-only / Execution-only / Additive / ECCBF / Placebo
```

探针 metadata 由以下命令生成，不需要 A100：

```bash
PYTHONPATH=. python -m probes.generators.eccbf_factorial \
  --num-scenes 10 \
  --seed 42 \
  --output /tmp/eccbf_probe.jsonl
```

每个 seed 的 ID 不同，同一场景四格共享 placements；目标明确为当前 red/blue，旧计划
提示为候选干扰。`command_delay_control_steps` 的 0/3 参数尚待策略 runner 施加，不能
把 JSONL 生成当成已完成因子干预。场景布局记录只给环境构造器，不能直接输入策略。

模型 rollout 与 metadata 的合并由以下脚本完成：

```bash
python -m analysis.scripts.merge_rollouts \
  /tmp/eccbf_probe.jsonl \
  /tmp/a100_rollouts.jsonl \
  --output /tmp/eccbf_merged.jsonl
```

脚本会严格检查 `episode_id` 缺失、重复、额外 rollout、metadata/rollout 字段覆盖和
privileged evaluator 字段。合并成功后再运行 `analysis/scripts/summarize_runs.py`。

在没有 VLA 的情况下，可以先验证动作、视频和日志链路：

```bash
conda activate cogcal-sim
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0
python scripts/run_so101_scripted_rollout.py \
  --steps 120 \
  --video /tmp/so101_scripted_smoke.mp4 \
  --trace /tmp/so101_scripted_smoke.jsonl
```

该 rollout 使用 `record_type=step`、`experiment_kind=plumbing_smoke`，不写 `task_success`；
不计入成功率，也不作为论文结果。视频按 30 fps 的仿真时间采样，逐步记录 `sim_time_s`。
可以验证相同单位的 SO-101 关节策略接口，不能直接替换成 OpenVLA/LIBERO 动作。

## A100 接入点

1. 克隆整个本项目，在 clone 内执行 `bash scripts/fetch_so101_assets.sh`。不能只复制
   `scene.xml`；它依赖相对 include、网格和已固定的上游资产。
2. 按 A100 手册在 OpenVLA 环境跑 LIBERO 次级启动基准，独立保存其任务和本体标识。
3. 为 SO-101 主实验核对兼容策略的 checkpoint、相机、六关节/夹爪单位和训练来源。
   LIBERO 结果不能用来填充 SO-101 探针的 `episode_id`。
4. 真正的策略 episode 结果合并后再汇总；只有 Pilot 有效后才冻结正式矩阵。

本地物理集成测试（需要依赖和资产，均不需 A100）：

```bash
MUJOCO_GL=egl PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/test_so101_scene.py tests/test_rollout_script.py
```

CI 单独安装仿真依赖和 `libosmesa6`，用 CPU OSMesa 运行上述测试；分析测试里的 optional
skip 不能代替该 job。WSL 本地已实测 EGL，未安装 `libOSMesa` 时不要直接切换 OSMesa。
