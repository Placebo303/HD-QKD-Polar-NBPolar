# Step-0 channel-survey prereg SKELETON (design artifact — authorizes nothing)

## 0. Status

- `EXPLORATION_ONLY / DOCS_ONLY` — this file is a **design artifact** for the
  future Step-0 channel survey. It **authorizes no code, no run, no freeze
  change, no frozen-constant change, no data access, no Tier-X probe run, and
  no Tier-Y decision gate**.
- Parent scope: `openspec/changes/nbpolar-native-highdim-exploration/`,
  specifically proposal §Step 0 ("channel survey: what does the existing error
  actually look like?") and design §D2 (Step-0 survey design: descriptive,
  Tier-X-shaped).
- Any future survey execution needs its own freeze document plus separate
  verbatim user authorization per AGENTS.md §10.1–10.4. Nothing here satisfies
  that requirement.
- Minimalism (AGENTS.md §5.7): plain markdown only. No code, no checksums, no
  atomic writes, no schema validators, no retry frameworks, no defensive
  machinery.

## 1. Scientific question, success criterion, stop-loss, not-doing list

(Substance identical to proposal §Step 0 and design §D2; neither weakened nor
extended.)

- **Scientific question:** is the residual channel (±1-dominated? heavy-tail?
  period-crossing?) of a type where preserving inter-level dependence could
  plausibly matter?
- **Read-only inputs:** already-derived per-block/per-frame tables and
  registries (frozen DEVELOPMENT artifacts) listed in §2 below. No `.ttbin`
  access.
- **Design outputs (later, under separate authorization):** error histogram,
  |Δ| distribution, bin-occupancy non-uniformity, period-crossing rate — all
  descriptive, Tier-X style, written only to the exploration write root (§5).
- **Success:** a preregistered survey spec exists with metrics, binnings, and
  denominators fixed in advance (§3–§4 below fix them).
- **Stop-loss:** if the survey spec cannot be written without new raw reads or
  without touching frozen artifacts, stop and return to planner (see §6).
- **Not doing:** no decoder, no prior change, no N/K/P/w move, no FER claim of
  any kind.

## 2. Read-only input manifest (all paths verified to exist at skeleton time)

Read-only inspection only (directory listing / file reading). No code
executed, no runs, no writes to any input path, no EVAL/RESERVE frame
consumption, no decoder, no simulation. No `.ttbin` path is listed anywhere.

| # | Path (repo-relative) | Supplies | Frozen provenance |
|---|---|---|---|
| M1 | `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/delta_profiles.json` | PRIMARY. Signed error-Δ histogram source (`profile.circular_counts`, 1025 cells, `circular_offset` −512; `profile.linear_counts`, 2047 cells, `linear_offset` −1023); \|Δ\| summary (`summaries.CIRCULAR`: n0 / n_plus / n_minus / n_tail / n_total); period-crossing wrap accounting (linear ±1023 cells closing into circular ∓1; `tail_gate` p̂ / U / B_tail / verdict) | G1R2 frozen derived artifact. SHG `_1` (`20260113_SHG_Type2PPLN_3s`), CHAR segment, 200,192 pairs, (N) W_P=200, MOD CIRCULAR, skip-702, derived offset +50 ps. Verified: file read (header keys, `linear_offset`, `circular_offset`, `summaries`, `tail_gate`, `sensitivity_triple` all present; linear tail cells 44 + 1 = 45 close exactly) |
| M2 | `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/delta_profiles.json` | CONTEXT ONLY. Signed-Δ histogram under the superseded G1 contract (`mod_frozen` LINEAR_ONLY). Recorded context; never compared numerically against M1 (cross-contract comparison forbidden) | G1 frozen derived artifact. Same acq/CHAR population (200,192 pairs) under (N) W_P=500, MOD LINEAR_ONLY, skip-702. Verified: file read (header keys, `mod_frozen: LINEAR_ONLY`, `linear_counts` present) |
| M3 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/G1R2_ADJUDICATION.md` | Frozen record anchoring M1: linear {−1023: 44, −1: 450, 0: 150909, +1: 48788, +1023: 1} / circular {−1: 451, 0: 150909, +1: 48832, tail 0} wrap closure; CAL32 triple q0/q+1/q−1/q_rest = 0.7562255859375 / 0.241943359375 / 0.0018310546875 / 0; H_M2 = 0.8168138 / H_M0 = 0.6910589. Supplies \|Δ\|-adjacent CAL-conditional distribution + period-crossing wrap reference | G1R2 main-thread adjudication `NBPOLAR_M2_PRIOR_G1R2_COMPLETE_DESCRIPTIVE` (descriptive/non-claim). Verified: file read |
| M4 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/G1_ADJUDICATION.md` | Frozen record anchoring M2: linear profile {0: 149852, +1: 48639, −1: 696, tail: 1005}; CAL triple 0.746704 / 0.243652 / 0.004395 / 0.005249; tail budget B_tail = 2.0e-4 with p̂ = 0.0050202 / U = 0.0052879. Supplies signed-Δ record + tail-budget reference for the G1 contract | G1 main-thread adjudication `NBPOLAR_M2_PRIOR_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`. Verified: file read |
| M5 | `.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/S11_ADJUDICATION.md` | Frozen Tier-X record: W-grid tail rates, offset scan, far-offset baseline (structured, not uniform), wrap-alias accounting (wrap+ fixed at 8, wrap− at 293→294; w=200 CIRCULAR tail = 0). Supplies period-crossing / window-dependence context | S11 main-thread adjudication `NBPOLAR_S11_SHG_TAIL_NATURE_COMPLETE_DESCRIPTIVE` (Tier-X, descriptive/non-claim). Verified: file read |
| M6 | `comparison_bench/outputs_comparison/real_frame_batch.parquet` | CANDIDATE marginal bin-occupancy source ONLY (Alice/Bob per-pair bin columns, if present). NOTE: this is a binary file whose columns/schema were NOT verified in this task. Its use is conditional on a Phase-A column/schema verification check at the future freeze (the single allowed deferred verification in this skeleton): the future packet must confirm per-pair bin-index columns exist before reading; if the check fails, the §6 stop rule fires and occupancy is reported as UNMEASURABLE_FROM_FROZEN_ARTIFACTS — never worked around with a substitute path | Frozen benchmark output (existence verified by directory listing). Plausibility only: the repo documents a `build_frame_batch(...) -> FrameBatch` path and a `frame_batch_path` config key (`AGENT_PROJECT_MEMORY.md` observed entries). No content claim is made here |

Evaluated and EXCLUDED (recorded so the future packet does not re-open them
without new justification):

- `docs/nbpolar/RAW_DATA_INVENTORY_20260921.md` — raw `.ttbin` inventory only;
  excluded by the no-`.ttbin` rule (verified by file read: per-file table of
  `.ttbin` paths/sizes).
- `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md` — prior-formula/contract freeze
  doc; supplies no Δ histogram, no occupancy table, no crossing record
  (verified by file read: axis/provenance table of builders, not data).
- `comparison_bench/outputs_comparison/run_manifest.json` and
  `ir_benchmark_results.csv` — frozen benchmark config snapshot + synthetic-d8
  method table; supply no d=1024 Δ/occupancy/crossing statistic (verified by
  file read: `dataset_id synthetic_d8_ser005`, d=8 rows only).
- `workspace/m2_prior_validation/remainder_101f_g1r2/` — contains
  `cal_ids.json`, `g1.json`, `remainder_driver.py`, `run_log.md` but no verified
  Δ-profile artifact (verified by directory listing; file list completed per T2
  R-1 comment, 2026-09-23); not listed as a statistic source.

## 3. Fixed metric definitions (nothing left open)

### 3a. Signed error-Δ histogram

- **Δ convention:** Δ = b_B − b_A, where b_A, b_B ∈ {0, …, 1023} are the
  within-period bin indices of the paired Alice/Bob symbols (d=1024 alphabet,
  bin 200 ps, period 204800 ps = 1024 × 200 ps). Positive Δ means the Bob
  symbol lands in a later bin than the Alice symbol. This convention matches
  the frozen profile asymmetry (+1 cell dominant: 48788 vs −1 cell 450 under
  the G1R2 contract).
- **Primary histogram (CIRCULAR semantics):** 1025 integer bins centered at
  −512, …, +512 with exact edges at k − 0.5 … k + 0.5 for each integer k;
  counts read directly from M1 `profile.circular_counts`
  (`circular_offset` −512). No re-binning, no smoothing, no fit.
- **Wrap cross-check (LINEAR semantics):** 2047 integer bins centered at
  −1023, …, +1023 with exact half-integer edges; counts read directly from M1
  `profile.linear_counts` (`linear_offset` −1023). Reported alongside the
  primary histogram only to show the wrap-closure accounting.
- **Population:** M1 CHAR segment only — SHG `_1`, 200,192 pairs,
  post-skip-702, (N) W_P=200, MOD CIRCULAR, derived offset +50 ps. M2 is
  recorded context, not a second population.

### 3b. |Δ| denominator — per symbol (exactly one choice)

- **Choice: per symbol.** |Δ| rates are counts divided by n_pairs = 200,192
  (e.g. tail rate p̂ = n_tail / 200,192; |Δ| = 1 mass = (n_plus + n_minus) /
  200,192 from the M1 CIRCULAR summary).
- **One-line justification:** the (N) narrow nearest-unique pairing drops a
  window-dependent number of coincidences, so pairs-per-frame varies and a
  per-frame denominator is ill-defined; the per-symbol denominator is exact
  and is the same arithmetic the frozen tail gate already uses
  (p̂ = n_tail / n with Clopper-Pearson U).

### 3c. Bin-occupancy normalization — exact rule

- Let c_A[b], b = 0, …, 1023, be the Alice marginal bin counts over the §3a
  population (Bob marginal c_B[b] reported symmetrically if the Phase-A
  schema check confirms both columns; Alice is the reference).
- **Normalization:** o[b] = c_A[b] / n_pairs, with n_pairs = 200,192.
- **Uniformity reference:** u = 1/1024 for every bin.
- **Reported non-uniformity (fixed, descriptive):** max_b o[b], min_b o[b],
  max_b o[b] / u, and the fraction of bins with o[b] < u/2. No model fit, no
  decoder input reuse claim.
- **Conditionality:** the occupancy readout depends on entry M6 passing its
  Phase-A schema check; otherwise reported as
  UNMEASURABLE_FROM_FROZEN_ARTIFACTS per §6.

### 3d. Period-crossing event — exact definition

- **Definition:** a paired coincidence is a period-crossing event iff its
  LINEAR bin-index difference satisfies Δ_linear ∈ {−1023, +1023}, i.e. it
  falls in the extreme wrap-alias cells of M1 `profile.linear_counts`
  (indices 0 and 2046 given `linear_offset` −1023). These are exactly the
  cells that close into the circular ∓1 cells under CIRCULAR semantics
  (linear −1023 → circular +1; linear +1023 → circular −1; frozen wrap
  accounting: 44 + 1 = 45 = LINEAR_ONLY n_tail under the G1R2 contract).
- **Period:** 204800 ps (1024 bins × bin 200 ps); the crossing is a wrap of
  this period boundary under LINEAR semantics.
- **Rate:** n_cross / n_pairs with n_pairs = 200,192 (per-symbol denominator,
  consistent with §3b).

## 4. Stop rule

If this manifest or any metric definition in §3 cannot be fixed without new
raw reads (including any `.ttbin` read) or without touching (writing to,
re-deriving, or re-fitting) frozen artifacts, the operator STOPS and reports
to the main thread. A placeholder path, an invented count, a substitute
population, or a post-hoc re-binning is forbidden. Concretely: any entry of
§2 found missing/unreadable at the future freeze, any M6 schema check
failure, or any ambiguity in §3a–§3d requiring new derivation, each
independently triggers the stop.

## 5. Tier-X / ledger framing

- This survey is **descriptive-only**. It produces **no FER object of any
  kind by construction**: no frame-error rate, no block-error rate, no
  success/failure gate on decoding, no threshold, no pass/fail verdict on any
  method.
- Its output belongs to the future **L3 descriptive-survey ledger** and is
  never merged into, compared numerically against, or cited as **L1
  real-data FER**.
- This skeleton contains no efficiency statement, no leakage statement, no
  promotion statement, no qualification statement, and no composable-key or
  security statement. The frozen numbers in §7 are verbatim provenance
  context, not survey results or claims.

## 6. Future run declaration (created by NO ONE in this task)

- The future survey — if ever authorized — writes ONLY to the future root
  `workspace/exploration/nbpolar-native-highdim/step0/`, holding at most
  three files: `prereg.md`, `results.json`, `notes.md`.
- That directory is NOT created by this task. Each of the three files
  requires its own future freeze plus separate verbatim user authorization
  before it is written. Forbidden writes (reaffirmed): `results/`,
  `comparison_bench/outputs_comparison/`, any frozen directory, any `.ttbin`
  path, any existing change/archive directory.

## 7. Frozen-number box (verbatim provenance; not survey results)

d=1024; N=32768 (=128 frames × 256 pairs); K1=319; K2=6492; P16
construction; W_P=200 / W_S=500 / CIRCULAR / skip=702; frame_pairs=256;
floor=1e-15; chunk=512; bin=200 ps; f(6811)=1.2747449;
key_dependent_bits=34,119 (=5·(K1+K2)+64, per-row constant);
public_control_bits=327,743; undetected 0/42 isolated (never merged into
success/FER); EVAL 14 blocks (frames 2398–4189); RESERVE SHG_1 29 frames /
SHG_2 99 frames; never pad/reuse/shrink, COMPLETE-BLOCKS-ONLY else
INSUFFICIENT; already-decoded segments = DEVELOPMENT data, never a
confirmation sample.
