# S1 run log — NBPOLAR-EXPLORATION-STEP1-SCREENING (Tier-X, synthetic only)

- Exact command (verbatim, amendment 2):
  `PYTHONPATH=comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python .workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/s1_screen.py --probe-root workspace/exploration/nbpolar-native-highdim/step1/`
- Branch: `codex/nbpolar-phase0` (never switched). No commit, no push.
- P0: PASS (branch, 5 packet files, primary interpreter + frozen import
  chain, output root absent).
- P1: output root created; `prereg_frozen.md` → `prereg.md`, `diff` clean
  before AND after the run (builder never touches prereg.md).
- Invocations of the probe command: exactly 1 (s1_runs=1, reruns=0,
  rebuilds=0). Exit code 0. Wall 169.4 s (budget 5400 s).
- Pre-run component exercising (import-only, zero probe-root writes, frozen
  screening/design streams untouched; same deterministic gate functions):
  caught and fixed 3 build defects before the frozen run —
  (1) packet-local binary-SC plus-branch P1 swap (branches were exchanged);
  (2) arm-B Bhattacharyya base missing the 1/2^(r-1) normalization (broke
  cross-plane comparability of the joint top-(r*K) selection);
  (3) MSD conditioning passed u-domain bits instead of re-encoded codeword
  bits (caused all-−inf induced priors + nan cascade; noiseless 18/128
  plane-1 errors before fix, 20/20 after).
  Also settled 1 gate-semantics reading: textbook-SC future-marginalization
  with first-divergence tie analysis (a frozen-conditioned enumerator
  disagreed with the frozen sc_decode on 44/200 tiny instances by
  definition, not defect; cascade-after-tie explained the residual).
  All readings recorded in output `notes.md`.
- Gate outcome (from results.json): G1 200/200 instances per (arm, q),
  hard mismatches 0 everywhere (strict: q4 A197/B199, q8 A200/B198,
  q16 A200/B200; remainder tie-tolerated ≤1e-9); G2 20/20 per (q, arm);
  G3 smoke FER(R=0.30) ≤ 0.0195 everywhere (bar < 0.5); full-screen R=0.30
  recheck passed before write.
- Output root holds exactly 3 files: prereg.md, results.json, notes.md.
  Packet dir holds s1_screen.py + this log only.
  comparison_bench/formal_ir untouched (read-only imports; `git status`
  shows no formal_ir modification). The one `comparison_bench/` dirty file
  (outputs_comparison test_fixture CSV) predates this task; all unrelated
  dirty/untracked worktree files preserved as found.
- Counters: s1_runs 1 / reruns 0 / rebuilds 0. Stop rules fired: none.
- Non-claim: synthetic L2 screening readout only; never cited as L1
  real-data FER. No efficiency/promotion/qualification/key-yield statement.
- Headline (per-seed mean; dFER = FER_B − FER_A; full series+stats in
  results.json):
  q=4: R0.30 A0.0000 B0.0107 d+0.0107 | R0.40 A0.0596 B0.2002 d+0.1406 |
       R0.50 A0.4189 B0.6719 d+0.2529 | R0.60 A0.9326 B0.9766 d+0.0439
  q=8: R0.30 A0.0000 B0.0000 d+0.0000 | R0.40 A0.0000 B0.0107 d+0.0107 |
       R0.50 A0.0039 B0.0908 d+0.0869 | R0.60 A0.1270 B0.5371 d+0.4102
  q=16: R0.30 A0.0000 B0.0000 d+0.0000 | R0.40 A0.0000 B0.0010 d+0.0010 |
       R0.50 A0.0000 B0.0117 d+0.0117 | R0.60 A0.0088 B0.1240 d+0.1152
  (H_delta bits: q4 0.881851, q8 0.893461, q16 0.900353.)
- Reading for main thread (no threshold fixed; qualitative bar only): the
  paired dFER series is same-sign (B worse) at every (q, R) cell except the
  two all-zero R0.30 cells — i.e. native-symbol SC separates from Gray
  bit-plane MSD with hard conditioning across the locked ladder under this
  frozen F4 instance. Promotion/Step-2 decisions belong to the main thread.
