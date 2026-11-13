# ECCBF 执行清单

## Gate N：查新冻结

- [ ] 完成 `docs/prior-art/search-log.md` 的首轮检索记录。
- [ ] 填写 `prior-art-matrix.md` 的每个核心维度。
- [ ] 确认没有工作同时覆盖语义×执行交互、选择性动作校准和同一本体仿真—真机。
- [ ] 在 `claim-boundary.md` 中冻结论文允许使用的表述。

## Gate S0：策略和任务可运行

- [ ] SO-101 MuJoCo 模型加载成功。
- [ ] SO-101 兼容策略完成一个中性任务 rollout。
- [ ] 任务成功率处于 60%–95% 的可测区间。
- [ ] 同一 `task_id + scene_id + seed` 能生成四格匹配 episode。

## Gate S1：交互项存在

- [ ] 完成四格 Pilot，每个 cell 至少 10 episodes。
- [ ] 保存原始 action、成功状态、失败原因和视频索引。
- [ ] 计算 `b_sem`、`b_exec` 和 `b_int`。
- [ ] 若 `b_int` 没有稳定方向，停止使用 ECCBF 作为主标题。

## Gate S2：校准提高准确率

- [ ] 完成 Raw、Reflection、Fixed Residual、Semantic-only、Execution-only、Additive、
  ECCBF、Placebo 和 Oracle 对照。
- [ ] ECCBF 在受扰条件下相对 Raw 提高至少 10 个百分点。
- [ ] ECCBF 优于无交互项 Additive。
- [ ] 中性条件性能下降不超过 5 个百分点。
- [ ] 至少一个 held-out 任务保持提升方向。

## Gate H：硬件采购触发

仿真通过 Gate S2 后立即提交 SO-101 follower 采购申请。采购前准备：

- [ ] 成品/组装件报价；
- [ ] RGB 相机、电源、夹具和备用舵机清单；
- [ ] 固定桌面和低速安全范围；
- [ ] 若同一 VLA 需要示范数据，准备 leader 的第二阶段报价。

## Gate R0：真机安全

- [ ] 完成关节零位和动作限位标定。
- [ ] 固定相机并保存 `camera_calibration_id`。
- [ ] 完成 shadow mode，再允许真实动作。
- [ ] 低速运行中性任务至少 10 次。
- [ ] 所有硬件、通信和重置失败单独标记，不归入认知偏差。

## Gate R1：真机同协议验证

- [ ] 复用仿真中的任务、四格条件和校准接口。
- [ ] 运行 Raw、Semantic-only、Execution-only、Additive、ECCBF、Placebo。
- [ ] 每个主 cell 至少 20 次，每个次任务 cell 至少 10 次。
- [ ] 报告真机成功率、置信区间、动作偏差、触发率和安全停止次数。
- [ ] 只允许重新估计本体变换，不在测试集上重新拟合语义校准。

## Gate P：投稿就绪

- [ ] 主表、交互项图、配对成功率图和失败/成功视频齐全。
- [ ] 仿真和真机使用同一 `task_id`、指标和 calibration variant 命名。
- [ ] 原始 JSONL、汇总 CSV、配置、commit 和 checkpoint 可追溯。
- [ ] 论文讨论中明确真机样本量和外部效度边界。
- [ ] 投稿前复查最近 90 天查新结果。
