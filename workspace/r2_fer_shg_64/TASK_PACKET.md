# TASK PACKET — r2-fer-shg-64

Per AGENTS.md §3/§10.1/§10.3/§10.4 (delta-successor fast path): this
document authorizes NOTHING by itself. This is a **Tier-Y decision-gate**
measurement (claim-bearing, real-data, one-shot), NOT a Tier-X probe and NOT
a descriptive diagnostic. Execution requires, IN ORDER:

1. The R2 contract (`openspec/changes/nbpolar-r2-fer-measurement-contract/`)
   T4 ledger rows in `docs/nbpolar/R2_REMAINING_DECISIONS_20260928.md`
   (D-ACQ-01/04/07/08, D-FER-04/05/06/07) formally adjudicated `DECIDED` and
   written back into that change's `tasks.md` §5 ledger (per that document's
   own header: "本文件本身不裁定、不冻结、不授权").
2. `R2_TAG_MASTER`/`R2_EVAL_SEED` pasted into `run.py` from the frozen T6
   contract values (currently `None` placeholders; `run.py` refuses to run
   otherwise).
3. **This packet's own open decision points (§3 below) resolved** by the
   main thread — in particular D_NEW_SEED_SCHEME, D_NEW_STRATUM_LABELS,
   D_NEW_FIDELITY_SCOPE, and the D-ACQ-06 budget conflict (§5).
4. Independent Pre-EXECUTE review PASS on this packet (AGENTS.md §10.3).
5. Explicit PI authorization, verbatim, pasted from `AUTHORIZATION_PROMPT.md`
   (currently a **template**, NOT yet granted — unlike the predecessor,
   which documented already-given authorization).
6. After execution: independent Pre-RESULT review PASS before `results.json`
   is cited in any adjudication/decision-log entry, `OPERATOR_RETURN.md`, or
   `RESULT_SUMMARY.md`.

**This preparation pass did NOT execute anything, did NOT run any decoder,
did NOT read raw `.ttbin` data content (existence/listing checks only), and
did NOT modify any existing file, including anything under
`workspace/m2_scl_check_g2g3_success/`.** No git write of any kind was
performed.

## 0. Inheritance (delta-successor of `workspace/m2_scl_check_g2g3_success/`)

Per AGENTS.md §10.1 item 5 / §10.4's "Delta-successor fast path", this
packet reuses that predecessor's contract unchanged except for the explicit
delta below. Predecessor: Pre-EXECUTE PASS, Pre-RESULT PASS, attempt 1
completed exit 0 (2026-09-28), `state: completed_descriptive`,
`main_thread_acceptance: accepted_descriptive`.

| | Predecessor (`m2_scl_check_g2g3_success`) | This packet (`r2-fer-shg-64`) |
|---|---|---|
| Classification | Descriptive real-data diagnostic (non-claim); zero attempt-budget impact | **Tier-Y decision-gate measurement** (claim-bearing); counts as ONE attempt |
| Target blocks | 19: outcome=exact EVAL blocks only (G2 11 + G3 8) | **64**: full DATA_LEDGER §7 pool — A1_CAL (16) + HELDOUT_model_selection (20) + EVAL_already_decoded (28), both sessions, all outcomes |
| Fidelity check | All 19 targets are EVAL blocks; per-block STOP; ANY mismatch withholds the WHOLE aggregate tally (ruling D3) | Fidelity check applies ONLY to the 28 `EVAL_already_decoded` blocks (comparable `per_block_outcomes.jsonl` record exists); the 36 A1_CAL/HELDOUT blocks get a descriptive-only SC baseline, no comparison, no gate. A mismatch STOPs only that block's SCL step and is excluded from the taxonomy tally for that block — it does **not** withhold the whole 64-block result (see D_NEW_FIDELITY_SCOPE below — this is a deliberate, flagged departure from ruling D3's all-or-nothing scope, since D3 was designed for an all-EVAL 19-block set and does not fit a mixed 64-block pool where most blocks have no comparable record at all) |
| tag_master / eval_seed | G2's own inherited master/seed for G2 blocks, G3's own for G3 blocks (unchanged from G2/G3's original frozen decode) | **NEW, single, shared** value for both sessions (D-ACQ-07 O-7b); placeholders `R2_TAG_MASTER`/`R2_EVAL_SEED` in `run.py`, not yet filled |
| block_index (seed derivation) | EVAL-native `block_index` (0-13), matching `g2_eval_blocks()` | **NEW `global_block_index`** (0-63, session-and-stratum-unique) — required because a SHARED master collapses `operational_seed_bits`'s uniqueness guarantee if `block_index` repeats across sessions/strata (see D_NEW_SEED_SCHEME) |
| Stratum labels | N/A (single arm=B EVAL-only target set) | **Dual labeling**: `stratum_official` (DECIDED D-ACQ-03 labels, coarse) + `stratum_task` (this task's finer request, splits the CHAR portion out of `HELDOUT_model_selection`) — see D_NEW_STRATUM_LABELS |
| Output | Descriptive counts (`n_preserved_exact`/`n_broken`/`n_undetected`/`n_errors_or_aborts`), non-claim prose | **Raw taxonomy counts only** (`exact`/`verify_failed`/`decode_failed`/`undetected`/`resource_abort`), Wilson(z=1.96) CI per stratum + pooled, **NO verdict string**, `stop_undetected` flag, per-session `f_book_*_computed` |
| `accepted` formula | `crc_pass AND tag_pass` (ruling F1) | **identical**, plus `AND NOT decode_failed` (new defensive C5-schema branch; structurally near-unreachable for the SCL list decoder, see §3) |
| Budget / parallelism | 1200s/2GiB per block, ≤8 concurrent, reruns=0, NO global wall cap | **1200s/2GiB per block (same numbers), ≤8 concurrent, reruns=0, PLUS a NEW 3h (10800s) total-wall backstop** — **PENDING-BUDGET, conflicts with DECIDED D-ACQ-06** (§5) |
| Decoder / other params (L, top_m, CRC, K1/K2, N, digest, window/skip/MOD) | frozen | **identical, unchanged** |
| Output dir | `workspace/m2_scl_check_g2g3_success/` | `workspace/r2_fer_shg_64/` |
| `probe_id` | `m2-scl-check-g2g3-success` | `r2-fer-shg-64` |

Main-thread rulings **inherited unchanged** from the predecessor chain
(F1 accepted-definition; per-block budget-check mechanism D4; one-shot/
reruns=0 discipline). Ruling **D3 is explicitly NOT inherited unchanged**
— see D_NEW_FIDELITY_SCOPE below.

## 1. Scope

### Allowed to write (additive only; must not pre-exist)

- `workspace/r2_fer_shg_64/results.json`
- `workspace/r2_fer_shg_64/part_<SESSION>_<global_block_index:02d>.json` (64 files)
- `workspace/r2_fer_shg_64/EXECUTION_TRANSCRIPT.md` — after execution completes.
- `workspace/r2_fer_shg_64/session_setup_execution_error_attemptN.json` —
  ONLY if an execution-defect death occurs before any measurement.

### Allowed to read

- Raw `.ttbin` for `20260113_SHG_Type2PPLN_3s` (SHG `_1`) and
  `20260113_SHG_Type2PPLN_3s_2` (SHG `_2`) — via the SAME frozen readers
  G2/G3/the predecessor used; no new acquisition, no different
  window/skip/MOD. **Not read in this preparation pass — directory listing
  / existence confirmed only (§4 below).**
- `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/per_block_outcomes.jsonl`
  and `.../20260113_SHG_Type2PPLN_3s_2_g3/per_block_outcomes.jsonl`
  (read-only; already read in this prep pass, JSON-lines only, to confirm
  all 28 EVAL blocks have a comparable arm=B record — §2 below — and read
  again at runtime for the fidelity check).
- `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
  (frozen P16 construction, digest-pinned; existence confirmed, not
  content-read, in this prep pass).
- `scripts/m2_prior_validation.py`,
  `comparison_bench/src/comparison_bench/formal_ir/{prior_m2.py,nbpolar/*.py}`
  — imported, never edited. Read (source) in this prep pass to confirm
  `run_g2_block`, `g2_eval_blocks`, `chunk_frames`, `operational_seed_bits`,
  and `scl_joint_decode` are frame-range-generic / block-index-parametric —
  §4 below records the evidence trail.
- `workspace/m2_scl_check_g2g3_success/run.py`, `TASK_PACKET.md`,
  `STATUS.yaml`, `prereg.md`, `AUTHORIZATION_PROMPT.md` — read-only, as the
  delta-successor base contract. **Not modified.**
- `docs/nbpolar/DATA_LEDGER.md`, `docs/nbpolar/R2_REMAINING_DECISIONS_20260928.md`,
  `openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md`,
  `AGENTS.md` — read-only planning/contract sources.

### Forbidden (hard stop if touched)

- Any edit to `sc.py`, `scl.py`, `scl_joint.py`, `two_layer.py`,
  `transform.py`, `algebra.py`, `prior.py`, `prior_m2.py`,
  `operational_f13*.py`, `m2_prior_validation.py`, or any other file under
  `src/`, `experiments/`, `tools/`, `comparison_bench/src/`.
- Any write under `results/`, `comparison_bench/outputs_comparison/`, or
  any EXISTING directory under `workspace/m2_prior_validation/`.
- **Any write to `workspace/m2_scl_check_g2g3_success/` (the predecessor
  packet) — read-only reference only.**
- Any edit to `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/` or
  `.../NBPOLAR-M2-PRIOR-G3-CONFIRM/`.
- Any change to `NBPOLAR_M2_PRIOR_G2_SUCCESS` / `NBPOLAR_M2_PRIOR_G3_SUCCESS`
  / the M2 status ladder, in this or any other document.
- Drawing any frame outside the frozen 64-block pool (0-1023, 1056-2397,
  2398-4189, both sessions) or CAL32 (1024-1055) for any purpose other than
  reproducing the SAME CAL fit G2/G3/the predecessor already used.
- git commit/push of any kind.
- Running the decoder / executing `run.py` (preparation only — this pass
  stops at `state=prepared_awaiting_contract_freeze_and_pre_execute`).
- **Filling `R2_TAG_MASTER`/`R2_EVAL_SEED` with an invented value.** These
  stay `None` until the main thread pastes the T6-frozen contract integers.

## 2. Target-pool confirmation (performed in this preparation pass)

- Block frame-boundary arithmetic (`0-1023` / `8` blocks; `1056-2397` /
  `10` blocks, `62`-frame remainder `2336-2397` unused; `2398-4189` / `14`
  blocks) verified by direct computation against `DATA_LEDGER.md` §7 —
  **matches exactly** (see §6 static self-check below for the reproducible
  arithmetic).
- `stratum_task` CHAR/HELDOUT sub-split (conservative any-HELDOUT-frame
  rule, HELDOUT starts at frame 1838): of the 10 `HELDOUT_model_selection`
  blocks per session, **6 are pure-CHAR** (`1056-1823`, no HELDOUT frame in
  the block → `stratum_task=never_decoded`) and **4 contain at least one
  HELDOUT frame** (`1824-2335` → `stratum_task=heldout_model_selection`).
  Combined with the 8 `A1_CAL` blocks (`stratum_task=never_decoded`), each
  session's `stratum_task` split is **(14 never_decoded, 4
  heldout_model_selection, 14 previously_decoded_eval)**, asserted in
  `run.py::build_session_blocks`.
- Both `per_block_outcomes.jsonl` files (`workspace/m2_prior_validation/.../per_block_outcomes.jsonl`,
  read-only, JSON-lines) confirmed to carry **all 14** `arm=B_M2_32f_candidate`
  rows per session (G2: 11 `exact` + 3 `verify_failed`; G3: 8 `exact` + 6
  `verify_failed`) — i.e. **all 28** `EVAL_already_decoded` blocks have a
  comparable frozen record for the fidelity check, not just the
  predecessor's 19-block `outcome=exact` subset. No `undetected` or
  `decode_failed` rows exist in either file for arm B (matches
  `docs/decision-log.md` "undetected 0/42 isolated" for both sessions).
- No mismatch encountered in this arithmetic-confirmation pass; no
  raw-`.ttbin` byte was read (per_block_outcomes.jsonl is JSON lines, not
  raw timetags).

## 3. Decision points for the main thread (NOT adjudicated by this operator)

These are flagged, not silently resolved, per AGENTS.md §3 ("if
implementation reveals requirement ambiguity, stop and return to
planner/OpenSpec instead of guessing"). `run.py` implements the recommended
default in each case so the packet is complete and self-consistent, but
none of these defaults should be treated as approved until the main thread
rules on them.

- **D_NEW_SEED_SCHEME** (new convention, no precedent in this repo):
  `operational_seed_bits(master, n, block_index)` depends on nothing else.
  R2's shared single `tag_master` across both sessions (D-ACQ-07 O-7b)
  means that if `block_index` were the EVAL-native 0-13 (or any
  session-local-only scheme) used identically by both sessions, the SAME
  seed would be reused across two *different* 32768-symbol blocks (a G2
  block and its "same-numbered" G3 block) — a public-seed-reuse pattern the
  existing single-session code never had to guard against, because the
  predecessor (and G2/G3 themselves) always used a session-own master.
  This packet's `run.py` assigns a NEW `global_block_index` (0-63, unique
  across the whole 64-block pool: G2 offset 0, G3 offset 32) and uses it —
  not the EVAL-native index — for ALL seed/tag derivation on ALL 64 blocks
  (EVAL included). This does not affect the EVAL fidelity-check comparison
  itself (§4 below records why: the compared fields either don't depend on
  the seed at all — `l1_exact`/`hard_l2_exact`/`first_error_*` are
  seed-independent SC-decode outputs — or, for `outcome`, are provably
  seed-invariant whenever the underlying decode is bit-exact, and only a
  ~2^-64 collision probability difference otherwise, immaterial to a
  64-block empirical run). **Recommend: accept as specified** — it is the
  only self-consistent option once D-ACQ-07 O-7b's shared master is
  adopted — but this operator does not have authority to rule on it, and it
  is a NEW convention with no prior main-thread ruling to inherit.
- **D_NEW_STRATUM_LABELS** (dual labeling vs the DECIDED coarse labels):
  `docs/nbpolar/DATA_LEDGER.md` §7 / `tasks.md` D-ACQ-03 DECIDED exactly
  three official strata: `A1_CAL_characterization` (8/session),
  `HELDOUT_model_selection` (the WHOLE 1056-2397 band, 10/session, no
  sub-split), `EVAL_already_decoded` (14/session). This task's own
  instruction additionally requests a finer split
  (`never_decoded`/`heldout_model_selection`/`previously_decoded_eval`)
  that pulls the pure-CHAR portion (6/session) OUT of the official
  `HELDOUT_model_selection` band and merges it into a `never_decoded`
  bucket together with `A1_CAL`. These are two genuinely different
  groupings answering two different questions (official
  model-selection-participation stratum vs. this task's
  "was-there-ever-a-comparable-decode-record" operational split). `run.py`
  emits **both** fields (`stratum_official`, `stratum_task`) per block and
  reports taxonomy tallies under both groupings, rather than silently
  picking one label scheme and dropping the other. **Recommend: keep
  both** — `stratum_official` for compliance with the frozen D-ACQ-03
  contract text, `stratum_task` as an additional descriptive breakdown.
  **Update, see §4a**: `T6_PACKET_SKELETON_20260928.md` §5 step 8's
  mandatory report contents require the `stratum_official` 3-way table +
  pooled (P-1) and do not mention a `stratum_task` split — so
  `stratum_task` is confirmed additive, not a conflicting substitute: the
  official 3-way + pooled table this packet emits already satisfies that
  requirement on its own, and `stratum_task` is extra description this
  task's own instruction asked for, with nothing in the frozen contract to
  reconcile it against.
- **D_NEW_FIDELITY_SCOPE** (departure from ruling D3's all-or-nothing
  scope): the predecessor's D3 ruling withholds the ENTIRE aggregate tally
  if ANY of its 19 (all-EVAL) targets fails the fidelity check. This
  packet's 64-block pool has only 28 EVAL blocks with a comparable record
  at all; a single fidelity mismatch on one EVAL block withholding the
  OTHER 63 blocks' taxonomy counts (including the 36 blocks that were never
  comparable to begin with) would not serve the same purpose D3 served
  (protecting against a broken/non-reproducible decode pipeline
  contaminating an all-comparable target set). `run.py` therefore scopes
  the STOP to the mismatched block only (excluded from all tallies,
  reported by id) and does NOT withhold the other 63 blocks' results.
  **Recommend: accept as specified**, but this is an explicit, non-trivial
  departure from an inherited ruling and needs main-thread sign-off before
  Pre-EXECUTE, not a silent divergence.
- **D_NEW_DECODE_FAILED_BRANCH**: the SCL joint decoder's list decode
  always yields >=1 L1 survivor in every empirical precedent in this repo
  (`workspace/probes/scl-gate-t3`, the predecessor's 19/19 run), so a
  `decode_failed` state (per C5's five-way taxonomy) is not expected to
  ever trigger for the SCL arm — unlike the SC arm, which has an explicit
  L1/L2 decode-failure path. `run.py::_scl_call` adds a defensive branch
  (`l1_survivor_count==0 or candidates_considered==0` → `decode_failed`)
  purely for C5 schema completeness. **Recommend: accept as a no-op safety
  net**, not a scientifically meaningful new code path.

## 4. Evidence that the reused functions are frame-range-generic

- `scripts.m2_prior_validation.run_g2_block` (`scripts/m2_prior_validation.py:2149-2321`):
  signature takes `bob`/`alice` arrays directly (no internal reference to
  `G2_EVAL_FIRST`/`G2_EVAL_LAST`/`g2_eval_blocks()`); `n = int(np.asarray(bob).size)`;
  `block_index` is used ONLY as a scalar passed to
  `chain.run_operational_block(block_index=...)` (seed derivation) and
  echoed into the returned record — never used to index into `eval_blocks`
  internally. Confirmed generic for any 32768-symbol (128-frame×256-pair)
  block, not limited to the 14 EVAL blocks.
- `chunk_frames` (`scripts/m2_prior_validation.py:984-1021`): returns
  `frames_a`/`frames_b` indexed by absolute post-skip frame number (0..
  `n_complete-1`), covering the WHOLE post-skip stream, not just the EVAL
  range — confirmed by the predecessor's own `_fidelity_check` already
  slicing `ctx["frames_a"][s:e+1]` directly by absolute frame index for
  EVAL blocks; this packet does the identical slice for A1_CAL/CHAR/HELDOUT
  frame ranges.
- `operational_seed_bits` (`comparison_bench/.../nbpolar/operational_f13.py:533-560`):
  `seed = SHA256("nbpolar-p16-operational-f13-seed:<master>:<n>:<block_index>:<counter>", ...)`
  — depends on nothing but `(master, n, block_index)`. This is the exact
  evidence underlying D_NEW_SEED_SCHEME above (no session/stratum salt
  exists in the frozen function; the caller must supply a unique
  `block_index` itself under a shared master).
- `scl_joint_decode` (`comparison_bench/.../nbpolar/scl_joint.py:170-...`):
  takes `bob` plus explicit `p1_table`/`p2_table`/`d1_positions`/`d2_positions`/etc.
  — no internal EVAL-range assumption; identical call shape already used by
  the predecessor on its 19-block subset.

## 4a. Finding: `openspec/changes/nbpolar-r2-fer-measurement-contract/T6_PACKET_SKELETON_20260928.md` exists

This preparation pass located an existing file,
`openspec/changes/nbpolar-r2-fer-measurement-contract/T6_PACKET_SKELETON_20260928.md`
(read-only; not modified), which records:

- All 15 R2 contract ledger rows as `DECIDED` (T4 round 1 + round 2), citing
  `docs/decision-log.md` 2026-09-28 "R2 剩余 8 项待决全部 DECIDED".
- `eval_seed = 2026092801`, `tag_master = 2026102801` (single value, shared
  by both sessions, per D-ACQ-07 O-7b) — §2 of that file.
- The identical 64-block layout (frame formulas, per-session/pooled counts)
  this packet's `run.py::build_session_blocks` independently derives — §3.
- P-1 (pooled-denominator reading, both pooled AND per-stratum tables
  required together) and P-2 (a `D-FER-06` STOP still counts as the
  one-shot attempt) — matching this packet's §3/§9 design.
- The budget gap is recorded there too, verbatim as `PENDING-BUDGET (SCL
  wall)`, with the SAME suggested (non-binding) numbers this packet's
  `run.py` uses (1200s/block, 2GiB/block, 3h total, 8-way parallel) — see
  §5 below.

**This packet's `run.py` still carries `R2_TAG_MASTER`/`R2_EVAL_SEED` as
`None` placeholders**, per this task's own originating instruction (leave a
placeholder field, to be filled from the frozen contract value and
cross-checked by the main thread before Pre-EXECUTE). The concrete integers
above are recorded here as a citation for that cross-check, not
transcribed into the executable script by this operator — inserting the
actual tag/seed constants into `run.py` is left as a deliberate main-thread
step, consistent with the general principle that this preparation pass does
not fabricate or independently finalize values that feed a Tier-Y
measurement's cryptographic tag derivation. **Decision point
D_TAG_MASTER_SOURCE**: main thread should verify
`T6_PACKET_SKELETON_20260928.md` §2 against `docs/decision-log.md` (2026-09-28
entry) and then fill `run.py`'s two placeholder constants directly.

## 5. Budget conflict — UNRESOLVED, flagged (not silently decided)

**Confirmed by `T6_PACKET_SKELETON_20260928.md` §6 (see §4a above)**: that
file independently records the identical gap under the heading
"PENDING-BUDGET (SCL wall) — flagged, not adjudicated here", with the same
SC-vs-SCL basis and the same suggested (non-binding) numbers as this
section. This is not a gap this operator introduced or discovered alone —
it is the single item the R2 contract's own T3/T6 authors left open after
adjudicating everything else on 2026-09-28.

`openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md` records
**D-ACQ-06 as DECIDED (2026-09-27)**: `wall_per_block=40s;
rss_per_block=2GiB; wall_total=5400s; machine_spec/parallelism=single-process
exclusive on this machine; stop_on_overbudget=STOP, no tuning` — basis: G3
measured **19.38-20.13 s/block** for the **SC** decoder
(`.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_ADJUDICATION.md:45`).

This task's own instruction (item 5) specifies different numbers: per-block
wall <=1200s, RSS <=2GiB, total wall <=3h (10800s), 8-way parallel — and
explicitly flags them `PENDING-BUDGET`. These are the predecessor packet's
own empirically-used values (`workspace/m2_scl_check_g2g3_success/run.py`:
`MAX_PARALLEL=8`, `BUDGET_WALL_S_PER_BLOCK=1200.0`), whose basis is
**SCL(L=16, top_m=4)** timing (~600s/block measured,
`workspace/probes/scl-gate-t3/results.json`; predecessor attempt-1 total
1643.5s for 19 SCL blocks + 2x session setup) — a ~30x per-block slowdown
vs the SC timing D-ACQ-06 was based on, and `8-way parallel` vs D-ACQ-06's
`single-process exclusive`.

**This is a real, unresolved conflict, not a cosmetic numbering
difference**: D-ACQ-06 was adjudicated for the SC decoder before any
SCL(L=16) real-data timing existed in this repo; the R2 measurement's
primary arm IS SCL(L=16). Running R2 under the literal DECIDED D-ACQ-06
numbers (40s/block wall cap, single-process) would abort essentially every
block (`resource_abort`), since a single SCL(L=16) block alone takes ~600s.
Running it under this task's proposed numbers without an explicit new PI
decision would mean executing under budget parameters that were never
formally adjudicated for this measurement.

**This packet does not resolve this conflict.** `run.py` implements the
task's proposed numbers as the operative constants (so the script is
complete and executable once authorized), but `STATUS.yaml`'s
`open_questions_for_main_thread` records this as a **blocking** item: the
main thread / PI must either (a) explicitly re-adjudicate D-ACQ-06 for the
SCL(L=16) decoder with new numbers (recommend: formalize this task's
proposed 1200s/block, 2GiB/block, 10800s total, 8-way parallel, as a
D-ACQ-06 amendment, citing the SCL empirical basis above), or (b) direct
this packet to use different numbers, before Pre-EXECUTE review can PASS.

## 6. Static self-check performed in THIS preparation pass (no execution)

- `python3 -m py_compile workspace/r2_fer_shg_64/run.py` → **pass**.
- AST scan for `%`-format `BinOp(Mod)` expressions → **0 found, 0 possible
  mismatches** (all string formatting uses f-strings).
- Independent reproduction of the block-boundary arithmetic (pure Python,
  no repo import needed — see the commands below, reproduced in this prep
  pass):
  - A1_CAL: `[(0,127),(128,255),...,(896,1023)]`, 8 blocks, last end=1023 — **matches**.
  - CHAR+HELDOUT: `[(1056,1183),...,(2208,2335)]`, 10 blocks, last end=2335,
    unused remainder = `2397-2335=62` — **matches** `DATA_LEDGER.md:46`.
  - `stratum_task` split of the CHAR+HELDOUT band (HELDOUT starts 1838):
    6 pure-CHAR (`never_decoded`) + 4 HELDOUT-touching
    (`heldout_model_selection`) — **matches** §2/§3 above and the
    `(14,4,14)` assertion in `run.py::build_session_blocks`.
  - EVAL band reused verbatim from `scripts.m2_prior_validation.g2_eval_blocks()`
    (not re-derived) — 14 blocks, 2398-4189.
- Path existence (existence/listing only — no raw `.ttbin` content read):
  - `workspace/r2_fer_shg_64/` → created, empty before this pass's writes.
  - `workspace/r2_fer_shg_64/results.json` → **absent** (confirmed).
  - Raw primaries for both acquisitions
    (`D:\Data\Raw Data\2026.1.13\SHG_Type2PPLN_3s_2026-01-13_162106\`,
    `...\SHG_Type2PPLN_3s_2_2026-01-13_162148\`) → **both exist**
    (directory listing only; no byte of content read).
  - `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
    → exists.
  - Both `per_block_outcomes.jsonl` files → exist; read (JSON lines) for §2.

## 7. Diff summary against the predecessor's `run.py`

Full rewrite rather than a line-oriented patch (the block-generation and
per-block-arm logic changed structurally — hardcoded 19-tuple `TARGETS` list
replaced by a pure `build_session_blocks()` generator over frozen frame
constants, matching the existing repo pattern already used by
`g2_eval_blocks()` for the EVAL band). Every change is one of the rows in
the §0 delta table above; nothing else in the reused call chain
(`_load_mod`, `_load_scl_joint`, `_reproduce_session_context`'s alignment/
CAL-fit steps, the `accepted`/`exact`/`undetected`/`verify_failed`
formulas, the per-block budget mechanism, `reruns=0`) changed in substance.
No frozen decoder/prior/protocol file was read for editing (import-only, as
listed in §1 "Allowed to read").

## 8. Test / evidence matrix (acceptance IDs)

| ID | Check | Evidence |
|---|---|---|
| S1_py_compile | `python3 -m py_compile run.py` exits 0 | done, §6 |
| S2_ast_percent | AST scan: 0 `%`-format expressions | done, §6 |
| S3_paths_exist | both raw `.ttbin` primaries, P16 construction json, both `per_block_outcomes.jsonl` files all exist on disk | done, §6 (existence only) |
| S4_block_arithmetic | 64-block pool arithmetic (8/10/14 per session, 62-frame CHAR/HELDOUT remainder, 6/4 CHAR/HELDOUT sub-split) matches `DATA_LEDGER.md` §7 exactly | done, §2/§6 |
| S5_results_absent | `results.json` and all 64 `part_*.json` absent before launch | confirmed, §6; also checked in-code at runtime |
| S6_no_predecessor_write | `workspace/m2_scl_check_g2g3_success/` untouched by this preparation pass | confirmed: no write tool invoked against that path this session |
| S7_no_git_write | no `git add`/`commit`/`push` invoked this session | confirmed |
| S8_placeholder_guard | `R2_TAG_MASTER`/`R2_EVAL_SEED` are `None`; `_reproduce_session_context` calls `_fail()` if either is still `None` | confirmed by code inspection, `run.py` |
| E1_fidelity_scope | **Pre-EXECUTE gate**: at execution time, a fidelity mismatch on an EVAL block excludes only that block (D_NEW_FIDELITY_SCOPE), never silently withheld/merged elsewhere | pending execution + main-thread ruling on D_NEW_FIDELITY_SCOPE |
| E2_no_new_data | `results.json["blocks"]` covers exactly the 64 frozen-pool blocks; no other frame/block ever opened | pending execution (structural: pool built from frozen constants, never derived from runtime input) |
| E3_no_state_write | grep after run: no byte touched under `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/`, `.../G3-CONFIRM/`, `results/`, `comparison_bench/outputs_comparison/`, any pre-existing `workspace/m2_prior_validation/*` file, or `workspace/m2_scl_check_g2g3_success/*` | pending execution |
| E4_one_shot | `results.json` and all 64 `part_*.json` absent before the run (checked in-code); reruns counter stays 0 unless an execution-defect rerun is explicitly recorded | pending execution |
| E5_budget | per-block wall/RSS recorded in each part file; total-wall backstop recorded; any `resource_abort_*`/hard-terminate/total-budget status is reported, never silently dropped | pending execution; budget NUMBERS themselves pending §5 resolution |
| E6_no_verdict | `results.json` contains no `FER_MEASURED_AT_CONTRACT`/PASS/FAIL string anywhere | pending execution (structural: `run.py::main` never writes one, by construction) |
| E7_undetected_isolation | `undetected` never counted into `D_valid_denominator` or the numerator in any stratum grouping | pending execution (structural: `_taxonomy_counts` excludes it by construction) |

## 9. Stop rules (binding at execution time)

- Any of the four decision points in §3 unresolved by the main thread ⇒ do
  not proceed to Pre-EXECUTE review.
- §5's D-ACQ-06 budget conflict unresolved ⇒ do not proceed to Pre-EXECUTE
  review (this is the single highest-priority open item in this packet).
- `R2_TAG_MASTER`/`R2_EVAL_SEED` still `None` ⇒ `run.py` refuses to run
  (enforced in code, not just documentation).
- Any EVAL-block fidelity mismatch during execution ⇒ that block excluded
  from all tallies, reported by id (D_NEW_FIDELITY_SCOPE), execution
  continues for the other 63 blocks.
- Any `undetected` outcome (pooled `>=1`) ⇒ `stop_undetected=true` recorded
  at top level; per D-FER-06 (`DECIDED`, O-6a) this defers the
  `FER_MEASURED_AT_CONTRACT` verdict pending PI review — this script itself
  makes no adjudication, only surfaces the flag and the block ids. **Per
  P-2** (`T6_PACKET_SKELETON_20260928.md` §5 step 6, `R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md`
  §9.3): this STOP still counts as the one-shot Tier-Y attempt — it must
  NOT be discarded and rerun to obtain a clean (`undetected=0`) result.
  Whether a deferred verdict can later be promoted from this same result,
  or requires an entirely new measurement, is a separate PI decision this
  script/operator does not make.
- Total wall budget (currently 10800s, PENDING per §5) exceeded ⇒ launcher
  stops starting new blocks; not-yet-started blocks recorded as
  `resource_abort_total_wall_budget_not_started`, never silently dropped.
- `D < 56` (n=56, D-FER-03) after removing `undetected`/`resource_abort`
  from any grouping used for the n=56 comparison ⇒ main thread must treat
  as `INSUFFICIENT`/`INCONCLUSIVE` per `R2_REMAINING_DECISIONS_20260928.md`'s
  judgment-rule draft step 3 — this script computes `D` per grouping but
  makes no INSUFFICIENT/INCONCLUSIVE determination itself.

## 10. Return conditions

- **Complete**: all frozen items above resolved, packet passes Pre-EXECUTE
  review, PI authorization on file verbatim, execution runs to completion
  (exit 0) or to a recorded STOP condition, Pre-RESULT review requested.
- **Blocked**: any of §3's decision points, §5's budget conflict, or the T4
  ledger rows in `R2_REMAINING_DECISIONS_20260928.md` remain unresolved —
  report the specific blocking item(s) to the main thread; this operator
  does not guess or silently pick a default to unblock itself.

## 11. Current state

`STATUS.yaml`: `state: prepared_awaiting_contract_freeze_and_pre_execute`.
This packet has **not** been executed, has **not** been reviewed
(Pre-EXECUTE not yet requested), and its `run.py` has **not** been run
(and cannot be, until `R2_TAG_MASTER`/`R2_EVAL_SEED` are filled in). Next
step is main-thread adjudication of §3's decision points and §5's budget
conflict, formal `DECIDED` write-back of the remaining R2 contract ledger
rows, then independent Pre-EXECUTE review.
