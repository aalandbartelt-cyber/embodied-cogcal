# 公开小模型入口资格检查：尚未取得绑定原生环境

2026-11-16。不是新方向，也没有下载权重、训练、推理或运行第三方代码。
原因是现有真实记录不能提供受控反事实；继续堆图不能补这一缺口。

## 原数据作者的公开ACT

- 固定`ngocthuong2212/icra_2026_SIM_ONLY` revision
  `5d9827d9b75ab3aa602bd5fc2aa57acc13f20586`，模型卡声明ACT、Apache-2.0、约51.7M。
  六状态/动作、top/front 480×640，chunk100/execute100，MEAN_STD；train_config为100k步。
- 数据源指向原200条`so101_mujoco_follower_7_31`，但训练dataset revision=None。
  不能将当前固定数据revision直接说成作者确切训练版本。
- 不重复20261114的三repo检查；本轮按HF直接链接的GitHub身份列出6个公开repo，
  补看`Practice-Drill-Set-for-MuJoCo`固定`1d0b3951c578a0e5172b1f6bd4b14897632f6910`。
  非截断tree76文件是MuJoCo/官方SO101教学结构，已读根README和文件表；
  未取得原200条录制任务的scene/camera/controller/calibration绑定。
  不声称穷尽每一文件或所有非公开来源。

## 另一组5000条数据与ACT

- 固定数据`szk1ck/so101-pickplace-sim-mujoco` revision
  `1405bdc99f86b646938599155d49b9d339fc987f`，meta写5000条/2380000帧/50Hz、robot_type=so101。
  卡称LeRobot v2.1而meta codebase_version=v3.0，按各文件分别记录；不根据名义六通道称六个arm DOF。
- 模型同名repo固定`3dcc200be7aa0f8b19130586ab7b99d6ff304494`，ACT，front/wrist、
  chunk100/execute100、MEAN_STD、训练50k；dataset revision同样None。
  数据和模型名字相同，不等于能在本项目XML/相机中直接运行或有物理抓取能力。
- HF主页直接链接GitHub `akh1r0ck`，本轮列出18个公开repo；
  相关`colab-lerobot`固定`787c8f1d426d1420daa8d6e43de5a8a244e7457d`，
  非截断tree只有README和一个训练notebook，实际引用另一YCB数据任务。
  notebook只静态检查10个code cells，共3960字符，没有MuJoCo/MJCF/MjModel/XML机器人定义；未执行。
  未资格验证这组5000条数据的原生scene、单位/校准、物理接触、成功判据或matched checkpoint能力。

## 裁决

两个入口都只有小模型/数据元信息，尚未组成可控制、可恢复、已成功完成任务的同体载体。
两个数据页community各一条仅为格式转换bot说明，未提供场景来源；没有向作者发送消息。
当前不因为模型小就下载权重/安装新平台，不将失败的直接移植归因到研究机制。
这项结果阻止两次未经资格验证的重跑，但不代表研究方向完成或所有公开入口不存在。
进一步载体工作必须优先获得明确source scene/接口及任务能力证据，不能再盲猜相机/控制器。

一个可继续核查的独立入口是本地已安装LeRobot0.4.3官方ACT实现，
配合本项目已固定、teacher32/32成功的匹配物理数据，而不是再微调旧小CNN/GRU。
目前只确认模块存在，未验证batch/normalizer/图像时间约定或开始新训练。
若采用，必须先写新固定配置/新测试集/资源与停止条件；普通能力检查不算科研创新或方向确定。
