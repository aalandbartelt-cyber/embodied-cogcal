# 科研控制台

在 WSL 的项目根目录运行：

```bash
python3 tools/live-panel/research_panel.py --port 8766
```

在 Windows 浏览器打开 http://127.0.0.1:8766/。默认仅绑定回环地址，不提供写入接口；端口占用时可指定其他端口。停止服务用 Ctrl+C。原 `panel.py`、`index.html`、`state.json` 和 `events.jsonl` 保留不变。

页面每 5 秒只读扫描 `experiments/discovery` 目录的预注册、结果、分析、验证和日志工件；历史事件每 30 秒刷新。实验进程按完整 `argv` 判断（不再依赖截断后的命令行字符串）：参数中的路径按进程 `cwd` 解析后若落在 `experiments/discovery` 内即视为实验进程，相对 `--out` 会解析为绝对路径用于匹配具体运行。扫描仍限于 Linux `/proc`，覆盖范围有限，未列出并不证明没有计算在运行。工件存在不等于实验成功，也不等于验证通过；需逐项核对原始文档、版本和判据。多个子实验的文件可能共处同一目录，页面不自动将其配对。

SO-101 回放仅在视频存在时展示，明确标注为脚本化连通性测试，非实时画面或策略效果。录像不存在时显示空缺。原始工件按受限路径和类型只读提供；不要把服务绑定到公共网络。

验证：`python3 tools/live-panel/test_research_panel.py`。

E7B/E8 进展是人工核对摘要（research-brief.json），标注核对时间及来源；每次请求检查来源 SHA-256，源文件发生变化或缺失时隐藏摘要，等待重新人工核对。摘要不会自动生成或视为实时裁决。

条件运行区每 5 秒读取所选实验中 episodes.jsonl、contract.json 和所选 *.trace.jsonl；仅统计完整行的唯一 seed，保留重复和缺失计数，计划数来自合同 seeds。轨迹图展示 q_after_rad[4] 与 command_rad[4]，横轴为存在时的 sim_time_s，否则 control_step；缺少字段时不伪造。每文件 episode 最多读取 2 MB、trace 8 MB，单实验读取 episode 总量最多 16 MB，最多扫描 2500 个目录、展示 300 个运行，轨迹最多 1500 点。受限或未完整写入时界面标明；仅当运行命令的 --out 精确匹配目录才标活动进程。

已完成集的物理回放：选择控制轨迹后，从同一运行的完整 `episodes.jsonl` 找到对应 seed，只展示其记录的轨迹和 NPZ 哈希均匹配的物理文件；显示物体高度、穿透和双指接触，峰值按全部采样计算。曲线最多 1500 点，短时峰值可能未落入采样点。NPZ 在当前实验中于每集完成后产生，不能当作在线仿真帧。服务默认仍可无 NumPy 启动，缺少 NumPy 时此功能显示不可用。每个 NPZ/轨迹受尺寸限制，读取拒绝 object pickle 及超限解压。

附加验证：`python3 tools/live-panel/test_research_physics.py`（需要 NumPy）。

当前后台运行：使用 `systemd-run --user --unit=embodied-cogcal-research-panel --working-directory=/home/mary/research/embodied-cogcal /usr/bin/python3 -u tools/live-panel/research_panel.py --port 8766` 创建临时用户服务。用 `systemctl --user status embodied-cogcal-research-panel` 查看，`systemctl --user stop embodied-cogcal-research-panel` 停止；该临时服务不保证 WSL 关闭或用户会话结束后自动启动。
