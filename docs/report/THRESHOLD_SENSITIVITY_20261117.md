# 端点阈值敏感性（首个科研动作）

网格：243 格；判定：|Δ| ≥ 0.1 且 McNemar p < 0.05。

## 结论

- **e5-compensation-20261118** `e5p-y15-b15` vs `e5p-y0-b15`：基线 A>B，稳健；配对 20 集。
- **e5-compensation-20261118** `e5pp-d10` vs `e5pp-d75`：基线 tie，稳健；配对 20 集。
- **e8-theta-estimator-20261118** `est15` vs `nocomp15`：基线 A>B，稳健；配对 20 集。
- **e8-theta-estimator-20261118** `est-15` vs `nocomp-15`：基线 tie，稳健；配对 20 集。
- **e4-appearance-contact-20261118** `e4-collision` vs `e4-deg0`：基线 B>A，稳健；配对 20 集。
- **e4-appearance-contact-20261118** `e4-visual` vs `e4-deg0`：基线 tie，稳健；配对 20 集。

## 逐对比明细

| 实验 | 对比 | 配对 | 基线裁决 | 翻转格数 | 裁决集合 | 最敏感参数 |
|---|---|---|---|---|---|---|
| e5-compensation-20261118 | e5p-y15-b15 vs e5p-y0-b15 | 20 | A>B | 0 | A>B | place_xy_m |
| e5-compensation-20261118 | e5pp-d10 vs e5pp-d75 | 20 | tie | 0 | tie | place_xy_m |
| e8-theta-estimator-20261118 | est15 vs nocomp15 | 20 | A>B | 0 | A>B | place_xy_m |
| e8-theta-estimator-20261118 | est-15 vs nocomp-15 | 20 | tie | 0 | tie | place_xy_m |
| e4-appearance-contact-20261118 | e4-collision vs e4-deg0 | 20 | B>A | 0 | B>A | place_xy_m |
| e4-appearance-contact-20261118 | e4-visual vs e4-deg0 | 20 | tie | 0 | tie | place_xy_m |

## 方法边界（必须与结论同时引用）

1. z 容差（±12 mm）与桌面参考高度（14 mm）不在网格内：它们描述"物体落在桌面上"这一物理事实，不是可调判据。
2. 预算格 330 对 285 步的运行是 `undefined` 而非失败；undefined 不计入翻转。
3. `released` 采用与冻结审计相同的正向尾部计数；参数化实现已与 `audit_act.predicate` 逐集比对（见 `--check`）。
4. `lift_s` 只改"持续多久算抬起"，不改"+0.05 m 才算抬起"这一常数。

## 复现

```bash
python3 analysis/threshold_sensitivity.py --check
python3 analysis/threshold_sensitivity.py --run
```
