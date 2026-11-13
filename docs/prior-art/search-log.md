# 查新检索记录

## 目的

在冻结实验矩阵前识别与 ECCBF 重叠的 VLA 诊断、动作校准、残差补偿、跨本体适配和
SO-101 仿真—真机工作。查新结果用于限定论文声称，不用于事后包装结果。

## 首轮检索式

- `VLA cognitive bias anchoring WYSIATI robot manipulation`
- `VLA language visual conflict benchmark correction`
- `LIBERO-CF ICBench LIBERO-Plus LIBERO-Pro`
- `VLA action calibration residual frozen policy real robot`
- `VLA embodiment conditioned bias semantic execution interaction`
- `SO-101 VLA simulation real robot benchmark`

## 已识别近邻

| 工作 | 覆盖内容 | ECCBF 的待验证差异 |
|---|---|---|
| ICBench | LIBERO 上的语言—动作耦合与受控指令冲突 | 不以冲突诊断本身作为核心；研究语义×执行交互项 |
| LIBERO-CF | 视觉覆盖语言的反事实基准 | 不重新提出同类基准；采用匹配因子设计并接入 SO-101 |
| LIBERO-Plus/Pro | 多维扰动鲁棒性诊断 | 主结果不是扰动排名，而是交互项和选择性校准的准确率提升 |
| BAS-VLA | 冻结 VLA 的任务语义动作校准 | 明确拆分语义、执行和交互分量，并做同一本体仿真—真机验证 |
| CorrectVLA | 语言纠正转为冻结策略的动作偏置 | 使用因子校准和跨执行条件验证，不依赖单句事后纠错 |
| RAGu/其他跨域方法 | 跨域/跨本体适配 | 语义校准参数冻结，只允许本体变换重新估计 |

## 查新门槛

若后续发现某工作已经同时具备“语义×执行交互建模、选择性动作校准、同一本体仿真—真机
验证”，则停止使用 ECCBF 作为主张，改写为可复现的比较研究或选择其他核心假设。

## 复查节点

1. Pilot 完成后：补充新出现的预印本和开源仓库；
2. 正式实验前：冻结 `claim-boundary.md`；
3. 投稿前：复查最近 90 天的论文、项目页和基准更新。
