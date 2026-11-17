#!/usr/bin/env python3
"""Reconstruct the E8 write/run timeline from the upstream harness session log.

The session log is a zstd-compressed JSONL event stream produced by the
DeepSeek harness under ``~/.dsh/sessions/<workspace>/<session>/session.v4.jsonl.zstd``.
Each ``tool/call`` record carries the full arguments of ``write`` / ``edit`` /
``bash`` calls, so file contents can be replayed and hashed version by version.

This tool is **read-only**: it never touches the repository, the session file, or
any experiment record.  It answers one provenance question -- which version of
``PREREG_E8.md`` / ``rollout_e8.py`` existed when each arm ran -- by comparing
the replayed SHA-256 values with the hashes recorded in each ``contract.json``.

Usage:
    python3 e8_timeline.py --session /path/to/session.v4.jsonl.zstd \
        --out e8_timeline_events.json
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=8))
EXPERIMENT = "e8-theta-estimator-20261118"
TRACKED = ("PREREG_E8.md", "rollout_e8.py", "theta_estimator.py", "validate_estimator.py")
LIB_CANDIDATES = ("libzstd.so.1", "libzstd.dll", "/usr/lib/x86_64-linux-gnu/libzstd.so.1")


class _In(ctypes.Structure):
    _fields_ = [("src", ctypes.c_void_p), ("size", ctypes.c_size_t), ("pos", ctypes.c_size_t)]


class _Out(ctypes.Structure):
    _fields_ = [("dst", ctypes.c_void_p), ("size", ctypes.c_size_t), ("pos", ctypes.c_size_t)]


def _load_zstd():
    for name in LIB_CANDIDATES:
        try:
            return ctypes.CDLL(name)
        except OSError:
            continue
    raise RuntimeError("libzstd not found; decompress the session file first and pass the .jsonl")


def decompress_zstd(src: Path, dst: Path) -> Path:
    """Stream-decompress ``src`` into ``dst`` (frames without a size header included)."""
    lib = _load_zstd()
    lib.ZSTD_createDStream.restype = ctypes.c_void_p
    lib.ZSTD_initDStream.argtypes = [ctypes.c_void_p]
    lib.ZSTD_initDStream.restype = ctypes.c_size_t
    lib.ZSTD_decompressStream.argtypes = [ctypes.c_void_p, ctypes.POINTER(_Out), ctypes.POINTER(_In)]
    lib.ZSTD_decompressStream.restype = ctypes.c_size_t
    lib.ZSTD_freeDStream.argtypes = [ctypes.c_void_p]
    lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
    lib.ZSTD_isError.restype = ctypes.c_uint
    lib.ZSTD_getErrorName.argtypes = [ctypes.c_size_t]
    lib.ZSTD_getErrorName.restype = ctypes.c_char_p

    raw = src.read_bytes()
    buf = ctypes.create_string_buffer(raw, len(raw))
    inb = _In(ctypes.cast(buf, ctypes.c_void_p), len(raw), 0)
    chunk = 1 << 20
    out_buf = ctypes.create_string_buffer(chunk)
    outb = _Out(ctypes.cast(out_buf, ctypes.c_void_p), chunk, 0)

    stream = lib.ZSTD_createDStream()
    if not stream:
        raise RuntimeError("ZSTD_createDStream failed")
    lib.ZSTD_initDStream(stream)
    try:
        with dst.open("wb") as handle:
            while inb.pos < inb.size:
                outb.pos = 0
                remaining = lib.ZSTD_decompressStream(stream, ctypes.byref(outb), ctypes.byref(inb))
                if lib.ZSTD_isError(remaining):
                    raise RuntimeError(lib.ZSTD_getErrorName(remaining).decode())
                if outb.pos:
                    handle.write(out_buf.raw[: outb.pos])
                if remaining == 0 and inb.pos < inb.size:
                    lib.ZSTD_initDStream(stream)
    finally:
        lib.ZSTD_freeDStream(stream)
    return dst


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def repo_relative(path: str) -> str:
    """Drop the absolute prefix so the extracted evidence can be published.

    Only the displayed path is shortened; every hash is computed from the file
    content and is therefore unaffected.
    """
    marker = f"experiments/discovery/{EXPERIMENT}/"
    if marker in path:
        return marker + path.split(marker, 1)[1]
    return path.rsplit("/", 1)[-1]


def iter_records(path: Path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True, help="session.v4.jsonl.zstd or .jsonl")
    parser.add_argument("--out", default=None, help="write extracted events as JSON")
    args = parser.parse_args()

    source = Path(args.session).expanduser()
    if not source.is_file():
        print(f"session not found: {source}", file=sys.stderr)
        return 2

    tmp = None
    if source.suffix == ".zstd":
        tmp = Path(tempfile.mkstemp(suffix=".jsonl")[1])
        decompress_zstd(source, tmp)
        source_jsonl = tmp
    else:
        source_jsonl = source

    shadow: dict[str, str] = {}
    events: list[dict] = []
    try:
        for record in iter_records(source_jsonl):
            if record.get("type") != "tool/call":
                continue
            data = record.get("data") or {}
            name = data.get("name")
            raw_args = data.get("arguments") or ""
            if not isinstance(raw_args, str) or EXPERIMENT not in raw_args:
                continue
            try:
                call = json.loads(raw_args)
            except json.JSONDecodeError:
                call = {}

            event = {
                "seq": record.get("seq"),
                "time": datetime.fromtimestamp(record["time"] / 1000, TZ).isoformat(timespec="seconds"),
                "tool": name,
            }
            if name == "write":
                path = str(call.get("file_path") or call.get("path") or "")
                content = call.get("content") or ""
                shadow[path] = content
                event.update({"path": repo_relative(path), "bytes": len(content.encode()), "sha256": sha(content)})
            elif name == "edit":
                path = str(call.get("file_path") or call.get("path") or "")
                old = call.get("old_string") or ""
                new = call.get("new_string") or ""
                before = shadow.get(path)
                occurrences = before.count(old) if before is not None else None
                if before is not None and occurrences:
                    shadow[path] = before.replace(old, new, 1)
                event.update({
                    "path": repo_relative(path),
                    "occurrences": occurrences,
                    "replaced": bool(before is not None and occurrences),
                    "sha256": sha(shadow[path]) if path in shadow else None,
                    "bytes": len(shadow[path].encode()) if path in shadow else None,
                })
            elif name == "bash":
                command = str(call.get("command") or "")
                event["command"] = command[:240].replace("/home/mary", "~")
            else:
                continue

            if event.get("path") and not any(event["path"].endswith(item) for item in TRACKED):
                continue
            events.append(event)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)

    payload = {"session": source.name, "experiment": EXPERIMENT, "events": events}
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {len(events)} events -> {args.out}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
