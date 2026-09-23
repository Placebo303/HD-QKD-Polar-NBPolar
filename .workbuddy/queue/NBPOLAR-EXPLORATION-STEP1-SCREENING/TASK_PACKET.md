# TASK PACKET — NBPOLAR-EXPLORATION-STEP1-SCREENING (Tier-X: native q-ary vs bit-plane MSD)

**GATED PACKET.** Authorizes exactly ONE Tier-X screening run and nothing else. User
authorization is recorded verbatim in `STATUS.yaml` as the 2026-09-23 instruction to
complete the full direction-exploration suite; scope is bound by this packet. Synthetic
only: no real data, no `.ttbin`, no EVAL/RESERVE, no decoder on real data, no frozen
constant changed, no claim.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; Branch (verify `.git/HEAD`):
  `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/`
- Output root (created by this task): `workspace/exploration/nbpolar-native-highdim/step1/`
  holding EXACTLY `prereg.md`, `results.json`, `notes.md`.
- Parent plan: `openspec/changes/nbpolar-native-highdim-exploration/` — proposal §Step 1,
  design §D3, `step1-screening-design.md` (the accepted design; this packet freezes its
  deferred items and executes the screening).

## Freeze decisions (main thread, 2026-09-23; the six deferred items, now fixed)

| # | Item | Frozen value |
|---|---|---|
| F1 | Arm A algorithm | **q-ary polar SC** reusing (READ-ONLY, zero modification — AGENTS.md §10.1(5) reuse-before-rebuilding) `comparison_bench.formal_ir.nbpolar.algebra.make_gf2m`, `.transform.polar_transform` (GF(q) butterfly, alpha=2), `.sc.sc_decode` (log-domain q-ary SC), and `.oracle` (enumerator pattern). Import failure under available interpreters ⇒ STOP (nothing installed) |
| F2 | Arm B algorithm | **r-level bit-plane MLC-polar with MSD hard conditioning**: r binary polar codes (packet-local binary butterfly + Arikan SC, numpy), Gray-mapped bit-planes, plane order 0..r−1 (increasing Gray significance); each plane designed on its induced binary channel (marginal-averaged over earlier message bits, uniform); at decode, plane i's SC is conditioned on the earlier planes' DECODED bits (hard MSD). Soft-carrying variants: deferred future-freeze item (recorded) |
| F3 | Fields / mapping | GF(4) primitive x²+x+1 (0b111); GF(8) x³+x+1 (0b1011); GF(16) x⁴+x+1 (0b10011); alpha = 2. Gray mapping (reflected binary Gray) for message↔symbol in BOTH arms (shared, so pairing is exact) |
| F4 | Channel family instance (single member) | ±1-dominated, asymmetric — mirroring the Step-0 diagnosis and the frozen CAL32 proportions: P(δ=0)=0.75, P(δ=+1)=0.24, P(δ=−1)=0.005, remaining mass 0.005 uniform over the other q−3 offsets. Symmetric control: NOT in this probe (recorded) |
| F5 | Operating points | n_sym = 128 symbols/block (all q); rates R ∈ {0.30, 0.40, 0.50, 0.60}; K_sym = round(R·128) (→ 38, 51, 64, 77). Information set per (q, R, arm): top-K positions by the design metric below; design seed 2026092400 (fixed for all designs, deterministic) |
| F6 | Seeds / blocks | screening seeds 2026092401..2026092416 (16 seeds); 64 blocks per seed ⇒ **1024 blocks per (q, R, arm)**. Per (seed, block): one message draw + one noise matrix; BOTH arms transmit through the SAME noise matrix (paired draws). PRNG: numpy `default_rng(seed_derived)` |
| F7 | Design metric | q-ary split-channel recursion `W⁻(y₁,y₂\|u₁)=1/q·Σ_{u₂}W(y₁\|u₁⊕u₂)W(y₂\|u₂)`, `W⁺(y₁,y₂,u₁\|u₂)=1/q·W(y₁\|u₁⊕u₂)W(y₂\|u₂)`; per-position reliability = Monte-Carlo estimate of H(uᵢ\|y) under the recursion (design seed fixed); top-K = information set. Arm B: identical method per plane on its induced binary channel (standard binary Arikan split + Bhattacharyva or MC entropy — same seed) |
| F8 | Metric | FER = block error fraction over the 1024 blocks per cell (block fails iff ANY message symbol decodes wrong); `f = r·K_sym / (n_sym · H_δ)` with H_δ = entropy (bits, log2) of the frozen δ distribution (identical for both arms; same channel). Record per-(q,R,arm): per-seed FER series + mean/sample-std/range; paired ΔFER(seed) = FER_B − FER_A series + mean/sample-std/range. **No numeric threshold is fixed here** — the qualitative bar of design §5 applies (no separation across q ⇒ do not scale + record negative; clear separation ⇒ Step 2/3 designs may be frozen next) |

## Correctness gates (BEFORE any screening arithmetic; failure ⇒ STOP with zero output files)

1. **Oracle agreement (per arm, per q):** ≥ 200 random tiny instances (n_sym ∈ {2,4};
   100 channel-instance draws from the F4 family + 100 random uniform transition matrices):
   arm A `sc_decode` vs brute-force MAP over all q^n codewords — decoded codeword must
   equal the MAP codeword exactly; arm B MSD pipeline vs brute-force MAP over arm B's
   code — same. Mismatch count must be **0**.
2. **Noiseless round-trip:** error-free channel through both encoders/decoders on 20
   random blocks per q — 20/20 exact for both arms.
3. **Low-rate smoke:** at R = 0.30, both arms' FER must be < 0.5 (code/design quality
   smoke gate; failure ⇒ design or decoder defect ⇒ STOP).
Any gate failure: exit non-zero, write NO output-root files, return condition 2.

## Builder spec (packet-local `s1_screen.py`, stdlib + numpy)

- Import path: run with `PYTHONPATH=comparison_bench/src` (record the exact command).
- Phases in ONE deterministic invocation: (1) correctness gates; (2) design per (q,R,arm);
  (3) screening run over q × R × arm × seed × block; (4) single end-of-run write of
  `results.json` + `notes.md` into the output root. No file is written before gates pass.
- Encoding arm A: message symbols at the information-set positions, zeros elsewhere,
  `polar_transform` (inverse-free: the butterfly is its own structure — use the module's
  documented encode path; verify round-trip via the noiseless gate).
- Decoding arm A: `sc_decode` with per-symbol log-priors from the F4 channel
  (`log P(y|x')` over x' ∈ GF(q)); frozen positions pinned to 0.
- Decoding arm B: per-plane binary polar SC (packet-local) with hard MSD conditioning.
- No network, no installs, no randomness outside the frozen seeds; deterministic.

## Exact command

```
PYTHONPATH=comparison_bench/src <interpreter> .workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/s1_screen.py --probe-root workspace/exploration/nbpolar-native-highdim/step1/
```
(interpreter per ordered policy: `.venv/bin/python` absent → `/home/karel_303/.venvs/timetagger/bin/python` (has numpy) → no stdlib fallback for this builder because numpy + formal_ir import are required; absence of a numpy-capable interpreter ⇒ STOP, nothing installed.)

## Budget & one-shot

wall ≤ 5400 s; RSS ≤ 4 GiB; single-threaded; `s1_runs: 1`, `reruns: 0`; one corrective
rebuild only after a zero-output crash, recorded. No parameter/seed/definition change
between prereg and run; nothing tuned after seeing results.

## Write scope / stop rules

- Allowed: output root (3 files) + packet dir (`s1_screen.py`, `s1_run_log.md`).
- Forbidden: any modification under `comparison_bench/` (imports only), `src/`,
  `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, any frozen
  dir, any `.ttbin`, other `workspace/` paths, existing change/archive dirs,
  `AGENT_PROJECT_MEMORY.md`, `docs/`.
- Stop rules: any correctness-gate failure; import failure; out-of-scope write; any
  real-data/EVAL/RESERVE contact; budget exceeded (record, no narrowing); any sim-FER
  framed as real FER; any post-hoc tuning.

## Output spec (results.json required keys)

`probe`, `tier` ("X"), `question`, `freeze` (F1–F8 echo), `gates` (oracle/round-trip/
smoke results incl. instance counts and mismatch counts), `population` (synthetic; n_sym;
q set; channel instance), `cells` (per q,R: K_sym, H_δ_bits, f, per-arm per-seed FER
series + mean/sample-std/range, paired ΔFER series + mean/sample-std/range, n_blocks),
`attestation` (`no_real_data: true`, `no_fer_claim: true`, `ledger: "L2 synthetic
screening — never cited as L1 real-data FER"`), `counters` (`s1_runs`, `reruns`),
`stop_rules_fired`.

## Acceptance IDs

- **S1-P** draft check PASS (branch, packet files, numpy-capable interpreter, output root absent).
- **S1-1** prereg byte-identical; run follows the frozen command; one run.
- **S1-2** all three correctness gates pass with the frozen instance counts (0 mismatches).
- **S1-3** run completeness: every (q,R,arm) cell has 1024 blocks × 16 seeds; pairing intact (same message + noise matrix per arm within a (seed,block)).
- **S1-4** metric integrity: FER denominators, f formula and H_δ value recorded, per-seed + mean/sample-std/range present, paired series present, zero numeric threshold invented.
- **S1-5** write scope exact; `formal_ir` untouched (read-only import only).
- **S1-6** no-claim attestation present; zero claim language; counters 1/0/0.

## Return (exactly two)

1. All-complete: per-ID PASS + the headline screening table (per q: per-arm FER at each R,
   paired ΔFER mean + spread) + gate results + counters + scoped write evidence.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the
   SINGLE decision needed from the main thread.
