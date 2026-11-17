# 科研控制台

在 WSL 的项目根目录运行：

```bash
python3 tools/live-panel/research_panel.py --port 8766
```

在 Windows 浏览器打开 http://127.0.0.1:8766/。默认仅绑定回环地址，不提供写入接口；端口占用时可指定其他端口。停止服务用 Ctrl+C。原 `panel.py`、`index.html`、`state.json` 和 `events.jsonl` 保留不变。

页面每 5 秒只读扫描 `experiments/discovery` 目录的预注册、结果、分析、验证和日志工件；历史事件每 30 秒刷新。实验进程扫描 Linux `/proc` 中工作目录或命令指向本项目实验目录的进程，覆盖范围有限，未列出并不证明没有计算在运行。工件存在不等于实验成功，也不等于验证通过；需逐项核对原始文档、版本和判据。多个子实验的文件可能共处同一目录，页面不自动将其配对。

SO-101 回放仅在视频存在时展示，明确标注为脚本化连通性测试，非实时画面或策略效果。录像不存在时显示空缺。原始工件按受限路径和类型只读提供；不要把服务绑定到公共网络。

验证：`python3 tools/live-panel/test_research_panel.py`。

E7B/E8 进展是人工核对摘要（research-brief.json），标注核对时间及来源；每次请求检查来源 SHA-256，源文件发生变化或缺失时隐藏摘要，等待重新人工核对。摘要不会自动生成或视为实时裁决。

条件运行区每 5 秒读取所选实验中 episodes.jsonl、contract.json 和所选 *.trace.jsonl；仅统计完整行的唯一 seed，保留重复和缺失计数，计划数来自合同 seeds。轨迹图展示 q_after_rad[4] 与 command_rad[4]，横轴为存在时的 sim_time_s，否则 control_step；缺少字段时不伪造。每文件 episode 最多读取 2 MB、trace 8 MB，单实验读取 episode 总量最多 16 MB，最多扫描 2500 个目录、展示 300 个运行，轨迹最多 1500 点。受限或未完整写入时界面标明；仅当运行命令的 --out 精确匹配目录才标活动进程。
