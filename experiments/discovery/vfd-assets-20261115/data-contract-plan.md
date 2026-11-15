# 只读资产资格检查（数据库下载/读取前冻结）

2026-11-15。目标是为研究方向筛选取得可验证的策略/任务证据入口，不新增方法名或训练。
此前已经读取仓库README、tree和metadata；数据库内容尚未读取。

1. 固定Advaitic/drishti commit eeaaaf4dbc0f0d8f15acd52dbd116c84f127c627及obs.db blob尺寸。
2. 只读SQLite完整性/schema；独立统计run/step、终态标签、模型身份、seed、初态、action/chunk、q、图像/embedding引用的可用字段。
3. 核录制脚本及success oracle。明确标签记录与可独立复算任务成功的差别；不从数据库标签推断真实抓取已验证。
4. 检查公开模型是否可绑定同一数据、接口、版本与场景；不同采样draw、不同训练终点或架构不当作同数据独立训练ensemble。
5. 不安装/执行上游，不下载策略权重，不把hook action-head单次spread当原始flow velocity或多次采样分歧。
6. 保存全部资格结论与缺失字段；不挑成功子集、重新训练检测器或使用帧级显著性统计。

裁决范围：可离线复查 ≠ 可复算物理成功 ≠ 可运行成熟策略 ≠ 可研究ensemble VFD。
若VFD所需资产未取得，当前候选降为待核线索；寻找其他具体科学问题，不增加纯解析反例维持该题。
