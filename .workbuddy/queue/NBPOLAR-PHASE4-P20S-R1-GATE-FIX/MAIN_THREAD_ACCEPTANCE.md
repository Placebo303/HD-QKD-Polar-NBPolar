# MAIN_THREAD_ACCEPTANCE.md — NBPOLAR-PHASE4-P20S-R1-GATE-FIX

- Packet: `NBPOLAR-PHASE4-P20S-R1-GATE-FIX`, delta-successor of
  `NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED` (P20S Stage-B).
- Date: 2026-09-20. Authority: main thread (operator never self-accepts).
- No commit yet (batched separately). No further execution authorized.

## 1. Accepted label

- `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`
- Non-BLOCKED. 36/36 integrity gates TRUE, `failing_integrity_gates: []`.
- `blocks_exact_with_declared_remainder` TRUE after the single
  gate-expression fix (DELTA.md §1: `list()` on scalar-int `frame_start`
  → scalar `int()` comparison; nothing else touched).

## 2. Basis

- Delta-successor identical freeze (DELTA.md §2: same population, files,
  digests, K, arms, caps, budgets, formula; §1 one-expression predicate fix
  is the entire delta) + ONE authorized execution (OPERATOR_RETURN.md §§1–3:
  exit 0, wall 37 s, 15/15 files,
  `integrity_all_pass: true`, `records_completed: 3`,
  outcome label `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE`).
- Disclosure/count recount: key 104722 / public 983229, mismatch 0.
- Budget accounting: SC 5 (A 2 / B 2 / O 1), tags 3, genie 0+0
  (zero sampling at every stage).
- Split audit: consumed-1M 0 / consumed-1.5M 0 / consumed-2M exclusions hold;
  merged-DEV 1/1 read; 1M 0 + 1.5M 0 + 2M-non-DEV 0 contacts beyond counting.
- Telemetry adjudication (DELTA.md `## Main-thread adjudication
  (2026-09-20)`): the R1-vs-P20S `per_block_arm_outcomes.jsonl` byte diff is
  telemetry-only (`wall_s`,
  `resources.{wall_s, vm_peak_kb, vm_size_kb, rss_bytes_hwm}`), all 9 IR-5
  `.bin` files byte-identical, every scientific/IR/gate/order/tag/order-digest
  field identical — NON-BLOCKING; determinism satisfied on scientific fields;
  no third execution authorized or needed (P20S block consumed, R1 attempt
  spent); both roots retained immutable.

## 3. Geometry reading (NOT recovery)

Descriptive geometry/coverage quantities only:

- Arm A: exact (prefix mean 0.87406 bits).
- Arm B: `verify_failed` with first error L2 @ coord 0, fail hazard
  0.513 bits, IR-2 rank pct 0.4322, fail site OUTSIDE the disclosed prefix
  under both domain flags, floor rate 0.3717, prefix mean 0.87683 bits.
- Arm O: oracle exact (diagnostic, non-deployable).
- A△B = 1599/1599, size-delta 0.
- IR-1 masses 6746/26022.
- IR-3 above-threshold A/O 1641 vs B 1651.
- IR-4 top-16 in-prefix 0 on all arms.
- IR-5 uncapped full-block series present 3×3 bins
  (A/B/O × hazard_bits_f32le / inprefix_u8 / inu_u8).
- Per D2 this is geometry/coverage evidence ONLY: no recovery-rate reading,
  no H2 verdict.

## 4. Provenance

- P20S root
  (`.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m/`)
  retained immutable as the BLOCKED-label provenance record (never
  overwritten or modified; post-run 15/15 files, `per_block_arm_outcomes.jsonl`
  sha256 unchanged).
- R1 root
  (`.workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m/`)
  is the accepted-descriptive record (15/15 files).

## Acceptance (2026-09-20)

- Independent Pre-RESULT review: PASS 9/9 (reviewer-go, session
  ses_f44c186afffej4IC26000cx8cB; record
  `PRE_RESULT_REVIEW.md` in this packet dir).
- Adjudicated substance: delta scope single-expression (DELTA.md §1 one
  gate-expression conjunct; nothing else touched); 36/36 integrity gates
  TRUE, `blocks_exact_with_declared_remainder` TRUE, non-BLOCKED outcome
  label; disclosure caps 35464/35464/33794 Δ0, key/public totals
  104722/983229, recount 0; undetected 0 isolated, O arm
  `deployable: false` excluded from operational aggregates; D2
  geometry-only judgement form (no recovery-rate reading, no H2 verdict);
  nine scalars + IR-1..IR-5 uncapped with truth isolation; determinism
  telemetry-only ruling factually verified — 9/9 IR-5 `.bin` byte-identical,
  `per_block_arm_outcomes.jsonl` diff confined to `wall_s`/`resources.*`;
  one-shot 1/1 with the P20S root retained immutable; honest-scope §0
  sentence verbatim.
- Final label:
  `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`.
- Non-blocking note carried forward: future delta successors should
  freeze-exclude `wall_s`/`resources.*` up front so byte-determinism holds
  without adjudication.
