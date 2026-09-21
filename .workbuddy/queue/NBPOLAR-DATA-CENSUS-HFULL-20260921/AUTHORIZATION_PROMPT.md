# AUTHORIZATION — NBPOLAR-DATA-CENSUS-HFULL-20260921
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE execution of packet NBPOLAR-DATA-CENSUS-HFULL-20260921
(zero-decoder H_full census, 10 NEW raw acquisitions) on branch
`codex/nbpolar-phase0` in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-DATA-CENSUS-HFULL-20260921/TASK_PACKET.md`,
using ONLY sibling venv `/home/karel_303/.venvs/timetagger/bin/python`
and intake script `scripts/census_intake_20260921.py`.

Scope authorized:
Frozen parameters (exact authorization surface — authorizer reads this as WHAT is authorized, no tuning permitted):
- Pipeline: `d=1024`, `bin_width_ps=200`, `period_ps=204800`, `pairing=nearest`, `rule=legacy_v1`, `frame_pairs=256`, `gate_ps=200`, `threshold_ps=40000`; channels FIXED logical A=hw1 / B=hw5 (not searched; other/total ≤ 0.20 guard).
- Delay (R1 rewrite 2026-09-21, SUPERSEDES the old `|delay−peak|<50ps` / `sigma∈[50,150]` gate): ONE `_estimate_peak_stats_from_timetags` invocation per acquisition, frozen scan `scan_range_ps=409600`, `bin_ps=100`; accept `status==ok` AND `peak_to_bg>=10`; FAIL ⇒ `ALIGN_FAIL`, exclude acquisition, continue — no tuning, no second scan. Yield self-check: derived offset at/within one coarse step of yield maximum (strict-exact plateau miss = PASS-with-note); beyond one step ⇒ `ALIGN_INCONSISTENT`, stop loudly. Frozen −50/+50/+50 NOT inherited. Dual-rule: (W) wide legacy_v1 + (N) nearest-unique grid {200,500,1000,2000,4000,40000}; σ vs [50,150] reported, gate never relaxed.
- Skip (R2): default 702 frames ALL acquisitions, labelled `INHERITED_NOT_DERIVED` (known weakness; census descriptive/non-claim) + mandatory non-decision first-~1500-frame coincidence diagnostic per acquisition.
- Tiers (R3, B0 after pairing before any H): FULL ≥ 1982 full frames (skip 702, CAL 1024, VAL 256); REDUCED 1342–1981 (skip 702, CAL 512, VAL 128, `REDUCED_SIZING`, not directly comparable); INSUFFICIENT < 1342 (`INSUFFICIENT_LENGTH`, no H). No reuse/padding/partial frames.
- Estimators: PRIMARY factorized H1+H2 raw-MLE+1e-15 floor; SECONDARY flat H_full separate field. Merge rule: PRIMARY-ONLY read, concatenation forbidden. Zero decoders.
A. Census execution:
1. Stage A0 env CHECKS (read-only: A0-1 `ldd`, A0-2 numpy version,
   A0-4/A0-5 `--stage-a0-env-check` — but NOT the A0-3 install):
   `/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py --stage-a0-env-check --out-root workspace/census_20260921`
2. Stage A parse test FIRST on `20260112_Type2PPLN_3s` ONLY (requires A0
   `stage_a0_go: true`):
   `/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py --stage-a-parse-test --acq-id 20260112_Type2PPLN_3s --out-root workspace/census_20260921`
3. Stage B census over all 10 acquisitions ONLY if Stage A records
   `stage_b_go: true` WITH the corrected
   `autofollow-confirmed-read-primary-only-concat-forbidden` verdict
   (the frozen `union-is-concat-use-both-files` verdict is superseded;
   merge rule is PRIMARY-ONLY — never concatenate):
   `/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py --stage-b-census --authorized --out-root workspace/census_20260921`

---
B. Environment install (SEPARATE authorization — authorize independently of A;
   this modifies an environment OUTSIDE the repo, not repo files):
I AUTHORIZE the single install command
`/home/karel_303/.venvs/timetagger/bin/python -m pip install Swabian-TimeTagger`
into the sibling venv ONLY (expected: Swabian-TimeTagger 2.22.6,
manylinux_2_28_x86_64 wheel, ~32.7 MB; needs glibc >= 2.28, numpy >= 1.23.0).
Fallback pins (`Swabian-TimeTagger==2.20.2` / `==2.21.2`) are covered by this
same item if the bare `TimeTagger` name is missing after install. No other
installs, no upgrades of other packages, no Windows-side install.

INSTALL AUTHORIZED BY: <name> — <UTC date> — timetagger_install_authorized: true/false

Constraints (binding): zero decoders; no execution of
`experiments/run_e2e_pipeline.py`, `tools/longrun_*`/`minrerun_*`/`routeA_*`;
writes ONLY under additive root `workspace/census_20260921/` (per-acq `<acq_id>/` dirs;
 plus the single Stage-A0 verdict file `stage_a0_env.json` directly under the root);
no writes to `results/` or `comparison_bench/outputs_comparison/`;
no modifications to `src/`, `experiments/`, `tools/`;
no branch switch; no commit/push.
Stop rules per TASK_PACKET.md §§6–6.0: adverse A5 ⇒ STOP before Stage B; Stage A0 stop rules per TASK_PACKET.md section 4: any adverse
A0-ID stops before Stage A;
B1 `ALIGN_FAIL` / B2 FAIL / B0-1 `INSUFFICIENT_LENGTH` ⇒ per-acquisition exclude-and-continue (report both exclusion counts);
B6/B7 violation ⇒ STOP entire run.

 Budgets: descriptive read-only census of 333.1 MiB local raw data; no network except the single item-B pip install (only if item B separately authorized),
 no other installs (if `TimeTagger` is missing without item-B authorization: STOP and report, do not pip-install).
Reporting: per-ID (A0-1-A0-5, A1–A5, B0-1, B1–B9) PASS/FAIL with evidence paths + run log at
`workspace/census_20260921/run_log.md`. No decision-log / memory / index updates
(batch at milestone).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <UTC date> — implementation_authorized: true (prepare) / execution_authorized: true (Stages A+B per stop rules)
