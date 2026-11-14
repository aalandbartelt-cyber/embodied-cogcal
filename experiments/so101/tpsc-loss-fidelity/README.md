# 固定源码的损失忠实性核算

这不是策略训练或机器人实验。解读见
[更正报告](../../../docs/prior-art/tpsc-loss-fidelity-correction.md)。

- `source-loss-audit.json`：真实调用上游 `compute_losses` 的 CPU 输出及 autograd；原 toy 不覆盖。
- `source-contracts.json`：公开 BAS-VLA artifact 的 revision、元数据哈希和实际 per_step / legacy 契约。
- 主入口：`scripts/audit_tpsc_loss_fidelity.py`，先校验三个上游文件 SHA256；输出文件要求不存在。

复现先下载固定源码（不安装上游项目、不下载权重）：

```bash
python - <<'PY'
from pathlib import Path
from urllib.request import urlopen
root = Path('/tmp/tpsc-bas-loss-audit-repro')
base = 'https://raw.githubusercontent.com/NEBULIS-Lab/Beyond-Appearance-Shifts/51f0dab5b2edab6539f3bccda7a04b3cb1d52a6c/'
for name in ['bas_vla/breaking/training.py', 'bas_vla/breaking/residual_adapter.py', 'docs/training.md']:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(urlopen(base + name, timeout=30).read())
PY
env -u PYTHONPATH PYTHONNOUSERSITE=1 \
  /home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python \
  scripts/audit_tpsc_loss_fidelity.py \
  --source-root /tmp/tpsc-bas-loss-audit-repro \
  --out /tmp/tpsc-loss-audit-repro.json
```

另一个有 PyTorch / NumPy 的 Python 环境也可运行；原记录注明 Python3.10、torch2.7.1+cu128，
所有计算明确在 CPU。结论只覆盖记录中的输出布局、IdentityAdapter 和数值条件。
