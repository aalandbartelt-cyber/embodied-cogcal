# SO-101 实验运行约定

本目录保存 SO-101 数字孪生和真实 follower 的运行说明、配置映射和实验日志索引。

正式运行前必须：

1. 固定 `configs/so101.yaml` 的模型、相机和动作空间；
2. 使用 `probes/definitions/eccbf_factorial.yaml` 生成四格匹配 episode；
3. 保存 Git commit、模型 checkpoint、随机种子和相机标定 ID；
4. 真机先运行 shadow mode 和低速安全轨迹；
5. 将原始 episode 写入外部数据盘，仓库只保存小型索引和汇总结果。

真机试验不允许直接把失败原因归为“认知偏差”。必须先区分策略、相机、通信、动作映射、
执行器和环境重置失败。
