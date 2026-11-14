# 普通循环BC与每查询清零对照：完整结果

本轮是原CNN BC0/20后的自适应能力调整，不是TPSC、执行补偿或新方法研究。
[执行前计划](../../../docs/plans/2026-11-14-recurrent-bc-capability.md)规定同一模型结构、
同初始化/采样/2000步固定最终权重，测试新seed7100–7119。

| 普通BC | 完整成功 | 双指抬升≥.5s | 失败分解 | 限幅命令向量 |
|---|---:|---:|---|---:|
| GRU跨查询保留hidden | 11/20 | 12/20 | 8未抬升、1未放置 | 295 |
| 同GRU每查询清零 | 4/20 | 7/20 | 13未抬升、2未放置、1未释放 | 164 |

二者均未达事前16/20能力门槛，**不运行补偿干预，不据此确定方向**。
两者参数量均285188，初始化hash与完整episode采样索引hash一致。
同20个初态：carry独成功9对、reset独成功2对、共同成功2对、共同失败7对。
这是单训练seed下的描述，不声称总体统计优势、事实特异性记忆或语义理解。

## 固定接口与训练

只复用原24train/8val成功示范及train-only q/action统计；RGB/q输入，不读时间/phase/物体goal真值。
双相机128→64、5Hz，q历史8个30Hz实测值；GRU128，chunk30、执行6，285控制预算不变。
训练按48个查询时刻取整episode，batch8、Adam .001、2000更新、seed42，不挑best checkpoint。
完整8条val teacher-forced误差仅报告，不选择checkpoint。

| 权重 | SHA256 |
|---|---|
| `checkpoints/recurrent-bc-20261114/carry-2000.pt` | `a5d006d0b9194e671c8f1e008af3006df7e78aa7a831b7ca19a0bc5adfaa653f` |
| `checkpoints/recurrent-bc-20261114/reset-2000.pt` | `809afdc5636c3ea8d4e145088bf6b549e024864b61e5dedc0e10b7820f704f0e` |

两训练CUDA峰值分配均365249536 bytes，更新阶段约24.40/21.75s；不代表端到端峰值或实时能力。
四个阶段均exit0，systemd服务 `cogcal-recurrent-bc-20261114.service`已正常结束，不重启。
代码在 `../recurrent_bc/`，绑定于 `source-hashes.json`，全部episode/chunk/q/hidden摘要原始trace保留。
额外的诊断脚本在主运行后新增，未修改任何已绑定运行源码。

## 诊断及其局限

`training-observability.json`全24train：短q历史非常接近时未来chunk可不同，但最近样本没有完整输入严格相等。
最初仅前两条的严格RGB匹配0命中，之后才扩展连续距离；不写成不可辨识定理、loss下界或新失效。
frame pair不当独立重复。

`grasp-diagnostic-carry.json`在首个gripper command≤.2rad的日志时刻做离线FK：
最终失败组pinch–物体XY误差中位24.17mm，成功组2.49mm。
8条carry未抬升episode均在闭爪前已发生>2mm物体位移。
这不能单独归因于感知，因为手爪可能已把物体推走；只说明“增加历史就够了”不成立。

`color-localization-diagnostic.json`的固定颜色mask与train-only线性映射，初始val8条平均位置误差1.49mm、
最大2.13mm；只说明固定初始视图中存在位置信息，不证明CNN忽略了该信息，也不是硬件精度结果。
在独立计划与新8100–8119测试上做的初始视觉特征对照见相邻 `anchor-bc-20261114/`。

已有文献对非Markov专家、复制前动作捷径与记忆干预提供直接近邻；参见
[新增文献边界](../../../docs/prior-art/feedback-memory-followup.md)。
本轮只为机制研究排查载体，不把普通循环网络、初始缓存或颜色特征列为创新。

## 证据核验

`evidence-audit-v2.json`核查全部60条recurrent/anchor rollout、17100命令与2880chunk，
逐步q连续性、chunk执行索引、限幅、hidden跨episode清零/跨查询携带、初始视觉缓存一致，
以及最终权重、运行源码、4份新增原文缓存和原TPSC保护文件。
早期auditor未显式写zip strict而触发Ruff，数值核验已通过；增加strict=True后另存v2，不覆盖旧记录。
连续双指contact持续时间来自物理evaluator，稀疏日志不能独立重算完整physics接触序列。

```bash
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/miniconda3/envs/cogcal/bin/python \
  experiments/discovery/recurrent_bc/audit_evidence.py --out /tmp/recurrent-evidence-fresh.json
```
