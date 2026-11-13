from __future__ import annotations

from pathlib import Path

import pytest

from scripts.a100_preflight import (
    DiskInfo,
    GitInfo,
    GpuInfo,
    PreflightState,
    _jsonable_state,
    run_checks,
)

EXPECTED_PACKAGES = {
    "torch": "2.2.0",
    "torchvision": "0.17.0",
    "transformers": "4.40.1",
    "tokenizers": "0.19.1",
    "timm": "0.9.10",
    "flash-attn": "2.5.5",
}


def passing_state(tmp_path: Path) -> PreflightState:
    return PreflightState(
        python_version=(3, 10, 13),
        packages=EXPECTED_PACKAGES.copy(),
        gpu=GpuInfo(
            available=True,
            count=1,
            name="NVIDIA A100-SXM4-40GB",
            capability=(8, 0),
            torch_version="2.2.0",
            cuda_version="12.1",
        ),
        environment={
            "MUJOCO_GL": "egl",
            "MUJOCO_EGL_DEVICE_ID": "0",
            "HF_HOME": str(tmp_path / "hf"),
            "COGCAL_STORAGE_ROOT": str(tmp_path),
            "COGCAL_MIN_FREE_GB": "1",
        },
        git=GitInfo(commit="abc123", dirty=False),
        disk=DiskInfo(path=tmp_path, free_bytes=2 * 1024**3),
    )


def test_passing_state_has_no_failed_checks(tmp_path):
    checks = run_checks(passing_state(tmp_path))

    assert all(check.ok for check in checks), [check.message for check in checks if not check.ok]


def test_cuda_wheel_local_versions_satisfy_package_contract(tmp_path):
    state = passing_state(tmp_path)
    state.packages.update(torch="2.2.0+cu121", torchvision="0.17.0+cu121")

    checks = run_checks(state)

    assert next(check for check in checks if check.name == "packages").ok is True


@pytest.mark.parametrize("version", ["2.2.1+cu121", "2.2.0rc1+cu121", "MISSING"])
def test_incorrect_torch_public_version_is_rejected(tmp_path, version):
    state = passing_state(tmp_path)
    state.packages["torch"] = version

    checks = run_checks(state)

    assert next(check for check in checks if check.name == "packages").ok is False


@pytest.mark.parametrize("threshold", ["nan", "inf", "-inf", "0", "-1", "invalid"])
def test_invalid_disk_threshold_is_reported_without_crashing(tmp_path, threshold):
    state = passing_state(tmp_path)
    state.environment["COGCAL_MIN_FREE_GB"] = threshold
    state.disk.free_bytes = 1000 * 1024**3

    checks = run_checks(state)

    assert next(check for check in checks if check.name == "runtime_env").ok is False
    assert next(check for check in checks if check.name == "disk").ok is False


def test_large_finite_disk_threshold_fails_without_overflow(tmp_path):
    state = passing_state(tmp_path)
    state.environment["COGCAL_MIN_FREE_GB"] = "1e308"

    checks = run_checks(state)

    assert next(check for check in checks if check.name == "disk").ok is False


def test_non_a100_gpu_is_rejected(tmp_path):
    state = passing_state(tmp_path)
    state.gpu = GpuInfo(True, 1, "NVIDIA RTX 4090", (8, 9), "2.2.0", "12.1")

    checks = run_checks(state)

    gpu_check = next(check for check in checks if check.name == "gpu")
    assert gpu_check.ok is False
    assert "A100" in gpu_check.message


def test_missing_required_runtime_environment_is_reported(tmp_path):
    state = passing_state(tmp_path)
    state.environment.pop("MUJOCO_GL")
    state.environment.pop("HF_HOME")

    checks = run_checks(state)

    env_check = next(check for check in checks if check.name == "runtime_env")
    assert env_check.ok is False
    assert "MUJOCO_GL" in env_check.message
    assert "HF_HOME" in env_check.message


def test_dirty_git_and_low_disk_are_blocking(tmp_path):
    state = passing_state(tmp_path)
    state.git = GitInfo(commit="abc123", dirty=True)
    state.disk = DiskInfo(path=tmp_path, free_bytes=0)

    checks = run_checks(state)

    assert next(check for check in checks if check.name == "git").ok is False
    assert next(check for check in checks if check.name == "disk").ok is False


def test_json_state_does_not_emit_unrelated_environment_secrets(tmp_path):
    state = passing_state(tmp_path)
    state.environment["HF_TOKEN"] = "do-not-print"

    payload = _jsonable_state(state)

    assert "HF_TOKEN" not in payload["environment"]
