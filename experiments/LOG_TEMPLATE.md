# 实验日志模板

每次运行复制一份为 `experiments/runs/YYYYMMDD-HHMM_<short-name>.md`，并填写全部字段。
W1 验收要求“实验日志仓库建立，所有配置可追溯”。

| 字段 | 值 |
|---|---|
| 日期 |  |
| Git commit |  |
| 执行位置 | A100 / 本地（本地只允许分析） |
| 模型 | OpenVLA / OpenVLA-OFT / 其他 |
| 检查点 |  |
| 任务套件 | libero_spatial / libero_object / libero_goal / libero_10 |
| 本体/环境 | SO101-MuJoCo / SO101-real / LIBERO |
| 任务数 |  |
| 每任务 trials |  |
| 随机种子 |  |
| 语义条件 | neutral / conflict |
| 执行条件 | nominal / perturbed |
| 校准变体 | raw / reflection / semantic_only / execution_only / additive / eccbf / placebo / oracle |
| scene_id 配对 |  |
| center_crop | True / False |
| unnorm_key |  |
| 渲染后端 | egl / osmesa / glx |
| 成功数 / 总数 |  |
| 成功率 |  |
| 95% CI |  |
| b_sem / b_exec / b_int |  |
| 触发率 |  |
| 安全停止数 |  |
| 配置路径 |  |
| 日志/视频路径 |  |
| 异常与处理 |  |

## 备注

- 冒烟（每任务 5 次）与正式基线（每任务 50+ 次、3 种子）分开记录；
- 任何超参数、归一化统计、center_crop 改动都要写进“异常与处理”；
- 不把冒烟成功率当论文结果。
