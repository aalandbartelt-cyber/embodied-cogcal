# E8 结果：RGB-only θ̂ 在 +15° 成立，−15° 全量注入反而有害

日期：2026-11-18 · 状态：**H1、H2a 通过；H2b 失败；H3 未按字面判定；另做 5 个事后诊断臂**
预注册：[PREREG_E8.md](PREREG_E8.md) · 上游：[E7A](../e7-return-schedule-20261118/RESULTS_E7A.md)

## 裁决

- **H1 SUPPORTED（静态精度）**：在开区间 (−45°, +45°)、2.5° 步长、5 个 reset seed 上，
  `n=175`，`max |θ̂−θ| = 0.90°`（闸门 ≤1.5°），`mean = 0.098°`（闸门 ≤0.5°），
  `p95 = 0.30°`。闭区间版因 ±45° 的 90° 别名被隔离在 `validation/`，
  闸门只读 `validation_open/validation.json`；该处置见预注册 §H1 的边界修正。
- **H2a SUPPORTED（确认性，+15°）**：`est15` **18/20**，正好压线 ≥18/20。
  与 E7A `D330` oracle 20/20 的差异不显著（Fisher p=0.487），与 E5′ 的 oracle 19/20 同侧。
- **H2b FAILED（探索性，−15°）**：`est-15` **13/20**，低于预注册的 ≥18/20。
  估计误差仍只有 `mean 0.10° / max 0.20°`，因此失败**不是估计精度**造成的。
- **H3 未按字面判定**：预注册写“yaw=0°、偏置≈0，成功 ≤5/20”，但同一条款又说
  “偏置应≈0”。yaw=0° 且偏置为 0 就是 nominal 基线，成功应当高，≤5/20 与 H2a
  的前提自相矛盾。实测 `est0` **19/20**，说明估计器在零偏航时没有注入伪偏置；
  这是对“无伪偏置”的支持，但**不是**对预注册字面判据的通过。该条是预注册缺陷，
  应如实记录，不能事后改写成 PASS。
- **事后诊断（非预注册，2026-11-18 同日追加）**：真正的 no-compensation 对照
  （`--bias-mode zero`，保留源位姿 yaw、q5 不加偏置）给出 +15° **6/20**、−15° **17/20**。
  −15° 的全量负偏置（13/20）不如不补偿；−7.5° 半量回到 18/20，−10° 为 15/20，
  +15° 反号偏置为 **0/20**。因此“补偿有害”只在 −15° 的全量/反号剂量上成立，
  且存在明显的方向不对称。

## 结果表

| 臂 | yaw | q5 偏置 | 来源 | n | 成功 | 失败 seed（原因） |
|---|---:|---:|---|---:|---:|---|
| `est15` | +15° | θ̂（RGB） | 预注册 H2a | 20 | **18** | 12856 placement 93.1 mm；12859 lift |
| `nocomp15` | +15° | 0（源位姿仍 +15°） | 事后对照 | 20 | **6** | 13 lift；12854 release（goal 3.0 mm） |
| `oracle15`（E7A `D330`） | +15° | +15° oracle | 上游 | 20 | **20** | 无 |
| `est0` | 0° | θ̂≈0 | 预注册 H3 | 20 | **19** | 12855 placement |
| `est-15` | −15° | θ̂（RGB） | 预注册 H2b | 20 | **13** | 12851/12860/12864/12867 placement（35.2–41.6 mm）；12858/12859/12865 release（17.8–27.0 mm） |
| `nocomp-15` | −15° | 0（源位姿仍 −15°） | 事后对照 | 20 | **17** | 12859/12861 placement（35.1/35.3 mm）；12862 lift |
| `half-15` | −15° | −7.5° 固定 | 事后剂量 | 20 | **18** | 12860/12861 placement（37.3/42.4 mm） |
| `neg10-15` | −15° | −10° 固定 | 事后剂量 | 20 | **15** | 12854/12862/12865/12867/12869 placement（35.2–59.0 mm） |
| `pos15-15` | −15° | +15° 固定（反号） | 事后特异性 | 20 | **0** | 全部 lift（goal error 139–154 mm） |

Fisher 精确检验（双侧）：

- `est15` 18/20 vs `nocomp15` 6/20：**p = 2.44e-4**；vs oracle 20/20：p = 0.487。
- `est-15` 13/20 vs `nocomp-15` 17/20：p = 0.273（方向为**负**，但不显著）。
- `half-15` 18/20 vs `nocomp-15` 17/20：p = 1.000；`neg10-15` 15/20：p = 0.695。
- `est-15` 13/20 vs `pos15-15` 0/20：p = 1.29e-5。
- 把 ±15° 合并，`est` 31/40 vs `nocomp` 23/40：p = 0.094，**合并终点不显著**。
  显著性完全由 +15° 臂贡献。

## 失败形态

- **+15° 的 no-comp 主要死在抓取**：14 个失败中 13 个是
  `two_finger_lift_not_established`，最终物体仍在源位（y≈−0.07），不是放置误差。
  估计偏置把这条从 13 个抓取失败压到 1 个（12859），说明 +15° 的 q5 偏置主要在
  **闭合/抬升阶段**起作用，而不是把物体推到更好的落点。
- **−15° 的 no-comp 已经能抓**：17/20 成功，3 个失败中只有 1 个是 lift；
  两个 placement 失败仅超界 5 mm 左右（35.1/35.3 mm）。这是“本来就接近通过”的臂，
  天花板很低，全量负偏置把 4 个 episode 推到 35–42 mm 的 placement 失败，
  再把 3 个 episode 变成 release 未确认（final z≈0.018–0.022 m，物体已放下但夹爪未满足释放判据）。
- **反号 +15° 在 −15° 源位姿上 0/20，全部 lift 失败**：说明 q5 的方向确实要紧，
  不是“随便加一个偏置都行”；但 −15° 需要的剂量明显小于 +15°，甚至 0 剂量已接近最优。
- 三个 release 失败（12858/12859/12865）都在 330 步内完成放置，仅释放判据未满足；
  E7A 的“330 解除释放尾”是在 +15° 上得到的，不能直接外推到负偏航的接触状态。

## 解释

1. **估计器本身可用**：静态最大误差 0.9°、闭环内最大 0.2°，±15° 的失败都不能归因于
   θ̂ 的幅度或符号错误。RGB-only 估计器在“测量”层面成立。
2. **+15° 的因果链成立**：θ̂=+15.0±0.2° 注入后 18/20，与 oracle +15° 的 20/20 不可区分；
   同时 no-comp 只有 6/20，说明收益来自与 yaw 匹配的 q5 偏置，而不是预算或 seed。
   这把 C4 从“oracle 机制上界”推进到“RGB 估计器闭环也成立（+15°）”。
3. **−15° 暴露方向不对称，而非估计器失败**：全量负偏置比不补偿更差，半量负偏置与不补偿
   持平，反号偏置灾难性失败。最省事的解释是**同一 q5 角度在正负源偏航下对应的抓取/释放
   几何不对称**（两指夹爪的 180° 等价、闭合停位、释放时指尖与物体的接触方向），
   而不是 θ̂ 符号错。现有数据不能区分“负偏航需要更小增益”与“负偏航的最优增益就是 0”；
   这是下一步要单独预注册的假设。
4. **合并终点不显著**：E8 不能主张“RGB-only 补偿在 ±15° 普遍成立”。能主张的是
   “+15° 成立；−15° 全量注入有害，且方向不对称是真实存在的边界条件”。

## 有效性与边界

- **确认性 vs 事后**：`est15`/`est0`/`est-15` 是预注册臂；no-comp、±7.5、−10、反号
  都是看到 −15° 结果后追加的诊断臂。诊断臂的 p 值只作描述，不作确认性推断；
  尤其 `half-15` 的 18/20 不能写成“半量增益已被验证”，它只是在同一 seed 块上的事后最优。
- **H3 的预注册文本有缺陷**：字面“成功 ≤5/20”与“偏置≈0”不相容。`est0` 19/20
  应解读为“零偏航下行为等同 nominal”，而不是“H3 通过”。论文/补充材料必须原样披露。
- n=20/臂、单 seed 块（12850–12869）、单场景、单物体、单 checkpoint；±15° 之外未测。
- 所有臂固定 330 步；没有重跑 285/320。`est-15` 的 3 个 release 失败不能排除是
  负偏航接触状态下的释放尾，但 330 已是当前统一预算。
- 估计器只在本场景橙色立方体、固定光照下验证；颜色阈值、遮挡、换物体未测。
- 反号臂（`pos15-15`）与半量臂使用 `--bias-mode fixed`，是预注册外的诊断扩展；
  `rollout_e8.py` 的默认路径仍是 `est`，注册臂未受影响。

## 复现

```bash
PY=/home/mary/miniconda3/envs/cogcal-sim/bin/python
E=experiments/discovery/e8-theta-estimator-20261118
$PY $E/rollout_e8.py --yaw-deg 15  --bias-mode est  --out $E/runs/est15   --physics $E/physics/est15
$PY $E/rollout_e8.py --yaw-deg 0   --bias-mode est  --out $E/runs/est0    --physics $E/physics/est0
$PY $E/rollout_e8.py --yaw-deg -15 --bias-mode est  --out $E/runs/est-15  --physics $E/physics/est-15
# 事后对照/剂量
$PY $E/rollout_e8.py --yaw-deg 15  --bias-mode zero --out $E/runs/nocomp15 --physics $E/physics/nocomp15
$PY $E/rollout_e8.py --yaw-deg -15 --bias-mode zero --out $E/runs/nocomp-15 --physics $E/physics/nocomp-15
$PY $E/rollout_e8.py --yaw-deg -15 --bias-mode fixed --bias-deg -7.5 --out $E/runs/diag-15-neg7p5 --physics $E/physics/diag-15-neg7p5
$PY $E/rollout_e8.py --yaw-deg -15 --bias-mode fixed --bias-deg -10  --out $E/runs/diag-15-neg10  --physics $E/physics/diag-15-neg10
$PY $E/rollout_e8.py --yaw-deg -15 --bias-mode fixed --bias-deg 15   --out $E/runs/diag-15-pos15  --physics $E/physics/diag-15-pos15
```

每个臂的 contract 记录 `bias_mode`、`bias_deg_fixed`、`yaw_deg`、源/目标哈希与 seed 表；
`runs/*/episodes.jsonl` 为逐集结果，`runs/*/*.trace.jsonl` 为 330 步轨迹。
