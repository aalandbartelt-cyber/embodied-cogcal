"""Read pinned source syntax; never import or execute either simulator or policy."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "data/discovery/instruction-necessity-20261115"
NEW = ROOT / "data/discovery/instruction-necessity-followup-20261115"


def function(path: Path, owner: str | None, name: str) -> ast.FunctionDef:
    tree = ast.parse(path.read_text())
    nodes = tree.body
    if owner is not None:
        nodes = next(
            x for x in nodes if isinstance(x, ast.ClassDef) and x.name == owner
        ).body
    return next(
        x for x in nodes if isinstance(x, ast.FunctionDef) and x.name == name
    )


def defaults(path: Path, owner: str, name: str) -> object:
    tree = ast.parse(path.read_text())
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == owner)
    node = next(
        x for x in cls.body
        if isinstance(x, ast.AnnAssign)
        and isinstance(x.target, ast.Name) and x.target.id == name
    )
    return ast.literal_eval(node.value)


def audit() -> dict:
    env = NEW / "robo__robo_orchard_sim__ext__envs__manager_based_env.py"
    evaluator = OLD / "roboorchardsim__robo_orchard_sim__pipeline__evaluator__evaluator.py"
    script = OLD / "roboorchardsim__examples__manipulation-app__scripts__eval_policy.py"
    canonical = NEW / "robo__robo_orchard_sim__policy__canonicalizer.py"
    pose = NEW / "robo__robo_orchard_sim__ext__envs__managers__events__pose_reset.py"
    pick = OLD / "roboorchardsim__robo_orchard_sim__orchard_env__task_templates__pick_task.py"
    config = OLD / "roboorchardsim__robo_orchard_sim__benchmark__manipulation__semantic_pick__configs__pick_category.yaml"
    sources = [env, evaluator, script, canonical, pose, pick, config]
    returns = {}
    for method in ("step", "reset"):
        fn = function(env, "IsaacManagerBasedEnv", method)
        calls = [
            x.value for x in ast.walk(fn) if isinstance(x, ast.Return)
            and isinstance(x.value, ast.Call)
            and isinstance(x.value.func, ast.Name)
            and x.value.func.id == "EnvStepReturn"
        ]
        assert len(calls) == 1
        fields = {k.arg: k.value for k in calls[0].keywords}
        assert all(
            isinstance(fields[k], ast.Constant) and fields[k].value is None
            for k in ("terminated", "truncated")
        )
        returns[method] = {
            "lines": [fn.lineno, fn.end_lineno],
            "terminated": None, "truncated": None,
        }
    fn = function(evaluator, "Evaluator", "_extract_done_flag")
    first_if = next(x for x in fn.body if isinstance(x, ast.If))
    assert ast.unparse(first_if.test) == "done is None"
    assert isinstance(first_if.body[0], ast.Return)
    assert ast.literal_eval(first_if.body[0].value) is False

    fn = function(canonical, None, "canonicalize_observations")
    call = next(x.value for x in fn.body if isinstance(x, ast.Return))
    canonical_fields = [k.arg for k in call.keywords]
    assert canonical_fields == ["instruction", "cameras", "manipulators", "action_layout"]
    assert not any(
        isinstance(x, ast.Constant) and x.value == "/object" for x in ast.walk(fn)
    )

    fn = function(pose, "PoseResetTerm", "__call__")
    role_reads = [
        x.attr for x in ast.walk(fn)
        if isinstance(x, ast.Attribute) and x.attr == "role_bindings"
    ]
    assert role_reads == []
    pick_fn = function(pick, "PickTask", "get_event_cfg")
    assert "self.assets.all_scene_names()" in ast.unparse(pick_fn)
    fps = int(next(
        x.split(":", 1)[1] for x in config.read_text().splitlines()
        if x.strip().startswith("step_fps:")
    ))
    max_steps = defaults(evaluator, "EvaluatorCfg", "max_steps")
    script_steps = defaults(script, "TaskCfg", "max_steps")
    assert max_steps == script_steps == 1000
    assert fps == 30
    return {
        "claim": "static source observations only; no Isaac run or learned-policy inference",
        "revision": "f2e041e5fabe354c1398ea97c934f603bb65d14d",
        "source_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources
        },
        "environment_return_fields": returns,
        "evaluator_none_done_flag": False,
        "canonical_policy_fields": canonical_fields,
        "canonicalizer_reads_raw_object_group": False,
        "pick_pose_reset_uses_all_asset_names": True,
        "pose_reset_call_reads_role_bindings": False,
        "config_defaults": {
            "evaluator_max_steps": max_steps,
            "script_max_steps": script_steps,
            "selected_pick_step_fps": fps,
            "default_control_budget_seconds": max_steps / fps,
            "scope": "defaults, not the paper experiment settings",
        },
        "limits": [
            "Does not execute scene sampling, Isaac physics, sensors or controller.",
            "Does not prove absence of arbitrary event exceptions or every config override.",
            "No cross-engine timing or benchmark-wide success claim.",
            "No novelty certification or evidence of an algorithmic increment.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    result = audit()
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["config_defaults"]))
