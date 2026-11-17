# 科研控制台

在 WSL 的项目根目录运行：

```bash
python3 tools/live-panel/research_panel.py --port 8766
```

在 Windows 浏览器打开 http://127.0.0.1:8766/。默认仅绑定回环地址，不提供写入接口；端口占用时可指定其他端口。停止服务用 Ctrl+C。原 `panel.py`、`index.html`、`state.json` 和 `events.jsonl` 保留不变。

## 主视觉：浏览器内 MuJoCo

顶部是**浏览器里运行的 MuJoCo**（官方 `@mujoco/mujoco` 4.0.1 编译的 WebAssembly）：`sim_view.js` 用 `MjModel.from_xml_string` 载入展平后的场景，按所选 trace 的 `q_after_rad` 写入 `qpos`，`mj_forward` 后由 three.js 以 60 fps 绘制 `geom_xpos/geom_xmat`。视角由 `OrbitControls` 处理，拖动/缩放不经过服务器，因此是连续的。

- **不是示意图**：网格来自 MuJoCo 自己解析的模型（`model.mesh_vert/face`），位姿来自记录；WASM 或 WebGL 不可用时页面报错并留空。
- **场景来源**：`build_scene.py` 把 `simulation/so101/eccbf_factorial_scene.xml` 的 `<include>` 展平为 `vendor/scene/scene.xml`；STL 由 `/api/mj-asset` 从 `third_party/SO-ARM100/.../assets` 只读提供。模型变更后重跑该脚本。
- **依赖**：`vendor/mujoco/`（mujoco.js + mujoco.wasm，约 11 MB）、`vendor/three/`（three.module.js + OrbitControls.js）。均为本地文件，页面不访问外网。
- **刷新与跟随**：运行中每 1 秒拉一次 `/api/live`，画面跟随最新集与最新步；回放时按 82 步/秒推进，时间轴可拖动。
- **尾窗读取**：trace 超过 2 MB 只读最后 2 MB（界面标注 `truncated_head`）。
- **运行中不可见的部分**：物理快照每集结束后一次性保存，运行中不提供逐帧物理曲线；成功率只统计已写入的集。

用假数据检查实时链路（不启动仿真）：

```bash
python3 tools/live-panel/fake_trace_writer.py --root /tmp/lp-fixture --experiment demo \
    --run live --seeds 11 12 13 --steps 330 --fps 82
python3 tools/live-panel/research_panel.py --root /tmp/lp-fixture --port 8799
```

页面每 5 秒只读扫描 `experiments/discovery` 目录的预注册、结果、分析、验证和日志工件；历史事件每 30 秒刷新。实验进程按完整 `argv` 判断（不再依赖截断后的命令行字符串）：参数中的路径按进程 `cwd` 解析后若落在 `experiments/discovery` 内即视为实验进程，相对 `--out` 会解析为绝对路径用于匹配具体运行。扫描仍限于 Linux `/proc`，覆盖范围有限，未列出并不证明没有计算在运行。工件存在不等于实验成功，也不等于验证通过；需逐项核对原始文档、版本和判据。多个子实验的文件可能共处同一目录，页面不自动将其配对。

SO-101 回放仅在视频存在时展示，明确标注为脚本化连通性测试，非实时画面或策略效果。录像不存在时显示空缺。原始工件按受限路径和类型只读提供；不要把服务绑定到公共网络。

验证：`python3 tools/live-panel/test_research_panel.py`。

E7B/E8 进展是人工核对摘要（research-brief.json），标注核对时间及来源；每次请求检查来源 SHA-256，源文件发生变化或缺失时隐藏摘要，等待重新人工核对。摘要不会自动生成或视为实时裁决。

条件运行区在运行中每 1 秒读取所选实验中 episodes.jsonl、contract.json 和所选 *.trace.jsonl；仅统计完整行的唯一 seed，保留重复和缺失计数，计划数来自合同 seeds。轨迹图展示 q_after_rad[4] 与 command_rad[4]，横轴为存在时的 sim_time_s，否则 control_step；缺少字段时不伪造。每文件 episode 最多读取 2 MB、trace 尾窗 2 MB（历史查看上限 8 MB），单实验读取 episode 总量最多 16 MB，最多扫描 2500 个目录、展示 300 个运行，轨迹最多 1500 点。受限或未完整写入时界面标明；仅当运行命令的 --out 精确匹配目录才标活动进程。

已完成集的物理回放：选择控制轨迹后，从同一运行的完整 `episodes.jsonl` 找到对应 seed，只展示其记录的轨迹和 NPZ 哈希均匹配的物理文件；显示物体高度、穿透和双指接触，峰值按全部采样计算。曲线最多 1500 点，短时峰值可能未落入采样点。NPZ 在当前实验中于每集完成后产生，不能当作在线仿真帧。服务默认仍可无 NumPy 启动，缺少 NumPy 时此功能显示不可用。每个 NPZ/轨迹受尺寸限制，读取拒绝 object pickle 及超限解压。

附加验证：`python3 tools/live-panel/test_research_physics.py`（需要 NumPy）。

当前后台运行：已改为常驻用户单元 `~/.config/systemd/user/embodied-cogcal-research-panel.service`（`ExecStart=/usr/bin/python3 -u tools/live-panel/research_panel.py --port 8766`，`Restart=on-failure`，并设置 `WB_SIM_PYTHON` 与 `MUJOCO_GL=egl`）。用 `systemctl --user status|restart|stop embodied-cogcal-research-panel` 管理；已 `enable`，登录后自动启动。渲染子进程由面板按需拉起，日志写入 `/tmp/wb-sim-render.log`。

## 工作站结构（二期）

首屏分三块，各自职责不重叠：

| 区域 | 回答的问题 | 说明 |
|---|---|---|
| 舞台（左） | 「机器人现在是什么姿态」 | 浏览器内 MuJoCo WASM 渲染；`实时 / 录制` 切换，录制模式放 `results/videos` 的归档视频 |
| 右栏 | 「谁在算、能不能动它」 | `运行现场` 列 `/proc` 匹配到的实验进程（不渲染画面）；`仿真控制` 提供 `开始物理 / 暂停 / 单步 / 0.5–2×`，浏览器内 `mj_step` 是**新的 rollout**，不是历史证据 |
| 作业中心（下） | 「下一步能跑什么」 | v0 只做预演：选模板与参数，生成命令、输出目录与预计时长，并显示 GPU 余量；**不启动进程**，执行开关待评审 |
| 研究路线 | 「这个实验走到哪一步」 | 七道门禁判定，红项给出依据；`docs/RESEARCH_STANDARD.md` 是判定依据 |

交互：拖拽旋转、滚轮缩放（距离自适应）、双击复位、`1/3/7/0` 切换前/侧/顶/默认视角、空格播放暂停；拖拽期间自动暂停"跟随最新集"，松手约 2.5 秒后恢复。

测试：`python3 tools/live-panel/test_research_standard.py`（门禁判定）、`test_jobs.py`（模板参数校验），其余四份照旧。
