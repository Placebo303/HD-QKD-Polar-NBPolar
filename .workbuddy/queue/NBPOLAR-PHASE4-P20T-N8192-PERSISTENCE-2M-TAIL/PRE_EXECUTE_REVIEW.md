# Pre-EXECUTE Review — NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL

- Packet: `NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL`
- Date: 2026-09-20
- Reviewer: reviewer-go (independent subagent)
- Session: `ses_f4313eceaffebVIFYfTW0Iz1xj`
- Verdict: **PRE_EXECUTE: PASS**

## Adjudications (13, condensed one line each)

1. Branch/cleanliness: branch `codex/nbpolar-phase0` confirmed; packet scope clean for Stage-B authorization.
2. §3 reuse replay: 2M session-H inputs (recomputed within 1e-12) + worktree `raw_prior_2m.npz` arrays + formula shapes + code paths — no alteration.
3. New N=8192 derivation: 16-block synthetic TRAIN sampling (seeds 2026092410..2413, P16 4×4 pattern) → construction/allocation + fresh L1/L2/spike orders at N=8192.
4. Spike-h reading WITHIN-CONTRACT, no rework: h=TRAIN-pooled h2_mean from the shared 16-block budget, +0/+0 spike genie.
5. D1/D2 replay before DEV: D1-A never invoked; DEV hold 3595..3626 before remainder 3627..3644; 1.5M stubs never used, never pooled.
6. §5 budget/K literals: K via frozen rule floor((1.3·8192·H−64)/5) from recomputed H (≈1760 estimate only); (K1,K2)=(84,1676) by TRAIN residual, never from 334/6746.
7. §4 gate family (a)→(g): all Tier-Y gates frozen, envelope 1200 s / 2 GiB / single thread, one-shot.
8. §2 thin delta: descriptive N=8192 persistence probe, within-N only; no FER/reliability/efficiency/leakage/key-rate/recovery/scaling promotion, no cross-N inference, no H2 input.
9. §7 recorders incl. IR-5 48 KiB/record ir5full-v1 (f32le hazard + u8 inprefix + u8 inu per record; no text-JSON floats; no npz/npy/parquet).
10. Authorization chain/STATUS honesty: `stage_b_authorized`/`decoder_execution_authorized`/`protected_data_read_authorized` false, `attempts_used: 0`, all read counters 0, `pre_result_review`/`main_thread_acceptance` PENDING.
11. Stage-B root absent: `stage_b_out_root: ABSENT`; no protected-data opens, no decoder execution, no Stage-B output created.
12. 23 tests + spot-checks + seed confinement: operator 23/23 accepted structurally; tag master 2026092400 / test seeds 2026092401..2026092407 repo-grep clean; SC stages 13, chunk_rows 128, tag 81983 bits.
13. FROZEN_COMMAND byte-identical, ready-not-executed: derivation program `n8192_persistence_probe_2m:run_derive_stage_a` pinned; nothing Stage-B has run.

## Non-blocking observations (3)

- O1: H last-digit 2.3e-16 difference is display-only rounding; no scientific effect.
- O2: Sibling untracked dirs are out-of-scope for this packet; no action.
- O3: No pytest re-run in this review (static spot-checks only); operator 23/23 accepted structurally.

## Authorization statement

STEP-2 has NOT been given. Nothing Stage-B has run: zero protected opens, zero data contact, zero decoder execution, zero Stage-B outputs, zero commits/pushes. Packet remains `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`; `next_gate: STAGE_B_AUTHORIZATION_AWAITING`.
