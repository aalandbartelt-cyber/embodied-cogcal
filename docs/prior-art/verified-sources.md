# ECCBF 原始来源核验记录

核验日期：2026-11-13。范围：已有 `docs/prior-art` 中的近邻声明，优先核验六项，补核已有 LIBERO-Plus / PRO。检测轴：reference-audit / preprint、dataset-code / closest-prior-work / invented-or-unverified / authoritative-only。

**结论：六项优先工作均有可直接访问的原始来源，但 ECCBF 的 novelty 尚未通过。** 文献存在、组件已有以及暂未找到完全同构方法，是三个不同判断。本次已直接打开摘要、六篇相关正文段落、官方项目/代码；未独立复现论文实验，未穷尽全领域检索。

## 证据标签

| 标签 | 本轮实际含义 | 不能推出 |
|---|---|---|
| M | 原始记录的题名、作者、日期、版本已直接核对 | 结果已被独立验证 |
| T | 已打开原文相关方法、实验与局限段落 | 所有附录/数据均通过审查 |
| C | 官方仓库、发布范围、指定实现文件可读并静态查看 | 完整依赖、权重和实验已跑通 |
| R | 在匹配本项目条件下独立运行并核验产物 | 本次所有近邻均未达到 R |

项目页会议信息为作者/项目声明；本次未逐项另核会议录。论文固定版本，代码固定提交。未核实到官方代码入口，不等于证明代码不存在。

## 六项优先核验的元数据

| 工作与完整题名 | 作者（原始记录） | 首次提交；所读版本 | 证据 |
|---|---|---|---|
| ICBench / IGAR：**Restoring Linguistic Grounding in VLA Models via Train-Free Attention Recalibration** | Ninghao Zhang; Bin Zhu; Shijie Zhou; Jingjing Chen | 2026-03-06；v2，2026-07-02 | M/T；代码入口未核实 |
| LIBERO-CF / CAG：**When Vision Overrides Language: Evaluating and Mitigating Counterfactual Failures in VLAs** | Yu Fang; Yuchun Feng; Dong Jing; Jiaqi Liu; Yue Yang; Zhenyu Wei; Daniel Szafir; Mingyu Ding | 2026-02-19；v3，2026-11-04 | M/T/C；未运行 |
| BAS-VLA：**Beyond Appearance Shifts: Task-Semantic Action Calibration for VLA Models** | Shuaijun Liu; Feiyang You; Chengyu Wu; Shuyang Hao; Chenglong Zhang; Jingyao Cai; Xingwei Chen; Li Sun; Ningxin Su | 2026-09-20；v2，2026-10-21 | M/T/C；部分设置公开 |
| CorrectVLA：**What Can One Sentence Fix? A Failure Taxonomy and a Minimal Language Correction for Frozen VLA Policies** | Owen Kwon; Pablo Ortega-Kral; Arthur Bucker; Jean Oh | 2026-08-30；v2，2026-10-23 | M/T；项目页 Code Coming Soon |
| RAGu：**Zero-Shot VLA Adaptation with Retrieved Guidance** | Subin Kim; Anh-Quan Pham; Dinesh Jayaraman | 2026-11-07；v1 | M/T；官方代码未核实 |
| SO-101 Bench：**SO-101 Bench: Accessible Spatial Manipulation** | Truman Hickok | 2026-10-27；v1 | M/T/C；主测试部分私有 |

## 原文支持什么

### ICBench / IGAR

来源：[arXiv 元数据与摘要](https://arxiv.org/abs/2603.06001v2)、[原文 §3–5](https://arxiv.org/html/2603.06001v2)、[官方项目](https://ray-nh.github.io/igar/)。

原文在固定 LIBERO 视觉场景下改变属性/空间关系，包含无解矛盾指令；IGAR 在推理时调整注意力且不更新权重。§5.6 已有 Franka 真机，因此旧记录仅视作“诊断”低估重叠。

其矛盾条件 SR 按旧标准任务计分，**SR 降低**可以表示停止错误执行；LGS 衡量标准指令与矛盾指令下旧任务 SR 差。不能把它直接当作 ECCBF 的可执行任务成功率提升。项目页有数据入口，本次未核实到官方代码入口。

### LIBERO-CF / CAG

来源：[arXiv](https://arxiv.org/abs/2602.17659v3)、[原文 §3–7 / 附录 C](https://arxiv.org/html/2602.17659v3)、[官方项目](https://vla-cf.github.io/)、[官方仓库](https://github.com/yuffish/VLA-CF)。

同场景反事实指令指定**可行替代任务**；CAG 用语言条件与无语言分支的动作差增强语言影响。TF-CAG 与需要训练单独 VA 分支的 VA-CAG 应区分。原文已有 Franka Research 3 真机语言落地与成功率验证，“反事实语言 + 冻结主策略纠偏 + 真机”已不是空白。

提交 `8280a500a01f7f7d45efe202cb416ca362aa8c1a` 的 [README](https://github.com/yuffish/VLA-CF/blob/8280a500a01f7f7d45efe202cb416ca362aa8c1a/README.md)、[eval/main_cf.py](https://github.com/yuffish/VLA-CF/blob/8280a500a01f7f7d45efe202cb416ca362aa8c1a/eval/main_cf.py) 可读，含条件数据库与逐条件评估。未加载权重或运行 rollout。

### BAS-VLA

来源：[arXiv](https://arxiv.org/abs/2609.23650v2)、[原文 §3–5 / 附录 A.1–A.2](https://arxiv.org/html/2609.23650v2)、[正确官方项目路径](https://nebulis-lab.com/Beyond-Appearance-Shifts/)、[官方仓库](https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts)。旧记录中的 `/BAS-VLA/` 不作为本轮已核入口。

已覆盖固定场景 matched clean/control/break、冻结动作残差、选择性 preserving 辅助与证据门控；已有 Songling PiPER 真机，并单列 changed-task New / Old / Other 结果。“残差 + 门控 + 匹配 + 真机”不能作为 ECCBF 独有机制。

提交 `51f0dab5b2edab6539f3bccda7a04b3cb1d52a6c` 的 [残差实现](https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts/blob/51f0dab5b2edab6539f3bccda7a04b3cb1d52a6c/bas_vla/breaking/residual_adapter.py)、[artifacts](https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts/blob/51f0dab5b2edab6539f3bccda7a04b3cb1d52a6c/docs/artifacts.md)、[机器人接口](https://github.com/NEBULIS-Lab/Beyond-Appearance-Shifts/blob/51f0dab5b2edab6539f3bccda7a04b3cb1d52a6c/docs/robot.md) 已读。发布 adapter 对应特定 OpenVLA 离线动作约定，只覆盖部分论文设置；不等于可直接接 SmolVLA / SO-101 的基线。

### CorrectVLA

来源：[arXiv](https://arxiv.org/abs/2608.29967v2)、[原文 §3–8](https://arxiv.org/html/2608.29967v2)、[官方项目](https://correctvla.github.io/)。

原文先做失败分型，针对 execution misalignment，把人观察失败后的一句任务级纠正解析为动作维度、方向、幅度与时间窗，加入冻结动作；已有 xArm7 真机。不声称一句话能修复全部目标/规划失败。

ECCBF 必须证明测试前冻结、运行时可观测的交互校准有增量，而非改写成事后人工调幅。项目页仍写 Paper / Code Coming Soon；论文由 arXiv 可读，不能据此称官方代码可复现。

### RAGu

来源：[arXiv](https://arxiv.org/abs/2611.10894v1)、[原文 §IV–V](https://arxiv.org/html/2611.10894v1)、[官方项目](https://raguvla.github.io/)。

方法使用语义筛选、几何轨迹变换、粗到细且考虑策略兼容性的检索，并引导 flow-matching 推理；已有真实/仿真/sim-to-real/跨本体实验范围。“几何校准 + 冻结 VLA 迁移”不是空白。

项目页仍显示 Anonymous Authors，arXiv v1 则有上述实名作者，按版本分别记录。项目有评估数据入口，但本次未核实到官方代码仓库。作者摘要的性能数字不是 ECCBF 的效果依据。

### SO-101 Bench

来源：[arXiv](https://arxiv.org/abs/2610.36420v1)、[原文与 Limitations](https://arxiv.org/html/2610.36420v1)、[官方项目](https://so101-bench.github.io/)、[官方仓库](https://github.com/5hadytru/so101_bench)。

已有 SO-101 Isaac Lab 数字孪生与同权重真机排名研究；“SO-101 + 数字孪生 + 真机”本身不是创新。局限限定五个策略、45 个布局、一个真实环境，且仿真高估绝对 SR；排名一致不保证本项目校准效应迁移。

提交 `470e09e2b66658049e1248378f20ce39bd134ad6` 的 [README](https://github.com/5hadytru/so101_bench/blob/470e09e2b66658049e1248378f20ce39bd134ad6/README.md)、[环境配置](https://github.com/5hadytru/so101_bench/blob/470e09e2b66658049e1248378f20ce39bd134ad6/source/so101_bench/so101_bench/tasks/direct/so101_bench/so101_bench_env_cfg.py) 可读。公开 validation 与私有主测试不同，不能称本地可完整复现全部 leaderboard。v1 写 3,629 条模拟示范，当前项目写 8,000+ real/sim training episodes，口径/版本不同，暂不合并。本项目 MuJoCo 场景也不是该 Isaac benchmark 的复现。

## 已有其余声明与无法核实项

| 项目 | 原始来源 | 本轮边界 |
|---|---|---|
| LIBERO-Plus | [arXiv 2510.13626v3](https://arxiv.org/abs/2510.13626v3)；[官方代码](https://github.com/sylvestf/LIBERO-plus) | 题名 **LIBERO-Plus: In-depth Robustness Analysis of Vision-Language-Action Models**。作者 Senyu Fei; Siyin Wang; Junhao Shi; Zihao Dai; Jikun Cai; Pengfang Qian; Li Ji; Xinzhe He; Shiduo Zhang; Zhaoye Fei; Jinlan Fu; Jingjing Gong; Xipeng Qiu。首次 2025-10-15；v3 2025-12-26。M、摘要七类扰动与仓库可核，未同等审查全文。 |
| LIBERO-Plus 的 CVPR 2026 版 | [CVF 页面](https://openaccess.thecvf.com/content/CVPR2026/html/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR_2026_paper.html) | 搜索返回 **A Progressive Robustness Benchmark...**，但直接打开 HTML/PDF 均 HTTP 403。**搜索摘要不算已读会议版正文**；先按可读 arXiv 版本描述。 |
| LIBERO-PRO | [arXiv 2510.03827v2](https://arxiv.org/abs/2510.03827v2)；[摘要指向官方仓库](https://github.com/Zxy-MLlab/LIBERO-PRO) | 作者 Xueyang Zhou; Yangming Xu; Guiyao Tie; Yongchao Chen; Guowen Zhang; Duanfeng Chu; Pan Zhou; Lichao Sun。首次 2025-10-04；v2 2026-05-25。M、摘要四维扰动与仓库可核，未同等审查全文。 |

本轮偶然发现 [pre-execution return 作者仓库](https://github.com/distortionlab/pre-execution-return)，但其题名版本与 arXiv 编号未完整核实，仅记有限交接：若主 E 选初态/几何误差，后续核对简单状态返回控制是否已覆盖该执行恢复。此次不据此扩张近邻数量或更改路线。

## 对旧审计结论的修正

原始来源足以确认相关组件已拥挤；不能由此推出“组合性科学命题的新颖性已成立”。尚可研究的假设是：**预定义语义 × 执行条件的系统行为交互，及建模该交互能否带来超出 additive / generic residual 的成功率增量**。四格差分本身是标准因子对比，不自动成为新方法或认知因果证据。

在六篇已读相关方法部分中，本轮未核实到与拟定协议完全同构的独立物理执行因子四格估计及交互增量消融。这是有限阅读范围内的观察，**不是全领域不存在同类方法的证明**；也不以关键词搜索无结果作不存在证明。合法目标变化与 bias 的区别、A100 冻结项和可证伪实验见 [EXPERIMENT_VALIDITY.md](../EXPERIMENT_VALIDITY.md)。
