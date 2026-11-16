# 本轮发现记录（不是全文结论）

2026-11-16。检索 robot VLA failed grasp state attractor recovery repeated attempts 2026、SO-101 grasp insertion failure compensation。
新发现一手入口ProbeAct 2606.09740、RESCUE 2610.13516、Backtrack 2610.32941。
摘要层面：ProbeAct声称gripper/EE状态机及重复失败位置的soft CBF；RESCUE直接区分检测与干预价值；
Backtrack已有冻结VLA的轻量回退。必须核原文/代码，不能把普通反复失败检测或恢复门控当创新。
旧MemoryClock/RePlanMem已读边界继续有效。搜索结果也包含二手博客，本轮不用其作技术依据。
尚无新方法推荐；真实固定cohort提取在活跃进程中，未预填观察或因果结论。

接续：327帧/7页固定cohort已读完，真实失败现象异质，不能用更多稀疏图补因果识别。
ProbeAct/RESCUE正文已压缩通用恢复核心；不默认做停滞/CBF新模块。
新查询spatial probing causal motor grounding发现2606.31257、2608.08904、2609.05376等一手入口，
目前仅发现/摘要层面，未将其当全文审查；特别是可解码不等于causal use不是新概念。

载体方面复查已存在的20261114作者source-scan：3个作者repo两README/一空，不能重复当新检查。
本次只审查其他公开入口是否新提供“同一原生scene+checkpoint+日志/接口”，不安装/训练。
网页发现原数据作者的51.7M ACT模型及另一个szk1ck SO101 MuJoCo数据入口；模型小不等于能力/同体已验证。
需要这项资格证据，是因为现有Armnet记录不包含可restorable simulator/policy状态，
无法完成受控原因区分；工程资格不等于科研方向完成。

访问诊断：将缓存树误当原始GitHub schema导致TypeError（旧缓存其实外层包装tree对象）；
随后直接读原source-scan和包装内容，未改旧缓存。Scholar新ProbeAct题名查询429/challenge、0结果卡，
没有成功Scholar检索列表。本轮未取得ProbeAct/RESCUE作者代码链接，不称穷尽GitHub或证明代码不存在。

两个HF dataset community均只有一条Parquet-converter bot讨论，实际latest.raw为格式转换说明，
无录制scene来源。首次提取误用content.raw字段而输出空串；检查schema后使用latest.raw，
未将空串解释为没有评论。原始API JSON全部保留。

2609.05376额外只定向读§III/IV与abs：已有阶段/对象条件视觉grounding干预，ACT及UR3e，
π0.5医械case的prompt/regularized指令不同，不能当公平同信息方法对照。
未由该文取得SO101场景/权重；未把未命中SO101/GitHub字符串当全网不存在的证据。
