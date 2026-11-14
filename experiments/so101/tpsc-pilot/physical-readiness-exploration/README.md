# 单一初态的物理teacher探索原始记录

2026-11-14；这是实际运行的MuJoCo控制器debug，不是VLA结果、方法效果或独立episode成功率。
`inventory.json`保存所有源脚本、summary、原始trace的SHA256及原scene/manifest哈希。

5个变体依次为：全程垂直；approach/lift仅约束位置；显式25×25×70mm宽度控制并保持原质量；
该宽度控制再用-0.17rad关闭目标；更低的垂直approach。每个变体都记录预设的5个侧向offset，
没有只保存最优结果。宽度控制只改该进程内的MjSpec，原XML/manifest不修改。

全部变体基于同一个`shared_left_right_0000_left`初态，不能把25次debug当25个独立样本。
没有变体达到末15个控制点物体高度>0.12m、z范围<5mm且双指接触至少10点的held-lift候选标准。
即使达到，该标准也不验证放置与释放，仍不等于pick-place teacher验收。

`v1_vertical_all`和部分`v5_low_vertical_approach`存在较大IK残差；不能把这些执行当作合格抓取试验，
也不能从数值求解失败推出几何不可达。`v2`的静态图只检查给定目标姿态的几何，物体姿态经过reset，
不是实际动态抓取成功的照片。其余trace中有实际测量关节与命令误差，接触和跟踪仍待解决。

`executed-script.source.txt`是原始执行脚本快照，保留当时绝对工作路径和/tmp输出路径，
不作为通用模块导入；复跑应先改为新的输出目录，避免覆盖本次记录。
第一次宽度控制因MuJoCo返回一元素mass数组导致float转换报错，修正为读取mass[0]后才产生记录；
失败发生在创建输出目录和物理rollout之前，没有删除失败episode来改变结果。

下一步若继续teacher工作，应先定位接触几何、可执行抓取姿态与轨迹，实测合格抓放后再收项目自有示范。
不从本目录的控制器失败推出认知偏差、共享前缀伤害或新方法优势。
