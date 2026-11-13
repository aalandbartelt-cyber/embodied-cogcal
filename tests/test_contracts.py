from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_so101_config_contains_primary_endpoint_and_safety_gate():
    config = yaml.safe_load((ROOT / "configs/so101.yaml").read_text(encoding="utf-8"))
    assert config["route"] == "eccbf_same_embodiment"
    assert config["policy"]["freeze_policy_during_calibration"] is True
    assert config["real"]["require_shadow_mode"] is True


def test_factorial_probe_has_exactly_four_conditions_and_forbids_privileged_inputs():
    probe = yaml.safe_load(
        (ROOT / "probes/definitions/eccbf_factorial.yaml").read_text(encoding="utf-8")
    )
    assert len(probe["conditions"]) == 4
    assert "evaluator_target_pose" in probe["runtime_inputs"]["forbidden"]


def test_analysis_contract_declares_primary_success_endpoint():
    contract = yaml.safe_load(
        (ROOT / "analysis/contracts/calibration_v1.yaml").read_text(encoding="utf-8")
    )
    assert contract["primary_endpoint"]["name"] == "task_success"
    assert contract["exclusion"]["never_silently_drop"] is True
