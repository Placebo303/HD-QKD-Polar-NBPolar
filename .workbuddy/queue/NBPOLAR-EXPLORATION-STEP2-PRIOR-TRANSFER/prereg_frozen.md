# PREG (FROZEN) — NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER

> Copied verbatim into the output root BEFORE any computation. Everything is frozen here.

- **Probe:** NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER — Tier-X, synthetic only, non-claim.
- **Question:** does initializing the Step-1 native q-ary SC decoder with the frozen real-data
  transition structure (the M2 ±1 finding) as non-uniform initial messages beat a uniform
  init at matched everything-else — with a negative recorded as a result, not discarded?
- **Arms (amendment 3, 2026-09-23):** I = informed init, the frozen G1R2 CAL32 triple
  verbatim (q0 0.7562, q+1 0.2419, q−1 0.0018, remaining q−3 offsets 0) with the frozen
  floor 1e-15 applied and NOT renormalized (`log P_I(y|x') = log(max(p_{δ=(y−x') mod q},
  1e-15))`); U = **no-injection baseline** (replaces the degenerate uniform arm):
  `log P_U(y|x') = log P_F4(y|x')` — the true synthetic channel belief. Both arms share
  the code construction, seeds, messages and noise matrices (paired); ONLY the
  initial-message priors differ. Scientific question (preserved, meaningful form): does
  injecting the real-data transition structure (M2 ±1, with its frozen floor rule) beat
  the standard no-injection baseline on the same frozen envelope? Zero/negative gain is
  kept as evidence (design §5).
- **Decoder/envelope (F1/F2, reused from Step 1):** native q-ary polar SC
  (`formal_ir.nbpolar` read-only reuse; GF(4)=0b111, GF(8)=0b1011, GF(16)=0b10011; alpha=2);
  channel F4 (P(δ=0)=0.75, P(δ=+1)=0.24, P(δ=−1)=0.005, 0.005 uniform over the other q−3
  offsets); n_sym=128; R ∈ {0.30,0.40,0.50,0.60}; K_sym={38,51,64,77}; design seed
  2026092400 (deterministic re-design; G0 cross-check vs Step-1 results.json if readable).
- **Seeds (F5):** 2026092401..2026092416 (16) × 64 blocks = 1024 paired trials per (q,R).
- **Metric (F6):** per (q, seed): `g_succ(s) = (Σ ok_I − Σ ok_U)/T_s`,
  `g_nll(s) = Σ(nll_U − nll_I)/T_s`, T_s = 64; `nll_arm(t) = −Σ_{i∈info} log2 P_arm(x_i =
  true_i|y)`; per-seed series + mean/sample-std/range per q. **No numeric threshold**;
  zero/negative gain kept as evidence (design §5).
- **Boundary guard (F7):** no EVAL/RESERVE; no re-fit; no `prior_m2.py` change; no CAL
  change; no decoder change; M2 values copied from the frozen record only.
- **Correctness gates (binding; failure ⇒ STOP, zero outputs):** G0 information-set equality
  (or recorded unavailability); G1a oracle agreement with the informed prior (≥200 tiny
  instances per q, decoded == brute-force MAP, 0 mismatches); G1b (amendment 3, renamed)
  oracle agreement with the TRUE-CHANNEL belief (same pattern); G2 noiseless round-trip
  20/20 per q; G3 smoke FER(R=0.30) < 0.9 both arms. Degeneracy note: the blind-uniform
  arm (log(1/q) messages) is degenerate by construction (FER = 1.0 at probability
  1 − q^-K) — recorded packet history, no discriminative information.
- **Exact command:**
  `PYTHONPATH=comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python .workbuddy/queue/NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER/s2_transfer.py --probe-root workspace/exploration/nbpolar-native-highdim/step2/`
- **Write root:** `workspace/exploration/nbpolar-native-highdim/step2/` — exactly
  `prereg.md`, `results.json`, `notes.md`. Nothing else, anywhere.
- **Budget:** wall ≤ 3600 s, RSS ≤ 4 GiB, single-threaded, one run (`s2_runs: 1`,
  `reruns: 0`; one corrective rebuild only after a zero-output crash, recorded).
- **Stop rules (packet §Stop rules, binding):** any gate failure; interpreter/import
  failure; out-of-scope write; any `comparison_bench/` modification; any
  real-data/EVAL/RESERVE contact; any prior-code/CAL change; budget exceeded; any claim
  object; any post-hoc tuning.
- **Non-claim:** synthetic paired readouts are L2-ledger screening values, never cited as
  L1 real-data FER; no efficiency/promotion/qualification/composable-key statement.
