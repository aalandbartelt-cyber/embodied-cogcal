# 全30Hz图像采集尝试：主动中止，未训练

首条seed4100在匹配物理任务中成功，完成285命令，耗时183.50s。
EGL实际使用Mesa llvmpipe软件渲染，缓存后两视图一次仍约0.620s。
因此在训练前主动SIGINT停止原采集进程，退出130；没有把资源中止写成模型或物理失败。

`collection/intentional-stop.json`记录原进程身份、信号与原因；
`collection/carrier.py.executed-source.txt`、`collection/collect.py.executed-source.txt`是调整前源码快照。
首条npz及逐条hash保留，部分未完成工作不补成完整episode，也未复用进后续数据。
`initial-two-cameras.png`为渲染预览。

新协议为5Hz双相机、30Hz控制，训练/评估使用同样时序；见
`../matched-bc-lowrate-20261114/README.md`。
