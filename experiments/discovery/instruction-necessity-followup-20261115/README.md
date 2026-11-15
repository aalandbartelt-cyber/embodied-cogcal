# 指令必要性候选的进一步裁决

2026-11-15。**当前发现降为诊断工具，暂移出主推荐；完整选题目标仍未完成。**
没有否定上一轮原始评分组件和SO-101物理共同轨迹的结果。
改变的是立项判断：已有直接评测原理与强简单解法，独立贡献和对成熟方法结论的实际影响仍缺失。

## 对最终研究目标意味着什么

目标是找到有查新依据、能实现、有核心增量，并能在同一SO-101上做仿真—真机验证的方向。
当前资产证明一个具体评测命题可测，但不足以回答“为什么这值得一篇新论文”。
不把增加更多扫描轨迹、改评分或移植完整Isaac环境作为默认下一阶段，也不重启已停止的小BC微调。

## 新近邻对贡献边界的影响

| 一手来源与本次读取范围 | 已覆盖部分 | 尚不能混同的部分 |
|---|---|---|
| [What Are We Actually Benchmarking… v1 §3、A.1、7–8](https://arxiv.org/html/2606.04233v1)；[固定作者源码](https://github.com/ripl/ManipulationBenchmarkAudit/tree/a5ad04ab0f26d46680c4d1c24911c728d37f7d16)的models.py/libero.py | 高分不足以证明被宣称的能力、shortcut诊断已经明确提出并有多基准实验 | probe通过task index获得目标；没有语言编码器不等于完全目标盲。不能把论文probe称为无目标共同扫描 |
| [Learning the Task or Learning the Verifier? v1 §3.2–3.4、4.2](https://arxiv.org/html/2611.08318v1)；[固定作者分支](https://github.com/DAGroup-PKU/PyRUA-Lean/tree/62eb1ce1a9878512356a41631fba6c340f0a8db6)的faithful_criteria/README.md、dual_table.py | 同episode双判据复评、指令/判据不一致、改变判据后优势消失已有直接实证与实现 | 我们的共同轨迹可能完全合法；无法识别语言依赖不必等于判据违背指令。不能直接套用“假成功”标签 |
| [On Evaluation of Embodied Navigation Agents v1 §4，PDF第3页](https://arxiv.org/pdf/1807.06757v1) | 已反对接近目标即oracle成功停止，建议用智能体DONE时刻评估；主动停止与曾经到达的区别早已有明确规范 | 是导航规范，未自动覆盖InstructMove具体实现反例或真实VLA排序影响；跨领域移植规范本身仍不足作核心增量 |

两篇2026年论文摘要页均只列v1；代码固定revision，未运行或复现其成绩。
新发现的[作者停止监测研究](https://easypapersniper.github.io/projects/blog_post/the_unstoppable_robot/the_unstoppable_robot.html)
也已用禁用成功早停的策略录像比较完成判定。这里只读实验设置与范围，未审计其模型成绩或执行监测器。
上一轮One Word、Inner Monologue、Code as Policies的边界继续有效。

以上不等于“具体共同扫描反例已被同一论文做过”，更不构成正式查新不通过的证明。
足够支持的裁决是：**现有证据没有独立核心增量，不能作为主方向推荐。**

## 完整协议源码多排除了哪个反驳

固定RoboOrchard revision仍为`f2e041e5fabe354c1398ea97c934f603bb65d14d`。
本轮增加检查EnvBuilder、IsaacManagerBasedEnv、TaskBase、PoseResetTerm、canonicalizer及公开eval脚本。
结果在[可重跑静态审计](protocol-static-audit.json)，程序见[audit_protocol.py](audit_protocol.py)。

- `step/reset`显式返回`terminated=None`、`truncated=None`；evaluator将None当False。
  在这条公开环境路径上，没有靠这两个字段对错误对象操作额外失败早停。
- 选定pick的pose-reset遍历全部asset；该reset函数不读role_bindings。
  canonical policy输入仅组织instruction/cameras/manipulators/action_layout，不转发原始`/object`真值组。
  这些是指定函数的语法事实，不是所有scene/reset配置的等价证明。
- evaluator和eval脚本默认1000控制步，选定pick配置30Hz，默认控制时域33.33秒。
  **不是论文实际预算，也不意味着MuJoCo的15.4秒扫描能在原PiperX/Isaac中同速成功。**

因此，“原环境也许一碰错误对象就失败”不能由这两个停止字段支持。
但完整原任务仍未执行：其物体分布、接触力/法向判据、重置物理、实际动作与模型接口均不能由静态审计替代。
不能把排除一个反驳升级为完整基准被攻破。

## 是否值得重新开启这一候选

| 具体主张 | 当前判定 | 有资格改变判定的证据 |
|---|---|---|
| 去oracle、首选择、加DONE是核心创新 | 否，已有明确先例 | 不能靠换名称恢复 |
| “高分不证明语言理解”是新原理 | 否，shortcut原则已经覆盖 | 需要具体新机制及其增量，不能只换一个基准 |
| 当前InstructMove代码有值得修复的测量风险 | 有限定组件/源码证据，无完整物理攻击 | 原发布协议、同预算、初态与目标信息受控的完整控制器验证 |
| 该风险改变成熟VLA的科学判断 | 未验证 | 有能力策略、完整配对episode与多个强简单对照；展示结论变化而非只复算toy分数 |
| 可作为研究主方向 | 暂不推荐 | 除上述任务后果外，需说明已有commit/严格匹配为何不充分，以及独立贡献是什么 |

真机若重启，应检验同一目标盲序列与停止/验收命题；只展示SO-101能抓两个物体不增加该科学命题的证据。
后续主工作恢复到具体任务失败的问题发现。保留这套审计用于筛选载体，避免再把成功率当语言依赖的充分证据。
尚无候选通过全部门槛，不宣布立项、查新通过或研究完成。

## 复核、来源和失败记录

```bash
/home/mary/miniconda3/envs/cogcal/bin/python \
  experiments/discovery/instruction-necessity-followup-20261115/audit_protocol.py \
  --out /tmp/instruction-protocol-fresh.json
```

输出必须为新路径；只解析缓存源码，不导入或启动Isaac、策略或torch。
来源SHA、固定revision、读取范围及访问失败分别保存在本目录的source manifests与[reading-scope.json](reading-scope.json)。
ANU的R2R PDF经web首次可读，后续find与直接下载超时；本轮不以它支撑额外结论。
2018规范HTML只有PDF占位，改用成功下载的原PDF读取§4；不是HTML全文审计。
没有成功访问Google Scholar结果页，不声称穷尽检索，也不把未检到当无人做过。
用户参考文章、原始TPSC记录、旧反例结果及官方XML均保留。

[本轮验证记录](verification.json)：29份来源SHA核对、全新路径静态审计结果一致、Ruff与diff检查通过；
上一轮除README接续提示外的50份已跟踪资产与HEAD逐字节一致，7份指定原始结果SHA保持一致。
这些验证针对审计产物，不是选题已完成或科研假设已验证。
