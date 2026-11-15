# 执行前冻结：共同行为与阶段评分的组件检查

2026-11-15。已读论文和固定源码，尚未运行组件。本计划不是原始论文确认实验。

固定RoboOrchardSim f2e041e5fabe354c1398ea97c934f603bb65d14d；Apache-2.0。
原样AST加载Validator/MetricStore/相关selector/SceneCheckerSuite，以及PickTask.build_validator。
只将物理checker接到显式布尔事实适配器；另外原样调用root-entity reach距离函数检查近邻控制。
不安装Isaac，不执行模型，不声称真实轨迹或原论文结果复现。

固定候选数N=2/3/6，访问顺序正/反。每目标15 reach、4 contact、4 grasp、4 lift步；
中间2步全false，末目标保持lift。blind-scan无语言/目标输入，所有目标使用同一事实序列。
对照：每个语言目标单独informed-single、no-op、reach-only；reach dwell14/15边界。
报告原始4阶段progress与success、首个完成目标、末时刻同时条件、完整事实/评估输出。
不把论文v1的2阶段0.5权重与当前代码4阶段0.25权重混同。

若同一blind事实序列可让所有目标分别成功，只证明评分组件容许共同完成路径。
物理可行性、错误对象交互是否在真实benchmark wrapper另行限制、原始VLA实际受影响，均仍待证。
若首目标/严格末状态等简单规则消除现象，保留为协议诊断，不宣布新算法。
