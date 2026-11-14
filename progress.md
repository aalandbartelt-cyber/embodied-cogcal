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
