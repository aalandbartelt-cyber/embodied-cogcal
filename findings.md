# 准备阶段事实与边界

- 用户已选择 A100 做模型运行，本地 `cogcal-sim` 仅验证物理资产和日志，不安装 OpenVLA 7B。
- 已有 SO-101 本体资产固定在 a758567c3978dfeefe282ede0500085a48fe8f78。
- 当前 `scene.py` 只有 load/reset；之前回答提到的观测/成功接口未实现，必须补齐再验收。
- OpenVLA LIBERO 输出为该 benchmark 的动作定义；不能直接替换 SO-101 六关节 position actuator。
- 当前 ECCBF 为待证假设和算法原型，尚无真实策略效应、泛化或成功率证据。
- 查新矩阵需核对一手原文；组合维度不同不能自动证明方法新颖。
- 已核六个主要近邻的原始来源；BAS-VLA 等已覆盖残差、门控和真机。ECCBF novelty 未通过。
- raw action 差可能包含合法任务目标变化。现有原型应基于目标相对残差才可能用于校准。
- 本地 EGL：16 项物理/渲染/短视频测试实际通过；分析环境 MuJoCo skip 另报。
- 本地 OSMesa 测试报缺少 libOSMesa 导致 OpenGL.glGetError 为 None；CI job 明确 apt 安装依赖后再验证。
