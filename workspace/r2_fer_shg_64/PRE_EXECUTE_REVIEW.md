# Pre-EXECUTE Review — r2-fer-shg-64

Reviewer: independent reviewer-go subagent (AGENTS.md §3/§10.3/§5.8).
Date: 2026-09-28. Scope: `workspace/r2_fer_shg_64/` (run.py, TASK_PACKET.md,
prereg.md, STATUS.yaml, AUTHORIZATION_PROMPT.md). No execution, no decoder
run, no raw `.ttbin` read, no git write performed by this review.

## Verdict: **FAIL**

One blocking correctness defect (F1) found in `run.py`'s taxonomy
aggregation. It can concretely corrupt the primary claim-bearing output
(`D`, the pooled/per-stratum taxonomy counts, and the resource_abort
isolation invariant) under a plausible one-shot execution condition. Per
AGENTS.md §3, this blocks execution until fixed and re-reviewed.

---

## Findings

### F1 — BLOCKING: `resource_abort_wall_post_scl` blocks double-count into `D`

`_run_one_block_entry` (run.py:615-624): when a block's SCL decode
completes but total elapsed wall exceeds `BUDGET_WALL_S_PER_BLOCK`
*after* `_scl_call` returns, the code sets `status =
"resource_abort_wall_post_scl"` but **does not clear `scl`** — the fully
populated SCL result dict (`exact`/`verify_failed`/`decode_failed`/
`undetected`) is still written into the part file's `"scl"` field.

`_taxonomy_counts` (run.py:751-776) then computes:
```
exact         = sum(... if b.get("scl") and b["scl"]["exact"])
verify_failed = sum(... if b.get("scl") and b["scl"]["verify_failed"])
decode_failed = sum(... if b.get("scl") and b["scl"]["decode_failed"])
undetected    = sum(... if b.get("scl") and b["scl"]["undetected"])
resource_abort = sum(... if "resource_abort" in str(b["status"]))
```
These are independent, non-exclusive predicates. A block with
`status="resource_abort_wall_post_scl"` and, say, `scl["exact"]=True` is
counted **both** in `exact` (hence in `D = exact+verify_failed+
decode_failed`) **and** in `resource_abort`. This directly violates the
frozen invariant stated identically in `prereg.md` §(output), the T6
skeleton §5 step 2 ("`D` ... excludes `undetected` and `resource_abort`"),
and `AUTHORIZATION_PROMPT.md` §D.2/E ("`undetected`/`resource_abort`
isolated ... never merged into `D` or the numerator").

All *other* abort paths are safe: `STOPPED_FIDELITY_MISMATCH` and
`resource_abort_wall_pre_scl` leave `scl=None` (never reached the SCL
call); the parent-side `resource_abort_wall_hard_terminate` /
`resource_abort_total_wall_budget_not_started` records are built by
`_resource_abort_record`, which explicitly sets `"scl": None`. Only the
in-worker post-SCL overrun path leaks a populated `scl` dict under a
non-`"ok"` status.

Likelihood: SCL(L=16) empirical cost is ~600s/block vs. the proposed
1200s/block budget (2x headroom), so this is not the common case, but it
is not negligible either — 64 blocks, 8-way parallel (contention can slow
individual workers), one-shot with `reruns=0`. This is exactly the kind
of edge case a Tier-Y one-shot claim-bearing measurement must handle
correctly the first time, per AGENTS.md §3's Pre-EXECUTE bar ("can
concretely cause a wrong numerical/scientific conclusion").

**Minimum fix**: gate the four `_taxonomy_counts` sums (and, for
consistency, `fidelity_mismatch`/`resource_abort`/`error` should remain
status-driven as they are) on `b["status"] == "ok"` in addition to
`b.get("scl")`, e.g.:
```python
def _counted(b):
    return b["status"] == "ok" and b.get("scl") is not None
exact = sum(1 for b in blocks if _counted(b) and b["scl"]["exact"])
verify_failed = sum(1 for b in blocks if _counted(b) and b["scl"]["verify_failed"])
decode_failed = sum(1 for b in blocks if _counted(b) and b["scl"]["decode_failed"])
undetected = sum(1 for b in blocks if _counted(b) and b["scl"]["undetected"])
```
This keeps the raw `scl` result in the part file for diagnostic/audit
purposes (no information lost) while restoring mutual exclusivity between
the five-way taxonomy and `resource_abort`. No other line needs to
change; this is a same-scope, same-contract correction, not a redefinition.

---

## Items checked and PASS (no other defect found)

1. **Branch/cleanliness**: `git status --porcelain` on `comparison_bench/src/`,
   `scripts/m2_prior_validation.py`, `src/` is empty — protected code
   untouched. Branch is `codex/nbpolar-phase0`, matches STATUS.yaml.
2. **Frozen inputs**: M2/CAL32 (`fit_g2_arm("B_M2_32f_candidate", ...,
   "CIRCULAR", ...)`), SCL params (`LIST_WIDTH_L=16`, `TOP_M=4`), K1=319/
   K2=6492 (`mod.G2_K1`/`G2_K2`), P16 digest
   `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
   (`mod.G2_CONSTRUCTION_DIGEST`, verified by direct read of
   `scripts/m2_prior_validation.py:429-431`), W_P=200/W_S=500/CIRCULAR/
   skip=702 (`pair_narrow_nearest_unique(..., 200)`, `chunk_frames(...,
   702)`) — all match TASK_PACKET/prereg/T6/AUTHORIZATION_PROMPT verbatim.
   `R2_TAG_MASTER=2026102801`/`R2_EVAL_SEED=2026092801` match
   `T6_PACKET_SKELETON_20260928.md` §2 and the corresponding
   `docs/decision-log.md` citation.
3. **64-block layout** (independently recomputed in
   `review_scratch/verify_blocks_and_wilson.py`, pure arithmetic, no data
   read — script run, output captured below): 8 `A1_CAL_characterization`
   (0–1023) + 10-block CHAR/HELDOUT band (1056–2335, remainder 2336–2397
   unused) split into 6 `never_decoded` (1056–1823) + 4
   `heldout_model_selection` (1824–2335, first HELDOUT frame 1838 falls in
   the 1824–1951 block, confirming the "any-HELDOUT-frame-in-block" rule
   against `run.py`'s `e >= HELDOUT_FIRST=1838` test) + 14
   `EVAL_already_decoded` (2398–4189) = 32/session, 64 pooled.
   `stratum_task` totals (14 never_decoded / 4 heldout_model_selection / 14
   previously_decoded_eval per session) match `run.py`'s own runtime
   assertion and `DATA_LEDGER.md` §7. CAL32 (1024–1055) excluded
   throughout, never in any band. Matches DATA_LEDGER.md §1/§2/§7 and T6 §3
   exactly.
4. **Seed scheme**: `global_block_index` 0–63 (G2 offset 0, G3 offset 32)
   is unique per (session, block); `operational_seed_bits(tag_master, n,
   global_block_index, ...)` is the identical call form the predecessor
   used, parameterized only by the new shared master — no redefinition.
5. **Fidelity check scope**: `fidelity_check_applicable=True` only for the
   28 EVAL blocks; the 5-field diff (`outcome`/`first_error_coordinate`/
   `first_error_layer`/`l1_exact`/`hard_l2_exact`) uses `!=` so `None !=
   None` is `False` (null equals null, as required). The 36 never-decoded
   blocks get a purely descriptive SC call, no gate, no STOP. Top-level
   `fidelity_compromised = pooled["fidelity_mismatch"] >= 1` is present
   (main-thread ruling `D_NEW_FIDELITY_SCOPE` correctly implemented: D3
   flag restored, but only the mismatched block itself is excluded from
   the taxonomy tally, not a blanket 64-block withhold).
6. **Taxonomy/statistics** (apart from F1): the five-way taxonomy is
   mutually exclusive and exhaustive at the `_scl_call` level (`decode_failed`
   ⇒ `accepted=False` ⇒ `verify_failed=False`; otherwise exactly one of
   `exact`/`undetected`/`verify_failed` holds) — verified by direct
   reading of the four boolean formulas in `_scl_call` (run.py:531-537).
   `accepted = crc_pass AND tag_pass AND NOT decode_failed` (ruling F1
   inherited, extended). Wilson(z=1.96) arithmetic in `run.py::_wilson`
   independently re-derived and numerically matched in
   `review_scratch/verify_blocks_and_wilson.py` (5 sample points, exact
   match to 1e-9). Output is grouped by `stratum_official` (3 groups),
   `stratum_task` (3 groups), and pooled — all three always present
   together (P-1 compliance). `stop_undetected = pooled["undetected"]>=1`
   present. No verdict string, no PASS/FAIL, no `FER_MEASURED_AT_CONTRACT`
   anywhere in `results.json`'s schema (confirmed by reading `main()`'s
   `results` dict construction end-to-end).
7. **Bookkeeping**: `kdb_with_crc=34135` independently re-derived
   (`5*(319+6492)+64+16 = 34135`, `DISCLOSED_BITS_PER_COORDINATE=5` from
   `two_layer.py:130`, `TAG_BITS=64` from `two_layer.py:133`) — matches
   `prereg.md` P and `AUTHORIZATION_PROMPT.md` §B exactly.
   `h_total_bits`/`H_total` is computed fresh each run via
   `mod.model_entropy_bits(fit["joint"], p_b, prior_mod)` (not hand-filled),
   per AGENTS.md §5.5.
8. **Write scope / one-shot**: `RESULTS_PATH`/`_part_path` both resolve
   under `THIS_DIR = workspace/r2_fer_shg_64/`; `main()` refuses to run
   if `results.json` or any of the 64 `part_*.json` files already exist
   (confirmed absent: `ls` returned "No such file or directory" for both
   globs at review time). `reruns=0`; no rerun logic exists in `run.py`.
9. **Budget**: code constants (`MAX_PARALLEL=8`,
   `BUDGET_WALL_S_PER_BLOCK=1200.0`, `BUDGET_RSS_GIB_PER_BLOCK=2.0`,
   `BUDGET_WALL_S_TOTAL=10800.0`) exactly match the *suggested*
   (non-binding) values in `T6_PACKET_SKELETON_20260928.md` §6 and
   `AUTHORIZATION_PROMPT.md` §C. Correctly flagged `PENDING PI` in
   `STATUS.yaml` (`main_thread_rulings_r2_prep_2026_09_28.D_BUDGET_CONFLICT`)
   — this is expected/correct, not a defect: the currently-`DECIDED`
   D-ACQ-06 (40s/block, SC-based) genuinely conflicts with SCL's ~600s/block
   empirical cost, and the packet correctly does not silently adopt either
   number as `DECIDED`. STOP-on-overbudget-no-tuning is implemented
   (`_launch_all`'s `total_budget_hit` path and per-block hard-terminate at
   `BUDGET_WALL_S_PER_BLOCK + HARD_TERMINATE_MARGIN_S`).
10. **Focused test**: `PYTHONPATH=D:\Code\HD-QKD_Polar_Comparison-nbpolar
    python -m pytest -p no:cacheprovider
    comparison_bench/tests/test_nbpolar_scl_joint.py -q` → **6 passed** in
    56.27s (1 benign pytest-cache-dir config warning, no failures).
    `py_compile workspace/r2_fer_shg_64/run.py` → OK.
11. **Authorization**: `STATUS.yaml.authorizations: []` is expected at this
    stage (PI authorization has not yet been pasted). Per the task
    instructions, both (a) PI's verbatim authorization text and (b) a PASS
    verdict from this review are required before `prereg.md`'s C-line may
    be run. Given F1 above, condition (b) is **not met**; this review's
    verdict is **FAIL**, so execution must not proceed even if (a) arrives
    in the meantime.

---

## review_scratch evidence

`review_scratch/verify_blocks_and_wilson.py` — pure arithmetic, no I/O,
no decoder, no `.ttbin` read. Run output:

```
[block layout] OK: 8 A1_CAL + (6 never_decoded + 4 heldout_model_selection
from the 10-block CHAR/HELDOUT band) + 14 EVAL = 32/session, 64 pooled.
[block layout] stratum_task per session = (never_decoded=14, heldout_model_selection=4, previously_decoded_eval=14)
[wilson] k=0 n=64: p_hat=0.000000 CI=[0.000000,0.056626] (matches run.py._wilson)
[wilson] k=1 n=64: p_hat=0.015625 CI=[0.002763,0.083343] (matches run.py._wilson)
[wilson] k=3 n=28: p_hat=0.107143 CI=[0.037118,0.271962] (matches run.py._wilson)
[wilson] k=5 n=56: p_hat=0.089286 CI=[0.038742,0.192562] (matches run.py._wilson)
[wilson] k=34135 n=34135: p_hat=1.000000 CI=[0.999887,1.000000] (matches run.py._wilson)
[kdb] kdb_no_crc=34119 kdb_with_crc=34135 (matches prereg.md / T6 / AUTHORIZATION_PROMPT.md)
ALL CHECKS PASSED
```

## Required action before re-review

Apply the F1 minimum fix to `_taxonomy_counts` (gate on `status=="ok"`),
re-run `py_compile` and the focused pytest, then request a fresh
Pre-EXECUTE review. No other change is required by this review.
