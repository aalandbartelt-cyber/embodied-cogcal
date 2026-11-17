# E8 运行准备与确定性核查

日期：2026-11-17（Asia/Shanghai）。此目录只包含工具链 smoke 和审计，不是正式负偏航剂量试验，也不作为验证科学假设的数据。

## 固定观测的 ACT 推理

从训练数据 seed 4100 的已有文件中取帧 0、90、180（先核对数据集索引中记录的文件 SHA-256）。两个独立启动的官方 `infer_worker.py` 在每帧进行连续两次推理、reset 后再推理一次：共 18 个 100×6 action chunk。以同帧、首 worker 首次结果为参照，全部元素逐浮点相等，最大差 0；各输入、输出、checkpoint、源脚本哈希和软件环境见 `worker_determinism_result.json`。

这只是同一机器、同一训练示范的 3 个固定输入；没有对模拟环境执行步进，不能推广为 GPU 普遍确定性、跨版本结果一致或闭环轨迹完全一致，也不能补回旧实验中未记录的 RNG 状态。此测试会重复推理，但不创建模拟 episode 或改变任何原始数据。

## 既有 runner 的独立 smoke

在 `smoke-14100-14101/SMOKE_PLAN.md` 先记录后，沿用旧 E8 运行器，分别在 seed 14100、14101 上运行固定 q5 偏置 0° 和 −7.5°，每臂 2 集，每集 330 控制步。两臂 shell exit 0，完整 stdout/stderr、合同、轨迹和 physics 输出保存在该子目录。只读校验 `verification_v3.json` 对四集的合同/source/checkpoint、轨迹和物理哈希、保存的物理序列与结果、330 步、每步注入及跨臂已记录初始位置、关节角和首帧图像哈希全部通过。配对字段一致不证明未记录的 RNG 状态一致。

四集任务判定均为成功，但每条件仅两集，**不能用于任何统计结论或最佳剂量判断**。零剂量无命令裁剪；−7.5° 条件 seed 14100 有一次第 4 个关节（数组索引 3）命令被裁剪，第 5 个关节无裁剪；另两集及该臂另一集均无裁剪。四集最大穿透 0.193 mm，小于原 1.5 mm 门槛。

必须披露：旧 runner 在固定剂量时仍执行 RGB yaw 估计器并以估计误差作为准入门槛；产物合同中的 E8 prereg hash 是旧 runner 固定引用，**不是这轮 smoke 的预注册**。另外其 episode 字段 `q5_bias_est_deg` 无论模式都写入视觉估计值，而不是固定剂量；实际剂量应由合同、`q5_bias_est_rad` 和逐步 raw/policy 差额核对。脚本不修改旧 runner，正式试验应以新的、独立登记的合同与明确字段修正。

种子清单结果及跳过项记录在 `smoke_seed_inventory.json`，仅现有草案引用 14100–14101，当前可读取文本未发现已识别历史使用；二进制、过大文件、Git 对象、外部历史及未识别格式未全面覆盖，不能证明种子全球新鲜。

归档边界：清单包含本机文件路径，保留在本地、不纳入本次 Git 提交；四份 physics NPZ 也按项目现有忽略规则留在本地，文件哈希保存在逐集记录和验证报告中。四条控制轨迹、合同、逐集记录、日志与验证报告纳入本地 Git。缺少 physics NPZ、模型或其他外置资产时，克隆仓库不能完成全部物理级复核。

## 复核

在本目录使用 `/home/mary/miniconda3/envs/cogcal-sim/bin/python -m unittest -v test_verify_smoke`；如需再次只读检查，使用新的输出文件名：

```bash
/home/mary/miniconda3/envs/cogcal-sim/bin/python verify_smoke.py \
  --repo /home/mary/research/embodied-cogcal --smoke smoke-14100-14101 \
  --out smoke-14100-14101/verification_new.json
```

固定输入测试的单元测试为 `/home/mary/.cache/cogcal/venvs/tpsc-policy/bin/python -m unittest -v test_worker_determinism`；完整固定输入核查使用同一解释器运行 `worker_determinism.py --repo /home/mary/research/embodied-cogcal --out <新的不存在的结果路径>`。真实模型、训练数据和部分物理工件不一定包含在 Git 仓库中，需先按记录中的哈希准备。运行脚本不会覆盖现有结果。
