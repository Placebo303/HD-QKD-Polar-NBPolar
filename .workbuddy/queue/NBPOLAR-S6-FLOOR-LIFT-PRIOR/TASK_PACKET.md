# TASK_PACKET — NBPOLAR-S6-FLOOR-LIFT-PRIOR (`nbpolar_s6_floor_lift_prior`)

Tier-X probe (AGENTS.md §10.4). Preparation-only packet; execution requires
user authorization via `AUTHORIZATION_PROMPT.md`. Non-claim, decoder-free,
zero protected data.

## 1. Question (frozen)

Separate spike suppression from fit quality under a FIXED construction: do
pure floor lifts (1e-6 / 1e-9 / incumbent 1e-15) on the raw-count MLE prior
suppress the S5 spike mass (181 symbols 1p5M / 294 symbols 2M at surprisal >
median+20) WITHOUT Laplace-α1's H1 destruction (0.025 → 4.70)? All variants
keep L1 path, K, and coordinate order identical to the incumbent, so any
difference is attributable to the floor alone — the separation P20N/O/Q
(Laplace + h2_alt 1.44/1.32 construction change) could not provide.

## 2. Preregistration (frozen, params freeze at prereg)

`workspace/probes/nbpolar_s6_floor_lift_prior/prereg.md` (3 lines) is the
preregistration. No post-hoc change to: sessions (1p5M N_CAL=424960, 2M
N_CAL=559872), seed 20260920, split rule (per-cell Binomial(c,0.5), fresh
generator per session, S5 convention), rule list (FLOOR_1e-6, FLOOR_1e-9,
FLOOR_1e-15-incumbent), fixed P16 construction (orders len 32768,
K1=319/K2=6492), K arithmetic (budget literal + H-proportional split,
descriptive-only), rank key ((has_spikes asc, NLL-mean asc, H1-full-mean
asc, rule order 1e-6 < 1e-9 < 1e-15)), exact command.

## 3. Allowed reads (closed list — NOTHING else)

1. `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz`
2. `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz`
3. `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz`
   (counts-equality identity check ONLY; never fit, never score)
4. `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz`
   (same)
5. `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
   (order/K identity ONLY)
6. `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json`
   (presence/identity ONLY)
7. `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json`
   (presence/identity ONLY)
8. `workspace/probes/nbpolar_s6_floor_lift_prior/prereg.md` + `body.py` (own probe)

## 4. Forbidden (STOP conditions — see §10)

- Opening ANY protected segment: `pairs.parquet`, `channel_counts.npz`, any
  file under `comparison_bench/outputs_comparison/`, `results/`, or raw-data roots.
- Running or importing ANY decoder: `sc.py`, anything under `formal_ir/`,
  `comparison_bench/.../nbpolar/`, `src/`, `experiments/`, `tools/` logic.
- Modifying `sc.py`, `formal_ir/nbpolar/`, `src/`, `experiments/`, `tools/`.
- Touching `docs/`, `AGENT_PROJECT_MEMORY.md`, `docs/decision-log.md`, any
  index/ledger (per-probe ledger updates forbidden by §10.4; batched at milestone).
- Writing ANYWHERE outside `workspace/probes/nbpolar_s6_floor_lift_prior/`.
- `git commit` / `git push` (other agents commit concurrently).
- Any λ (lambda) program, Laplace smoothing, Dirichlet-like reweighting, or
  construction/order change (X08 disposition; Laplace out of scope).
- Network/package install/`rm -rf`/large-scale formatting.

## 5. Exact functionality (`body.py`)

Per session (1p5M, 2M): load counts; sanity that FLOOR_1e-15 full-count fit
reproduces stored h1/h2; alt-counts equality check; split via fresh
`default_rng(20260920)` per session with hard assert N_A/N_B equals S5
literals (212904/212056; 280309/279563). Per variant: full-count H1/H2/H_total
(MLE+floor+column renorm); split-A-refit H1/H2; floor cell fraction + B-mass
floor-hit rate; min/max prob; LLR span; B-weighted surprisal median; spike
symbols/cells/fraction over median+20; held-out NLL on B; K_total/K1/K2 at
f=1.3 (budget literal + H-proportional descriptive split) with disclosure
deltas vs session-frozen (1p5M 7020; 2M 7080) and vs P16 operational (6811);
decisive triple (spike_symbols, H1_full, H2_full). Cross-session
mean/sample-std/range per S5 convention. Preregistered recommendation
ranking; explicit no-claim statement. Single write: `results.json` in probe root.

## 6. Acceptance IDs

- **S6-A1** Packet/probe files exist: 4 packet docs here + `prereg.md`/`body.py`
  in probe root; operator recreates NOTHING.
- **S6-A2** `body.py` passes `py_compile`; imports are stdlib+numpy ONLY
  (`json`, `math`, `os`, `numpy`); no `sc`/decoder/`formal_ir`/`comparison_bench` reference.
- **S6-A3** Runtime reads ⊆ §3 allow-list (operator reports the read set; any
  other open = FAIL).
- **S6-A4** Construction identity asserts pass: P16 orders are permutations of
  0..32767, k1=319/k2=6492/n=32768, row 0 disclosed; orders-file presence recorded.
- **S6-A5** `results.json` contains, per variant per session: H1/H2/H_total
  (full + refit), floor-hit rate, LLR span, spike symbols/cells/fraction,
  held-out NLL, K_total/K1/K2 + both disclosure deltas, decisive triple.
- **S6-A6** Split asserts pass exactly (N_A/N_B match S5 literals); split_seed
  recorded as 20260920.
- **S6-A7** `results.json` is the ONLY write, inside the probe root; schema has
  per-source values + mean/sample-std/range; recommendation present under the
  frozen rank key; file contains NO `candidate`/`accepted`/`PASS`/`FAIL` claim
  tokens (the strings `PASS`/`FAIL` must not appear as verdicts).
- **S6-A8** Tier-X counters: `decoder_calls==0`, `protected_reads==0`,
  `rng_calls==2`; no `docs/`/memory/index writes; no `sc.py`/`formal_ir` modification.

## 7. Commands (exact; sibling venv — this checkout has no `.venv`)

- Compile check (preparation already ran; operator re-runs):
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m py_compile workspace/probes/nbpolar_s6_floor_lift_prior/body.py`
- Execution (ONLY after user authorization):
  `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python workspace/probes/nbpolar_s6_floor_lift_prior/body.py`

## 8. Artifacts

- Input: §3 allow-list (7 artifacts + own probe files).
- Output: `workspace/probes/nbpolar_s6_floor_lift_prior/results.json` (ONE file).
- No production output; no ledger/index/memory updates.

## 9. Frozen reference literals (asserted or recorded, never recomputed-into)

- S5: N_A/N_B 212904/212056 (1p5M), 280309/279563 (2M); spike masses 181/294.
- P16 operational: K1=319/K2=6492/K_total=6811, f≈1.3, N=32768.
- Session-frozen: 1p5M 331/6689/7020 (P20M); 2M 334/6746/7080 (P20O).
- Budget literal: `floor((1.3*32768*H_total-64)/5)` clipped [0,65536].

## 10. Stop rules

STOP and report as blocker (with failing command + exact error + attempted
remedies + the SINGLE decision needed from the main thread) if: any §4 item
becomes necessary; any §3 artifact is missing/unreadable; split asserts fail;
construction asserts fail; `results.json` already exists (no-overwrite: stop,
do not overwrite); execution errors persist after one fix attempt (record any
fix-run in `reruns_to_fix_execution_errors`).

## 11. Return conditions (ONLY two)

1. **All-complete**: S6-A1..S6-A8 all satisfied; report files/line counts,
   command, `results.json` top-level keys, per-variant decisive triples,
   recommendation ranking, counters, and confirmation of §4 non-touches.
2. **Concrete blocker**: failing command, exact error/traceback, attempted
   remedies, and the SINGLE decision needed. "Still incomplete" is not a report.

## 12. Pre-EXECUTE note (for the main thread, not the operator)

Claim-bearing/costly execution gates do not apply beyond the frozen Tier-X
checklist: this probe is decoder-free, zero-protected-data, single-write, and
reversible by deletion. Authorization is still required before the §7 execute
command runs. Pre-RESULT review applies to any downstream use of `results.json`.
