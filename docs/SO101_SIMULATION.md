# SO-101 仿真路线

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

在单独的 `cogcal-sim` 环境中安装 MuJoCo，避免污染只做分析的 `cogcal`：

```bash
conda activate cogcal-sim
cd ~/research/embodied-cogcal
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

这一步只生成匹配场景和条件元数据，不声称产生 VLA 结果。A100 明天部署完成后，再把
模型动作填入相同的 episode schema。

## A100 接入点

明天 A100 部署完成后，不重新找模型或重建任务：

1. 将 `scene.xml` 和探针 metadata 复制到 A100 持久盘；
2. 在 A100 OpenVLA 环境验证 EGL 和 baseline；
3. 将 `run_libero_eval.py` 的 rollout 记录转换为本项目 episode 字段；
4. 使用 `analysis/scripts/summarize_runs.py` 生成汇总 CSV；
5. 仅在 Pilot 通过后运行正式矩阵。
