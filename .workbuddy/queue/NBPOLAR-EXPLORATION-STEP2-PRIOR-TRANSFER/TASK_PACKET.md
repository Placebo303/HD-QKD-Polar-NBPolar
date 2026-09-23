# TASK PACKET — NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER (Tier-X: uniform vs informed init)

**GATED PACKET.** Authorizes exactly ONE Tier-X transfer-prior probe and nothing else.
User authorization is recorded verbatim in `STATUS.yaml` (2026-09-23 full-suite
instruction); scope is bound by this packet. Synthetic only: no real data, no `.ttbin`,
no EVAL/RESERVE, no prior-code change, no frozen-constant change, no claim.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; Branch (verify `.git/HEAD`):
  `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER/`
- Output root (created by this task): `workspace/exploration/nbpolar-native-highdim/step2/`
  holding EXACTLY `prereg.md`, `results.json`, `notes.md`.
- Parent plan: `openspec/changes/nbpolar-native-highdim-exploration/` — proposal §Step 2,
  design §D4, `step2-transfer-prior-design.md` (the accepted design; this packet freezes
  its deferred items and executes the probe). Envelope: the Step-1 screening frozen
  selections (decoder, channel, operating points, seeds) — reused, not re-decided.

## Freeze decisions (main thread, 2026-09-23; the deferred items of step2-transfer-prior-design.md §8, now fixed)

| # | Item | Frozen value |
|---|---|---|
| F1 | Decoder | the SAME native q-ary polar SC as Step-1 arm A: read-only reuse of `comparison_bench.formal_ir.nbpolar` (`algebra.make_gf2m`, `transform.polar_transform` alpha=2, `sc.sc_decode`); fields GF(4)=0b111, GF(8)=0b1011, GF(16)=0b10011; design = F7 recursion with design seed 2026092400; operating points n_sym=128, R ∈ {0.30,0.40,0.50,0.60}, K_sym={38,51,64,77}. The bit-plane MSD axis is NOT part of Step 2 (recorded delta: the transfer question is orthogonal; a future freeze may extend to arm B) |
| F2 | Channel | the SAME F4 instance as Step 1: P(δ=0)=0.75, P(δ=+1)=0.24, P(δ=−1)=0.005, 0.005 uniform over the other q−3 offsets |
| F3 | Arm I (informed init) | initial messages from the frozen M2 ±1 structure as a FIXED NUMERICAL REFERENCE — the frozen G1R2 CAL32 triple, copied verbatim, never recomputed: q0=0.7562, q+1=0.2419, q−1=0.0018, remaining q−3 offsets 0 ⇒ frozen floor 1e-15 applied, **NOT renormalized** (frozen floor rule; the floor-pricing effect is part of what is measured — recorded). `log P_I(y∣x') = log(max(p_{δ=(y−x') mod q}, 1e-15))` |
| F4 | Arm U (no-injection baseline; **amendment 3**: replaces the degenerate uniform arm) | `log P_U(y∣x') = log P_F4(y∣x')` — the true synthetic channel belief (standard no-transfer-prior baseline). Recorded rationale: at the `sc_decode` interface a uniform message vector is information-free (blind decoder, FER = 1.0 by construction at 1 − q^-K), making "informed vs uniform" vacuous |
| F5 | Seeds/blocks | identical to Step 1: 16 screening seeds 2026092401..2026092416 × 64 blocks = 1024 trials per (q, R); per (seed, block) one message + one noise matrix shared across arms (paired); numpy `default_rng` |
| F6 | Metric | per design §4: per (q, seed) `g_succ(s) = (Σ_t ok_I(s,t) − Σ_t ok_U(s,t)) / T_s` and `g_nll(s) = Σ_t (nll_U(s,t) − nll_I(s,t)) / T_s`, `T_s` = 64 paired trials; `nll_arm(t) = −Σ_{i∈info set} log2 P_arm(x_i = true_i ∣ y)` (decoder output posterior at information positions); per-seed series + mean/sample-std/range per q; paired Δ series. **No numeric threshold** — zero/negative gain is KEPT EVIDENCE per design §5 |
| F7 | Boundary guard | no EVAL/RESERVE consumption, no re-fit on any data, no `prior_m2.py` change, no CAL change, no decoder change; M2 values copied from the frozen record only |
| F8 | Cross-check G0 | if Step-1's `results.json` is readable at run time (read-only), verify the recomputed information sets equal Step-1's per (q,R) (deterministic re-design with the same design seed); record equality or "reference unavailable, deterministic recompute only" |

## Correctness gates (BEFORE any probe arithmetic; failure ⇒ STOP with zero output files)

- **G1a** oracle agreement with the INFORMED prior: ≥200 tiny instances (n_sym ∈ {2,4};
  100 F4-family + 100 random uniform transitions) per q — arm-I-initialized `sc_decode`
  vs brute-force MAP codeword exactly, 0 mismatches.
- **G1b (renamed, amendment 3):** oracle agreement with the TRUE-CHANNEL belief (was
  "uniform prior"): ≥200 tiny instances (n_sym ∈ {2,4}; 100 F4-family + 100 random
  uniform transitions) per q — arm-U-initialized `sc_decode` vs brute-force MAP codeword
  exactly, 0 mismatches. Documented degeneracy note for `notes.md`: the blind-uniform
  arm (log(1/q) messages) is degenerate by construction (FER = 1.0 at probability
  1 − q^-K); recorded as packet history, no discriminative information.
- **G2** noiseless round-trip 20/20 per q (arm I path).
- **G3** sanity smoke: at R=0.30, both arms' FER < 0.9.
Any gate failure: exit non-zero, write NO output-root files, return condition 2.

## Builder spec (packet-local `s2_transfer.py`, stdlib + numpy)

- Same interpreter policy as Step-1 (amendment 2): PRIMARY
  `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`; nothing installed;
  `PYTHONPATH=comparison_bench/src` for the frozen import chain.
- One deterministic invocation: gates ⇒ design (deterministic re-design, G0 cross-check)
  ⇒ paired probe run ⇒ single end-of-run write of `results.json` + `notes.md`.
- Both arms share: code construction, seeds, messages, noise matrices; ONLY the initial
  message priors differ (F3 vs F4).

## Exact command

```
PYTHONPATH=comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python .workbuddy/queue/NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER/s2_transfer.py --probe-root workspace/exploration/nbpolar-native-highdim/step2/
```

## Budget & one-shot

wall ≤ 3600 s; RSS ≤ 4 GiB; single-threaded; `s2_runs: 1`, `reruns: 0`; one corrective
rebuild only after a zero-output crash, recorded. No tuning after seeing results.

## Write scope / stop rules

- Allowed: output root (3 files) + packet dir (`s2_transfer.py`, `s2_run_log.md`).
- Forbidden: any modification under `comparison_bench/` (imports only), `src/`,
  `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, frozen
  dirs, `.ttbin` paths, other `workspace/` paths (Step-0/Step-1/Step-3 roots are
  read-only reference), change/archive dirs, `AGENT_PROJECT_MEMORY.md`, `docs/`.
- Stop rules: any gate failure; interpreter/import failure; out-of-scope write; any
  real-data/EVAL/RESERVE contact; any prior-code/CAL change; budget exceeded (record, no
  narrowing); any claim object; any post-hoc tuning ⇒ as applicable (hard STOP).

## Output spec (results.json required keys)

`probe`, `tier` ("X"), `question`, `freeze` (F1–F8 echo), `gates` (G0/G1a/G1b/G2/G3
results incl. instance counts and mismatch counts), `population` (synthetic; channel F4;
operating points), `cells` (per q, R: K_sym, H_δ, f, per-arm per-seed FER series +
mean/sample-std/range, per-seed g_succ/g_nll series + mean/sample-std/range, T_s),
`m2_reference` (the verbatim CAL32 triple + floor rule + provenance label),
`attestation` (`no_real_data: true`, `no_fer_claim: true`, `ledger: "L2 synthetic
screening — never cited as L1 real-data FER"`), `counters`, `stop_rules_fired`.

## Acceptance IDs

- **S2-P** draft check PASS (branch, packet files, interpreter+import chain, Step-1 envelope files present as read-only reference, output root absent).
- **S2-1** prereg byte-identical; one run; frozen command.
- **S2-2** all gates pass with the frozen instance counts (0 mismatches); G0 outcome recorded.
- **S2-3** run completeness: every (q,R) cell has 16 seeds × 64 paired trials for both arms; pairing intact.
- **S2-4** metric integrity: g_succ/g_nll denominators and the nll definition as frozen; per-seed + mean/sample-std/range present; zero numeric threshold; negative-recording rule stated.
- **S2-5** write scope exact; Step-0/Step-1/Step-3 roots untouched; `formal_ir` read-only.
- **S2-6** no-claim attestation; M2 reference verbatim with provenance; counters 1/0/0.

## Return (exactly two)

1. All-complete: per-ID PASS + the headline paired table (per q, R: arm FERs, g_succ and
   g_nll mean + spread) + gate results + M2-reference provenance + scoped write evidence.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the
   SINGLE decision needed from the main thread.
