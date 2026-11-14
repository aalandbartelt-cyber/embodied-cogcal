# SO-101 静态可见性预检

这是**受控渲染/测量可行性**记录，不是策略 rollout、reward-model 结果或新方法验证。
采样 240 个构型，对两种物体状态、front/overhead 两相机得到 744 条记录。
`contact-sheet.png` 是八个极值样本；每行物体放置判据固定。

使用已有 cogcal-sim 环境，在仓库根目录重跑：

```bash
env -u PYTHONPATH PYTHONNOUSERSITE=1 MUJOCO_GL=egl \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/so101/visibility-precheck/render_probe.py
```

依赖是本项目已有 MuJoCo、numpy、Pillow 和固定 SO-101 资产；本次 MuJoCo 4.0.1。
重跑会替换此目录的生成 JSON/PNG，不改变机器人模型、场景或政策代码。

可见比例为红块正常 segmentation 像素数除以同构型下隐藏机器人渲染的红块像素数。
隐藏机器人只改变 evaluator 渲染选项；不是部署输入，也不是物理消除机器人。
负距离接触过滤不证明构型之间存在可执行的无碰撞轨迹。
物体由 reset 设置，未由机器人放置；当前放置谓词不检验抓取、抬升或释放历史。
静态速度为零不证明动力学平衡或硬件稳定。

后续须分别验证当前成功输出语义、模型误判、可达轨迹和闭环影响。
研究问题与强对照见 [机制候选](../../../docs/prior-art/mechanism-first-completion-verification.md)。
