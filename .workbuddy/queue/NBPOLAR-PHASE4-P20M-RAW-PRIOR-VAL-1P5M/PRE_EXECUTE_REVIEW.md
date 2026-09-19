# P20M Pre-EXECUTE review (independent; Stage A -> Stage B gate)

- Reviewer: `reviewer-go` (independent subagent), session `ses_f487e1984ffehLtiRnmG90vJXs`, 2026-09-19.
- Scope (packet §14 P20M-R7 + `AGENTS.md` §10.3): §3 corrected-prior derivation,
  §5 budget literal + split, §4 gate family/population, §2 runner-delta design,
  plus branch / scoped cleanliness / explicit user authorization / target-output
  absence / focused tests.
- Verdict: **PASS (PX1–PX7 all PASS)**. Stage B MAY be authorized, subject only
  to the pasted filled Stage-B authorization text and re-verified target-output
  absence. No rework required. (The reviewer marks nothing accepted.)

## Verdicts (abridged evidence)

| ID | Verdict | Key evidence |
|---|---|---|
| PX1 command+pins identity | PASS | `FROZEN_COMMAND` == `P20M_FREEZE.md` §5 Stage-B block, byte-identical (1171 chars); all pins present (`--k1 331 --k2 6689`, `--dev-frames 1660 2043`, `--remainder-frames 2044 2212`, `--tag-master 2026092280`, order digest `a9f18a9f…`, `--source 1p5M`, `--floor 1e-15`, `--n 32768`); prior digest is a module/freeze gate pin as designed. |
| PX2 §3 derivation | PASS | Own implementation from the P20H worktree npz: `f` vs stored `f_raw` max abs 0.0; H1 `0.02519949692375297` (Δ0), H2 `0.800366554749543` (Δ≤3.3e-16), TOTAL within 1e-12 of `0.8255660516732963`; new artifact exact 10-key set, `lambda_star 0.0`, `floor 1e-15`, shapes `(32,1024)/(32,1024,32)/(1024,)`, column-norm maxdev ≤ 1.13e-13, `p_b` maxdev 0.0, counts total 424960, floor hits 1046140/1048576, zero columns 0; canonical digest `372dcc1c…f7d46ac` == frozen. |
| PX3 §5 budget+split | PASS | `budget_k_total(32768, H, 1.3)` = 7020 (formula/clip verified); full independent replay (16 synthetic blocks, seeds 2026092291..94, 225.7 s, zero protected reads, no frozen-artifact writes) -> K1 331 / K2 6689 / residual `3.0162993815141537e-07` exact match; split path is the accepted `select_empirical_split`; order file sha `a9f18a9f…1da11bc638`, `k_total 7020/k1 331/k2 6689/n 32768`, full L1+L2 32768-permutations, provenance present. |
| PX4 §2 runner-delta | PASS | Only d1–d7 new code; `import ... as p20l` read-only; SC via accepted `run_operational_block`/`run_oracle_control_block` (greedy, no SCL); exactly 3 arms G0/G1/G2; no order reselection (`disclosure_order_from_stats` absent); no CLI K override; no λ smoothing; ambiguous/mixed mode refuses before read/write. |
| PX5 §4 gates+population | PASS | Order enforced before DEV open (line 2131) and before any SC; family (a)→(g) reused+new; S2-ii `build 0..1659` vs `DEV 1660..2043` disjoint; VAL-containment/HOLD + P20H/I/J/K + remainder exclusions; 1M fail-closed; 2M non-access; tag domain master 2026092280 / prefix unique by grep. |
| PX6 Pre-EXECUTE checklist | PASS | Branch `codex/nbpolar-phase0`; STEP-1 authorization recorded, `stage_b_authorized: false`; Stage-B root ABSENT; focused suite `19 passed in 29.69s` (`-p no:cacheprovider`, sibling venv); tests injected/fake in fresh `workspace/p20m/<uuid>` temp root; no `results/`/`outputs_comparison/` writes; no commit/push. |
| PX7 write scope | PASS | Stage-A window files only: new module, new test, `raw_prior_1p5m.npz`, `raw_prior_orders_1p5m.json`, `P20M_FREEZE.md`, `P20M_IMPLEMENTATION_NOTES.md`, `STATUS.yaml`; pre-existing dirt untouched; V25/1M/2M/DEV/HOLD non-access holds in code + declared audit. |

## Caveats (non-blocking)

- Module is 2669 lines vs the brief's "2655" (14-line pin-fill delta, expected).
- `openspec/.../specs/nbpolar-phase4-p20m/spec.md` and the `tasks.md` P20M section
  (mtime 09:24, planning-stage) are not itemized in `P20M_IMPLEMENTATION_NOTES.md` §1
  (allowed by §12; manifest-doc gap only).

No files were edited by this review; no commit/push; not a self-acceptance.
