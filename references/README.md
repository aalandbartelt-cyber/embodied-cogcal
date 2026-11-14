# 可追溯文献库

截至 2026-11-14：47 篇研究/方法文献，另有 3 项官方工程来源，共 50 条。没有本项目效果数字。
这不是固定参考文献数量要求，纳入规则是对研究问题、近邻比较、平台或证据设计有实际作用。

## 使用

- Zotero / EndNote / JabRef：导入 `research.bib`；也提供 `research.ris`，两种格式选一种，避免重复导入。
- Excel / 表格：打开 `reading-list.csv`。
- 人读目录：[CATALOG.md](../docs/literature/CATALOG.md)；逐项保存 Scholar 题名检索入口。
- `catalog.json` 保存完整作者、引用版本、分类、证据等级和使用目的。
- `metadata-arxiv.json`、`metadata-arxiv-additional.json`、`metadata-arxiv-alternatives.json`
  保存共 41 篇原始页面 citation meta；不收录全文或摘要。另有 6 篇通过 Crossref 核验的经典/方法文献。
- `metadata-publishers.json` 保存 Crossref 原始登记元数据及 PMLR/CVF 页元数据和获取失败。
  响应 SHA256 用于标记本次访问版本，不承诺动态网页以后仍有相同哈希。

## 版本纪律

1. OpenVLA 引正式 PMLR 2025 版；2024 是首次预印本年。正式版作者列表与 arXiv 不完全相同，未混合。
2. LIBERO 引 NeurIPS 2023 原始记录；IGAR 引已直接核对的 Springer ECCV 2026 出版记录。
3. LIBERO-Plus 引 CVPR 2026 的 Progressive 标题；其 arXiv v3 仍是 In-depth 标题。
   当前方法阅读来自 arXiv，未假称本次读取被 403 拒绝的正式版 PDF。
4. 其余 arXiv 项按固定版本导出 `@misc`；`formal_status_not_checked` 不表示论文从未被录用。
5. DOI 仅从出版记录/Crossref 核实后填写；没有猜填作者、页码、DOI 或发表 venue。
6. 官方网页不猜填发表年，保留访问日期；网页来源不计入 47 篇研究文献。
7. 团体作者按团体处理；未用 `et al.` 截掉原始作者列表。RIS 保留原始题名中的数学标记，
   用于正式排版时再按目标模板检查字体和转义，当前未声称 LaTeX 全稿编译通过。

## 尚待复核，未加入主库

| 项目 | 已有线索 | 缺口/处理 |
|---|---|---|
| Holm (1979), A Simple Sequentially Rejective Multiple Test Procedure | [原始 JSTOR 入口](https://www.jstor.org/stable/4615733)；[国家图书馆目录](https://ndlsearch.ndl.go.jp/en/books/R100000136-I1572543024862166272) | 原始页只返回脚本，原始 PDF 403，候选 DOI 的 Crossref 请求 404；不猜填 DOI，不标已精读 |
| 主要近邻的最新正式录用与代码状态 | 每篇原始页面和已有官方仓库 | 论文存在不等于全部实验/权重已公开或复现；投稿前再次检查 |
| Scholar 被引与引用链 | 逐篇 Scholar URL | 直接 Scholar 页面不可访问；没有伪造被引数或宣称已完成 Scholar forward-citation sweep |

原始引用键用于 `docs/paper` 中的 `[@key]`；这是写作准备语法，不是已经排版的最终编号。
SIMPLER 也按已核对的 PMLR 2025 正式版引用，其预印本年为 2024。

## 后续独立补充

- `supplement-deep-audit.bib` / `.ris` / `supplement-deep-audit-metadata.json`：31条固定版本记录，
  对应30篇新增论文（Ao 的v1/v2题名与方法变化，刻意分开保留）。与主库不重复；
  完整作者、原始 citation meta、来源哈希、Scholar 入口保留。
  [深审阅读入口](../docs/literature/DEEP_AUDIT_READING_GUIDE.md)区分正文阅读与仅元数据核验。
  其中 Continual VLA 的 ICML2026/PMLR 正式版已核实；其他正式发表状态未逐项检查。
  Ao v1 的 abs 元数据漏词，导出题名从原始全文核实并保存覆盖依据，不猜填。
  实际读回与来源对应检查见 [supplement-validation.json](supplement-validation.json)；不是Zotero GUI导入或论文复现。

- `supplement-supermimic.bib` / `supplement-supermimic-metadata.json`：用户追加的原始 SuperMimic 论文和 UniSuperMimic 独立复现，
  不并入上述冻结 50 条。[适用性评估](../docs/literature/UNISUPERMIMIC_ASSESSMENT.md) 明确静态核验与运行边界。
