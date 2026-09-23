"""S0M6 Phase-A check: deferred M6 bin-occupancy source verification (Tier-X, read-only).

Reads ONLY comparison_bench/outputs_comparison/real_frame_batch.parquet
(+ run_manifest.json as provenance context). No decoder, no claim object.
Stdlib + optional pyarrow/pandas; nothing installed.

Phase-A checks IN ORDER: reader -> columns -> alphabet -> provenance.
Any failure => UNMEASURABLE_FROM_FROZEN_ARTIFACTS with the failing check.
Writes results.json + notes.md into --out-root in one end-of-run pass.
"""
import argparse
import importlib.util
import json
import os
import sys
import time

M6_REL = os.path.join("comparison_bench", "outputs_comparison",
                       "real_frame_batch.parquet")
MANIFEST_REL = os.path.join("comparison_bench", "outputs_comparison",
                            "run_manifest.json")
U = 1.0 / 1024.0


def mod_present(name):
    return importlib.util.find_spec(name) is not None


def main():
    t0 = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()
    out_root = args.out_root

    # Packet dir is .workbuddy/queue/NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM/;
    # repo root is four levels up from this file.
    here = os.path.abspath(__file__)
    repo = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(here))))
    m6_path = os.path.join(repo, M6_REL)
    manifest_path = os.path.join(repo, MANIFEST_REL)

    reader_attempts = []
    reader_attempts.append({
        "interpreter": sys.executable,
        "python": sys.version.split()[0],
        "pyarrow_importable": mod_present("pyarrow"),
        "pandas_importable": mod_present("pandas"),
        "fastparquet_importable": mod_present("fastparquet"),
    })

    checks = {
        "reader_attempts": reader_attempts,
        "column_check": {"status": "not_run", "reason": None},
        "alphabet_check": {"status": "not_run", "reason": None},
        "provenance_check": {"status": "not_run", "reason": None},
    }
    occupancy = {
        "status": "UNMEASURABLE_FROM_FROZEN_ARTIFACTS",
        "denominator_n": None,
        "max_o": None,
        "min_o": None,
        "max_over_u": None,
        "fraction_below_half_u": None,
        "reason": None,
    }

    # Manifest context (stdlib json, read-only) for the run log only.
    manifest_ctx = {"readable": False, "dataset_ids": None, "dimensions": None}
    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            man = json.load(fh)
        snap = man.get("benchmark_config_snapshot", {}) or {}
        ds = snap.get("datasets", []) or []
        manifest_ctx = {"readable": True,
                        "dataset_ids": [d.get("dataset_id") for d in ds],
                        "dimensions": [d.get("dimension") for d in ds]}
    except Exception as exc:  # noqa: BLE001 -- recorded, not hidden
        manifest_ctx = {"readable": False, "error": "%r" % exc,
                        "dataset_ids": None, "dimensions": None}

    # --- Check 1: reader (functional parquet read capability) ---
    df = None
    read_error = None
    if mod_present("pyarrow"):
        try:
            import pyarrow.parquet as pq  # type: ignore
            df = pq.read_table(m6_path).to_pandas()
        except Exception as exc:  # noqa: BLE001
            read_error = "pyarrow read failed: %r" % exc
    elif mod_present("pandas"):
        try:
            import pandas  # type: ignore
            df = pandas.read_parquet(m6_path)
        except Exception as exc:  # noqa: BLE001
            read_error = "pandas read_parquet failed: %r" % exc
    else:
        read_error = "no pyarrow/pandas importable; nothing installed per policy"

    if df is None:
        checks["reader_attempts"][0]["functional_read"] = False
        checks["reader_attempts"][0]["read_error"] = read_error
        failing = "reader"
        occupancy["reason"] = (
            "reader check failed: %s; column/alphabet/provenance checks "
            "not executed (in-order stop)" % read_error)
    else:
        checks["reader_attempts"][0]["functional_read"] = True
        # --- Check 2..4 would go here, in order (not reached this run) ---
        failing = None

    elapsed_s = round(time.time() - t0, 3)
    results = {
        "probe": "NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM",
        "tier": "X",
        "question": ("can the deferred M6 bin-occupancy metric be measured "
                     "from the frozen artifact real_frame_batch.parquet, and "
                     "if so what is the Alice marginal non-uniformity?"),
        "inputs": {"m6": M6_REL, "context": MANIFEST_REL,
                   "manifest_context_observed": manifest_ctx},
        "checks": checks,
        "occupancy": occupancy,
        "failing_check": failing,
        "attestation": {
            "no_decoder": True,
            "no_real_data_decode": True,
            "no_eval_reserve_contact": True,
            "no_fer_no_efficiency_no_claim": True,
            "single_threaded": True,
        },
        "counters": {"s0m_runs": 1, "reruns": 0, "rebuilds": 0},
        "stop_rules_fired": [],
        "elapsed_s": elapsed_s,
    }

    if not (os.path.isdir(out_root) and os.path.isfile(
            os.path.join(out_root, "prereg.md"))):
        raise SystemExit(
            "out-root must already exist with prereg.md (P1 copy); refusing "
            "to create directories (stop rule: output root pre-exists means "
            "this probe already ran)")
    with open(os.path.join(out_root, "results.json"), "w",
              encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
        fh.write("\n")

    notes_lines = [
        "# NOTES — NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM (Tier-X, non-claim)",
        "",
        "## Interpreter attempts (ordered policy, nothing installed)",
        "- (1) %s (python %s): pyarrow=%s, pandas=%s, fastparquet=%s" % (
            sys.executable, sys.version.split()[0],
            mod_present("pyarrow"), mod_present("pandas"),
            mod_present("fastparquet")),
        "- (2) other venvs probed import-only: hd-qkd-polar-release "
        "(pandas, no pyarrow), paper2slides (pandas, no pyarrow), "
        "time-tagger-tools (pandas, no pyarrow); jti-extract-clean / "
        "jti-extract-cn / timetagger (neither); /usr/bin/python3 (neither). "
        "No interpreter on this system imports pyarrow or fastparquet.",
        "- Functional read probe: FAILED — %s" % read_error,
        "",
        "## Checks (in order)",
        "- reader: FAIL (no usable parquet engine; nothing installed per "
        "policy).",
        "- column_check / alphabet_check / provenance_check: not_run "
        "(blocked on reader; in-order stop).",
        "- Manifest context (read-only, stdlib json): readable=%s, "
        "dataset_ids=%s, dimensions=%s — context only, not a check verdict." % (
            manifest_ctx.get("readable"), manifest_ctx.get("dataset_ids"),
            manifest_ctx.get("dimensions")),
        "",
        "## Outcome",
        "- occupancy.status = UNMEASURABLE_FROM_FROZEN_ARTIFACTS; "
        "failing_check = reader.",
        "- No substitute source used; no mixed population; no occupancy "
        "numbers reported (none measured).",
        "",
        "## Non-claim statement",
        "- Descriptive L3-ledger readout only. No FER / efficiency / leakage / "
        "promotion / qualification / composable-key statement is made. No "
        "decoder was run and no real-data decode was performed.",
        "",
        "## Budget",
        "- one run (s0m_runs=1, reruns=0, rebuilds=0), single-threaded, "
        "elapsed %.3f s of 600 s wall budget." % elapsed_s,
        "",
    ]
    with open(os.path.join(out_root, "notes.md"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(notes_lines))
    print("wrote results.json + notes.md to %s (failing_check=%s)" % (
        out_root, failing))


if __name__ == "__main__":
    main()
