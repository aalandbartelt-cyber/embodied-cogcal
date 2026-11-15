"""Replay original scoring definitions on controlled facts, without Isaac or VLA."""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType, ModuleType, SimpleNamespace
from typing import Any, ClassVar

import torch

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / "data/discovery/instruction-necessity-20261115"
PREFIX = "roboorchardsim__robo_orchard_sim__"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_definitions(namespace, path, names, parent=None):
    tree = ast.parse(path.read_text())
    body = tree.body if parent is None else next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == parent).body
    chosen = [n for n in body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    if {n.name for n in chosen} != set(names):
        raise ValueError(f"missing definitions in {path}")
    code = ast.Module(body=ast.parse("from __future__ import annotations").body + chosen, type_ignores=[])
    exec(compile(code, str(path), "exec"), namespace)


def original_components():
    sources = []
    for name in ["implementation-sources.json", "validator-sources.json", "evaluation-sources.json", "helper-and-evaluator-sources.json"]:
        sources.extend(json.loads((HERE / name).read_text())["sources"])
    for entry in sources:
        if "error" not in entry and digest(ROOT / entry["cache"]) != entry["sha256"]:
            raise ValueError("fixed source changed")
    module = ModuleType("_instruction_scoring_probe")
    sys.modules[module.__name__] = module
    ns = module.__dict__
    ns.update(torch=torch, inspect=inspect, Callable=Callable, Iterable=Iterable,
              Mapping=Mapping, Sequence=Sequence, dataclass=dataclass, field=field,
              MappingProxyType=MappingProxyType, Any=Any, ClassVar=ClassVar)
    ns.update(EntityId=str, SceneEntityKey=str, RelationKey=tuple,
              SceneBodyKey=type("BodyKey", (), {}), SceneJointKey=type("JointKey", (), {}))
    load_definitions(ns, CACHE / (PREFIX + "task_components__validators__physical_entity.py"), ["scene_name_of"])
    load_definitions(ns, CACHE / (PREFIX + "task_components__validators__role_scope.py"), ["_stable_unique", "RoleScope"])
    load_definitions(ns, CACHE / (PREFIX + "task_components__validators__metrics.py"),
                     ["SceneMetrics", "_copy_scene_metrics", "MetricStore", "BoundRoleMetricSelector", "AllMetricSelector", "DwellMetricSelector"])
    load_definitions(ns, CACHE / (PREFIX + "task_components__validators__base.py"), ["ValidatorOutput", "Validator"])
    load_definitions(ns, CACHE / (PREFIX + "task_components__validators__checkers.py"), ["SceneCheckerSuite", "_entity_is_reached"])

    def fact_checker(metrics):
        class FactAdapter:
            def __init__(self, **kwargs):
                self.parameters = kwargs

            def evaluate(self, env, context, scope, env_idx=0):
                return ns["SceneMetrics"](unary={m: env.facts[m] for m in metrics})

            def reset(self):
                pass
        return FactAdapter

    # These adapters inject declared physical facts; they are not physics checkers.
    ns.update(ReachChecker=fact_checker(["reached"]), ContactChecker=fact_checker(["contacted", "grasped"]),
              LiftChecker=fact_checker(["lifted"]), counterfactual_condition_for_task=lambda task: None,
              PICK_ROLE="pick", entity_position=lambda env, key, env_idx: env.positions[key])
    load_definitions(ns, CACHE / (PREFIX + "orchard_env__task_templates__pick_task.py"), ["build_validator"], parent="PickTask")
    return ns, sources


def facts_for(names, order, *, reach_only=False):
    facts = []
    for index, name in enumerate(order):
        if index:
            facts.extend([{m: {n: False for n in names} for m in ["reached", "contacted", "grasped", "lifted"]} for _ in range(2)])
        for stage, count in [(0, 15), (1, 4), (2, 4), (3, 4)]:
            for _ in range(count):
                facts.append({metric: {n: n == name and (k == 0 or (not reach_only and k <= stage)) for n in names}
                              for k, metric in enumerate(["reached", "contacted", "grasped", "lifted"])})
    return facts


def evaluate(ns, names, timeline):
    task = SimpleNamespace(params=SimpleNamespace(reach_dwell_steps=15), roles={"pick": None},
                           get_role_scene_entities=lambda role, swap: tuple(names))
    validators = {}
    for target in names:
        context = SimpleNamespace(robot=object(), scene_name_of=lambda role, env_idx=0, target=target: target)
        validators[target] = ns["build_validator"](task, context)
    histories = {name: [] for name in names}
    for fact in timeline:
        env = SimpleNamespace(facts=fact)
        for name, validator in validators.items():
            out = validator.evaluate(env)
            histories[name].append({"success": out.success, "progress": out.progress, "current": out.metrics["criteria_met_now"]})
    first = {name: next((i for i, row in enumerate(histories[name]) if row["success"]), None) for name in names}
    present = [(i, name) for name, i in first.items() if i is not None]
    earliest = min(present)[1] if present else None
    return {"first_success_steps": first, "first_completed_target": earliest,
            "latched_successes": sum(rows[-1]["success"] for rows in histories.values()),
            "terminal_current_all_successes": sum(all(rows[-1]["current"].values()) for rows in histories.values()),
            "first_completion_matches": {name: name == earliest for name in names},
            "final_progress": {name: rows[-1]["progress"] for name, rows in histories.items()},
            "per_target_step_outputs": histories}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("fresh output required")
    torch.set_num_threads(1)
    ns, sources = original_components()
    rows = []
    for n in [2, 3, 6]:
        names = [f"object_{i}" for i in range(n)]
        for order in [names, list(reversed(names))]:
            timeline = facts_for(names, order)
            row = {"n": n, "order": order, "facts_sha256": hashlib.sha256(json.dumps(timeline, sort_keys=True).encode()).hexdigest(),
                   "steps": len(timeline), "controlled_facts": timeline, "scores": evaluate(ns, names, timeline)}
            rows.append(row)
    controls = {}
    names = ["object_0", "object_1"]
    for name in names:
        controls["informed_" + name] = evaluate(ns, names, facts_for(names, [name]))
    controls["no_op"] = evaluate(ns, names, [{m: {n: False for n in names} for m in ["reached", "contacted", "grasped", "lifted"]}] * 27)
    controls["reach_only"] = evaluate(ns, names, facts_for(names, names, reach_only=True))
    for dwell in [14, 15]:
        controls[f"dwell_{dwell}"] = evaluate(ns, names, facts_for(names, [names[0]], reach_only=True)[:dwell])
    env = SimpleNamespace(positions={"left": torch.tensor([-.05, 0., 0.]), "right": torch.tensor([.05, 0., 0.])})
    proximity = {name: ns["_entity_is_reached"](env, name, threshold=.2, tcp_positions=torch.zeros((1, 3)), collision_bounds=None) for name in env.positions}
    if not all(r["scores"]["latched_successes"] == r["n"] and r["scores"]["terminal_current_all_successes"] == 1 for r in rows):
        raise ValueError("controlled witness does not show predicted scoring distinction")
    if controls["no_op"]["latched_successes"] or controls["reach_only"]["latched_successes"]:
        raise ValueError("negative control scored terminal success")
    if controls["dwell_14"]["final_progress"]["object_0"] != 0 or controls["dwell_15"]["final_progress"]["object_0"] != .25:
        raise ValueError("original dwell boundary differs")
    for name in names:
        if controls["informed_" + name]["latched_successes"] != 1:
            raise ValueError("single-target positive control failed")
    report = {"kind": "controlled_boolean_source_component_probe_not_physics_or_policy_rollout", "rows": rows,
              "controls": controls, "root_distance_overlap_control": proximity,
              "source_revision": "f2e041e5fabe354c1398ea97c934f603bb65d14d", "source_records_verified": len(sources),
              "script_sha256": digest(Path(__file__)), "plan_sha256": digest(HERE / "PLAN-component.md"),
              "limits": ["Unmodified scorer/builder definitions with declared fact adapters, not full environment.",
                         "No model, geometry/contact simulation, physical witness or benchmark score reproduction.",
                         "The paper v1 uses two stage weights; current code uses four. These results concern the fixed code.",
                         "First-completion and current-state comparisons are simple diagnostic controls, not a new method."]}
    with args.out.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"blind_cases": [{"n": r["n"], "order": r["order"], "steps": r["steps"], "latched": r["scores"]["latched_successes"], "terminal_current": r["scores"]["terminal_current_all_successes"]} for r in rows], "proximity": proximity}))


if __name__ == "__main__":
    main()
