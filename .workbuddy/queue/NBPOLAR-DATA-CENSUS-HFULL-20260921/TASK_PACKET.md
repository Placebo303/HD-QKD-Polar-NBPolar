# TASK PACKET — NBPOLAR-DATA-CENSUS-HFULL-20260921 (zero-decoder H_full census, 10 NEW raw acquisitions)

PREPARATION ONLY packet. Execution requires explicit user authorization
(AUTHORIZATION_PROMPT.md pasted by main thread). Operator executes later.
Per AGENTS.md §10.1: freeze one complete packet before delegation.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verified 2026-09-21, DO NOT SWITCH): `codex/nbpolar-phase0`
- Packet dir: `.workbuddy/queue/NBPOLAR-DATA-CENSUS-HFULL-20260921/`
- Intake script (skeleton, NOT executed): `scripts/census_intake_20260921.py`
- Sibling venv (TimeTagger 2.22.6 installed, numpy 2.5.3):
  `/home/karel_303/.venvs/timetagger/bin/python`
  (this checkout has NO `.venv`; use the timetagger venv for ALL execution)
- Nature: **non-claim descriptive census** (no FER, no qualification, no
  promotion). Per Tier-X/§10.4: must NOT update decision-log / project memory
  / indexes (batch at milestone).

## 1. Established facts (frozen, verbatim from tasking — do not re-derive)

### 1.1 Data — 10 acquisitions, 20 files, 349,249,648 B ≈ 333.1 MiB
Source: `docs/nbpolar/RAW_DATA_INVENTORY_20260921.md` +
`workspace/data_intake_20260921/inventory.json`. WSL root: `/mnt/d/Data/Raw Data/`.
Exact sub-paths per inventory.json (operator MUST read paths from inventory.json,
not reconstruct from stems).

Type-II-labeled (6): `20260112_Type2PPLN_3s` 16.1 MiB;
`20260113_SHG_Type2PPLN_3s` 56.6; `20260113_SHG_Type2PPLN_3s_2` 57.3;
`20260121_Type2_1-5M_3s` 29.6; `20260121_Type2_1M_3s` 21.0;
`20260121_Type2_2M_3s` 39.9.
Type0 (4): `20260120_Type0_nofilter_500K_3s` 12.6; `1M` 22.2; `1_5M` 31.9;
`2M` 45.7.

**PI RULING 2026-09-21: Type0 and SHG are only SOURCE differences and have NO
effect on the IR process. ⇒ ALL 10 acquisitions are in scope. Any
`TYPE0_SOURCE_UNVERIFIED` exclusion language in the inventory doc / JSON
(source_type_verbatim fields) is SUPERSEDED and must not gate execution.**

All 10 `NOT_REGISTERED`, `LIKELY_NEW_SESSION`.

### 1.2 Frozen pipeline contract (Release + NB-Polar survey)
- `d=1024`, `bin_width_ps=200`, `period_ps=204800`, `pairing=nearest`,
  `rule=legacy_v1`, `frame_pairs=256`, `gate_ps=200`, `threshold_ps=40000` —
  single source `scripts/v66_data_readiness.py:11` (FROZEN dict).
- Channels: interleaved single stream, per-record channel id;
  **logical A = hardware 1, B = hardware 5**, FIXED by contract, NOT searched
  (`scripts/v65ar2_pipeline.py:232` records `searched_channel_pair:False`).
  Ambiguity guard: other/total > 0.20 ⇒ FAIL (`:143-147`).
- `<<SEARCH>>` delay per acquisition: `_estimate_peak_stats_from_timetags`
  (`src/workflow/export_joint_sequence_sidecar.py:715`) invoked ONCE per
  acquisition on that acquisition's OWN timetags with frozen scan params
  `scan_range_ps = max(50_000, 2*204800) = 409600`, `bin_ps = max(10, 200//2)
  = 100`, `frame_period_ps` NOT passed (passing it would trigger the
  function's internal 20M clamp and override the frozen range). No grid
  search over ranges/bins, no second invocation.
  R1 REWRITE 2026-09-21 (PI alignment instruction — SUPERSEDES the old gate
  `|delay−peak| < 50 ps`, `sigma ∈ [50,150]`, gate=200, threshold=40000, which
  was calibrated for the 01-21 V25 sources and is inapplicable to new
  sources): acceptance is unit-independent — `status == "ok"` AND
  `peak_to_bg >= 10` (contrast ratio, scale-free). Report `peak_center_ps`,
  `peak_sigma_ps`, `peak_to_bg` for every acquisition regardless. Reject only
  on `status != "ok"`, `peak_to_bg < 10`, or no peak found ⇒ `ALIGN_FAIL`,
  exclude, continue. Never tune, never widen, never retry with other scan
  params. The derived offset (`peak_center_ps`, applied as
  `tA_aligned = tA_raw + offset`) must MAXIMIZE pairing yield: sweep offset
  over the search range at a coarse step, report yield vs offset, require the
  derived offset at or within one coarse step of the yield maximum —
  otherwise `ALIGN_INCONSISTENT` (recorded, never silently passed).
  **Frozen −50/+50/+50 belong to the 01-21 V25 sources and MUST NOT be inherited.**
  Rationale (recorded): `legacy_v1` pairing only needs timestamp/bin-width/
  superframe unit-self-consistency; what breaks pairing is a wrong OFFSET. A
  correlation-derived offset in raw units is correct under any unit reading ⇒
  auto-alignment makes pairing immune to the ps-vs-0.1ps ambiguity, which now
  affects only physical interpretation and cross-session comparability.
- Binning: `b = floor_divide(t, 200)`; legacy_v1 coincidence = same `//1024`
  super-frame (`src/reconciliation/run_nbldpc_demo_point.py:135-136,150-156`).
- Framing: chunk pair stream into consecutive **256-pair frames**, assert
  `n % 256 == 0` (`scripts/v65ar2_pipeline.py:258-261`).
- Mapping: `symbol = low + 32*high`, `U1 = s>>5`, `U2 = s&31`
  (`comparison_bench/src/comparison_bench/formal_ir/v72p2d5_model_f_input.py:166`;
  NOTE: correct path is `formal_ir/`, not `methods/`).
- `counts_ab[A,B]` shape (1024,1024) int64; `p_b` = column marginal, must match
  within 1e-12 (`v72p2d5_model_f_input.py:147-149`).

### 1.3 THE H ESTIMATOR DECISION (main thread ruled — record, do not relitigate)
- **PRIMARY: factorized chain** `H1 = H(U1|B_full)`, `H2 = H(U2|U1,B)`,
  `H_total = H1+H2`, canonical raw-count MLE + 1e-15 floor
  (λ concentration program REFUTED for target priors — X08, `docs/decision-log.md`;
  raw+floor only).
- **SECONDARY: flat full-joint `H_full`** (v70 `hierarchical_P`
  `(C+λ·p_global)/(n_b+λ)`, λ by 30-point 4-fold CV,
  `scripts/v70_binary_soft_joint_feasibility.py:33-100,262-296,439-440`),
  reported ONLY for comparability with `v70_table.csv`, **never in the same
  comparison column** as the factorized chain.
- Rationale: CAL holds 262144 symbols over 1,048,576 cells (0.25 counts/cell;
  1,046,140 zero cells; ~2–3 live Alice symbols per Bob column), so a flat joint
  model cannot exploit the ±1 structure and degrades to ~7 bits, whereas the
  factorization reaches ~0.825.
- Frozen reference values (BOTH conventions, all three sessions):

| session | H1 | H2 | **H1+H2 (primary)** | v70 `CAL_H_full` |
|---|---|---|---|---|
| `20260123_1M_600k_0dB` | 0.02428054681872374 | 0.7767572780789994 | **0.8010378248977231** | 7.135005172802673 |
| `20260107_PPLN_1p5M` | 0.02519949692375297 | 0.8003665547495433 | **0.8255660516732963** | 7.523243697268693 |
| `20260123_2M_1p2M_0dB` | 0.02566204884275839 | 0.8069006731309893 | **0.8325627219737477** | 8.385623861090046 |

### 1.4 Blocking unknown — Stage A0 enables, Stage A resolves first
**Census blocked on environment: `.ttbin` is opaque TimeTagger format, read only
via `from TimeTagger import FileReader` (`src/qkd_io/ttbin_pipeline.py:148`).
WSL has no such package; Windows does. Resolution (verified from PyPI JSON
2026-09-21, do not re-research): package **`Swabian-TimeTagger`** (owner
`swabian`), latest **2.22.6** (released 2026-09-08), requires Python >=3.8,
numpy>=1.23.0, **glibc >= 2.28**, Linux or Windows 10+. Linux wheel
`swabian_timetagger-2.22.6-cp38-abi3-manylinux_2_28_x86_64.whl`
(~32.7 MB; `cp38-abi3` ⇒ works with any Python >= 3.8; sibling venv numpy
2.5.3 is fine). Install command:
`<venv-python> -m pip install Swabian-TimeTagger`. WSL-native preferred over
Windows wheels (~29.2 MB `win_amd64` exist but are not the plan).
**CRITICAL namespace-mismatch risk:** repo code does
`from TimeTagger import FileReader`, but the official PyPI package (>= 2.20)
exposes `from Swabian import TimeTagger as TT` — the bare `TimeTagger`
top-level name may not exist after install. Fallbacks in order: (1) preferred —
`Swabian`-import shim at the top of `scripts/census_intake_20260921.py`
(BEFORE any `src.qkd_io` import); (2) pin an older release that still ships the
bare name (`Swabian-TimeTagger==2.20.2` or `==2.21.2`, both with
manylinux_2_28_x86_64 wheels); (3) last resort, needs PI decision — Windows
install + export timestamps to neutral format (`.npy` int64 ps + channel id)
via Codex Desktop bridge, then consume from WSL (materially slower, avoid).
**Stage A0 (new §4) performs this enablement and must pass before Stage A.**

**.1.ttbin merge semantics.** Every primary `<stem>.ttbin` is 8–21 KiB while
`<stem>.1.ttbin` holds ~99.9% of bytes. Existing code takes
`sorted(glob("*.ttbin"))[0]` only (`scripts/v65ar2_pipeline.py:154-156`);
**zero** continuation/merge handlers exist in either checkout. `.ttbin` is opaque
TimeTagger format read only via `from TimeTagger import FileReader`
(`src/qkd_io/ttbin_pipeline.py:148`). If `FileReader` does not auto-follow `.1`,
running as-written silently drops ~99.9% of data.
**The user's hypothesis is that `FileReader` auto-follows `.1` segments; this
is UNVERIFIED and Stage A exists precisely to test it empirically.** Do not
assume it.

**STAGE A RESULT 2026-09-21 (SUPERSEDES the "UNVERIFIED" paragraph above and
the old union/concat acceptance wording in §§5–6): auto-follow CONFIRMED on
`20260112_Type2PPLN_3s` — `FileReader(primary)` and `FileReader(.1)` each
yield the IDENTICAL full acquisition: 3,836,088 / 3,836,088 events, identical
channel histograms ({1: 1952312, 5: 1873601, 1001: 10175}), identical
timestamp span (7486100101885435 → 7516100054295827 ps). Concatenating both
reads gives 7,672,176 = exact 2×, i.e. every event duplicated. ⇒ BINDING MERGE
RULE: read the PRIMARY `<stem>.ttbin` ONLY; never concatenate; never read
`.1` separately and add (intake script `stage_b_census` implements this).
The frozen `stage_a_parse.json` A5 `stage_b_go: true` with
`union-is-concat-use-both-files` is SUPERSEDED — Stage B as previously
scripted (concat) was NO-GO. Evidence JSONs on disk are frozen and unchanged;
the script now records `autofollow-confirmed-read-primary-only-concat-forbidden`.**

## 2. Allowed files
- READ: `docs/nbpolar/RAW_DATA_INVENTORY_20260921.md`,
  `workspace/data_intake_20260921/inventory.json`, `scripts/v66_data_readiness.py`,
  `scripts/v65ar2_pipeline.py`, `scripts/v65_data_readiness.py`,
  `scripts/v70_binary_soft_joint_feasibility.py`,
  `src/qkd_io/ttbin_pipeline.py`, `src/workflow/export_joint_sequence_sidecar.py`,
  `src/reconciliation/run_nbldpc_demo_point.py`,
  `comparison_bench/src/comparison_bench/formal_ir/v72p2d5_model_f_input.py`,
  `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`, `v70_data_registry.json`,
  `scripts/census_intake_20260921.py` (the intake skeleton itself).
- WRITE (additive only): `scripts/census_intake_20260921.py` (skeleton fixes only,
  operator must not redesign), `workspace/census_20260921/<acq_id>/` outputs,
  packet dir docs (`TASK_PACKET.md`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`,
  `STATUS.yaml` — status updates only).
- Raw `.ttbin` paths: READ via `FileReader` only. Never copy, move, or modify.

## 3. Forbidden (hard stop if touched)
- `experiments/run_e2e_pipeline.py` (frozen baseline entrypoint — never run on raw data).
- `tools/longrun_*`, `tools/minrerun_*`, `routeA_*` under `tools/` (AGENTS.md §5.6).
- ANY decoder import or call (zero-decoder census; census script must contain no
  decoder import — verified by grep in B6).
- ANY write into `results/` or `comparison_bench/outputs_comparison/`
  (AGENTS.md §5.2; census root is `workspace/census_20260921/` only).
- ANY modification of `src/`, `experiments/`, `tools/` (AGENTS.md §5.1).
- `git commit`, `git push`, `rm -rf`, package installs, network commands,
  large-scale formatting (coder constraints). EXCEPTION: the Stage A0-3
  `pip install Swabian-TimeTagger` into the sibling venv is an install action
  OUTSIDE the repo and requires its own SEPARATE explicit user authorization
  (AUTHORIZATION_PROMPT.md item B); the operator must never run it on Stage A/B
  authorization alone.
- `git checkout` / branch switch (branch `codex/nbpolar-phase0` verified — stay).
- Reading contents of untrusted results artifacts in data folders
  (`*.opju`, `*.CSV`, `results_*`, `e2e_new_ttbin_fullgrid_*`, sidecar
  `run_config.json`); names from inventory only.
- Copying the frozen −50/+50/+50 delays into any new acquisition (each
  acquisition gets its own single frozen-params delay invocation per §6 B1).
  The 702-frame skip DEFAULT (§6 B8, labelled `INHERITED_NOT_DERIVED` with a
  mandatory non-decision companion diagnostic) is the one preregistered
  exception — do not invent per-acquisition skips mid-run.

## 4. Stage A0 — ENVIRONMENT ENABLEMENT (must pass before Stage A)

Installs `Swabian-TimeTagger` into the SIBLING venv
`/home/karel_303/.venvs/timetagger/bin/python` (this checkout has no
`.venv`). **This modifies an environment OUTSIDE the repo — it is an install
action, not a repo edit, and requires SEPARATE explicit user authorization
(AUTHORIZATION_PROMPT.md item B), independent of the census execution
authorization (item A). Operator must not run A0-3 on Stage A/B authorization
alone.** Nothing is parsed beyond the one tiny smoke file in A0-5; no census.

Exact commands (run in order; record verbatim output for each):

```bash
# A0-1: glibc version (must be >= 2.28; STOP and report if not)
ldd --version | head -1
# A0-2: numpy version in the TARGET (sibling) venv
/home/karel_303/.venvs/timetagger/bin/python -c "import numpy; print(numpy.__version__)"
# A0-3 (REQUIRES separate install authorization — item B — do not run otherwise):
/home/karel_303/.venvs/timetagger/bin/python -m pip install Swabian-TimeTagger
# A0-4/A0-5 (after A0-3; script shim or 2.20.2/2.21.2 pin applied if needed):
/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py \
  --stage-a0-env-check --out-root workspace/census_20260921
```

| ID | Acceptance | Evidence |
|----|-----------|----------|
| A0-1 | glibc recorded via `ldd --version`, must be >= 2.28 (package wheel needs `manylinux_2_28`) | run log: `ldd` first line |
| A0-2 | numpy version in sibling venv recorded (expect 2.5.3; needs >=1.23.0) | run log: `numpy.__version__` line |
| A0-3 | `Swabian-TimeTagger` installed into the sibling venv ONLY, under separate install authorization | run log: pip output + install authorization reference |
| A0-4 | `from TimeTagger import FileReader` succeeds; record WHICH path worked: direct bare import, `Swabian`-import shim (in intake script top), or older-version pin (`==2.20.2` / `==2.21.2`) | `--stage-a0-env-check` output: `filereader_import_path` |
| A0-5 | `FileReader` constructs successfully on ONE tiny primary file only (`20260112_Type2PPLN_3s`, primary 8–21 KiB) | `--stage-a0-env-check` output: `smoke_construct_ok`, `n_events_primary_probe` |

Stage A0 stop rules: ANY adverse result (glibc < 2.28, numpy missing/incompatible,
install failure, `FileReader` still unimportable after shim AND pin attempts,
smoke construction fails) ⇒ STOP and report as concrete blocker (second return
condition), naming the failing ID and the single decision needed. Do NOT proceed
to Stage A. The Windows-export last resort (neutral `.npy` via Codex Desktop
bridge) needs a PI decision — operator must not start it unilaterally.
Pass = all A0-1–A0-5 recorded with `stage_a0_go: true`.

## 5. Stage A — PARSE-TEST GATE (one acquisition, must pass before Stage B; requires Stage A0 `stage_a0_go: true` first)

Target: smallest Type-II acquisition `20260112_Type2PPLN_3s`:
- primary: `/mnt/d/Data/Raw Data/2026.1.12/Type2PPLN_3s_2026-01-12_165236.ttbin`
- `.1`: `/mnt/d/Data/Raw Data/2026.1.12/Type2PPLN_3s_2026-01-12_165236.1.ttbin`
  (operator MUST confirm these two paths against inventory.json before running).

Exact command (sibling venv; this checkout has no `.venv`):

```bash
/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py \
  --stage-a-parse-test --acq-id 20260112_Type2PPLN_3s \
  --out-root workspace/census_20260921
```

Functionality: `read_ttbin_events` on (a) primary alone, (b) `.1` alone,
(c) union of both; record per file: event count, channel histogram, timestamp
min/max span; answer (a) does `FileReader(primary)` alone yield the full event
count? (b) separate yields? (c) union == sum of parts? (d) channel ids identical
across segments? Print PASS/FAIL verdict + write
`workspace/census_20260921/20260112_Type2PPLN_3s/stage_a_parse.json`.

| ID | Acceptance | Evidence |
|----|-----------|----------|
| A1 | Event count from `FileReader(primary)` alone recorded | `stage_a_parse.json`: `n_primary` |
| A2 | Separate counts for primary and `.1` recorded (`.1` expected ≈99.9% of union by bytes — counts recorded, not assumed) | `n_primary`, `n_cont1` |
| A3 | Union count recorded; equality `n_union == n_primary + n_cont1` checked. CORRECTED SEMANTICS (Stage A 2026-09-21): identical part-counts with identical histograms/spans PROVE duplication (concat = exact 2×), NOT disjoint parts — concatenation is forbidden, merge rule is primary-only | `n_union`, `union_is_sum: bool`, `autofollow_confirmed: true` |
| A4 | Channel histogram + timestamp span recorded for primary, `.1`, union; channel-id sets compared | `channels_{primary,cont1,union}`, `tspan_{...}`, `channel_ids_match: bool` |
| A5 | Merge verdict + comparability verdict recorded; GO/NO-GO for Stage B explicit. CORRECTED (Stage A 2026-09-21): expected verdict is `autofollow-confirmed-read-primary-only-concat-forbidden` with `stage_b_go: true` gating the FIXED primary-only Stage B. **Any adverse answer (parts differ, channel ids differ, primary read fails) ⇒ STOP, report, do NOT proceed to Stage B** | `merge_verdict`, `stage_b_go: bool`, `merge_rule` |

Stage A stop rules: adverse A5 ⇒ return as concrete blocker (second return
condition), naming the failing ID and the single decision needed (main thread:
new merge rule). Missing `TimeTagger` package at Stage A ⇒ blocker meaning
Stage A0 did not pass (decision: Stage A0 install path — operator must NOT
pip-install unilaterally). Pass = all A1–A5 recorded
with `stage_b_go: true`. Stage A must NOT run unless Stage A0 passed with
`stage_a0_go: true`.

## 6. Stage B — CENSUS (only after Stage A passes with `stage_b_go: true`)

Exact command (requires explicit `--authorized` flag; exits non-zero without it):

```bash
/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py \
  --stage-b-census --authorized --out-root workspace/census_20260921
```

Per-acquisition ORDERED pipeline (no step may be reordered, retried, or tuned;
detailed stage rules in §6.0 + table below): inventory confirm → PRIMARY-ONLY read
(`<stem>.ttbin` alone; concatenation forbidden per §1.4 autofollow finding) →
channel verify B2 (FAIL ⇒ record, exclude acquisition, continue) →
ONE frozen-params auto-alignment invocation + contrast gate + yield self-check
B1 (ALIGN_FAIL ⇒ record, exclude, continue; ALIGN_INCONSISTENT ⇒ record, STOP
loudly — never silently proceed) → pairing at the derived offset (legacy_v1) →
B0 length-tier assignment B0-1 (`INSUFFICIENT_LENGTH` ⇒ no H, exclude, continue) → skip/CAL/VAL per tier B8 →
256-frame chunking B3 → `counts_ab` B4 → PRIMARY H1/H2/H_total (raw-MLE + 1e-15 floor)
+ SECONDARY flat H_full (separate column) B5 → per-acquisition JSON with full
provenance B9. CAL/VAL keyed (source, session, frame); zero overlap.

### 6.0 Stage B0 — LENGTH PRECHECK (per acquisition, after pairing, before any H work)

Frozen sizing needs 1024 CAL frames + 256 VAL frames = 1280 frames × 256 pairs
= 327,680 pairs, PLUS the 702 skipped frames ⇒ 1982 full frames = 507,392 pairs
for TIER_FULL. Preregistered reduced fallback (fixed, declared here): 512 CAL +
128 VAL frames = 640 × 256 = 163,840 pairs, PLUS 702 skipped ⇒ 1342 full frames =
343,552 pairs for TIER_REDUCED. Tier on full-frame count `n_frames = n_pairs // 256`
(trailing <256-pair remainder excluded by construction and recorded, never padded).

- **TIER_FULL**: n_frames ≥ 1982 → frozen sizing as-is (skip 702, CAL 1024, VAL 256).
- **TIER_REDUCED**: 1342 ≤ n_frames < 1982 → reduced sizing (skip 702, CAL 512
  frames = 131,072 symbols, VAL 128 frames = 32,768 symbols), output labelled
  `REDUCED_SIZING`, **not directly comparable** to the frozen three sessions' H
  values nor to TIER_FULL census rows.
- **TIER_INSUFFICIENT**: n_frames < 1342 → record `INSUFFICIENT_LENGTH`, emit no
  H and no counts_ab for that acquisition.
- Crucially: **no frame reuse, no padding, no partial-frame inclusion** — a frame
  is either fully 256 pairs or excluded. (Minor declared deviation from the frozen
  framing assert: where frozen code hard-fails on `n % 256 != 0`, the census floors
  to full frames and records the remainder; effect ≤ 255 pairs per acquisition,
  negligible against ≥343,552 tier pairs, and fully recorded per B0-1/B3.)

| ID | Acceptance | Evidence |
|----|-----------|----------|
| B0-1 | Length tier assigned from full-frame count BEFORE any H work: TIER_FULL (n_frames ≥ 1982) / TIER_REDUCED (1342–1981, labelled `REDUCED_SIZING`) / TIER_INSUFFICIENT (n_frames < 1342 ⇒ `INSUFFICIENT_LENGTH`, no H emitted). No reuse/padding/partial frames | per-acq JSON: `n_pairs_raw`, `n_pairs_excluded_remainder`, `n_frames`, `tier` |
| B1 | Per-acquisition auto-alignment passes from the SINGLE frozen-params invocation (§1.2): `status == "ok"` AND `peak_to_bg >= 10`. **Preregistered anti-tuning failure rule (R1 rewrite 2026-09-21): on FAIL do NOT tune, do NOT widen, do NOT scan a second range — record `ALIGN_FAIL`, exclude that acquisition from the census, continue to the next; report the excluded-acquisition count. Mandatory self-check: yield-vs-offset sweep must show the derived offset at/within one coarse step of the yield maximum, else `ALIGN_INCONSISTENT` (recorded, STOP loudly)** | per-acq JSON: `align` (peak_center/sigma/to_bg/status/criterion), `offset_applied_to_alice`, `yield_sweep` (offsets/yields/yield_max_ok); run log: `n_align_fail_excluded` |
| B2 | Channel guard passes: A=hw1/B=hw5 dominant, other/total ≤ 0.20 | `channel_pair`, `channel_hist`, `other_frac` |
| B3 | Full-256 framing: `n_frames = n_pairs // 256` consecutive frames keyed (source, session, frame); trailing <256 remainder excluded by construction and recorded, never padded | `n_pairs_raw`, `n_pairs_excluded_remainder`, `n_frames`, `frame_ids` head/tail |
| B4 | `counts_ab` shape (1024,1024) int64; sum == CAL symbols (1024×256=262144); `p_b` matches column marginal within 1e-12 | `counts_sum`, `counts_shape`, `marginal_check_1e12: true` |
| B5 | H values present with provenance: PRIMARY H1/H2/H_total (raw-MLE+floor) + SECONDARY flat H_full in a SEPARATE field; never merged into one column | `H1`, `H2`, `H_total`, `H_full_flat_secondary`, `estimator: raw-mle-floor-1e-15` |
| B6 | No decoder call: `grep -rn "decoder\|decode\|SC_decode\|LDPC" scripts/census_intake_20260921.py` empty (excluding the words in the no-decoder assertion comment); no decoder import in script | grep output recorded in run log |
| B7 | No write outside additive root: all outputs under `workspace/census_20260921/<acq_id>/` (plus the single Stage-A0 verdict `stage_a0_env.json` directly under the root); `git status --short` shows zero modifications under `results/`, `comparison_bench/outputs_comparison/`, `src/`, `experiments/`, `tools/` | `git status` snippet in run log |
| B8 | CAL/VAL framing per B0 tier (R2, frozen 2026-09-21): TIER_FULL → CAL = 1024 consecutive full-256 frames after 702 skipped, VAL = next 256, zero overlap; TIER_REDUCED → CAL 512 / VAL 128 after 702 skipped, labelled `REDUCED_SIZING`. Skip default is **702 frames for ALL acquisitions, explicitly labelled `INHERITED_NOT_DERIVED`** — the frozen 702 is an artifact of three particular sessions so copying it is unjustified, but a per-acquisition data-driven skip derived on census data would be tuning; the inherited default is therefore frozen with eyes open. **Mandatory companion diagnostic (NON-DECISION, does not change the run): operator records per-frame coincidence counts over the first ~1500 frames per acquisition** so the main thread can adjudicate post-hoc whether 702 is defensible per acquisition | `skip_frames: 702`, `skip_provenance: INHERITED_NOT_DERIVED`, `tier`, `CAL_frame_ids`, `VAL_frame_ids`, `overlap: 0`, `skip_diagnostic_first1500` |
| B9 | Per-acquisition JSON contains full provenance: files used + bytes, delay/peak/sigma/gate/threshold, channel pair, skip, CAL/VAL ids, counts sum, all H values | JSON schema check (all keys present) |

Stage B stop rules: B1 `ALIGN_FAIL`, B2 channel-guard FAIL, or B0-1
`INSUFFICIENT_LENGTH` on an acquisition ⇒ record the verdict for that
acquisition, EXCLUDE it from the census, continue the remaining acquisitions
(do not tune/retry a failed gate — one-shot descriptive census). B1
`ALIGN_INCONSISTENT` ⇒ record the verdict, STOP the run loudly (never proceed
silently). Report the
per-acquisition table PLUS the counts of `ALIGN_FAIL`-excluded and
`INSUFFICIENT_LENGTH` acquisitions. B3 framing FAIL (non-consecutive or
mis-keyed frames) ⇒ same per-acquisition exclude-and-continue treatment.
Any B6/B7 violation ⇒ STOP entire run immediately. Adverse Stage A inheritance
(merge semantics change mid-census) ⇒ STOP, report.

## 7. Artifacts
- `workspace/census_20260921/stage_a0_env.json` (Stage A0 env verdict).
- `workspace/census_20260921/<acq_id>/stage_a_parse.json` (Stage A; only the
  Stage-A acquisition).
- `workspace/census_20260921/<acq_id>/census.json` (Stage B; all 10).
- `workspace/census_20260921/run_log.md` (commands, branch, package versions,
  grep outputs for B6, git-status snippet for B7, per-acquisition PASS/FAIL table).
- No other outputs. Nothing under `results/` or
  `comparison_bench/outputs_comparison/`.

## 8. Test/evidence matrix (full ID list)
A0-1, A0-2, A0-3, A0-4, A0-5, A1, A2, A3, A4, A5, B0-1, B1, B2, B3, B4, B5, B6, B7, B8, B9.
Each ID maps to exactly one row above; operator reports PASS/FAIL per ID with
the named evidence artifact. No ID may be marked PASS without its evidence file.
Ordering gate: no A-ID may be attempted before all A0-IDs PASS (`stage_a0_go:
true`); no B-ID may be attempted before A5 records `stage_b_go: true`.

## 9. Return conditions (exactly two)
1. **All-complete**: every ID above PASS with evidence files listed; return file
   list + per-acquisition H table (H1/H2/H_total primary, H_full secondary in a
   separate column) + run log path.
2. **Concrete blocker**: failing command + exact error/traceback (or adverse
   verdict with the ID, e.g. A0-3 install failure or A5 `stage_b_go: false`) +
   attempted remedies +
   the SINGLE decision needed from the main thread. "Still incomplete" is not a
   completion report.

## 10. Notes for operator
- KNOWN WEAKNESS (R2, stated plainly — this census is descriptive/non-claim
  precisely because of it): the 702-frame skip default is inherited, not derived.
  Do not promote census H values against the frozen three sessions' reference
  values on skip-comparability grounds; TIER_REDUCED rows are additionally not
  directly comparable to TIER_FULL rows (§6.0).
- OPEN PI QUESTION `DURATION_TOKEN_VS_SPAN_DISCREPANCY_10X` (flagged for PI,
  metadata-only, does NOT affect the H census — kept visible per R5): acquisition
  `20260112_Type2PPLN_3s` filename says `3s` but the measured timestamp span is
  30.0 s (7486100101885435 → 7516100054295827 ps = 29.99995 s). Record but do
  not resolve. R1-rewrite note 2026-09-21: correlation auto-alignment in raw
  units makes pairing immune to the ps-vs-0.1ps reading, so this item no longer
  blocks pairing — it stays OPEN for physical interpretation and cross-session
  comparability.
- Channel **1001** (10,175 events, 0.27% on `20260112_Type2PPLN_3s`) looks like
  a sync/marker channel: it is NOT A or B, falls in the `other` fraction
  (guard ≤ 0.20), and the census pairing uses ONLY channels 1 and 5. CONFIRMED
  in script (R4): `stage_b_census` selects `ch == HW_A(1)` / `ch == HW_B(5)` masks
  only; every other channel id lands in `other` counted against the 0.20 guard
  (here other_frac = 10175/3836088 ≈ 0.0027 ≪ 0.20). 1001 is excluded by
  construction — confirm the exclusion holds per acquisition via the B2
  `other_frac` check; no other action needed.
- Read `.ttbin` paths from `workspace/data_intake_20260921/inventory.json`
  (exact `path_posix` per file); do not reconstruct paths from stems.
- Sibling venv has numpy 2.5.3 (verified 2026-09-21); script needs stdlib+numpy
  only (+ `Swabian-TimeTagger` after Stage A0). If `TimeTagger` is missing
  before Stage A0 passes, STOP and report (do not pip-install without the
  SEPARATE A0-3 install authorization — item B).
- This census creates NO candidate/accepted token, consumes no attempt, changes
  no scientific status (descriptive only).

## 11. Addendum 2026-09-21 — dual-rule descriptive census (all 10, executed)

RULE QUESTION SETTLED EMPIRICALLY (not by argument): the frozen evidence
string `pairing: "nearest"` + `rule: "legacy_v1"` admits two pairing
generations, and the pilot had used only one. Both were measured per
acquisition, decoder-free, with frozen constants (no threshold tuning):
- **(W) wide / legacy_v1 same-superframe**: `b = t//200`, pair iff same
  `b//1024` (effective window 204800 units = 204.8 ns).
- **(N) narrow / nearest-unique** (`_pair_nearest_unique`,
  `src/qkd_io/ttbin_pipeline.py:219`): greedy monotonic 1-1 pairing within a
  symmetric window, offset on A; preregistered window grid
  `{200,500,1000,2000,4000,40000}` reported per window, no "best" picked.
True-vs-accidental separation per rule from the yield-vs-offset sweep:
accidental baseline at `|offset| ≥ 2` superframes (409600); report `n_pairs`,
`n_accidental`, `n_true_excess`, accidental fraction. The pilot strict-exact
yield-max miss (35399 vs 35402, 3 pairs = 0.008%) is PASS-with-note
(within-one-coarse-step holds everywhere, 10/10); never tuned.
Execution: `workspace/dual_rule_census_20260921.py` (scratch, stdlib+numpy;
reuses the frozen estimator + `legacy_v1` gather from
`scripts/census_intake_20260921.py` without modifying it); per-acquisition
`workspace/census_20260921/<acq_id>/dual_rule_census.json` (additive — pilot
`census.json` untouched) + `workspace/census_20260921/dual_rule_summary.json`.
H emitted ONLY where a rule reaches ≥ REDUCED (prereg 512/128 sizing, frozen
skip 702): 8 acquisitions under (W)/FULL; none under (N)-only.

PILOT `20260112_Type2PPLN_3s` (W vs N): (W) 35,399 pairs = 138 fr,
INSUFFICIENT, acc 24,600.5 / true 10,798.5 (69.5% acc). (N) grid yields
4782 / 8232 / 10165 / 10882 / 11380 / 20286 pairs (18–79 fr, all
INSUFFICIENT); acc frac 1.0% → 47.6%; true excess saturates ≈ 10.4–10.8k
across windows ≥ 2000 — the SAME ≈10.7k true population both rules see.
(N)-200 is the cleaner channel (1.0% acc vs 69.5%); NEITHER rule reaches a
tier permitting H on the pilot.

σ PICTURE (headline diagnostic, frozen gate `[50,150]` NOT relaxed):
inside 7/10 — SHG 112.5/114.4; Type0-500K 104.7, 1M 132.4; 01-21 Type2
77.6/66.7/91.4. Outside 3/10 — pilot 385.7 (2.57× upper), Type0-1.5M 175.9
(1.17×), Type0-2M 233.2 (1.55×). New-source σ far outside the 01-21 design
range is a CONTRACT INCOMPATIBILITY with the frozen `gate_ps=200` pairing
gate (designed together with `[50,150]`), not something to tune around —
flagged for the PI (decision-log entry same date).

TIER CENSUS: (W) FULL 8 / INSUFFICIENT 2 (pilot, Type0-500K) / ALIGN_FAIL 0.
(N) window-dependent — w=200: FULL 5 / INSUFFICIENT 5; w=40000: FULL 7 /
INSUFFICIENT 3; all 10 align `ok`, `other_frac` ≤ 0.087 < 0.20 everywhere.
H (factorized raw-MLE+1e-15, flat secondary separate): 8 rows under (W)/FULL,
H_total 4.34–7.62 — accidental-dominated W streams (53–96% acc), NOT
comparable to the frozen ≈0.8 clean-coincidence references; 2 acquisitions
with no H (both rules INSUFFICIENT).

## §12 Narrow-rule (N) H follow-up 2026-09-21 (executed, decoder-free, no tuning)

Gap closed: the dual-rule census emitted H only under (W) and withheld (N) H
as "mapping undefined". The mapping is identical under both rules — a pair
yields `(b_A % 1024, b_B % 1024)`, `b = t // 200` floor, `tA` aligned by the
frozen per-acquisition `peak_center_ps`; rules differ only in WHICH pairs are
selected. Computed per (acquisition, window) cell on the preregistered grid
with frozen CAL/VAL sizing (skip 702; FULL 1024/256; REDUCED 512/128;
no padding/reuse/shrink): factorized H1+H2 (raw-count MLE + 1e-15 floor) plus
flat full-joint H_full (30-pt 4-fold CV λ) as a SEPARATE field.
Script `workspace/narrow_h_census_20260921.py`; evidence
`workspace/census_20260921/narrow_h_summary.json` + `narrow_h_table.csv`
(gitignored workspace, read-only). No REDUCED tier exists under (N) anywhere;
28 INSUFFICIENT cells emit no H. λ\* = 0.0 on all 32 H cells, hence Hflat ==
H_total bit-identical (fields kept separate regardless). Correction to the
packet's bias line: w=200 Gaussian ±w coverage is ~99% only for σ≲87 (the
01-21 sources: 0.9900/0.9973/0.9714); σ≈112–114 (SHG) gives 0.92, σ=132 gives
0.87 — clean+FULL but marginally biased under a strict ≥0.95 gate. The
window/gate choice stays a PI contract decision; no "best" window picked.
