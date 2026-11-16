# A100 前准备进度

## 2026-11-16 固定真实阶段复核与近邻/载体边界

- 上轮84525e1是实际progress，已同步；本轮完整选题继续active，不恢复几何监督toy或旧BC微调。
- 沿用冻结12条ring_insert/pi0.5，事前绝对3秒网格+末帧，109时点/327帧/7页均实际看完。
  真实失败含原槽停留与搬离后未完成，成功229/236也有中途到其他槽；没有从阶段现象拼因果。
- 定向读ProbeAct v1 §3.2–3.5/4/5与RESCUE v1 §III–V；已有对象同步、分级CBF、
  干预价值/非单调可恢复性/时长控制，不立通用恢复新模块。
  2609.05376另只读阶段视觉grounding方法/结果，未当已核完整SO101载体。
- 新查两组公开小ACT与数据metadata、两位作者直接链接的GitHub身份及相关固定repo。
  教学repo/训练notebook没有补录制scene/相机/控制器绑定；dataset revision=None，未证训练源精确版本。
  没有下载权重、安装依赖、执行上游或新训练/物理/硬件试验。
- Scholar题名429/challenge、0结果卡；未成功取得Scholar结果页。
  旧包装cache树schema误读TypeError后按原source-scan恢复；讨论API首次错读字段，核latest.raw后确认为bot说明。
- [本轮入口](experiments/discovery/real-stage-screen-20261116/README.md)保存全部网格、原文边界、资产资格。
  下一步停止扩充同类联系表，先核本地官方ACT与自有匹配物理数据的接口/固定能力screen条件。
- 技术核验通过：完整grid327帧/7图/3视频，37源快照；与两次旧提取各60个重叠帧完全同SHA，
  145旧tracked资产及3指定原始SHA不变，官方模型/ACT模块tracked干净，Ruff/diff与31既有本地链接通过。
  没有新策略/物理/硬件试验；不把技术核验当选题通过。

## 2026-11-15 几何监督有界检查与真实过程接续

- 原GRASP参数与RFM条件等价/最新Preconditioned FM方法、KADP/STG-DP运动学目标已定向核。
  KStar固定cb0e850公开24文件，仅插件范围；未取得完整runner/URDF/权重，不当可运行载体。
- 按冻结计划，一坐标总体梯度/独立FK/SO3差分及负对照完成；实际源权重.15未放大。
  两prior×3步数×2场的全部终点保存。10步非对称1/1024分位数离开合法带，100/1000步消失。
  不是1024个episode或机器人成功率；没有实际任务损害或可立项方法。
- 独立MuJoCo目标优化与Brent全10步检查通过，fresh数值输出字节相同。
  verifier初版Ruff闭包/import警告后仍运行并产生v1，原脚本/JSON保留；绑定变量后v2数值相同。
- 几何监督线按规则降为诊断储备，不扩大解析扫描、不开始修正训练。
  [完整记录](experiments/discovery/geometric-supervision-20261115/README.md)。
- 真实过程接续先冻结规则：此前12条中最早成功225与失败226，三相机固定0.5秒网格。
  新下载front 93156054 bytes、wrist108839727 bytes，均匹配固定HF LFS SHA；不称新策略rollout。
  已实际复核306帧/7页（44/58时点×3视角），225后段运环到桩，226多数后段在取环区域。
  看图后10–20秒遥测检查明确标探索性：226 action200/state192个不同行，不能称动作日志冻结。
  初态未配对/单操作员标签/相机真实曝光同步未知，不能归因。
  [过程记录](experiments/discovery/deployment-failures-20261115/process-review.md)含全部网格与边界。
- 验证：11份来源、306帧/7图/3视频SHA及新2视频LFS大小一致；fresh总体结果字节相同，
  216份旧tracked资产与33份上一轮原始结果不变，指定3原始SHA/官方模型工作树/3脚本Ruff/diff通过。
  50个既有本地链接检查通过；技术核验不证明任务效应或新颖性。

## 2026-11-15 真实失败检查与配对几何监督问题入口

- 上轮ed2f5b3属于实际progress，改变了主推荐排序。本轮保留完整研究目标，不恢复已降级扫描/VFD或旧BC微调。
- 只读旧20k SmolVLA：原checkpoint 7文件SHA通过，pre/post action/state mean/std共8组与数据float32一致；
  20episode/600query/30000完整chunk行/6000命令的幅度复算保留，不能据此识别0/20原因。
- 新核Warp最新v4的强随机residual对照、Self-Adaptive VLA原文与RoboColosseum固定SO101代码/模型/数据入口。
  原数据镜像未证明等于训练源；作者要求24GB GPU，未安装/推理或声称本地12GB载体已就绪。
- 固定Armnet revision，先冻结同checkpoint/ring_insert前6成功+6失败（225–236）；实际核5421行和固定1/3秒前缀。
  下载top视频110353625 bytes，SHA与LFS一致；按PTS提取72张固定图并看完3页。
  可见正确套环与另一侧凹槽放置差异，接触/位姿/错误原因仍不明，不能把日志差写成机械误差原因。
- GRASP §III-A提供新的待证伪问题：配对非线性FK监督与CFM条件均值；显式penalty、RFM、预条件化为直接近邻。
  没有GRASP模型结果，Armnet π0.5也不声称使用该损失。当前只核数学对象，不先造新算法或宣布创新。
- 首次视频提取因relative/absolute路径混用中止，partial保留；定位后只改路径解析，在新v2目录成功。
  无ffmpeg CLI，使用已安装PyAV；没有新增包、训练或策略rollout。
- 原始结果、source hashes、接续问题与范围在
  [本轮记录](experiments/discovery/deployment-failures-20261115/README.md)。完整选题仍active，尚无最终方向。
- 验证：49份来源SHA、3份数值/选择审计全新输出逐字节相同、72张帧/3图新目录重放hash一致；
  98份旧tracked资产与HEAD字节不变，指定TPSC SHA、Ruff、diff检查通过。重放不增加n或证明新颖性。

## 2026-11-15 指令必要性候选进一步裁决

- 新核2018导航DONE规范、2026 shortcut审计与双judge研究的一手限定章节和固定代码入口。
  task-index probe不是目标盲；合法共同轨迹也不必是错误评分。两项区别保留，不以此自动宣称创新。
- 静态解析固定环境/原evaluator/公开脚本：两个done字段None、None映射False，默认1000步与指定30Hz；
  原始物体真值不转发canonical输入。首次audit执行通过，未运行Isaac/策略或增加物理样本。
- 当前核心增量仍不足，测量发现降为诊断工具、暂移出主推荐。未证明具体反例已被发表，亦未把该线全部否定。
  不将常规停止规则、更多扫描或换平台作为主任务；完整目标仍active，尚无候选通过全部门槛。
- 来源hash/读取范围/访问失败与静态复核入口见
  [本轮裁决](experiments/discovery/instruction-necessity-followup-20261115/README.md)。
  ANU PDF后续find/下载超时；2018规范HTML是PDF占位，已从原PDF读取对应章节。
- 验证：29份来源SHA、全新路径静态审计一致、50份旧资产逐字节不变、7份指定原始结果SHA不变；
  26个既有本地链接、Ruff与diff检查通过。没有新物理/策略结果，不用资产验证代替选题证据。

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

## 2026-11-14 循环BC/初始视觉对照：60条完整结果

- 普通GRU carry/reset固定seed42、同结构/初始化/采样索引/285188参数、2000步最终权重，在新7100–7119均完整执行：11/20与4/20。四阶段正常exit0，均未过能力门槛。
- 全24train短q历史近似观测/不同未来chunk的描述性审计不支持严格不可辨识定理；最初严格RGB匹配0命中也保留。carry8条未抬升前都已发生物体>2mm位移，离线FK与RGB定位只是后续工程选择线索。
- 固定初始RGB颜色特征的普通GRU对照使用新8100–8119，15/20成功、19/20持物抬升，4放置失败/1未抬升。未达事前16/20，未放宽条件或延长预算，按计划停止继续微调此小模型。
- 两条systemd流水线均正常结束，全部60episode、17100命令、2880chunk及hidden/q/裁剪保留。证据核查v2通过；4个因果/序列测试通过，Ruff通过。旧记录/绑定源码及受保护TPSC文件未改。
- 新增Copycat原文、因果混淆proceedings摘要、CSA与IMEP有界审计。历史捷径、组合补偿与记忆干预已有直接近邻；当前精度/阶段线索问题既未证实也未过查新。
- 具体进展改变了后续选择：不再继续小模型架构试错，不从未合格策略提取补偿机制。研究方向仍待确定，完整目标active。
- 新核到NVIDIA官方SO101 SAGE/GapONet/Workshop：三个固定revision、19份指定源码及公开75条sim数据/N1.6检查点元数据。GapONet＋GR00T的SO101集成仍为future work，未安装/下载权重或声称复现；单位/normalizer/horizon及官方页面样本数不一致均明确保留。它既提供成熟载体入口，也进一步压缩宽泛“VLA后接精度补偿”的新意空间。

## 2026-11-14 目标复核与公开执行证据

- 用户提醒不要偏离完整选题目标；将 task_plan / RESEARCH_READINESS 的当前入口明确为方向确认，早期 A100 准备记录保留为历史。
- 从固定 SAGE revision 在看误差前选取三类真实记录，共 16,840 行；12 份来源文件 hash、单位和逐行时间检查已落盘。没有 RGB/成功标签/匹配 sim，不把逐行残差当机械纯误差或任务损害。
- 当前采集源码用循环起始时刻同时标记发送与后续串行读取，历史采集版本未核实；没有估计纯机械延迟，不排除带额外假设的有效动态拟合。
- 新读 SimuGuard 的限定章节，核到精确重放/物理窗口干预/评分 seed 边界；一般仿真假失败审计不能作为新核心。GapONet 作者出版页可读，OpenReview 全文浏览器验证未通过，未假称完成全文审计。
- 不再增加小 BC 微调。后续最多同时深审两个具体问题，要求任务后果、最近邻差异、强简单对照和同命题 SO-101 真机可测性；没有候选立项，目标仍 active。
- 新路径重跑轨迹审计与保留输出逐项完全一致；Ruff / diff whitespace 检查通过，三份受保护原始文件 hash、两份新一手缓存及18个本地文档链接通过。核查范围见 `experiments/discovery/sage-real-20261114/verification.json`，不将其计为科研假设验证。

## 2026-11-14 新问题入口：有效示范与五自由度参考约束

- 上轮是实际进展：公开执行数据资格与新近邻改变了可主张范围，提交 e381e64；未把它当选题完成。本轮继续具体问题发现，没有重启已结束的 BC 流水线。
- 新作者博客提供 SO101 示范生成/IK/少量真实运行线索；其链接 fork 本轮公开/API 404，运行标签有未决差异，不借五次非配对运行作机制效应量，也不将别的官方 Workshop 当其源码。
- 先写运动学检查计划，再对固定官方XML24个中央限位配置计算五轴Jacobian。24例秩5；三种预定特征长度一致，120列中心差分最大误差8.53e-11m/rad与3.40e-10rad/rad。工具wrist_roll轴约[-1,0,0]，不能泛称固定缺失工具旋转轴。
- 这些是几何配置而非任务episode，未生成/拒绝真实任务，不能证明数据覆盖或策略损害。
- 新读 CP-Gen 的关键点约束/配置优化和 MoMaGen 硬软约束原文范围，核官方 SO101位置优先IK。一般改IK/关键点约束增强不立项；仅保留“强对照仍错拒可行任务”的条件问题，需要独立成功轨迹见证。
- CPGen固定源码1e7c1fc、MoMaGen固定源码入口5da6216，CPGen7份指定源码/许可只读缓存，未安装/执行。官方CPGen不是已验收SO101载体，不再因源公开就声称可直接用。
- 完整方向目标仍active；本轮没有新核心方法、策略/补偿干预或真机部署结果。
- 本轮数值新路径复跑与原JSON完全一致，Ruff/diff检查通过；11份一手缓存、6个本地链接与三份受保护原始hash核验通过，官方资产工作树无改动。核查只证明记录完整性，不证明新问题成立。

## 2026-11-14 位姿重定向的物理 go/no-go：停止当前核心

- 上轮24配置核查是真实前提证据，但不能证明任务损害。本轮先冻结四个布局、两个普通IK目标、共同预算和严格原成功条件，再实际运行物理回放；未训练策略。
- cogcal-sim原缺SciPy，核官方PyPI兼容元数据后只补装scipy1.16.3 --no-deps；NumPy2.5.4/MuJoCo4.0.1未变，pip check通过。初次Ruff报循环闭包未绑定，执行前显式绑定目标修复；没有覆盖已产生实验。
- 独立teacher成功见证5/5，源→源identity2/2（最大命令差1.11e-16rad），完整位姿IK4/4、简单方向IK4/4。15条/4275命令、0个限幅向量，脚本正常exit0，原始stdout/trace/IK诊断/绑定源码全部保存。
- 本工作区没有预想任务损害，简单方向对照足够；停止将该线作为当前核心，不继续增大扰动或改阈值制造效果。保留其载体工具价值，不以资料/代码或否决候选当选题完成。
- 最终物体目标误差6.38–33.34mm，不能把小IK残差当物理定位精度。本screen用特权固定技能分段与源命令FK，不是CPGen忠实复现、VLA、语言分支或真机。
- 独立原始trace审计通过：复算全部任务谓词、15条/4275控制、100次IK起点尝试、源模型/代码/计划及三份保护原始hash；Ruff通过。当前没有新方向通过立项门槛，完整目标active。
- 核验v2再加强布局身份及同场景最初12步的实际状态一致性，仍通过；v1原输出及对应脚本保留，实验原始数据和绑定runner不改。
- 11月15日最终新路径复核与v2逐项一致，51份结果文件hash及源码Ruff检查通过；官方/外部载体tracked工作树无改动。原始实验于11月14日23:53完成，目录日期保持原执行日期。

## 2026-11-15 新问题筛查：分歧代理与实际动作分布

- 上轮15次物理回放是改变下一选择的负面证据，已提交0f5e2be。本轮没有重跑/扩大该线，而是扩大一手检索后深入VFD有限网格及有限拟合误差。
- 固定UQ-VLA bcc2433原始评分/路径/状态选择定义只读AST调用，CPU float64；默认真实评分节点为0,.1,…,.9,.95共11点，不与原文均匀10点混淆。原源码未复制入公共实现，无VLA检查点/机器人运行。
- 精确Gaussian OT的48个预定条件：默认网格20/1062个明确MI排序反转，原文左10点23/1062；连续KL恒等式独立核验通过。经典中点/Gauss–Legendre对照完整保留，Gauss–Legendre20点反转0，不将普通求积升级为核心。
- 接续构造终点sample map严格相同的路径误差：6个ε全部保存，正VFD且任意固定ε>0连续加权积分发散；场不满足人口最优OT假设，不声称推翻前作定理。初次quad绝对容差尺度失败被显式诊断后改成单位ε积分缩放，未删条件。
- 72对/144个两参数普通OLS拟合显示路径项可污染分歧排序；成员独立数据的限制明确。另补同数据不同初始化144个拟合、32/128/512全部终点：充分收敛后分数近零，保留“普通收敛即可解决”强简单解释，不用微小末端KL作实际风险效应量。
- 新读MMG/MINDE数值信息估计、FM Geometry终点污染与prefix规避、一般有符号KL演化，排除普通换积分/去尾/prefix/加校准器为新核心。Scholar实际429，SciSpace恢复可用后仅作为发现，关键结论回到一手原文。
- 生成并实际查看4-panel解析图，附图合同、源数据/hash、SVG/PDF/PNG；只展示解析证据，无机器人成功率、时延收益或p值。
- 当前仅保留“有限拟合路径误差污染epistemic代理”的可核查问题线索；真实VLA任务后果、新方法增量与同题SO101真机均未验证，完整选题目标仍active。
- 四阶段全部新路径重跑与保存JSON逐项一致；Ruff通过，20份一手缓存/31个本地链接/图源脚本hash及三份受保护原始文件通过。冻结计划的一处代数被链接正则误认，核查中单列排除且原计划不改。
- 额外读FM Geometry固定1cb8af4的5份README/实现/许可，源码本已警告normalizer尺度问题，不能靠错用默认归一化制造失效；其数据/权重说明没有提供本轮取得的可绑定真实ensemble。未执行上游或声称复现。
- 提交前检查发现Matplotlib SVG尾空白，保留原导出后仅规范空白、核XML内容等价，并同步导出脚本hash；未改数值结果。README中复述代数的文字被链接正则再次误认，改为自然语言说明，冻结计划保持原样。

## 2026-11-15 VFD版本与公开资产的实际后续

- 上轮为progress：四阶段探针/负对照改变了下一动作，570ef7c已同步；当前完整目标仍active。
- 补读UQ v2，§4/A.2保留OT假设与learned近似，C.7已有flow-time子集消融。新读2608.28010v1 §6.2/A.5保持整个Gaussian边缘路径的旋转场反例，路径代理一般原理不空白。
- 新查Bijou固定ebaa8e0及公开HF metadata：有raw weights但本轮未验证匹配独立flow ensemble/任务能力；一个根README 404如实保留，不推断全库不可用。
- 固定Drishti eeaaaf4，下载前冻结只读资格计划；SQLite Git blob/尺寸/hash检查通过。实际63run、4607step、35/28标签；60条有embedding文件（34/26），6条保留图像。
- 自身审计运行两次逐项一致：完整q/action均6维；805步32维head摘要，非完整chunk或ODE；没有权重hash/数据revision绑定或独立ensemble。t等于步号，不当秒。
- 接续初态检查3条1步成功标签已在当前xy目标区域；当前成功谓词不要求抬升/释放/接触，数据库缺cube/contact，不能独立复算物理抓放。不改标签，不重训检测器，不复算作者AUC。
- FlowEval A.2已有事后关节标签重建导致近hold-position的具体失败；SO101 Bench是此前已审资产，本轮命中不当新发现。
- 当前VFD线移出主推荐、停止扩展纯解析反例，恢复具体任务问题发现。没有确定方向或方法有效性主张；无模型训练/权重下载/上游代码执行。
- 技术检查首次Ruff仅报新审计程序import顺序，执行前修正后通过；不存在失败后删研究条件的操作。

## 2026-11-15 具体失效发现：评分过程与指令必要性

- 上轮7e49b34为progress；本轮停止追VFD并检索同步观测/语义任务可区分性。DAM-VLA/UMI、InstructMove/One Word直接覆盖宽题，缩到“静态多目标不代表轨迹评分需要语言”。
- 固定RoboOrchard f2e041e原样AST评分定义及PickTask builder：N=2/3/6正反序共同扫描均让各目标累计success；single/no-op/reach-only/dwell强对照保留。物理checker是显式事实适配器，非Isaac。
- 原样episode loop组件对双目标各24/53步早停成功；强制同56步但保留累计评分也成功。首完成目标仅匹配其一，这是已知简单对照非新方法。
- 物理计划冻结后实际执行SO101双cube见证：scan AB/BA各462命令/15.4s，两个single各231/7.7s，no-op462/15.4s。真实双指持物抬升每个1.241s，0clip，max穿透约.117mm，无rollout物体pose写入。
- 全5条/1848命令保留；fresh physics replay所有命令、JSON及trace字节一致。audit v2另核single与对应scan全部前缀相同，控制率抬升37连续样本；v1保留。无VLA/原Isaac完整基准/真机或独立随机n主张。
- 初次组件执行因AST遗漏scene_name_of原函数报NameError，输出前失败；查源并加载原helper后恢复，未改源码/删条件。Ruff动态namespace和闭包/import诊断在输出前修正。
- 查新定向读One Word最新v2、InstructMove v1及Inner Monologue作者PDF/Code as Policies v4原始oracle对照，排除简单去oracle/首选择/commit的新颖性。
- Scholar实际HTTP200为验证挑战，0结果卡；保留HTML/hash。SciSpace本轮发现8项metadata后被移除，未借其作全文证据。
- 当前优先深审该测量问题，尚缺对成熟方法判断的实际影响及独立核心增量；完整目标仍active，尚不能确定方向。下一阶段不以增加同类反例替代完整基准与近邻门槛。
