# 原scripted控制器为什么不能当物理teacher

2026-11-14。原 `scripted_prefix.py` 和历史JSON不改，本目录是新证据。
这不是VLA实验，也没有证明修正后能抓取。

实际在MuJoCo4.0.1、同一官方XML、同一手臂姿态下设置gripper为0、0.7、1.4 rad，
保存三张EGL渲染与FK数值；见 `observations.json`。图像已人工/视觉检查：

- `gripper-0.0.png` 的两指接近；`gripper-1.4.png` 明显张开。
- 旧脚本却写 `OPEN=0.0`、`CLOSED=1.4`，抓取阶段实际向张开方向运动。
- 旧IK优化的是 `moving_jaw_so101_v1` **body原点**，这是夹爪转轴附近，
  不是官方 `gripperframe` site；本次FK测得二者相距 **0.08206999 m**。
  转轴body原点在不同夹爪角度下不变，而指尖会移动。

因此旧8.6mm IK误差是相对错误抓取参考点的数值，不能解释为指尖已对准物体。
这两项足以阻止把旧脚本当物理teacher，但尚未隔离它们各自对0/20的因果份额；
还存在姿态、碰撞、物体尺寸、速度和控制增益等问题，不能声称两个修正就能解决全部抓取。
原 shared-prefix target相等的代数结论仍可作为脚本结构检查，不能升级成可行物理共享前缀。

后续若需要本项目成对示范，先建立明确的TCP/夹爪约定，在不传送物体的物理抓取中验收teacher，
再采RGB/q/语言/动作数据。不能用kinematic carry补出成功标签，也不能用当前失败解释VLA或TPSC。

渲染器检查另发现本地没有libOSMesa；直接设置OSMesa的import失败，
EGL则实际成功渲染上述三图。故自动pilot队列v1在任何episode开始前取消，v2改用实测EGL。
记录在 `../runs/local-5070ti/pilot-queue-v1-cancelled.json`；训练进程未重启。
