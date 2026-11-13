# Notebooks

用于探索性分析和图表草稿，内核选 **Python (cogcal)**。

约定：

- 正式图表必须能由 `analysis/scripts/` 里的脚本重跑生成，notebook 只做探索；
- 不把大段数据或模型权重写进 notebook；
- 每个 notebook 顶部写清输入文件、数据版本和结论；
- 需要 GPU/模型推理的实验放 A100，不在本地 notebook 里跑。
