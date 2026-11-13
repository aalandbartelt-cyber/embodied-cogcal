# 部署前本地验证记录

本记录只证明工程接口和可重跑性，不记录 VLA/真机研究结果。

## 环境与输入

- 本地分析：`cogcal` / Python 3.10；不装模型。
- 本地仿真：`cogcal-sim` / Python 3.12、MuJoCo 4.0.1；依赖见 `requirements-sim.txt`。
- 资产：`TheRobotStudio/SO-ARM100@a758567c3978dfeefe282ede0500085a48fe8f78`。
- 场景：`simulation/so101/eccbf_factorial_scene.xml`，SHA256：
  `797f7c99715be8ecb12adf3a2de1c122a1810503873262958500ac8389329255`。
- 控制：六关节 position targets，单位 rad，2 ms 物理步；没有模型推理。

## 实际检查

| 检查 | 本地实际观察 |
|---|---|
| 编译模型 | `nq=20 nv=18 nu=6`，两个自由物体 + 六机器人关节 |
| 重置 | 改变 red/blue/goal 位置实际生效；速度重置为零 |
| 观测 | 仅 RGB 与六机器人关节，不包含物体坐标或目标真值 |
| 动作 | 拒绝 7D 动作、非有限数和越界关节值 |
| 几何判定 | 目标物在区内且静止可通过；错误物体或高速物体不通过 |
| 四格场景 | 从同一 metadata placements 重置，四格初始 qpos 完全一致 |
| EGL | 成功渲染 RGB 与短视频；截图见 `results/figures/so101_readiness.png` |
| 时间 | 30 帧/30 fps，MP4 1.0 秒；日志最后仿真时间 1.000 秒 |
| 日志隔离 | `record_type=step` / `experiment_kind=plumbing_smoke`，不含 `task_success` |

短视频保存在本地 `results/videos/so101_readiness.mp4`，逐步日志在
`results/validation/so101_readiness.steps.jsonl`；两者被 Git 忽略，不作为 source-data 论文数据。

## 重跑

```bash
conda activate cogcal-sim
bash scripts/fetch_so101_assets.sh
export MUJOCO_GL=egl
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/test_so101_scene.py tests/test_rollout_script.py
python scripts/run_so101_scripted_rollout.py \
  --steps 30 --video results/videos/so101_readiness.mp4 \
  --trace results/validation/so101_readiness.steps.jsonl
```

本地物理测试为 16 passed，无 skip。OSMesa 需要系统 `libosmesa6`；WSL 本地缺少该库
时直接设置 `MUJOCO_GL=osmesa` 会失败，不能视为 EGL 失败。云端 simulation job 单独
安装该依赖后再跑物理测试。

## 没有证明的事项

没有证明抓取能力、真实任务准确率、VLA 交互效应或真机一致性。当前放置谓词不含
抓取/抬升/释放历史，不能单独宣称完整 pick-and-place 成功。下一步按
[NEXT_A100.md](../../docs/NEXT_A100.md) 执行模型环境和接口冒烟。
