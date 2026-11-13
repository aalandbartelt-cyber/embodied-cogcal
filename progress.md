# A100 前准备进度

## 本轮验收

- 仓库基线：9fb61a6，干净；新建集成分支 feat/pre-a100-readiness。
- 启动三个独立智能体：数据完整性、部署/版本前检、查新/实验效度。
- 根 agent 负责 SO-101 场景运行时接口、集成验证与最终交接。
- 已确认 goal 仍 active，目标是部署前准备，不是替代用户明天的 A100 部署。

## 本轮验证进展

- 数据任务：合并原子写出、保护原输入、递归禁越权字段；严格成功标签；拒绝 smoke/step；跨任务/模型/域分组。
- 部署任务：核对 OpenVLA 官方 commit 和约束；接受 CUDA 本地版本；修复非有限磁盘门槛；说明 toolkit、pip constraints 与 pipefail。
- 证据任务：六个主要近邻的原文/发布状态核查，明确创新未证、合法动作改变不是 bias。
- 场景任务：修复 goal 重置；实现不泄漏真值的 RGB/关节观测、六关节 rad 动作和稳定放置谓词。
- 探针：跨种子 ID 唯一；红蓝候选、明确当前任务和可重建 placements；延迟参数未声称已经执行。
- 集成：分析环境 135 passed / 9 optional MuJoCo skipped；独立仿真环境 16 passed、没有跳过；EGL 30帧/1秒 MP4+trace 已实际生成并检查。
- OSMesa 本地缺 libOSMesa，已定位为系统依赖；CI 显式安装后验证，当前尚待云端运行。
- 已完成只读复核：修复 scripted runner 硬链接输出别名，避免误覆盖原场景。
- 最终本地回归：148 passed / 9 optional skipped；独立 EGL 仿真 16 passed；Ruff 与 diff --check 均通过。
- 汇总新增 episode 身份判重，避免重复行污染分母和置信区间；全部无 ID 的旧格式仅兼容，不作为正式实验数据格式。
