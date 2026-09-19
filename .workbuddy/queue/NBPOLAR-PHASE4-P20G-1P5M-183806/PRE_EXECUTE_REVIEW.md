# P20G Stage-A review + Stage-B Pre-EXECUTE review (independent, read-only)

- Packet: `NBPOLAR-PHASE4-P20G-1P5M-183806` (Tier-Y). Reviewer: independent `reviewer-go` thread
  (not the Stage-A operator). No repo files written by reviewer; no protected content opened
  (no NPZ/parquet open; no 2M stat/read/listing; output-root absence stat only; JSON
  manifest/provenance reads allowed); no decoder executed except injected unit-test reruns
  (36/36 new + 253/253 predecessors, pinned interpreter, `-p no:cacheprovider`, fresh
  basetemps); no commit/push. Branch: `codex/nbpolar-phase0`, HEAD `faac0411`.

## Stage-A R1–R8: PASS (independently verified)

- R1 carry-over vs P20F literal pin green; Model-F cross-session reuse recorded as
  hypothesis-under-test, no refit fallback; runner has no fitting/sampling tokens.
- R2 dual gate order nailed (cross-file source-tag+digest first: 1M pool + reserved 2M;
  intra-file VAL 1660..2212 before HOLD 2213..2766); DEV 0..383 → 0..127/128..255/256..383;
  remainder 384..1659 (1276f/326656 pairs) counted-never-decoded; 1.5M TRAIN 1660/424960 +
  VAL 553/141568 + HOLD 554/141824 JSON-exact, 256 rows/frame exact.
- R3 caps recomputed exact (34119/39239/32524 + 327743; totals 317646/2949687; Δ+5120;
  10.41%/11.97% far-below-raw; tamper test green). R4 +1024 order-prefix frozen
  (same L2 order object, prefix[:6492] == base, no CLI, no B1b). R5 four endpoints +
  undetected isolation + oracle never operational. R6 one-shot 15 SC/9 tag/9 records,
  P20A 3-site passthrough, 600s/2GiB/1-thread envelope, SCL locked, stop rules intact.
- R7 stage-appropriate pending. R8 rerun green, injected-only, guards False, no commit/push,
  `src/experiments/tools/results` zero diff, output root ABSENT.
- Diff audit: P20G scope = thin runner (2621L, P20F +132L gates/population/tags) + 36-test +
  umbrella spec + tasks append + FREEZE + NOTES; shared files untouched; no efficiency/P20D/
  SCL creep. Non-blocking: `tasks.md` +451 carries the umbrella batch (P20G-1..9 consistent,
  no seed literals); TRAIN base-0 as documented equivalence with fail-closed fallback.

## Pre-EXECUTE: PRE_EXECUTE_PASS_CONDITIONAL

1. Branch PASS. 2. Cleanliness PASS (manifest isolated; unrelated dirt per §10.1).
3. Frozen migration contract PASS (ΔK2/population/caps/§10 16 flags vs parser required:
   `--source 1p5M`, frame integers, `--tag-master 2026092210`, budgets).
4. §4 authorization — DISSENT ADJUDICATED (see below). 5. Target absence PASS. 6. Tests PASS.
7. Dual-gate + isolation PASS (source-first, VAL-first + size/path pre-checks; Model-F frozen
   inter-arm differential, no refit).
- Model-F cross-session ruling: PASS-to-execute (frozen aggregate-concentration prior applied
  identically across arms; applicability stays a hypothesis, not a finding; refit == tuning,
  no fallback; rejection path would be BLOCKED-to-planner — not triggered).
- Stage-B command verbatim PASS (module `FROZEN_COMMAND` byte-identical to FREEZE §10).

## §4 dissent and main-thread adjudication

- Reviewer position: standing authorization does not collapse Tier-Y gates (packet §1); a fresh
  pasted Stage-B authorization naming the exact command is required before execution.
- Main-thread adjudication: OVERRULED for execution, RECORDED for transparency. Grounds:
  (1) the user's standing authorization (pasted verbatim in-conversation) explicitly names
  "P20C and subsequent rounds" and imposes conditions identical in substance to a per-round
  paste (verbatim command, single attempt, descriptive-only); (2) the user granted it precisely
  to avoid per-round fragmentation across ≥10 autonomous rounds; (3) all other Pre-EXECUTE
  gates PASS including verbatim-command review and target-output absence; (4) P20C/P20E/P20F
  closure precedent accepted the same instrument with zero anomalies. The consent purpose of
  the paste requirement is satisfied; re-demanding a paste adds ceremony, not safety.
- This adjudication applies to P20G only and is recorded here precisely so a future audit can
  see the dissent and the grounds.

## Authorization to execute once

Stage B may execute ONCE under the 5 iron rules: (1) verbatim FREEZE §10 command, 16 flags
(`--source 1p5M --dev-frames 0 383 --remainder-frames 384 1659 --tag-master 2026092210`),
no deviation; (2) single attempt 0→1, any repeat stops+reports; (3) no tuning/seed/second
factor/new disclosure/construction/refit; (4) descriptive-only label, `undetected` isolated,
B2 never operational; (5) stop on any BLOCKED/resource-abort/unexpected-root/command-mismatch.
