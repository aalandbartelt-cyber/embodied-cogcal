# 执行前：旧SmolVLA只读normalizer/输出幅度审计

本轮不重开训练、调参或rollout，不修改任何旧结果或processor。
问题仅是：公开#5082所猜测的processor不一致/近常量输出，是否有证据足以改变本项目下一动作？

输入固定为既有20k checkpoint的pre/postprocessor小safetensors、其JSON、
固定carrier数据stats.json、原pilot-20k的20条episode和各自trace。

先检查processor action/state mean/std与本地固定数据stats的数值一致性（float32容差1e-6）；
同时绑定原保存的checkpoint manifest SHA，不加载大权重。

对每个episode分别计算：全部记录的预测chunk标准差/1%–99%幅度；
实际发送目标的相同指标；再除以训练数据的对应std/范围作无量纲描述。
全chunk包含未执行tail，不能当实际动作，也不把chunk/帧作独立重复。
现有接口将六通道数值degrees转rad，按这个既有数值映射复算，
不据此补证真实夹爪单位或机器人同体。

不事后制定collapse阈值、不改normalizer扩大动作、不从0/20提取新机制。
输出只支持processor资格/幅度描述；不能证明训练因果、任务改善或查新通过。
