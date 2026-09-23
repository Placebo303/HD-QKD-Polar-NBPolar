# TASK PACKET AMENDMENT 3 — NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER (2026-09-23, main thread)

**Trigger:** the dispatched run STOPPED at gate G3 with zero writes (operator discipline
correct): `GATE-FAIL: G3 smoke arm-U q=4: FER=1.0`. Root cause is a **packet design
defect, not an execution defect**: `log P_U(y|x') = log(1/q)` is constant in both `y`
and `x'`, so the uniform arm is an information-free (blind) decoder — every information
decision is an exact tie, `argmax` picks 0, and block success requires an all-zero
message (probability q^-K = 4^-38 at R=0.30). FER = 1.0 is deterministic. Any fix
redefines F4/G3, which the operator is forbidden to do — hence the STOP. No new
authorization is needed (same verbatim full-suite instruction, recorded in STATUS.yaml);
this amendment is the recorded main-thread freeze correction.

## Amendment (binding)

**Arm U is redefined from "uniform initial messages" to the NON-DEGENERATE no-injection
baseline: the true-channel belief.**

- **F4-arm-U (replaces `log P_U(y|x') = log(1/q)`):** `log P_U(y|x') = log P_F4(y|x')`
  — the decoder uses the actual synthetic channel instance it faces (the standard
  no-transfer-prior baseline). Rename in artifacts: arm U = "no-injection baseline".
- **F3-arm-I (unchanged):** the frozen G1R2 CAL32 triple verbatim (q0 0.7562, q+1 0.2419,
  q−1 0.0018, remaining q−3 offsets 0) with the frozen floor 1e-15 applied, NOT
  renormalized: `log P_I(y|x') = log(max(p_{δ=(y−x') mod q}, 1e-15))`.
- **Rationale (recorded, superseding design §2's "uniform over the q-ary alphabet" for
  this probe):** at the `sc_decode` interface the initial messages ARE the channel
  likelihoods; a uniform message vector carries zero channel information, so the
  uniform arm is degenerate by construction and the comparison "informed vs uniform"
  would be vacuous (informed beats blind trivially). The non-degenerate, standard
  control is the true-channel belief. The scientific question is preserved in the
  meaningful form: **does injecting the real-data transition structure (the M2 ±1
  finding, with its frozen floor rule) as the decoder's channel belief beat the standard
  no-injection baseline on the same frozen envelope?** The mismatch structure is real
  and informative: arm I's q−1 = 0.0018 vs F4's 0.005, and arm I's floored tail cells
  (1e-15) vs F4's 0.005 uniform tail — i.e. the project's floor-mishandling mechanism is
  part of what is measured. Per design §5, a zero/negative gain is KEPT EVIDENCE.
- **G1b (renamed):** oracle agreement with the true-channel belief (was "uniform prior"):
  ≥200 tiny instances per q, decoded == brute-force MAP, 0 hard mismatches
  (tie-tolerance ≤1e-9, first-divergence semantics as in Step-1).
- **G3 (unchanged):** at R = 0.30 both arms' FER < 0.9 — now a meaningful smoke gate
  (both arms are non-degenerate).
- **Documented degeneracy note (for `notes.md`):** the blind-uniform arm is degenerate by
  construction (FER = 1.0 at probability 1 − q^-K); this is recorded as packet history
  and carries no discriminative information.

## Consumed-run accounting (one-shot integrity)

The dispatched run consumed `s2_runs: 1` and produced ZERO output-root artifacts
(failed at G3, before any measurement arithmetic). Hence no measurement exists to
"rerun" or "tune": the re-dispatch after this amendment is a **fresh packet execution**
under the corrected control definition, not a rerun of any measurement. STATUS counters
keep the consumed run visible: `s2_runs: 1` (gate-failed, zero outputs) and the
re-dispatched run's builder run is recorded with its own counters in `results.json`
(`s2_runs` for the measurement invocation). No screening value was ever produced,
published, or discarded.

## Additional requirement (from the G0 gap)

Step-1's `results.json` does not record the information sets (G0 reference unavailable —
recorded). The Step-2 builder must now record, per (q,R), the recomputed information-set
SUMMARY (K_sym, n_frozen, design-method echo; no digests) in `results.json`, so future
cross-probe verification is possible.

## Continuity

Everything else in `TASK_PACKET.md` holds verbatim: decoder/envelope reuse, channel F4,
seeds/blocks, metric F6, boundary guard F7, budget, write scope, stop rules, acceptance
IDs (S2-2 now covers the amended gates), and the two return conditions.
