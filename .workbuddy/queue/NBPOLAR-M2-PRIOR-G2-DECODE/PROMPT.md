# OPERATOR PROMPT — NBPOLAR-M2-PRIOR-G2-DECODE (copy-paste, self-contained)

You are the operator implementing and executing a frozen Tier-Y packet. Do NOT redesign. Do NOT guess.
If the packet or the freeze is ambiguous or they conflict, STOP and report (second return condition).
M2 is a CANDIDATE, never "baseline". This is a ONE-SHOT decision gate: after a verdict, no rerun, no tuning.

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD` shows `ref: refs/heads/codex/nbpolar-phase0`. Else STOP.
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (TimeTagger 2.22.6 + Swabian shim per `docs/troubleshooting.md`).
- Packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/TASK_PACKET.md` (authoritative; overrides this prompt).
- Freeze: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/g2_freeze.md` (all TO-FREEZE values + gates + layout).
- NEVER modify `sc.py`/`algebra.py`/`transform.py` or anything under `src/`, `experiments/`, `tools/`,
  `results/`, `comparison_bench/outputs_comparison/`, `formal_ir/nbpolar/`. NEVER read SHG `_2`.
  NEVER write outside `workspace/` + this packet dir + the runner file + the new test file.

## 1. Build / phases

- **Phase 0 (synthetic; no data):** implement the `--stage-g2-decode` body in `scripts/m2_prior_validation.py`
  per TASK_PACKET Spec 1 — preserve every Stage-1/G1R2 guard verbatim (`--authorized` store_true gate,
  19-key `--freeze-config` enforcement with null/absent ⇒ exit 2, flag↔key cross-checks, K pin 319/6492,
  out-root confinement, import purity). Reuse the frozen P16 construction + orders (digest pinned),
  N=32768, chunk_rows 512, floor 1e-15, 64-bit Toeplitz tag per block from tag_master; per-arm prior
  construction via `formal_ir/prior_m2.py` (M0 = `build_m0_joint`, M2 = `fit_m2_triple`→`build_m2_joint`,
  CIRCULAR) and the UNCHANGED frozen layer factorization (`derive_p1`/`derive_p2` →
  `build_p1_metrics`/`gather_p2_metrics` → `probs_to_symbol_metric(provenance=PRIOR_ONLY)`).
  Tests `comparison_bench/tests/test_nbpolar_m2_g2_decode.py` per Spec 2 — fake runner only; never invoke
  the production decode from tests; cover the Wilson gate with hand-computed cases.
- **Phase A (closure; decoder-free):** emit `g2_freeze_config.json` (every TO-FREEZE non-null) + the four
  closure keys at w=200 / CIRCULAR / skip-702 (A1-CAL 1024 frames = post-skip 0–1023; CAL32 = 1024–1055;
  HELDOUT = 1838–2397; disjointness) **by reusing the G1R2 closure literals verbatim** — there is **no**
  `--stage-g2-decode --closure-only` invocation (`--closure-only` applies to `--stage-g1-nll` only; blocking-fix B2).
  Out-root (canonical, blocking-fix B4): `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/`.
  Routing (blocking-fix B3): write ONLY to this packet dir + that out-root; never to G1/G1R2 packet dirs.
- **STOP after Phase 0 + A.** Wait for the independent Pre-EXECUTE PASS + the main thread's recorded
  authorization before any decode. Return Phase 0 + A results in the meantime.
- **Phase B (after authorization):** ONE-SHOT three-arm decode on the 14 EVAL blocks (post-skip
  2398–4189) at K1=319/K2=6492, tag_master 2026103001; record the full measurement set
  (`l1_exact`/`hard_l2_exact`/`oracle_l2_exact`/`pair_exact`; first-error coordinate AND layer; raw
  zero-count hits; floor hits + log loss; true-H and candidate-H L2 NLL; taxonomy with `undetected`
  isolated; disclosure recount; tag invocations; wall/RSS per block; SC/tag counts); apply the Wilson gate:
  SUCCESS iff Wilson-lower(B) > Wilson-upper(A2); FAIL iff point(B) ≤ point(A2); INCONCLUSIVE iff
  point(B) > point(A2) with overlap. A1 has no gate.

## 2. Verify (exact commands)

```
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
cat .git/HEAD  # expect: ref: refs/heads/codex/nbpolar-phase0
/home/karel_303/.venvs/timetagger/bin/python -m pytest comparison_bench/tests/test_nbpolar_m2_g2_decode.py -p no:cacheprovider -q
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --selfcheck
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --help
git status --porcelain -- scripts/ comparison_bench/ .workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/
git diff --stat -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/
```

## 3. Return (exactly two conditions)

1. All-complete: per-ID PASS (G2-0, G2-A; later G2-2..G2-4, R1) with evidence paths + pytest log +
   gate arithmetic + `git status` snippet. For Phase 0 + A: state explicitly that Phase B is NOT run.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision
   needed. "Still incomplete" is not a report.

## Stop rules

Budget ≤ 900 s wall / 2 GiB RSS single-threaded (exceeded ⇒ STOP, record as blocker, no tuning).
Any FORBIDDEN touch (SHG `_2`, decoder modification, out-of-scope write) ⇒ STOP + blocker.
δ-tail FAIL ⇒ no proceed. Verdict rendered ⇒ no rerun/tuning. Ambiguity ⇒ STOP, never guess.
No decision-log / memory / index updates in-packet.
