# TASK PACKET — NBPOLAR-M2-PRIOR-G2-DECODE (Tier-Y one-shot three-arm decode, SHG `_1`)

Per AGENTS.md §10.1: one complete frozen packet before delegation. This packet authorizes NOTHING until
verbatim user authorization flips `STATUS.yaml`.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/`
- Freeze (authoritative): `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/g2_freeze.md`
- Parent spec: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md` §6 (G2) + §7 (Pre-RESULT)
- Change: `openspec/changes/nbpolar-prior-rebaseline/` — **T6 (freeze) + T7 (execute)**
- Successor contract inherited: `g1r2_delta.md` (W_P=200 / W_S=500 / MOD=CIRCULAR / skip=702 / tag_master 2026103001 / 14 EVAL blocks)
- Venv: `/home/karel_303/.venvs/timetagger/bin/python`
- Nature: **Tier-Y decision gate.** One-shot: no rerun, no tuning, no seed change. M2 is a CANDIDATE, never the baseline.
  No FER/efficiency/qualification/promotion claim follows under any outcome (G3 deferred).

## Goal

Run the decisive test: at frozen K1=319/K2=6492 with the frozen P16 construction/orders on 14 preregistered SHG `_1` EVAL
blocks, decode three arms (A1 = M0@1024f incumbent as-deployed / A2 = M0@32f prior-form control / B = M2@32f CANDIDATE)
and apply the preregistered Wilson gate. A1 additionally supplies the first-ever SHG measurement of the incumbent.

## Non-Goals

No `sc.py`/algebra/transform change; no construction re-derivation; no K increase or re-split (D4 DEFERRED); no pooled M1;
no G3/SHG `_2`; no FER/efficiency/qualification/promotion claim; no post-freeze threshold/seed/K/window/MOD change;
no rerun/tuning after a verdict.

## Impact Scope

WRITE: `scripts/m2_prior_validation.py` (the `--stage-g2-decode` body — the ONLY code file); new focused tests
(`comparison_bench/tests/test_nbpolar_m2_g2_decode.py`); `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/`
outputs; this packet's `STATUS.yaml` (counters/artifacts/ids only) + `g2_freeze_config.json`.
**Routing (blocking-fix B3):** G2 uses its own packet dir (`NBPOLAR-M2-PRIOR-G2-DECODE`) and config name
`g2_freeze_config.json`, stage-keyed; it SHALL NOT write to any G1/G1R2 packet dir. **Canonical out-root
(blocking-fix B4):** `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/` (matches the `…_g1r2` sibling).
READ: `g2_freeze.md`; parent §6/§7; `formal_ir/nbpolar/{prior,sc,operational_f13,empirical_genie_scaling}.py`;
`formal_ir/prior_m2.py`; P16 `construction_and_allocation.json` (orders + K, digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`); `REAL_DATA_FEASIBILITY_STRATEGY.md`;
`docs/troubleshooting.md` (TimeTagger traps); census/S11/G1R2 artifacts (read-only reference values).
FORBIDDEN (hard stop): modify `sc.py`/`algebra.py`/`transform.py`/`prior_m2.py` or ANY file under `formal_ir/nbpolar/`,
`src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`; read SHG `_2`; write outside scope;
add checksums/atomic writes/locking/retry frameworks (AGENTS.md §5.7).

## Spec 1 — G2 decode body (`scripts/m2_prior_validation.py`, `--stage-g2-decode`)

PRESERVE every Stage-1/G1R2 guard verbatim: `--authorized` store_true (exit 2 before any read/create), `--freeze-config`
19-key enforcement (null/absent ⇒ exit 2 listing keys, never a default), flag↔key cross-checks, K pin 319/6492,
`--out-root` workspace + forbidden-tree confinement, import purity (repo-root `sys.path.insert(0,…)` BEFORE the Swabian
`sys.modules["TimeTagger"]` shim BEFORE any `src.qkd_io` import; `main(argv=None)` + `__main__` guard, no import side effects).
Contract selection stays window-keyed (200 ⇒ G1R2/G2 contract); labels/packet-dir per contract.

Body requirements:
1. Framing identical to G1R2: (N) w=200 pairing at derived offset +50, skip-702, 256-pair frames, MOD CIRCULAR,
   post-skip ledger 4,219; EVAL = post-skip frames 2398–4189 → 14 blocks × 128 frames × 256 = N=32768 pairs per block.
2. Per-arm priors from the arm's own CAL over the SAME frozen framing: A1 from post-skip 0–1023 (8,192·32 = 262,144 pairs);
   A2 and B from post-skip 1024–1055 (8,192 pairs). M0 via `build_m0_joint`; M2 via `fit_m2_triple`→`build_m2_joint`
   (CIRCULAR). Layer factorization via UNCHANGED frozen `derive_p1`/`derive_p2` + `build_p1_metrics`/`gather_p2_metrics`
   + `probs_to_symbol_metric(provenance=PRIOR_ONLY)`.
3. Decode: two-layer causal SC through the accepted chunked `sc_decode` (chunk_rows=512) with frozen P16 `l1_order`/`l2_order`
   and K1=319/K2=6492. Reuse the frozen operational semantics (`operational_f13.run_operational_block` contract) where it
   fits without modification; if a thin G2-side driver is needed, it must import and call, never copy-and-rewrite.
4. Verification: 64-bit Toeplitz tag per block from frozen `tag_master` = 2026103001 (rule EVAL_SEED+10000);
   `exact` = tag_pass AND label_match; `undetected` isolated, never merged.
5. Measurement set per block (§4 of the freeze): `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`, `pair_exact`;
   first-error coordinate AND layer; raw zero-count hits; fixed-floor (1e-15) hits + log loss; true-H-conditioned and
   candidate-H-conditioned L2 NLL; outcome taxonomy; disclosure bits recount; wall/RSS.
6. Gate: per-arm Wilson CI (z=1.96) on exact/14; SUCCESS iff Wilson-lower(B) > Wilson-upper(A2); FAIL iff point(B) ≤
   point(A2); INCONCLUSIVE iff point(B) > point(A2) with overlap. A1 descriptive, no gate.
7. Refusals: `block_formation_fallback` COMPLETE-BLOCKS-ONLY else INSUFFICIENT ⇒ INCONCLUSIVE; never pad/reuse/shrink N.

## Spec 2 — Focused tests (`comparison_bench/tests/test_nbpolar_m2_g2_decode.py`)

Synthetic fixtures + explicit fake runner ONLY (AGENTS.md §10.1 item 8: test-only calls must pass a fake runner —
NEVER invoke the production decode path from tests): freeze-config key enforcement; K pin; contract selection;
block/frame arithmetic (14×128×256); per-arm CAL disjointness enforcement; `undetected` isolation; Wilson arithmetic
against hand-computed values (incl. boundary cases); exit codes 0/2/3; import purity; no modification of frozen files
(`git diff --stat` on `formal_ir/nbpolar/` empty).

## Spec 3 — Phases

**Phase 0 (synthetic, no data):** implement the G2 body + tests per Spec 1–2; suites green.
**Phase A (closure, decoder-free):** re-emit/verify the closure keys (`a1_cal_ids`, `cal_frame_ids`, `heldout_frame_ids`,
`disjointness_matrix`, `block_formation_fallback`) and the complete 19-key `g2_freeze_config.json` under this packet dir,
reusing the G1R2 closure literals (ledger 4,219; reserve 4190–4218).
**Pre-EXECUTE (independent) + user authorization:** recorded BEFORE any decode.
**Phase B (execution):** one-shot three-arm decode + gate; target-output absence verified pre-run.
**Pre-RESULT (independent) before any publication/commit.**

## Acceptance IDs → evidence

`G2-0` (Phase-0 code + tests green) · `G2-A` (closure keys + config + ledger/reserve verification) ·
`G2-1` (freeze + Pre-EXECUTE PASS + pasted authorization recorded before run) ·
`G2-2` (`per_block_outcomes.jsonl`, 14 rows/arm, one-shot) ·
`G2-3` (full measurement set + disclosure bits + wall/RSS + NLL pairs, `undetected` isolated) ·
`G2-4` (no rerun/tuning; pre-run absence check; Wilson CI arithmetic; SUCCESS/FAIL/INCONCLUSIVE) ·
`R1` (Pre-RESULT PASS) · `R2` (main-thread adjudication).

## Exact commands

```
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
cat .git/HEAD  # expect: ref: refs/heads/codex/nbpolar-phase0
# Phase 0 (synthetic; --authorized NOT needed):
/home/karel_303/.venvs/timetagger/bin/python -m pytest comparison_bench/tests/test_nbpolar_m2_g2_decode.py -p no:cacheprovider -q
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --selfcheck
# NOTE: there is NO G2 --closure-only invocation. `--closure-only` applies to --stage-g1-nll only
# (the runner hard-refuses it with --stage-g2-decode) — see freeze blocking-fix B2.
# Phase A builds g2_freeze_config.json by reusing the G1R2 closure literals verbatim; it does not
# invoke the runner. The single G2 command below is Phase B (executed only after Pre-EXECUTE PASS
# + explicit user authorization):
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --freeze-config .workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/g2_freeze_config.json --stage-g2-decode --acq-id 20260113_SHG_Type2PPLN_3s --arms A1_M0_1024f_incumbent,A2_M0_32f_matched,B_M2_32f_candidate --blocks 14 --k1 319 --k2 6492 --tag-master 2026103001 --window-primary 200 --mod CIRCULAR --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2 --authorized
# NOTE (CORRECTION 2026-09-22, blocking-fix S3): `--arms` must use the FULL frozen `g2_arms` spellings
# verbatim; the earlier `A1,A2,B` shorthand (copied from the parent packet's historical command) FAILS the
# runner's verbatim flag<->key cross-check and is withdrawn. The freeze VALUES are unchanged.
```

## Budget + stop rules

Phase B ≤ 900 s wall / 2 GiB RSS single-threaded (parent §9). Exceeded ⇒ STOP + blocker (no tuning to fit).
Any FORBIDDEN touch (SHG `_2`, decoder modification, out-of-scope write) ⇒ STOP + blocker. Reproduction mismatch ⇒ STOP loudly.
Verdict rendered ⇒ no rerun/tuning. Ambiguity ⇒ STOP (second return condition), never guess.

## Return (exactly two)

1. All-complete: per-ID PASS with evidence paths + logs + gate arithmetic + scoped `git status`.
   (Phase 0 + A return with Phase B explicitly NOT run; Phase B dispatched later after Pre-EXECUTE + authorization.)
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision needed.
   "Still incomplete" is not a report.

## Frozen resolutions (report, do not smooth)

R1: G2 is a Tier-Y decision gate — a SUCCESS/FAIL/INCONCLUSIVE verdict is a complete return, not a failure of execution.
R2: K is frozen at 319/6492 for G2 regardless of the D4 question; G1R2's H_M2 = 0.8168138 is a G2 INPUT for later
rate planning, never a license to re-split here.
R3: A1 is the incumbent's first SHG measurement — report it descriptively with no gate; it is not a control for B.
R4: the decoder, algebra/transform, `prior_m2.py` and all of `formal_ir/nbpolar/` are REUSED, never modified for G2.
R5: truncation caveat (w=200 keeps a timing-truncated population) must appear in any rate/efficiency/leakage statement.
R6 (caveat propagation, added 2026-09-22 per review N1): carry both into the G2 record — (a) the census far-offset
accidental baseline is **structured, not uniform** (S11 R4: far-offset tail ≈ 0.40 vs uniform 0.997), so the w=200
accidental estimate (0.0058) must NOT be read as a uniform-accidental level; (b) **q_rest = 0 is a weak statement**
at a 32-frame CAL (zero-observation upper bound 3/8192 = 3.66e-4) — G2 is precisely the test of whether that matters,
so a FAIL/INCONCLUSIVE must not later be misread as "the premise was validated".
R7 (seed provenance, added per blocking-fix B1): `tag_master 2026103001` is INHERITED from G1R2 (value-identical),
not fresh; no tag was ever consumed there (G1R2 decoder-free). Report it that way.
