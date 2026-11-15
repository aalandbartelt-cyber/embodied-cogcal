"""Render an explicitly analytic VFD mechanism figure, not robot results."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/discovery/vfd-quadrature-20261115/analytic-results.json"
OUT = ROOT / ".research/figures/vfd_grid_analytic_20261115"
COLORS = ["#2563EB", "#7C3AED", "#525252", "#16A34A"]


def main():
    for suffix in ["svg", "pdf", "png"]:
        if OUT.with_suffix(f".{suffix}").exists():
            raise ValueError("fresh figure paths required")
    data = json.loads(SOURCE.read_text())
    rows = data["rows"]
    pair = data["summary"]["source_default_11"]["mi_ranking"]["first_inversion_row_indices"]
    if pair is None:
        raise ValueError("no inversion example")
    selected = [rows[i] for i in pair]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.2,
                         "axes.labelsize": 7.2, "axes.titlesize": 7.8,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "pdf.fonttype": 42,
                         "xtick.labelsize": 6.8, "ytick.labelsize": 6.8,
                         "legend.fontsize": 6.3, "legend.frameon": False})
    fig, axes = plt.subplots(2, 2, figsize=(17.8 / 2.54, 10.5 / 2.54), layout="constrained")
    a, b, c, d = axes.ravel()
    remaining = np.geomspace(1e-4, .9999, 2000)
    time = 1 - remaining
    for row, color, style in zip(selected, COLORS, ["-", "--"], strict=False):
        sigma = row["sigma"]
        variance = remaining ** 2 + sigma ** 2 * time ** 2
        density = 2 * sigma ** 2 * time * remaining / variance ** 2
        a.loglog(remaining, density, color=color, linestyle=style,
                 label=rf"$\sigma={sigma:g}$", linewidth=1.4)
    preset = np.r_[np.arange(10) / 10, .95]
    a.plot(1 - preset, np.full(len(preset), .025), "|", color="#525252",
           transform=a.get_xaxis_transform(), markersize=5)
    a.axvspan(1e-4, .05, color="#EFF6FF", zorder=0)
    a.axvline(.05, color="#525252", linewidth=.7, linestyle=":")
    a.text(.004, .94, "No default nodes", transform=a.transAxes, va="top", fontsize=6.5)
    a.set(xlabel="Remaining flow time 1 − s", ylabel="Normalized KL integrand",
          xlim=(1e-4, 1), ylim=(1e-4, 1e2), title="a  Endpoint concentration")
    a.legend(loc="upper right")
    sigmas = sorted({r["sigma"] for r in rows})
    configs = [("paper_left_10", "Uniform left, 10", COLORS[0], "-", "o"),
               ("source_default_11", "Source default, 11", COLORS[1], "--", "s"),
               ("gauss_legendre_10", "Gauss–Legendre, 10", COLORS[3], ":", "^")]
    for key, label, color, style, marker in configs:
        ratio = [np.median([r["scores"][key] / r["exact_pairwise_kl_nats"] for r in rows
                            if r["sigma"] == sigma and r["mean_separation_delta"] > 0]) for sigma in sigmas]
        b.semilogx(sigmas, ratio, marker=marker, color=color, linestyle=style,
                   label=label, markersize=3, linewidth=1.2)
    b.axhline(1, color="#525252", linewidth=.7)
    b.set(xlabel="Within-member standard deviation σ", ylabel="Estimated / exact pairwise KL",
          ylim=(0, 1.45), title="b  Width-dependent distortion")
    b.legend(loc="lower right")
    counts = [5, 10, 20, 50, 100, 500]
    for prefix, label, color, style, marker in [
        ("paper_left", "Uniform left", COLORS[0], "-", "o"),
        ("midpoint", "Midpoint", COLORS[2], "--", "s"),
        ("gauss_legendre", "Gauss–Legendre", COLORS[3], ":", "^")]:
        flips = [data["summary"][f"{prefix}_{n}"]["mi_ranking"]["strict_inversions"] for n in counts]
        c.semilogx(counts, flips, color=color, linestyle=style, marker=marker,
                   label=label, markersize=3, linewidth=1.2)
    c.set(xlabel="Integrand evaluations N", ylabel="MI-order inversions / 1,062 pairs",
          ylim=(-1.5, 60), title="c  All prescribed conditions")
    c.legend(loc="upper right")
    for label, row, color, marker in zip(["A", "B"], selected, COLORS, ["o", "s"], strict=False):
        d.semilogy([0, 1], [row["exact_pairwise_kl_nats"], row["source_function_score"]],
                   color=color, marker=marker, linestyle="-" if label == "A" else "--",
                   markersize=4, linewidth=1.3,
                   label=f"{label}: σ={row['sigma']:g}, δ={row['mean_separation_delta']:g}")
    d.set(xticks=[0, 1], xticklabels=["Exact KL", "Default-grid estimate"],
          xlim=(-.12, 1.12), ylabel="Pairwise KL / estimate (nats)",
          title="d  First default-grid rank reversal")
    d.legend(loc="upper right")
    for ax in axes.ravel():
        ax.tick_params(length=2.5, width=.7)
        ax.grid(axis="y", alpha=.13, linewidth=.5)
    for suffix in ["svg", "pdf", "png"]:
        fig.savefig(OUT.with_suffix(f".{suffix}"), dpi=250)
    svg_path = OUT.with_suffix(".svg")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n")
    plt.close(fig)
    manifest = {"figures": [{
        "figure_id": OUT.name, "panels": ["a", "b", "c", "d"],
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "script": str(Path(__file__).relative_to(ROOT)),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outputs": [str(OUT.with_suffix(f".{suffix}").relative_to(ROOT)) for suffix in ["svg", "pdf", "png"]],
        "example_row_indices": pair, "selection": "first saved lexicographic inversion, post-result illustration",
        "notes": "Deterministic analytic probe. No robot, learned-policy risk or time advantage claimed."}]}
    path = ROOT / ".research/figures/source_data_manifest.json"
    with path.open("x") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"outputs": manifest["figures"][0]["outputs"], "example_rows": pair}))


if __name__ == "__main__":
    main()
