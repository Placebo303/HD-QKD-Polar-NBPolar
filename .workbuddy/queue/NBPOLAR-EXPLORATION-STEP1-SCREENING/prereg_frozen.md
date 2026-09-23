# PREG (FROZEN) — NBPOLAR-EXPLORATION-STEP1-SCREENING

> Copied verbatim into the output root BEFORE any computation. Everything is frozen here.

- **Probe:** NBPOLAR-EXPLORATION-STEP1-SCREENING — Tier-X (AGENTS.md §10.4), synthetic only,
  non-claim.
- **Question:** does native-symbol decoding (arm A) separate from bit-plane binary
  decomposition with ordered MSD conditioning (arm B) on FER–f at matched
  rate/block-length/prior over the locked ladder q ∈ {4, 8, 16}?
- **Arms:** A = q-ary polar SC via read-only reuse of `comparison_bench.formal_ir.nbpolar`
  (`algebra.make_gf2m`, `transform.polar_transform` alpha=2, `sc.sc_decode`); B = r-level
  Gray bit-plane MLC-polar (packet-local binary polar SC, MSD hard conditioning on earlier
  decoded planes, plane order 0..r−1).
- **Fields/mapping:** GF(4) 0b111, GF(8) 0b1011, GF(16) 0b10011; alpha=2; reflected Gray
  mapping shared by both arms.
- **Channel (F4):** P(δ=0)=0.75, P(δ=+1)=0.24, P(δ=−1)=0.005, 0.005 uniform over the
  other q−3 offsets. Symmetric control not in this probe (recorded).
- **Operating points (F5):** n_sym = 128; R ∈ {0.30, 0.40, 0.50, 0.60}; K_sym =
  {38, 51, 64, 77}; design seed 2026092400 (fixed); design metric = q-ary split-channel
  recursion + Monte-Carlo H(u|y), top-K information set (arm B: same per plane on the
  induced binary channel, marginal-averaged).
- **Seeds/blocks (F6):** screening seeds 2026092401..2026092416 (16); 64 blocks/seed ⇒
  1024 blocks per (q, R, arm); shared message and shared noise matrix per (seed, block)
  across arms (paired); numpy `default_rng`.
- **Metric (F8):** FER = block-error fraction (any message symbol wrong) over 1024 blocks;
  f = r·K_sym/(n_sym·H_δ), H_δ = entropy of the F4 δ distribution (log2); per-seed series
  + mean/sample-std/range per (q,R,arm); paired ΔFER = FER_B − FER_A. **No numeric
  threshold** — qualitative bar only (no separation across q ⇒ do not scale + record
  negative; clear separation ⇒ Step 2/3 designs may be frozen next).
- **Correctness gates (all binding; failure ⇒ STOP, zero outputs):** G1 oracle agreement
  (≥200 tiny instances per arm per q, decoded == brute-force MAP, 0 mismatches); G2
  noiseless round-trip 20/20 per q per arm; G3 low-rate smoke FER(R=0.30) < 0.5 both arms.
- **Exact command (amendment 2, 2026-09-23):**
  `PYTHONPATH=comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python .workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/s1_screen.py --probe-root workspace/exploration/nbpolar-native-highdim/step1/`
  (interpreter re-frozen by amendment 2: existing pandas-capable venv, frozen import
  chain verified, primitives match F3 exactly; timetagger venv demoted — no pandas, cannot
  import the formal_ir package chain; `.venv` absent; nothing installed).
- **Write root:** `workspace/exploration/nbpolar-native-highdim/step1/` — exactly
  `prereg.md`, `results.json`, `notes.md`. Nothing else, anywhere.
- **Budget:** wall ≤ 5400 s, RSS ≤ 4 GiB, single-threaded, one run (`s1_runs: 1`,
  `reruns: 0`; one corrective rebuild only after a zero-output crash, recorded).
- **Stop rules (packet §Stop rules, binding):** gate failure; interpreter/import failure;
  out-of-scope write; any `comparison_bench/` modification; any real-data/EVAL/RESERVE
  contact; budget exceeded; any sim-FER-as-real-FER framing; any post-hoc tuning.
- **Non-claim:** synthetic FER values are L2-ledger screening readouts, never cited as L1
  real-data FER; no efficiency/promotion/qualification/composable-key statement.
