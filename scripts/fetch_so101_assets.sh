#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSET_DIR="${ROOT_DIR}/third_party/SO-ARM100"
REPO_URL="https://github.com/TheRobotStudio/SO-ARM100.git"
PINNED_COMMIT="a758567c3978dfeefe282ede0500085a48fe8f78"

mkdir -p "${ROOT_DIR}/third_party"

if [[ ! -d "${ASSET_DIR}/.git" ]]; then
  git clone --depth=1 "${REPO_URL}" "${ASSET_DIR}"
fi

git -C "${ASSET_DIR}" fetch --depth=1 origin "${PINNED_COMMIT}"
git -C "${ASSET_DIR}" checkout --detach "${PINNED_COMMIT}"

MODEL="${ASSET_DIR}/Simulation/SO101/scene.xml"
if [[ ! -f "${MODEL}" ]]; then
  echo "SO-101 MuJoCo scene not found: ${MODEL}" >&2
  exit 1
fi

echo "SO-101 assets ready: ${ASSET_DIR}"
echo "Pinned commit: ${PINNED_COMMIT}"
echo "MuJoCo scene: ${MODEL}"
