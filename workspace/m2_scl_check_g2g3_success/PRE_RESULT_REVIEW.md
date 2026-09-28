# PRE-RESULT REVIEW — m2-scl-check-g2g3-success

Reviewer: independent reviewer-go subagent (AGENTS.md §3/§10.3). Scope:
this packet's `results.json`/`EXECUTION_TRANSCRIPT.md`/19 `part_*.json`
plus a read-only cross-check against the predecessor
`workspace/m2_scl_rescue_g2g3/` (Pre-RESULT PASS, commit 326594ca). Only
`PRE_RESULT_REVIEW.md` and `review_scratch/*` were written by this review;
no existing file was modified; no decoder was rerun; no raw `.ttbin` was
read; no git write performed.

**VERDICT: PASS**

## Findings

1. **Independent fidelity recompute (5 fields x 19 blocks)**: re-filtered
   both frozen `per_block_outcomes.jsonl` files myself
   (`arm=="B_M2_32f_candidate"`) and rebuilt each block's `expected` row
   independently (`review_scratch/verify.py`), comparing
   `outcome`/`first_error_coordinate`/`first_error_layer`/`l1_exact`/
   `hard_l2_exact` against each part file's `fidelity.actual`, treating
   `None==None` as equal. Result: 19/19 match, 0 mismatches — identical to
   the reported `fidelity.match=true` on all 19 parts and to
   `results.json["fidelity_compromised"]=false`. All 19 frozen rows do say
   `outcome=="exact"`, confirming the target list is exactly the SC-success
   set it claims to be.
2. **Independent recompute of the 7 rescue fields**: from each part's raw
   `crc_hat`/`crc_true`/`l1_error_symbols_scl`/`l2_error_symbols_scl`, I
   recomputed `crc_pass := crc_hat==crc_true` and
   `label_exact := (l1_error_symbols_scl==0 and l2_error_symbols_scl==0)`
   independently, then `accepted := crc_pass and tag_pass` (reported
   `tag_pass` used as input — raw tag values are not persisted in the part
   JSON, so `tag_pass` itself could not be re-derived from first principles,
   only the formulas downstream of it), `exact := accepted and
   label_exact`, `undetected := accepted and not label_exact`,
   `verify_failed := not accepted`. All 19 blocks: 0 mismatches against the
   reported fields. `exact`/`undetected`/`verify_failed` are mutually
   exclusive and exhaustive on all 19 blocks (sum of the three booleans ==
   1 every time); `undetected` is 0/19 and never merged into `exact` in
   either my recompute or the reported summary.
3. **Summary tally recompute**: my independently-accumulated
   `{n_targets:19, n_fidelity_ok:19, n_fidelity_mismatch:0,
   n_preserved_exact:19, n_broken:0, n_undetected:0,
   n_errors_or_aborts:0}` is byte-identical to `results.json["summary"]`.
   `fidelity_compromised=false` is correct (0 mismatches), so withholding
   the tally never applies here.
4. **Write-scope**: `git status --porcelain` for
   `workspace/m2_scl_check_g2g3_success`, `workspace/m2_scl_rescue_g2g3`,
   `workspace/m2_prior_validation`, and the frozen source trees
   (`src/`, `experiments/`, `tools/`, `comparison_bench/src/`, `scripts/`)
   is empty (this repo's `.gitignore` excludes `workspace/*`, confirmed via
   `git check-ignore -v`, so absence from `git status` is the expected
   signal, not a gap). Predecessor directory file mtimes are all `<=
   2026-09-28 02:33` (its own `STATUS.yaml` edit), none newer than this
   packet's `prereg.md`/launch time — the predecessor's 9 `part_*.json`,
   `results.json`, and `PRE_RESULT_REVIEW.md` are untouched by this run.
   Both `per_block_outcomes.jsonl` files carry Sep 22 mtimes, well before
   this run's 2026-09-28 05:53 UTC launch — not rewritten by this
   execution.
5. **Execution/prereg consistency**: `STATUS.yaml` records
   `reruns: 0`, `attempts: 0` (counted as zero per D1 classification, no
   Tier-Y attempt-budget impact), `exit_code: 0`, one attempt only. Every
   part file's `resources.wall_total_s` and `rss_gib_peak_advisory` are
   within the frozen `budget_wall_s=1200.0`/`budget_rss_gib=2.0` caps
   (checked programmatically, no violations). `results.json["frozen_params"]`
   (`K1=319, K2=6492, N=32768, L=16, top_m=4`, construction digest
   `055c9064...3faea1b`, per-session `tag_master`/`eval_seed`) matches
   `prereg.md`'s frozen values verbatim.

## 6. Merged B-arm 28-block SCL(L=16) tally (predecessor 9 + this packet 19)

Combining this packet's 19 `part_*.json` (preservation-check target set,
SC `outcome=exact`) with the predecessor `workspace/m2_scl_rescue_g2g3/`'s
9 `part_*.json` (rescue target set, SC `verify_failed`) accounts for all
28 B-arm blocks across G2 (14) + G3 (14), with a confirmed-disjoint target
split (no block appears in both packets) — independently recomputed in
`review_scratch/verify.py`:

| Source | Exact | Undetected | Verify_failed | Total |
|---|---|---|---|---|
| G2 | 13 | 0 | 1 | 14 |
| G3 | 14 | 0 | 0 | 14 |
| **Combined** | **27** | **0** | **1** | **28** |

The single broken block is **G2 block 5**, which was `verify_failed` under
SC and remains `verify_failed` under SCL(L=16, top_m=4, CRC-16) in the
predecessor's rescue attempt — i.e. **G2 block 5 fails under both the SC
decode and the SCL-joint re-decode** (it is not one of this packet's 19
targets, since this packet only re-checks blocks that were SC-`exact`; it
surfaces here only via the merged 28-block tally). No `undetected` case
occurred anywhere across all 28 blocks in either packet.

**Permitted descriptive statement** (post-hoc diagnostic; EVAL data for
all 28 blocks was already consumed by the frozen G2/G3 SC decode runs
before either SCL packet existed; SCL(L=16, top_m=4, CRC-16) is not part
of the frozen operational decode contract for this arm):

> Applying the SCL-joint (L=16, top_m=4, CRC-16-aided) decoder
> descriptively to all 28 already-decoded B-arm (`B_M2_32f_candidate`)
> EVAL blocks from the G2/G3 real-data sessions — reusing the frozen SC
> outcomes for classification rather than drawing any new EVAL data —
> yields 27/28 blocks exact and 1/28 (G2 block 5) `verify_failed` under
> SCL, with 0 `undetected` cases; adding the 16-bit CRC increases the
> descriptive book rate `f_book` by ≈0.0006 (G2: 1.274745→1.275343,
> Δ=0.000598; G3: 1.267507→1.268101, Δ=0.000594) over the no-CRC baseline.
> This is a descriptive count only — SCL is not part of the frozen
> operational decode contract, does not constitute an FER gate, an R2
> decision, or any promotion criterion, and does not change
> `NBPOLAR_M2_PRIOR_G2_SUCCESS`/`NBPOLAR_M2_PRIOR_G3_SUCCESS`/the M2
> status ladder.

## Comments (do not block PASS)

- `tag_pass` itself is taken as given from each part file (raw
  Toeplitz-tag hat/true bit vectors are not persisted, by design, in the
  part JSON schema — same as the predecessor), so this review re-derives
  everything downstream of `tag_pass` (accepted/exact/undetected/
  verify_failed) but not `tag_pass` from first principles. This is
  unchanged from the predecessor's own Pre-RESULT review scope and is not
  a new gap introduced by this packet.
- D_NEW1/D_NEW2 (n_broken redefinition; authorization-text update) are
  recorded as main-thread `ACCEPTED` in `STATUS.yaml`; not re-litigated
  here (main-thread decision, outside this review's scope).

## Scope not re-litigated

Decoder correctness of `scl_joint_decode`, the CAL-fit/P16
construction-digest verification mechanism, and the fidelity re-derivation
mechanism (`run_g2_block` reuse) were reviewed at this packet's own
Pre-EXECUTE (PASS) and the predecessor's Pre-EXECUTE
(PASS_WITH_COMMENTS)/Pre-RESULT (PASS); not re-run or re-reviewed here
since no raw `.ttbin` was read and no decoder was invoked by this review.
