# TASK PACKET — NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE (Tier-X: native vs soft-carrying binary baseline)

**GATED PACKET.** Authorizes exactly ONE Tier-X synthetic screening probe and nothing more.
User authorization is recorded verbatim in `STATUS.yaml` as the 2026-09-23 continuation
instruction bound to the next-step priority recorded in the suite closure adjudication
(same-caliber comparison against a stronger soft-information binary baseline); scope is
bound by this packet. Synthetic only: no real data, no `.ttbin`, no EVAL/RESERVE, no
frozen-constant change, no claim.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; Branch (verify `.git/HEAD`):
  `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE/`
- Output root (created by this task): `workspace/exploration/nbpolar-native-highdim/step1b-soft-baseline/`
  holding EXACTLY `prereg.md`, `results.json`, `notes.md`.
- Parent plan: the closure adjudication (`docs/decision-log.md` 2026-09-23) names this probe
  as the most discriminative next step; parent design `step1-screening-design.md` §2 arms/
  fairness (arm B upgraded from hard to soft conditioning — the Step-1 design's own
  "soft-carrying variants deferred" note, now frozen here).

## Scientific question

On the frozen Step-1 envelope (F4 ±1-dominated asymmetric channel, q ∈ {4, 8, 16},
n_sym = 128, R ∈ {0.30, 0.40, 0.50, 0.60}, identical seeds/blocks/pairing), does the
native q-ary SC separation (Step-1: cell-mean ΔFER + for native in 12/12 cells) SURVIVE
when the bit-plane arm B is upgraded from HARD MSD conditioning to EXACT SOFT-CARRYING
MSD conditioning? I.e. is the separation attributable to native-vs-binarized rather than
to soft-carrying-vs-hard-conditioning?

## Freeze decisions (main thread, 2026-09-23; all values fixed before any run)

| # | Item | Frozen value |
|---|---|---|
| F1 | Arm A (native) | UNCHANGED from Step-1: q-ary polar SC via read-only reuse of `comparison_bench.formal_ir.nbpolar` (`algebra.make_gf2m`, `transform.polar_transform` alpha=2, `sc.sc_decode`); fields GF(4)=0b111, GF(8)=0b1011, GF(16)=0b10011; design seed 2026092400; operating points n_sym=128, R∈{0.30,0.40,0.50,0.60}, K_sym={38,51,64,77} |
| F2 | Arm B-hard (reference) | RE-IMPLEMENTED faithfully from the frozen Step-1 builder `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/s1_screen.py` (r-level Gray bit-plane MLC-polar, packet-local binary butterfly + Arikan SC, MSD HARD conditioning on earlier decoded planes, plane order 0..r−1, joint top-(r·K_sym) design, design seed 2026092400). Fidelity is gated by G0 (reproduction) |
| F3 | Arm B-soft (new baseline) | SAME decomposition and SAME information-set design as F2; ONLY the decoding changes to EXACT SOFT-CARRYING MSD conditioning: plane 0 decoded with the marginal induced binary channel; for plane i>0 the per-position binary log-prior over the plane-i bit b is `log S_b − log(S_0 + S_1)` with `S_b = Σ_{a_{<i}, a_{>i}} P_F4(y − symbol(b@i, a_{<i}, a_{>i})) · Π_{j<i} belief_j(a_j) · 2^{-(r-1-i)}`, where `symbol()` is the shared reflected-Gray bits→symbol map, `P_F4` is the F4 offset distribution, `belief_j(v)` is plane j's SC output posterior probability at that position (soft, not hard), and the later planes a_{>i} are marginalized uniformly. Terms ≤ 2^(r−1) ≤ 8 per (position, b). Soft beliefs are taken at ALL n_sym positions from each plane's SC posteriors. Deterministic; no numerical tolerance beyond float64 |
| F4 | Channel / seeds / pairing | F4 unchanged: P(δ=0)=0.75, P(δ=+1)=0.24, P(δ=−1)=0.005, 0.005 uniform over the other q−3 offsets (mod q). Screening seeds 2026092401..2026092416 (16) × 64 blocks = 1024 per (q,R); one message + one noise matrix per (seed,block) shared across ALL THREE arms (paired); numpy `default_rng` |
| F5 | Metric | FER per (q,R,arm) over 1024 blocks; per-seed series + mean/sample-std/range per arm; primary paired ΔFER(seed) = FER_Bsoft − FER_A with series + stats; secondary ΔFER = FER_Bsoft − FER_Bhard. H_δ/f as in Step-1 (H_δ q4 0.8818511717297366, q8 0.8934608122041734, q16 0.900353370320442; f = r·K_sym/(n_sym·H_δ)). NO numeric threshold — qualitative reading recorded; negative-for-native results are kept evidence |
| F6 | Gates (all binding; failure ⇒ STOP with zero output files) | **G0 reproduction**: arm B-hard cell means must equal the Step-1 recorded `armB_fer.mean` values exactly (bit-level) for all 12 cells — proves builder fidelity AND the same-caliber claim; mismatch ⇒ STOP. **G1/G1b oracle**: arm A and arm B-soft each ≥200 tiny instances (n_sym ∈ {2,4}; 100 F4-family + 100 random uniform transitions) per q vs brute-force MAP, 0 hard mismatches, ties ≤1e-9 with first-divergence cascade semantics documented. **G2** noiseless round-trip 20/20 per q per arm. **G3 smoke** FER(R=0.30) < 0.5 both compared arms. **G4** determinism spot-check: a fixed internal excerpt re-run gives identical values |
| F7 | Interpreter | ordered, nothing installed: (1) `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python` (numpy 2.4.4 + pandas 3.0.2 + **numba** confirmed by listing; the frozen `formal_ir` import chain verified under amendment-2 precedent; numba covers the lab arm's `polar_core`); (2) `.venv/bin/python` if it ever exists; timetagger venv demoted (no pandas) |

> **Amendment 1 (2026-09-23, binding)** adds a FOURTH arm — **B-lab**, the production-proven
> binary pipeline from `/mnt/d/Code/qkd-reconciliation-lab` (read-only import of
> `qkd_recon.polar_core` + `qkd_recon.msd_conditional`, exact-F4 shift-invariant MSD tables,
> uniform per-plane k_i = K_sym, hard-prefix soft-metric conditioning), with gate G1c, a
> tertiary paired metric, budget wall ≤ 7200 s, and revised acceptance IDs — see
> `TASK_PACKET_AMENDMENT_1.md`.
> **Amendment 2 (2026-09-23, binding)** redefines gate G1c to a min-sum MIRROR oracle
> (integration fidelity, not optimality) and requires the min-sum-vs-exact-MAP divergence
> counts to be measured and recorded as a documented property of the B-lab baseline — see
> `TASK_PACKET_AMENDMENT_2.md`.

## Builder spec (packet-local `s1b_screen.py`, stdlib + numpy)

- READ FIRST (reference, do not modify): `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/s1_screen.py` — reuse its arm-A calls, its arm-B-hard code (copied into the new builder verbatim where possible), its design functions, and its enumerator pattern; the Step-1 probe root `results.json` is read-only input for G0.
- One deterministic invocation: gates (G0 first) ⇒ design (deterministic re-design, seed 2026092400) ⇒ three-arm paired screening run ⇒ single end-of-run write of `results.json` + `notes.md` into the output root. No file written before gates pass.
- `notes.md` must state the soft-conditioning formula as implemented and document any oracle tie cases with the cascade rule.

## Exact command

```
PYTHONPATH=comparison_bench/src <interpreter> .workbuddy/queue/NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE/s1b_screen.py --probe-root workspace/exploration/nbpolar-native-highdim/step1b-soft-baseline/
```
(interpreter per F7; record which was used)

## Budget & one-shot

wall ≤ 7200 s (four arms incl. the lab baseline, per amendment 1); RSS ≤ 4 GiB; single-threaded; `s1b_runs: 1`, `reruns: 0`; one corrective
rebuild only after a zero-output crash, recorded. No tuning after seeing results.

## Write scope / stop rules

- Allowed: output root (3 files) + packet dir (`s1b_screen.py`, `s1b_run_log.md`).
- Forbidden: any modification under `comparison_bench/` (read-only imports only), `src/`,
  `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, any frozen
  dir, any `.ttbin`, other `workspace/` paths (Step-0/Step-1/Step-2/Step-3 roots are
  READ-ONLY reference), existing change/archive dirs, `AGENT_PROJECT_MEMORY.md`, `docs/`.
- Stop rules: any gate failure (incl. G0 reproduction mismatch); interpreter/import
  failure; out-of-scope write; any real-data/EVAL/RESERVE contact; budget exceeded
  (record, no narrowing); any claim object; any post-hoc tuning ⇒ hard STOP.

## Output spec (results.json required keys)

`probe`, `tier` ("X"), `question`, `freeze` (F1–F7 echo), `gates` (G0 with the 12-cell
equality evidence, G1/G1b/G2/G3/G4 outcomes incl. instance counts), `population`
(synthetic; F4; operating points; seeds), `cells` (per q,R: K_sym, H_δ, f, per-arm
per-seed FER series + mean/sample-std/range for A/Bhard/Bsoft, paired ΔFER series + stats
for Bsoft−A and Bsoft−Bhard), `attestation` (`no_real_data: true`, `no_fer_claim: true`,
`ledger: "L2 synthetic screening — never cited as L1 real-data FER"`), `counters`,
`stop_rules_fired`.

## Acceptance IDs

- **S1B-P** draft check PASS (branch, packet files, interpreter + import chain, Step-1 builder + results.json readable, output root absent).
- **S1B-1** prereg byte-identical; one run; frozen command.
- **S1B-2** all gates pass: G0 reproduction bit-exact on all 12 cells; G1/G1b 0 hard mismatches; G2 20/20; G3 smoke ok; G4 determinism identical.
- **S1B-3** run completeness: 12 cells × 3 arms × 1024 blocks × 16 seeds; pairing intact (shared message + noise per (seed,block) across all three arms).
- **S1B-4** metric integrity: H_δ/f recomputed exact; all series statistics recomputable from the recorded series; the B-hard reference means equal Step-1's recorded values; no numeric threshold anywhere.
- **S1B-5** write scope exact; Step-1 root and `formal_ir` untouched (read-only).
- **S1B-6** no-claim attestation; zero claim language; counters 1/0/0.

## Return (exactly two)

1. All-complete: per-ID PASS + the headline table (per q,R: FER_A, FER_Bhard, FER_Bsoft,
   Δ(Bsoft−A) mean ± sample-std, Δ(Bsoft−Bhard) mean ± sample-std) + gate results +
   G0 equality evidence + scoped write evidence.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the
   SINGLE decision needed from the main thread.
