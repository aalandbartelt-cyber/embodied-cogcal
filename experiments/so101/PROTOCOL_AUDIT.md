# 候选探针协议审计

日期：2026-11-14。审计对象是 metadata 生成器，不是策略评测。
机器可读观察：[protocol-audit.json](protocol-audit.json)。

## 实际执行

对 `generate_records(num_scenes=100, seed=42)` 实际生成并归一化比较：

| 项目 | 实测 |
|---|---:|
| 四格记录数 | 400 |
| 唯一 scene_id | 100 |
| 唯一物理 placements | 8 |
| 唯一 placements + 当前目标组合 | 16 |
| task_id 标签 | 2 |
| 去掉颜色差异后的实际任务指令模板 | 1 |

生成器 SHA256 见 JSON。当前两个 task_id 都对应“抓起指定颜色方块，放入绿色区域”，
不同标签不能作为独立任务家族，更不能做一个校准、另一个 held-out 后宣称跨任务。

## 语义因子实际是什么

四格中当前合法目标保持相同，conflict 只增加 `Previous plan (superseded)` 的另一颜色旧计划。
这是**作废计划文本干扰**候选；物体仍存在、当前任务合法，不是 ICBench 的无解语言—场景矛盾，
也不是在动作执行中实际收到新指令。论文和汇报应采用这个操作定义。

主对照还需要等长度/近似 token 长度的无冲突旧计划、同义改写、颜色/左右平衡，以及旧目标/新目标计分。
不直接把 neutral 与长 prompt 的差全部解释为锚定。以上对照尚未实现，不声称已生成完整正式基准。

## 必须修订后才能正式采样

1. 定义真正不同的任务谓词与动作需求，例如放入区域、相对位置关系等；先用专家/脚本或人工验证可达，
   再冻结任务划分。此处是候选例子，不代表相关任务已实现或可解。
2. 把 reset manifest 按实际 placements/target/任务谓词分组；训练/开发/测试按该组隔离。
3. 如增加连续随机布局，应验证可达、无初始碰撞、相机可见与任务合法；不能只给重复位置换 ID。
4. 区分独立 reset、重复同一 reset 的推理采样与训练初始化；相同物理状态重放不能扩大独立场景 N。
5. 0/3 control-step delay 只是 JSON 配置；runner 未注入时不能声称已测试延迟。

## 重跑本次审计

```bash
conda activate cogcal
python - <<'PY'
import json
from probes.generators.eccbf_factorial import generate_records
rows = generate_records(num_scenes=100, seed=42)
neutral = [r for r in rows if r['condition_id'] == 'neutral_nominal']
canonical = lambda x: json.dumps(x, sort_keys=True)
print('records', len(rows))
print('placements', len({canonical(r['scene_metadata']['placements']) for r in neutral}))
print('placement_target', len({canonical([r['scene_metadata']['placements'], r['current_target_color']]) for r in neutral}))
print('templates', {r['instruction'].replace('red', 'COLOR').replace('blue', 'COLOR') for r in neutral})
PY
```

这些计数只用于审计场景覆盖，不得填入论文的 VLA 成功率或样本量证明。
