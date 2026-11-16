"""Analytic heading gain of the SO-101 gripper: d(phi)/dq per joint at grasp.

phi is the horizontal direction of the gripper's closing axis (gripper body local
y axis); q are the six commanded joints. Solved by FK on a real E2 approach target
(step 55 of the theta=0 condition, median seed), finite difference 0.05 rad.

Purpose: decide whether orientation compensation can be a joint-space offset (one
number added to one joint) or needs an IK wrapper. Also reports the world-z
component of the gripper approach axis, i.e. how vertical the roll axis is at grasp.

Writes heading_gain.json next to this file.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
XML = HERE.parents[2] / "third_party/SO-ARM100/Simulation/SO101/so101_new_calib.xml"
TAG = "e2-y0-d1"
STEP = 55
H = 0.05


def main() -> None:
    model = mujoco.MjModel.from_xml_path(str(XML))
    data = mujoco.MjData(model)
    gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "gripper")
    names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(6)]

    def axes(q):
        data.qpos[:6] = q
        mujoco.mj_forward(model, data)
        rot = data.xmat[gid].reshape(3, 3)
        y, z = rot[:, 1], rot[:, 2]
        return math.degrees(math.atan2(y[1], y[0])), float(z[2])

    rows = [json.loads(line) for line in (RUNS / TAG / "episodes.jsonl").read_text().splitlines() if line.strip()]
    traces = []
    for row in rows:
        path = RUNS / TAG / f"{row['seed']}.trace.jsonl"
        traces.append(np.array([json.loads(line)["raw_target_rad"] for line in path.read_text().splitlines() if line.strip()]))

    gains: dict[str, list[float]] = {n: [] for n in names}
    zcomp = []
    for tgt in traces:
        q = tgt[STEP].copy()
        phi0, zz = axes(q)
        zcomp.append(zz)
        for j, name in enumerate(names):
            qp = q.copy()
            qp[j] += H
            gains[name].append((axes(qp)[0] - phi0) / H)

    out = {
        "xml": str(XML),
        "probe": {"tag": TAG, "step": STEP, "h_rad": H,
                  "closing_axis": "gripper body local y, world-xy heading (deg)",
                  "n_episodes": len(traces)},
        "dphi_deg_per_rad": {k: float(np.median(v)) for k, v in gains.items()},
        "dphi_rad_per_rad": {k: float(np.median(v) / 57.29577951308232) for k, v in gains.items()},
        "approach_axis_world_z": float(np.median(zcomp)),
    }
    (HERE / "heading_gain.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
