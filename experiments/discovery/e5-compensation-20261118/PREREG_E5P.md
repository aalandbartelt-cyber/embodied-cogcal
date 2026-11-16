# E5′ 预注册：指令侧 q5（wrist_roll）取向补偿

写定于 2026-11-17 01:40 CST，**在任何正式 episode 之前**。本文件哈希写入每个
`contract.json`；正式运行开始后不得修改，任何偏离记入 `RESULTS_E5P.md` 的
"偏离" 节。

## 0. 背景与要回答的问题

E2 已把失败机制钉在接触几何上：

- 15° 偏航、δ~U(0.5,1.5) mm 时成功率 **1/20**；0° 为 19/20（E2，配对 seeds
  12850–12869）。
- ANCHOR_PROBE（零成本 FK）测得：闭合轴方向对 `shoulder_pan` 的增益
  dφ/dq = **−1.0000**、对 `wrist_roll` 为 **+1.0000**；闭合轴竖直分量 1.0000；
  `q5 += 15°` 时 gripper 原点位移 **0.00 mm**（roll 轴过指尖抓取点）。
  即"转腕"在运动学上恰好是绕抓取点的纯取向旋转。
- E4 已把外观与接触几何分开：外观旋转 20/20，接触旋转 0/20。因此 15° 的失败
  不是"方块看起来转了"，而是"指垫闭合轴与方块面法向差 15°"。

E2 的轨迹还显示策略把 q5 停在 `0.433 ± 0.001 rad`（与 θ 无关）：策略输出的是
示教位形关节角，不是绕物体的朝向。于是一个**只改指令、不改策略、不重训**的
干预是可行的：给每个控制目标加上 `target[4] += θ̂`。

**问题**：纯指令侧 q5 补偿能否把 15° 的成功率从 1/20 拉回 0° 的水平？如果
能，C4 的成立就不再依赖"换一个会转腕的策略"，而只需要一个解码端偏置。

## 1. 假设与预测

- **H5′（匹配补偿）**：θ=15°、δ~U(0.5,1.5) mm，q5 指令恒加 +15°，成功率
  **≥ 11/20（>50%）**。
- **H5′-naive（固定偏置不能通用）**：θ=0° 时同样加 +15°，成功率**不高于**
  E2 y0（19/20）。若固定偏置在 0° 也能保持，则"补偿必须知道 θ"这一说法不成立，
  本实验如实报告。
- **H5′-stage（失败阶段迁移）**：补偿后若仍失败，失败应从"闭合未抓住"迁移到
  "放置/释放"（描述性，不作主判据）。

## 2. 条件与配对

20 个配对 seeds（12850–12869），δ 由 E2 的同一函数、同一 key
`[20261118, 10θ, 10, seed]` 生成，即每集 δ∈[0.5,1.5) mm；同一 seed 在 A 与
E2 y15 的 δ 完全相同，B 与 E2 y0 的 δ 完全相同。

| 组 | θ | q5 偏置 | 集数 | 作用 |
|---|---|---|---|---|
| A | 15° | +15°（常量，285 步全段） | 20 | 匹配补偿，主检验 |
| B | 0° | +15°（常量） | 20 | 朴素固定偏置，特异性对照 |

- 0° 自适应条件（偏置 = 0）**不重跑**：E2 y0（19/20，同 seeds、同 checkpoint、
  同 carrier、同 harness）就是它。`target[4] += 0.0` 在浮点上是恒等操作，
  因此"0° 不降"由构造保证，不是由新 episode 保证。正式结果中引用 E2 y0。
- 两组各 20 集，合计 **40 集**，均在注册分母内；smoke 不计入。
- 每集 285 控制步、30 fps、chunk 100 / execute 30、每次 query 用当前两路 RGB +
  当前实测 q；与 E2 完全一致（`rollout_e5p.py` 仅加偏置与 trace 字段）。

## 3. 端点与统计

**P1（主）**：A 成功率 vs E2 y15 的 1/20，单侧 Fisher 精确检验（H1: A > 1/20），
α=0.05；同时报 Wilson 95% CI 与配对 bootstrap（10⁴ 次，按 seed 重采样）。

**P2（特异性）**：B 成功率 vs E2 y0 的 19/20，单侧 Fisher（H1: B < 19/20），
α=0.05。此检验只用于判断"固定偏置是否通用"，不参与 C4 主判据。

**P3（0° 不降）**：逻辑恒等（见 §2），引用 E2 y0 19/20；不设新检验。

**P4（阶段，描述性）**：按 E2 的 `failure_reason` 分类（`two_finger_lift_not_established`
/ `placement_not_achieved` / `release_not_verified` / `penetration_limit_exceeded`），
并统计 `longest_two_finger_lift_s ≥ 0.5` 的比例；与 E2 y15 的 13/20 闭合失败对比。

**P5（操作检查，manipulation check）**：A 组闭合段（step 55–85）实测 q5 中位数应
在 `0.695 ± 0.035 rad`（= 0.433 + 15°）；若偏置没有真正进入执行器，P1 无效并
判 INVALID，不得报"补偿无效"。

**P6（方向核验，零成本）**：用 ANCHOR_PROBE 的 FK 函数对 A 组 step 55 的
`raw_target_rad` 重算闭合轴 φ，确认相对 E2 同 seed 的 φ 增加 15.0°±0.5°。

## 4. 决策规则（运行前写定）

- **COMPENSATION-SUPPORTED**：A ≥ 11/20 **且** P1 单侧 p<0.01 **且** P5 通过。
  此时 C4 保留，E5′ 作为"指令侧补偿足以恢复"的证据；B 的结果只用于限定
  "偏置必须随 θ 变"。
- **NULL**：A ≤ 6/20（≤30%）。C4 删除，论文走"诊断到机制、不做方法"的路线；
  E5′ 作为"运动学对齐不足以恢复"的负结果报告（与 E4 的接触几何结论合起来，
  说明失败不只是指垫朝向，或说明策略对 q5 偏置有闭环反应）。
- **INCONCLUSIVE**：A ∈ 7..10。照实报告点估计与 CI，不扩种子、不追加条件；
  是否再投入由用户决定。
- **特异性旁判**：若 B ≥ A，则"匹配 vs 不匹配"的解释不成立，如实写明；这不会
  推翻 P1，但会削弱"补偿量必须等于 θ"的论断。
- **无效判据**：P5 失败、contract/hash 不一致、worker 未 reset、任何一集缺失，
  整组判 INVALID，不进入上述三档。

## 5. 完整性与排除

- 40 集全部进入分母；无排除、无中途停止、无种子扩增。
- `verify_e5p.py` 检查：contract 的 kind/θ/bias/seeds/prereg hash/checkpoint sha/
  carrier sha/XML sha；每集 285 步、trace 行数、episodes 行数与 summary 一致；
  physics npz 存在且 sha 与 row 一致。
- 任何哈希漂移（carrier、checkpoint、XML、`rollout_e5p.py`、本文件）→ 拒绝。

## 6. 混杂与限度

- **外观**：A 组腕部旋转 15°，方块也旋转 15°；B 组腕部旋转而方块不转。E4 已
  表明"只转外观"20/20，但本实验不能把"腕部外观"与"接触几何"完全分离；B 就是
  几何对照。
- **闭环**：策略在下一次 query 会看到含偏置的实测 q，并可能调整其余关节。测得
  的是"偏置 + 策略反应"的部署量，不是纯开环运动学补偿；这是 C4 想要的量，但
  解释时要写明。
- **常量偏置 vs DIRECTION 草图**：DIRECTION §4 写的是"接近/闭合段加，抬升段
  减回"。本实验注册**全段常量**，理由：(i) `outcome()` 的放置判据不含朝向
  （xy≤35 mm、|z−0.014|≤12 mm，已由 carrier 字节码反汇编核对），保持旋转不会
  仅因方块朝向判失败；(ii) 在夹持中段回零是"再转一次被夹物体"，是第二个干预，
  会混淆补偿检验。若 A 的失败集中在放置，E5″ 再单独测"抬升段回零"。
- **剂量**：只测 +15° 一个点，不做 7.5°/10° 的剂量-反应；"补偿量预测"只在这
  一点上成立。
- **单策略、单物体、20 seeds**：结论限定在 frozen ACT + 28 mm 立方体 + 本
  harness；不外推到其他策略或物体。

## 7. 产物

```
e5-compensation-20261118/
  PREREG_E5P.md            # 本文件（运行前冻结）
  rollout_e5p.py           # 运行器（仅在 E2 基础上加偏置与 trace 字段）
  run_e5p.sh               # 两组串行/并行启动
  verify_e5p.py            # 哈希、完整性、P5/P6 操作检查
  analyze_e5p.py           # P1–P4 统计与逐 seed 表
  RESULTS_E5P.md           # 结果与裁决
  runs/e5p-y15-b15/        # A: contract.json, episodes.jsonl, summary.json, *.trace.jsonl
  runs/e5p-y15-b15-physics/...
  runs/e5p-y0-b15/         # B
  runs/e5p-y0-b15-physics/...
  runs/smoke-*/            # 管线 smoke（2 seeds/组，不进分母）
```

## 8. 与 DIRECTION §4 的偏离（运行前声明）

1. **常量偏置**而非"抬升段减回"：理由见 §6。
2. **40 集**而非 20–40 的下限：A 与 B 各 20，B 是 NOVELTY 风险 5 要求的"naive
   固定偏置"对照；0° 自适应不重跑（恒等）。仍在 20–40 预算内。
3. 不新增 checkpoint、不重训、不改 carrier/XML；`rollout_e5p.py` 的差异仅限：
   `--q5-bias-deg`、seed 校验分支、contract 字段、`target[4] += bias`、trace 的
   `policy_target_rad`/`q5_bias_rad`。
4. smoke 先于正式运行跑 2 seeds/组（12940–12941），只验证管线与 P5，不用于
   选择条件或阈值；smoke 结果写进 `RESULTS_E5P.md` 的"管线检查"节。

## 9. 复现

```bash
cd experiments/discovery/e5-compensation-20261118
PY=/home/mary/miniconda3/envs/cogcal-sim/bin/python
$PY rollout_e5p.py --yaw-deg 15 --delta-center-mm 1 --q5-bias-deg 15 --tag e5p \
  --seed-start 12850 --seed-count 20 --out runs/e5p-y15-b15 \
  --physics runs/e5p-y15-b15-physics
$PY rollout_e5p.py --yaw-deg 0 --delta-center-mm 1 --q5-bias-deg 15 --tag e5p \
  --seed-start 12850 --seed-count 20 --out runs/e5p-y0-b15 \
  --physics runs/e5p-y0-b15-physics
$PY verify_e5p.py
$PY analyze_e5p.py
```

预期墙钟：每组 20 集约 2–3 分钟（与 E2 同量级）。
