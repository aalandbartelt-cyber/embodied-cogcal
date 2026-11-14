# A100 前准备进度

## 持续目标：真正确定研究方向（2026-11-14）

- 新目标active，完整保留科研方向、查新、可行性、先进性、突出问题、突破机会与Scholar/GitHub要求。
- 上一目标回合产生87871e3约束记录，判为progress；不能以已完成的资料整理提前结束本目标。
- 本轮先做三域候选发现与GitHub可实现性核查，不直接实现新的机器人算法。
- 三域线索初筛完成：执行补偿TeAR、可修改记忆REMM、验证/不确定性CoVer/Pre-VLA/DiVeR/VFD均有强近邻；新增风险来源分解候选，正在做正向机会审计。
- 当前候选并未确定；是否只是模块组合/经典主动诊断的重命名，需继续查原文公式、GitHub可运行性和否证实验。
- 风险来源分解候选被PATCH、CommitFlow、ReTrace、RoboValue等新作进一步压缩，降为背景/对照。
- 新增首要候选D：动态executable-policy specification与同体等价证书；直接边界来自Same Weights的静态ExecSpec限制、FAN、TeAR、PolicyIK和SO-101 Bench。
- 新增候选发现报告 `docs/prior-art/discovery-direction-20261114.md` 及18条arXiv元数据/固定GitHub来源；D仍需公式级经典控制红队，不是查新通过。

## 用户后续确认（2026-11-14）

- 换题时保留SO-101、A100和同体仿真—真机，允许更换核心研究问题；已写入路线决策。
- 不把该答复当成接触适配候选获选或查新通过；后续可在原认知偏差主题之外寻找科学问题。

## 本轮验收

- 仓库基线：9fb61a6，干净；新建集成分支 feat/pre-a100-readiness。
- 启动三个独立智能体：数据完整性、部署/版本前检、查新/实验效度。
- 根 agent 负责 SO-101 场景运行时接口、集成验证与最终交接。
- 已确认 goal 仍 active，目标是部署前准备，不是替代用户明天的 A100 部署。

## 本轮验证进展

- 数据任务：合并原子写出、保护原输入、递归禁越权字段；严格成功标签；拒绝 smoke/step；跨任务/模型/域分组。
- 部署任务：核对 OpenVLA 官方 commit 和约束；接受 CUDA 本地版本；修复非有限磁盘门槛；说明 toolkit、pip constraints 与 pipefail。
- 证据任务：六个主要近邻的原文/发布状态核查，明确创新未证、合法动作改变不是 bias。
- 场景任务：修复 goal 重置；实现不泄漏真值的 RGB/关节观测、六关节 rad 动作和稳定放置谓词。
- 探针：跨种子 ID 唯一；红蓝候选、明确当前任务和可重建 placements；延迟参数未声称已经执行。
- 集成：分析环境 135 passed / 9 optional MuJoCo skipped；独立仿真环境 16 passed、没有跳过；EGL 30帧/1秒 MP4+trace 已实际生成并检查。
- OSMesa 本地缺 libOSMesa，已定位为系统依赖；CI 显式安装后已实际通过物理及渲染测试。
- 已完成只读复核：修复 scripted runner 硬链接输出别名，避免误覆盖原场景。
- 最终本地回归：148 passed / 9 optional skipped；独立 EGL 仿真 16 passed；Ruff 与 diff --check 均通过。
- 汇总新增 episode 身份判重，避免重复行污染分母和置信区间；全部无 ID 的旧格式仅兼容，不作为正式实验数据格式。

## 阶段收尾

- `afe481f` 已提交并推送集成分支；main 已快进合并同一代码，无合并差异。
- 云端 CI `43458874457` 的 `test (3.10)` 和 `simulation` 均成功。
- simulation 从空环境安装系统渲染库、固定依赖并获取官方资产，避免只在已有本地环境可用。
- 部署前准备已达到验收边界。后续按 `docs/NEXT_A100.md` 在 A100 加载模型并执行策略冒烟；
  SO-101 本体兼容策略/动作适配、ECCBF 实际收益、查新结论和真机证据仍待验证。

## 新目标：文献与汇报/论文准备

- main 基线 bcef4a2，工作区干净。
- 应用 planning-with-files、ieee-citation、ieee-experiment；继续保存真实检索和核验证据。
- Google Scholar 直接检索受访问限制；已记录失败，采用论文原始页面与正式出版记录作为可核验来源。

## 文献与研究准备产物

- 原始元数据：41 篇 arXiv 记录全部成功；Crossref 8 条（2 条与 arXiv 合并）及 3 个正式出版页；失败与待确认项保留记录。
- 最终文献库：47 篇研究/方法文献 + 3 个工程来源，共 50 条 BibTeX / RIS / CSV / JSON；17 篇相关正文段落阅读。
- 补充 IDR、PRO2.0、VLA-Gauge、MetaFine、RoboMD、主动辨识与延迟近邻；更新旧创新主张，不用关键词无结果证明新颖。
- 形成研究现状、阅读卡、查新/换题决策、12 页汇报提纲与问答、中英文相关工作准备稿、主张—证据表及研究就绪度清单。
- 当前生成器实际审计 100 scenes / 400 metadata rows：8 个物理布局、16 个布局目标组合、1 个实际任务模板；没有 VLA 结果。
- 离线验证：50 条 BibTeX 和 RIS 分别成功读回；引用键、题名/作者数/年份/DOI、源记录与响应 hash 对应检查通过。
  校验范围与非 Zotero GUI/非 LaTeX 全稿的局限记录在 references/validation.json。
- 合成示例 `[@key]` 导致首版引用检查误报，已剔除代码示例后复核；没有删改真实缺失引用来规避验证。
- 文档回归：148 passed、9 个可选 MuJoCo skipped；本轮未改仿真代码，未重复本地物理回归。
- 所有检查依赖仅安装到 /tmp/cogcal-reference-check，未修改项目/模型环境依赖。

## 本轮材料验收与集成

- `efb413b` 分支提交已同步，CI `43467383859` 的分析与 simulation 均成功；main 已快进集成同一内容。
- 原始目标逐项检查：真实检索/Scholar 限制记录、47 篇文献库、现状与近邻、剩余工作、汇报、相关工作及换题门槛均有实物文件。
- 另检查 16 个核心产物存在且内容非空；汇报有连续编号的 12 页；所有外部论文均未标成独立复现。
- 最终研究边界：旧组合性创新不再默认推进；备选 B/C 尚未查新通过，后续先查新和可证伪设计，再定具体机制。

## 用户追加 UniSuperMimic 线索

- 主库资料 main `6eb700b` 的 CI `43467753291` 已全部成功。
- 已定位 `Motphys/Uni-SuperMimic`，它是 SuperMimic 的独立下游复现；作者原始代码是 `HybridRobotics/supermimic`。
- 原始论文为 arXiv:2610.28480v2，官方摘要对象是人形全身运动跟踪；继续核查 native MuJoCo 接口和 SO-101 适用性。

## 深入查新与换方向裁决

- 三个独立域完成公式、输入条件、经典引用链和强基线审计；另完成接触替代初审。
- 撤回初轮C/B优先推荐；停止当前ECCBF核心，保留SO-101/MuJoCo共用资产。
- 形成ROUTE_DECISION新裁决、EXPLORATION_PROTOCOL限时草案，更新导师汇报、研究现状、相关工作和执行入口，避免继续旧主张。
- 新增脚本audit_eccbf_structure.py，实际核验四角点/1,000连续分数和400提示清理；证据明确为结构检查，不是策略结果。
- 深审补充31版本记录/30篇论文从arXiv原始meta核验，另核Continual VLA正式PMLR出版页；保留Ao标题异常和版本变化来源。
- 接触探索尚未预注册/运行，尚无新机制通过查新；文献/方案完成不等于研究方向已最终确定。
- 两位独立审阅者核总裁决与探索草案：无P0，已修正optimizer/buffer冻结推理不可识别、真机机械carry-over、实际随机分配和无更新单元不得事后选择删除四处执行边界。
- 结构脚本实际通过；ruff通过；分析回归148 passed、9 optional MuJoCo skipped。本轮未修改物理仿真代码，未把跳过项计为物理验收。
- 补充BibTeX/RIS各31条、SuperMimic BibTeX两条读回通过；31记录原始元数据/版本对应、下游5个固定源码hash与结构审计hash检查通过。

## 用户选定 D 的后续深审

- 完成 ForeReach 原文 §2–4/Algorithm 1/§5.3、CARE §3/A.5–A.6 和经典任务鲁棒性/rollout保证的定向核查；拒绝以动态误差界＋任务margin＋拒绝部署作为当前新机制。
- 直接读 ActionABI/ActionShift 固定源码，区分实际实现、README实验报告与尚未独立复现的性能；两项目 MIT LICENSE 已读取。
- 撤回 D/D′ 首推荐；更新 ROUTE_DECISION 和候选发现页，接触探索也没有自动恢复为主推荐。
- 更正 Same Weights 仿射位移漏项/已有 local margin 与 RoboStress 模型归属；审计稿明确保留历史推演与当前裁决边界。
- 新增6篇原始版本元数据，discovery补充现27条arXiv/10项GitHub；分析反例与样本规模核算单列JSON，不记机器人实验。
- 这是一次完成的候选深审，完整“确定有先进性、可行性和核心增量的研究方向”目标仍active。

## DeepSeek 扫描纳入与机制候选收敛

- 用户提供 DeepSeek 探索稿；原稿保留，独立复核补充经典 MTGP/AT-GP/latent-GP/ALPaCA/MRPL 近邻，并加入单参考动作多模态反例。
- 用户选择“先验证失效机制，再提出方法”。从 BAS-VLA 原文公式抽出 shared-prefix 目标函数条件反例；定向核到 One Word、Stage-Aware、RT-H、Acting While Understanding、PHASER、Hide-and-Seek，更新边界。
- 完成 SO-101 静态可见性预检和来源核验；新渲染记录只证明对照可构造，不证明 reward model 误判或策略 reward hacking。
- 当前更值得小规模否证的是 temporal-prefix calibration，而非 RCBT GP 配方或完成判定模型；尚未确定主方向，未进入方法实现。
- 复核后补齐 6 个时序/共享动作近邻的 arXiv API 元数据与响应哈希；修正共享前缀玩具核算，使分离损失只在必需分叉支持上计数（统一 margin=2.0、支持掩码=0.0）。
- 清理路线决策中的重复段落；当前下一步仍是冻结任务对、验证 uniform separation 是否真的造成前缀误纠偏，再决定是否值得实现方法。
- 定向查新继续发现 AtomSkill、TRA、REFACTOR-VLA 与 Counterfactual Memory Audit；已将 TPSC 的必要条件收窄为 outcome-conditioned temporal support，人工 phase mask 或片段级行为等价不能作为核心方法。
- CriticHack 原文审计完成；完成判定/视觉 reward 线已降为复现与强对照，不再并列主推荐。
- 核验公开 SmolVLA/SO-101 Hub revision 与官方 A100 微调路径，新增 `docs/NEXT_A100_TPSC.md`；载体基线可以先在 A100 验收，候选损失仍冻结。
- 下载并哈希校验公开数据的 `meta/info.json`/`meta/stats.json`，完成 6 维字段、单位转换和 MuJoCo actuator 范围审计；发现 elbow/wrist range mismatch，已将其列为 A100 前置阻塞项，避免把接口错误当科学现象。
- 接续 Codex 的接口预检：用 2025-05-23 旧版 LeRobot 证据确认数据集单位为 degrees；量化 `elbow_flex` +3.17°、`wrist_flex` +4.49° 越界；`robot_type=so100_follower` 不支持 SO-101 同体。原始 `summary.json` 保留为 `summary-degree-assumption.json`；新分析见 `range-mismatch-analysis.md`。A100 只验证 LeRobot/SmolVLA 训练链路，TPSC 同体实验需项目自有 SO-101 数据。
- 完成公开 SO-101/SmolVLA 数据集扫描：`kristaqp/so101-pick-place`（真实 `so101_follower`，50 eps，elbow 100°）、`ngocthuong2212/so101_mujoco_follower_7_31`（MuJoCo SO-101，200 eps，范围与 XML 吻合）、`svla`（SO-100 负对照）；新增 `public-dataset-scan.md`、`audit_real_so101_range.py`、`real-so101-reference.json`，更新 A100 交接与 Codex handoff 的 P1/P2。
- 新增 TPSC 项目自有 SO-101 数据采集协议 `experiments/so101/tpsc-data-protocol.md`：shared-prefix/no-common-prefix/multi-valid 三族任务对、校准/单位契约、`episodes_meta.jsonl`、拒绝准则、2 周 120-episode 资源盒；先 20-episode 管线试跑。
- TPSC pilot 资产落地：`simulation/so101/tpsc_scene.xml/.py`、`probes/generators/tpsc_pairs.py`、`experiments/so101/tpsc-pilot/`（20/120 manifest、validator、MuJoCo scene smoke、README、6 张渲染）。20/120 条几何/配对校验通过；MuJoCo 4.0.1 逐条 reset 与目标入 goal 的评估器 smoke 通过；尚无策略 rollout。
- 可达性 proxy：20k 关节采样，240 个目标物体/goal 点均在夹爪 5 cm 内，最差约 3.5 cm（`reachability.json`）。这只是几何 proxy，不证明抓取/放置或碰撞安全。
- Scripted IK full 120：shared-prefix 的 target/executed prefix diff = 0.0；no-common 从 above_object 起 diff >1.2 rad；multi-valid prefix 0、route diff >1.15 rad。kinematic-carry place 120/120，物理抓取 pilot 0/20，final 56/120。只验证任务结构/路径，不是 learned policy 或物理抓取 benchmark。

## Codex 恢复后 review / 保全提交

- 按用户交接先审阅未提交资产；完整审阅见 `experiments/so101/tpsc-pilot/REVIEW.md`。
- 发现 scripted pair 汇总只保留最后重复、executed qpos 混合物体状态、自然任务对同时改变 RGB、kinematic place 显式重设终点；历史 JSON/manifest 不重写。
- 分析回归 153 passed / 11 optional skipped；仿真 23 passed；20/120 validator、120 reset/predicate smoke 通过。
- A100 尚无已配置作业入口；本机 RTX 5070 Ti，已向用户询问 A100 入口并继续本地可做项。

- 用户明确当前选题阶段改用本地 5070 Ti。已验证 torch CUDA sm_120 矩阵乘法；建立独立 tpsc-policy venv，避免修改原分析/仿真环境。
- 指定 carrier 的 gripper 数值含 -10，前序 handoff 的 `gripper_0_100` 不能直接沿用；此为适配检查，不重复已完成的查新。

## 本地 learned carrier 实际启动

- PyTorch 2.7.1+cu128 / torchvision0.22.1 / LeRobot0.4.3 环境已建立，解决 nightly VideoReader API 删除。MuJoCo仍独立4.0.1。
- 指定carrier已实际解码（200 eps /60245帧）；SmolVLA严格加载、CUDA前反向有限，chunk[1,50,6]，99,880,992参数有梯度；原batch形状失败日志保留。
- batch4的20-step普通训练试跑完成；固定seed42、20k终点的载体训练已启动（session74436，PID87789；运行状态须实时核验）。这不是TPSC任务对训练。
- learned rollout与配对报告入口已实现，但尚未执行20条正式能力screen；shared-prefix和uniform-separation伤害均未验证。

- Python3.12仿真侧→Python3.10GPU侧的真实IPC检查已通过：读取已保存的20-step资源checkpoint及其processor，返回有限[50,6] chunk。输入为黑图fixture，只证明通信与加载，不计episode/成功率。
- 增加“预测chunk未来分叉不等于实际执行分叉”的回归；5项契约测试和全量158 passed/11 optional skipped通过，Ruff通过；policy环境pip check无损坏依赖。

## 目标门槛复核：损失忠实性与用户开源材料

- 用户再次明确目标是确定有核心增量、可查新、能产出同题仿真—真机成果的研究方向；训练/环境/盘点不算完成。
- 固定BAS-VLA v2和源码51f0dab，实际CPU调用compute_losses：旧toy逐步hinge求和2.0，按展平chunk求距为0；完全共享坐标的直接梯度也为0。撤回一般性“已发现前作伤害”解释，保留原JSON。
- 公开BAS artifact固定revision的实际布局为per_step/legacy/7D；仍保留为忠实比较对象，不能把chunk更正误写成不存在逐步基线。
- 修正候选定义：“未来损失相同”可能意味着同样失败，不能证明共同行动可行；方法实现继续冻结。
- 读取用户新材料docs/VLAkaiyuanxiangmu.md，核验15个原始仓库revision/README哈希；补充MolmoAct2真实5.44B规模/normalizer和SO100同体验证局限、TurboVLA 7D/chunk12对照、StarVLA的SO101未完成状态。详见review-vla-open-source-20261114.md。
- 本地训练原进程87789仍在运行，约13k/20k（日志显示值为缩写，精确完成看checkpoint步数）。训练未重启；固定最终checkpoint后才进行能力screen。
- 自动screen v1因未验证的OSMesa约定在episode前取消并保留记录；EGL实测三图通过，v2队列session57985/PID2595058接续等待，输出未产生前不称pilot完成。
- 额外机械检查发现旧脚本OPEN/CLOSED反置、IK用夹爪转轴body原点且与官方gripperframe差8.207cm。只证明teacher未就绪，不把0/20归因VLA/TPSC，也不声称修正后已能抓取。
- 本轮全量分析pytest进程14734退出0，11项可选仿真跳过；新CPU代数/autograd断言通过、Ruff通过。没有把这些检查计为方法优势或真机证据。

## 2026-11-14 最终20k与原20条能力pilot完成

- 原训练/队列在用户轮次中断后消失，核实最近完整18k状态后续跑至20k，正常退出0；保留中断/恢复记录，明确采样器位置未恢复。没有挑best seed/checkpoint。
- EGL正式执行原20条manifest，20:44:24完成，退出0；20条/10对/600chunk/6000控制目标身份与轨迹通过核验。任务成功、抬升、放置均0/20，55个目标向量裁剪事件。
- 左右首chunk存在差异，初始q/seed相同但RGB/语言同时变化；实测q每10步记录。正确共享前缀不可识别，uniform separation未测试，不从无能力策略提取前缀伤害。
- 模型权重hash、原始episode/chunk/q、全部10对表、完成stdout与hash清单已保存。当前一页go/no-go：载体未就绪；不实现TPSC，不直接扩大120条或迁移A100。
- 支持集合量词更正：VA∩VB非空不强制两个正确动作相同；过大margin也可损伤无共同支持任务。原manifest中的no_common仅描述脚本早分叉，不证明必要分叉边界。
- 核验SupCon/DCL/FALCON/ECT/IntentVLA/CompCPZ等原始近邻，要求同池配对BC等强简单对照；ECT训练因素尚未拆解仅是研究问题，BEHAVIOR2026已覆盖机器人antithetic/分层flow训练，不能包装通用噪声方法。
- 独立读取MolmoAct2公开双YAM rollout共75条/89546帧，元数据无success标签；固定抽帧停滞只作线索，初始严格tail规则0条，不事后调阈值或混入TPSC。
- 物理teacher单初态5变体×5offset全部保留，仍没有合格双指抬升；接触/IK失败不作认知偏差或VLA结果。
- 完整目标仍active：尚未确定可经查新、可实现、有核心增量的研究方向，工程/文献产物不算完成。
- 后续积极可行性检查：固定外部SO101控制器b02b8b2，原样及独立接触记录复跑均为place成功/hover失败；双指接触且抬升最长2.6365s。原模型有显式盒状指垫、friction2及28mm物体，与本项目原场景不同，只作独立资格线索。
- 作者HF主页追到公开GitHub身份，定向3仓库为两README/一空仓库，未取到原carrier录制源码；局限与请求结果落盘。新增R3L/DEFLECT-v3/TPC-FM原文快照与方法定位，进一步排除通用prefix mask/共享noise的宽泛创新。

## 2026-11-14 匹配能力检查与近邻继续收窄

- 外部物理teacher中央工作区0/10保留，事后发现初始固定指垫穿透15.37mm；避开后的10/10仅为运动资格，目标成功圆重叠不能计语义左右能力。
- 30Hz teacher四例重验通过，5Hz双相机/30Hz控制的24train+8val示范32/32成功；原30Hz软件渲染采集主动中止及首条/源码均保留，数据未混用。
- 普通小BC固定2000步最终权重训练正常完成；预定20个test seed全保留，任务成功/双指抬升0/20。2828个命令向量限幅、平均episode跟踪误差0.06889rad。三阶段exit0，不是训练进程仍在运行。
- 冻结同一权重，仅val集自适应诊断执行6/30步：0/8与4/8；后者8/8双指抬升和目标内放桌，4例未释放。未放宽成功条件，不当作新测试或核心机制证据。
- 继续核验15份有界原文，任务切换/事件记忆/本体捷径/执行补偿/非Markov chunk与阶段路由均有直接近邻。GAP官方源码固定版本入口AST失败，未找到tracked license；仅作实现审计，不用代码问题宣称科学创新。
- 保留待证伪问题“执行精度改善是否破坏策略利用的阶段线索”，但近邻重合风险高、尚无现象证据。能力未过，未运行补偿干预，也不实现新算法。
- 研究方向尚未确定，目标active；本轮新证据改变的是能力瓶颈定位，不是查新结论。
