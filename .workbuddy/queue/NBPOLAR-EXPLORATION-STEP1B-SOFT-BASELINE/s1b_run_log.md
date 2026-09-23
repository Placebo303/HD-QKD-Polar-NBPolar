# S1B Run Log — NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE

First dispatch return condition: **2 (BLOCKER)** — official one-shot deliberately
NOT consumed (see below); resolved by AMENDMENT 2.
Re-dispatch return condition: **1 (ALL-COMPLETE)** — see "Re-dispatch
execution" section at the end.

## Timeline

- P0 freeze verification: `prereg.md` byte-identical to
  `prereg_frozen.md` (sha256
  `3dabe75c05aa93e9a2e8b0149f9dfeebcd2ab0bc846e435cf3b476b05232a225`).
  Write-scope snapshots captured:
  `/tmp/opencode/s1b_{lab_src,lab_status,repo_status}_before.txt`.
  Lab HEAD `f9d3c25a0ce95009bdb3a2fa03bab9e067d22f09`. Step-1 G0 targets
  captured from `workspace/exploration/nbpolar-native-highdim/step1/results.json`.
- P1: `s1b_screen.py` written (four-arm builder, gates G0–G4,
  single end-of-run write). Fixes during development (pre-acceptance,
  semantics-preserving): removed dead `lab_masks` placeholder; `soft_priors`
  elementwise `np.isfinite` guard (`np.where(ok, l0-lt, 0.0)` — same mask for
  both planes); `naive_M_soft` called with `EJBs[i]`/`EJBs[1]`/`EJBs[0]` (no
  list-vs-ndarray misuse). Import smoke test: PASS.
- Dev pre-flight (scratch `/tmp/opencode/s1b_dev_preflight.py`, NOT the official
  command, no probe-root writes), log `/tmp/opencode/s1b_preflight.log`,
  wall 107.9 s:

  | Gate | Result |
  |---|---|
  | H_delta frozen | PASS (0.8818511717297366 / 0.8934608122041734 / 0.900353370320442) |
  | Encoder equivalence (n=2,4,128) | PASS (benc == lab polar_encode) |
  | soft_priors vs naive log-odds | max\|diff\| = 1.78e-15 PASS |
  | plane0 naive vs plane_priors | max\|diff\| = 0 PASS |
  | G0 (12 cells, B-hard bit-exact Step-1) | PASS (`[]`) |
  | G1 arm A (q=4/8/16, n=200) | PASS hard=0 (q4: 197 strict / 3 tie) |
  | G1b B-soft (q=4/8/16, n=200) | PASS hard=0 (q8: 1 tie) |
  | **G1c B-lab (q=4/8/16, n=200)** | **FAIL hard=5/6/7 (ties=0)** |
  | G2 noiseless (4 arms × 3 q) | PASS 20/20 each |
  | G3 smoke R=0.30 (4 arms × 3 q) | PASS all < 0.5 |

- Diagnosis (`/tmp/opencode/s1b_g1c_diag.py`, log
  `/tmp/opencode/s1b_g1c_diag.log`), 600 instances (200 per q, same salt-5
  draws as the gate): lab-min-sum SC vs exact brute = 5/6/7 (bit-for-bit
  reproduces gate counts); **exact boxplus SC vs exact brute = 0 mismatches
  at every q and n**. All mismatches occur at n=4 (frozen/first-polarized
  masks active); n=2 (no frozen positions) never diverges. Divergence
  magnitudes 0.24–27.9, i.e. ≫ the 1e-9 tie tolerance.

## Root cause

The lab decoder `sc_decode_frame` uses the **min-sum** f-node
(`_left_alpha`: `sign(l)·min(|l|,|r|)`), while the frozen G1c oracle is the
**exact boxplus** brute successive-MAP. On n=4 instances with active frozen
positions the two recursions select different hard decisions with large
margins. This is an inherent property of the lab decoder, not a
implementation bug in the probe: replacing the lab decoder by an exact
boxplus SC in the identical setup removes ALL mismatches (0/600).

## Consequence

G1c as frozen ("lab min-sum hard decisions == exact brute successive-MAP,
0 hard mismatches") is structurally unachievable for any instance count ≥ 1
where frozen positions are active. Per packet STOP rule: official one-shot
NOT run, probe root contains only `prereg.md`, `results.json`/`notes.md`
not written, `s1b_runs` not consumed. Single decision required from main
thread (see operator return).

## Scope note

Two untracked Chinese-named markdown files appeared in the lab checkout at
16:15/16:18 (after P0 snapshot) — created by an external concurrent process;
this task's scripts contain no write path to the lab. No tracked lab file
was modified; `comparison_bench/` and repo status unchanged vs snapshot.

---

# Re-dispatch execution (AMENDMENT 2) — 2026-09-23

Return condition: **1 (ALL-COMPLETE per-ID report)** — official one-shot
consumed ONCE (`s1b_runs: 1`, `reruns: 0`, `rebuilds: 0`).

## P0 draft check (re-dispatch)

- Branch `codex/nbpolar-phase0` ✓; all 8 packet files present (6 base +
  both amendments + builder + this log).
- Interpreter F7 primary `/home/karel_303/.venvs/hd-qkd-polar-comparison/
  bin/python`: numpy 2.4.4, pandas 3.0.2, numba 0.65.1; `formal_ir`
  import chain OK; lab `qkd_recon.polar_core`/`msd_conditional` import
  chain OK.
- Output root held EXACTLY the stale `prereg.md` (no measurement had ever
  existed; any other file would have STOPped the run). Refreshed from the
  current `prereg_frozen.md` by explicit copy: byte-identical before AND
  after, sha256
  `3dabe75c05aa93e9a2e8b0149f9dfeebcd2ab0bc846e435cf3b476b05232a225`.
- Write-scope snapshots re-captured:
  `/tmp/opencode/s1b2_{lab_status,repo_status,cb_status}_{before,after}.txt`.
  Lab HEAD `f9d3c25a0ce95009bdb3a2fa03bab9e067d22f09`.
- Authorization: `STATUS.yaml.authorizations` non-empty (verbatim user
  instruction bound by the main thread) ✓.

## Builder amendment (Amendment 2, before any run)

- Replaced G1c's exact-MAP comparison with an INDEPENDENTLY coded
  packet-local min-sum mirror (`mirror_min_sum_sc`,
  `mirror_decode_planes`, `_first_divergence`): recursive natural-order
  SC, f-node `sign·min(|l|,|r|)` (lab sign convention x>=0 => +1),
  exact g-node `r + (1-2·benc(uleft))·l` (partial-sum feedback through
  the packet-local butterfly), leaf 1 iff LLR<0, frozen pinned 0, lab
  clip 30.0 re-applied (idempotent on table lookups). NOT a copy of the
  lab's iterative `sc_decode_frame`. Same `conditional_llr` priors, same
  frozen masks, same natural-plane prefix chain (mirror carries its OWN
  chain).
- The exact-MAP comparison moved to the NON-gating diagnostic
  `results.json gates.G1c_approx_gap` (+ `notes.md` section), measured
  on the SAME salt-5 instances (100 F4-family + 100 random uniform per
  q; n∈{2,4}).
- Freeze echo F6 updated + `AMENDMENT_2` key added in `results.json`.

## Dev gate test (scratch, NOT the official command, zero output-root writes)

Log `/tmp/opencode/s1b_dev_g1c2.log`:
- First attempt found a REAL mirror bug (dev only, official not run):
  the g-node initially conditioned on the RAW left-half decisions
  instead of the partial-sum feedback — lab-vs-mirror 16 hard + 1 tie
  mismatches at q=4. Diagnosed with
  `/tmp/opencode/s1b_debug_mirror.py` (first divergent instance:
  q=4 F4 n=4 plane0 all-info, llr [-a,+a,+a,-a]; a literal
  pure-Python transcription of the lab's iterative schedule matched the
  lab exactly, isolating the mirror as wrong).
- Fix: condition the g-node on `benc(uleft)` (what the lab's
  `_merge_beta` tree reconstructs). Re-test: mirror 200/200 strict,
  0 hard, 0 ties at q=4/8/16; approx-gap 5/6/7 (n=4 only) — matching
  the Amendment-2 diagnostic. No tuning of any threshold occurred.

## Official one-shot (frozen command, ONE invocation)

`PYTHONPATH=comparison_bench/src
/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python
.workbuddy/queue/NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE/s1b_screen.py
--probe-root workspace/exploration/nbpolar-native-highdim/step1b-soft-baseline/`
— exit 0, wall 271.0 s (shell 272 s) <= 7200 s budget; log
`/tmp/opencode/s1b_official_run.log`.

| Gate | Result |
|---|---|
| G0 (B-hard vs Step-1, 12 cells) | PASS — all 12 `equal: True`, bit-exact float means |
| G1 arm A q=4/8/16 (n=200) | PASS hard=0 (ties: q4 3) |
| G1b B-soft q=4/8/16 (n=200) | PASS hard=0 (q8 1 tie) |
| **G1c mirror q=4/8/16 (n=200)** | **PASS hard=0 ties=0, strict 200/200 each q** |
| G1c_approx_gap (non-gating) | q4=5, q8=6, q16=7 hard per 200, all n=4, ties=0, gaps 0.0022–0.5772 (>1e-9); n=2 never diverges |
| G2 noiseless | PASS 20/20 × 4 arms × 3 q |
| G3 smoke R=0.30 | PASS max FER 0.0195 < 0.5 (all four arms); full-screen recheck ok |
| G4 determinism (q4_R0.40, seed 2026092401) | PASS runs_identical=True AND matches screening series[0] (A=5, Bh=20, Bs=19, Bl=12 fails / 64) |

- Outputs written (single end-of-run write): `results.json` (60597 B),
  `notes.md` (13086 B); root holds EXACTLY prereg.md + these two.
- Post-run verification: series lengths 16 for all 7 series × 12 cells;
  mean/sample-std/range recompute EXACTLY (builder formula, 0 diff);
  paired Δ series elementwise-exact vs arm series; H_δ recomputed equal
  to the three frozen values; f = r·K/(n_sym·H_δ) exact on all 12;
  counters 1/0/0; stop_rules_fired []; attestation present.
- Write scope: lab repo status and `comparison_bench` status byte-equal
  to before-snapshots; whole-repo status delta EMPTY (output root is
  gitignored-by-design); no `.pyc` written anywhere in repo trees after
  the run (hygiene env + NUMBA_CACHE_DIR redirect).
- A stray `__pycache__` created by the operator's `py_compile` check in
  the packet dir was removed immediately (out-of-scope write, lasted
  < 1 min, zero bytecode remains; subsequent checks used in-memory
  `compile()`).
- RSS: not instrumented post-hoc; the workload's largest arrays are the
  q×q×r MSD tables and n_sym=128 frame buffers (KB–MB scale), far below
  the 4 GiB cap; single-thread env pins verified in-script.
- Pre-flight accounting (Amendment 2): the consumed pre-flight dev run
  remains `s1b_runs: 0` with zero official outputs; this re-dispatch ran
  the official one-shot fresh → counters `1/0/0`.
