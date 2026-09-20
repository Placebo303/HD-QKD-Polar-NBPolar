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
Stop rules per TASK_PACKET.md §§4–5: adverse A5 ⇒ STOP before Stage B; Stage A0 stop rules per TASK_PACKET.md section 4: any adverse
A0-ID stops before Stage A;
B6/B7 violation ⇒ STOP entire run.

 Budgets: descriptive read-only census of 333.1 MiB local raw data; no network except the single item-B pip install (only if item B separately authorized),
 no other installs (if `TimeTagger` is missing without item-B authorization: STOP and report, do not pip-install).
Reporting: per-ID (A0-1-A0-5, A1–A5, B1–B9) PASS/FAIL with evidence paths + run log at
`workspace/census_20260921/run_log.md`. No decision-log / memory / index updates
(batch at milestone).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <UTC date> — implementation_authorized: true (prepare) / execution_authorized: true (Stages A+B per stop rules)
