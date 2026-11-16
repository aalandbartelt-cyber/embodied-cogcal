"""Build the E4 geom-orientation variants from the pristine variant-source tree.

E4 decouples "what the policy sees" from "what the fingers touch" at one fixed
yaw (15 deg). The cube body carries two coincident boxes in variant-source:
  cube_look    group 0 (rendered), mass 0, contype 0  -> appearance only
  cube_visual  group 3 (hidden; mjv_defaultOption hides groups 3-5),
               mass 0.020, contype 2                 -> collision only

A quat on a single geom cannot be changed at runtime in MuJoCo 4.0.1 (a
compiled-in geom frame is not re-read by mj_forward; verified against a minimal
model), so each condition gets its own compiled XML: only the quat attribute of
cube_look differs from the pristine file. Real rotation of the physical object is
done the way E2 did it, by writing the free-joint quaternion at reset, so the
solver state stays on E2's numerical path:

  condition   tree      body yaw at reset   cube_look geom quat
  deg0        deg0       0 deg              0 deg
  visual      visual     0 deg             +15 deg   (image rotated only)
  collision   collision +15 deg            -15 deg   (object rotated, image cancels
                                                      back to axis-aligned)
  both        deg0      +15 deg              0 deg    (E2's theta=15, image+contact)

Each tree is a hardlink copy of variant-source, so nothing is duplicated on disk
and the pristine tree is never written.

Written: variants.json (per-condition xml path, sha256, body yaw, geom yaw,
quat, changed lines) plus the four-condition rollout map.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRISTINE = HERE / "variant-source"
REL_XML = Path("assets") / "so101" / "sim_replay.xml"
YAW_DEG = 15.0
# tree -> geom quat written into the compiled XML (deg about z)
TREE_GEOM_YAW = {
    "deg0": {},
    "visual": {"cube_look": +YAW_DEG},
    "collision": {"cube_look": -YAW_DEG},
}
# rollout condition -> (tree, body yaw at reset in deg)
CONDITIONS = {
    "deg0": ("deg0", 0.0),
    "visual": ("visual", 0.0),
    "collision": ("collision", +YAW_DEG),
    "both": ("deg0", +YAW_DEG),
}


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def quat_z(deg: float) -> tuple:
    half = math.radians(deg) / 2.0
    return (math.cos(half), 0.0, 0.0, math.sin(half))


def patched_xml(text: str, geoms: dict[str, float]) -> str:
    for name, deg in geoms.items():
        needle = f'name="{name}" type="box"'
        if text.count(needle) != 1:
            raise ValueError(f"expected exactly one {needle!r}")
        text = text.replace(
            needle, needle + ' quat="' + " ".join(f"{v:.9f}" for v in quat_z(deg)) + '"')
    return text


def main() -> int:
    base_xml = PRISTINE / REL_XML
    base_text = base_xml.read_text()
    record = {"yaw_deg": YAW_DEG, "pristine": str(PRISTINE),
              "pristine_xml_sha256": sha(base_xml), "conditions": {}, "trees": {}}
    for tree, geom_yaws in TREE_GEOM_YAW.items():
        path = HERE / tree
        if path.exists():
            shutil.rmtree(path)
        shutil.copytree(PRISTINE, path, copy_function=os.link)
        xml = path / REL_XML
        xml.unlink()  # break the hardlink before writing
        text = patched_xml(base_text, geom_yaws)
        xml.write_text(text)
        record["trees"][tree] = {
            "source": str(path), "xml": str(xml), "geom_yaw_deg": geom_yaws,
            "xml_sha256": sha(xml),
            "changed_lines": [ln for ln in text.splitlines() if "quat=" in ln and "cube_look" in ln],
        }
    for condition, (tree, body_yaw) in CONDITIONS.items():
        entry = dict(record["trees"][tree])
        entry["tree"] = tree
        entry["body_yaw_deg"] = body_yaw
        entry["image_yaw_deg"] = body_yaw + entry["geom_yaw_deg"].get("cube_look", 0.0)
        record["conditions"][condition] = entry
    (HERE / "variants.json").write_text(json.dumps(record, indent=2) + "\n")
    for condition, entry in record["conditions"].items():
        print(f"{condition:9s} tree={entry['tree']:9s} body={entry['body_yaw_deg']:5.1f} "
              f"look={entry['geom_yaw_deg'].get('cube_look', 0.0):5.1f} "
              f"image={entry['image_yaw_deg']:5.1f} xml={entry['xml_sha256'][:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
