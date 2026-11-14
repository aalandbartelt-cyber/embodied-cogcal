# SmolVLA/SO-101 接口预检

这是公开载体的字段、单位和范围审计，不是策略结果。

数据元信息固定为 `lerobot/svla_so101_pickplace` revision
`f641879e22172be7e8161d5e6c1503c2d2feb657`。该数据包含 50 个 episode、11,939 帧、30 Hz、
6 维 action/state，字段顺序与本项目 SO-101 名称一致：

```text
shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper
```

但该 revision 的 `meta/info.json` 将 `robot_type` 写为 `so100_follower`，数据 README 的旧元数据
也如此标注。数据集名称含 SO-101 不能替代机械本体、校准和关节限位证据；本预检只确认字段兼容性。

该数据集创建于 2025-05-23，早于 LeRobot v0.3.2；旧版 SO follower 的 `activate_calibration()`
明确把关节旋转表示为 degrees（[-180,180]），夹爪为 0–100。当前 `so_follower` 的
`use_degrees=true` 是后来为了兼容旧策略/数据集而保留的默认值。前五个关节的公开值是角度，
夹爪是 0–100 的公开范围。当前 MuJoCo 场景的 `step_joint_targets()` 接受弧度，夹爪也是弧度
hinge，因此不能直接把数据或 SmolVLA 输出传给场景。

重跑（需要已有 `cogcal-sim` 环境）：

```bash
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/smolvla-interface-preflight/audit_interface.py
```

当前审计结果显示：公开 action 范围转换到弧度后，`elbow_flex` 和 `wrist_flex` 的上界超出本
MuJoCo 场景 actuator 范围。它可能来自数据/模型版本、校准范围或场景关节限制差异；在明确
来源前，不能声称已经完成同体仿真，也不能把越界裁剪后的行为当作 VLA 失效。

`dataset-info.json` 和 `dataset-stats.json` 只保存小型 Hub 元数据快照，不含视频或模型权重。
`summary.json` 保存本次 MuJoCo 4.0.1 范围核算和限制。

## 2026-11-14 接续分析

在上一段单位证据基础上，本次补上量化与决策。原“角度”假设成立，elbow/wrist 越界是
**真实范围差异**，不是 `RANGE_M100_100` 归一化误读。

- 越界量：`elbow_flex` **+3.17°**，`wrist_flex` **+4.49°**。
- 数据集元数据 `robot_type=so100_follower`；不能声称 SO-101 同体。
- 决策：只允许作为 carrier smoke test，显式做角度→弧度/gripper 适配并报告 clip；
  TPSC 的同体实验需要项目自有 SO-101 数据。
- 详见 [range-mismatch-analysis.md](range-mismatch-analysis.md)；原始结果保留为
  [summary-degree-assumption.json](summary-degree-assumption.json)。

