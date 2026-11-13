# 本地环境说明（cogcal）

## 1. 定位

`cogcal` 是**本地开发与分析环境**，不是 OpenVLA 推理环境。

按研究方向记录中的分工：

| 位置 | 用途 | 是否装模型 |
|---|---|---|
| 本地 WSL + RTX 5070 Ti Laptop（实测约 12GB） | 分析、SmolVLA/LeRobot Pilot、绘图、剪视频、维护日志 | 不装 OpenVLA 7B 官方环境 |
| 自强 5000 A100 | OpenVLA 加载、LIBERO 评测、EGL 渲染、批量实验 | 是 |

原因：本机是 Blackwell Compute Capability 12.0，且实测可见显存约 12GB；OpenVLA 官方仓库
固定 PyTorch 2.2.* 和旧版依赖，不能按官方环境稳定承载 7B 主实验。本机如需模型，另建
`cogcal-sim` 跑 SmolVLA/LeRobot，不污染 `cogcal`。

本机路线详见 [LOCAL_GPU_ROUTE.md](LOCAL_GPU_ROUTE.md)。

## 2. 当前环境

| 项目 | 值 |
|---|---|
| WSL | Ubuntu 22.04 |
| Conda 环境 | `cogcal` |
| 路径 | `~/miniconda3/envs/cogcal` |
| Python | 3.10 |
| Jupyter 内核 | `Python (cogcal)` |
| 主要包 | numpy / pandas / scipy / scikit-learn / matplotlib / seaborn / imageio / jupyterlab / pytest / ruff / pyyaml / tqdm / statsmodels / openpyxl / pyarrow |
| 明确不装 | torch、torchvision、transformers、flash-attn、OpenVLA、LIBERO、模型检查点 |

激活：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cogcal
cd ~/research/embodied-cogcal
```

### 2.1 环境隔离（重要）

本机 `~/.local/lib/python3.10/site-packages` 里已有一批共享包（numpy/pandas 等），而
Python 默认会把 user-site 排在 conda 环境之前。第一次安装时 pip 因此把部分包判定为
“已满足”，没有装进 `cogcal`。现已做两层隔离：

1. 激活钩子：`~/miniconda3/envs/cogcal/etc/conda/activate.d/no_user_site.sh`
   设置 `PYTHONNOUSERSITE=1`；
2. Jupyter 内核 `Python (cogcal)` 的 `kernel.json` 也设置了 `PYTHONNOUSERSITE=1`。

验证包确实来自环境：

```bash
conda activate cogcal
python -c "import numpy, pandas; print(numpy.__file__); print(pandas.__file__)"
# 期望路径包含 /envs/cogcal/lib/python3.10/site-packages/
```

精确版本已冻结在 `requirements-lock.txt`。

## 3. 从零重建

```bash
conda create -y -n cogcal python=3.10
conda activate cogcal

# 隔离 user-site，避免 ~/.local 的包混进来
ENV=~/miniconda3/envs/cogcal
mkdir -p $ENV/etc/conda/activate.d $ENV/etc/conda/deactivate.d
printf 'export PYTHONNOUSERSITE=1\n' > $ENV/etc/conda/activate.d/no_user_site.sh
printf 'unset PYTHONNOUSERSITE\n'    > $ENV/etc/conda/deactivate.d/no_user_site.sh

python -m pip install -U pip
python -m pip install --ignore-installed -r requirements.txt

python -m ipykernel install --user --name cogcal --display-name "Python (cogcal)"
python -m pip install -e . --no-deps
make check
```

安装后检查内核 `kernel.json` 是否含 `"PYTHONNOUSERSITE": "1"`；若没有，手动加上。

## 4. Jupyter

```bash
cd ~/research/embodied-cogcal
jupyter lab --no-browser --ip=0.0.0.0 --port=8891
```

浏览器打开终端输出的 `http://127.0.0.1:8891/...`，内核选 **Python (cogcal)**。
端口用 8891，避免和 `arm-error-comp` 的 8888 冲突。

## 5. 与 A100 环境的边界

A100 上的 `openvla` 环境是另一套契约，不要用本地的 `cogcal` 去装它：

```text
Python 3.10
torch 2.2.0 + cu121
torchvision 0.17.0 / torchaudio 2.2.0
transformers 4.40.1
tokenizers 0.19.1
timm 0.9.10
flash-attn 2.5.5
```

完整八步、检查点、LIBERO 安装、EGL 渲染、冒烟评测与验收清单见主记录第七部分。

本地只负责把代码写好、提交到 git，然后在 A100 上 pull 运行。

## 6. 如果以后确实要在本地跑仿真

可以另开一个环境（例如 `cogcal-sim`），不要污染 `cogcal`。LIBERO/robosuite 的
MuJoCo 渲染在 WSL 里需要 EGL/OSMesa，且与 torch 版本强相关；这属于平台侧工作，
不建议在本地作为 W1 任务。

## 7. 常见问题

**`conda activate cogcal` 找不到**
执行 `source ~/miniconda3/etc/profile.d/conda.sh`，或 `conda init bash` 后重开终端。

**`import numpy` 的路径指向 `~/.local`**
说明 `PYTHONNOUSERSITE` 没生效。检查激活钩子是否存在，或手动
`export PYTHONNOUSERSITE=1` 后再启动 Python。Jupyter 里则检查内核 `kernel.json`。

**不要在这里 `pip install torch`**
会把环境变成半模型环境，既跑不动 OpenVLA，又可能破坏分析栈的 numpy 版本。
需要模型时上 A100。

**Jupyter 端口冲突**
改 `--port=8892` 或先 `ss -ltnp | grep 889` 查看占用。

**文档更新**
`docs/reference/` 是 2026-11-13 的快照；如果原始笔记更新，重新复制并更新
`MANIFEST.sha256`，不要直接编辑快照。
