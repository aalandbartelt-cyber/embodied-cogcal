# 本轮原文核查记录

状态：仍无合格研究方向；此文不是查新报告或完整复现。

## 已读边界

- GRASP v1 §III-A式2–11与实验超参数段：确认lambda_geo=.15、rho_geo=.3、
  beta_rel=.1、rho_rel=.1、2000步warmup、10步采样。没有假定公开权重或实现已取得。
  [原文](https://arxiv.org/html/2610.23123v1)。
- RFM v3 §3.1式3–10、附录A的CFM等价证明：二次内积在给定(t,x)的同一切空间中，
  对隐藏target线性展开并边缘化，差为与参数无关的常数。
  因此给定(t,x,o)、不依赖隐藏配对target或待优化输出的正定metric，其速度平方损失
  已有直接原理，不能作为新修正。依赖输出且不停止求导的metric不能直接套用该结论。
  这不是已经证明任意非线性clean-action配对损失也等价。
  [原文](https://arxiv.org/html/2302.03660v3)。
- Preconditioned FM最新v5 §2–4：中间协方差决定特定Gaussian/linear predictor的收敛，
  mixture部分有perfect component assignment假设；先可逆变换target再做标准FM，采样后逆变换。
  不把其特定理论扩写成任意神经网络定理，也不将本文受限检查当其反例。
  [原文](https://arxiv.org/html/2603.02337v5)。
- KADP作者站PDF §IV-A/B式6–10及Algorithm1/2：在joint空间加噪再经FK回到node空间，
  网络预测node clean sample，训练MSE；训练用冻结MLP IK，推理改用优化IK，节点误差加权。
  这是表示/加噪/映射设计，不将其简单说成GRASP的同一配对FK辅助项。
  PDF署名仍Anonymous Author(s)，项目页列具名作者且记RA-L接收，按文件分别标明，未拼版本。
  [作者PDF](https://kinematics-aware-diffusion-policy.github.io/docs/manuscript.pdf)。
- STG-DP正式CVPR2025 PDF §3.3.4–3.4式15–23：额外joint回归和FK编码HR作为pose diffusion条件，
  最终loss为lambda*LEE+(1-lambda)*Ljoint。不能从“differentiable kinematics”关键词推成
  已完全覆盖GRASP随机配对clean-action目标。通用运动学监督优势已有，仍无新方法增量。
  [正式PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Lv_Spatial-Temporal_Graph_Diffusion_Policy_with_Kinematic_Modeling_for_Bimanual_Robotic_CVPR_2025_paper.pdf)。
- KStar官方GitHub固定`cb0e850afcb2286873c1d9ec9ad5bd92679cbd46`：
  完整非截断tree仅24个文件；README说明公开范围为plugins，非完整研究代码。
  其指向的`src/utils/model_utils.py`本轮全文只读，含通用layer/pose helpers和pk import，
  未见完整FK正则训练/端到端runner；tree也未见URDF/权重。
  这只是固定公开快照资格边界，未运行代码，不以缺资产否定论文结果或宣称全库不能用。
  [固定源码](https://github.com/iLearn-Lab/CVPR25-KStar-Diffuser/tree/cb0e850afcb2286873c1d9ec9ad5bd92679cbd46)。

## 访问诊断

- 首次Python urllib直连RFM在SSL握手报UNEXPECTED_EOF_WHILE_READING；没有产生源文件。
  改用环境已有requests的代理处理后取得574543字节HTML，记录SHA；没有改SSL验证或安装依赖。
- Web工具取得RFM/KADP原文；CVPR官方STG-DP PDF入口返回403，改核作者/官方其他入口，
  未把搜索摘要当全文。
  环境requests随后成功取得同一CVPR官方PDF（2217369 bytes），已转文本阅读；不是原文不可得。
- 独立verifier第一次Ruff报import顺序与循环闭包捕获；检查和运行以换行连续启动，
  因此已有v1数值输出。保留v1脚本/JSON，显式绑定t/w并调整import后v2通过；
  两版数值相同，仅source hash变化。未改原population脚本、计划或预定条件。
  v1源码以`verifier-v1-source.py.txt`逐字节归档，避免把历史诊断源码当活跃程序运行。

## 已执行的最小检查

原参数的一坐标总体场非零梯度得到验证；线性、单解、对称单坐标、关几何项等对照保留。
10步/非对称prior出现一个分位数点的合法带损失；100/1000步两种场的所有1024终点相同。
这不能写成几何监督损坏机器人多解，也不隐藏10步的小差异。
下一步只独立核求解/终点，不扩大lambda/阈值/模式扫描；再据最近邻与任务证据裁决。

## 本轮数学对象与最近邻的差别

RFM：切向速度残差的给定位置二次范数；预条件化：改变可逆表示与运输路径；
显式penalty理论：固定残差及真实ODE端点（另有Euler近似）；
GRASP：带随机配对target的非线性FK/TCP clean估计损失。
这些对象并不完全相同，但不同本身不证明新颖性或值得发论文。
本轮只检查其中一维受限情形能否支持下一科学动作。
GRASP实现/权重尚未核准；原文范数式与实际tensor reduction可能不同，
本轮使用原文平方范数在受限子空间的定义，不称忠实全模型训练复现。
冻结计划写“原文10步Euler”不够精确：仅10步预算取自原文，Euler是本检查选定的积分器，
未核准原实现。保留原计划，明确这项来源边界；不因此改变数值预算或结果。
