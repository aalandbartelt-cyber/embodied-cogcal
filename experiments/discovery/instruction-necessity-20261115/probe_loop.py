"""Unchanged episode loop on identical target-blind controlled sequences."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace

from probe_components import (
    CACHE,
    PREFIX,
    evaluate,
    facts_for,
    load_definitions,
    original_components,
)

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    ns, _ = original_components()
    source = CACHE / (PREFIX + "pipeline__evaluator__evaluator.py")
    records = json.loads((HERE / "helper-and-evaluator-sources.json").read_text())["sources"]
    if not any(Path(e["cache"]).name == source.name and e["sha256"] == digest(source) for e in records):
        raise ValueError("loop source not bound")
    ns["UnifiedJointCommand"] = type("UnifiedJointCommand", (), {})
    load_definitions(ns, source, ["_step_episode"], parent="Evaluator")
    names = ["object_0", "object_1"]
    rows = []
    for order in [names, list(reversed(names))]:
        facts = facts_for(names, order)
        for fixed in [False, True]:
            for target in names:
                task = SimpleNamespace(params=SimpleNamespace(reach_dwell_steps=15), roles={"pick": None},
                                       get_role_scene_entities=lambda role, swap: tuple(names))
                context = SimpleNamespace(robot=object(), scene_name_of=lambda role, env_idx=0, target=target: target)
                validator = ns["build_validator"](task, context)
                validator.fixed_horizon = fixed
                env = SimpleNamespace()
                # Only force a fixed horizon; keep the original final cumulative score.
                if fixed:
                    validator.finalize = lambda validator=validator, env=env: validator.evaluate(env)
                sent = []

                def policy(ignored_observation, sent=sent):
                    index = len(sent)
                    sent.append(index)
                    return index

                def step(index, env=env, facts=facts):
                    env.facts = facts[index]
                    return SimpleNamespace(observations={"index": index + 1}, terminated=False, truncated=False)

                env.step = step
                evaluator = SimpleNamespace(cfg=SimpleNamespace(max_steps=len(facts)), _task=None,
                    _resolve_policy_tag=lambda policy: "controlled-component-probe",
                    _build_policy_input=lambda **kwargs: kwargs["observations"],
                    _extract_terminated=lambda out: out.terminated,
                    _extract_truncated=lambda out: out.truncated)
                with contextlib.redirect_stdout(io.StringIO()) as captured:
                    steps, reason, output = ns["_step_episode"](evaluator, env, policy, {"index": 0}, validator, target)
                if not output.success or sent != list(range(len(sent))):
                    raise ValueError("controlled loop did not reach predicted success")
                rows.append({"order": order, "target_binding": target, "fixed_horizon_only": fixed,
                             "steps": steps, "stop_reason": reason, "success": output.success,
                             "progress": output.progress, "executed_index_sequence": sent,
                             "source_loop_stdout": captured.getvalue()})
    first_rule = evaluate(ns, names, facts_for(names, names))["first_completion_matches"]
    report = {"kind": "original_loop_with_controlled_fact_adapter_not_isaac_or_vla",
              "rows": rows, "simple_first_completion_control": first_rule,
              "loop_source_sha256": digest(source), "component_script_sha256": digest(HERE / "probe_components.py"),
              "script_sha256": digest(Path(__file__)), "plan_sha256": digest(HERE / "PLAN-loop.md"),
              "limits": ["Fixed-horizon control deliberately retains cumulative scoring, not a complete protocol repair.",
                         "No real action input or observation pipeline or external environment termination reproduced."]}
    with args.out.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"rows": [{k: r[k] for k in ["order", "target_binding", "fixed_horizon_only", "steps", "stop_reason", "success"]} for r in rows]}))


if __name__ == "__main__":
    main()
