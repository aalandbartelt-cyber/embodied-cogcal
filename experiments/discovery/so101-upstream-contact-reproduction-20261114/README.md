# 固定外部SO-101控制器的物理抓放复现

2026-11-14。独立载体资格检查；**不是learned policy、TPSC结果、新方法或真机验证**。
原TPSC的20条0/20、XML、manifest和所有历史raw记录不变。

上游：[FERBIN12/so101-manipulation-eval](https://github.com/FERBIN12/so101-manipulation-eval)，
固定commit `b02b8b2e300733dbe76cead4f3a57425c37955fe`。代码MIT、机器人资产Apache-2.0。
源码缓存在被忽略的`data/discovery/so101-manipulation-eval-20261114/`，未复制到项目公开源码。

## 实际结果

先原样运行place/hover，再只添加接触记录分别复跑；不是4个独立episode或成功率统计。
两次place结果一致：放置XY误差22.308mm，物体落桌且脱离夹爪；hover的XY误差虽只有4.076mm，
但仍高于桌面且未脱离，判定不成功。每条执行9.5s仿真时间、19000个物理步。

| 仪器化场景 | 放置判定 | 抬离桌面50mm且两个独立指垫同时接触的物理步数 | 最长连续时长 | 物体最大z |
|---|---|---:|---:|---:|
| place | 成功 | 5273 | 2.6365s | 0.083498m |
| hover | 失败 | 6361 | 2.6365s | 0.083685m |

原上游contact gate只检查至少一次单指接触，不能证明它注释里所说的全程双指接触；
故额外子类记录**不同指垫ID**，在每一物理步后统计双指/高度，并每33物理步保存实际q/ctrl/物体/接触。
子类只观察，不写qpos、物体位置、控制目标或模型参数。控制器本身只在IK求解和初始reset时写姿态，
正式执行由`mj_step`和位置伺服推进；没有attach/weld/carry传送。
接触gate的跟踪误差下限只是启发式，这里不把它当作通用的物理真实性证明。

## 与项目原模型的差异

读过源码并diff模型后发现，上游在自己的机器人XML中添加pinch-centre site与两个盒状指垫，
设置物体与原夹爪mesh不直接碰撞，以显式contact pair、摩擦2.0与2000Hz求解接触。
使用28mm立方体、20g质量、source=[0.20,-0.075,0.014]m。
这些条件与原TPSC的70mm物体、工作区和官方接触mesh不同，**不能声称完全同一接触模型**，
也没有校准到实物。原官方`third_party`文件未改。

这提供了“有物理接触的SO101 teacher可在当前机器/引擎上运行”的积极可行性证据。
下一步只能在另建且明确版本化的资格场景验证接触/工作区，再收匹配任务示范；不能改写原20条结果。
若采用接触proxy，真机必须检查对应指面、摩擦与载荷，研究结论也必须在实物相同任务上成立。
teacher使用物体/目标真值只是示范生成器；未来learned policy仍只可见RGB/q/语言。

## 复现

已有缓存无需重新clone。新机器先clone上游，并checkout上述精确commit，避免浮动main。
以下输出目录必须不存在：

```bash
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/miniconda3/envs/cogcal-sim/bin/python \
  experiments/discovery/so101-upstream-contact-reproduction-20261114/reproduce_with_contact_trace.py \
  --source data/discovery/so101-manipulation-eval-20261114 \
  --out /tmp/so101-contact-reproduction-fresh
```

运行证据：[仪器化汇总](instrumented/independent-contact-audit.json)、
[原样运行](execution-summary.json)、[source/output哈希](source-and-output-inventory.json)。
`place/hover`是首次原样输出，`instrumented/place/hover`是独立接触记录复跑，均保留。
