# SCOPING_NOTES.md — NBPOLAR-REDUCED-N-PERSISTENCE (no authorization)

- State: `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED` (see `STATUS.yaml`).
  This skeleton proposes the probe; it authorizes nothing.
- Date/authority: planner subagent scoping, 2026-09-20, branch
  `codex/nbpolar-phase0`, workdir
  `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- Main-thread decision (recommend path, option (iv)): SCOPING ONLY — an
  OpenSpec change proposal + freeze design, with NO execution and NO
  contact of the 2M HOLD tail. The probe remains a persistence probe
  (one N=8192 block), never statistical discrimination, and needs its
  own Stage-A/Stage-B authorizations + independent reviews before
  anything runs.

## No data contact occurred

This scoping performed ZERO protected opens: no pairs parquet, no
counts NPZ (not even stat), no prior/alt NPZ content, no `.bin` series
bytes were opened, statted, listed, or read. Inputs were worktree queue
docs, accepted evidence JSON/md scalars, the P16 packet structure
(`construction_and_allocation.json` header fields + `TASK_PACKET.md`),
and the umbrella OpenSpec layout only. Any file-content claim above is
traceable to those reads.

## N=8192 construction/order derivation is future work

The following are NOT done and each requires its own future explicit
authorization (tasks RN-2..RN-7 in the umbrella `tasks.md`, all marked
`[GATE — NOT AUTHORIZED]`): N=8192 construction/allocation derivation
(P16 pattern: TRAIN sampling, pooled risks, worst-first orders,
exhaustive (K1,K2) by TRAIN residual); K derivation via
`floor((1.3·8192·H−64)/5)` from recomputed 2M H (≈1760 estimate only,
never hand-filled); fresh length-8192 L1/L2 orders; fresh length-8192
spike order (F-median8 carried, R=8 re-frozen); new tag domain (fresh
master/prefix + grep proof); new `FROZEN_N = 8192` runner + focused
tests + full-suite green; independent Pre-EXECUTE PASS; separate
Stage-B execution authorization; independent Pre-RESULT review;
main-thread acceptance.

## The 2M HOLD tail 3595..3644 stays never-decoded until then

Ledger restatement (unchanged by this scoping): CONSUMED — 2M VAL
2827..2915 (89) + 2M HOLD 3556..3594 (39) = 128 frames = 1 × N=32768
block (P20S block consumed, R1 attempt spent; both roots immutable).
NEVER-DECODED — 1.5M VAL stub 2172..2212 (41 / 10,496 pr); 1.5M HOLD
2725..2766 (42 / 10,752 pr); 2M HOLD tail 3595..3644 (50 / 12,800 pr);
total 133 fr / 34,048 pr. At N=8192 the 2M tail yields Block R1 =
3595..3626 (32 fr / 8192 pr) + remainder 3627..3644 (18 fr / 4608 pr).
Authorizing a future execution would consume Block R1 irreversibly
(one-shot attempt, no rerun/tuning). Until each gate above is granted,
the full 50-frame tail stays never-decoded and attempts stay 0/1.

## Comparability reminder

Per-N results are NOT comparable across N. Nothing in this skeleton
transfers the 1/4→2/5→4/5 chain, any H2 verdict, the IR-5 32768
geometry, or any leakage literal to N=8192. Valid comparisons are
within-N=8192 only (Q-G1/Q-G2).

(End of file)
