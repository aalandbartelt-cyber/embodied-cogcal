"""Read-only contact instrumentation of a pinned external scripted controller.

This is a carrier qualification check, separate from the frozen TPSC pilot.
The external model has explicit box finger pads and friction 2.0; this does
not validate our official contact meshes, a learned policy, or real hardware.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import mujoco

REVISION = "b02b8b2e300733dbe76cead4f3a57425c37955fe"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True
    ).strip()
    if revision != REVISION:
        parser.error("external source revision differs from the inspected version")
    script = source / "src/sim/mujoco_pick_place.py"
    spec = importlib.util.spec_from_file_location("external_so101_pick", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    args.out.mkdir(parents=True, exist_ok=False)
    original = module.ContactAudit
    summaries = []
    for scenario in ["place", "hover"]:
        out = args.out / scenario
        out.mkdir()
        module.OUT = out
        instances = []
        with (out / "measured-contacts.trace.jsonl").open("x") as trace:

            class MeasuredAudit(original):
                def __init__(self, model, _instances=instances):
                    super().__init__(model)
                    _instances.append(self)
                    self.steps = 0
                    self.two_jaw_lifted_steps = 0
                    self.longest_two_jaw_lifted_run = 0
                    self.current_run = 0
                    self.max_object_z_m = 0.0
                    self.cube_qadr = int(model.jnt_qposadr[model.joint("cube").id])

                def observe(self, data, object_z, table_z):
                    super().observe(data, object_z, table_z)
                    touched = set()
                    for contact in data.contact:
                        if contact.geom1 == self.object_geom and contact.geom2 in self.jaws:
                            touched.add(int(contact.geom2))
                        if contact.geom2 == self.object_geom and contact.geom1 in self.jaws:
                            touched.add(int(contact.geom1))
                    both_lifted = len(touched) == 2 and object_z > table_z + 0.05
                    self.current_run = self.current_run + 1 if both_lifted else 0
                    self.two_jaw_lifted_steps += int(both_lifted)
                    self.longest_two_jaw_lifted_run = max(
                        self.longest_two_jaw_lifted_run, self.current_run
                    )
                    self.max_object_z_m = max(self.max_object_z_m, float(object_z))
                    if self.steps % 33 == 0:
                        trace.write(json.dumps({
                            "physics_step": self.steps + 1,
                            "sim_time_s": float(data.time),
                            "robot_q_rad": data.qpos[:6].tolist(),
                            "target_q_rad": data.ctrl[:6].tolist(),
                            "object_xyz_m": data.qpos[self.cube_qadr:self.cube_qadr + 3].tolist(),
                            "unique_finger_contact_count": len(touched),
                            "two_jaw_and_lifted": both_lifted,
                        }) + "\n")
                    self.steps += 1

            module.ContactAudit = MeasuredAudit
            metrics = None
            gate_error = None
            try:
                with (out / "execution.stdout.txt").open("x") as stdout:
                    with contextlib.redirect_stdout(stdout):
                        try:
                            metrics = module.run(False, scenario)
                        except SystemExit as error:
                            gate_error = {"type": "SystemExit", "code": error.code}
            finally:
                module.ContactAudit = original
        if len(instances) != 1:
            raise ValueError("expected exactly one external audit instance")
        audit = instances[0]
        summaries.append({
            "scenario": scenario,
            "upstream_task_success": metrics["success"] if metrics else None,
            "gate_error": gate_error,
            "physics_steps": audit.steps,
            "unique_two_jaw_contact_while_lifted_steps": audit.two_jaw_lifted_steps,
            "longest_two_jaw_lifted_duration_s":
                audit.longest_two_jaw_lifted_run / module.PHYSICS_HZ,
            "max_object_z_m": audit.max_object_z_m,
            "sample_stride_physics_steps": 33,
        })
    report = {
        "kind": "external_scripted_contact_check_not_learned_policy_or_tpsc",
        "repo": "https://github.com/FERBIN12/so101-manipulation-eval",
        "revision": revision,
        "mujoco_version": mujoco.__version__,
        "source_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "instrumentation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "results": summaries,
        "limitations": [
            "Two deterministic scenarios; no independent-episode success rate.",
            "External collision pads/friction and 28mm cube differ from the original TPSC scene.",
            "The teacher reads privileged object/goal positions; it is not an RGB/q/language policy.",
            "Contact counters observe state after each physics step and do not change physics.",
            "The external gate counts any jaw contact; our additional counter requires both unique jaws.",
            "No real-hardware or same-contact-model equivalence has been established.",
        ],
    }
    (args.out / "independent-contact-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
