# TASK PACKET — NBPOLAR-M2-PRIOR-G4-INVENTORY (exhaustive public-message inventory, Release pattern, CAL frames listed)

**GATED PACKET. This packet authorizes NOTHING.** Execution requires the main thread to paste
`AUTHORIZATION_PROMPT.md` **verbatim** (AGENTS.md §10.1); until then `STATUS.yaml` stays
`stage: PACKET_DRAFT` / `authorizations: []` and **no G4 work of any kind may be performed**.
One complete frozen packet before delegation; the operator never marks its own work accepted.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G4-INVENTORY/`
- Change: `openspec/changes/nbpolar-prior-rebaseline/` — D6 gate **G4** (exhaustive public-message
  inventory, Release pattern, with the CAL frames listed).
- Venv (for the packet-local builder only): `/home/karel_303/.venvs/timetagger/bin/python`
- Nature: **Tier-Y one-shot RECORD/AUDIT gate**. No decoder, no SC call, no tag generation, no raw-data
  read, no re-derivation. G4 inventories **already-executed, already-adjudicated** public messages under
  the frozen M2 contracts (G1 / G1R2 / G2 / G3). It changes no decode conclusion and re-runs nothing.
- M2 state at dispatch (STATE.md §4.1): `VALIDATED_AT_FROZEN_CONTRACT` (2nd rung; R2 FER gate and R3
  efficiency gate NOT done).

## Goal

Produce ONE exhaustive, countable, artifact-traceable inventory of **every public message** that the
frozen M2 track has already emitted, covering:

1. **G1** (SHG `_1`, w=500/LINEAR contract): contract parameters, derived alignment record, closure
   ledger/layout, CAL frame lists, NLL/delta-profile results, any disclosure/tag field — or an explicit
   `none recorded` row where the frozen artifacts contain no such field.
2. **G1R2** (SHG `_1`, w=200/CIRCULAR contract): same enumeration.
3. **G2** (SHG `_1`, three-arm one-shot): per-block `key_dependent_bits` / `public_control_bits`
   disclosure, the 42 tags + `tag_master 2026103001` (INHERITED), CAL lists (A1-CAL 1024, CAL32 32),
   freeze/threshold/contract values published, verdict artifacts.
4. **G3** (SHG `_2`, three-arm one-shot): same enumeration with `tag_master 2026110101`, CAL lists,
   participation-disclosure statement as a listed public message.
5. **CAL frames listed explicitly** (spec.md "sacrificed small CAL" requirement): every sacrificed CAL
   frame ID list, per session, as recorded in the frozen `cal_ids*.json` artifacts — listed, never
   re-derived, re-allocated, or edited.
6. **CONTRACT/structural rows**: N, K1/K2, P16 digest + orders, W_P/W_S/MOD/skip/frame_pairs/floor/
   chunk/bin, prior triple + reveal-bits diagnostic (per `docs/SECURITY_MODEL.md` skeleton).
7. **Release-pattern mapping**: each row classified into one frozen handling class (§ Inventory
   definition), filling the 0-bit skeleton in `docs/SECURITY_MODEL.md` § "Public-message inventory
   skeleton" with **values read from the frozen artifacts** (the skeleton document itself is NOT edited
   in-packet — Main-thread adjudication 2026-09-22 item 8: skeleton not written back; the filled values
   land in this packet's outputs, and any `docs/SECURITY_MODEL.md` write-back is a separate main-thread
   docs commit at archive stage).

### G4 closure domain (Main-thread adjudication 2026-09-22, item 1)

- **IN scope (exhaustive):** every public message already emitted by G1 / G1R2 / G2 / G3, the CAL frames
  明细 (listed frame-ID detail per session), and the Release-pattern mapping. Nothing else.
- The census enters **only as the quoted-σ source** (frozen value #15) — a citation source, not a domain.
- **OUT (explicit):** S8/S9 synthetic probe parameters; Stage-1 test outputs. Never inventoried, never
  read, never cited.
- Any closure-domain expansion = **a NEW freeze**; the operator may not widen the domain on the fly during
  execution (such a need ⇒ STOP / return condition 2; Main-thread adjudication 2026-09-22, item 1).

## Non-Goals

No decode of any kind; no SC calls; no tag generation; no alignment derivation or census reproduction
(the census σ is **quoted as a frozen value only**, never recomputed); no gate arithmetic (Wilson /
`B_tail` / `delta_min` are N/A for G4); no λ decomposition, no disclosure cap, no Stage-3 measurement
set (see boundary below); no FER/efficiency/qualification/promotion/composable claim; no S9 citation as
FER/efficiency evidence; no model selection, no K change, no construction re-derivation; no edit of any
existing verdict/adjudication/freeze/STATUS artifact of G1/G1R2/G2/G3; no read of raw SHG acquisition
data; no writes outside this packet dir; no code change in any existing module; no read, inventory, or
citation of S8/S9 synthetic probe parameters or Stage-1 test outputs — explicitly outside the G4 closure
domain (Main-thread adjudication 2026-09-22, item 1).

### Scope boundary: the Stage-3 measurement set is NOT part of this packet

- **D6's "Stage-3 measurement set"** = `MACRO_PLAN_20260921.md` §5 **Stage 3 真实数据可行性与测量集**:
  a *preregistered disclosure cap* plus *per-block λ decomposition* (B1 → Müller eq 11/13, H(q)→
  empirical H(X|Y) substitution preregistered before use, `undetected` never merged in), i.e. the
  R2/R3-line measurement work in `REAL_DATA_CORRECTION_ROADMAP_20260922.md`.
- **Not** the parent packet `NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md` §6 "Stage 3" (the G2
  freeze + one-shot execution) — that stage is closed (G2 SUCCESS). Two different "Stage 3"s; do not
  conflate them.
- **G4 covers ONLY the inventory part of D6.** G4 computes no λ_total, sets no cap, publishes no
  per-block decomposition, and produces no rate/FER/efficiency number. The Stage-3 measurement set is a
  **separate, not-yet-frozen deliverable** requiring its **own packet, own freeze, and own user
  authorization**; G4's inventory is a read-only *input* to it. D6 requires G4 **and** the Stage-3 set
  (plus R2/R3 gates) before any claim-bearing statement — neither substitutes for the other.

**Main-thread adjudication 2026-09-22 (item 2):** the packet-internal disambiguation above **stands**. In the
D6/spec formulation "G4 + Stage-3", Stage-3 = `MACRO_PLAN_20260921.md` §5 measurement set and is **wholly
carved out of G4** (its own packet, own freeze, own authorization); G4 computes no λ, no disclosure cap, no
FER. Nothing about Stage-3 is decided inside this packet at execution time.

## Impact Scope

WRITE (new additive files only, this packet dir exclusively):
`g4_build_inventory.py` (packet-local, read-only builder), `g4_freeze_config.json` (Phase-A input
manifest), `g4_inventory.json`, `g4_inventory.md`, `g4_counts.json`, `g4_run_log.md`, this packet's
`STATUS.yaml` (stage/counters/artifacts/result only — never another packet's STATUS).

FORBIDDEN (hard stop ⇒ second return condition):
modify anything under `scripts/`, `formal_ir/`, `src/`, `experiments/`, `tools/`, `results/`,
`comparison_bench/outputs_comparison/`, `comparison_bench/tests/`; modify `prior_m2.py`,
`sc.py`, `algebra.py`, `transform.py`, or `scripts/m2_prior_validation.py`; modify
`docs/SECURITY_MODEL.md` or any G1/G1R2/G2/G3 packet artifact (their STATUS/verdicts/freeze files are
read-only inputs); write under `results/` or `comparison_bench/outputs_comparison/` (append-or-not rule
does not apply — G4 writes there NEVER); write anywhere outside this packet dir (including
`workspace/` and `workspace/probes/` — single output route confirmed, Main-thread adjudication 2026-09-22
item 7); read any raw SHG acquisition file; rerun the census or any alignment/alignment-repair;
recompute the census σ; add checksums/SHA-256/atomic writes/locking/retry frameworks (AGENTS.md §5.7 —
provenance is `path + field locator + artifact content as-is`, not digests); any Pre-EXECUTE/Pre-RESULT
self-approval; any decision-log / project-memory / index update in-packet.

## Frozen constants (verbatim — any change requires a NEW freeze; do not guess)

| # | Key | Value | G4 handling |
|---|---|---|---|
| 1 | `N` | 32768 | recorded verbatim as contract context (inventory row, not re-derived) |
| 2 | `K1` | 319 | recorded verbatim (frozen; D4 deferred, no re-split) |
| 3 | `K2` | 6492 | recorded verbatim (frozen; no increase) |
| 4 | P16 construction digest | `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` | quoted verbatim; inner P16 procedure digest of the canonical `construction_and_allocation.json` (wrapper file's own sha256 differs — P17-established; G4 computes NO digest) |
| 5 | `W_P` | 200 | recorded verbatim |
| 6 | `W_S` | 500 | recorded verbatim (sensitivity readout only) |
| 7 | `MOD` | CIRCULAR | recorded verbatim |
| 8 | `skip` | 702 | recorded verbatim (`INHERITED_NOT_DERIVED`) |
| 9 | `frame_pairs` | 256 | recorded verbatim |
| 10 | `floor` | 1e-15 | recorded verbatim |
| 11 | `chunk` | 512 | recorded verbatim (`chunk_rows`) |
| 12 | `bin` | 200 ps | recorded verbatim = pairing `bin_width_ps=200` (census frozen block). NOT the alignment scan `bin=100 ps` — different constant; G4 derives neither |
| 13 | G2 `tag_master` | 2026103001 | recorded verbatim, labeled **INHERITED** (from G1R2; EVAL_SEED 2026093001 by frozen rule `TAG_MASTER = EVAL_SEED + 10000`) |
| 14 | G3 `tag_master` | 2026110101 | recorded verbatim (EVAL_SEED 2026100101, same frozen rule) |
| 15 | census σ | 114.43029692866367 | **frozen value, quoted only** — if G4 cites any census conclusion it MUST carry the label "frozen quoted value, not recomputed in G4" + its source artifact path. Recomputation ⇒ STOP |

Not in this freeze list (e.g. other census constants `d`/`period_ps`/`threshold_ps`/`gate_ps`, gate
values `B_tail 2.0e-4` / `delta_min 0.020` / Wilson `z=1.96`) are **not restated, not verified, not
computed** by G4 — they remain whatever the G1–G3 artifacts say. Needing them ⇒ new freeze.

## Discipline mapping (G3 template → G4; inapplicable decode items are marked N/A, never silently dropped)

| G3 discipline item | G4 status |
|---|---|
| Tier-Y one-shot, `g4_runs: 1`, `reruns: 0` | **RETAINED** (applies to the inventory build: exactly one complete build; see rebuild rule in Stop rules) |
| Independent Pre-EXECUTE PASS + authorization recorded BEFORE the build | **RETAINED** |
| Independent Pre-RESULT PASS before any publication/commit | **RETAINED** |
| Verbatim user authorization in `STATUS.yaml` before dispatch | **RETAINED** (`authorizations: []` = not authorized) |
| `undetected` isolation (never merged into success/FER) | **RETAINED as reporting discipline**: G2/G3 `undetected` counts (0/42 each, as recorded in their artifacts) are listed as isolated rows; G4 asserts NO success/FER from them |
| Disclosure recount discipline | **RETAINED**: G4 sums `key_dependent_bits`/`public_control_bits` over the frozen `per_block_outcomes.jsonl` rows and compares to the frozen recount (G2/G3: key 1,432,998 = 34,119×42; public 13,765,206 = 327,743×42). Mismatch ⇒ STOP/blocker; **never publish a corrected number** — frozen values stand |
| Every TO-FREEZE non-null (null/absent ⇒ hard error, never a default) | **RETAINED** (`g4_freeze_config.json` fields) |
| Ambiguity ⇒ STOP and report (return condition 2), never guess | **RETAINED**, incl. the ambiguity register below — except the A-class σ cross-artifact string check, now an allowed resolved rule (Main-thread adjudication 2026-09-22, item 6) |
| Participation disclosure (G3: decoder/model independence, NOT no-prior-contact) | **RETAINED** wherever G3 artifacts are cited |
| No decision-log / memory / index updates in-packet | **RETAINED** |
| Phase-A first-contact rules for SHG `_2`, alignment reproduction vs census σ | **N/A** — G4 reads **no raw acquisition data** and performs **no derivation**; both SHG acquisitions stay untouched. Reason: inventory operates solely on already-produced derived artifacts |
| Three-arm decode A1/A2/B, EVAL blocks, COMPLETE-BLOCKS-ONLY | **N/A** — no decode, no frames allocated. Reason: G4 touches no frame and runs no decoder |
| Wilson gate, `B_tail`, `delta_min`, `g2/g3_blocks` | **N/A** — G4 has no statistical verdict; success = completeness criteria (§ Success criteria). Values are not restated or evaluated |
| SC calls, tag invocations, decode wall budget 900 s | **N/A** (expected `sc_calls: 0`, `tag_invocations: 0`); replaced by the inventory budget in Stop rules |
| K/construction enforcement at decode time | **N/A** as execution constraint (nothing decodes); retained as recorded contract rows |
| "Never pad/reuse/borrow frames" | **N/A as a frame-handling rule** (no frames handled); **RETAINED as a listing rule**: CAL/segment frame IDs are copied exactly as frozen in `cal_ids*.json`; never re-derived, re-allocated, or edited |

## Inventory definition (frozen row schema + Release-handling enum — extension requires a new freeze)

Rows are entries of `g4_inventory.json` with fields:
`id` (stable, `G4-<STAGE>-<nnn>`), `stage` (`CONTRACT|G1|G1R2|G2|G3`), `message_class`
(`contract_param|construction|alignment_record|ledger_allocation|cal_frame_list|fitted_prior|
reveal_bits_diagnostic|disclosure_bits|tag|threshold_or_gate_record|result_publication|
participation_disclosure|blocked|none_recorded`), `message` (what is public), `producer`,
`key_dependent` (bool), `size_bits` (int, or `0`, or `N/A` with reason), `count` (e.g. 42 tags),
`seed_mask_code_ref` (e.g. `tag_master 2026103001`), `source_artifact` (repo-relative path),
`source_locator` (JSON field / JSONL row selector / markdown section), `release_handling` (enum below),
`status` (`frozen|quoted|derived_read_only|to_freeze`).

`release_handling` enum (Release fail-closed pattern, `decision-log.md` F3 / D3). **Main-thread
adjudication 2026-09-22 (item 3):** the six-class enumeration is accepted as a **packet-local freeze**
(no separate freeze review required); an unassignable row ⇒ still STOP.

- `counted_in_leak_IR` — disclosure actually charged to leakage (the per-block key/public bits).
- `charged_0_labeled_public_ec_only_not_secure` — Release charges 0 bits for in-sample estimation and
  pays with the label (`public_ec_only_not_secure`, `composable_security_claim_flag=0`); G4 records
  which rows sit in that pattern without importing any composable claim. **Scope limit (Main-thread
  adjudication 2026-09-22, item 3):** a *对照记录行* — a comparison record row against the Release
  in-sample mode only; **never counted in NB-Polar's own accounting** (NB-Polar accounts sacrificed CAL
  frames via `sacrificed_excluded_from_denominator`).
- `result_publication` — **Main-thread adjudication 2026-09-22 (item 4):** result announcements
  (NLL / δ-profile results, etc.) are entered exhaustively-first with this handling and `size_bits`
  0 / `N/A`; this value joins the enumeration by that adjudication (the six pre-existing classes remain
  the packet-local freeze per item 3).
- `sacrificed_excluded_from_denominator` — CAL frames: excluded from the key denominator AND listed.
- `diagnostic_only_never_lambda` — reveal bits (~18–22, params·log2(n) order-of-magnitude).
- `structural_public_parameter` — N/K/orders/window/MOD/skip/thresholds: public by construction.
- `blocked_never_public` — fail-closed rows: messages that must NOT be public (raw key symbols, raw
  CAL contents, seeds before use). G4 lists them as `blocked` with size `N/A`, asserting nothing about
  content.

Any row that cannot be assigned exactly one enum value ⇒ **STOP** (return condition 2). Enum changes ⇒
new freeze.

## Input manifest (READ-ONLY; every path must exist at Phase A — missing path ⇒ STOP)

Contract / rules / gate text:
1. `openspec/changes/nbpolar-prior-rebaseline/design.md` — D6 (G4 definition), D3 (Release 0-bit
   labeling + CAL sacrifice), D7 (frozen list).
2. `openspec/changes/nbpolar-prior-rebaseline/specs/nbpolar-prior-rebaseline/spec.md` —
   validation-gates + sacrificed-small-CAL ("listed in the public-message inventory") requirements.
3. `openspec/changes/nbpolar-prior-rebaseline/tasks.md` — T4/T8: G4 needs its own packet +
   authorization; inventory recomputable-from-frozen-artifacts acceptance line.
4. `docs/nbpolar/STATE.md` §4.1 — promotion ladder (G4 sits inside the READY_FOR_QUALIFICATION
   conjunct; see Success criteria ladder note).
5. `docs/SECURITY_MODEL.md` § "NB-Polar M2 CAL / prior accounting" + § "Public-message inventory
   skeleton (M2 track, 0-bit shape)" — the skeleton G4 fills (read-only).
6. `docs/nbpolar/MACRO_PLAN_20260921.md` §5 Stage 3 (measurement-set boundary) + §9 F3 (Release
   fail-closed inventory pattern).
7. `docs/decision-log.md` — F3 entry (Release pattern provenance, ~line 5327).
8. `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md` — R2/R3/Stage-3 ownership (boundary only).

G1 packet + outputs:
9. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/{TASK_PACKET.md, FREEZE_REVIEW.md,
   AUTHORIZATION_PROMPT.md, STATUS.yaml, g1_freeze_config.json, G1_ADJUDICATION.md}`
10. `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/{g1.json, delta_profiles.json,
    cal_ids.json, cal_ids_closure.json, g1_closure_reproduction.json, run_log.md, run_log_closure.md}`

G1R2 packet + outputs:
11. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/{TASK_PACKET.md, DELTA_REVIEW.md,
    AUTHORIZATION_PROMPT.md, STATUS.yaml, g1r2_freeze_config.json, G1R2_ADJUDICATION.md}`
12. `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/{g1.json, delta_profiles.json,
    cal_ids.json, cal_ids_closure.json, g1_closure.json, run_log.md, run_log_closure.md}`

G2 packet + outputs:
13. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/{TASK_PACKET.md, g2_freeze.md,
    AUTHORIZATION_PROMPT.md, STATUS.yaml, g2_freeze_config.json, G2_ADJUDICATION.md}`
14. `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/{g2_summary.json,
    per_block_outcomes.jsonl, cal_ids.json, run_log.md}`

G3 packet + outputs:
15. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/{TASK_PACKET.md, AUTHORIZATION_PROMPT.md,
    STATUS.yaml, g3_freeze_config.json, G3_ADJUDICATION.md, G3_ADJUDICATION_PREWRITE.md,
    PRE_RESULT_REVIEW.md, G3_PROCESS_DEVIATION.md}`
16. `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3/{g3.json, g3_summary.json,
    per_block_outcomes.jsonl, cal_ids.json, run_log.md, input/g3_freeze_config.json}`

Construction + provenance context:
17. `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/
    construction_and_allocation.json` (canonical P16 path; G4 records path + K/orders presence, computes
    no digest).
18. `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md` + `g1_freeze.md` (parent
    contract; source of the §6-Stage-3 vs MACRO-Stage-3 disambiguation).
19. `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/PROMPT.md` (T4 inventory-skeleton
    provenance) and `.workbuddy/queue/NBPOLAR-M2-PRIOR-K-RESPLIT-D4/D4_RECORD.md` (report-only K
    context; G4 records that D4 changed nothing).

Explicitly NOT in the input manifest: raw SHG files; `workspace/dual_rule_census_20260921.py`; the
census script/packet (σ is quoted from items 15/16 and `docs/decision-log.md`, never re-derived — census is
the σ quoted source only); any sibling checkout; `results/`; `comparison_bench/outputs_comparison/`;
**S8/S9 synthetic probe parameters; Stage-1 test outputs** (explicitly outside the G4 closure domain,
Main-thread adjudication 2026-09-22 item 1 — the Stage-1 `PROMPT.md` in item 19 stays manifest-listed as
skeleton provenance, but no Stage-1 test output is read).

## Output spec (all under this packet dir; additive; never overwrite an existing file)

1. **`g4_freeze_config.json`** (Phase A): input manifest with per-item `path` + `exists` +
   `locators_used`, frozen-constants block copied verbatim from the table above, outcome strings from
   the preregistration table below, budget, `authorizations` pointer. Every TO-FREEZE field non-null.
2. **`g4_inventory.json`** (Phase B): `{packet, generated_by, row_count, rows:[...]}` with the row schema
   above. This is the machine-countable list.
3. **`g4_inventory.md`** (Phase B): human report — scope + no-claim statement; per-stage tables
   (CONTRACT/G1/G1R2/G2/G3); **CAL frames listed** (SHG `_1`: A1-CAL 1024-frame list and CAL32 32 IDs;
   SHG `_2`: CAL32 32 IDs + `a1_cal_ids` as recorded — printed as ranges + explicit ID arrays, sourced
   from `cal_ids*.json`); Release-pattern mapping summary (row counts + bit totals per
   `release_handling`); disclosure cross-check block vs the frozen recount; `undetected` isolation line;
   completeness declaration (§ Success criteria); G3 participation-disclosure statement where G3 is
   cited; inputs list verbatim from `g4_freeze_config.json`.
4. **`g4_counts.json`** (Phase B): `rows_by_stage`, `rows_by_message_class`, `rows_by_release_handling`,
   `key_bits_sum`, `public_bits_sum`, `tags_total`, `cal_frames_listed{shg_1,shg_2}`,
   `cross_check{key:{computed,frozen,match}, public:{...}, tags:{...}}`, `sc_calls: 0`,
   `tag_invocations: 0`, `g4_runs`, `reruns`.
5. **`g4_run_log.md`**: commands run, timestamps, per-ID status.
6. `STATUS.yaml` updated by the operator (stage/counters/artifacts/result only).

**Single output route confirmed (Main-thread adjudication 2026-09-22, item 7):** the ONLY files this packet
may ever write are the five outputs listed above — `g4_freeze_config.json`, `g4_inventory.json`,
`g4_inventory.md`, `g4_counts.json`, `g4_run_log.md` — plus this packet's own `STATUS.yaml`. Nothing is ever
written under `workspace/probes/` or anywhere else outside this packet dir.

## Success criteria (exhaustiveness — all must hold; FAIL ⇒ no publication, blocker return)

- **G4-0** Pre-conditions: `.git/HEAD` = `codex/nbpolar-phase0`; every input-manifest path exists;
  `g4_freeze_config.json` complete, all TO-FREEZE non-null; this authorization recorded in
  `STATUS.yaml` **before** the Phase-B build.
- **G4-1** Traceability: every row carries a resolvable `source_artifact` + `source_locator`; no row
  cites a path outside the input manifest without a recorded STOP; zero rows with `status: to_freeze`
  at the end (each resolved to a value read from an artifact or explicitly reported as a blocker).
- **G4-2** CAL listing: all sacrificed CAL frame lists printed (SHG `_1` A1-CAL 1024 + CAL32 32;
  SHG `_2` CAL32 32 + `a1_cal_ids` as recorded), byte-identical membership to the source
  `cal_ids*.json` arrays (set equality check in the builder; mismatch ⇒ STOP), labeled
  `sacrificed_excluded_from_denominator`.
- **G4-3** Release mapping + accounting: every row has exactly one enum value; computed disclosure sums
  equal the frozen recount (G2/G3: key 1,432,998 = 34,119×42; public 13,765,206 = 327,743×42);
  `undetected` listed separately (0/42 as frozen) and never merged; mismatch anywhere ⇒ blocker, frozen
  numbers stand.
- **G4-4** Countability + no-omission declaration: `row_count` == number of JSON rows == number of MD
  table rows == sum of `rows_by_stage` == sum of `rows_by_release_handling`; every expected field class
  that is ABSENT in a stage gets an explicit `none_recorded` row (draft-time expectation, to be
  re-verified at execution: G1/G1R2 `g1.json` contain no `tag` and no
  `key_dependent_bits`/`public_control_bits` fields ⇒ explicit `none_recorded` rows, never silence —
  exhaustive-first publication convention confirmed, Main-thread adjudication 2026-09-22 item 4); a written
  enumeration rule ("all rows = every disclosure-bearing/public field in every input-manifest artifact,
  plus contract rows, plus explicit none rows") appears in `g4_inventory.md`; **no claim sentences**
  (no FER/efficiency/qualification/promotion/composable-key statement; no S9 citation).
- **R1** Independent Pre-RESULT review PASS against G4-0…G4-4 before any publication/commit.
- **R2** Main-thread adjudication (only the main thread may accept; operator never self-accepts).

**Ladder note (STATE.md §4.1, no level skipping):** G4 PASS records the G4 conjunct of the
`READY_FOR_QUALIFICATION` row (≥2 independent sessions + sample size + **G4** + independent
Pre-RESULT) and **does not, by itself, move M2**: state stays `VALIDATED_AT_FROZEN_CONTRACT` (R2 FER
gate and R3 efficiency gate remain outstanding and cannot be replaced by G4). G4 FAIL/incomplete leaves
M2 at `VALIDATED_AT_FROZEN_CONTRACT`, blocks the `READY_FOR_QUALIFICATION` conjunct, and keeps every
D6 claim-bearing statement forbidden. G4 never promotes, never demotes, and cannot be satisfied by a
partial inventory.

## Preregistered outcome strings (**FROZEN** — proposed ⇒ frozen by Main-thread adjudication 2026-09-22 item 5; recorded at authorization, BEFORE the build — G3 three-state discipline)

| Outcome | State string |
|---|---|
| Complete inventory, G4-0…G4-4 + R1 PASS | `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE` |
| Incomplete / any G4 criterion fails / blocker returned | `NBPOLAR_M2_PRIOR_G4_INVENTORY_INCOMPLETE_BLOCKED` (failure layer stated in the body text; no new labels) |
| Builder crash with **no** output file written | no state string; recorded in `STATUS.yaml` counters with the crash reason; corrective-rebuild rule below applies; **no** science status invented |

No statistical FAIL/INCONCLUSIVE verdict exists for G4 (no CI, no gate arithmetic — N/A by design).

## Stop rules

- Budget: **≤ 300 s wall / 2 GiB RSS, single-threaded** (G4-new value, **FROZEN** — proposed ⇒ frozen by
  Main-thread adjudication 2026-09-22 item 5 — reads and aggregation only; decode budgets 900 s are N/A).
  Exceeded ⇒ STOP, record as blocker, no
  tuning, no narrowing of scope to fit the budget.
- Expected resource counters: `sc_calls: 0`, `tag_invocations: 0`, `g4_runs: 1`, `reruns: 0`.
- **Rebuild rule (one-shot analogue; FROZEN — proposed ⇒ frozen by Main-thread adjudication 2026-09-22
  item 5):** a corrective rebuild is permitted ONLY if the first build
  crashed leaving **zero** inventory output files (exactly **one** such rebuild), and must be recorded in `STATUS.yaml`
  (`rebuild: 1, reason: ...`). Once ANY complete `g4_inventory.json` exists, no rebuild, re-generation,
  patch, or "addendum" run is allowed — any need afterwards ⇒ STOP/blocker + new freeze.
- Any raw SHG read, any decode/SC/tag invocation, any write outside this packet dir, any forbidden-path
  touch ⇒ STOP + blocker.
- Any attempt to recompute census σ, alignment, pairing, CAL allocation, or K/orders ⇒ STOP.
  **Allowed (Main-thread adjudication 2026-09-22, item 6):** a cross-artifact **string** consistency check
  of the quoted σ across the G3 freeze / adjudication / `docs/decision-log.md` (pure traceability, no
  numeric work; the operator executes it directly). Any **numeric** re-derivation of σ remains forbidden ⇒ STOP.
- Recount cross-check mismatch ⇒ STOP; frozen numbers stand; never publish a corrected number.
- Missing/null TO-FREEZE value ⇒ hard error (never a default).
- Any ambiguity, incl. any row not fitting the enums, any schema conflict between artifacts, any
  `Stage 3` referent ambiguity ⇒ STOP (return condition 2), never guess.

### Ambiguity register (pre-declared STOP triggers — operator resolves none of these alone)

A1: whether the *filled skeleton* also belongs in `docs/SECURITY_MODEL.md` — **RESOLVED, Main-thread
adjudication 2026-09-22 (item 8):** NO in-packet; the skeleton is not written back, the filled values live
only in this packet's outputs, and any docs update is a separate main-thread docs commit at archive stage
(statement retained in-packet). A2: whether G1/G1R2 truly
produced zero disclosure/tag messages or merely recorded them elsewhere (verify; `none_recorded` only
if genuinely absent). A3: whether the Stage-3 measurement set's own disclosure cap must be *referenced*
by any inventory row (packet: reference-only row allowed, no cap computed). A4: any G4 scope item read
from D6 that is neither inventory nor CAL-listing nor Release-mapping ⇒ main-thread decision.

**A-class rule (Main-thread adjudication 2026-09-22, item 6) — RESOLVED, no longer an automatic STOP:**
a cross-artifact **string** consistency check of the quoted census σ across the G3 freeze, the G3
adjudication, and `docs/decision-log.md` is **allowed** as a traceability check and is executed directly by
the operator (no new authorization, no new freeze). Any **numeric** re-derivation/recomputation of σ stays
forbidden ⇒ STOP. Record retained here for provenance.

## Return (exactly two — AGENTS.md §10.1)

1. **All-complete:** per-ID PASS (G4-0…G4-4, R1, R2 noted as pending-main-thread) with output paths,
   row/count arithmetic (JSON == MD == counts sums), cross-check block, run log, scoped
   `git status -- <packet dir>`.
2. **Concrete blocker:** failing command + exact error/traceback + attempted remedies + the SINGLE
   decision needed from the main thread.

## Authorization statement

**This packet itself authorizes nothing.** No inventory work, no input-manifest freeze, no builder
script, not even a path-existence listing may be performed until the main thread pastes
`AUTHORIZATION_PROMPT.md` verbatim and `STATUS.yaml.authorizations` is non-empty. Until then the correct
stage is `PACKET_DRAFT` and the correct next gate is `USER_AUTHORIZATION_PENDING`.
