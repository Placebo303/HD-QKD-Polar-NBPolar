# R1 Pre-RESULT review (2026-09-20, independent reviewer-go — PASS 9/9)

Scope: R1 evidence root
`.workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m/`
(15/15 frozen files) vs OPERATOR_RETURN.md claims, DELTA.md §§1–8 identical
freeze, and MAIN_THREAD_ACCEPTANCE.md §§1–4. No re-execution, no
protected-source opens beyond the evidence root. Session
ses_f44c186afffej4IC26000cx8cB.

1. Delta-scope fidelity PASS — the entire code delta is the single
   gate-expression conjunct (`list()` on scalar-int `frame_start` →
   scalar `int()` comparison); population, files, digests, K, arms, caps,
   budgets, formula unchanged per DELTA.md.
2. Integrity-gate conjunction PASS — 36/36 gates TRUE,
   `failing_integrity_gates: []`,
   `blocks_exact_with_declared_remainder` TRUE, non-BLOCKED outcome label
   `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE`.
3. Disclosure accounting PASS — per-arm caps 35464/35464/33794 Δ0
   (actual == full-block), key/public totals 104722/983229, recount
   mismatch 0.
4. `undetected` isolation + oracle exclusion PASS — undetected 0
   (`undetected_count: 0`, `undetected_zero` gate TRUE), O arm
   `deployable: false` / `oracle_control: true`, excluded from
   operational aggregates.
5. D2 judgement-form PASS — geometry/coverage reading only (A exact
   prefix-mean 0.87406; B L2 fail @coord 0, hazard 0.513, IR-2 0.4322,
   outside disclosed prefix, floor 0.3717, prefix-mean 0.87683; O oracle
   exact; A△B 1599/1599); no recovery-rate reading, no H2 verdict.
6. Nine-scalar + IR-1..IR-5 payload PASS — nine per-record scalars present;
   IR-1 masses, IR-3 counts, IR-4 top-16 in-prefix 0, IR-5 uncapped
   full-block series (3×3 bins) with truth isolation
   (`truth_isolation` TRUE, `truth_leak_violation` absent/false).
7. Determinism-ruling factual PASS — 9/9 IR-5 `.bin` byte-identical
   R1-vs-P20S; `per_block_arm_outcomes.jsonl` diff confined to `wall_s` /
   `resources.*`; every scientific/IR/gate/order/tag field identical;
   the telemetry-only ruling is factually verified.
8. One-shot + P20S-immutability PASS — attempts 1/1 consumed, no rerun;
   P20S root 15/15 files untouched (`per_block_arm_outcomes.jsonl`
   sha256 unchanged post-run); R1 writes confined to the new out-root.
9. Honest-scope verbatim PASS — P20S TASK_PACKET.md §0 sentence
   byte-verbatim in OPERATOR_RETURN.md §6.

Non-blocking observations: (1) the jsonl byte diff is run-telemetry
variance (`wall_s`, RSS/VM counters), not scientific content;
(2) wall/RSS values are expected to vary across runs and carry no
evidentiary weight; (3) future delta successors should freeze-exclude
`wall_s`/`resources.*` up front so byte-determinism holds without
adjudication.

Verdict: PRE_RESULT: PASS.
