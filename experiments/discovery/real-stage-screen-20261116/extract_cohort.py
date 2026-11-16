"""Fixed 3s multiview grid of all 12 preselected episodes, not causal labels."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "deployment-failures-20261115"
DATA = ROOT / "data/discovery/deployment-failures-20261115"
CAMERAS = ["front", "top", "wrist"]
SOURCES = {
    "front": (11, "9ded72fecd2c418a75b82685450c07a8f0c9d906392a7819b56f62df342b1e31"),
    "top": (14, "13b2e1bd78f4618f8ff285e8cb806fd4219c5a2352e63ef4f04ff8b85baa19c3"),
    "wrist": (12, "30e4863acbee60914f04b23270600389a90d7c07fd6b2f0b0909289bfe588739"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        parser.error("fresh output required")
    out.mkdir(parents=True)
    selection_path = PREVIOUS / "real-rollout-selection.json"
    selection = json.loads(selection_path.read_text())
    episodes = selection["episodes"]
    if [e["episode_index"] for e in episodes] != list(range(225, 237)):
        raise ValueError("frozen selection differs")
    groups, sources, samples = [], [], []
    for episode in episodes:
        ticks = list(range(0, episode["length"], 60))
        if ticks[-1] != episode["length"] - 1:
            ticks.append(episode["length"] - 1)
        for tick in ticks:
            groups.append({"episode_index": episode["episode_index"],
                           "outcome_label": episode["success_class"],
                           "relative_tick": tick, "relative_seconds": tick / 20,
                           "author_trimmed_last": tick == episode["length"] - 1,
                           "views": {}})
    for camera in CAMERAS:
        index, expected = SOURCES[camera]
        source = DATA / f"armnet-{camera}-file{index:03d}.mp4"
        if sha(source) != expected:
            raise ValueError("unverified video")
        targets = {}
        for episode in episodes:
            stem = f"videos/observation.images.{camera}"
            if episode[stem + "/file_index"] != index or episode[stem + "/chunk_index"] != 0:
                raise ValueError("unexpected video range")
            start = episode[stem + "/from_timestamp"]
            for group in [x for x in groups if x["episode_index"] == episode["episode_index"]]:
                seconds = start + group["relative_seconds"]
                tick = round(seconds * 20)
                if abs(seconds - tick / 20) > 1e-6:
                    raise ValueError("metadata not nominal 20Hz aligned")
                targets[tick] = group
        found = set()
        with av.open(str(source)) as container:
            stream = container.streams.video[0]
            if float(stream.average_rate) != 20:
                raise ValueError("unexpected nominal video fps")
            sources.append({"camera": camera, "cache_path": str(source.relative_to(ROOT)),
                            "sha256": expected, "bytes": source.stat().st_size,
                            "width": stream.width, "height": stream.height,
                            "time_base": str(stream.time_base), "average_rate": str(stream.average_rate)})
            stream.thread_type = "AUTO"
            stream.codec_context.thread_count = 4
            for frame in container.decode(video=0):
                seconds = float(frame.pts * frame.time_base)
                tick = round(seconds * 20)
                if abs(tick / 20 - seconds) > 1e-6:
                    raise ValueError("frame PTS not nominal aligned")
                if tick in targets:
                    group = targets[tick]
                    path = out / f"ep{group['episode_index']}-tick{group['relative_tick']:04d}-{camera}.png"
                    frame.to_image().save(path)
                    row = {"camera": camera, "file": str(path.relative_to(ROOT)),
                           "sha256": sha(path), "pts": frame.pts, "time_base": str(frame.time_base),
                           "video_seconds": seconds, "episode_index": group["episode_index"],
                           "relative_seconds": group["relative_seconds"]}
                    samples.append(row)
                    group["views"][camera] = row
                    found.add(tick)
                if tick >= max(targets):
                    break
        if found != set(targets):
            raise ValueError("missing grid frames")
    pages = []
    font = ImageFont.load_default(size=14)
    for page_start in range(0, len(groups), 16):
        subset = groups[page_start:page_start + 16]
        sheet = Image.new("RGB", (1536, 8 * 174 + 32), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((7, 7), "Armnet pinned SO101 / fixed 3s cohort grid / metadata time, not verified exposure sync / Apache-2.0", fill="black", font=font)
        for group_index, group in enumerate(subset):
            for camera_index, camera in enumerate(CAMERAS):
                entry = group["views"][camera]
                with Image.open(ROOT / entry["file"]) as img:
                    thumbnail = img.resize((256, 144), Image.Resampling.LANCZOS)
                x, y = ((group_index % 2) * 3 + camera_index) * 256, 32 + (group_index // 2) * 174
                sheet.paste(thumbnail, (x, y))
                last = " LAST" if group["author_trimmed_last"] else ""
                draw.text((x + 2, y + 147), f"ep{group['episode_index']} {group['relative_seconds']:.2f}s {camera}{last}", fill="black", font=font)
        path = out / f"process-sheet-{len(pages) + 1}.png"
        sheet.save(path)
        pages.append({"file": str(path.relative_to(ROOT)), "sha256": sha(path)})
    report = {"source_code_sha256": sha(Path(__file__)), "selection_sha256": sha(selection_path),
              "plan_sha256": sha(HERE / "PLAN.md"), "sources": sources,
              "av_version": av.__version__, "samples": samples, "pages": pages,
              "grid_times_per_episode": {str(e["episode_index"]): sum(g["episode_index"] == e["episode_index"] for g in groups) for e in episodes},
              "limits": ["3s grid is not every-frame continuous playback.",
                         "Camera correspondence is metadata nominal time, not verified exposure/action synchronization.",
                         "All 12 previously stratified episodes; unmatched initial states, no causal or prevalence inference."]}
    (out / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"frames": len(samples), "pages": len(pages), "grid_times_per_episode": report["grid_times_per_episode"]}))


if __name__ == "__main__":
    main()
