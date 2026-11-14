# 接续资产审阅

本次依据用户交接要求，先保全并 review 尚未提交的 carrier / scene / scripted IK 资产。
下列问题在后续版本修复；当前 JSON、manifest 和原始轨迹不重写，也不提升为 learned-policy 结果。

## 必须限制的结论

1. `scripted_prefix.py` 的 `by_pair[pair_id][branch]` 在 10 次重复中覆盖旧结果。
   现存 pair 表仅代表每个任务模板的最后一个重复；不能当作所有配对的均值、最大值或独立样本。
   后续必须用 `(pair_id, repeat_id, action_seed)` 完整身份，对每组左右轨迹逐一比较，缺分支则拒绝。
2. `executed_prefix` 当前保存整个 `data.qpos`，含物体位置和四元数。
   no-common 的 executed 最大差混合米、弧度和无量纲值；不能标成关节弧度距离。
   后续关节比较只取六个机器人 joint qpos；物体结果另报。
3. shared-prefix 左右目标区域改变，输入 RGB 也改变；no-common 还改变了物体位置。
   这可以验证各自任务能力，但不能单独识别语言干预。必须另做同一 RGB/q 下交换语言的配对查询。
   同时报告自然 rollout 与固定输入查询，不能用查询敏感性替代任务能力。
4. `kinematic-carry` 的 place 阶段显式把物体重设到目标中心。
   `120/120 place_success` 只验证 predicate 可翻转，不证明路径可执行、碰撞安全或物理抓取。
   0/20 的物理 scripted 放置结果意味着尚无可用的物理教师，不能据此训练并声称 VLA 任务能力。
5. 原渲染脚本在 reset 物体至 goal 后才截图，现存六张 PNG 是 evaluator 阳性样本，并非初始场景图。
6. `ngocthuong2212` 的关节范围吻合不是相机、动力学、夹爪表示等价证据。
   原扫描已列 gripper 范围含 -10，故不能未经该载体源码核验就沿用 SO-100 的 0–100 夹爪适配。
7. 单任务公开 carrier 可验证 loader/训练链路；还未建立两目标任务的策略能力。
   在能力验收前，shared-prefix / uniform-separation 伤害均应记为不可判定。

## 本次实际验证

- 分析环境：153 passed / 11 optional MuJoCo skipped。
- 仿真环境：TPSC、原 SO-101、探针生成共 23 passed。
- 两份 manifest validator 通过；120 条 reset/placement evaluator smoke 在 MuJoCo 4.0.1 重跑通过，
  新输出写入临时路径，未覆盖历史记录。
- JSON 解析与 `git diff --check` 通过。
- 保全 SHA-256：
  - `summary-degree-assumption.json`: `48fce62e85353a8dc0c81214bd8c6f8963ca8e5745226c2b40824af85b4b3a81`
  - `manifest-pilot.jsonl`: `2b351ca811adbe9672973cebe17597827b902a1f1be12210ae5030eda2baf883`
  - `manifest-full.jsonl`: `ced15f2b419275c89cff76516e17d2468324512eb7b32e10002a4148f6be39e5`

## 接续执行

按用户批准顺序：提交现有资产 → 固定 carrier 源码/processor/单位 → 在 A100 加载或训练普通 SmolVLA
→ 20 条自然 rollout 和同输入语言配对查询 → 能力合格才比较 uniform separation。
当前工作机实际 GPU 是 RTX 5070 Ti Laptop 12 GB；A100 访问入口已向用户询问，未提交远端作业。
