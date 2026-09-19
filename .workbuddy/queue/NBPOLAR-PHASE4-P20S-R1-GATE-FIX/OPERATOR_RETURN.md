# OPERATOR_RETURN.md — NBPOLAR-PHASE4-P20S-R1-GATE-FIX (Stage-B executed once)

- Packet: `NBPOLAR-PHASE4-P20S-R1-GATE-FIX`, delta-successor of P20S Stage-B
  (DELTA.md §§1–8 inherited identical freeze; single-expression predicate fix
  at `l2_mechanism_probe_2m.py` `_integrity_gates` line 2548).
- Branch: `codex/nbpolar-phase0`.
  Workdir: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- Authorization: user standing pre-authorization 2026-09-20 + main-thread
  `proceed` adjudication (recommend path; two failing test pins handled first).
- Operator never self-accepts. No commit, no push. No rerun, no tuning, no H2
  verdict, no recovery-rate reading. `test_evidence_package.py` never run.

## 1. Test-pin handling (pre-execution)

- File: `comparison_bench/tests/test_nbpolar_mechanism_probe_2m.py` (+1 import).
- (a) `test_no_stage_b_root_and_no_protected_opens_in_stage_a`: body preserved
  verbatim as the P20S-Stage-A-historical record; scoped with a
  `pytest.mark.skipif((REPO_ROOT / l2s.FROZEN_OUT_ROOT).exists())` guard plus
  an explanatory comment (P20S Stage-B has executed: 15/15 files present,
  attempt consumed, so the absence clause is stale; all other clauses stay
  live invariants). New live R1 companion test
  `test_r1_out_root_absent_and_p20s_root_untouched` asserts the R1 out-root
  ABSENT and the P20S root PRESENT with 15/15 frozen `OUTPUT_FILES`
  (existence checks only — no writes, opens, stats, or listings).
- (b) `test_grep_rule_seed_placement`: `allowed_prefixes` extended with
  `.workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/` only (R1 is an authorized
  delta successor of the same P20S freeze; rule stays strict). `git grep`
  verification: `2026092360` appears in no new location — all hits sit under
  the previously allowed prefixes plus the R1 packet dir.
- Suite: `22 passed, 1 skipped` (the skip is the P20S-Stage-A-historical pin)
  via the sibling venv
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_mechanism_probe_2m.py -p no:cacheprovider`.

## 2. Stage-B execution (exactly once)

- Pre-execution: R1 out-root verified ABSENT; P20S root 15 files present.
- Command: DELTA.md §7 frozen command byte-identical except `--out-dir`
  repointed at
  `.workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m`,
  under `OPENBLAS/OMP/MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2`,
  `ulimit -v 2097152`, `timeout 1200`.
- Result: `EXIT=0`, wall `37s`.
- Runner stdout: `integrity_all_pass: true`, `records_completed: 3`,
  `outcome_label: TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE`.
- R1 out-root now holds exactly the fifteen frozen files (15/15 present).

## 3. Integrity conjunction (geometry/label only)

- `aggregate_summary.json`: `integrity` dict has 36 gates, all TRUE
  (36/36), `failing_integrity_gates: []`.
- `blocks_exact_with_declared_remainder: TRUE` (the P20S BLOCKED conjunct now
  passes on the unchanged frozen quantities).
- `resource_stop_fired: false`; `stage_b_sampling_calls: 0`;
  `sc_calls: 5/5 planned`; `tag_invocations: 3/3 planned`;
  `records_completed: 3/3 planned`; attempt read-accounting 1/1 consumed.
- Exact outcome label: `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE`
  (non-BLOCKED).

## 4. Determinism comparison R1 vs P20S (binding) — STOP-LEVEL FINDING

| File | P20S sha256 (prefix) | R1 sha256 (prefix) | Verdict |
|---|---|---|---|
| `per_block_arm_outcomes.jsonl` | `eae067eb…` (full: `eae067ebf904955ce79107004e866f2fb98af67ca87cc2052afdcafdaf9eeb51`) | `924cf1bc…` (full: `924cf1bc70e2ba14e09c87b29852d80ce3a9ecb4a2b73ef5ebd2953d8c8d81a3`) | MISMATCH (all 3 records differ) |
| `A_hazard_bits_f32le.bin` | `ef4398d3…` | `ef4398d3…` | MATCH |
| `A_inprefix_u8.bin` | `9e9f5e98…` | `9e9f5e98…` | MATCH |
| `A_inu_u8.bin` | `c3502047…` | `c3502047…` | MATCH |
| `B_hazard_bits_f32le.bin` | `ef4398d3…` | `ef4398d3…` | MATCH |
| `B_inprefix_u8.bin` | `cf75440d…` | `cf75440d…` | MATCH |
| `B_inu_u8.bin` | `bf4e871b…` | `bf4e871b…` | MATCH |
| `O_hazard_bits_f32le.bin` | `ef4398d3…` | `ef4398d3…` | MATCH |
| `O_inprefix_u8.bin` | `9e9f5e98…` | `9e9f5e98…` | MATCH |
| `O_inu_u8.bin` | `c3502047…` | `c3502047…` | MATCH |

- Per-record key-level diff (read-only, outcome values not read): the ONLY
  differing keys in all 3 records are run-telemetry fields — `wall_s` and
  `resources.{wall_s, vm_peak_kb, vm_size_kb, rss_bytes_hwm}` (e.g. record 0:
  `wall_s` 12.673539 → 12.760586; `rss_bytes_hwm` 548155392 → 547971072).
  Every scientific/decoding/IR/gate/order/tag field is identical across all 3
  records, and all nine IR-5 binaries match byte-for-byte.
- Binding classification: under DELTA.md §4 (exact bytes per record) this is
  a STOP-level non-determinism finding. Both roots retained immutable; NO
  repair, NO rerun performed. Main-thread adjudication required on whether a
  telemetry-only diff clears the §4 bar before any Pre-RESULT review.

## 5. Split audit (P20S root immutability)

- P20S root NEVER written/modified: post-run file count still 15/15;
  `per_block_arm_outcomes.jsonl` sha256 post-run still
  `eae067ebf904955ce79107004e866f2fb98af67ca87cc2052afdcafdaf9eeb51`
  (identical to the pre-run value recorded in §4).
- R1 writes confined to the new R1 out-root (15 files) + this packet's
  `STATUS.yaml`/`OPERATOR_RETURN.md` + the two test-pin edits in §1.
- No other files touched; `git status` shows no new modifications beyond the
  §1 test edits, the §1-adjacent runner fix (prepared), and the packet dirs.

## 6. Honest scope (verbatim, P20S TASK_PACKET.md §0)

> Honest scope (binding on proposal/design/packet/return language): a single
> merged-block (2M VAL-remainder tail + HOLD-remainder head) mechanism probe
> of one local-spike L2-order position rule under the frozen α1 construction
> at frozen disclosure with full-block hazard geometry recorded; descriptive
> geometry only; the merged DEV block is consumed by this packet; the HOLD
> tail 3595..3644 and all 1.5M remainders stay untouched; no recovery claim,
> no H2 verdict; the H2 decision is analysis, not a block result.
