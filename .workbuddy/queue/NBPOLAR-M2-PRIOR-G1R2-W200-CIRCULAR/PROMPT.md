# OPERATOR PROMPT — NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR (copy-paste, self-contained)

You are the operator executing a frozen delta-successor packet (G1R2 = G1 at w=200 + CIRCULAR).
Do NOT redesign. Do NOT guess. If the packet or the delta is ambiguous or they conflict, STOP and
report (second return condition). M2 is a CANDIDATE, never the baseline. G1 scope:
DESCRIPTIVE / NON-CLAIM and DECODER-FREE — you never call a decoder.

CRITICAL: **do NOT modify `scripts/m2_prior_validation.py`.** The re-parameterization required to
run this packet (delta item 8: window-keyed G1/G1R2 contracts, ledger-driven reserve emission,
G1R2 packet-dir/label routing) is **already applied and separately reviewed**; G1's literals and
code path remain reproducible. If the CLI still cannot express MOD=CIRCULAR or
`--window-primary 200` / `--window-sensitivity 500`, STOP and report rather than editing the runner
(TASK_PACKET R5).

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD`. Else STOP.
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (TimeTagger 2.22.6 + Swabian shim per
  `docs/troubleshooting.md` — read the import-namespace trap and the `.1`-segment trap first).
- Packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/TASK_PACKET.md` (authoritative).
- Delta: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1r2_delta.md` (the **8** CHANGED items;
  everything else inherited from `g1_freeze.md`). Item 8 (runner re-parameterization: window-keyed
  G1/G1R2 contracts, ledger-driven reserve, G1R2 packet-dir/labels) is **already applied and
  separately reviewed** — do NOT modify `scripts/m2_prior_validation.py` any further; if the CLI
  still cannot express this invocation, STOP and report.
- NEVER modify anything under `src/`, `experiments/`, `tools/`, `results/`,
  `comparison_bench/outputs_comparison/`, or `formal_ir/nbpolar/`. NEVER read SHG `_2`.
  NEVER call a decoder. NEVER write outside the two `workspace/m2_prior_validation/**` roots +
  this packet's STATUS.yaml (counters/artifacts/ids only) + `g1r2_freeze_config.json`.

## 1. Phase A — freeze closure (SHG `_1`, decoder-free; no prior fitting, no NLL)

```
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --freeze-config .workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/g1r2_freeze_config.json --stage-g1-nll --acq-id 20260113_SHG_Type2PPLN_3s --window-primary 200 --window-sensitivity 500 --skip 702 --mod CIRCULAR --char-pairs 200192 --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2 --authorized --closure-only
```
Reproduction gate (all EXACT vs the census (N)-200 cell + S11 `wgrid_offset50.200`):
n_pairs 1,259,992; pre-skip n_frames 4,921; accidental 0.0058; linear {0: 950276, +1: 306566,
−1: 2849, tail: 301 (= −1023:293 + +1023:8)}; circular {0: 950276, +1: 306859, −1: 2857, tail: 0};
alignment peak 50 / σ 112.45189572400645 / status ok. Mismatch ⇒ STOP loudly (ALIGN_INCONSISTENT).
Then skip-702; enumerate the post-skip ledger (expect **4,219**; verify ≥ 4,190); apply the inherited
layout (A1-CAL 0–1023 | CAL32 1024–1055 | CHAR 1056–1837 | HELDOUT 1838–2397 | EVAL 2398–4189 |
RESERVE 4190–4218); emit `cal_frame_ids` (32), `heldout_frame_ids` (560), `a1_cal_ids` (1024),
`disjointness_matrix`, and the complete 19-key `g1r2_freeze_config.json`. Budget ≤ 300 s / 2 GiB.
Do NOT run Phase B.

## 2. Verify + return (exactly two conditions)

1. Phase A complete: `G1R2-A` PASS with reproduction evidence 5/5 exact (incl. the circular tail = 0
   and the wrap split 293/8), ledger 4,219 ≥ 4,190, the five segment lists, the disjointness matrix,
   the filled 19-key config; plus evidence paths + run log + scoped `git status`; Phase B explicitly
   not run.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE
   decision needed. "Still incomplete" is not a report.

(Phase B is dispatched later in the same session after the main thread records the closure
verification: G1R2-1..G1R2-4 + G1R2-R remainder check, budgets ≤ 600 s / 2 GiB per invocation.)

Stop rules: any FORBIDDEN touch (SHG `_2`, decoder, runner edit, out-of-scope write) ⇒ STOP + blocker.
Reproduction mismatch ⇒ STOP loudly. Budget exceeded ⇒ STOP (no tuning). Ambiguity ⇒ STOP.
Do NOT update decision-log / memory / index / parent packet STATUS.
