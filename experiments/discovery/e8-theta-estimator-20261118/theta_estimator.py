"""RGB-only yaw estimator for the orange 28 mm cube.

The estimator is intentionally independent of simulator state: it renders the
same top view used by the diagnostic cameras, segments the orange cube by colour,
and fits a minimum-area rectangle to the mask.  For a square silhouette the
rectangle angle is defined modulo 90 deg; the task range is [-45, +45] deg, so
the acute solution is mapped back into that range.

No object qpos, segmentation buffer, success label or policy output is used.
The 512 px render is an estimator-only sensor; the frozen policy still sees its
own 2 x 128 x 128 RGB stream.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import ndimage

MIN_AREA = 200
MAX_AREA = 5000
ANGLE_STEP_DEG = 0.1


@dataclass(frozen=True)
class Estimate:
    yaw_deg: float
    rectangle_angle_deg: float
    area_px: int
    bbox: tuple[int, int, int, int]


def _mask(rgb: np.ndarray) -> np.ndarray:
    r = rgb[..., 0].astype(np.int32)
    g = rgb[..., 1].astype(np.int32)
    b = rgb[..., 2].astype(np.int32)
    return (r > 200) & (g > 150) & (b < 150) & ((r - b) > 60)


def _largest_cube_component(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray] | None:
    labels, count = ndimage.label(mask)
    best: tuple[int, np.ndarray, np.ndarray] | None = None
    for index in range(1, count + 1):
        ys, xs = np.nonzero(labels == index)
        area = int(xs.size)
        if MIN_AREA <= area <= MAX_AREA and (best is None or area > best[0]):
            best = (area, xs, ys)
    if best is None:
        return None
    _, xs, ys = best
    return xs, ys


def _min_area_angle(xs: np.ndarray, ys: np.ndarray) -> float:
    """Angle in [0, 90) that minimizes the axis-aligned bounding area."""
    x = xs.astype(np.float64)
    y = ys.astype(np.float64)
    best_area = math.inf
    best_angle = 0.0
    for angle in np.arange(0.0, 90.0, ANGLE_STEP_DEG):
        t = math.radians(float(angle))
        c, s = math.cos(t), math.sin(t)
        u = x * c + y * s
        v = -x * s + y * c
        area = float((u.max() - u.min()) * (v.max() - v.min()))
        if area < best_area:
            best_area = area
            best_angle = float(angle)
    return best_angle


def estimate_yaw(rgb: np.ndarray) -> Estimate:
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"expected HxWx3 RGB, got {rgb.shape}")
    mask = _mask(rgb)
    component = _largest_cube_component(mask)
    if component is None:
        raise ValueError("orange cube component not found")
    xs, ys = component
    angle = _min_area_angle(xs, ys)
    yaw = (90.0 - angle) % 90.0
    if yaw > 45.0:
        yaw -= 90.0
    return Estimate(
        yaw_deg=float(yaw),
        rectangle_angle_deg=float(angle),
        area_px=int(xs.size),
        bbox=(int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())),
    )


def estimate_yaw_deg(rgb: np.ndarray) -> float:
    return estimate_yaw(rgb).yaw_deg
