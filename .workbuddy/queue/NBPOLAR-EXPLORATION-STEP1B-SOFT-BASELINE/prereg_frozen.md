# PREG (FROZEN) — NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE

> Copied verbatim into the output root BEFORE any computation. Everything is frozen here.

- **Probe:** NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE — Tier-X, synthetic only, non-claim.
- **Question:** on the frozen Step-1 envelope (F4 ±1-dominated asymmetric channel;
  q∈{4,8,16}; n_sym=128; R∈{0.30,0.40,0.50,0.60}; identical seeds/blocks/pairing), does
  the native q-ary SC separation SURVIVE when arm B is upgraded from HARD MSD conditioning
  to EXACT SOFT-CARRYING MSD conditioning?
- **Arms (all four paired on the same message+noise per (seed,block)):**
  - A = native q-ary polar SC (Step-1 arm A unchanged; formal_ir read-only reuse;
    GF(4)=0b111/GF(8)=0b1011/GF(16)=0b10011; alpha=2).
  - B-hard = faithful re-implementation of Step-1 arm B (Gray bit-plane MLC-polar, MSD
    hard conditioning on earlier decoded planes, plane order 0..r−1, joint
    top-(r·K_sym) design, design seed 2026092400).
  - B-soft = same decomposition/design as B-hard with EXACT soft-carrying MSD decoding:
    plane 0 marginal induced binary channel; plane i>0 per-position binary log-prior
    `log S_b − log(S_0 + S_1)` with
    `S_b = Σ_{a_<i,a_>i} P_F4(y − symbol(b@i, a_<i, a_>i)) · Π_{j<i} belief_j(a_j) · 2^{-(r-1-i)}`
    (belief_j = plane j SC posteriors, soft; later planes marginalized uniformly).
  - B-lab (amendment 1) = the production binary pipeline from
    `/mnt/d/Code/qkd-reconciliation-lab` — read-only import of `qkd_recon.polar_core`
    (3GPP PW order, beta=2^0.25, per-plane frozen-mask SC) +
    `qkd_recon.msd_conditional.build_msd_llr_tables_shift` on the exact F4 difference pmf
    (smoothing 0.0, clip 30.0) with `conditional_llr` hard-prefix conditioning; uniform
    per-plane k_i = K_sym; lab git HEAD recorded as provenance.
- **Channel/seeds (F4):** P(δ=0)=0.75, P(δ=+1)=0.24, P(δ=−1)=0.005, 0.005 uniform over
  the other q−3 offsets; seeds 2026092401..2026092416 (16) × 64 blocks = 1024 per cell.
- **Metric:** FER over 1024 blocks per (q,R,arm); per-seed series + mean/sample-std/range;
  paired ΔFER = Bsoft−A (primary) and Bsoft−Bhard (secondary); H_δ
  0.8818511717297366 / 0.8934608122041734 / 0.900353370320442; f = r·K_sym/(n_sym·H_δ).
  NO numeric threshold; qualitative reading; negatives kept as evidence.
- **Gates (binding; failure ⇒ STOP, zero outputs):** G0 reproduction — B-hard cell means
  must equal the Step-1 recorded `armB_fer.mean` bit-exactly on all 12 cells (fidelity +
  same-caliber proof); G1/G1b oracle ≥200 tiny instances per q per arm vs brute-force MAP,
  0 hard mismatches (ties ≤1e-9, first-divergence cascade documented); G2 noiseless 20/20
  per q per arm; G3 smoke FER(R=0.30) < 0.5 both compared arms; G4 determinism excerpt
  identical.
- **Exact command:**
  `PYTHONPATH=comparison_bench/src <interpreter> .workbuddy/queue/NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE/s1b_screen.py --probe-root workspace/exploration/nbpolar-native-highdim/step1b-soft-baseline/`
  (interpreter per ordered policy; recorded).
- **Write root:** `workspace/exploration/nbpolar-native-highdim/step1b-soft-baseline/` —
  exactly `prereg.md`, `results.json`, `notes.md`. Nothing else, anywhere.
- **Budget:** wall ≤ 5400 s, RSS ≤ 4 GiB, single-threaded, one run (`s1b_runs: 1`,
  `reruns: 0`; one corrective rebuild only after a zero-output crash, recorded).
- **Stop rules (packet §Stop rules, binding):** any gate failure incl. G0; interpreter/
  import failure; out-of-scope write; any `comparison_bench/` modification; any
  real-data/EVAL/RESERVE contact; budget exceeded; any claim object; any post-hoc tuning.
- **Non-claim:** synthetic FER values are L2-ledger screening readouts, never cited as L1
  real-data FER; no efficiency/promotion/qualification/composable-key statement.
