# 历史、执行补偿与选题门槛：进一步收窄

日期：2026-11-14。目的仍是确定可查新、可实现、有核心贡献的方向。
本页是有界原文核查与待证伪问题，**不是查新通过、已发现失效或已确定选题**。
硬件沿用用户最新决定：选题阶段本地5070Ti；保留低成本SO-101与同题仿真—真机。

## 哪些宽题已有直接近邻

| 想法 | 已阅读的一手依据 | 对本项目的约束 |
|---|---|---|
| 新指令来了再决定继续、回滚或前进 | [SwitchVLA §3](https://arxiv.org/html/2506.03574v1) | 不能把“根据当前执行状态切换任务”再作为核心 |
| 防止记忆把停顿、空抓当作任务进展 | [MemoryClock §3–6、附录I.5–I.6](https://arxiv.org/html/2611.14488v1) | 事件索引及非特权传感器版本已有讨论；清除记忆也可能丢失真实循环进展 |
| 用动作变化决定保存历史 | [RePlanMem-VLA §3–5](https://arxiv.org/html/2610.22556v1) | 其差异量包含视觉特征；不能误读成纯动作信号，再声称增加视觉就是创新。原文对任务局部校准、缓慢变化与短暂事件有限制 |
| 保存未来有用的事件 | [EventVLA v2 §3、附录A](https://arxiv.org/html/2606.20092v2) | 已有未来chunk的关键帧概率与事件缓存；离线视觉模型标签也须公平说明 |
| 在策略与黑盒控制器之间改善执行 | [APEX §3–6](https://arxiv.org/html/2606.16504v1) | 动态参考重建、反馈自适应及跟踪目标已存在 |
| 跟踪更准就必然更利于学习/迁移？ | [Tune to Learn §IV–V、附录A](https://arxiv.org/html/2604.02523v1) | 增益、动作噪声传递、可学习性和sim-to-real之间的非单调关系已有系统研究；普通高增益失败不能当新现象 |
| 本体状态成为学习捷径 | [Adapt Your Body §3](https://arxiv.org/html/2506.23944v1) | 已有proprioception shift、时间条件分布度量和两阶段噪声增强；不把丢弃q或加噪当新方法 |
| 运动转换阶段视觉被本体信号压制 | [GAP §3–4](https://arxiv.org/html/2602.12032v1) | 已有受控阶段切换、变化点分段及阶段条件梯度调整；“阶段感知模态门控”宽题不能另起新名 |
| 指令—执行误差可以提供接触信息 | [Mind the Gap §III、附录B](https://arxiv.org/html/2602.08776v1) | 误差不都是应被消除的机械偏差；不能把利用该误差估计交互力当空白 |
| 策略与DOB重复补偿 | [Taming VLAs §3、附录B.6](https://arxiv.org/html/2609.37334v1) | 原文DOB+方法组合已明确以DOB前策略reference算残差，避免重复归因；不能把改用pre-DOB reference当新方案 |

原文缓存、版本、读取范围与SHA见
[来源清单](../../experiments/so101/vla-open-source-audit/history-compensation-primary-sources.json)。
搜索结果只用于发现，未阅读的命中不算全文核查。Google Scholar本轮再次访问仍返回403，
记录见 `experiments/so101/vla-open-source-audit/scholar-followup-access.json`，未宣称穷尽检索。
项目页当前可见状态：APEX、Tune to Learn页面未提供可用实现链接；
[NADA页面](https://proprioception-shift.github.io/)的“Code (Coming soon)”指向GitHub首页；
[GAP页面](https://gewu-lab.github.io/GAP/)提供Code入口；固定仓库版本
`2f605436c68eedf328c05520d52877604af730d3`已有训练/阶段分段代码，但入口第85行
把保留字`lambda`作变量，独立AST解析失败；还观察到batch最大phase统一缩放梯度，
不同于逐样本phase语义。仓库未找到受版本管理的license文件，未修复/复用或声称复现。
细节见 [只读源码审计](../../experiments/so101/vla-open-source-audit/gap-code-audit.json)。
页面没有链接只表示本轮未取得代码，不证明作者没有代码。

## 暂留一个具体问题，不预先发明算法

> 冻结策略在训练时是否利用了命令—实测状态之间的滞后作为阶段线索，
> 以至于改善执行会改变其决策？这种影响能否与普通动力学失配、噪声放大、
> 接触柔顺性和视觉/本体融合失衡区分？

这与《思考，快与慢》的联系只在于“学到的便捷线索在环境改变后失效”；
心理学比喻不提供新颖性。工业补偿是受检验的干预，也不是先验正确的答案。

**保留理由**：能用同一机械臂、RGB/q/命令历史测量，也能在实机上施加有界执行改变。
**主要否决风险**：Tune to Learn、NADA、GAP或经典反馈理论足以解释全部现象；
只有低能力BC才出现；所谓改善跟踪实际增加了噪声或改变了接触；仅改变q输入导致RGB/q不一致。
这些都是必须正面排除的风险，并非已有证据。

## 主张—证据矩阵

实验审计轴：control；baseline/ablation/reproducibility；overclaimed-results；planning。

| 主张 | 当前证据 | 缺失的决定性证据 | 门槛 |
|---|---|---|---|
| SO-101短抓放在独立物理载体可行 | 固定外部版本实跑；30Hz teacher四例合格 | 匹配数据与learned policy闭环资格 | 不以teacher替代策略 |
| 执行改善破坏特定阶段线索 | 无 | 合格冻结策略；同初态的执行/仅观测分离干预；动作决策变化先于失败 | 未过能力门槛不解释机制 |
| 超过普通gain/noise/contact解释 | 无 | 同命令replay、噪声传递、阻尼/接触匹配、RGB/q一致性对照；NADA/GAP强对照 | 简单解释成立则降级/换题 |
| 可以提出有优势的方法 | 无 | 明确现有方法边界，随后设计针对性机制及传统/近期/简单对照 | 现在不实现或命名新方法 |
| 同题仿真—真机 | 尚无真机 | 相同输入、误差定义、物体/任务谓词和干预语义；实测接触与时序 | 外部指垫/friction不当物理校准 |

先执行[普通BC能力计划](../plans/2026-11-14-matched-bc-capability-screen.md)。
能力门槛通过后另写干预计划；不会从能力失败中提取“补偿伤害”。
TPSC原20条结果仍保留：载体未就绪，uniform separation未运行，核心主张既未确认也未由该失败否定。

## 选题结论

当前没有方向达到“确定立项”的证据门槛。上述窄问题仅值得一个低成本证伪实验，
不是主推荐结论；若与已有机制没有可测差异，停止此表述并换问题。
下一次汇报必须说明“哪条观察改变了选题判断”，不能只汇报环境、文档或训练步数。

## 完成能力检查后的进一步约束

新匹配teacher32/32，固定小BC测试0/20，因此补偿干预仍不运行。
冻结权重的验证集诊断中，执行6步为0/8，执行30步为4/8；后者8例均有双指抬升和桌面目标内放置，
4例未释放。该诊断发生在看到首轮测试失败之后，不能当预注册机制验证或重新定义的测试成绩。

[Why Does Action Chunking Improve… §5–7、附录C](https://arxiv.org/html/2608.02547v1)
已有非Markov表达、延迟条件及隐式集成解释；
[Revisiting Open-Loop Execution §5](https://arxiv.org/html/2608.15938v1)
已有专家非Markov性与长上下文代替长执行窗口的研究；
[Measuring the Stability Assumption §3、§5](https://arxiv.org/html/2610.01626v1)
已有配对开环/闭环扰动与误差传播探针，且明确传播率不能直接决定最佳任务horizon。
所以本轮执行长度线索只作能力诊断，不是核心创新。
[TRACT v2 §III](https://arxiv.org/html/2607.29285v2)
还已有未来阶段边界路由与接触响应亏损积分；“分阶段chunk+补偿”宽题也须排除。
