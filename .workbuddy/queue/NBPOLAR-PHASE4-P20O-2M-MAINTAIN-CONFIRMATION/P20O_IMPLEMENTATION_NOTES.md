# P20O Stage-A implementation notes (2026-09-19)

Packet: `NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION`. Stage A only;
Stage B is NOT authorized and was NOT executed. No commit/push. Operator:
backup `coder-fast` instance (the primary handler was platform-aborted twice
before any write; the verified clean start is documented in the handoff).

## 1. Files changed (exact paths)

New (untracked additions; nothing else was written outside the packet dir
and the `workspace/p20o/` scratch root):

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_maintain_2m.py`
  — the thin P20O runner (3474 lines; sha256
  `ee446380fb0a8c9eabe37e9dc9335a286bbbd2076cae9ff7a9655efdc7d12d75`).
- `comparison_bench/tests/test_nbpolar_l2_alt_maintain_2m.py`
  — focused injected tests (1106 lines; sha256
  `84f6e7516718827aa4548646bcfb8a239a08bb3dee43a8825522e441957951e4`).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz`
  — frozen Stage-A 2M raw prior (25438650 B; canonical digest
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json`
  — frozen orders/derivation file (438535 B; file-bytes sha256
  `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz`
  — frozen Stage-A alt-L2 table (25430240 B; file-bytes sha256
  `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/P20O_FREEZE.md`
  — the Stage-A freeze (all pins, D1 literals, D2 outcome, ninth-scalar
  PRESENT decision, read audit).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/P20O_IMPLEMENTATION_NOTES.md`
  — this file.
- `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/STATUS.yaml`
  — updated in place, stage-true.
- `workspace/p20o/8da2574c51b74d039606110bc55b0d72/derive_stdout.json` +
  `derive_stderr_and_time.log` — the exact stdout/stderr + `/usr/bin/time -v`
  capture of the single Stage-A derivation (temp scratch root).

NOT changed: `src/`, `experiments/`, `tools/`, every accepted
`comparison_bench/.../formal_ir/nbpolar/*.py` (including
`raw_prior_val_1p5m.py`, `l2_alt_hold_1p5m.py`, `l1_order_1p5m.py`,
`prior.py`, `per_session_calibration.py`, `target_construction.py`), the
accepted P20M/P20N products (`raw_prior_1p5m.npz`,
`raw_prior_orders_1p5m.json`, `alt_l2_tables_1p5m.npz`,
`raw_prior_val_1p5m/`, `l2_alt_hold_1p5m/`), X08/X09 probe roots,
`results/`, `comparison_bench/outputs_comparison/`, and the packet's
`TASK_PACKET.md` / `PROMPT.md` / `AUTHORIZATION_PROMPT.md`. The P20O
OpenSpec delta (`specs/nbpolar-phase4-p20o/spec.md` + the `tasks.md` P20O
section) was already staged by the planner at freeze time (16:42) and was
left byte-untouched (its tasks explicitly say no box is checked by the
implementing session).

Read-only reuse evidence (module hashes at Stage-A close, matching their
pre-session values and the P20N implementation-notes table where applicable
— computed with sha256 over file bytes):

| accepted module | sha256 |
|---|---|
| `raw_prior_val_1p5m.py` | `a9adc19aa53769a5449626b5ba60bf2929d48558fc8547681eb30d03d0835b6f` |
| `l2_alt_hold_1p5m.py` | `d101831bc54f65096bfbb505afebdbe37b965540d52b572cd29b7d5a50bf9082` |
| `l1_order_1p5m.py` | `3bc6865f2bd3fbc558253cf1d1d693f3678666d89a1c88e3052c23b32e0e036d` |
| `prior.py` | `c6fb48cbe718636f52063da82892519b0ec87bd43d56a57f97d5b0ea80f7ee32` |
| `per_session_calibration.py` | `c0d8d960b53191ccb884f56ea743815b000e98656648d8ac761d0708afdb0a31` |
| `target_construction.py` | `2adb50449019c12063998d362dc3ee9acf810abc0548ff27a0e43942b346d347` |
| `target_n_scaling.py` | `0802f57fc2a4cdd45f89b8a25652bc052a02cd5495773896d198137d25339779` |
| `empirical_genie_scaling.py` | `a9258871dbd4b8cc2ccef738b0aec74ed20d8baac23b5055aea585338f22e912` |

The pre-existing dirty worktree entries (the ` M` set recorded in the
handoff: 27 files) were preserved untouched; the only new status entries
are the two untracked files above (plus the already-untracked packet dir).

## 2. §2 delta-list evidence (d1–d8), nothing else

- **d1 prior source**: `verify_session_prior_2m()` wraps the accepted
  `raw_prior_val_1p5m.verify_corrected_prior` under the
  `session_prior_identity` gate name (exact 10-key set, canonical digest
  vs `FROZEN_SESSION_PRIOR_DIGEST`, lambda-0.0 pin, floor pin, H1/H2/TOTAL
  recomputation within 1e-12, `p_b` cross-check, normalization). Stage A
  derives the artifact with the accepted raw rule
  (`raw_prior_arrays()` delegates to `p20m.build_raw_prior_arrays`); the
  single protected counts open is the new `load_counts_2m()` (2M key ONLY,
  no-reopen guard, array-bytes sha256, no whole-file hash).
- **d2 alt-L2-table source**: `alt_tables_2m()` delegates the frozen α=1
  rule to the accepted `l2_alt_hold_1p5m.derive_alt_l2_arrays` on the SAME
  counts; `verify_alt_l2_identity_2m()` / `verify_alt_l2_arrays_2m()`
  implement the `alt_l2_identity` gate (file-bytes sha256, α==1.0, floor
  pin, exact 9-key set, `p1` equality vs the 2M prior within 1e-12,
  `h1_inc` literal, `h_total_alt` consistency, `h2_alt` recomputation via
  `entropy_bits`, column/axis normalization).
- **d3 K pins**: `FROZEN_K_TOTAL/K1/K2 = 7080/334/6746` module literals;
  `check_k_literals()` replays them and recomputes the S2-i budget literal
  from the same-run 2M `FROZEN_H_TOTAL` (never recarried, never the alt-H);
  the per-arm leaks are the frozen `5*(K1+K2)+64` / `5*K2+64` arithmetic.
- **d4 orders**: `verify_stage_b_order_file_2m()` (P20O protocol/kind/n,
  both permutations, derived k literals, prior digest + program pin +
  derivation seeds + 16 blocks) called with the Stage-A pins; the same
  `l1_order`/`l2_order` arrays feed all four arms (first-334 / first-6746
  prefixes), zero sampling.
- **d5 arms**: four hardcoded `ArmSpec`s in `frozen_arm_table()` +
  `check_frozen_arm_table()` (A incumbent/334/6746, B alt/334/6746, C
  incumbent oracle, D alt oracle; B−A and D−C key-bit deltas exactly 0;
  30 SC / 20 tag / 20 record design totals); no CLI surface can change them.
- **d6 tag domain**: `l2_alt_maintain_2m_seed_bits()` with master
  `2026092310` and prefix `nbpolar-p20o-maintain-2m-seed` (validated
  against `FROZEN_ARM_NAMES`; differs from every prior packet domain).
- **d7 instrumentation**: `_l2_hazard_diagnostics(*, block, view, p2_arm,
  counts_arr, l2_order, k2, first_error, field=None, low_hat=None)` — the
  eight X09-R1 scalars (gated `l2_prefix_len == K2`, radius R=8, natural
  block index space, true-cell prefix means, null-unless-L2 fail fields)
  plus the ninth U-domain scalar `l2_fail_in_prefix_u_domain` **frozen
  PRESENT** (main-thread instruction; closes the P20N domain-mixed
  `l2_fail_in_prefix` ambiguity). Called post-decode from
  `_operational_record()` / `_control_record()` at the carried-over P20M
  `_selected_diagnostics` code point (accepted
  `raw_prior_val_1p5m.py:1306-1334` pattern; `_selected_diagnostics`,
  `_block_view`, `_dev_block_scoring`, `_scoring_absent`, `_stat_record`
  reused read-only). Recording-only: outputs are written into the record
  dict and never passed to `run_operational_block`,
  `run_oracle_control_block`, `_decode_layer`, metric builders, disclosure
  or order decisions; pinned by `test_truth_isolation_recording_only` and
  the no-input-mutation assertions in
  `test_instrumentation_fields_nullability_and_formulas`.
- **d8 2M-VAL population**: `form_val_blocks()` mirrors the accepted
  VAL/HOLD formation semantics for the 2M VAL pool (first 640 VAL frames
  2187..2826, five 128-frame blocks, remainder 2827..2915 counted never
  decoded, `(frame_id, pair_idx)` lexsort only, no sampling); gate family
  (b)/(c)-(e) in `verify_val_containment()` /
  `verify_consumed_exclusions_2m()` (identity-level consumed-1M/1.5M
  exclusions + same-identity TRAIN/HOLD exclusions + S2-ii declaration);
  cross-file identity (a) via `verify_dev_source_identity_2m()` (2M path
  only; 1M and 1.5M paths refuse by name; build-manifest size/sha
  provenance pins); manifest identity via `verify_dev_manifest_2m()`;
  prior/alt/order/K/budget pins (f)-(g) before any SC call.
- Reused read-only helpers (no reimplementation): `run_operational_block`,
  `run_oracle_control_block`, `OracleControlResult`,
  `verify_predecessor_construction`, `first_error_coordinate`,
  `l1_prefix_positions`, `l2_prefix_positions`, `seed_bits_for`,
  `_stat_record`, `_block_view`, `_dev_block_scoring`, `_scoring_absent`,
  `_selected_diagnostics`, the block-event/recount helpers,
  `p20m.derive_raw_prior_arrays` / `build_raw_prior_arrays` /
  `sample_synthetic_train_blocks` / `verify_budget_literal` /
  `budget_literal_display` / `verify_corrected_prior`,
  `p20n.derive_alt_l2_arrays` / `in_sample_l2_ce_bits_per_symbol` /
  `alt_prefloor_table` / `_raw_p2_from_counts` / `_hazard_bits`,
  `psc.canonical_prior_digest`, `select_empirical_split`,
  `budget_k_total`, `entropy_bits`, `polar_transform`, `make_gf32`,
  `load_pairs_table`/`normalize_pair_columns`, `toeplitz_tag`,
  `SOURCE_IDS`/`NPZ_KEYS`, `operational_f13._write_json`/`_append_jsonl`/
  `_budget_exceeded`/`_cell_resource_record`/`_peak_rss_bytes`/
  `_check_chunk_contract`/`_check_tag_bits`/`_check_n`/`_as_int`.

## 3. Counts source path resolution (disclosed)

The packet pins the counts file by its canonical repo-relative path
`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`.
Under this worktree that relative path does not resolve: the V25 counts
`*.npz` is gitignored and is present only in the canonical data root used
by every accepted nbpolar derivation, i.e. the sibling checkout's absolute
path pinned by `holdout_microcheck.FROZEN_COUNTS_PATH`
(`/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/.../channel_counts.npz`;
see the accepted P20H identity doc `counts_path`, size 25166822 B). The
single Stage-A open therefore used that canonical absolute path; the
runner's `_check_counts_path()` accepts ONLY a path resolving to it, and
the derivation output records the exact path used. No other file was
opened.

## 4. Stage-A derivation record (executed EXACTLY once)

- Scratch root: `workspace/p20o/8da2574c51b74d039606110bc55b0d72/`
  (`derive_stdout.json`, `derive_stderr_and_time.log`).
- Exact argv (frozen `--derive` mode; engine exports applied):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_maintain_2m --derive --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 2M --alpha 1 --floor 1e-15 --n 32768 --target-f 1.3 --deriv-seeds 2026092321 2026092322 2026092323 2026092324 --out-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --out-orders .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --out-alt .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz
```

  (The only difference from the packet §10 template is the canonical
  absolute `--counts` value per §3 above; every other token is identical.)
- Result: exit 0; start `2026-09-19T09:49:23Z`, end `09:53:07Z` (≈224 s
  external); in-runner `wall_s 221.892093`; no rerun (no execution error).
- Counts identity: array sha256
  `e391a3466eee4354f76d65be7093f78b8322103178b6d8577331dbcd092351e4`,
  shape (1024,1024), total 559872, npz size 25166822 B,
  `counts_content_opens 1`, `protected_content_opens 1`.
- Raw prior: canonical digest
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`;
  h1 `0.02566204884275839` / h2 `0.8069006731309893` /
  h_total `0.8325627219737477`; floor hits `1045941` / 1048576 (rate
  `0.9974870681762695`); zero columns `0`; column dev `1.13464793116691e-13`.
- Budget/split/orders: literal
  `1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536] = 7080`;
  `(K1,K2,K_total) = (334,6746,7080)`; 16 blocks used / 0 impossible /
  32 genie calls / 0 provenance violations; TRAIN residual
  `3.603823440223586e-07`; order file sha256
  `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`.
- Alt table: file-bytes sha256
  `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`;
  α 1.0 / floor 1e-15; floor hits 0 (rate 0.0); zero columns 0; `f_alt`
  range `0.0006071645415907555..0.2895392278953916`; `p1`
  equality `0.0`; `h1_inc 0.02566204884275839` / `h2_alt 1.3245794596410305`
  / `h_total_alt 1.3502415084837889` (descriptive only).
- D1: `ce_alt 0.8850983725781965`, `ce_incumbent 0.8069006731253678`,
  ceilings `33794/35464`, `alt_ideal_length_bits 29002.90347264234`.
  D2 `alt_construction_budget_feasibility` = **FEASIBLE** (margin
  `4791.09652735766` bits), evaluated BEFORE any VAL contact.
- Read-only post-derivation verification (independent recomputation, no
  protected opens): all three artifacts re-hashed with `sha256sum`; prior
  canonical digest recomputed; `session_prior_identity`,
  `alt_l2_identity` and `order_derivation_identity` gates all PASS against
  the real artifacts; D1/D2 recomputed and equal to the pins within 1e-12
  (1e-9 on the product).

## 5. Focused tests: commands and results

```
.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_l2_alt_maintain_2m.py -p no:cacheprovider
```

run with the sibling venv (`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`,
numpy 2.5.3 / pandas 3.0.5 / pytest 9.1.1):

- Pre-freeze run (module pins all `None`; derivation sampled via a
  deterministic injected stub; fresh `workspace/p20o/<uuid>/` roots):
  **20 passed, 0 failed, 0 skipped** (`39.31 s`). Two pin-dependent tests
  early-return in this state by design (documented in their docstrings).
- Post-freeze run (all Stage-A pins filled; same command): **20 passed,
  0 failed, 0 skipped** (`39.17 s`). This state additionally exercises
  `check_frozen_arm_table`/`check_k_literals` and the byte-identical
  `FROZEN_COMMAND` reconstruction.

Test matrix (all injected/synthetic, no production invocation, no
protected-content open):

1. frozen literals/arms/population/keys/tag domain + frozen-pin replay;
2. `FROZEN_COMMAND` byte-identity + required tokens;
3. 2M raw rule vs independent literal (MLE + floor + renorm, `p_b`
   cross-check, H via `entropy_bits`, no-lambda pin, digest reproducibility)
   over 7 fresh seeds;
4. α=1 alt rule vs independent literal + key set + p1 equality + alt-H;
5. derive end-to-end: 10-key prior npz + canonical digest, orders JSON
   protocol/kind/permutations/digest/seeds/blocks, 9-key alt npz + byte
   digest, counters (counts open 1, 16 blocks/32 genie calls, zero decoder
   calls), fail-if-present;
6. CLI mode refusals (ambiguous / derive-missing / mixed / Stage-A-only /
   Stage-B-missing);
7. K-literal gate refusals (K1/K2/source/n/dev/remainder/tag-master/digest
   pins/alpha/target-f/deriv seeds) in the frozen state;
8. D1 estimator exactness on a tiny fixture + zero-mass refusal;
9. D2 gate arithmetic both ways (feasible/infeasible) + congruence with the
   derive verdict;
10. source/exclusion gate refusals (1M path, 1.5M path, other path,
    VAL-containment, remainder, consumed TRAIN/HOLD, manifest 2M cell,
    schema, missing file);
11. `session_prior_identity` refusals (digest, H literal, lambda pin, floor
    pin, key set);
12. `alt_l2_identity` refusals (digest pin None, flag/digest mismatch,
    bytes-digest mismatch, α tamper, p1 tamper, key-set tamper);
13. order-file gate positive + refusals (digest pin, bytes digest,
    k_total, prior digest, permutation, seeds, protocol, block count);
14. nine instrumentation scalars: presence, nullability (all five fail
    fields incl. the U-domain scalar), prefix/fail/window exact formulas,
    U-domain membership both ways, gated prefix-length refusal,
    missing-field refusal, no input mutation;
15. truth-isolation sentinel (hostile recorder: post-decode fields
    unchanged, recorder outputs land only in record fields);
16. 2M VAL population + block/remainder formation + gate refusals +
    malformed-population refusals;
17. no Stage-B root + zero protected opens in Stage A + module token
    presence/absence audit (no `load_v25_channel_counts`, no
    `smooth_joint_to_conditional`, no `LAMBDA_STAR`, no 1M/1.5M lambda
    constant);
18. zero Stage-B sampling pin (no seed/sample CLI flag, no `seeds`
    parameter, the only `default_rng`/`sample_full_block` mention is the
    frozen order-program provenance pin);
19. one-open guards refuse reload + missing-2M-key refusal without
    consuming the guard;
20. seed-domain grep rule (`2026092310`, `2026092311..2026092317`,
    `2026092321..2026092324` only in the P20O runner / test / packet /
    P20O OpenSpec documents).

## 6. Seed-domain grep evidence (repo-wide, `git grep -l --untracked`)

Allowed locations only:

- master `2026092310`: `l2_alt_maintain_2m.py`,
  `test_nbpolar_l2_alt_maintain_2m.py`, the P20O packet dir
  (`TASK_PACKET.md`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `STATUS.yaml`),
  `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20o/spec.md`,
  `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md`.
- test seeds `2026092311..2026092317`: the P20O test file (all seven),
  plus `2026092311`/`2026092317` also appearing in the packet dir and the
  P20O OpenSpec docs (planner-staged range notation). No other files.
- derivation seeds `2026092321..2026092324`: the P20O runner (frozen
  constants), the P20O test file (range notation only; no literal lists),
  the three frozen artifacts' provenance fields (the orders JSON carries
  the seed list), the packet dir, and the P20O OpenSpec docs. No other
  files.
- No hit outside the P20O runner / tests / packet / P20O OpenSpec
  documents; the same check runs inside the test suite
  (`test_grep_rule_seed_placement`, green).

## 7. Protected-read audit (Stage-A close)

| protected input | allowed | used |
|---|---|---|
| V25 counts npz, `--source 2M` array ONLY | 1 | **1** (single Stage-A derivation open) |
| V25 counts npz, any other array (1M/1.5M/other) | 0 | **0** |
| 2M VAL-DEV pairs content open | 0 (Stage A) | **0** |
| 2M VAL-remainder open/stat/listing | 0 | **0** |
| 2M HOLD open/stat/listing | 0 | **0** |
| 1M / 1.5M splits in any form | 0 | **0** |
| real-data decoder execution | 0 | **0** |
| Stage-B output root | absent | **absent** |

- The derive mode opened ONLY the counts file (2M member materialized; no
  other member content) and wrote the three artifacts; no pairs parquet
  was opened/statted by the runner.
- Disclosed deviation: one early `ls -la` directory listing of the 2M
  pairs directory printed the parquet's size/mtime metadata (no content
  read, no hash, no open, no frame access). No pin/derivation/selection
  uses it: the frozen size/sha pins are the v13r3fresh build-manifest
  values (`2458335` B /
  `d5a36eec8a03ce7e801bba4fd4b2e62cf8aef13c1efe1166766db79364ffc307`),
  read as JSON metadata. The observed size happens to equal the manifest
  pin. Recorded here, in `P20O_FREEZE.md` §9 and in the operator return.
- Accepted-module hashes unchanged (§1 table); frozen directories
  (`results/`, `comparison_bench/outputs_comparison/`) untouched; no
  commit/push.

## 8. Stage-B state

- Stage-B output root
  `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/`
  ABSENT (asserted by the suite).
- Stage B remains unauthorized: it needs an independent Pre-EXECUTE PASS
  (adjudicating the §3 prior/alt derivation, the D2 outcome, the §5
  budget/K-literal, the §4 gate family, the §2 runner-delta design and the
  §7 instrumentation boundary incl. the U-domain scalar), the filled
  STEP-2 text with the pins above, and target-output absence.
- The operator marks nothing accepted and never authorizes Stage B.
