# AUTHORIZATION — NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION on branch `codex/nbpolar-phase0`
in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/TASK_PACKET.md`.
M2 is a CANDIDATE, never the baseline.

A. Implementation (Stage 1 ONLY — decoder-free, synthetic fixtures + temp roots only):
NEW strict M2 adapter `comparison_bench/src/comparison_bench/formal_ir/prior_m2.py` (beside,
never inside `formal_ir/nbpolar/`) with frozen MOD (`LINEAR_ONLY` default; S8 all-1024-δ fit
SHALL NOT be reused), M0-reproducing switch (P7 raw-MLE-plus-floor rule, bit-exact),
focused tests T1–T11, frozen-`select_empirical_split` re-split path on synthetic fixtures
(real-data numbers diagnostic-only, no K decision; fixed-K vs fixed-f DEFERRED),
`docs/SECURITY_MODEL.md` CAL note + 0-bit inventory skeleton, runner
`scripts/m2_prior_validation.py` with the unified `--freeze-config` interface (all 19
TO-FREEZE keys required, null/absent ⇒ hard error) and `--authorized action="store_true"`.
Acceptance IDs: S1-1..S1-8. Touches nothing under `src/`/`experiments/`/`tools/`/`results/`,
nothing under `formal_ir/nbpolar/`. No protected read, no `.ttbin`, no decoder call, no SHG `_2`
read, no writes outside `workspace/`.

B. Explicitly NOT authorized: G1/G2/G3 execution, any freeze with TO-FREEZE values, any
Pre-EXECUTE/Pre-RESULT gate, any construction re-derivation, any K decision, any claim.

Constraints (binding): forbidden list + stop rules per TASK_PACKET; 300 s wall cap on the
focused suite ⇒ STOP. Reporting: per-ID S1-1..S1-8 PASS with evidence paths + pytest log +
`git status` snippet; or concrete blocker with failing command, exact error, remedies, and
the SINGLE decision needed. No decision-log / memory / index updates in-packet
(milestone batch).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <UTC date> — implementation_authorized: true (Stage 1) / execution_authorized: false (no data/decoder execution under this packet)
