#!/usr/bin/env python3
"""M2 prior validation runner — SKELETON for NBPOLAR-M2-PRIOR-REALDATA-VALIDATION.

THIS IS A SKELETON. Nothing here is executable science yet: no prior is
fitted, no events are paired, no held-out NLL is scored, and the G2 one-shot
decoder comparison does not run. Each stage body below raises
``NotImplementedError`` naming what Stage 1 must implement and pointing at
the Stage 1 packet
(``.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md``,
CLI CONTRACT block + §5/§6) and the 19 ``to_freeze`` keys in the sibling
``STATUS.yaml``.

Wiring that IS real in this skeleton (verifiable via ``--selfcheck``):

- ``--freeze-config`` loading with all 19 keys required (missing/null is a
  hard error, never a default);
- the ``--authorized`` hard gate for stage modes;
- the out-root guard (additive ``<out-root>/<acq-id>/`` only; never under
  ``results/`` or ``comparison_bench/outputs_comparison/``).

Importing this module reads no files, constructs no model, and opens no
data. All non-stdlib/non-numpy imports (YAML, TimeTagger shim targets,
``src.qkd_io``) are deferred inside functions.
"""

from __future__ import annotations

import argparse
import json
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


def run_stage_g1_nll(*, acq_id: str, out_root: Path, freeze: dict, options: dict) -> int:
    """G1 held-out NLL skeleton (packet §5). Raises ``NotImplementedError``, always."""
    raise NotImplementedError(
        "Stage G1 NLL is a skeleton: implement per-session fit + held-out scoring per "
        f"Stage 1 packet {STAGE1_PACKET} §5 (freeze-config CLI CONTRACT; "
        "run_stage_g1_nll must only create <out-root>/<acq-id>/). "
        "Nothing here is executable science yet."
    )


def run_stage_g2(*, acq_id: str, out_root: Path, freeze: dict, options: dict) -> int:
    """G2 one-shot skeleton (packet §6). Raises ``NotImplementedError``, always."""
    raise NotImplementedError(
        "Stage G2 decode is a skeleton: implement the one-shot A1/A2/B comparison per "
        f"Stage 1 packet {STAGE1_PACKET} §6 (frozen K1/K2, tag master, Wilson gate; "
        "outputs only under <out-root>/<acq-id>/). "
        "Nothing here is executable science yet."
    )


def _selfcheck() -> int:
    """Verify skeleton wiring using ONLY pure logic. Touches no data.

    Covers: freeze-config loading + missing-key detection, the
    ``--authorized`` guard, the out-root guard, and the stage stubs.
    Prints one PASS/FAIL line per check; returns 0 iff all pass.
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

        def t_stubs_raise_not_implemented() -> None:
            for fn in (run_stage_g1_nll, run_stage_g2):
                try:
                    fn(acq_id="X", out_root=tmp, freeze=dict(full), options={})
                except NotImplementedError as exc:
                    assert STAGE1_PACKET in str(exc), "stub must point at the Stage 1 packet"
                else:
                    raise AssertionError(f"{fn.__name__} did not raise NotImplementedError")

        for name, fn in [
            ("complete-json-loads", t_complete_json_loads),
            ("missing-two-keys-exit2-lists-exactly", t_missing_two_keys_exit2_lists_exactly),
            ("null-counts-as-missing", t_null_counts_as_missing),
            ("missing-file-exit2", t_missing_file_exit2),
            ("bad-suffix-exit2", t_bad_suffix_exit2),
            ("yaml-branch", t_yaml_branch),
            ("authorized-guard", t_authorized_guard),
            ("out-root-guard", t_out_root_guard),
            ("stubs-raise-not-implemented", t_stubs_raise_not_implemented),
        ]:
            check(name, fn)

    if failures:
        print(f"SELFCHECK_FAIL {len(failures)} failing check(s)")
        return 1
    print("SELFCHECK_PASS all skeleton wiring checks passed (no data touched)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="M2 prior validation runner (SKELETON — Stage 1 fills in the science)."
    )
    ap.add_argument(
        FLAG_G1,
        dest="stage_g1",
        action="store_true",
        help="G1 held-out NLL skeleton (packet §5). Body raises NotImplementedError.",
    )
    ap.add_argument(
        FLAG_G2,
        dest="stage_g2",
        action="store_true",
        help="G2 one-shot skeleton (packet §6). Body raises NotImplementedError.",
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
    if a.stage_g1:
        return run_stage_g1_nll(
            acq_id=a.acq_id, out_root=Path(a.out_root), freeze=freeze, options=options
        )
    return run_stage_g2(
        acq_id=a.acq_id, out_root=Path(a.out_root), freeze=freeze, options=options
    )


if __name__ == "__main__":
    raise SystemExit(main())
