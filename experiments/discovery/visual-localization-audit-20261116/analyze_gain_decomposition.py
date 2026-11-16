#!/usr/bin/env python3
"""Decompose the recorded gain into magnitude ratio and direction error.

Reads `localization-landmarks.json` (frozen record, 20 source-shift pairs) and
reports, for the planned first-query target and for the executed pinch site:

  * |response| / |object shift|  -- how far the response travels
  * angle between response and object shift  -- how well it points
  * the projection gain g that the report quotes

Why this exists: g alone cannot tell "moved a little in the right direction"
from "moved the right distance in the wrong direction". The executed site moves
about the full shift length but at a large angle, while the planned target
underruns in length and points fairly well. That difference decides whether a
compensator should be a scalar gain or a 2x2 map, so it is worth reproducing in
one command instead of re-deriving it in a chat.

No MuJoCo, no policy, no new episodes: pure arithmetic over the frozen record.
Usage: python3 analyze_gain_decomposition.py [--json path]
"""

import argparse
import json
import math
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOUNDARY = "0.2"  # grip-command threshold entry used by the report's main row


def _ratio_and_angle(response, shift):
    sn = math.hypot(*shift)
    rn = math.hypot(*response)
    if sn < 1e-9 or rn < 1e-9:
        return None
    cos = (response[0] * shift[0] + response[1] * shift[1]) / (rn * sn)
    return rn / sn, math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def describe(rows, key):
    ratios, angles, gains = [], [], []
    for row in rows:
        cell = row[key].get(BOUNDARY) or row[key][BOUNDARY]
        pair = _ratio_and_angle(cell["response_xy_m"], row["delta_object_xy_m"])
        if pair is None:
            continue
        ratios.append(pair[0])
        angles.append(pair[1])
        gains.append(cell["parallel_gain"])
    if not ratios:
        return None
    return {
        "n": len(ratios),
        "magnitude_ratio_median": st.median(ratios),
        "magnitude_ratio_range": (min(ratios), max(ratios)),
        "angle_deg_median": st.median(angles),
        "angle_deg_range": (min(angles), max(angles)),
        "parallel_gain_median": st.median(gains),
        "frac_magnitude_over_0.8": sum(1 for r in ratios if r > 0.8) / len(ratios),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(HERE / "localization-landmarks.json"))
    args = ap.parse_args()
    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    rows = data["rows"]

    print(f"record: {args.json}  pairs={len(rows)}  boundary={BOUNDARY}s")
    for key, label in (
        ("first_query_planned", "planned first-query target"),
        ("executed", "executed pinch site"),
    ):
        d = describe(rows, key)
        if d is None:
            print(f"{label}: no usable rows")
            continue
        lo, hi = d["magnitude_ratio_range"]
        alo, ahi = d["angle_deg_range"]
        print(f"\n{label} (n={d['n']})")
        print(f"  |response|/|shift|  median {d['magnitude_ratio_median']:.2f}  [{lo:.2f}, {hi:.2f}]")
        print(f"  angle to shift       median {d['angle_deg_median']:.0f} deg  [{alo:.0f}, {ahi:.0f}]")
        print(f"  projection gain g    median {d['parallel_gain_median']:.3f}")
        print(f"  share with |response| > 0.8|shift|: {d['frac_magnitude_over_0.8']:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
