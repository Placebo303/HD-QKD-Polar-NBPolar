# DELTA REVIEW RECORD — NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR (delta-successor fast path, AGENTS.md §10.4)

Delta under review: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1r2_delta.md`.
Reviewer: reviewer-go (independent subagent). Branch `codex/nbpolar-phase0` verified. Read-only; no `.ttbin`, no TimeTagger, no decoder. Record persisted by main thread 2026-09-21/22.

## First review — DELTA_FAIL (one blocking finding)

**G (blocking): the runner could not execute the packet without modification**, contradicting the
packet's own R5 premise ("the runner is already G1-capable and must NOT be modified"). Four sites:
(1) `REPRO_GATE` hardcoded w=500 `n_pairs 1269268 / n_frames 4958`, compared bit-exact in both
`run_closure` and `run_g1_science` ⇒ both phases refuse at w=200 (1259992/4921); (2)
`SEG_RESERVE = ("reserve", 4190, 4255)` would emit 37 non-existent frame ids at the w=200 ledger
(4,219); (3) `G1_PACKET_DIR` would destructively overwrite G1's adjudicated config and mislabel
outputs as G1; (4) no `g1r2_freeze_config.json` existed ⇒ Phase-A command exits 2. Consequence:
the packet as first written would have authorized unexecutable work, or (worse) invited a silent
runner edit that contaminated G1's accepted code path.

## Rework applied (main thread + scoped code item; reviewer option (a))

- Delta item **8** added, documenting the runner re-parameterization as an explicit CHANGED item
  (6 → 8 items; item 7 = the reproduction-gate literals).
- Code (`scripts/m2_prior_validation.py`, +189/−41): contract table with `REPRO_GATE_G1R2`
  (1259992/4921; shared alignment 50 / σ 112.45189572400645 / ok), `G1R2_PACKET_DIR`,
  `G1/G1R2_CONFIG_NAME`, `CONTRACTS` (window 500→G1 legacy, 200→G1R2), `contract_for_window`
  (unknown window ⇒ exit 2, never a default), `contract_for_freeze`, `reserve_ids_for_ledger`
  (start 4190, end = ledger−1; empty + recorded note below allocation, never invented ids);
  `_closure_outputs`/`run_closure`/`run_g1_science` contract-driven; new selfcheck
  `contracts-g1-g1r2`; original `REPRO_GATE`/`SEG_RESERVE`/`G1_PACKET_DIR`/`ALLOCATED_FRAMES`
  and `main()`/`__main__` kept verbatim. Selection keyed by `freeze["pairing_window_primary"]`
  only — never data-inferred.
- New `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/g1r2_freeze_config.json` (19 keys,
  0 nulls, explicit int-array frame lists + disjointness matrix).
- New `comparison_bench/tests/test_nbpolar_m2_g1r2_contract.py` (10 tests) + existing G1 file
  unmodified (15/15).

## Re-review — DELTA_PASS_WITH_COMMENTS (authorization may proceed; packet is now executable)

Blocking: none. All four sites fixed and verified; G1 reproducibility preserved (G1 contract gate
`is REPRO_GATE`; legacy reserve 4190–4255 reproduced; `git diff --stat -- .workbuddy/` empty ⇒ G1's
`g1_freeze_config.json` and `G1_ADJUDICATION.md` untouched); w=200 reserve stops at 4218 (never
≥4219, empty+note below allocation); closure routes to the G1R2 dir/config with G1R2 labels;
config 19/19 verified element-wise; mechanics unweakened; fifth-site sweep clean; re-verified
arithmetic (4,219 ledger / trailing 216 / reserve 29 / 16-block deficit 227 / CHAR-shrink deficit
32 / U = 1.4986e-5); no new scientific value (W_P 200, W_S 500, CIRCULAR, tag 2026103001 only).

Non-blocking (batch-fixed by main thread, docs-only): "6 deltas"/"6 CHANGED items" → 8 in
TASK_PACKET/PROMPT/AUTHORIZATION; PROMPT's stale "already G1-capable" clause reworded to
"re-parameterization already applied, do not modify further"; authorization record clarifies that
the runner language refers to the already-applied separately reviewed change, not future operator
edits. Pre-existing unrelated worktree dirt noted, not bundled.
