"""Extract a preregistered descriptive review sheet from pinned public robot video."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DATA = ROOT / "data/discovery/deployment-failures-20261115"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(out: Path) -> dict:
    out = out.resolve()
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    selection_path = HERE / "real-rollout-selection.json"
    selection = json.loads(selection_path.read_text())
    source = DATA / "armnet-top-file014.mp4"
    expected = "13b2e1bd78f4618f8ff285e8cb806fd4219c5a2352e63ef4f04ff8b85baa19c3"
    assert sha(source) == expected
    targets = {}
    samples = []
    for episode in selection["episodes"]:
        assert episode["videos/observation.images.top/file_index"] == 14
        assert episode["videos/observation.images.top/chunk_index"] == 0
        start = episode["videos/observation.images.top/from_timestamp"]
        for tag, relative in [(str(t), float(t)) for t in (0, 1, 3, 6, 9)] + [
            ("last", (episode["length"] - 1) / 20)
        ]:
            tick = round((start + relative) * 20)
            assert abs(tick / 20 - start - relative) < 1e-6
            sample = {
                "episode_index": episode["episode_index"], "outcome_label": episode["success_class"],
                "tag": tag, "relative_seconds": relative, "video_seconds": tick / 20,
                "source_tick": tick,
            }
            samples.append(sample)
            targets.setdefault(tick, []).append(sample)
    extracted = set()
    with av.open(str(source)) as container:
        stream = container.streams.video[0]
        assert float(stream.average_rate) == 20
        stream.thread_type = "AUTO"
        stream.codec_context.thread_count = 4
        for frame in container.decode(video=0):
            seconds = float(frame.pts * frame.time_base)
            tick = round(seconds * 20)
            assert abs(tick / 20 - seconds) < 1e-6
            if tick in targets:
                rgb = frame.to_image()
                for sample in targets[tick]:
                    path = out / f"ep{sample['episode_index']}-{sample['tag']}.png"
                    rgb.save(path)
                    sample.update({
                        "file": str(path.relative_to(ROOT)), "sha256": sha(path),
                        "pts": frame.pts, "time_base": str(frame.time_base),
                    })
                extracted.add(tick)
            if tick >= max(targets):
                break
    assert extracted == set(targets)
    pages = []
    font = ImageFont.load_default(size=15)
    for page_index in range(3):
        episodes = selection["episodes"][page_index * 4:(page_index + 1) * 4]
        sheet = Image.new("RGB", (1536, 4 * 190 + 32), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((8, 6), "Armnet SO-101 / fixed samples; labels by dataset operator; last frame is outcome-trimmed", fill="black", font=font)
        for row, episode in enumerate(episodes):
            entries = [x for x in samples if x["episode_index"] == episode["episode_index"]]
            assert len(entries) == 6
            for col, entry in enumerate(entries):
                with Image.open(ROOT / entry["file"]) as rgb:
                    thumb = rgb.resize((256, 144), Image.Resampling.LANCZOS)
                x, y = col * 256, 32 + row * 190
                sheet.paste(thumb, (x, y))
                draw.text((x + 3, y + 146), f"ep{entry['episode_index']} t={entry['relative_seconds']:.2f}s", fill="black", font=font)
                draw.text((x + 3, y + 165), entry["outcome_label"] + (" / LAST" if entry["tag"] == "last" else ""), fill="black", font=font)
        path = out / f"contact-sheet-{page_index + 1}.png"
        sheet.save(path)
        pages.append({"file": str(path.relative_to(ROOT)), "sha256": sha(path)})
    result = {
        "source_sha256": expected, "selection_sha256": sha(selection_path),
        "script_sha256": sha(Path(__file__).resolve()), "av_version": av.__version__,
        "samples": samples, "pages": pages,
        "limits": [
            "Human-readable descriptive review, not an independent outcome relabel or measured force/pose.",
            "Last frames reflect author trimming and are not length-matched comparisons.",
            "One top view cannot reveal every grasp, occlusion, contact or insertion condition.",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = extract(args.out)
    print(json.dumps({"samples": len(result["samples"]), "pages": result["pages"]}))
