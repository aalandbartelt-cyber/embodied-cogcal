#!/usr/bin/env python
"""Offline preflight checks for the A100 OpenVLA environment."""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

EXPECTED_PACKAGES = {
    "torch": "2.2.0",
    "torchvision": "0.17.0",
    "transformers": "4.40.1",
    "tokenizers": "0.19.1",
    "timm": "0.9.10",
    "flash-attn": "2.5.5",
}


@dataclass
class GpuInfo:
    available: bool
    count: int
    name: str
    capability: tuple[int, int] | None
    torch_version: str
    cuda_version: str


@dataclass
class GitInfo:
    commit: str
    dirty: bool


@dataclass
class DiskInfo:
    path: Path
    free_bytes: int


@dataclass
class PreflightState:
    python_version: tuple[int, int, int]
    packages: dict[str, str]
    gpu: GpuInfo
    environment: dict[str, str]
    git: GitInfo
    disk: DiskInfo


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    message: str


def package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for package in EXPECTED_PACKAGES:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "MISSING"
    return versions


def gpu_info() -> GpuInfo:
    try:
        import torch
    except ModuleNotFoundError:
        return GpuInfo(False, 0, "torch is not installed", None, "MISSING", "MISSING")

    available = bool(torch.cuda.is_available())
    count = int(torch.cuda.device_count())
    if not available or count == 0:
        return GpuInfo(False, count, "CUDA is unavailable", None, torch.__version__, str(torch.version.cuda))
    return GpuInfo(
        True,
        count,
        str(torch.cuda.get_device_name(0)),
        tuple(torch.cuda.get_device_capability(0)),
        torch.__version__,
        str(torch.version.cuda),
    )


def git_info(root: Path) -> GitInfo:
    try:
        commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        return GitInfo(commit, dirty)
    except (OSError, subprocess.CalledProcessError):
        return GitInfo("UNAVAILABLE", True)


def disk_info(environment: dict[str, str]) -> DiskInfo:
    configured = environment.get("COGCAL_STORAGE_ROOT", "")
    path = Path(configured).expanduser() if configured else Path.cwd()
    try:
        usage = shutil.disk_usage(path)
        return DiskInfo(path, int(usage.free))
    except OSError:
        return DiskInfo(path, 0)


def collect_state(root: Path | None = None) -> PreflightState:
    root = (root or Path.cwd()).resolve()
    environment = dict(os.environ)
    return PreflightState(
        python_version=tuple(sys.version_info[:3]),
        packages=package_versions(),
        gpu=gpu_info(),
        environment=environment,
        git=git_info(root),
        disk=disk_info(environment),
    )


def _check_python(version: tuple[int, int, int]) -> CheckResult:
    ok = version[:2] == (3, 10)
    message = f"Python {'.'.join(map(str, version))}; expected 3.10.x"
    return CheckResult("python", ok, message)


def _check_packages(packages: dict[str, str]) -> CheckResult:
    mismatches = [
        f"{name}={packages.get(name, 'MISSING')} (expected {expected})"
        for name, expected in EXPECTED_PACKAGES.items()
        if packages.get(name) != expected
    ]
    if mismatches:
        return CheckResult("packages", False, "version mismatch: " + "; ".join(mismatches))
    return CheckResult("packages", True, "all pinned OpenVLA packages match")


def _check_gpu(gpu: GpuInfo) -> CheckResult:
    is_a100 = gpu.available and "A100" in gpu.name.upper() and gpu.capability == (8, 0)
    message = (
        f"{gpu.name}, count={gpu.count}, capability={gpu.capability}, "
        f"torch={gpu.torch_version}, cuda={gpu.cuda_version}"
    )
    if not is_a100:
        return CheckResult("gpu", False, f"A100 required; {message}")
    return CheckResult("gpu", True, message)


def _check_runtime_environment(environment: dict[str, str]) -> CheckResult:
    problems: list[str] = []
    if environment.get("MUJOCO_GL") != "egl":
        problems.append("MUJOCO_GL must be egl")
    device_id = environment.get("MUJOCO_EGL_DEVICE_ID", "")
    if not device_id.isdigit():
        problems.append("MUJOCO_EGL_DEVICE_ID must be a non-negative integer")
    for variable in ("HF_HOME", "COGCAL_STORAGE_ROOT"):
        if not environment.get(variable):
            problems.append(f"{variable} is missing")
    try:
        if float(environment.get("COGCAL_MIN_FREE_GB", "30")) <= 0:
            problems.append("COGCAL_MIN_FREE_GB must be positive")
    except ValueError:
        problems.append("COGCAL_MIN_FREE_GB must be numeric")
    if problems:
        return CheckResult("runtime_env", False, "; ".join(problems))
    return CheckResult("runtime_env", True, "EGL, cache and storage variables are configured")


def _check_git(git: GitInfo) -> CheckResult:
    if git.dirty or git.commit == "UNAVAILABLE":
        return CheckResult("git", False, f"commit={git.commit}, working tree is dirty or unavailable")
    return CheckResult("git", True, f"commit={git.commit}")


def _check_disk(disk: DiskInfo, environment: dict[str, str]) -> CheckResult:
    try:
        minimum_gb = float(environment.get("COGCAL_MIN_FREE_GB", "30"))
    except ValueError:
        minimum_gb = 30.0
    minimum_bytes = int(minimum_gb * 1024**3)
    free_gb = disk.free_bytes / 1024**3
    ok = disk.free_bytes >= minimum_bytes
    return CheckResult(
        "disk",
        ok,
        f"path={disk.path}, free={free_gb:.1f} GiB, required={minimum_gb:.1f} GiB",
    )


def run_checks(state: PreflightState) -> list[CheckResult]:
    return [
        _check_python(state.python_version),
        _check_packages(state.packages),
        _check_gpu(state.gpu),
        _check_runtime_environment(state.environment),
        _check_git(state.git),
        _check_disk(state.disk, state.environment),
    ]


def _jsonable_state(state: PreflightState) -> dict[str, Any]:
    payload = asdict(state)
    payload["environment"] = {
        name: state.environment.get(name, "")
        for name in (
            "MUJOCO_GL",
            "MUJOCO_EGL_DEVICE_ID",
            "HF_HOME",
            "COGCAL_STORAGE_ROOT",
            "COGCAL_MIN_FREE_GB",
        )
    }
    payload["disk"]["path"] = str(state.disk.path)
    payload["gpu"]["capability"] = list(state.gpu.capability) if state.gpu.capability else None
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    state = collect_state(args.root)
    checks = run_checks(state)
    failed = [check for check in checks if not check.ok]
    if args.json:
        print(
            json.dumps(
                {
                    "ok": not failed,
                    "state": _jsonable_state(state),
                    "checks": [asdict(check) for check in checks],
                }
            )
        )
    else:
        print(f"python: {platform.python_version()}")
        for check in checks:
            print(f"[{ 'PASS' if check.ok else 'FAIL' }] {check.name}: {check.message}")
        print(f"A100 PREFLIGHT: {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
