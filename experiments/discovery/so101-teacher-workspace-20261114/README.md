# 中央位置工作区资格尝试：0/10，保留失败

固定外部来源与执行前布局见 `plan-before-execution.json`，逐例记录见 `results.jsonl`、
各目录stdout及trace。5个source布局×2目标，均未通过上游物理抓放资格。

事后检查 `posthoc-reset-contact-diagnostic.json` 发现中央source在HOME处与固定指垫
初始穿透15.37mm；原source `[.2,-.075,.014]m`没有这项接触。
这是静态reset诊断，不是随机因果消融，不将失败解释成VLA、TPSC或IK不可达。

驱动程序当时通过内联命令运行，未另存完整脚本；来源hash/布局/原始输出仍保留。
后续可重跑的载体见 `../matched_bc/carrier.py`，它会拒绝初始物体—机器人穿透。
该新脚本不是此尝试的原始执行脚本快照。
