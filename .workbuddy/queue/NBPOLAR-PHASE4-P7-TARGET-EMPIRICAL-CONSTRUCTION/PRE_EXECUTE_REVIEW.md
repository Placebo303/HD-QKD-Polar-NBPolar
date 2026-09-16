# Pre-EXECUTE review — NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION

- Reviewer: independent `reviewer-go` (backup instance). Did not write the reviewed code.
- Date: 2026-09-14 (WSL). Repository: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- HEAD during review: `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged after review; no commit, no push).
- Read-only: the only file written by this review is this document. Old roots, accepted modules and the sibling checkout were not modified.
- Closure (details §7): the registered V25 `channel_counts.npz` was **not opened** (metadata `stat` only); artifact reads / attempts remain **0/1 and 0/1**; the frozen output root is **still absent**; the frozen gate command was **never run**.

## Verdict: PASS

All eight required Pre-EXECUTE checks pass. Review item #1 is adjudicated as an
acceptable, uniquely self-consistent reading of the packet's own two-tier
entropy contract, with the precise frozen semantics ratified in §3. No blocking
issues. Five non-blocking observations are recorded in §6. This PASS does not
by itself authorize execution: the explicit authorization in
`AUTHORIZATION_PROMPT.md` and the main-thread Pre-EXECUTE checklist remain the
gates. Reviewer evidence is trusted per AGENTS.md §4.1; main-thread acceptance
remains separate.

---

## 1. Required checks (commands and raw evidence)

### Check 1 — STATUS exactness: PASS

Evidence (`cat .workbuddy/queue/.../STATUS.yaml`):

- exactly five `true` flags: `documentation_authorized`, `implementation_authorized`, `artifact_read_authorized`, `decoder_execution_authorized`, `development_gate_authorized`;
- other flags all `false`: `real_data_authorized`, `eval_authorized`, `scalable_decoder_authorized`, `scl_authorized`, `scientific_promotion`;
- `artifact_reads_allowed: 1`, `artifact_reads_used: 0`, `attempts_allowed: 1`, `attempts_used: 0`;
- `state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P7_TARGET_EMPIRICAL_CONSTRUCTION`, `next_gate: IMPLEMENTATION_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW`, `independent_pre_execute: pending`, `result: null` — consistent with the stage and with `AUTHORIZATION_PROMPT.md`.

### Check 2 — OpenSpec delta consistency with TASK_PACKET: PASS

Evidence: read of `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p7/spec.md`
(134 lines) and `tasks.md:241-291`.

- Requirements cover exactly the packet's frozen surface: input/support rule; preconditions + `BLOCKED(target_population_contract)`; TRAIN/DEV streams, orders, permutations, Spearman >= 0.95 both layers, BEC `epsilon_l=H_l/5` report-only; paired arms with per-layer SC restart, 10-bit label, one tag; truth boundary; buckets; 989/2623 accounting + independent recount; integrity/scientific gates and the three labels; CLI/five-file output, absent root, no-rerun, forbidden paths; bounded claim + independent Pre-EXECUTE/Pre-RESULT.
- All numeric constants in the delta match the packet bit-for-bit: path, 25,166,822 bytes, 1e-15 floor, literals `0.02428054681872374` / `0.7767572780789994` / `0.8010378248977232`, `1e-12` / `1e-9` tolerances, seeds `2026091650..1652`, `2026091660..1664`, 256/128, 640, `K1=45`/`K2=140`, `stream+10000`, `989`, `2623`, `>=620/640`, `z = 1.6448536269514722`.
- `tasks.md` P7 section: all nine items `- [ ]`; no box checked. No P3–P6 content altered (pre-existing uncommitted rows left as-is).

### Check 3 — Frozen identity: PASS

Commands and evidence:

- `stat -c '%n %s' /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`
  -> `25166822` bytes (metadata only; no content open; local nbpolar copy does not exist, so the registered sibling path is unambiguous).
- Command identity script (`build_parser().parse_args` on the extracted block): packet command == freeze command == module `FROZEN_COMMAND` (byte-identical strings), and parsing yields `--counts <registered path> --source 1M --n 256 --floor 1e-15 --train-seeds 2026091650 2026091651 2026091652 --train-blocks 256 --dev-seeds 2026091660..2026091664 --dev-blocks 128 --k1 45 --k2 140 --out-dir <frozen root>`.
- Module constants: `FROZEN_TRAIN_SEEDS=(2026091650,2026091651,2026091652)`, `FROZEN_DEV_SEEDS=(2026091660..2026091664)`, `FROZEN_TRAIN_BLOCKS=256`, `FROZEN_DEV_BLOCKS=128`, `FROZEN_PAIRS=640`, `FROZEN_K1=45`, `FROZEN_K2=140`, `FROZEN_N=256`, `FROZEN_FLOOR=1e-15`, `PUBLIC_TAG_MASTER_OFFSET=10000`; derived masters `[2026101660..2026101664]`.
- Source/axis: accepted loader `v35_algorithm_development.load_v25_channel_counts` maps source `1M` to key `type2_1M_20260121_184040_N_ab_train_N_ab_train` and validates shape `(1024,1024)`; the 1M record is the 2026-01-21 `type2_1M` session (`data_inventory.json`), consistent with V49/X07.
- Seeds freshness: worktree grep for the eight seeds lists only the P7 packet/spec/code/tests and the main-thread memory record (`AGENT_PROJECT_MEMORY.md:4167`); `git grep` finds only that memory line among tracked files. No prior consumed run, evidence root or probe uses these streams.
- Output root: `ls .workbuddy/queue/.../target_construction_gate` -> `No such file or directory` (absent).

### Check 4 — Review item #1 (entropy literals / floor reading): PASS with ratified semantics

Full adjudication in §3. Summary: the claimed floor-induced shift is reproduced
from code logic (mimic: H1 `4.263e-11`, H2 `8.540e-12`, total `5.117e-11`, vs
the operator's `4.27e-11` / `8.5e-12` / `5.118e-11`); the literals are exactly
the V49 `nll_*` columns; the strict floored-table reading is unsatisfiable at
either floor level (V49's own recorded floored `ent` exceeds its `nll` by
`1.542e-12`); the population reading is the only one jointly consistent with
the packet's separate `<=1e-9` floor guard. Ratified semantics recorded in §3.

### Check 5 — Code review: PASS (non-blocking notes in §6)

Evidence: full read of `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_construction.py`
(2323 lines) plus the accepted dependencies (`prior.derive_p1/derive_p2`,
`construction.genie_conditionals/disclosure_order_from_stats/analytic_order/spearman_rank_corr`,
`sc.sc_decode` `x_hat = u_hat G_N`, `empirical_channel.sample_full_block`,
`shared.toeplitz_tag/canonical_event`, `protocol.wilson_lower_bound/WILSON_Z`,
`two_layer` constants). Verified:

- Refusals before the NPZ open: existing `--out-dir` (`:1554-1556`), range/point validation (`:1557-1584`), then stat-only size check (`:1591-1596`) and exactly one loader call (`:1597`); no reopen path exists.
- Preconditions before any genie/SC (`:1649-1660`); direct reviewer probe with a guaranteed mismatch: `BLOCKED(target_population_contract): failing preconditions: h1_matches_literal,h2_matches_literal,total_matches_literal`, `sc_decode calls: 0`, `genie calls: 0`, `output root exists: False`.
- Support rule exactly `column-normalize -> max(1e-15) -> renormalize`, `p_b` from column totals, accepted `derive_p1`/`derive_p2` under `A=32*U1+U2` (`:434-473`, `:501-536`); sampling is the accepted `sample_full_block` (B first, then A per coordinate; `high=A//32`, `low=A%32`) with explicit per-stream `default_rng` (`:1671`, `:1748`).
- TRAIN: accepted `genie_conditionals` accumulation per stream and pooled, matching `build_construction` exactly; orders frozen (per-stream + pooled + BEC, canonical digest) before the first DEV call (`:1696-1718`); every order checked a permutation; `orders_unchanged_after_dev` recomputed after DEV (`:1790`).
- DEV: two paired arms (`:984-1025`), fresh per-layer `sc_decode` calls with fresh metric objects, candidate-conditioned L2 gathered from Bob + `sc1.x_hat` only (`:867-868`), `label_hat = low_hat + 32*high_hat` (`:876`), one arm/block-domain-separated 64-bit Toeplitz comparison per viable candidate (`:870-882`).
- Truth boundary: truth used only for sampling, disclosed values, tag construction and scoring; block sentinel mutates per-arm truth copies after metrics/decisions exist and requires protected arrays bitwise (`:938-946`, `:1026-1033`); L2 spy test confirms the candidate (not truth) enters `gather_p2_metrics`.
- Buckets `exact`/`undetected`/`verify_failed`/`decode_failed`/`resource_abort` with accepted precedence (`:713-730`), paired cells `both_exact`/`empirical_only`/`bec_only`/`neither`; per-record structural consistency checker (`:1101-1161`).
- Accounting: L1 `225`, L2 `700`, tag `64` => fully invoked arm `989` (`:152-155`); `2623` public bits per tag; transcript events arm-tagged; independent literal recount (`:1193-1274`) and mismatch list; incremental totals vs recount; aborted arms exempt and event-free.
- Gates/labels exactly per packet: 11 integrity flags in frozen order (`:206-218`), 3 scientific flags (`:219-223`), `z=1.6448536269514722`, labels `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE` / `..._NOT_CONFIRMED` / `BLOCKED(<earliest gate>)` (`:1888-1914`), all persisted in `aggregate_summary.json`; exactly five output files (`:224-230`, write block `:2145-2159`); aggregate summary carries per-stream results, cells, all bucket counts, stability, disclosure, planning-only `f`, wall/RSS (packet reporting requirement satisfied across the five files).
- Five-file schema: scalar/aggregate only; no symbols, labels, disclosed values, decoded keys or raw seed bits persisted (`_arm_record` `:1044-1067`).

### Check 6 — Tests: PASS

Pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3). Fresh basetemps, `-q -p no:cacheprovider`:

- Focused: `11 passed, 1 warning in 7.85s` (`comparison_bench/tests/test_nbpolar_target_construction.py`, `/tmp/p7_review_focused`).
- Full NB-Polar suite: `228 passed, 1 warning in 105.59s` (`test_nbpolar_*.py`, `/tmp/p7_review_full`); per-file collection sums to 228 = 217 predecessor + 11 new.
- Coverage matrix confirmed in the focused file: floor/renorm + refusals (`:150-188`), independent literal entropy reconstruction incl. floored variants (`:190-227`), zero-column/literal-mismatch/floor-change preconditions (`:230-259`), sampler frequencies/packing/determinism (`:262-286`), per-stream/pooled orders + freeze digest (`:289-328`), arm separation + candidate-L2 truth isolation (`:331-437`), buckets + record consistency (`:440-519`), disclosure/tag accounting + literal recount + tamper (`:522-577`), CLI refusals/frozen constants (`:580-740`), sentinel + resource-abort (`:743-801`), no-forbidden-marker/no-artifact/no-production + empty-cwd import (`:804-840`).
- Artifact isolation: Python audit-hook runs recorded **zero** opens of `channel_counts`/Model-F/parquet/TTBin/V25/`outputs_comparison`/held-out paths — focused file: 0 events; full 16-file NB-Polar suite: 228 passed with **0 non-temp artifact-marker opens**. Focused tests patch the loader with a raising stub for path-refusal tests and use injected counts otherwise; frozen streams are never used as inputs (test seeds `2026091680..86`).

### Check 7 — Bounded smoke and budget projection: PASS

Injected 1024x1024 V25-like mimic (2541 nonzero cells), `N=256`:

- Tiny injected runner at a temp root writes exactly `['aggregate_summary.json','construction_orders.json','frozen_plan.json','per_block_paired_outcomes.json','report.md']`; all integrity gates true; label `TARGET_EMPIRICAL_CONSTRUCTION_NOT_CONFIRMED` (shape not the frozen 640) — expected for injected smoke.
- Timing (same interpreter, same code path): TRAIN-like block `0.0682 s` (2 genie SC calls), DEV-like paired block `0.1305 s` (4 SC + 2 tags). Projected frozen wall `768*0.0682 + 640*0.1305 = 135.9 s`, i.e. **~26.5x margin under 3600 s**.
- Memory: kernel `VmHWM` after a 24-block injected run `209.2 MB` (`/proc/self/status`); module-recorded `rss_bytes_peak` still `<= 2 GiB`. Note in §6.2: WSL `ru_maxrss` misreports in this environment (constant 1,173.1 MB that does not track real usage), but both readings are below the 2 GiB gate, so `resource_limits_met` stays true with large margin.

### Check 8 — Scope / premises: PASS

- `git status --porcelain` (67 entries) matches the declared set plus pre-existing dirty state: P7 additions are exactly `target_construction.py`, `test_nbpolar_target_construction.py`, `specs/nbpolar-phase4-p7/`, the P7 section of `tasks.md`, and the packet queue (`STATUS.yaml`, `P7_FREEZE.md`, `P7_IMPLEMENTATION_NOTES.md` + packet docs).
- No accepted-module edits: mtime scan of every modified/untracked file shows all accepted modules and prior modules predate the P7 session (`nbpolar/__init__.py` 2026-09-13 21:07, `two_layer.py` 09-13 12:59, `protocol.py` 09-13 02:13, `empirical_channel.py` 09-13 00:58, etc.); files newer than 2026-09-14 02:23 are the P7 artifacts plus main-thread X07/P7-freeze docs (memory/decision-log/CURRENT_TASK/DOCUMENT_INDEX at 02:23–02:27, before `STATUS.yaml` at 02:43).
- X06/X07 roots untouched (`workspace/probes/nbpolar_x06.../results.json` 09-14 00:52; `...x07.../results.json` 01:47, both before the P7 session).
- HEAD unchanged `ab173f2a`; no commit/push; frozen root absent; STATUS reads/attempts still 0.

---

## 2. Frozen record (reviewer-verified)

| item | frozen value (verified) |
|---|---|
| Input | `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`; `st_size == 25166822` (stat only); source `1M` -> `type2_1M_20260121_184040_N_ab_train_N_ab_train`, shape `[1024,1024]`, axis `[Alice,Bob]`; one content open + one attempt consumed at that open, no reopen |
| Support rule | `f = counts / column totals`; every cell `< 1e-15` -> `1e-15`; each Bob column renormalized; `p_b = column totals / total count`; `P1/P2 = derive_p1/derive_p2(f)` under `A = 32*U1 + U2`; no lambda/backoff/tuning/floor scan |
| Checked entropies (ratified) | `h1 = sum_b p_b H(P1_raw(.|b))`, `h2 = sum_b p_b sum_u1 P1_raw(u1|b) H(P2_raw(u1,b,.))`, `total = h1+h2` on the **raw MLE** table; `|h1-0.02428054681872374| <= 1e-12`, `|h2-0.7767572780789994| <= 1e-12`, `|total-0.8010378248977232| <= 1e-12`; `0 log 0 = 0` |
| Floor guard | `|floor_total - total| <= 1e-9` where `floor_*` are the same functionals on the A-level floored/renormalized sampling table; floored values reported but never gated against the literals |
| Column checks | no zero Bob column; `|sum p_b - 1| <= 1e-12`; `max_b |sum_a f(a,b) - 1| <= 1e-12` |
| Construction | GF32 poly 37, alpha 2, natural order, `N=256`; TRAIN `2026091650..1652` x 256; DEV `2026091660..1664` x 128 = 640; masters `stream+10000`, domain-separated by arm/block; `B~p_b` then `A~f(.|B)`; per-stream + pooled worst-first orders frozen before DEV; permutations; min pairwise TRAIN Spearman `>= 0.95` L1 and L2; BEC `epsilon_l=H_l/5` report-only |
| DEV / truth | two paired arms per block; fresh per-layer SC restart; candidate-conditioned L2; `label_hat = low_hat + 32*high_hat`; one 64-bit Toeplitz comparison per viable candidate; truth only in sampling/disclosed values/tag construction/scoring; sentinel bitwise check |
| Accounting | `5*(45+140)+64 = 989` key-dependent bits per fully invoked arm (L1 225, L2 700, tag 64); `2623` public bits per tag; independent literal recount must equal incremental totals per arm and overall; reads/attempts `0/1 -> 1/1` at first content open, `retries=0` |
| Budgets | `ulimit -v 2097152` (2 GiB), `timeout 3600`; module wall cap 3600 s, RSS cap 2 GiB; TRAIN-phase breach raises with no writes, DEV-phase breach fills remaining blocks with `resource_abort`; projected wall ~136 s (~26x margin) |
| Schema | exactly `frozen_plan.json`, `construction_orders.json`, `per_block_paired_outcomes.json`, `aggregate_summary.json`, `report.md`, scalar/aggregate only |
| Integrity gates (frozen order) | `target_population_contract`, `coverage_complete_and_disjoint`, `orders_frozen_permutations_provenance`, `pairing_and_buckets`, `truth_leak_zero`, `undetected_zero`, `nonfinite_zero`, `resource_abort_zero`, `disclosure_and_recount_exact`, `attempt_read_accounting_exact`, `resource_limits_met` |
| Scientific gates | min pairwise TRAIN-order Spearman `>= 0.95` both layers; empirical exact `>= 620/640`; one-sided 95% Wilson LB `>= 0.95` with `z=1.6448536269514722` |
| Labels | all true at 640-pair shape -> `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`; integrity true + any scientific false -> `TARGET_EMPIRICAL_CONSTRUCTION_NOT_CONFIRMED`; integrity false -> `BLOCKED(<earliest gate>)`; precondition failure -> `BLOCKED(target_population_contract)` with no root |
| Command (never executed here) | `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` / `ulimit -v 2097152` / `timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_construction --counts <registered npz> --source 1M --n 256 --floor 1e-15 --train-seeds 2026091650 2026091651 2026091652 --train-blocks 256 --dev-seeds 2026091660 2026091661 2026091662 2026091663 2026091664 --dev-blocks 128 --k1 45 --k2 140 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate` (byte-identical across packet §P7-05, freeze §8, module `FROZEN_COMMAND`) |
| Root absence | `target_construction_gate/` absent at review time (verified twice) |

---

## 3. Review item #1 adjudication (operator-flagged entropy functional)

### 3.1 (a) Claimed magnitude of the floor-induced entropy shift — CONFIRMED

Reproduced with the reviewed code on a synthetic V25-like sparse mimic
(2541 nonzero cells, ~2.48 per Bob column; `tc.target_entropies`):

| functional | mimic shift | operator claim |
|---|---|---|
| `floor_h1 - h1` (A-level floor) | `4.263e-11` (`4.264e-11` second seed) | `4.27e-11` / ~`4.3e-11` |
| `floor_h2 - h2` (A-level floor) | `8.540e-12` | `8.5e-12` |
| `floor_total - total` | `5.117e-11` (`5.118e-11`) | `5.118e-11` |

Mechanism: the floor is applied to all 1024 cells of each column, so a zero
`u1` row of the derived `P1` receives 32 aggregated floors (`32e-15/Z`) whose
own entropy contribution is `~32e-15 * 44.8 * (#zero u1 rows) ~ 4.3e-11`; the
`P2` group floors contribute `~8.5e-12`. The u1-level (V49-style) floored
entropy shift is also reproduced (`1.479e-12`), and the V49 CSV's own recorded
difference `ent - nll_u1 = 1.5420e-12` is consistent with it. The magnitudes are
data-dependent within a plausible sparse-count band but robustly exceed
`1e-12` by 1–2 orders of magnitude.

### 3.2 (b) Contract reading — the population functional is the only self-consistent one

- The packet literals `0.02428054681872374 / 0.7767572780789994 / 0.8010378248977232` are **exactly** the V49 CSV `1M/TRAIN` `nll_u1/nll_u2/nll_total` columns (`docs/v49_distribution_tables/v49_train_val_hold_nll.csv`); V49 computes these as pair-mean NLLs of the raw-count MLE prior (`scripts/v49_diagnose_distribution.py:59-123`). On the same population they equal the raw-MLE in-sample conditional entropies up to the tiny u1-level floor renormalization term `avg log2 Z_b ~ 4.3e-14` — which is exactly the operator's `<= 5e-14` match claim, independently derived here.
- TASK_PACKET §P7-02 deliberately separates the `1e-12` literal checks (preconditions 3–5) from the separate `<= 1e-9` "floor-induced total-entropy change relative to raw MLE" (precondition 6). If preconditions 3–5 were read as entropies of the floored table, precondition 6's own floor change (`~5.1e-11 > 1e-12`) would make 3–5 unsatisfiable; the packet's thresholds are only jointly satisfiable on the population reading.
- The strict reading also fails at the u1 level (`1.5e-12`), and the frozen literals cannot be the V49 `ent` column (that value differs by `1.54e-12`). The A-level floored reading fails by `~4.3e-11`.
- Code and freeze documents record both functionals explicitly (`target_construction.py:501-536`, `P7_FREEZE.md:66-92`), and the floor functional is used only for the `<=1e-9` guard. This is not a silent deviation; it is the unique reading of the packet.

Verdict for item 1: **acceptable — ratified**, not a contract deviation.

### 3.3 (c) Ratified frozen semantics (binding for this attempt and its Pre-RESULT review)

1. Preconditions 3–5 compare the **raw-MLE in-sample population conditional entropies** of the loaded `1M` counts — `H1 = sum_b p_b H(P1_raw(.,b))`, `H2 = sum_b p_b sum_u1 P1_raw(u1|b) H(P2_raw(u1,b,.))`, `total = H1+H2`, exact-zero convention `0 log 0 = 0`, `P1_raw/P2_raw = derive_p1/derive_p2(counts / column totals)` — against the literals with tolerance `1e-12`.
2. Precondition 6 compares `|floor_total - population_total| <= 1e-9`, where `floor_*` is the same functional chain evaluated on the A-level floored/renormalized protocol table (`max(cell, 1e-15)` then column renormalization).
3. The sampled protocol law remains the floored table; the checked entropies are the raw-MLE population values; the floored-table entropies are reported (`floor_h1/h2/total/floor_entropy_change`) but must never be gated against the literals.
4. The Pre-RESULT review must recompute exactly these semantics from the five artifacts and reject any post-hoc reinterpretation (e.g. re-checking the literals against `floor_*`).

Residual risk (accepted by this review): the `<= 5e-14` match cannot be
independently recomputed without opening the artifact; it rests on the V49 CSV
identity plus the derived floor term. The path is fail-closed: a mismatch
returns `BLOCKED(target_population_contract)` before any genie/SC call and
before any output root, consuming the read/attempt with no rerun. The main
thread should accept this residual explicitly.

---

## 4. Blocking issues

None.

## 5. Non-blocking observations (for the record; no repair required for PASS)

1. `orders_frozen` is passed to the integrity gates as a constant `True` (`target_construction.py:1805`); the operative checks are the canonical digest recomputed after DEV (`:1790`) and the permutation/provenance flags. Freeze-before-DEV is guaranteed by code order (`:1696-1718` before `:1738`) and test evidence. Consider deriving the flag if this pattern is reused.
2. `report.md` renders gates, cells, entropy, stability, disclosure and planning-`f`, but not the per-stream table or per-arm bucket counts (those live in `aggregate_summary.json`, meeting the packet's reporting requirement at the five-file level). Rendering the per-stream lines would help the Pre-RESULT read-through.
3. WSL `resource.getrusage().ru_maxrss` is unreliable in this environment: it reported a constant `1,173.1 MB` that did not track a deliberate 500 MB allocation while `/proc/self/status VmHWM` tracked correctly. Both readings are below 2 GiB, so `resource_limits_met` passes; however the module's RSS gate cannot by itself detect a hypothetical >2 GiB breach. The external `ulimit -v 2097152` bounds that risk.
4. Attempt/read accounting is self-reported (`open_count: 1` written after the single verified call site `:1597`) and re-verified internally; no instrumented open counter exists. Code and audit-hook evidence cover the one-shot requirement.
5. The runner-level precondition-failure path has no dedicated unit test (the focused tests exercise `target_preconditions` directly and the size/root/node-missing refusals). This review verified the runner path directly (zero SC/genie calls, no root). A one-test addition would close the gap at the next touch.

## 6. Checklist

- [x] Matches OpenSpec spec (P7 delta == packet, no box checked)
- [x] Tests pass (11 focused + 228 total on the pinned interpreter; fresh basetemps)
- [x] No scope creep (declared file set only; accepted modules untouched; old roots untouched)
- [x] No blocking issues
- [ ] docs/decision-log.md or docs/troubleshooting.md update → not required for Pre-EXECUTE; the main thread already recorded the X07 disposition and P7 freeze in `docs/decision-log.md` and `AGENT_PROJECT_MEMORY.md` (2026-09-14 02:27). Any new finding belongs in the Pre-RESULT cycle.

## 7. Closure statements

- The V25 `channel_counts.npz` was **not opened** by this review; only `stat` metadata (size 25,166,822 bytes) was read. Audit-hook runs of the focused file and the full NB-Polar suite recorded zero non-temp opens of `channel_counts`/Model-F/parquet/TTBin/V25/held-out paths.
- No Model-F, raw, held-out or real-frame data was read; no old-root writes occurred; the sibling checkout was only `stat`-ed.
- The frozen command was **not executed**; the only runs used injected synthetic tables in temp roots.
- Artifact reads / attempts remain **0/1** and **0/1** (STATUS.yaml unchanged); the frozen output root remains **absent**.
- HEAD remains `ab173f2a5e17336383a897b941080b731ba3dd9e`; no commit or push was made.
- This review wrote only this file.

Verdict: **PASS** — proceed to the main-thread Pre-EXECUTE record and the single authorized frozen run, preserving the ratified §3.3 entropy semantics.
