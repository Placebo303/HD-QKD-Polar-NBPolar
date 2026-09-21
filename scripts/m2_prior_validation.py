#!/usr/bin/env python3
"""M2 prior validation runner — Stage-1 interface for NBPOLAR-M2-PRIOR-REALDATA-VALIDATION.

Stage-1 wiring is REAL (``--freeze-config`` with all 19 keys required,
the ``--authorized`` hard gate, flag/freeze cross-check, the frozen
319/6492 K pin, and the ``workspace/``-confined out-root guard). The G1
held-out NLL body (``--stage-g1-nll``) is implemented decoder-free per
``NBPOLAR-M2-PRIOR-G1-REALDATA-NLL`` / ``g1_freeze.md`` (Phase-0 code;
Phase-A ``--closure-only`` framing pass + Phase-B full G1 science). The
G2 stage body belongs to a later freeze: after all validation passes it
exits 3 ``STAGE_BODY_PENDING_FREEZE`` with zero data contact (nothing
read beyond the freeze-config file, nothing created). No decoder runs
under this packet.
Science constants are window-keyed contracts: the G1 legacy contract at
w=500 is preserved verbatim, and the G1R2 successor at w=200 (delta
item 8, NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR) reuses the same mechanics.
Selection uses the freeze ``pairing_window_primary`` only, never data.

Wiring verifiable via ``--selfcheck`` (pure logic; touches no data).

Importing this module reads no files, constructs no model, and opens no
data. All non-stdlib/non-numpy imports (YAML, TimeTagger shim targets,
``src.qkd_io``, frozen prior leaves) are deferred inside functions.

Frozen prior leaves (``formal_ir/prior_m2.py``,
``formal_ir/nbpolar/prior.py``) are loaded read-only by file location
inside functions: the mandated execution venv has no pandas, and the
``formal_ir`` package ``__init__`` requires it, so the package import
path is unusable there. Both leaves are NumPy+stdlib-only with no
relative imports (enforced by a runtime AST check before loading); they
are NEVER modified.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import NoReturn

import numpy as np

# Repo-root insertion: `python scripts/m2_prior_validation.py` puts scripts/
# (not the repo root) on sys.path, so Stage-1 `src....` imports would fail
# without it. This block must stay BEFORE any TimeTagger shim or `src.qkd_io`
# import. It reads no files and has no other side effects.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

STAGE1_PACKET = (
    ".workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md"
)
STAGE1_STATUS = (
    ".workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/STATUS.yaml"
)

# Frozen CLI spellings (packet §5/§6 commands). Used for add_argument and for
# user-facing messages so the literal appears once.
FLAG_G1 = "--stage-g1-nll"
FLAG_G2 = "--stage-g2-decode"

# Frozen G2 one-shot K pair (packet §6): G2 decodes frozen K1=319/K2=6492
# regardless; any re-split belongs to a separate later freeze.
FROZEN_K1 = 319
FROZEN_K2 = 6492

# CLI-flag -> freeze-config-key cross-check (packet Spec 5). A provided
# flag whose normalized value differs from the freeze value is a hard
# error, never a silent override. --k1/--k2 have no freeze key; they are
# pinned to FROZEN_K1/FROZEN_K2 instead. --acq-id/--out-root are runtime
# selectors with no freeze key.
FLAG_FREEZE_KEYS = {
    "window_primary": "pairing_window_primary",
    "window_sensitivity": "pairing_window_sensitivity",
    "skip": "skip_frames",
    "mod": "mod_boundary",
    "char_pairs": "char_sample_pairs",
    "blocks": "g2_blocks",
    "tag_master": "tag_master",
    "arms": "g2_arms",
}

# The 19 STATUS.yaml to_freeze keys (sorted). Authoritative source of values
# is the --freeze-config file; a missing or null key is a hard error.
REQUIRED_FREEZE_KEYS = (
    "B_tail",
    "a1_cal_ids",
    "block_formation_fallback",
    "cal_frame_ids",
    "cal_split_rule",
    "char_sample_pairs",
    "delta_min",
    "disjointness_matrix",
    "g2_arms",
    "g2_blocks",
    "g2_fail_rule",
    "g2_inconclusive_rule",
    "g2_success_rule",
    "heldout_frame_ids",
    "mod_boundary",
    "pairing_window_primary",
    "pairing_window_sensitivity",
    "skip_frames",
    "tag_master",
)


def _fail(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _ensure_timetagger_shim() -> str:
    """Make the bare ``TimeTagger`` name importable (Stage-1 helper).

    Tries the bare top-level name first; otherwise aliases the official
    ``Swabian.TimeTagger`` into ``sys.modules``. Stage 1 MUST call this
    BEFORE any ``src.qkd_io`` import (``src/qkd_io/ttbin_pipeline.py`` does
    ``from TimeTagger import FileReader``). Deferred into a function so
    module import stays pure. Returns which path resolved.
    """
    try:
        import TimeTagger  # type: ignore  # noqa: F401

        return "bare-toplevel-TimeTagger"
    except Exception:
        pass
    try:
        from Swabian import TimeTagger as _TT  # type: ignore
    except Exception as exc:
        _fail(f"neither TimeTagger nor Swabian.TimeTagger is importable: {exc}")
    sys.modules.setdefault("TimeTagger", _TT)
    return "swabian-shim"


def _missing_freeze_keys(cfg: dict) -> list[str]:
    """Sorted required keys absent or null in an already-loaded mapping.

    Pure: no I/O. Only absence and explicit null count as missing (0, false
    and empty containers count as present per the packet's null/absent rule).
    """
    if not isinstance(cfg, dict):
        _fail("freeze-config top level must be a JSON/YAML mapping/object")
    return sorted(k for k in REQUIRED_FREEZE_KEYS if cfg.get(k) is None)


def load_freeze_config(path: Path | str) -> dict:
    """Load ``--freeze-config`` and require ALL 19 keys.

    Accepts ``.json`` natively and ``.yaml``/``.yml`` only when PyYAML
    imports. Any missing or null key prints the sorted missing list and
    exits 2. NEVER substitutes a default.
    """
    p = Path(path)
    if not p.is_file():
        _fail(f"freeze-config not found: {p} (run from repo root; no defaults substituted)")
    suffix = p.suffix.lower()
    if suffix == ".json":
        try:
            cfg = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            _fail(f"freeze-config {p} is not valid JSON: {exc}")
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml  # deferred: PyYAML is optional, never imported at module level
        except Exception:
            _fail(
                f"freeze-config {p} needs YAML but PyYAML is not installed; "
                "use a .json freeze-config instead"
            )
        try:
            cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as exc:
            _fail(f"freeze-config {p} is not valid YAML: {exc}")
    else:
        _fail(f"freeze-config {p} has unknown suffix {suffix!r}; use .json or .yaml/.yml")
    missing = _missing_freeze_keys(cfg)
    if missing:
        _fail(
            f"freeze-config {p} missing/null {len(missing)} required key(s): "
            + ", ".join(missing)
            + " (sorted; refusing to substitute defaults)"
        )
    return cfg


# Forbidden-tree guard: additive to the Spec-5 workspace/ confinement enforced by _out_root_workspace_refusal.
def _out_root_refusal(out_root: Path | str) -> str | None:
    """None when ``--out-root`` is an allowed target, else the refusal text.

    Pure: resolves paths but never creates anything. Refuses any target at
    or under ``results/`` or ``comparison_bench/outputs_comparison/``.
    """
    r = Path(out_root).expanduser()
    if not r.is_absolute():
        r = Path.cwd() / r
    try:
        r = r.resolve()
    except Exception as exc:
        return f"cannot resolve --out-root {out_root!s}: {exc}"
    for forbidden in (
        _REPO_ROOT / "results",
        _REPO_ROOT / "comparison_bench" / "outputs_comparison",
    ):
        try:
            f = forbidden.resolve()
        except Exception:
            f = forbidden
        if r == f or f in r.parents:
            return (
                f"refusing --out-root {r}: inside forbidden tree {f}; "
                "M2 outputs are additive under workspace/m2_prior_validation/ only"
            )
    return None


def _require_authorized(authorized: bool) -> None:
    """Hard gate: stage modes run ONLY with ``--authorized``.

    No file access here; the caller must invoke this before any
    freeze-config parsing or data access.
    """
    if not authorized:
        print(
            "ERROR: stage execution requires --authorized "
            "(refusing implicit production run)",
            file=sys.stderr,
        )
        raise SystemExit(2)


def _out_root_workspace_refusal(out_root: Path | str) -> str | None:
    """None when ``--out-root`` resolves under repo ``workspace/``, else text.

    Pure: resolves paths but never creates anything. Stage-1 M2 outputs
    (when later freezes allow them) are additive under ``workspace/``
    only; anything else exits 2.
    """
    r = Path(out_root).expanduser()
    if not r.is_absolute():
        r = Path.cwd() / r
    try:
        r = r.resolve()
    except Exception as exc:
        return f"cannot resolve --out-root {out_root!s}: {exc}"
    anchor = _REPO_ROOT / "workspace"
    try:
        anchor_resolved = anchor.resolve()
    except Exception:
        anchor_resolved = anchor
    if r == anchor_resolved or anchor_resolved in r.parents:
        return None
    return (
        f"refusing --out-root {r}: outside workspace/ ({anchor_resolved}); "
        "M2 outputs are additive under workspace/m2_prior_validation/ only"
    )


def _norm_crosscheck(value) -> str:
    """Normalize one side of a flag/freeze comparison (whitespace-blind).

    Freeze lists (e.g. ``g2_arms: [A1, A2, B]``) compare as comma-joined
    against the CLI spelling (``--arms A1,A2,B``).
    """
    if isinstance(value, (list, tuple)):
        text = ",".join(str(v) for v in value)
    else:
        text = str(value)
    return "".join(text.split())


def _cross_check_mismatches(options: dict, freeze: dict) -> list[str]:
    """Flag values (when provided) that disagree with the freeze file.

    Pure: no I/O. The freeze file is authoritative; a provided CLI flag
    that contradicts it is a hard error, never an override.
    """
    out: list[str] = []
    for flag, key in FLAG_FREEZE_KEYS.items():
        opt = options.get(flag)
        if opt is None:
            continue
        frozen = freeze.get(key)
        if _norm_crosscheck(opt) != _norm_crosscheck(frozen):
            out.append(f"--{flag.replace('_', '-')}={opt!r} != freeze {key}={frozen!r}")
    return out


def _check_k_pin(k1, k2) -> None:
    """Pin ``--k1/--k2`` to the frozen G2 pair (no I/O; exits 2 on violation)."""
    for label, value, want in (("k1", k1, FROZEN_K1), ("k2", k2, FROZEN_K2)):
        if value is None:
            continue
        try:
            got = int(str(value).strip())
        except (TypeError, ValueError):
            got = None
        if got != want:
            _fail(
                f"--{label} must equal frozen {want}, got {value!r} "
                "(G2 decodes frozen K1=319/K2=6492 regardless; "
                "re-split needs its own freeze)"
            )


# ---------------------------------------------------------------------------
# G1 body (decoder-free; Phase-0 implementation for
# NBPOLAR-M2-PRIOR-G1-REALDATA-NLL, freeze g1_freeze.md).
#
# Boundaries (hard): NEVER call a decoder here (no sc_decode / genie /
# SCL anywhere in this file); NEVER read SHG `_2` (production reader
# refuses it); NEVER write outside the passed ``out_root`` (workspace-
# confined by the Stage-1 guard) except the single Phase-A packet-dir
# freeze-config emission. Remainder science takes caller-supplied pair
# arrays only (no alignment, no char sample — exempt per freeze §1.2);
# the production remainder pairs binding belongs to the Phase-B
# dispatch and is refused loudly, never invented.
# ---------------------------------------------------------------------------

# Frozen (N)-pairing constants, vendored literally from the 2026-09-21
# census implementation `workspace/dual_rule_census_20260921.py`
# (`frozen` block + `_count_nearest` + symbol map `(b_A % 1024,
# b_B % 1024)`, `b = t // 200`, `tA_aligned = tA_raw + offset`).
G1_D = 1024
G1_BIN_WIDTH_PS = 200
G1_PERIOD_PS = 204800
G1_FRAME_PAIRS = 256
G1_GATE_PS = 200  # frozen design-gate provenance (census frozen block)
G1_THRESHOLD_PS = 40000  # frozen threshold provenance (same block)
G1_SCAN_RANGE_PS = 409600
G1_BIN_PS_ALIGN = 100
G1_PEAK_TO_BG_MIN = 10.0

# Phase-A reproduction gate (g1_freeze.md §2/§6; observed values in
# `workspace/census_20260921/20260113_SHG_Type2PPLN_3s/dual_rule_census.json`).
REPRO_GATE = {
    "peak_center_ps": 50,
    "peak_sigma_ps": 112.45189572400645,
    "status": "ok",
    "n_pairs": 1269268,
    "n_frames": 4958,
}

# Segment layout (g1_freeze.md §4): 0-based post-skip complete frames.
SEG_RANGES = (
    ("a1_cal", 0, 1023),
    ("cal32", 1024, 1055),
    ("char", 1056, 1837),
    ("heldout", 1838, 2397),
    ("eval", 2398, 4189),
)
SEG_RESERVE = ("reserve", 4190, 4255)
ALLOCATED_FRAMES = 4190  # frames 0..4189 must exist (freeze §4 fallback)

REMAINDER_ACQ_ID = "remainder_101f"
REMAINDER_N_FRAMES = 101
REMAINDER_CAL_FRAMES = 32

G1_PACKET_DIR = _REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL"
G1_CONFIG_NAME = "g1_freeze_config.json"

# G1R2 successor contract (delta item 8, NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR):
# same layout/mechanics as G1, corrected pairing+MOD window (w=200).
REPRO_GATE_G1R2 = {
    "peak_center_ps": 50,
    "peak_sigma_ps": 112.45189572400645,
    "status": "ok",
    "n_pairs": 1259992,
    "n_frames": 4921,
}
G1R2_PACKET_DIR = _REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR"
G1R2_CONFIG_NAME = "g1r2_freeze_config.json"

# Per-contract record. Selection is explicit and deterministic via
# freeze["pairing_window_primary"] (500 -> G1 legacy, 200 -> G1R2) —
# never inferred by reading data. G1's literals stay verbatim so a G1
# invocation reproduces its accepted record; alignment literals
# (peak_center / sigma / status) are shared across both contracts.
CONTRACTS = {
    500: {
        "window": 500,
        "repro_gate": REPRO_GATE,
        "packet_dir": G1_PACKET_DIR,
        "config_name": G1_CONFIG_NAME,
        "packet": "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL",
        "freeze": "NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1_freeze.md",
        "label": "G1",
        "science_mode": "g1-science",
    },
    200: {
        "window": 200,
        "repro_gate": REPRO_GATE_G1R2,
        "packet_dir": G1R2_PACKET_DIR,
        "config_name": G1R2_CONFIG_NAME,
        "packet": "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR",
        "freeze": "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/TASK_PACKET.md",
        "label": "G1R2",
        "science_mode": "g1r2-science",
    },
}


def contract_for_window(window) -> dict:
    """Select the science contract for an explicit pairing window (pure).

    500 selects the G1 legacy contract, 200 the G1R2 successor. Any
    other value exits 2 loudly (never a silent default, never inferred
    from data — the caller passes the freeze value through).
    """
    try:
        w = int(str(window).strip())
    except (TypeError, ValueError):
        w = None
    if w not in CONTRACTS:
        _fail(
            f"pairing_window_primary {window!r} selects no science contract "
            f"(known windows: {sorted(CONTRACTS)}; G1=500, G1R2=200)"
        )
    return CONTRACTS[w]


def contract_for_freeze(freeze: dict) -> dict:
    """Select the science contract from an already-loaded freeze mapping."""
    return contract_for_window(freeze.get("pairing_window_primary"))


def reserve_ids_for_ledger(n_postskip) -> dict:
    """Ledger-driven reserve emission (delta item 8; pure, no I/O).

    The reserve starts at ALLOCATED_FRAMES (frames 0..ALLOCATED_FRAMES-1
    are allocated) and ends at the last available post-skip frame
    (n_postskip - 1): 4190..4255 at the G1 ledger (4256 frames, exactly
    the legacy SEG_RESERVE range), 4190..4218 at the G1R2 ledger (4219
    frames). When no post-skip frame lies beyond the allocation the
    reserve is empty with a recorded note — frame ids are never
    invented, so ids past the ledger end (e.g. 4219+ at w=200) cannot
    be emitted.
    """
    n = int(n_postskip)
    start = ALLOCATED_FRAMES
    end = n - 1
    if end < start:
        return {
            "ids": [],
            "note": (
                f"no post-skip frame beyond allocated {ALLOCATED_FRAMES} "
                f"(ledger {n}); empty reserve, never invented"
            ),
        }
    return {"ids": list(range(start, end + 1)), "note": ""}

MODES = ("LINEAR_ONLY", "CIRCULAR")

BUDGET_CLOSURE_S = 300.0
BUDGET_G1_S = 600.0
BUDGET_RSS_GIB = 2.0


class _InsufficientFrames(Exception):
    """Post-skip ledger below ALLOCATED_FRAMES (freeze §4 fallback path)."""


def _frozen_leaf_module(relpath: str, cache_name: str):
    """Load a frozen NumPy+stdlib-only leaf module read-only by file location.

    The mandated venv cannot use the ``formal_ir`` package import path
    (its ``__init__`` needs pandas, which no venv here provides), so the
    leaf file itself — the identical frozen source — is loaded directly.
    A runtime AST check refuses relative imports, frozen-package-root
    imports, TimeTagger imports, and any decoder entry point before
    loading. The file is only read, never modified.
    """
    import ast
    import importlib.util

    cache = globals().setdefault("_FROZEN_LEAF_CACHE", {})
    if cache_name in cache:
        return cache[cache_name]
    path = _REPO_ROOT / relpath
    if not path.is_file():
        _fail(f"frozen leaf not found: {path}")
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if (node.level or 0) != 0:
                _fail(f"frozen leaf {relpath} uses a relative import (refusing file-location load)")
            root = (node.module or "").split(".")[0]
            if root in ("nbpolar", "comparison_bench", "TimeTagger"):
                _fail(f"frozen leaf {relpath} imports frozen/package root {root!r} (refusing file-location load)")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in ("nbpolar", "comparison_bench", "TimeTagger"):
                    _fail(f"frozen leaf {relpath} imports {alias.name!r} (refusing file-location load)")
    for banned in ("sc_decode", "genie_conditionals"):
        if banned in src:
            _fail(f"frozen leaf {relpath} mentions decoder entry {banned!r} (refusing load)")
    spec = importlib.util.spec_from_file_location(cache_name, str(path))
    module = importlib.util.module_from_spec(spec)
    # Register before exec: dataclass processing resolves the module via
    # sys.modules[cls.__module__]; without this the load fails.
    sys.modules[cache_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(cache_name, None)
        raise
    cache[cache_name] = module
    return module


def _frozen_m2():
    """Stage-1 M2/M0 surface (accepted; CANDIDATE adapter, never baseline)."""
    return _frozen_leaf_module(
        "comparison_bench/src/comparison_bench/formal_ir/prior_m2.py",
        "m2_g1_frozen_prior_m2",
    )


def _frozen_prior():
    """Frozen layer-factorization helpers (derive_p1/derive_p2/...; unchanged)."""
    return _frozen_leaf_module(
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py",
        "m2_g1_frozen_nbpolar_prior",
    )


def pair_narrow_nearest_unique(tA_sorted, tB_sorted, offset, window):
    """(N) narrow nearest-unique pairing with census symbol mapping.

    Greedy monotonic 1-1 loop vendored literally from
    ``workspace/dual_rule_census_20260921.py::_count_nearest`` (symmetric
    window, offset applied to Alice raw timestamps); on a match the
    census symbol map applies: ``b = t // 200`` with
    ``tA_aligned = tA_raw + offset``, symbols ``(b_A % 1024,
    b_B % 1024)``. The (W) legacy rule is NEVER used for G1 science.
    Returns ``(alice, bob)`` int64 vectors, chronological.
    """
    a = np.asarray(tA_sorted, dtype=np.int64).ravel()
    b = np.asarray(tB_sorted, dtype=np.int64).ravel()
    aL = a.tolist()
    bL = b.tolist()
    off = int(offset)
    w = int(window)
    if w < 0:
        raise ValueError(f"pairing window must be non-negative, got {window!r}")
    i = j = 0
    na, nb = len(aL), len(bL)
    pa: list = []
    pb: list = []
    bw = G1_BIN_WIDTH_PS
    dd = G1_D
    while i < na and j < nb:
        dt = aL[i] + off - bL[j]
        if dt < -w:
            i += 1
        elif dt > w:
            j += 1
        else:
            pa.append(((aL[i] + off) // bw) % dd)
            pb.append((bL[j] // bw) % dd)
            i += 1
            j += 1
    return (np.asarray(pa, dtype=np.int64), np.asarray(pb, dtype=np.int64))


def chunk_frames(alice, bob, skip_frames, frame_pairs=G1_FRAME_PAIRS):
    """Apply skip, chunk into fixed frames, drop the trailing incomplete frame.

    Returns ``(frames_a, frames_b, ledger)`` with ``(n_complete,
    frame_pairs)`` int64 arrays and a ledger dict (skip/post-skip/drop
    counts). Pure; no I/O.
    """
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    fp = int(frame_pairs)
    if fp <= 0:
        raise ValueError(f"frame_pairs must be positive, got {frame_pairs!r}")
    skip_pairs = int(skip_frames) * fp
    if skip_pairs < 0:
        raise ValueError(f"skip_frames must be non-negative, got {skip_frames!r}")
    if a.size < skip_pairs:
        raise ValueError(f"stream of {a.size} pairs shorter than skip {skip_pairs}")
    rest_a = a[skip_pairs:]
    rest_b = b[skip_pairs:]
    n_complete = int(rest_a.size // fp)
    used = n_complete * fp
    ledger = {
        "skip_frames": int(skip_frames),
        "skip_pairs": skip_pairs,
        "preskip_pairs": int(a.size),
        "postskip_pairs": int(rest_a.size),
        "frame_pairs": fp,
        "complete_frames": n_complete,
        "used_pairs": used,
        "dropped_trailing_pairs": int(rest_a.size - used),
    }
    return (
        rest_a[:used].reshape(n_complete, fp),
        rest_b[:used].reshape(n_complete, fp),
        ledger,
    )


def build_counts_1024(alice, bob):
    """Paired symbols -> counts_ab ``[Alice,Bob]`` int64 ``(1024,1024)``."""
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    if a.size == 0:
        raise ValueError("empty symbol vectors")
    if a.min() < 0 or a.max() > 1023 or b.min() < 0 or b.max() > 1023:
        raise ValueError("symbols out of [0,1023]")
    counts = np.zeros((G1_D, G1_D), dtype=np.int64)
    np.add.at(counts, (a, b), 1)
    return counts


def mod_tail_counts(alice, bob, mod):
    """Delta-mass triple under the frozen MOD (mirror of fit_m2_triple fit level).

    LINEAR_ONLY: wrap cells (0,1023)/(1023,0) count as tail
    (conservative); CIRCULAR: priced as +/-1 neighbours. Pure.
    """
    if mod not in MODES:
        raise ValueError(f"mod must be one of {list(MODES)}, got {mod!r}")
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    n = int(a.size)
    if n == 0:
        raise ValueError("empty symbol vectors")
    n0 = int((a == b).sum())
    if mod == "LINEAR_ONLY":
        d = a - b
        n_plus = int((d == 1).sum())
        n_minus = int((d == -1).sum())
    else:
        d = (a - b) % G1_D
        n_plus = int((d == 1).sum())
        n_minus = int((d == G1_D - 1).sum())
    return {
        "n0": n0,
        "n_plus": n_plus,
        "n_minus": n_minus,
        "n_tail": n - n0 - n_plus - n_minus,
        "n_total": n,
        "mod": mod,
    }


def delta_profile(alice, bob):
    """Delta-mass profile linear AND circular (G1-2, descriptive, no gate).

    Linear bins cover -1023..1023 (offset -1023); circular signed bins
    cover -512..511 (offset -512). Summaries under both MOD values via
    :func:`mod_tail_counts`. Pure.
    """
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape or a.size == 0:
        raise ValueError("alice/bob must be equal-length non-empty vectors")
    d_lin = a - b
    lin = np.bincount(d_lin + 1023, minlength=2047)
    d_circ = ((d_lin + 512) % G1_D) - 512
    circ = np.bincount(d_circ + 512, minlength=1024)
    return {
        "n": int(a.size),
        "linear_counts": [int(v) for v in lin],
        "linear_offset": -1023,
        "circular_counts": [int(v) for v in circ],
        "circular_offset": -512,
        "summaries": {
            "LINEAR_ONLY": mod_tail_counts(a, b, "LINEAR_ONLY"),
            "CIRCULAR": mod_tail_counts(a, b, "CIRCULAR"),
        },
    }


def clopper_pearson_upper(k, n, alpha=0.05):
    """One-sided exact upper limit: p solving P(X <= k | p) = alpha.

    Stdlib-only (log-domain binomial CDF + bisection; no scipy in the
    mandated venv). ``k >= n`` -> 1.0. Pure.
    """
    k = int(k)
    n = int(n)
    if n <= 0:
        raise ValueError(f"n must be positive, got {n!r}")
    if not 0 <= k <= n:
        raise ValueError(f"k must lie in 0..n, got k={k!r} n={n!r}")
    if k >= n:
        return 1.0
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must lie in (0,1), got {alpha!r}")

    def _cdf_le(p):
        if p <= 0.0:
            return 1.0
        if p >= 1.0:
            return 0.0
        lp = math.log(p)
        lq = math.log1p(-p)
        ln = math.lgamma(n + 1)
        terms = [
            ln - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq
            for i in range(k + 1)
        ]
        mx = max(terms)
        return min(1.0, math.fsum(math.exp(t - mx) for t in terms) * math.exp(mx))

    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _cdf_le(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def eval_delta_tail(n_tail, n, B_tail):
    """G1-dtail gate exactly per freeze §6 (CHAR only, frozen MOD decides wrap).

    Zero observations -> rule-of-three ``3/n``; else Clopper-Pearson
    upper. PASS iff U < B_tail; FAIL iff phat > B_tail; else
    INCONCLUSIVE (bounded negative, no proceed). Pure.
    """
    n_tail = int(n_tail)
    n = int(n)
    if n <= 0 or not 0 <= n_tail <= n:
        raise ValueError(f"need 0 <= n_tail <= n with n > 0, got {n_tail!r}/{n!r}")
    B = float(B_tail)
    p_hat = n_tail / n
    U = 3.0 / n if n_tail == 0 else clopper_pearson_upper(n_tail, n)
    if U < B:
        verdict = "PASS"
    elif p_hat > B:
        verdict = "FAIL"
    else:
        verdict = "INCONCLUSIVE"
    return {"p_hat": p_hat, "U": U, "n_tail": n_tail, "n": n, "B_tail": B, "verdict": verdict}


def eval_nll_gate(delta, delta_min):
    """G1-NLL gate exactly per freeze §6 (matched-CAL, descriptive only).

    PASS iff Δ > Δ_min; FAIL iff Δ <= 0; else INCONCLUSIVE. Pure.
    """
    d = float(delta)
    m = float(delta_min)
    if d > m:
        verdict = "PASS"
    elif d <= 0:
        verdict = "FAIL"
    else:
        verdict = "INCONCLUSIVE"
    return {"delta_bits": d, "delta_min_bits": m, "verdict": verdict}


def _bits_entropy(probs) -> float:
    p = np.asarray(probs, dtype=np.float64).ravel()
    p = p[p > 0]
    if p.size == 0:
        return 0.0
    return float(-np.sum(p * np.log2(p)))


def model_entropy_bits(joint, p_b, prior_mod):
    """Model-implied H1/H2/H_total via the UNCHANGED frozen derive helpers.

    ``p1 = derive_p1(joint)`` ``[U1,B]``, ``p2 = derive_p2(joint)``
    ``[U1,B,U2]``; expectations weighted by the CAL empirical Bob
    marginal ``p_b`` (the V49 raw-MLE population functional per
    troubleshooting: ``H1 = sum_b p_b H(P1)``,
    ``H2 = sum_b p_b sum_u1 P1(u1|b) H(P2)``). Bits. Pure.
    """
    j = np.asarray(joint, dtype=np.float64)
    if j.shape != (G1_D, G1_D):
        raise ValueError(f"joint must be (1024,1024), got shape {j.shape}")
    pb = np.asarray(p_b, dtype=np.float64).ravel()
    if pb.shape != (G1_D,) or not np.isfinite(pb).all() or (pb < 0).any():
        raise ValueError("p_b must be a finite non-negative length-1024 vector")
    if abs(float(pb.sum()) - 1.0) > 1e-9:
        raise ValueError("p_b must sum to 1")
    p1 = np.asarray(prior_mod.derive_p1(j), dtype=np.float64)
    p2 = np.asarray(prior_mod.derive_p2(j), dtype=np.float64)
    h1 = 0.0
    h2 = 0.0
    for bb in range(G1_D):
        w = float(pb[bb])
        if w == 0.0:
            continue
        h1 += w * _bits_entropy(p1[:, bb])
        row1 = p1[:, bb]
        for u in range(32):
            wu = float(row1[u])
            if wu == 0.0:
                continue
            h2 += w * wu * _bits_entropy(p2[u, bb, :])
    h1 = float(h1)
    h2 = float(h2)
    return {"H1_bits": h1, "H2_bits": h2, "H_total_bits": h1 + h2}


def heldout_nll_bits(joint, bob_frames, alice_frames, prior_mod):
    """Held-out per-symbol NLL (bits) through the frozen metric pipeline.

    ``build_p1_metrics`` / ``gather_p2_metrics`` (hard Alice ``u1`` for
    L2 scoring — oracle scoring of held-out truth, decoder-free) ->
    ``probs_to_symbol_metric(provenance=PRIOR_ONLY)`` per layer; NLL is
    ``-(logp1[u1] + logp2[u2]) / ln2`` averaged over held-out symbols.
    ``bob_frames``/``alice_frames`` are ``(F,P)`` int arrays. Pure.
    """
    bf = np.asarray(bob_frames, dtype=np.int64)
    af = np.asarray(alice_frames, dtype=np.int64)
    if bf.shape != af.shape or bf.ndim != 2 or bf.shape[1] == 0:
        raise ValueError(f"bob/alice frames must be equal non-empty (F,P), got {bf.shape}/{af.shape}")
    if bf.min() < 0 or bf.max() > 1023 or af.min() < 0 or af.max() > 1023:
        raise ValueError("frame symbols out of [0,1023]")
    j = np.asarray(joint, dtype=np.float64)
    if j.shape != (G1_D, G1_D):
        raise ValueError(f"joint must be (1024,1024), got shape {j.shape}")
    p1 = prior_mod.derive_p1(j)
    p2 = prior_mod.derive_p2(j)
    u1 = ((af >> 5) & 31).astype(np.int64)
    u2 = (af & 31).astype(np.int64)
    m1 = np.asarray(prior_mod.build_p1_metrics(bf, p1), dtype=np.float64).reshape(-1, 32)
    s1 = prior_mod.probs_to_symbol_metric(m1, provenance=prior_mod.Provenance.PRIOR_ONLY)
    l1 = -np.asarray(s1.logp)[np.arange(u1.size), u1.ravel()] / math.log(2)
    g2 = np.asarray(prior_mod.gather_p2_metrics(bf, u1, p2), dtype=np.float64).reshape(-1, 32)
    s2 = prior_mod.probs_to_symbol_metric(g2, provenance=prior_mod.Provenance.PRIOR_ONLY)
    l2 = -np.asarray(s2.logp)[np.arange(u2.size), u2.ravel()] / math.log(2)
    tot = l1 + l2
    return {
        "n_symbols": int(u1.size),
        "nll_mean_bits": float(tot.mean()),
        "nll_l1_bits": float(l1.mean()),
        "nll_l2_bits": float(l2.mean()),
    }


def segment_frame_lists(n_postskip):
    """Enumerate the freeze §4 segment lists over post-skip frames.

    Raises :class:`_InsufficientFrames` when the ledger holds fewer
    than ALLOCATED_FRAMES (freeze §4 ``block_formation_fallback``).
    Pure.
    """
    n = int(n_postskip)
    if n < ALLOCATED_FRAMES:
        raise _InsufficientFrames(
            f"post-skip ledger {n} < allocated {ALLOCATED_FRAMES}: "
            "COMPLETE-BLOCKS-ONLY else INSUFFICIENT => INCONCLUSIVE "
            "(never pad/reuse/shrink)"
        )
    return {name: list(range(s, e + 1)) for name, s, e in SEG_RANGES}


def disjointness_matrix(segments):
    """Pairwise-disjointness proof over named frame-ID lists (pure).

    ``segments`` maps name -> iterable of frame ids. Returns the
    segment ranges plus every pairwise overlap count and the
    ``all_disjoint`` flag; any overlap invalidates the run.
    """
    sets = {name: set(int(v) for v in ids) for name, ids in segments.items()}
    names = sorted(sets)
    pairwise = {}
    for ii in range(len(names)):
        for jj in range(ii + 1, len(names)):
            a, b = names[ii], names[jj]
            pairwise[f"{a}|{b}"] = len(sets[a] & sets[b])
    ranges = {
        name: [min(sets[name]), max(sets[name])] if sets[name] else []
        for name in names
    }
    return {
        "segments": ranges,
        "pairwise_overlap": pairwise,
        "all_disjoint": all(v == 0 for v in pairwise.values()),
    }


def remainder_split_ids(n_frames=REMAINDER_N_FRAMES):
    """Remainder mini-layout: 32 CAL + 69 held-out (chronological, pure)."""
    n = int(n_frames)
    if n != REMAINDER_N_FRAMES:
        raise ValueError(f"remainder population holds {REMAINDER_N_FRAMES} frames, got {n!r}")
    return {
        "cal_ids": list(range(0, REMAINDER_CAL_FRAMES)),
        "heldout_ids": list(range(REMAINDER_CAL_FRAMES, REMAINDER_N_FRAMES)),
    }


def _peak_rss_gib_advisory():
    """VmHWM-based peak RSS in GiB (advisory only; never a gate)."""
    try:
        with open("/proc/self/status", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    kb = float(line.split()[1])
                    return kb / 1024.0**2
    except Exception:
        pass
    return None


def _read_timetags_production(acq_id):
    """Production timetag read: inventory primary ONLY (autofollow rule).

    Deferred TimeTagger shim + ``src.qkd_io`` import (import purity:
    never at module top). SHG `_2` is refused loudly here. Returns
    ``(tA_sorted, tB_sorted)`` int64 raw timestamps.
    """
    if acq_id == "20260113_SHG_Type2PPLN_3s_2" or str(acq_id).endswith("_2"):
        _fail(
            f"refusing protected acquisition {acq_id!r}: SHG `_2` is frozen "
            "for G3 (no G1/G2 contact of any kind)"
        )
    _ensure_timetagger_shim()
    from scripts.census_intake_20260921 import (  # deferred: runs its own shim+src import
        HW_A,
        HW_B,
        _acq_files,
    )
    from src.qkd_io.ttbin_pipeline import read_ttbin_events  # deferred

    prim, _cont = _acq_files(acq_id)
    if not prim.exists():
        _fail(f"raw file not found: {prim} (run from repo root)")
    try:
        ev = read_ttbin_events(prim)  # primary ONLY; FileReader auto-follows `.1`
    except Exception as exc:
        _fail(f"{acq_id}: FileReader(primary) failed: {exc}")
    ch = np.asarray(ev.channel).astype(np.int64)
    ts = np.asarray(ev.time_ps).astype(np.int64)
    del ev
    if ch.shape != ts.shape or ch.ndim != 1 or int(ch.size) == 0:
        _fail(f"{acq_id}: primary read self-inconsistent")
    total = int(ch.size)
    uniq, counts = np.unique(ch, return_counts=True)
    chan_hist = {int(k): int(v) for k, v in zip(uniq.tolist(), counts.tolist())}
    other = int(np.sum((ch != HW_A) & (ch != HW_B)))
    import gc as _gc

    tA = np.sort(ts[ch == HW_A])
    tB = np.sort(ts[ch == HW_B])
    del ch, ts
    _gc.collect()
    return {
        "tA": tA,
        "tB": tB,
        "n_events": total,
        "channel_hist": chan_hist,
        "other_count": other,
        "other_frac": other / total if total else 1.0,
        "primary": str(prim),
    }


def _align_frozen(tA, tB):
    """ONE frozen-params alignment call (scan 409600 / bin 100).

    Deferred estimator load (frozen
    ``src/workflow/export_joint_sequence_sidecar.py`` single function).
    Returns the estimator dict.
    """
    from scripts.census_intake_20260921 import _load_peak_estimator  # deferred

    peak_fn, _load_path = _load_peak_estimator()
    return peak_fn(
        np.asarray(tA, dtype=np.int64),
        np.asarray(tB, dtype=np.int64),
        scan_range_ps=G1_SCAN_RANGE_PS,
        bin_ps=G1_BIN_PS_ALIGN,
    )


def _yield_sweep_selfcheck(tA, tB, derived_offset):
    """Mandatory yield-vs-offset self-check ((W) sweep, self-check ONLY).

    The (W) legacy rule is used here exactly as in the census — as an
    alignment self-check, never for G1 science. Deferred import.
    """
    from scripts.census_intake_20260921 import yield_vs_offset  # deferred

    return yield_vs_offset(
        np.asarray(tA, dtype=np.int64),
        np.asarray(tB, dtype=np.int64),
        int(derived_offset),
    )


def _sweep_accept(sweep):
    """Yield-sweep self-check verdict under the census dual_rule convention.

    The frozen provenance (``dual_rule_census_20260921.py:239-247``,
    adopted by ``g1_freeze.md`` §2) treats within-one-coarse-step as
    PASS-with-note: a strict-exact-max miss is recorded as a note, and
    only a beyond-one-step miss is a self-check failure. (The intake
    ``yield_max_ok`` flag additionally demands strict plateau
    membership; the dual_rule convention governs here because the
    freeze's census values carry its PASS-with-note verdict.) Pure.
    """
    within = bool(sweep["within_one_step_of_max_ok"])
    strict = bool(sweep.get("strict_exact_max", sweep.get("plateau_membership_ok")))
    if within:
        note = ("derived offset at sweep maximum" if strict
                else "strict-exact-max miss recorded as note; "
                     "within-one-coarse-step treated as PASS-with-note per 2026-09-21 tasking")
    else:
        note = "SELF-CHECK MISS: derived offset beyond one coarse step of maximum"
    return within, note


def _tier(n_pairs):
    from scripts.census_intake_20260921 import (  # deferred
        TIER_FULL_MIN,
        TIER_REDUCED_MIN,
    )

    n_frames = int(n_pairs) // G1_FRAME_PAIRS
    if n_frames >= TIER_FULL_MIN:
        return "FULL"
    if n_frames >= TIER_REDUCED_MIN:
        return "REDUCED"
    return "INSUFFICIENT"


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _closure_outputs(*, acq_id, out_root: Path, freeze, align, sweep, pairing,
                     ledger, segments, matrix, elapsed_s, _packet_dir=None):
    """Flush Phase-A closure artifacts (workspace + packet-dir config)."""
    contract = contract_for_freeze(freeze)
    gate = contract["repro_gate"]
    reserve = reserve_ids_for_ledger(ledger["complete_frames"])
    seg_text = " / ".join(f"{name} {s}-{e}" for name, s, e in SEG_RANGES)
    if reserve["ids"]:
        seg_text += f" / reserve {reserve['ids'][0]}-{reserve['ids'][-1]}"
    else:
        seg_text += f" / reserve empty ({reserve['note']})"
    g1 = {
        "packet": contract["packet"],
        "freeze": contract["freeze"],
        "mode": "closure-only",
        "acq_id": acq_id,
        "nature": "DESCRIPTIVE/NON-CLAIM, decoder-free; M2 CANDIDATE, never baseline",
        "align": align,
        "yield_sweep": sweep,
        "offset_applied_to_alice": int(align["peak_center_ps"]),
        "offset_sign_convention": "tA_aligned = tA_raw + peak_center_ps",
        "pairing": pairing,
        "reproduction_gate": {
            "expected": dict(gate),
            "observed": {
                "peak_center_ps": align["peak_center_ps"],
                "peak_sigma_ps": align["peak_sigma_ps"],
                "status": align["status"],
                "n_pairs": pairing["n_pairs"],
                "n_frames": pairing["n_frames"],
            },
            "match5": (
                align["peak_center_ps"] == gate["peak_center_ps"]
                and align["peak_sigma_ps"] == gate["peak_sigma_ps"]
                and align["status"] == gate["status"]
                and pairing["n_pairs"] == gate["n_pairs"]
                and pairing["n_frames"] == gate["n_frames"]
            ),
            "verdict": "REPRODUCED",
        },
        "ledger": ledger,
        "segments": {name: [ids[0], ids[-1]] for name, ids in segments.items()},
        "disjointness_all_disjoint": bool(matrix["all_disjoint"]),
        "timing": {
            "wall_s": elapsed_s,
            "wall_budget_s": BUDGET_CLOSURE_S,
            "rss_gib_peak_advisory": _peak_rss_gib_advisory(),
            "rss_budget_gib": BUDGET_RSS_GIB,
        },
    }
    _write_json(out_root / "g1.json", g1)
    _write_json(
        out_root / "cal_ids.json",
        {
            "acq_id": acq_id,
            "ledger_complete_frames": ledger["complete_frames"],
            "layout_rule": "g1_freeze.md §4 (0-based post-skip complete frames)",
            "a1_cal_ids": segments["a1_cal"],
            "cal_frame_ids": segments["cal32"],
            "char_frame_ids": segments["char"],
            "heldout_frame_ids": segments["heldout"],
            "eval_frame_ids": segments["eval"],
            "reserve_frame_ids": reserve["ids"],
            "reserve_note": reserve["note"],
            "disjointness_matrix": matrix,
        },
    )
    lines = [
        f"# {contract['label']} Phase-A closure run log — {contract['packet']}",
        "",
        f"acq: {acq_id}",
        f"mode: closure-only (zero NLL/gate science)",
        f"align: peak_center={align['peak_center_ps']} sigma={align['peak_sigma_ps']} "
        f"to_bg={align['peak_to_bg']} status={align['status']}",
        f"yield_sweep: at_derived={sweep['yield_at_derived']} max={sweep['yield_max']} "
        f"note={sweep.get('yield_note', sweep['yield_max_ok'])}",
        f"pairing (N) w={pairing['window']}: n_pairs={pairing['n_pairs']} "
        f"n_frames={pairing['n_frames']} tier={pairing['tier']}",
        "reproduction_gate: 5/5 exact (peak_center / sigma / status / n_pairs / n_frames)",
        f"ledger post-skip: {ledger['complete_frames']} complete frames "
        f"(allocated>={ALLOCATED_FRAMES} ok={ledger['complete_frames'] >= ALLOCATED_FRAMES})",
        f"segments: {seg_text}",
        f"disjointness all_disjoint={matrix['all_disjoint']}",
        f"wall_s={elapsed_s:.1f} (budget {BUDGET_CLOSURE_S}) "
        f"rss_peak_advisory_GiB={g1['timing']['rss_gib_peak_advisory']}",
        "",
        f"Outputs: g1.json cal_ids.json run_log.md (+ packet-dir {contract['config_name']}).",
    ]
    (out_root / "run_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    cfg = {k: freeze[k] for k in REQUIRED_FREEZE_KEYS if k in freeze}
    cfg["a1_cal_ids"] = segments["a1_cal"]
    cfg["cal_frame_ids"] = segments["cal32"]
    cfg["heldout_frame_ids"] = segments["heldout"]
    cfg["disjointness_matrix"] = matrix
    missing = _missing_freeze_keys(cfg)
    if missing:
        _fail(f"closure config missing keys: {', '.join(missing)}")
    # Contract-routed packet-dir emission (never the other contract's
    # dir). _packet_dir is the test-only override (tests MUST pass an
    # explicit fake dir; default None keeps the production routing).
    target_dir = Path(_packet_dir) if _packet_dir is not None else contract["packet_dir"]
    _write_json(target_dir / contract["config_name"], cfg)
    return g1


def run_closure(*, acq_id, out_root: Path, freeze, options, _read_timetags=None):
    """Phase-A freeze closure (SHG `_1`, ONE framing pass; decoder-free).

    No prior fitting, no NLL, no gates. Emits the workspace closure
    artifacts plus the complete packet-dir freeze-config (all 19 keys).
    Returns 0 on REPRODUCED; 1 (loud) on ALIGN/reproduction/ledger
    failures. Creates nothing on the failure paths before the point of
    evidence flush (partial g1.json is flushed for forensics).
    """
    import time as _time

    t0 = _time.time()
    read = _read_timetags or _read_timetags_production
    window = int(freeze["pairing_window_primary"])
    skip = int(freeze["skip_frames"])
    mod = str(freeze["mod_boundary"])

    got = read(acq_id)
    tA, tB = got["tA"], got["tB"]
    if float(got.get("other_frac", 0.0)) > 0.20:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(
            out_root / "g1.json",
            {"acq_id": acq_id, "mode": "closure-only", "verdict": "CHANNEL_FAIL",
             "other_frac": got.get("other_frac"), "channel_hist": got.get("channel_hist")},
        )
        print(f"CLOSURE_CHANNEL_FAIL other_frac={got.get('other_frac')}", file=sys.stderr)
        return 1

    peak = _align_frozen(tA, tB)
    align = {
        "estimator_source": "src/workflow/export_joint_sequence_sidecar.py:715",
        "scan_range_ps": G1_SCAN_RANGE_PS,
        "bin_ps": G1_BIN_PS_ALIGN,
        "peak_center_ps": peak.get("peak_center_ps"),
        "peak_sigma_ps": peak.get("peak_sigma_ps"),
        "peak_to_bg": peak.get("peak_to_bg"),
        "status": peak.get("status"),
        "accept": bool(
            peak.get("status") == "ok"
            and peak.get("peak_to_bg") is not None
            and float(peak.get("peak_to_bg")) >= G1_PEAK_TO_BG_MIN
        ),
        "criterion": "status==ok AND peak_to_bg>=10 (unit-independent)",
    }
    if not align["accept"]:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "mode": "closure-only",
                     "verdict": "ALIGN_FAIL", "align": align})
        print(f"CLOSURE_ALIGN_FAIL status={align['status']} to_bg={align['peak_to_bg']}",
              file=sys.stderr)
        return 1

    offset = int(align["peak_center_ps"])
    sweep = _yield_sweep_selfcheck(tA, tB, offset)
    sweep_ok, sweep["yield_note"] = _sweep_accept(sweep)
    if not sweep_ok:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "mode": "closure-only",
                     "verdict": "ALIGN_INCONSISTENT", "align": align,
                     "yield_sweep": sweep})
        print(f"CLOSURE_ALIGN_INCONSISTENT offset={offset} "
              f"yield@derived={sweep['yield_at_derived']} max={sweep['yield_max']}",
              file=sys.stderr)
        return 1

    alice, bob = pair_narrow_nearest_unique(tA, tB, offset, window)
    del tA, tB
    n_pairs = int(alice.size)
    n_frames = n_pairs // G1_FRAME_PAIRS
    pairing = {
        "rule": "(N) narrow nearest-unique",
        "window": window,
        "offset_ps": offset,
        "n_pairs": n_pairs,
        "n_frames": n_frames,
        "tier": _tier(n_pairs),
        "frozen": {"d": G1_D, "bin_width_ps": G1_BIN_WIDTH_PS,
                   "period_ps": G1_PERIOD_PS, "frame_pairs": G1_FRAME_PAIRS},
    }
    gate = contract_for_freeze(freeze)["repro_gate"]
    repro_ok = (
        align["peak_center_ps"] == gate["peak_center_ps"]
        and align["peak_sigma_ps"] == gate["peak_sigma_ps"]
        and align["status"] == gate["status"]
        and n_pairs == gate["n_pairs"]
        and n_frames == gate["n_frames"]
    )
    if not repro_ok:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "mode": "closure-only",
                     "verdict": "ALIGN_INCONSISTENT", "align": align,
                     "yield_sweep": sweep, "pairing": pairing,
                     "reproduction_expected": dict(gate)})
        print("CLOSURE_ALIGN_INCONSISTENT reproduction gate mismatch "
              f"(expected {gate}; observed peak={align['peak_center_ps']}/"
              f"{align['peak_sigma_ps']}/{align['status']} n_pairs={n_pairs} "
              f"n_frames={n_frames})", file=sys.stderr)
        return 1

    _, _, ledger = chunk_frames(alice, bob, skip)
    del alice, bob
    try:
        segments = segment_frame_lists(ledger["complete_frames"])
    except _InsufficientFrames as exc:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "mode": "closure-only",
                     "verdict": "INSUFFICIENT", "align": align,
                     "pairing": pairing, "ledger": ledger,
                     "detail": str(exc)})
        print(f"CLOSURE_INSUFFICIENT {exc}", file=sys.stderr)
        return 1
    named = {
        "a1_cal": segments["a1_cal"],
        "cal32": segments["cal32"],
        "char": segments["char"],
        "heldout": segments["heldout"],
        "eval": segments["eval"],
    }
    matrix = disjointness_matrix(named)
    if not matrix["all_disjoint"]:
        _fail(f"closure segment overlap invalidates run: {matrix['pairwise_overlap']}")
    for key, want in (("a1_cal_ids", named["a1_cal"]),
                      ("cal_frame_ids", named["cal32"]),
                      ("heldout_frame_ids", named["heldout"])):
        if list(freeze.get(key)) != want:
            _fail(f"closure input freeze {key} != §4 rule enumeration "
                  "(bootstrap the input config from the frozen rules verbatim)")

    elapsed = _time.time() - t0
    _closure_outputs(acq_id=acq_id, out_root=out_root, freeze=freeze,
                     align=align, sweep=sweep, pairing=pairing,
                     ledger=ledger, segments=named,
                     matrix=matrix, elapsed_s=elapsed)
    if elapsed > BUDGET_CLOSURE_S:
        print(f"CLOSURE_BUDGET_EXCEEDED wall_s={elapsed:.1f} > {BUDGET_CLOSURE_S}",
              file=sys.stderr)
        return 1
    print(f"CLOSURE_REPRODUCED acq={acq_id} n_pairs={n_pairs} "
          f"postskip_frames={ledger['complete_frames']} wall_s={elapsed:.1f}")
    return 0


def run_remainder_check(*, out_root: Path, freeze, alice, bob):
    """Remainder NLL/H-only check (32 CAL + 69 held-out; exempt path).

    Takes caller-supplied pair arrays (frozen derived pairs at Phase B;
    synthetic fixtures in tests). NO alignment, NO char sample, NO delta
    gate — exempt per freeze §1.2. Decoder-free. Returns 0.
    """
    import time as _time

    t0 = _time.time()
    mod = str(freeze["mod_boundary"])
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    if a.size != REMAINDER_N_FRAMES * G1_FRAME_PAIRS:
        raise ValueError(
            f"remainder population holds {REMAINDER_N_FRAMES * G1_FRAME_PAIRS} pairs, "
            f"got {a.size}"
        )
    fa = a.reshape(REMAINDER_N_FRAMES, G1_FRAME_PAIRS)
    fb = b.reshape(REMAINDER_N_FRAMES, G1_FRAME_PAIRS)
    split = remainder_split_ids()
    m2_mod = _frozen_m2()
    prior_mod = _frozen_prior()
    cal_a = fa[split["cal_ids"]].ravel()
    cal_b = fb[split["cal_ids"]].ravel()
    counts = build_counts_1024(cal_a, cal_b)
    triple = m2_mod.fit_m2_triple(counts, mod=mod)
    joint_m2 = m2_mod.build_m2_joint(triple["q0"], triple["q_plus1"], triple["q_minus1"], mod=mod)
    joint_m0 = m2_mod.build_m0_joint(counts)
    n_cal = float(counts.sum())
    p_b = counts.sum(axis=0) / n_cal
    ent_m2 = model_entropy_bits(joint_m2, p_b, prior_mod)
    ent_m0 = model_entropy_bits(joint_m0, p_b, prior_mod)
    h_cal = fa[split["heldout_ids"]]
    h_calb = fb[split["heldout_ids"]]
    nll_m2 = heldout_nll_bits(joint_m2, h_calb, h_cal, prior_mod)
    nll_m0 = heldout_nll_bits(joint_m0, h_calb, h_cal, prior_mod)
    delta = nll_m0["nll_mean_bits"] - nll_m2["nll_mean_bits"]
    gate = eval_nll_gate(delta, float(freeze.get("delta_min", 0.020)))
    elapsed = _time.time() - t0
    _write_json(out_root / "g1.json", {
        "population": REMAINDER_ACQ_ID,
        "scope": "NLL_H_COMPARISON_ONLY",
        "exemptions": ["G1-1_alignment_EXEMPT_frozen_derived_pairs",
                       "delta_tail_200k_EXEMPT_only_25856_pairs_available"],
        "mod": mod,
        "cal_frames": REMAINDER_CAL_FRAMES,
        "heldout_frames": REMAINDER_N_FRAMES - REMAINDER_CAL_FRAMES,
        "m2_triple": {k: (float(v) if isinstance(v, float) else v) for k, v in triple.items()},
        "H_M2_bits": ent_m2,
        "H_M0_bits": ent_m0,
        "NLL_M2_bits": nll_m2,
        "NLL_M0_bits": nll_m0,
        "nll_delta_bits": delta,
        "nll_gate": gate,
        "timing": {"wall_s": elapsed},
    })
    _write_json(out_root / "cal_ids.json", {
        "population": REMAINDER_ACQ_ID,
        "cal_ids": split["cal_ids"],
        "heldout_ids": split["heldout_ids"],
    })
    (out_root / "run_log.md").write_text(
        "# G1 remainder NLL/H check — NLL/H comparison only (exempt population)\n\n"
        f"cal=32 heldout=69 delta_bits={delta:.6f} gate={gate['verdict']} "
        f"wall_s={elapsed:.1f}\n",
        encoding="utf-8",
    )
    print(f"REMAINDER_DONE delta_bits={delta:.6f} gate={gate['verdict']} wall_s={elapsed:.1f}")
    return 0


def run_g1_science(*, acq_id, out_root: Path, freeze, options, _read_timetags=None):
    """Phase-B G1 execution (SHG `_1`; decoder-free; preregistered gates).

    Re-verifies the §6 reproduction gate bit-exact, then G1-1..G1-4:
    alignment record; pairing at W_P (+W_S sensitivity readout, no
    switching); δ-profile linear+circular + δtail gate on CHAR; CAL32
    FIT + matched-CAL held-out NLL + H tables both models + NLL gate.
    Returns 0 with all verdicts recorded (gates are descriptive).
    """
    import time as _time

    t0 = _time.time()
    read = _read_timetags or _read_timetags_production
    window_p = int(freeze["pairing_window_primary"])
    window_s = int(freeze["pairing_window_sensitivity"])
    skip = int(freeze["skip_frames"])
    mod = str(freeze["mod_boundary"])
    char_pairs = int(freeze["char_sample_pairs"])
    B_tail = float(freeze["B_tail"])
    delta_min = float(freeze["delta_min"])
    contract = contract_for_freeze(freeze)
    gate = contract["repro_gate"]
    label = contract["label"]

    got = read(acq_id)
    tA, tB = got["tA"], got["tB"]
    peak = _align_frozen(tA, tB)
    align = {
        "estimator_source": "src/workflow/export_joint_sequence_sidecar.py:715",
        "scan_range_ps": G1_SCAN_RANGE_PS,
        "bin_ps": G1_BIN_PS_ALIGN,
        "peak_center_ps": peak.get("peak_center_ps"),
        "peak_sigma_ps": peak.get("peak_sigma_ps"),
        "peak_to_bg": peak.get("peak_to_bg"),
        "status": peak.get("status"),
        "accept": bool(
            peak.get("status") == "ok"
            and peak.get("peak_to_bg") is not None
            and float(peak.get("peak_to_bg")) >= G1_PEAK_TO_BG_MIN
        ),
        "criterion": "status==ok AND peak_to_bg>=10 (unit-independent)",
    }
    if not align["accept"]:
        _fail(f"{label} ALIGN_FAIL status={align['status']} to_bg={align['peak_to_bg']}")
    offset = int(align["peak_center_ps"])
    sweep = _yield_sweep_selfcheck(tA, tB, offset)
    sweep_ok, sweep["yield_note"] = _sweep_accept(sweep)
    if not sweep_ok:
        _fail(f"{label} ALIGN_INCONSISTENT offset={offset} "
              f"yield@derived={sweep['yield_at_derived']} max={sweep['yield_max']}")

    alice, bob = pair_narrow_nearest_unique(tA, tB, offset, window_p)
    n_pairs = int(alice.size)
    n_frames = n_pairs // G1_FRAME_PAIRS
    repro = {
        "peak_center_ps": align["peak_center_ps"],
        "peak_sigma_ps": align["peak_sigma_ps"],
        "status": align["status"],
        "n_pairs": n_pairs,
        "n_frames": n_frames,
    }
    if not (repro["peak_center_ps"] == gate["peak_center_ps"]
            and repro["peak_sigma_ps"] == gate["peak_sigma_ps"]
            and repro["status"] == gate["status"]
            and repro["n_pairs"] == gate["n_pairs"]
            and repro["n_frames"] == gate["n_frames"]):
        _fail(f"{label} ALIGN_INCONSISTENT reproduction gate mismatch: {repro} != {gate}")

    # W_S sensitivity readout (no switching): counts + δ triple only.
    sens_a, sens_b = pair_narrow_nearest_unique(tA, tB, offset, window_s)
    del tA, tB
    sensitivity = {"window": window_s, "n_pairs": int(sens_a.size),
                   "triple": mod_tail_counts(sens_a, sens_b, mod)}
    del sens_a, sens_b

    frames_a, frames_b, ledger = chunk_frames(alice, bob, skip)
    del alice, bob
    try:
        segments = segment_frame_lists(ledger["complete_frames"])
    except _InsufficientFrames as exc:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "verdict": "INSUFFICIENT",
                     "align": align, "ledger": ledger, "detail": str(exc)})
        print(f"{label}_INSUFFICIENT {exc}", file=sys.stderr)
        return 1
    named = {name: segments[name] for name, _, _ in SEG_RANGES}
    matrix = disjointness_matrix(
        {k: v for k, v in
         [("a1_cal", named["a1_cal"]), ("cal32", named["cal32"]),
          ("char", named["char"]), ("heldout", named["heldout"]),
          ("eval", named["eval"])]}
    )
    if not matrix["all_disjoint"]:
        _fail(f"{label} segment overlap invalidates run: {matrix['pairwise_overlap']}")

    char_a = frames_a[named["char"]].ravel()
    char_b = frames_b[named["char"]].ravel()
    if int(char_a.size) != char_pairs:
        _fail(f"CHAR sample {int(char_a.size)} != frozen char_sample_pairs {char_pairs}")
    prof = delta_profile(char_a, char_b)
    tail = mod_tail_counts(char_a, char_b, mod)
    dtail_gate = eval_delta_tail(tail["n_tail"], tail["n_total"], B_tail)

    m2_mod = _frozen_m2()
    prior_mod = _frozen_prior()
    cal_a = frames_a[named["cal32"]].ravel()
    cal_b = frames_b[named["cal32"]].ravel()
    counts = build_counts_1024(cal_a, cal_b)
    triple = m2_mod.fit_m2_triple(counts, mod=mod)
    joint_m2 = m2_mod.build_m2_joint(triple["q0"], triple["q_plus1"], triple["q_minus1"], mod=mod)
    joint_m0 = m2_mod.build_m0_joint(counts)
    n_cal = float(counts.sum())
    p_b = counts.sum(axis=0) / n_cal
    ent_m2 = model_entropy_bits(joint_m2, p_b, prior_mod)
    ent_m0 = model_entropy_bits(joint_m0, p_b, prior_mod)
    h_a = frames_a[named["heldout"]]
    h_b = frames_b[named["heldout"]]
    del frames_a, frames_b
    nll_m2 = heldout_nll_bits(joint_m2, h_b, h_a, prior_mod)
    nll_m0 = heldout_nll_bits(joint_m0, h_b, h_a, prior_mod)
    delta = nll_m0["nll_mean_bits"] - nll_m2["nll_mean_bits"]
    nll_gate = eval_nll_gate(delta, delta_min)
    elapsed = _time.time() - t0

    _write_json(out_root / "g1.json", {
        "packet": contract["packet"],
        "mode": contract["science_mode"],
        "acq_id": acq_id,
        "nature": "DESCRIPTIVE/NON-CLAIM, decoder-free; M2 CANDIDATE, never baseline",
        "align": align,
        "yield_sweep": sweep,
        "offset_applied_to_alice": offset,
        "offset_sign_convention": "tA_aligned = tA_raw + peak_center_ps",
        "pairing": {"rule": "(N) narrow nearest-unique", "window_primary": window_p,
                    "n_pairs": n_pairs, "n_frames": n_frames,
                    "sensitivity": sensitivity,
                    "frozen": {"d": G1_D, "bin_width_ps": G1_BIN_WIDTH_PS,
                               "period_ps": G1_PERIOD_PS, "frame_pairs": G1_FRAME_PAIRS}},
        "reproduction_gate": {"expected": dict(gate), "observed": repro,
                              "match5": True, "verdict": "REPRODUCED"},
        "ledger": ledger,
        "cal": {"n_frames": 32, "n_pairs": int(cal_a.size),
                "m2_triple": {k: (float(v) if isinstance(v, float) else v)
                              for k, v in triple.items()}},
        "H_M2_bits": ent_m2,
        "H_M0_bits": ent_m0,
        "NLL_M2_bits": nll_m2,
        "NLL_M0_bits": nll_m0,
        "nll_delta_bits": delta,
        "gates": {"delta_tail": dtail_gate, "nll": nll_gate},
        "timing": {"wall_s": elapsed, "wall_budget_s": BUDGET_G1_S,
                   "rss_gib_peak_advisory": _peak_rss_gib_advisory(),
                   "rss_budget_gib": BUDGET_RSS_GIB},
    })
    _write_json(out_root / "delta_profiles.json", {
        "acq_id": acq_id, "segment": "char", "n_pairs": int(char_a.size),
        "mod_frozen": mod, "profile": prof,
        "tail_gate": dtail_gate,
        "sensitivity_triple": sensitivity["triple"],
    })
    _write_json(out_root / "cal_ids.json", {
        "acq_id": acq_id, "layout_rule": "g1_freeze.md §4",
        "a1_cal_ids": named["a1_cal"], "cal_frame_ids": named["cal32"],
        "char_frame_ids": named["char"], "heldout_frame_ids": named["heldout"],
        "eval_frame_ids": named["eval"],
        "disjointness_matrix": matrix,
    })
    (out_root / "run_log.md").write_text(
        f"# {label} science run log — {contract['packet']}\n\n"
        f"acq: {acq_id}\n"
        f"reproduction_gate: 5/5 exact\n"
        f"delta_tail: phat={dtail_gate['p_hat']:.3e} U={dtail_gate['U']:.3e} "
        f"B={B_tail:.1e} verdict={dtail_gate['verdict']}\n"
        f"nll: M0={nll_m0['nll_mean_bits']:.6f} M2={nll_m2['nll_mean_bits']:.6f} "
        f"delta={delta:.6f} min={delta_min} verdict={nll_gate['verdict']}\n"
        f"H_M0={ent_m0['H_total_bits']:.6f} H_M2={ent_m2['H_total_bits']:.6f}\n"
        f"wall_s={elapsed:.1f} (budget {BUDGET_G1_S})\n",
        encoding="utf-8",
    )
    if elapsed > BUDGET_G1_S:
        print(f"{label}_BUDGET_EXCEEDED wall_s={elapsed:.1f} > {BUDGET_G1_S}", file=sys.stderr)
        return 1
    if dtail_gate["verdict"] == "FAIL":
        print(f"{label} recorded: delta-tail FAIL ⇒ premise fails on this source; "
              "NOT proceeding toward G2", file=sys.stderr)
    print(f"{label}_DONE acq={acq_id} dtail={dtail_gate['verdict']} nll={nll_gate['verdict']} "
          f"wall_s={elapsed:.1f}")
    return 0


def run_stage_g1_nll(*, acq_id: str, out_root: Path, freeze: dict, options: dict,
                     closure_only: bool = False, _read_timetags=None) -> int:
    """G1 held-out NLL entry (decoder-free; NO decoder call on any path).

    ``closure_only=True`` restricts the body to the Phase-A closure
    (frame ledger + segment lists + packet-dir freeze-config; zero
    NLL/gate science). Otherwise the full Phase-B G1 science runs
    (``remainder_101f`` takes the exempt NLL/H-only remainder path on
    caller-supplied pairs). ``_read_timetags`` is the injectable
    acquisition reader (tests MUST pass an explicit fake; default
    ``None`` selects the production FileReader path).
    """
    if acq_id == REMAINDER_ACQ_ID and not closure_only:
        if _read_timetags is None:
            _fail(
                f"remainder population {acq_id!r}: the frozen derived-pairs "
                "binding belongs to the Phase-B dispatch; refusing to invent "
                "an artifact path (pass pairs explicitly)"
            )
        kwargs = _read_timetags(acq_id)
        return run_remainder_check(out_root=out_root, freeze=freeze, **kwargs)
    if closure_only:
        return run_closure(acq_id=acq_id, out_root=out_root, freeze=freeze,
                           options=options, _read_timetags=_read_timetags)
    return run_g1_science(acq_id=acq_id, out_root=out_root, freeze=freeze,
                          options=options, _read_timetags=_read_timetags)


def run_stage_g2(*, acq_id: str, out_root: Path, freeze: dict, options: dict) -> int:
    """G2 one-shot entry (Stage-1: body pending freeze, packet §6).

    Post-validation Stage-1 behaviour: exit 3 ``STAGE_BODY_PENDING_FREEZE``
    with zero data contact (nothing read, nothing created). The G2 science
    body belongs to a later freeze.
    """
    print(
        "STAGE_BODY_PENDING_FREEZE: Stage G2 decode body belongs to a later freeze "
        f"(packet {STAGE1_PACKET} §6; all validation passed for acq {acq_id}; "
        "zero data contact: nothing read, nothing created)",
        file=sys.stderr,
    )
    return 3


def _selfcheck() -> int:
    """Verify Stage-1 wiring using ONLY pure logic. Touches no data.

    Covers: freeze-config loading + missing-key detection, the
    ``--authorized`` guard, the out-root guards (forbidden trees +
    ``workspace/`` confinement), flag/freeze cross-check, the frozen
    319/6492 K pin, and the exit-3 ``STAGE_BODY_PENDING_FREEZE`` bodies
    (zero data contact). Prints one PASS/FAIL line per check; returns 0
    iff all pass.
    """
    import contextlib
    import io
    import tempfile

    failures: list[str] = []

    def check(name: str, fn) -> None:
        try:
            fn()
        except AssertionError as exc:
            failures.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")
        except Exception as exc:
            failures.append(f"{name}: unexpected {type(exc).__name__}: {exc}")
            print(f"FAIL {name}: unexpected {type(exc).__name__}: {exc}")
        else:
            print(f"PASS {name}")

    print(f"selfcheck: numpy {np.__version__}; required keys: {len(REQUIRED_FREEZE_KEYS)}")

    def _expect_exit2(fn) -> str:
        buf = io.StringIO()
        try:
            with contextlib.redirect_stderr(buf):
                fn()
        except SystemExit as exc:
            assert exc.code == 2, f"exit code {exc.code!r}, want 2"
            return buf.getvalue()
        raise AssertionError("did not exit(2)")

    with tempfile.TemporaryDirectory(prefix="m2skel_selfcheck_") as td:
        tmp = Path(td)
        full = {k: f"value-{k}" for k in REQUIRED_FREEZE_KEYS}

        def t_complete_json_loads() -> None:
            p = tmp / "full.json"
            p.write_text(json.dumps(full), encoding="utf-8")
            got = load_freeze_config(p)
            assert set(REQUIRED_FREEZE_KEYS) <= set(got), "round-trip lost keys"

        def t_missing_two_keys_exit2_lists_exactly() -> None:
            drop = ["delta_min", "tag_master"]
            cfg = {k: v for k, v in full.items() if k not in drop}
            assert _missing_freeze_keys(cfg) == sorted(drop), (
                "pure helper must list exactly the dropped keys"
            )
            p = tmp / "missing2.json"
            p.write_text(json.dumps(cfg), encoding="utf-8")
            err = _expect_exit2(lambda: load_freeze_config(p))
            for k in drop:
                assert k in err, f"{k} not listed in: {err.strip()}"
            for k in REQUIRED_FREEZE_KEYS:
                if k not in drop:
                    assert k not in err, f"unexpected key {k} listed in: {err.strip()}"

        def t_null_counts_as_missing() -> None:
            cfg = dict(full)
            cfg["B_tail"] = None
            assert _missing_freeze_keys(cfg) == ["B_tail"], "explicit null must count as missing"

        def t_missing_file_exit2() -> None:
            err = _expect_exit2(lambda: load_freeze_config(tmp / "nope.json"))
            assert "not found" in err, f"unclear message: {err.strip()}"

        def t_bad_suffix_exit2() -> None:
            p = tmp / "f.txt"
            p.write_text(json.dumps(full), encoding="utf-8")
            err = _expect_exit2(lambda: load_freeze_config(p))
            assert "suffix" in err, f"unclear message: {err.strip()}"

        def t_yaml_branch() -> None:
            import importlib.util

            p = tmp / "f.yaml"
            p.write_text("B_tail: 1\n", encoding="utf-8")
            if importlib.util.find_spec("yaml") is None:
                err = _expect_exit2(lambda: load_freeze_config(p))
                assert "PyYAML" in err, f"unclear message: {err.strip()}"
            else:
                import yaml  # deferred, test-only

                p.write_text(yaml.safe_dump(dict(full)), encoding="utf-8")
                got = load_freeze_config(p)
                assert set(REQUIRED_FREEZE_KEYS) <= set(got), "yaml round-trip lost keys"

        def t_authorized_guard() -> None:
            buf = io.StringIO()
            try:
                with contextlib.redirect_stderr(buf):
                    _require_authorized(False)
            except SystemExit as exc:
                assert exc.code == 2, f"exit code {exc.code!r}, want 2"
            else:
                raise AssertionError("guard did not exit(2) without --authorized")
            assert "--authorized" in buf.getvalue(), "refusal must name --authorized"
            _require_authorized(True)  # must not raise

        def t_out_root_guard() -> None:
            assert _out_root_refusal(_REPO_ROOT / "results" / "x") is not None
            assert _out_root_refusal(_REPO_ROOT / "results") is not None
            assert (
                _out_root_refusal(
                    _REPO_ROOT / "comparison_bench" / "outputs_comparison" / "y"
                )
                is not None
            )
            assert (
                _out_root_refusal(tmp / "workspace" / "m2_prior_validation") is None
            )

        def t_g2_body_still_exit3() -> None:
            target = tmp / "never_created_g2"
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc = run_stage_g2(acq_id="X", out_root=target, freeze=dict(full), options={})
            assert rc == 3, f"run_stage_g2 returned {rc!r}, want 3"
            assert "STAGE_BODY_PENDING_FREEZE" in buf.getvalue(), (
                "run_stage_g2 must name STAGE_BODY_PENDING_FREEZE"
            )
            assert STAGE1_PACKET in buf.getvalue(), (
                "run_stage_g2 must point at the Stage 1 packet"
            )
            assert not target.exists(), "run_stage_g2 created output"

        def t_g1_pure_helpers() -> None:
            import math as _math

            # Framing: skip + chunk + trailing-drop arithmetic.
            n = 3 * 4 + 2
            a = np.arange(n, dtype=np.int64) % 1024
            b = (np.arange(n, dtype=np.int64) * 7) % 1024
            fa, fb, led = chunk_frames(a, b, 1, 4)
            assert led["skip_pairs"] == 4 and led["postskip_pairs"] == n - 4
            assert led["complete_frames"] == (n - 4) // 4
            assert led["dropped_trailing_pairs"] == (n - 4) % 4
            assert fa.shape == (led["complete_frames"], 4)
            try:
                chunk_frames(a, b, 99, 4)
            except ValueError as exc:
                assert "shorter than skip" in str(exc)
            else:
                raise AssertionError("overskip must raise")

            # MOD tail counts: wrap cells are tail under LINEAR_ONLY.
            wa = np.array([5, 6, 0, 1023, 100], dtype=np.int64)
            wb = np.array([5, 5, 1023, 0, 200], dtype=np.int64)
            lin = mod_tail_counts(wa, wb, "LINEAR_ONLY")
            assert (lin["n0"], lin["n_plus"], lin["n_minus"], lin["n_tail"]) == (1, 1, 0, 3), lin
            cir = mod_tail_counts(wa, wb, "CIRCULAR")
            assert (cir["n0"], cir["n_plus"], cir["n_minus"], cir["n_tail"]) == (1, 2, 1, 1), cir
            try:
                mod_tail_counts(wa, wb, "WRAP")
            except ValueError as exc:
                assert "mod must be" in str(exc)
            else:
                raise AssertionError("bad MOD must raise")

            # Delta-tail gate: zero-obs rule-of-three; k=n upper is 1.0 FAIL.
            g0 = eval_delta_tail(0, 200192, 2.0e-4)
            assert g0["U"] == 3.0 / 200192 and g0["verdict"] == "PASS", g0
            assert clopper_pearson_upper(7, 7) == 1.0
            g1 = eval_delta_tail(7, 7, 2.0e-4)
            assert g1["verdict"] == "FAIL", g1
            u = clopper_pearson_upper(1, 10)
            assert 0.1 < u < 1.0, u
            assert clopper_pearson_upper(2, 10) > u, "CP upper must grow with k"
            gn = eval_nll_gate(0.03, 0.020)
            assert gn["verdict"] == "PASS"
            assert eval_nll_gate(0.0, 0.020)["verdict"] == "FAIL"
            assert eval_nll_gate(0.01, 0.020)["verdict"] == "INCONCLUSIVE"

            # Segments + disjointness on the frozen layout size.
            segs = segment_frame_lists(4256)
            assert [len(segs[k]) for k in ("a1_cal", "cal32", "char", "heldout", "eval")] == [
                1024, 32, 782, 560, 1792,
            ], [len(v) for v in segs.values()]
            mx = disjointness_matrix(
                {"a1_cal": segs["a1_cal"], "cal32": segs["cal32"],
                 "char": segs["char"], "heldout": segs["heldout"],
                 "eval": segs["eval"]}
            )
            assert mx["all_disjoint"] and set(mx["pairwise_overlap"]) != set()
            assert len(mx["pairwise_overlap"]) == 10
            bad = disjointness_matrix({"x": [1, 2], "y": [2, 3]})
            assert not bad["all_disjoint"] and bad["pairwise_overlap"] == {"x|y": 1}
            try:
                segment_frame_lists(4189)
            except _InsufficientFrames as exc:
                assert "INSUFFICIENT" in str(exc)
            else:
                raise AssertionError("short ledger must raise _InsufficientFrames")

            # Remainder mini-layout: 32 CAL + 69 held-out covering 101.
            sp = remainder_split_ids()
            assert len(sp["cal_ids"]) == 32 and len(sp["heldout_ids"]) == 69
            assert sp["cal_ids"][-1] + 1 == sp["heldout_ids"][0]
            assert set(sp["cal_ids"]) | set(sp["heldout_ids"]) == set(range(101))

            # Frozen-pairing literal spot check (hand-computed greedy trace).
            pa, pb = pair_narrow_nearest_unique(
                np.array([0, 250, 10000], dtype=np.int64),
                np.array([40, 300, 10060], dtype=np.int64),
                50, 500,
            )
            assert pa.tolist() == [0, 1, 50] and pb.tolist() == [0, 1, 50], (
                pa.tolist(), pb.tolist(),
            )

        def t_closure_only_store_true_ast() -> None:
            import ast as _ast

            tree = _ast.parse(Path(__file__).read_text(encoding="utf-8"))
            found = False
            for node in _ast.walk(tree):
                if isinstance(node, _ast.Call) and getattr(node.func, "attr", "") == "add_argument":
                    names = [
                        a.value
                        for a in node.args
                        if isinstance(a, _ast.Constant) and isinstance(a.value, str)
                    ]
                    kw = {k.arg: k.value for k in node.keywords}
                    action = kw.get("action")
                    if "--closure-only" in names:
                        found = True
                        assert isinstance(action, _ast.Constant) and action.value == "store_true", (
                            "t: --closure-only must be action='store_true'"
                        )
            assert found, "t: --closure-only argument not found"

        def t_cross_check_detects_mismatch() -> None:
            bad = {"window_primary": "501", "mod": "value-mod_boundary"}
            mism = _cross_check_mismatches(bad, dict(full))
            assert len(mism) == 1 and "pairing_window_primary" in mism[0], (
                f"must list exactly the mismatched key: {mism}"
            )
            good = {"window_primary": "value-pairing_window_primary"}
            assert _cross_check_mismatches(good, dict(full)) == [], (
                "matching flags must pass the cross-check"
            )
            listed = {"arms": "value-g2_arms"}
            assert _cross_check_mismatches(listed, dict(full)) == [], (
                "matching flags must pass the cross-check"
            )
            assert _norm_crosscheck(["A1", "A2", "B"]) == _norm_crosscheck("A1,A2,B"), (
                "freeze-list vs CLI-spelling arms must normalize equal"
            )

        def t_k_pin() -> None:
            _check_k_pin("319", "6492")  # must not raise
            _check_k_pin(None, None)  # absent flags are unchecked
            err = _expect_exit2(lambda: _check_k_pin("320", "6492"))
            assert "319" in err, f"k-pin refusal must name 319: {err.strip()}"

        def t_workspace_confinement() -> None:
            assert (
                _out_root_workspace_refusal(
                    _REPO_ROOT / "workspace" / "m2_prior_validation"
                )
                is None
            )
            outside = tmp / "ws_outside_probe"
            # tmp itself is a system temp dir here (outside repo workspace):
            assert _out_root_workspace_refusal(outside) is not None, (
                "system-temp roots must be refused (Stage-1 allows workspace/ only)"
            )

        def t_contracts_g1_g1r2() -> None:
            # Explicit window-keyed selection: 500 -> G1 legacy literals,
            # 200 -> G1R2 successor; anything else exits 2 (never a
            # default, never data-inferred).
            g1c = contract_for_window(500)
            assert g1c["repro_gate"] is REPRO_GATE, "G1 contract must keep the legacy gate object"
            assert g1c["repro_gate"]["n_pairs"] == 1269268, g1c["repro_gate"]
            assert g1c["repro_gate"]["n_frames"] == 4958, g1c["repro_gate"]
            assert g1c["packet_dir"] == G1_PACKET_DIR, g1c["packet_dir"]
            assert g1c["config_name"] == "g1_freeze_config.json", g1c["config_name"]
            assert g1c["label"] == "G1", g1c["label"]
            r2c = contract_for_window("200")
            assert r2c["repro_gate"]["n_pairs"] == 1259992, r2c["repro_gate"]
            assert r2c["repro_gate"]["n_frames"] == 4921, r2c["repro_gate"]
            assert r2c["packet_dir"] == G1R2_PACKET_DIR, r2c["packet_dir"]
            assert r2c["config_name"] == "g1r2_freeze_config.json", r2c["config_name"]
            assert r2c["label"] == "G1R2", r2c["label"]
            # Alignment literals stay shared across both contracts.
            for cc in (g1c, r2c):
                assert cc["repro_gate"]["peak_center_ps"] == 50, cc
                assert cc["repro_gate"]["peak_sigma_ps"] == 112.45189572400645, cc
                assert cc["repro_gate"]["status"] == "ok", cc
            # Ledger-driven reserve: G1 ledger -> legacy 4190-4255 range;
            # G1R2 ledger -> 4190-4218 (never 4219+); empty + note below
            # the allocation (never invented ids).
            assert reserve_ids_for_ledger(4256)["ids"] == list(range(4190, 4256)), (
                "G1 ledger must reproduce the legacy SEG_RESERVE range"
            )
            r200 = reserve_ids_for_ledger(4219)
            assert r200["ids"] == list(range(4190, 4219)) and r200["note"] == "", r200
            assert r200["ids"][-1] == 4218 and all(i < 4219 for i in r200["ids"])
            rempty = reserve_ids_for_ledger(4190)
            assert rempty["ids"] == [] and "never invented" in rempty["note"], rempty
            err = _expect_exit2(lambda: contract_for_window(300))
            assert "no science contract" in err, f"unclear message: {err.strip()}"
            err = _expect_exit2(lambda: contract_for_freeze({}))
            assert "no science contract" in err, f"unclear message: {err.strip()}"

        for name, fn in [
            ("complete-json-loads", t_complete_json_loads),
            ("missing-two-keys-exit2-lists-exactly", t_missing_two_keys_exit2_lists_exactly),
            ("null-counts-as-missing", t_null_counts_as_missing),
            ("missing-file-exit2", t_missing_file_exit2),
            ("bad-suffix-exit2", t_bad_suffix_exit2),
            ("yaml-branch", t_yaml_branch),
            ("authorized-guard", t_authorized_guard),
            ("out-root-guard", t_out_root_guard),
            ("stage-g2-body-exit3-pending-freeze", t_g2_body_still_exit3),
            ("g1-pure-helpers", t_g1_pure_helpers),
            ("closure-only-store-true", t_closure_only_store_true_ast),
            ("cross-check-detects-mismatch", t_cross_check_detects_mismatch),
            ("k-pin-319-6492", t_k_pin),
            ("contracts-g1-g1r2", t_contracts_g1_g1r2),
            ("workspace-confinement", t_workspace_confinement),
        ]:
            check(name, fn)

    if failures:
        print(f"SELFCHECK_FAIL {len(failures)} failing check(s)")
        return 1
    print("SELFCHECK_PASS all Stage-1 wiring checks passed (no data touched)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="M2 prior validation runner (Stage-1 guards real; G1 body "
        "decoder-free per g1_freeze.md; G2 body exits 3 STAGE_BODY_PENDING_FREEZE).",
    )
    ap.add_argument(
        FLAG_G1,
        dest="stage_g1",
        action="store_true",
        help="G1 held-out NLL entry (packet §5). Decoder-free: --closure-only "
        "restricts to the Phase-A closure (ledger + lists + freeze-config); "
        "otherwise the full G1 science runs.",
    )
    ap.add_argument(
        FLAG_G2,
        dest="stage_g2",
        action="store_true",
        help="G2 one-shot entry (packet §6). Stage-1 body exits 3 "
        "STAGE_BODY_PENDING_FREEZE with zero data contact.",
    )
    ap.add_argument(
        "--closure-only",
        action="store_true",
        default=False,
        help="G1 Phase-A only: restrict the body to closure outputs (frame "
        "ledger + segment lists + packet-dir freeze-config); zero NLL/gate "
        "science. Applies to --stage-g1-nll only.",
    )
    ap.add_argument(
        "--selfcheck",
        action="store_true",
        help="Verify skeleton wiring (pure logic only; touches no data).",
    )
    ap.add_argument(
        "--authorized",
        action="store_true",
        default=False,
        help="Stage modes run ONLY with --authorized (exits 2 if absent).",
    )
    ap.add_argument(
        "--freeze-config",
        default=None,
        help="JSON/YAML file with all 19 STATUS.yaml to_freeze keys (no defaults).",
    )
    ap.add_argument("--acq-id", default=None, help="Acquisition id (required for stage modes).")
    ap.add_argument("--out-root", default=None, help="Additive output root (required for stage modes).")
    # Descriptive per-stage flags for readability (packet §5/§6 commands);
    # authoritative values come from --freeze-config, never from these alone.
    ap.add_argument("--window-primary", default=None)
    ap.add_argument("--window-sensitivity", default=None)
    ap.add_argument("--skip", default=None)
    ap.add_argument("--mod", default=None)
    ap.add_argument("--char-pairs", default=None)
    ap.add_argument("--arms", default=None)
    ap.add_argument("--blocks", default=None)
    ap.add_argument("--k1", default=None)
    ap.add_argument("--k2", default=None)
    ap.add_argument("--tag-master", default=None)
    a = ap.parse_args(argv)

    if sum([bool(a.stage_g1), bool(a.stage_g2), bool(a.selfcheck)]) != 1:
        _fail(f"pick exactly one of {FLAG_G1} / {FLAG_G2} / --selfcheck")
    if a.selfcheck:
        return _selfcheck()
    # Authorization BEFORE any freeze-config parsing or file access.
    _require_authorized(bool(a.authorized))
    stage_flag = FLAG_G1 if a.stage_g1 else FLAG_G2
    if not a.freeze_config:
        _fail(f"--freeze-config <path> is required with {stage_flag} (all 19 to_freeze keys; never a default)")
    freeze = load_freeze_config(a.freeze_config)
    if not a.acq_id:
        _fail("--acq-id is required for stage modes")
    if not a.out_root:
        _fail("--out-root is required for stage modes")
    refusal = _out_root_refusal(a.out_root)
    if refusal is not None:
        print(f"ERROR: {refusal}", file=sys.stderr)
        raise SystemExit(2)
    confinement = _out_root_workspace_refusal(a.out_root)
    if confinement is not None:
        print(f"ERROR: {confinement}", file=sys.stderr)
        raise SystemExit(2)
    options = {
        k: getattr(a, k)
        for k in (
            "window_primary",
            "window_sensitivity",
            "skip",
            "mod",
            "char_pairs",
            "arms",
            "blocks",
            "k1",
            "k2",
            "tag_master",
        )
    }
    mismatches = _cross_check_mismatches(options, freeze)
    if mismatches:
        _fail(
            "flag/freeze-config mismatch (freeze file is authoritative, "
            "never an override): " + "; ".join(mismatches)
        )
    _check_k_pin(options.get("k1"), options.get("k2"))
    if a.closure_only and not a.stage_g1:
        _fail("--closure-only applies to --stage-g1-nll only")
    if a.stage_g1:
        return run_stage_g1_nll(
            acq_id=a.acq_id, out_root=Path(a.out_root), freeze=freeze, options=options,
            closure_only=bool(a.closure_only),
        )
    return run_stage_g2(
        acq_id=a.acq_id, out_root=Path(a.out_root), freeze=freeze, options=options
    )


if __name__ == "__main__":
    raise SystemExit(main())
