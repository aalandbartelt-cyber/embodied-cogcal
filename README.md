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

> 本地 5070 Ti 是 Blackwell sm_120，OpenVLA 官方 torch 2.2.0 环境不兼容；
> 7B 模型的加载、评测与 MuJoCo EGL 渲染全部放在自强 5000 A100 上。

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
│   ├── README.md                                   # 文档索引与阅读顺序
│   ├── environment.md                              # 本地环境说明
│   └── reference/                                  # 9 份参考笔记 + SHA256
├── configs/local.yaml        # 本地角色、路径、W1 关键参数
├── probes/                   # 偏差探针定义（W2 开始填充）
├── analysis/                 # 分析脚本与统计契约（W2 开始填充）
├── experiments/              # 实验日志模板与运行记录
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
- [ ] A100 账号/资源申请与 `openvla` 环境（平台侧执行）
- [ ] LIBERO 冒烟 + EGL 渲染 + 首条视频（平台侧）
- [ ] W2：分析契约（偏差指数、条件、样本量、检验）与锚定/WYSIATI 探针设计（本地起草）

公开路线图见 [docs/ROADMAP.md](docs/ROADMAP.md)。当前采用 B 方案：锚定效应 + WYSIATI，
先用一个模型跑通最小科学闭环，再用第二个模型做验证性复现。第一版主结果来自
LIBERO/MuJoCo；SO-101/LeRobot 低成本真机只作为后续外部效度验证，不替代仿真主实验。

## 7. 三条纪律

1. **本地不跑模型**：5070 Ti 只做开发与分析；模型推理全部上 A100。
2. **笔记不等于一手证据**：`docs/reference` 是二手笔记/综述，正式引用必须回到原论文。
3. **不越级声称**：仿真探针结果不能写成真机验证；年底目标是“可投稿实验包”，不是 SCI 录用。
