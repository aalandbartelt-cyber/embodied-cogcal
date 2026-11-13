# embodied-cogcal

具身认知标定（Cognitive Calibration）的**本地开发与文档工作区**。

本工作区独立于 EC63 机械臂定位误差项目（`~/research/arm-error-comp`），使用独立的
conda 环境 `cogcal`，不共享 `armec` 环境，也不改动任何原始资料。

## 1. 这个工作区是什么

- 阅读、整理“具身认知标定”方向的文献与讨论记录；
- 编写偏差探针（probe）定义、分析脚本、统计与绘图代码；
- 做视频剪辑、论文图表和实验日志管理；
- 作为 A100 平台代码的本地编辑与版本管理入口。

**它不是** OpenVLA 的模型推理环境。按研究方向记录里的铁律：

> 本地实测为 RTX 5070 Ti Laptop GPU、约 12GB 可见显存、Blackwell Compute Capability 12.0；
> OpenVLA 官方 torch 2.2.0 环境不作为本机主线。7B 主实验放在自强 5000 A100，
> 本机可单独跑 SmolVLA/LeRobot 的 SO-101 Pilot。

本地环境因此只安装分析栈，不安装 torch / transformers / flash-attn，也不下载 15GB 检查点。

## 2. 环境

```bash
wsl
conda activate cogcal
cd ~/research/embodied-cogcal
```

| 项目 | 值 |
|---|---|
| 环境名 | `cogcal` |
| Python | 3.10 |
| 用途 | 本地开发、分析、绘图、文档 |
| 不含 | torch、OpenVLA、LIBERO、模型检查点 |
| Jupyter 内核 | `Python (cogcal)` |
| 精确版本 | `requirements-lock.txt` |
| 隔离 | 已禁用 `~/.local` user-site，包只从 `cogcal` 环境加载 |

首次检查：

```bash
make check       # 版本、路径、文档数量与 SHA256
make test        # 文档归档与路径测试
```

安装/重建见 `docs/environment.md`。

## 3. 目录

```text
embodied-cogcal/
├── docs/
│   ├── 具身认知标定_研究方向形成全记录_20261112.md   # 主记录（含六份子文档与 W1 清单）
│   ├── CORE_HYPOTHESIS.md                         # ECCBF 核心假设与声称边界
│   ├── ROADMAP.md                                 # 仿真—SO-101 路线
│   ├── prior-art/                                  # 查新记录与差异矩阵
│   ├── README.md                                   # 文档索引与阅读顺序
│   ├── environment.md                              # 本地环境说明
│   └── reference/                                  # 9 份参考笔记 + SHA256
├── configs/                  # 本地环境与 SO-101 实验配置
├── probes/                   # ECCBF 四格因子探针定义
├── analysis/                 # 指标、统计契约与 episode 汇总脚本
├── experiments/              # 实验日志模板与 SO-101 运行约定
├── results/
│   ├── figures/
│   └── videos/
├── notebooks/
├── src/cogcal/               # 轻量路径与工具包
├── scripts/check_env.py
├── tests/
├── Makefile
├── pyproject.toml
└── requirements.txt
```

## 4. 文档入口

先读主记录：

[docs/具身认知标定_研究方向形成全记录_20261112.md](docs/具身认知标定_研究方向形成全记录_20261112.md)

再按 [docs/README.md](docs/README.md) 的索引读 9 份参考笔记。索引里标了每份文档的类型、
一句话内容和建议用法。

## 5. W1 的分工（摘要）

| 位置 | 任务 |
|---|---|
| 本地 `cogcal` | 读文档、写探针/分析代码、画图、剪视频、维护实验日志 |
| A100 `openvla` | Python 3.10 + torch 2.2.0+cu121 + transformers 4.40.1 + timm 0.9.10 + flash-attn 2.5.5 |
| A100 运行 | LIBERO-Spatial 基线、OpenVLA 检查点、`MUJOCO_GL=egl` 渲染、冒烟评测、首条 mp4 |

W1 的完整八步、验收清单和常见坑见主记录第七部分（W1 环境搭建操作清单）。

## 6. 当前状态与下一步

- [x] 独立项目目录与 `cogcal` 环境
- [x] 主记录 + 9 份参考文档归档（SHA256 固定）
- [x] A100 账号/资源已确认（模型运行仍在平台侧）
- [ ] SO-101 数字孪生与 SO-101 兼容模型冒烟
- [x] ECCBF 核心假设、查新记录模板、四格探针和统计契约已落地
- [ ] Pilot：确认语义×执行交互项与任务成功率下降
- [ ] 正式仿真矩阵与 SO-101 真机外部效度验证

公开路线图见 [docs/ROADMAP.md](docs/ROADMAP.md)。当前 B 路线的核心是
**具身条件化认知偏差场（ECCBF）**：在同一 SO-101 数字孪生和真实 SO-101 上，分解
语义冲突、执行误差及其交互项，并以任务成功率提升作为主结果。LIBERO/OpenVLA 作为
次级可比基准，不替代同体仿真—真机主线。

## 7. 三条纪律

1. **环境分开**：`cogcal` 只做分析；本机模型 Pilot 使用独立 `cogcal-sim`，OpenVLA 7B 正式实验上 A100。
2. **笔记不等于一手证据**：`docs/reference` 是二手笔记/综述，正式引用必须回到原论文。
3. **不越级声称**：仿真探针结果不能写成真机验证；年底目标是“可投稿实验包”，不是 SCI 录用。
