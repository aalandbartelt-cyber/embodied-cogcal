"""Live-console support: layered caches and growth observation.

The console polls once per second while an episode is running, so every reader
that touches the disk must be either memoised on a stat key or cheap enough to
re-run.  Nothing here writes to the repository; all state is process-local and
is rebuilt after a restart.
"""
from __future__ import annotations

import hashlib
import threading
import time
from pathlib import Path

import research_runs

CATALOG_TTL_S = 30.0
PROCESS_TTL_S = 30.0
RUNS_TTL_S = 2.0
TRACE_TTL_S = 1.0
LIVE_STALE_S = research_runs.LIVE_STALE_S


class TTLCache:
    """Small thread-safe cache with per-entry TTL and LRU eviction."""

    def __init__(self, max_items):
        self._items = {}
        self._lock = threading.Lock()
        self._max = max_items

    def get_or(self, key, ttl, producer):
        now = time.monotonic()
        with self._lock:
            hit = self._items.get(key)
            if hit is not None and (ttl is None or now - hit[0] < ttl):
                hit[1] = now
                return hit[2]
        value = producer()  # produced outside the lock: no long IO under it
        with self._lock:
            self._items[key] = [now, now, value]
            if len(self._items) > self._max:
                stale = sorted(self._items.items(), key=lambda kv: kv[1][1])
                for extra, _ in stale[: len(self._items) - self._max]:
                    self._items.pop(extra, None)
            return value

    def clear(self):
        with self._lock:
            self._items.clear()


_CATALOG = TTLCache(4)
_RUNS = TTLCache(32)
_TRACE = TTLCache(256)
_PROCESSES = TTLCache(4)
_EPISODES = TTLCache(32)
_ACTIVE = TTLCache(32)

_LIVE = {}
_LIVE_LOCK = threading.Lock()


def stat_key(path):
    """Identity of one file version; any rewrite produces a new key."""
    st = Path(path).stat()
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def digest_cached(path):
    """SHA-256 of a file, recomputed only when its stat key changes.

    The verification semantics are unchanged: a modified source always yields a
    different digest, because the key embeds size, mtime and ctime.
    """
    path = Path(path)
    key = ('digest', str(path), *stat_key(path))
    return _CATALOG.get_or(key, None, lambda: hashlib.sha256(path.read_bytes()).hexdigest())


def catalog_cached(root, builder):
    key = ('catalog', str(root), _discovery_stamp(root))
    return _CATALOG.get_or(key, CATALOG_TTL_S, builder)


def _discovery_stamp(root):
    try:
        return (root / 'experiments/discovery').stat().st_mtime_ns
    except OSError:
        return None


def processes_cached(root, scanner):
    return _PROCESSES.get_or(('proc', str(root)), PROCESS_TTL_S, scanner)


def runs_cached(root, experiment):
    return _RUNS.get_or(('runs', str(root), experiment), RUNS_TTL_S,
                        lambda: research_runs.discover_runs(root, experiment))


def active_trace(root, traces):
    """Most recently modified trace in a run, or None.

    Sorted glob order is lexicographic, so it cannot identify the episode that
    is currently being written.
    """
    if not traces:
        return None
    key = ('active', str(root), len(traces), traces[-1])
    def pick():
        best = None
        best_key = None
        for relative in traces:
            try:
                st = (Path(root) / relative).stat()
            except OSError:
                continue
            candidate = (st.st_mtime_ns, st.st_size)
            if best_key is None or candidate > best_key:
                best_key = candidate
                best = relative
        return best
    return _ACTIVE.get_or(key, TRACE_TTL_S, pick)


def load_trace_cached(root, relative, mode='auto'):
    if not relative:
        return None
    path = Path(root) / relative
    try:
        key = ('trace', str(path), mode, *stat_key(path))
    except OSError:
        return None
    return _TRACE.get_or(key, TRACE_TTL_S,
                         lambda: research_runs.load_trace(root, relative, mode=mode))


def observe_growth(abspath, size, last_step, now):
    """Three-state growth flag: None on first sight, then True/False.

    A single ``stat`` cannot tell whether a file is growing, so the answer is
    derived across observations and never guessed on the first poll.
    """
    with _LIVE_LOCK:
        previous = _LIVE.get(abspath)
        if previous is None:
            _LIVE[abspath] = {'size': size, 'grew_at': now if size else 0.0,
                              'step': last_step, 'seen': now, 'rate': None}
            return None
        elapsed = max(1e-3, now - previous['seen'])
        if size > previous['size']:
            if last_step is not None and previous['step'] is not None:
                instant = (last_step - previous['step']) / elapsed
                if instant >= 0:
                    previous['rate'] = instant if previous['rate'] is None else 0.7 * previous['rate'] + 0.3 * instant
            previous['grew_at'] = now
        previous.update(size=size, step=last_step, seen=now)
        return (now - previous['grew_at']) <= LIVE_STALE_S


def growth_rate(abspath):
    with _LIVE_LOCK:
        record = _LIVE.get(abspath)
        return record['rate'] if record else None


def episodes_rows(root, run):
    """Decoded episode rows for one run, cached on the file's stat key."""
    relative = run.get('episodes')
    if not relative:
        return []
    path = Path(root) / relative
    try:
        key = ('episodes', str(path), *stat_key(path))
    except OSError:
        return []
    return _EPISODES.get_or(key, None,
                            lambda: research_runs.read_lines(path, research_runs.MAX_EPISODE_BYTES)[0])


def seed_of(relative):
    return Path(relative).name.split('.')[0] if relative else None


def physics_probe(root, run, trace_relative, trace):
    """Cheap answer to "should the console fetch /api/physics now".

    Never opens the NPZ archive: the physics snapshot is written once per
    episode, so during a run the honest answer is "still writing".
    """
    if not trace_relative:
        return {'state': 'missing', 'why': 'no_trace'}
    if trace and trace.get('live', {}).get('partial_line'):
        return {'state': 'writing', 'why': 'episode_open'}
    seed = seed_of(trace_relative)
    rows = [row for row in episodes_rows(root, run) if str(row.get('seed')) == str(seed)]
    if not rows:
        return {'state': 'writing', 'why': 'episode_row_absent'}
    row = rows[0]
    if isinstance(row.get('physics_path'), str) and isinstance(row.get('physics_sha256'), str):
        return {'state': 'ready', 'why': None}
    return {'state': 'missing', 'why': 'no_provenance'}


def live_payload(root, experiment, run_id=None, trace_relative=None, processes=None, now=None):
    """Assemble one console poll. Pure except for the caches above."""
    if now is None:
        now = time.monotonic()
    data = runs_cached(root, experiment)
    if not data or not data.get('runs'):
        return None
    runs = data['runs']
    run = next((item for item in runs if item['id'] == run_id), None)
    if run is None:
        # Fall back to the most recently updated run, not the first in walk order.
        run = max(runs, key=lambda item: item.get('updated') or '')
    pids = []
    if processes is not None:
        expected = str((Path(root) / run['id']).resolve())
        pids = [process['pid'] for process in processes if expected in process['outputs']]
    summary = dict(run, pids=pids)
    latest = active_trace(root, run['traces'])
    relative = trace_relative if trace_relative in run['traces'] else latest
    trace = load_trace_cached(root, relative) if relative else None
    growing = None
    rate = None
    eta = None
    if trace:
        growing = observe_growth(str(Path(root) / relative), trace['live']['file_bytes'],
                                 trace.get('last_step'), now)
        rate = growth_rate(str(Path(root) / relative))
        budget = run.get('conditions', {}).get('control_budget')
        step = trace.get('last_step')
        if isinstance(budget, (int, float)) and rate and step is not None and rate > 0.5:
            eta = round(max(0.0, (budget - step) / rate), 1)
    return {'experiment': experiment,
            'run': summary,
            'run_count': len(runs),
            'trace': trace,
            'physics': physics_probe(root, run, relative, trace),
            'live': {'growing': growing, 'latest_trace': latest, 'following_trace': relative,
                     'last_step': trace.get('last_step') if trace else None,
                     'rate_steps_s': round(rate, 1) if rate else None,
                     'eta_s': eta}}
