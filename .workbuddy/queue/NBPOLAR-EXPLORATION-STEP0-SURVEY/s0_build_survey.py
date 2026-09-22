#!/usr/bin/env python3
"""Step-0 Tier-X channel-survey builder (packet NBPOLAR-EXPLORATION-STEP0-SURVEY).

Stdlib-only core. Reads frozen derived artifacts, writes results.json +
notes.md into the probe root in a single end-of-run write. Any assertion
failure => no output written, exit non-zero (return condition 2).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
M1 = REPO / "workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/delta_profiles.json"
M2 = REPO / "workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/delta_profiles.json"
M6 = REPO / "comparison_bench/outputs_comparison/real_frame_batch.parquet"

N_PAIRS = 200192
ANCHORS = {"linear_m1023": 44, "linear_p1023": 1, "circular_m1": 451,
           "circular_p1": 48832, "circular_tail": 0}


def fail(msg):
    print("ASSERT-FAIL: " + msg, file=sys.stderr)
    sys.exit(1)


def need(cond, msg):
    if not cond:
        fail(msg)


def m6_attempts():
    """Try each available interpreter for a parquet reader; record all outcomes."""
    attempts = []
    candidates = [sys.executable]
    other = shutil.which("python3")
    if other and Path(other).resolve() != Path(sys.executable).resolve():
        candidates.append(other)
    reader = None
    for interp in candidates:
        for lib in ("pyarrow", "pandas"):
            p = subprocess.run([interp, "-c", "import " + lib],
                               capture_output=True, text=True)
            ok = (p.returncode == 0)
            attempts.append({"interpreter": interp, "import": lib,
                             "ok": ok,
                             "reason": None if ok else
                             (p.stderr.strip().splitlines() or ["import failed"])[-1]})
            if ok and interp == sys.executable and reader is None:
                reader = lib
    return attempts, reader


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-root", required=True)
    a = ap.parse_args()
    probe_root = Path(a.probe_root)
    out_results = probe_root / "results.json"
    out_notes = probe_root / "notes.md"

    # ---- M1 (primary) ----
    try:
        m1 = json.loads(M1.read_text())
    except Exception as e:
        fail("M1 unreadable: %s: %s" % (M1, e))
    need(m1.get("mod_frozen") == "CIRCULAR", "M1 mod_frozen != CIRCULAR")
    need(m1.get("n_pairs") == N_PAIRS, "M1 n_pairs != 200192")
    prof = m1.get("profile", {})
    need(isinstance(prof, dict), "M1 missing profile dict")
    lin = prof.get("linear_counts")
    cir = prof.get("circular_counts")
    need(isinstance(lin, list) and len(lin) == 2047,
         "M1 linear_counts len != 2047 (got %s)" %
         (len(lin) if isinstance(lin, list) else type(lin)))
    need(isinstance(cir, list) and len(cir) == 1024,
         "M1 circular_counts len != 1024 (got %s)" %
         (len(cir) if isinstance(cir, list) else type(cir)))
    need(prof.get("linear_offset") == -1023, "M1 linear_offset != -1023")
    need(prof.get("circular_offset") == -512, "M1 circular_offset != -512")
    need(sum(lin) == N_PAIRS, "M1 sum(linear_counts) != 200192")
    need(sum(cir) == N_PAIRS, "M1 sum(circular_counts) != 200192")
    summ = prof.get("summaries", {}).get("CIRCULAR")
    need(isinstance(summ, dict), "M1 missing profile.summaries.CIRCULAR")
    for k in ("n0", "n_plus", "n_minus", "n_tail", "n_total"):
        need(k in summ, "M1 summaries.CIRCULAR missing " + k)
    need(summ["n_total"] == N_PAIRS, "M1 summaries.CIRCULAR.n_total != 200192")

    n0, n_plus, n_minus, n_tail = (summ["n0"], summ["n_plus"],
                                   summ["n_minus"], summ["n_tail"])

    # ---- |D| fold: unsigned residue j = (k mod 1024), |D| = min(j, 1024-j) ----
    abs_hist = [0] * 513
    for i, c in enumerate(cir):
        k = i - 512
        j = k % 1024
        abs_hist[min(j, 1024 - j)] += c
    need(sum(abs_hist) == N_PAIRS, "folded |D| sum != 200192")
    mass_le1 = (cir[513] + cir[511]) / N_PAIRS
    need(abs_hist[1] == cir[513] + cir[511], "|D|=1 fold != circular[513]+circular[511]")

    # ---- period crossing ----
    lin_m1023, lin_p1023 = lin[0], lin[2046]
    n_cross = lin_m1023 + lin_p1023
    rate_cross = n_cross / N_PAIRS

    # ---- wrap closure (VERIFY, never correct) ----
    circ_m1, circ_p1 = cir[511], cir[513]
    chk_m1 = (circ_m1 == lin[1022] + lin[2046])
    chk_p1 = (circ_p1 == lin[1024] + lin[0])
    anchor_match = {
        "linear_m1023_eq_44": lin_m1023 == ANCHORS["linear_m1023"],
        "linear_p1023_eq_1": lin_p1023 == ANCHORS["linear_p1023"],
        "circular_m1_eq_451": circ_m1 == ANCHORS["circular_m1"],
        "circular_p1_eq_48832": circ_p1 == ANCHORS["circular_p1"],
        "circular_tail_eq_0": n_tail == ANCHORS["circular_tail"],
    }

    # ---- M2 context only (NO M1-vs-M2 arithmetic anywhere) ----
    try:
        m2 = json.loads(M2.read_text())
    except Exception as e:
        fail("M2 unreadable: %s: %s" % (M2, e))
    m2lin = m2.get("profile", {}).get("summaries", {}).get("LINEAR_ONLY")
    need(isinstance(m2lin, dict), "M2 missing profile.summaries.LINEAR_ONLY")
    context_m2 = {
        "path": str(M2.relative_to(REPO)),
        "mod_frozen": m2.get("mod_frozen"),
        "n_pairs": m2.get("n_pairs"),
        "summaries_LINEAR_ONLY": {k: m2lin.get(k) for k in
                                  ("n0", "n_plus", "n_minus", "n_tail", "n_total")},
        "note": ("CONTEXT ONLY under the superseded G1 contract "
                 "(W_P=500, LINEAR_ONLY). Never numerically compared to M1; "
                 "no M1-vs-M2 arithmetic performed."),
    }

    # ---- M6 occupancy (conditional; failure => UNMEASURABLE, designed) ----
    attempts, reader = m6_attempts()
    occupancy = {"status": "UNMEASURABLE_FROM_FROZEN_ARTIFACTS",
                 "reason": None, "attempts": attempts, "denominator_n": None}
    if reader is None:
        occupancy["reason"] = ("no parquet reader available: pyarrow/pandas "
                               "import failed under every available interpreter; "
                               "nothing installed (packet forbids installs)")
    else:
        occupancy["reason"] = ("reader present but Phase-A schema/provenance "
                               "check not satisfied or not executed")
        # Phase-A checks would run here in-process via `reader`; any failure
        # keeps status UNMEASURABLE_FROM_FROZEN_ARTIFACTS with the reason above
        # replaced by the exact failing check. No substitute source is used.

    # ---- results (single end-of-run write below; nothing written before) ----
    results = {
        "probe": "NBPOLAR-EXPLORATION-STEP0-SURVEY",
        "tier": "X",
        "question": ("Is the residual channel of the frozen DEVELOPMENT "
                     "population (dominated by adjacent-bin offsets? heavy-tail? "
                     "period-crossing?) of a type where preserving inter-level "
                     "conditional dependence could plausibly matter?"),
        "inputs": {
            "M1": {"id": "M1",
                   "path": str(M1.relative_to(REPO)),
                   "role": "PRIMARY signed-D histograms + summaries + tail gate",
                   "read": True},
            "M2": {"id": "M2",
                   "path": str(M2.relative_to(REPO)),
                   "role": "CONTEXT ONLY (never compared)",
                   "read": True},
            "M3": {"id": "M3",
                   "path": ".workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/G1R2_ADJUDICATION.md",
                   "role": "frozen anchor record (human anchor; not read by builder)",
                   "read": False},
            "M4": {"id": "M4",
                   "path": ".workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/G1_ADJUDICATION.md",
                   "role": "frozen anchor record (human anchor; not read by builder)",
                   "read": False},
            "M5": {"id": "M5",
                   "path": ".workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/S11_ADJUDICATION.md",
                   "role": "frozen Tier-X record (human anchor; not read by builder)",
                   "read": False},
            "M6": {"id": "M6",
                   "path": str(M6.relative_to(REPO)),
                   "role": "CANDIDATE occupancy source (conditional Phase-A check)",
                   "read": False},
        },
        "population": {
            "acq_id": m1.get("acq_id"),
            "segment": m1.get("segment"),
            "n_pairs": N_PAIRS,
            "mod_frozen": m1.get("mod_frozen"),
            "W_P": 200, "MOD": "CIRCULAR", "skip": 702,
            "offset_provenance": ("derived offset +50 ps (G1R2 contract); "
                                  "frozen provenance per prereg, not recomputed"),
        },
        "metrics": {
            "delta_histogram_circular": {
                "offset": -512, "length": 1024, "counts": cir, "sum": sum(cir)},
            "delta_histogram_linear": {
                "offset": -1023, "length": 2047, "counts": lin, "sum": sum(lin)},
            "abs_delta_distribution": {
                "fold": "|D| = min(j, 1024-j) over unsigned residues j = (k mod 1024)",
                "values_0_to_512": abs_hist, "denominator_n_pairs": N_PAIRS,
                "mass_le1": mass_le1,
                "mass_le1_denominator": N_PAIRS,
                "n0": n0, "n_plus": n_plus, "n_minus": n_minus, "n_tail": n_tail,
                "n0_rate": n0 / N_PAIRS, "n_plus_rate": n_plus / N_PAIRS,
                "n_minus_rate": n_minus / N_PAIRS,
                "tail_rate": n_tail / N_PAIRS,
                "rates_denominator": N_PAIRS},
            "period_crossing": {
                "linear_m1023": lin_m1023, "linear_p1023": lin_p1023,
                "n_cross": n_cross, "rate_per_symbol": rate_cross,
                "denominator_n_pairs": N_PAIRS, "period_ps": 204800},
            "wrap_closure_check": {
                "circular_m1": circ_m1, "circular_p1": circ_p1,
                "linear_m1_idx1022": lin[1022], "linear_p1_idx1024": lin[1024],
                "linear_m1023_idx0": lin_m1023, "linear_p1023_idx2046": lin_p1023,
                "check_minus1": chk_m1, "check_plus1": chk_p1,
                "circular_tail": n_tail,
                "frozen_anchors": ANCHORS,
                "frozen_anchor_match": anchor_match},
            "bin_occupancy": occupancy,
        },
        "context_m2_never_compared": context_m2,
        "attestation": {
            "no_fer_object": True, "no_claim": True,
            "ledger": "L3 descriptive -- never cited as L1 FER"},
        "counters": {"s0_runs": 1, "reruns": 0, "rebuilds": 0,
                     "sc_calls_on_protected": 0, "tag_invocations": 0},
        "stop_rules_fired": [
            "stop-rule-3 designed conditional: M6 occupancy := "
            "UNMEASURABLE_FROM_FROZEN_ARTIFACTS (not a blocker; run continued; "
            "no substitute source used)"],
    }

    notes = """# NOTES — NBPOLAR-EXPLORATION-STEP0-SURVEY (Tier-X, non-claim)

- Provenance: M1 `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/delta_profiles.json`
  (acq %s, segment %s, n_pairs 200192, mod CIRCULAR); M2 context-only
  (mod %s). M3-M5 human anchors, not read by this builder. No raw data, no decode,
  no EVAL/RESERVE contact.
- Interpreter policy: `.venv/bin/python` absent; ran under `%s`.
  M6 reader attempts: %s.
- Wrap closure (VERIFY, never correct): circular[-1](idx511)=%d vs linear[-1](1022)=%d + linear[+1023](2046)=%d -> %s;
  circular[+1](idx513)=%d vs linear[+1](1024)=%d + linear[-1023](0)=%d -> %s;
  circular tail=%d. Frozen anchors 44/1/451/48832/tail 0 match: %s.
- Period crossing: n_cross=%d (cells %d + %d), rate=%s per symbol (denominator 200192).
- |D| fold: |D|=min(j,1024-j) over unsigned residues j; mass(|D|=1)=(cir[513]+cir[511])/200192=%s.
  n0=%d n_plus=%d n_minus=%d n_tail=%d (denominator 200192).
- Occupancy: %s (%s).
- Stop rules fired: stop-rule-3 designed conditional only (see results.json); no hard STOP.
- Non-claim: descriptive L3 survey only. No FER, leakage, efficiency, promotion,
  qualification, or key statement of any kind; never merged into or cited as L1 real-data FER.
""" % (m1.get("acq_id"), m1.get("segment"), m2.get("mod_frozen"),
       sys.executable, json.dumps(attempts),
       circ_m1, lin[1022], lin[2046], chk_m1,
       circ_p1, lin[1024], lin[0], chk_p1, n_tail,
       json.dumps(anchor_match),
       n_cross, lin_m1023, lin_p1023, repr(rate_cross), repr(mass_le1),
       n0, n_plus, n_minus, n_tail,
       occupancy["status"], occupancy["reason"])

    probe_root.mkdir(parents=True, exist_ok=True)
    out_results.write_text(json.dumps(results, indent=1) + "\n")
    out_notes.write_text(notes)
    print("WROTE %s %s" % (out_results, out_notes))


if __name__ == "__main__":
    main()
