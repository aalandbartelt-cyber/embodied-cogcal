# 科研接手记录（2026-11-17）

## 当前状态

- 工作区 `/home/mary/research/embodied-cogcal`；保留原用户及前序代理所有未提交工件。大量 E7B、E8 原始数据尚未进入 Git，不能将本仓库克隆称作完整实验归档。
- 主张仍限于单一 ACT checkpoint、单场景和物体的仿真证据。E7B 第二训练 seed 的能力门未通过，canonical fallback 不是第二训练复现；E8 H3 原条款矛盾，不能认作通过。
- 负偏航 E8 事后配对复核详见 `experiments/discovery/e8-theta-estimator-20261118/E8_PAIRED_AUDIT_20261117.md`。+15° 与 −15° 的比较和事后选择均须披露；−15° 的 13/20 vs 17/20 不足以证明总体伤害或最优剂量。
- `RESEARCH_FRAMEWORK.md` 和 `proposal/PROPOSAL.md` 的局部补偿残差公式已在本地修正；它们此前均未跟踪，连同其他历史改动保留，不混入本轮提交。多份旧工件以 2026-11-18 命名，但本机 2026-11-17 时已存在；原因尚未确定，不以文件名证明注册先后。

## 可用面板

WSL 中运行 `python3 tools/live-panel/research_panel.py --port 8766`，Windows 浏览器打开 `http://127.0.0.1:8766/`。扫描实验、进程、结果和验证工件；支持真实 episode 与轨迹的只读展示、历史视频回放及来源检查。真实活跃运行下的持续流、三维实时画面和完整求解指标尚未验证或接入。旧 8765 面板及其文件保留，旧状态可能过期。

## 下一步

1. 梳理原始实验工件、代码、模型及存储许可，建立可复现清单与哈希，决定大文件归档策略后再整理既有未提交数据。不得批量覆盖、清理或推送。
2. 根据 `DRAFT_PREREG_NEGATIVE_YAW_DOSE_20261117.md`、`DRAFT_SEED_RUNNER_AUDIT_20261117.md` 继续完善独立 runner、随机数和跨臂契约、种子使用史与资源上限；先冻结协议、代码、校验器，完成独立 smoke，再考虑正式采集。历史事后结果不升级为确认性结论。
3. 接入真实在运行任务的状态与帧/指标流，先核实实际格式、资源和数据来源；对不可获取的进程与工件明确显示未知。用新实验实测持续更新。
4. 排查 GitHub 连接：本地 `origin` 已配置；2026-11-17 经代理连接 GitHub 时 TLS 握手失败，`gh auth status` 报认证未通过，网络异常使其原因未能进一步区分。未 fetch 或 push，旧远端跟踪引用不代表实时状态。网络和身份恢复后先 fetch、审计差异，再选择性同步。

## 核验与版本

- 既有测试：`/home/mary/miniconda3/envs/cogcal/bin/python -m pytest -q`（通过，部分跳过）。
- 面板：`python3 tools/live-panel/test_research_panel.py` 与 `python3 tools/live-panel/test_research_runs.py`，各 4 项通过；E8 est0 接口读取 20 集、19 成功、1 失败，样本轨迹 330 点。
- 科研：只读 E8 配对检查及 60 集物理序列核对通过；其约束见各脚本与审计文档。随机状态未能从旧记录完整重建。
- 本轮独立本地提交包括 `599a948`、`1caa257`、`cf85afb`、`bb3d002`、`8b34ab8`、`d99bbe4`；它们不代表其他未提交历史工件已经归档。
