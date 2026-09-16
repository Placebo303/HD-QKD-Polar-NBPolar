# FOCUSED_REVIEW.md — NBPOLAR-X01-PROBE-TIER-BOOTSTRAP

- Reviewer: reviewer-go (focused numerical review, Tier-X scope).
- Date: 2026-09-13.
- Contract: `workspace/probes/nbpolar_x01_20260913/prereg.md` (frozen),
  `workspace/probes/nbpolar_x01_20260913/results.json`,
  `.workbuddy/queue/NBPOLAR-X01-PROBE-TIER-BOOTSTRAP/{TASK_PACKET.md,STATUS.yaml,PROMPT.md}`,
  `AGENTS.md` §10.4, `docs/nbpolar/PROBE_TIER.md`.
- Method: read-only audit; independent recomputation and four independent
  in-memory spot reruns. The only file written is this review.

## Verdict: focused review PASS (no blocking issues)

This is **not** a scientific acceptance and **not** a candidate/accepted token.
It consumes no attempt, changes no scientific status, and cannot promote
previously accepted evidence. It recommends the next Tier-Y decision
experiment(s) only.

## 1. Write-scope audit — PASS

Probe root `workspace/probes/nbpolar_x01_20260913/` contains **exactly two
files** (no script file, no hidden files):

| file | size (B) | mtime (+0800) |
|---|---|---|
| `prereg.md` | 8497 | 2026-09-13 15:51:04.545 |
| `results.json` | 102429 | 2026-09-13 16:02:36.423 |

- Probe command window from `results.json.commands`: first command
  15:55:48, frozen execution 15:57:08–16:00:31, final writer 16:02:36.
  `prereg.md` mtime (15:51:04) is **before** every execution → prereg untouched
  after the run. PASS.
- Repo files modified inside the probe window (15:50–16:05): only
  `workspace/probes/nbpolar_x01_20260913/results.json`. No `*.pyc` written in
  the window. `comparison_bench/outputs_comparison/` untouched (mtime
  2026-09-12); this checkout has no `results/` root.
- Outside-root writes attributable to the probe execution are the **declared
  `/tmp/x01_*` capture files only** (14 files, all created/updated
  15:55:48–16:02:36, listed in the logged commands n=1..n=7; e.g.
  `/tmp/x01_body.log` sha256 `c1934200e5d5ff0ce2890d04cbe29044126c5658175f125019c09ee59a2d14d7`,
  `/tmp/x01_body_fixed.log` sha256 `420031ce6d8adfb4b24b0da236378dbf8fdb9c8b2618e2a847806a6ad33466d7`).
  No repo path outside the probe root was written by the logged probes.
- No artifact/real-data access anywhere in the logged commands: occurrences of
  `Data`, `artifact`, `parquet`, `TTBin`, `Model-F`, `pairs`, `csv`,
  `results/`, `outputs_comparison` in the command log = 0. The only `raw`
  occurrences (8) are the n=7 writer's local variable
  `raw = json.loads((ROOT / "results.json").read_text(...))`.
- Repo deliverables in the packet window: queue docs
  (`TASK_PACKET.md`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `STATUS.yaml`),
  workflow-rule docs (`AGENTS.md` §10.1 item 4 + §10.4, new
  `docs/nbpolar/PROBE_TIER.md`, `docs/nbpolar/WORKBUDDY_LIFECYCLE.md`,
  `docs/nbpolar/DOCUMENT_INDEX.md` rows, OpenSpec change
  `nbpolar-probe-tier-and-decision-gate-slimming/`), the probe root, and this
  review. The main-thread milestone ledger batch at 15:41:23
  (`CURRENT_TASK.md`, `docs/decision-log.md`, `AGENT_PROJECT_MEMORY.md`)
  predates authorization and the probe, is main-thread-owned per AGENTS.md
  §10.1, and contains no probe numbers (grep for `0.2325`, `2026091400`,
  `298.0`, `273.4` = none). Attribution note in NB-4.
- `STATUS.yaml` flags are consistent with a non-claim probe
  (`artifact_read_authorized: false`, `real_data_authorized: false`,
  `claim_bearing_execution_authorized: false`, `scientific_promotion: false`).

## 2. Prereg discipline — PASS

- `prereg_sha256` recorded `761821c3efeac12b2a14be2a4ecf4262d9e682ab5474d3a685bf0cf6e9b99662`
  equals the current sha256 of `prereg.md`. PASS.
- Executed body fidelity, recomputed by me:
  - expected frozen body = prereg lines 33–179 with the uniform 3-space indent
    stripped → sha256 `c1934200...d14d7` = recorded `frozen_body_sha256` =
    `/tmp/x01_body.log` sha256;
  - executed body = recorded `executed_stdin_body_text` → sha256
    `420031ce...33466d7` = recorded = `/tmp/x01_body_fixed.log` sha256;
  - unified diff frozen → executed is exactly one insertion at `4a5`:
    `from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer  # X01-FIX: register the two_layer submodule for nb.two_layer`.
    No parameter, model, seed, N, block count or semantics line differs.
- Seven logged executions, every rerun included:

| n | kind | exit | window (UTC) |
|---|---|---|---|
| 1 | heredoc body extraction | 0 | 07:55:48 |
| 2 | preflight (no decode, no writes) | 1 | 07:55:58–07:56:00 |
| 3 | execution fix (script only) | 0 | 07:56:46 |
| 4 | preflight 2 (no decode, no writes) | 0 | 07:56:56–07:56:58 |
| 5 | frozen five-seed execution | 0 | 07:57:08–08:00:31 |
| 6 | writer attempt 1 (no decode) | 1 | 08:01:55–08:01:57 |
| 7 | writer attempt 2 (final results.json) | 0 | 08:02:34–08:02:36 |

- Failure fix 1 (n=2 → n=3): preflight `AssertionError: nb.two_layer missing`
  (`nbpolar/__init__.py` does not import the `two_layer` submodule); fixed by
  the single body import insertion above. Confirmed independently: a fresh
  process reproduces `AttributeError: module ... has no attribute 'two_layer'`
  without the import, and `__init__.py` (mtime 10:41, an earlier packet) still
  has no `two_layer` import. The repo module was not modified by this packet.
- Failure fix 2 (n=6 → n=7): writer `AttributeError` at its line 128 on
  `nb.two_layer`; the only write in the n=6 body is its line 332
  (`results.json`), never reached → failed writer wrote nothing. The n=6→n=7
  writer diff is post-processing-only (see NB-1); it does not touch frozen
  probe parameters, models, seeds or the n=5 raw data (n=7 reads
  `results.json` and reformats it).
- No parameter/model/seed changed after prereg. PASS.

## 3. Five-seed completeness — PASS

| family | seeds | N | blocks | registered params |
|---|---|---|---|---|
| `p5_k45` | 2026091400..1404 (5) | 256 | 300 | K=45, epsilon=0.05 |
| `r1_three_arm` | 2026091410..1414 (5) | 256 | 300 | three arms, K=(29,33,37,41,45), epsilon=0.05 |
| `p4_independent` | 2026091420..1424 (5) | 256 | 96 | eps1=0.05, eps2=0.20, K1=45, K2=110 |
| `p4_dependent_l2` | 2026091430..1434 (5) | 256 | 96 | eps1=0.05, eps2(u1)=0.08+0.24*u1/31, K1=45, K2=110 |

- Each family has exactly the registered five seed values; `n=256` and the
  block counts 300/300/96/96 are recorded per family config. PASS.
- Dependent kernel: `eps2_u1() = 0.08 + 0.24*arange(32)/31` (endpoints
  0.08/0.32, mean 0.20); the table builder indexes it by the high-layer symbol
  (`e2[hi]`, `hi = u1`) and the sampler by `e2[high]`. Formula matches the
  prereg. PASS.
- Masters = run_seed + 10000: verified per family (see §4); recorded default
  masters match the modules (`protocol` 2026091318, `incremental` 2026091341,
  `two_layer.FROZEN_TOEPLITZ_MASTER` 2026091361). PASS.

## 4. Arithmetic recomputation — PASS

All 64 aggregate keys (mean / sample-std(n-1) / range) across all four
families were recomputed from the recorded per-seed values:
**0 mismatches, 0 float differences** (exact equality of means, `stdev` and
ranges). 115 accounting identities also checked, **0 failures**:

- per-seed outcome sums exactly equal 300 (P5, each R1 arm) or 96 (each P4
  arm); `failure == decode_failed + verify_failed + resource_abort` in every
  row, so `undetected` is reported separately and never merged into failure;
- every P4 arm row has `key_dependent_bits_total == 80544`
  (= 96*(5*(45+110)+64)) and `public_control_bits_total == 251808` (= 96*2623);
- all `undetected` and `resource_abort` counts are 0.

Dependent pre-decode proof, independently recomputed by rebuilding the
dependent table from the frozen formula (verbatim helper):

- column-sum max deviation = `3.3306690738754696e-15` (recorded same) ≤ 1e-12 → PASS;
- `max_{u1,u1',b,u2}|P2[u1,b,u2]-P2[u1',b,u2]|` frozen formula
  = `0.2325000000000006` (recorded same) ≥ 0.10 → PASS;
- pairwise sup form `(P2.max(0)-P2.min(0)).max()` = `0.2325000000000006`
  (recorded same) → PASS; `family_decoded = true`;
- independent table gap recomputed `7.771561172376096e-16` = recorded.

Master-parameterization verification, independently recomputed (same module
functions, SHA-256 counter reference stream, 2623 bits):

| family / seed | master | expected-master match | differs from pristine default |
|---|---|---|---|
| P5 2026091400 | 2026101400 | true | true |
| R1 2026091410 (static, incremental arms) | 2026101410 | true, true | true, true |
| P4 2026091420 (operational, oracle arms) | 2026101420 | true, true | true, true |

All equal the recorded check rows. PASS.

## 5. Independent spot-check (one seed per family) — PASS

Independent in-memory reruns (no writes) reproducing the frozen body exactly;
counts compared to `results.json`:

| family / seed | recomputed (exact / failure / decode_failed / verify_failed) | recorded | match |
|---|---|---|---|
| p5_k45 / 2026091400 | 296 / 4 / 3 / 1; kdb 86508; pcb 779031 | same | yes |
| r1_three_arm / 2026091410 static | 300 / 0 / 0 / 0; kdb 86700; pcb 786900 | same | yes |
| r1_three_arm / 2026091410 strict_stop | 278 / 22 / 22 / 0; kdb 62300; pcb 760682 | same | yes |
| r1_three_arm / 2026091410 r1 | 300 / 0 / 0 / 0; kdb 64452; pcb 821045 | same | yes |
| p4_independent / 2026091420 operational | 23 / 73 / 0 / 73; kdb 80544; pcb 251808 | same | yes |
| p4_independent / 2026091420 oracle | 40 / 56 / 0 / 56; kdb 80544; pcb 251808 | same | yes |
| p4_dependent_l2 / 2026091430 operational | 23 / 73 / 0 / 73; kdb 80544; pcb 251808 | same | yes |
| p4_dependent_l2 / 2026091430 oracle | 39 / 57 / 0 / 57; kdb 80544; pcb 251808 | same | yes |

Every recomputed field matched exactly (including all eight count fields and
both bit totals per arm). P4 spot check also reported 0 `truth_leak_violation`
flags in the recomputed operational+oracle arms. PASS. This is a Tier-X
arithmetic/consistency check, not a claim.

## 6. Truth isolation — PASS

Verified from the probe body and the accepted module APIs:

- P5: body calls `protocol.execute_blocks(run_seed=s, blocks=300, n=256, k=45)`
  only; internally `generate_erasure_block` → `run_static_block`, where the
  decoder receives only `logp` and the disclosed `U[D]` (`sc_decode(...,
  known_positions=positions, known_values=disclosed)`, protocol.py L313–319);
  Alice truth is confined to the transform, disclosure, scoring and Bob-side
  tag comparison, and the in-module truth-isolation sentinel (L354–358)
  checks decision arrays do not alias truth buffers.
- R1: body calls frozen `incremental.run_three_arm_block`; the three arms each
  decode from Bob's `logp` with `known_values=disclosed`
  (incremental.py L532–537, L691–696); truth (x) is used only for
  transform/disclosure/score/tag. Probe discards `y`; no override seams are
  used (`tag_fn`/overrides default).
- P4: body calls frozen `two_layer.run_two_layer_block` with defaults for all
  test seams. Operational arm: P1 metric from Bob only (two_layer.py L640–641),
  L2 metric conditioned on the decoded candidate (L666–669), one tag over the
  public seed; the oracle arm is a labelled diagnostic that receives the true
  high layer (L736–739). The operational decoder/metric/tag path receives no
  oracle value and no hidden truth beyond the registered disclosures.
- No artifact/real-data/Model-F access in any command; all arithmetic in
  memory; the dependent pre-decode proof is evaluated before any decode.

## 7. No-claims audit — PASS

- `results.json` contains no candidate/accepted token, no pass/fail verdict on
  the probe hypotheses, no attempt accounting, no status change, and no pooled
  cross-family metric. All occurrences of `candidate` are inside the explicit
  negation "No pass/fail, threshold verdict, candidate, attempt accounting or
  scientific status is computed"; all occurrences of `accept*` describe
  *accepted module semantics*; `attempt` occurrences describe logged execution
  attempts.
- The only threshold-like item is the registered model-validity precondition
  `dependent_model_p2_maxdiff >= 0.10` recorded as `passed: true`. The packet
  itself required this pre-decode proof ("normalize ... and verify ... before
  decoding"), so it is required evidence about model validity, not a
  claim-bearing performance threshold. Report structure is per-seed +
  mean/std(n-1)/range per family per arm. PASS (context note NB-3).
- `prereg.md` is the frozen question/parameters/command; it contains no
  results and no verdict.

## 8. Non-blocking observations

- **NB-1 (writer rerun changed more than one line).** The n=6 → n=7 writer
  diff is not only the import line: it also expands `p4_seeds` to both P4
  families (n=6 checked only `p4_independent` seeds), renames
  `default_master_python312_temporary` → `default_master`, and adds the n=6
  failure entry to `commands`. This is post-processing verification code; it
  does not alter the frozen probe parameters, models, seeds, or the n=5 raw
  data (n=7 reads and reformats the raw `results.json`). Recorded here for
  transparency; no action required.
- **NB-2 (outside-root `/tmp` captures).** The probe wrote 14 `/tmp/x01_*`
  capture files as declared execution plumbing. This is a literal deviation
  from "write only under `workspace/probes/<id>/`", but it is temp-only,
  non-repo, fully listed in the command log, and anticipated by the packet's
  own review checklist. Recommend that future Tier-X packets declare a
  permitted scratch-log location in the prereg so the scope rule and the
  audit checklist agree.
- **NB-3 (wording).** `dependent_model_predecode_proof.passed` and
  `threshold: 0.1` use claim-like words for what is a registered model-validity
  precondition. Not a claim; consider `precondition_satisfied` next time.
- **NB-4 (doc drift; main thread).** `DOCUMENT_INDEX.md` still says X01
  "frozen all-false; awaiting authorization" and the OpenSpec change
  "proposed; not enacted", while `STATUS.yaml` is authorized and the rule text
  has landed. OpenSpec `tasks.md` boxes remain unchecked by design
  (`IMPLEMENTATION_NOTE.md`). Batch at the next milestone; no probe action.
- **NB-5 (prereg length).** `PROBE_TIER.md` says "exactly three lines"; the
  actual prereg is a three-section document whose command section must
  reproduce the full heredoc. Semantically compliant; consider softening the
  template wording.
- **NB-6 (raw first record overwritten).** The final `results.json` is a
  re-formatted derivative of the raw n=5 output; the raw n=5 bytes were
  overwritten by n=7, so byte-level fidelity of the raw file cannot be checked
  retroactively. Mitigated: one-seed-per-family independent reruns reproduce
  the recorded per-seed counts exactly and all aggregate arithmetic recomputes
  exactly. Recommend that future probes either write the final schema directly
  from the frozen body or preserve the first raw record as a separate file.

## 9. Recommendation — next Tier-Y decision experiment(s)

Based on the five-seed dispersion (recorded values):

| point | metric | mean | sample std | range |
|---|---|---|---|---|
| P5 K45 | exact | 298.0 | 1.2247 | [296, 299] |
| R1 static | exact | 299.2 | 1.0954 | [298, 300] |
| R1 strict-stop | exact | 273.4 | 5.5946 | [267, 280] |
| R1 advance | exact | 299.2 | 1.0954 | [298, 300] |
| P4 independent | operational exact | 23.2 | 6.6106 | [12, 29] |
| P4 independent | oracle exact | 37.8 | 7.3621 | [25, 44] |
| P4 dependent L2 | operational exact | 27.6 | 4.6152 | [23, 33] |
| P4 dependent L2 | oracle exact | 42.0 | 2.5495 | [39, 46] |

- **Single-layer R1-vs-static replication (recommended first Tier-Y).** The
  paired exact difference is exactly 0 in 5/5 seeds (static = R1 = 299.2 ±
  1.10); paired key-dependent-bits difference is 20831.2 ± 886.3 bits
  (~23.5 sample-std), i.e. R1 is disclosure-lighter at equal exact count. A
  frozen single-layer Tier-Y gate at N=256, 300 blocks, with e.g. a
  non-inferiority margin of R1 exact >= static exact - 4 (≈3.7 sample-std) or
  a paired key-dependent-bits threshold around +15k bits is variance-supported
  by this probe. strict-stop separation is also well-resolved (paired
  difference 25.8 ± 4.66 blocks; e.g. strict <= static - 10 is ≈3.4 std).
- **P4 two-layer gate (needs more power).** At 96 blocks the operational exact
  dispersion is ±4.62 (dependent) / ±6.61 (independent); a single 96-block
  draw cannot discriminate differences below ≈9 blocks, and the observed
  dependent-vs-independent operational means differ by only 4.4 blocks
  (SE ≈ 3.60, ≈1.2σ). Do not freeze a 96-block single-seed threshold. If a
  Tier-Y gate is desired: (a) use the **dependent-L2 model** (P2 maxdiff
  0.2325) for any paired L1→L2 gate, because the independent model is
  metric-degenerate (P2 maxdiff 7.77e-16, so candidate conditioning cannot be
  tested at the metric level); (b) power it with >=300-400 blocks per seed or
  more seeds; and (c) prefer the operational-vs-oracle gap as the endpoint -
  under the dependent model the 5x96 signal is ~14.4 blocks (SE ≈ 2.36,
  ≈6σ), whereas absolute operational exact sits near a ~71% failure rate and
  is a poor threshold target.
- Cite this X01 record as the prior Tier-X variance/sensitivity evidence in
  any frozen Tier-Y threshold (per AGENTS.md §10.4), and keep the dependent
  pre-decode proof as a frozen model-validity precondition.

## 10. Checklist

- [x] Matches OpenSpec spec (W-01/W-02 landed in AGENTS.md/PROBE_TIER.md;
  W-03..W-06 present in the probe root; W-07 is this review; `tasks.md` boxes
  left unchecked — NB-4).
- [x] Tests/evidence pass (no unit-test requirement for Tier X; 64/64
  aggregate keys, 115/115 identities, all four spot seeds exact).
- [x] No scope creep (probe writes confined to the probe root + declared /tmp
  captures; ledger batch predates authorization and contains no probe results).
- [ ] `docs/decision-log.md` / `docs/troubleshooting.md` update? Not for this
  probe (Tier X forbids per-probe ledger updates). Recommend recording the X01
  dispersion table and the chosen next Tier-Y point in the next milestone batch.

## Closing statement

Focused review verdict: **PASS** (no blocking issues; non-blocking observations
NB-1..NB-6). This review is a Tier-X arithmetic/consistency/completeness audit
only. It is **not** a scientific acceptance, creates **no**
candidate/accepted token, consumes no attempt, and recommends the next Tier-Y
decision experiment without enacting it.
