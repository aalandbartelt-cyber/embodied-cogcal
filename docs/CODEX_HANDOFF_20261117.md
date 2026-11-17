# 科研接手记录（2026-11-17）

## 当前状态

- 工作区 `/home/mary/research/embodied-cogcal`；保留原用户及前序代理所有未提交工件。E8 的合同和逐集汇总已入库，但 E7B、E8 大量逐步轨迹、物理数组与 checkpoint 等仍为外置工件，不能将本仓库克隆称作完整实验归档。
- 主张仍限于单一 ACT checkpoint、单场景和物体的仿真证据。E7B 第二训练 seed 的能力门未通过，canonical fallback 不是第二训练复现；E8 H3 原条款矛盾，不能认作通过。
- 负偏航 E8 事后配对复核详见 `experiments/discovery/e8-theta-estimator-20261118/E8_PAIRED_AUDIT_20261117.md`。+15° 与 −15° 的比较和事后选择均须披露；−15° 的 13/20 vs 17/20 不足以证明总体伤害或最优剂量。
- `RESEARCH_FRAMEWORK.md` 和 `proposal/PROPOSAL.md` 的局部补偿残差公式已在本地修正；它们此前均未跟踪，连同其他历史改动保留，不混入本轮提交。多份旧工件以 2026-11-18 命名，但本机 2026-11-17 时已存在；原因尚未确定，不以文件名证明注册先后。
- E8 三个历史 runner 版本已从 DeepSeek 事件恢复，与 7 臂原合同的源码 SHA-256 精确匹配；`source_versions/README.md` 和 `E8_SOURCE_INTEGRITY_20261117.md` 记录恢复与边界。当前 runner 只匹配 3 个后续诊断臂。共 162 条旧 episode 的 trace 与 physics 文件已按记录哈希核对。
- `reproducibility-audit-20261117/` 保存固定输入双 worker 的一致性核查及 4 集工具链 smoke。两臂记录的初始条件和实际 q5 注入一致，旧 runner 的估计角字段、RGB 门槛、旧协议哈希缺陷已披露；每臂 2 集不能作科学推断，外置 NPZ 与模型未入 Git。

## 可用面板

WSL 中运行 `python3 tools/live-panel/research_panel.py --port 8766`，Windows 浏览器打开 `http://127.0.0.1:8766/`。扫描实验、进程、结果和验证工件；支持真实 episode、关节轨迹和经哈希核对的已完成集物理高度、接触、穿透回放。面板当前以 systemd 用户临时服务运行，WSL/用户会话终止后的自动恢复未配置。真实活跃运行下的持续流、三维实时画面和完整求解指标尚未验证或接入。旧 8765 面板及其文件保留，旧状态可能过期。

## 下一步

1. 梳理原始实验工件、代码、模型及存储许可，建立可复现清单与哈希，决定大文件归档策略后再整理既有未提交数据。不得批量覆盖、清理或推送。
2. 根据 `DRAFT_PREREG_NEGATIVE_YAW_DOSE_20261117.md`、`DRAFT_SEED_RUNNER_AUDIT_20261117.md` 继续完善独立 runner、随机数和跨臂契约、种子使用史与资源上限；先冻结协议、代码、校验器，完成独立 smoke，再考虑正式采集。历史事后结果不升级为确认性结论。
3. 接入真实在运行任务的状态与帧/指标流，先核实实际格式、资源和数据来源；对不可获取的进程与工件明确显示未知。用新实验实测持续更新。
4. GitHub 连接已恢复：2026-11-17 fetch 成功；本仓库 GitHub 专用凭据助手改为使用已登录的 Windows gh，API 核实当前账号对远端有推送权限。远端仓库为公开仓库，尚未推送；合同和历史提交含本机绝对路径等信息，须先审查公开范围和依赖完整性再决定同步。

## 核验与版本

- 既有测试：`/home/mary/miniconda3/envs/cogcal/bin/python -m pytest -q`（通过，部分跳过）。
- 面板：`python3 tools/live-panel/test_research_panel.py` 与 `python3 tools/live-panel/test_research_runs.py`，各 4 项通过；E8 est0 接口读取 20 集、19 成功、1 失败，样本轨迹 330 点。
- 科研：只读 E8 配对检查及 60 集物理序列核对通过；其约束见各脚本与审计文档。随机状态未能从旧记录完整重建。
- 补充：`check_e8_assets.py` 核验 162 集及恢复的旧源码哈希；smoke 的独立验证和 worker 固定输入测试已通过。推理的固定输入一致不证明跨环境或闭环确定性。
- 本轮独立本地提交包括 `599a948`、`1caa257`、`cf85afb`、`bb3d002`、`8b34ab8`、`d99bbe4`；它们不代表其他未提交历史工件已经归档。

---

# 接管记录（Codex → WorkBuddy，2026-11-17 18:37 起）

> 触发原因：原 Codex 会话（thread `01a1e8ac-…-9a995d1f2454`）在 17:28 因 `usage_limit_exceeded` 中断，恢复时间约 21:43。
> 本节按"基线 / 里程碑 / 决策与理由 / 改动清单 / 遗留问题 / 下一步与交还"六项维护，交还时只需读本节。

## 1. 接管基线（M0，18:52 记录）

- `HEAD = a2468eb`（`docs: update research provenance and connection status`），分支 `main`，**领先 `origin/main` 28 个提交，落后 0**。
- 工作区：9 个已跟踪改动（`DIRECTION.md`、`NOVELTY.md`、`RESULTS_E5P.md`、`findings.md`、`progress.md`、`task_plan.md`、`tools/live-panel/` 三文件），258 个未跟踪项，0 个已暂存。这些是原用户与前序代理的历史工件，**接管期一律不动**。
- 面板：`embodied-cogcal-research-panel.service`（systemd 用户单元）active，`http://127.0.0.1:8766/` 返回 200；旧 `live-panel.service`（8765）亦在运行。
- 环境约束：本轮开始时 `wsl.exe` 被 WorkBuddy 程序黑名单阻断，只能经 `\\wsl.localhost` 读文件；18:46 用户解除后恢复执行。**Windows 侧 git 对该仓库 `core.filemode=true`、`autocrlf=true`，会产生 9 条 0 行差异的假改动，不可用于提交**；所有提交均在 WSL 内完成。

## 2. 里程碑

| 时间 | 编号 | 结论 |
|---|---|---|
| 18:50 | M0 | 基线快照完成；确认 WSL 可执行 |
| 18:52 | M1（A3） | 面板进程识别改为按完整 `argv` 判定；16 项测试全绿；真实短跑验证通过；已提交 `03c8abd` |
| 18:53 | M2（A1） | E4 复核完成：注册对比为双重差分，`both` 计数描述有误；析因重算支持原结论方向；已提交 `3aa5c15` |
| 18:55 | M3（A2） | E8 时间线复原完成：预注册早于全部闭环运行，±45° 修正属"观察后、冻结前"的披露式修订；已提交 `0462485` |
| 19:02 | M4（A5/A7 前置） | 自查发现本轮产物含 61 处绝对路径，已改为仓库相对路径（`c9275c6`）；公开范围审查成文（`b9ccb68`） |

## 3. 决策与理由

1. **先收尾审计、不启动新采集**。理由：中断点恰在 E4/E8 的证据解释层，这些缺陷会污染后续正式剂量实验的设计；新采集成本高且不可回退。否掉的方案：直接开跑负偏航正式实验。
2. **原始实验记录只读**。`PREREG*`、`contract.json`、`episodes.jsonl`、`analysis.json`、`RESULTS*.md` 结论段一律不改；发现的问题以新增审计文档 + `RESULTS.md` 顶部一行勘误指针披露。理由：科学记录的可追溯性高于文字整洁。否掉的方案：直接改写 `RESULTS.md` 结论段。
3. **E4 用析因重算而非重跑**。4 个条件本身就是完整 2×2（外观 × 接触），既有 80 集足以估计主效应，无需消耗仿真。否掉的方案：补跑"只改外观/只改接触"的新臂。
4. **面板修复单独提交并先验证再提交**。用真实短跑（`--out` 相对路径、从仓库根启动）复现原缺陷，修复后同一场景通过。否掉的方案：与文档改动混在一个提交里。
5. **E8 时间线以合同哈希为锚点**。重放会话得到的三个源码哈希与合同逐一吻合，因此采用合同哈希校验，而不是让重放序列自证；其中 `seq 23510` 一条 `edit` 的 `old_string` 未命中，已在文档中披露。
6. **推送前审查**（用户 18:40 决策：审查后推 `main`）。理由：仓库为公开仓库，合同与历史提交含本机绝对路径。

## 4. 改动清单

| 提交 | 内容 | 验证 |
|---|---|---|
| `03c8abd` | `fix: detect experiment processes from full argv and relative --out`：`tools/live-panel/research_panel.py`、`test_research_panel.py`、`test_research_runs.py`、`README-research.md` | `test_research_panel/runs/physics` 共 16 项通过；真实进程识别验证 `process_found=True`、`outputs_ok=True`；服务重启后 8766 返回 200 |
| `3aa5c15` | `research: audit E4 decoupling -- registered contrast is a double difference`：新增 `E4_DECOUPLING_AUDIT_20261117.md`、`recompute_e4_pairs.py`、`recompute_e4_pairs.json`；`RESULTS.md` 加勘误指针 | 重算与 `analysis.json` 四格数字一致；`consistency_problems=[]`；种子/δ 跨条件一致性检查通过 |
| `0462485` | `research: reconstruct E8 prereg and runner timeline from session events`：新增 `E8_TIMELINE_20261117.md`、`e8_timeline.py`、`e8_timeline_events.json`；`E8_SOURCE_INTEGRITY_20261117.md` 补时序段 | `check_e8_assets.py --repo .` 的 `error_count=0`；重放哈希 `00feb89b/2c766676/aab88f97` 与合同逐一吻合 |
| `c9275c6` | `chore: keep E8 timeline evidence repo-relative for publication`：事件表改为仓库相对路径，`~` 替代家目录 | 重新生成后 `/home/mary` 命中 0；四次写入哈希不变 |
| `b9ccb68` | `docs: record public-scope review before the first push`：新增 `docs/PUBLIC_REVIEW_20261117.md` | 392 个跟踪文件；凭据/私钥/Windows 路径 0 命中；`/home/mary` 57 文件 228 处 |

关键结论复述：

- **E4**：`visual − collision` 同时翻转外观与接触，是双重差分；识别依赖 `deg0→visual`（+2/20，McNemar p=0.50）与 `deg0→collision`（−18/20，McNemar p=7.6e-06）。析因主效应：外观 +1.5/20（p=0.125），接触 −18.5/20（p=7.3e-12），交互 −1/20。C2 仍成立，但归因应引用单因素对比；`both` 为 1/20（seed 12895），原文"每颗种子都失败 `both`"不成立。
- **E8**：`PREREG_E8.md` 13:49:19 写入、13:49:57 修正定稿，最早闭环运行 13:50:48；±45° 的 90° 别名在 13:49:21 首轮验证即被观察到，故 H1 容差非完全先验；11 份合同 `prereg_sha256` 全为修正版 `d3825996…`，修正前 `3abfcc15…` 无任何臂使用。

## 5. 遗留问题

**P0（阻塞交还质量）**

1. 面板实时性仍缺：真实运行中的帧流、求解指标流、三维实时画面未接入；当前为每集结束后的 NPZ 回放。需先核实在运行任务的输出格式与资源占用。
2. 推送待决策：本地领先远端 33 个提交。公开范围审查已完成（见 `docs/PUBLIC_REVIEW_20261117.md`）：无凭据、无 Windows 路径、无个人信息，唯一暴露面为合同中的 `/home/mary/...`（57 文件 228 处，不可改写）。推送与否取决于是否接受该路径公开。

**P1（影响解释力）**

3. E7B 第二训练 seed 未过能力门；canonical fallback 不等于第二训练复现。跨策略/跨物体/真机有效性均未建立。
4. 负偏航剂量仍为事后探索性；`DRAFT_PREREG_NEGATIVE_YAW_DOSE_20261117.md` 与 `DRAFT_SEED_RUNNER_AUDIT_20261117.md` 未冻结，独立 runner 未完成。
5. 外置工件（trace、physics NPZ、checkpoint、carrier 字节码）未入 Git，克隆仓库不足以复现。

**P2（工程卫生）**

6. 面板服务为 systemd 用户单元，需 `loginctl enable-linger` 才能在会话结束后自恢复；本轮未改。
7. 仓库 258 个未跟踪项未分类归档；不得批量清理，需先做清单与哈希。

## 6. 下一步与交还指引

**建议顺序**：P0-2（公开审查 → 推送）→ P0-1（面板实时化设计）→ P1-4（冻结剂量协议）→ P1-3（第二 seed）。

**交还时原会话只需**：

1. 读本节 + `experiments/discovery/e4-appearance-contact-20261118/E4_DECOUPLING_AUDIT_20261117.md` + `experiments/discovery/e8-theta-estimator-20261118/E8_TIMELINE_20261117.md`。
2. 跑三条验证：`python3 tools/live-panel/test_research_panel.py`、`python3 experiments/discovery/e4-appearance-contact-20261118/recompute_e4_pairs.py --repo .`、`python3 experiments/discovery/e8-theta-estimator-20261118/check_e8_assets.py --repo .`。
3. `git log --oneline a2468eb..HEAD` 查看本轮三个提交；`git status` 确认接管期未引入新的未提交改动（历史工件保持原样）。

**接管期未触碰**：所有 `PREREG*`、`contract.json`、`episodes.jsonl`、`results` 原始数据、`progress.md`/`findings.md`/`task_plan.md` 等历史未提交工件、`source_versions/` 与 `reproducibility-audit-20261117/` 的既有内容。
