# TASK PACKET — NBPOLAR-S11-SHG-TAIL-NATURE (Tier-X probe: nature of the SHG `_1` δ-tail)

Per AGENTS.md §10.4 (Tier X — probe runs, non-claim) and §10.1 (one complete frozen packet before delegation). This packet authorizes NOTHING until verbatim user authorization flips `STATUS.yaml`.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/`
- Probe root (ONLY write root): `workspace/probes/nbpolar_s11_shg_tail_nature/` (`prereg.md`, `body.py`, `results.json`; gitignored by design).
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (TimeTagger 2.22.6 + Swabian shim; read the `.ttbin` traps in `docs/troubleshooting.md` first).
- Nature: Tier-X descriptive/non-claim, DECODER-FREE, zero prior fitting, zero model selection. No candidate/accepted token; no attempt consumption; no scientific-status change; no ledger/memory/index updates in-packet (milestone batch).

## Motivation (why this probe exists)

G1 (adjudicated bounded negative, `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/G1_ADJUDICATION.md`) found the SHG `_1` δ-tail at 0.50% (1005/200,192 at (N) w=500, LINEAR_ONLY) — ~25× over the ±1 premise budget (B_tail=2.0e-4). Diagnostic puzzle: 0.50% is BELOW the uniform-accidental prediction from the census w=500 accidental estimate (1.44%) — a uniform-accidental pair would land in the tail with probability ≈ 1 − 3/1024 ≈ 99.7%, so if the far-offset baseline pairs were truly uniform they would imply ~1.4% tail from accidentals alone. The tail is therefore NOT explained as pure uniform accidentals; its nature (accidental-artifact vs alignment-artifact vs channel structure vs baseline-overestimate) is unknown, and the next prior-form decision must not be made on a guess. This probe measures the tail's signatures decoder-free.

## Question (one sentence, prereg verbatim)

On SHG `_1`, is the observed |δ|≥2 tail an accidental-pairing artifact (scales with window/accidental fraction), an alignment artifact (offset-sensitive), or channel structure (window- and offset-stable) — and is the census far-offset accidental baseline itself uniform (tail ≈ 99.7%) or structured?

## Exact parameters (frozen; no tuning after prereg)

- Source: SHG `_1` primary `/mnt/d/Data/Raw Data/2026.1.13/SHG_Type2PPLN_3s_2026-01-13_162106/SHG_Type2PPLN_3s_2026-01-13_162106.ttbin` via `FileReader` (auto-follows `.1`; NEVER concatenate); 16,130,065 events; channels 1/5. NEVER touch SHG `_2`.
- Pairing: vendored (N) narrow nearest-unique from the 2026-09-21 census implementation (`workspace/dual_rule_census_20260921.py` — read-only reference; vendor into the probe body, do not import from workspace). Frozen constants: d=1024, bin_width 200 ps, period 204800 ps, frame_pairs 256, gate 200 ps, threshold 40000 ps; symbol map `(b_A % 1024, b_B % 1024)`, `b = t // 200`, `tA_aligned = tA_raw + offset`.
- Frozen alignment: derived offset +50 ps (census `peak_center_ps`, σ=112.45189572400645, status ok). NOT re-derived in this probe (G1 already reproduced it 5/5 exact); the offset-scan arm perturbs around it as a measurement.
- Arms (all at full event stream, NO skip-702, except the anchor):
  - **W-grid** at offset +50: w ∈ {200, 500, 1000, 2000} → per-arm δ-profile + tail rate p̂_w. Census accidental estimates for reference: 0.0058 / 0.0144 / 0.0284 / 0.0555.
  - **Anchor** at w=500, skip-702, post-skip frames **1056–1837** (= the G1 CHAR segment per the frozen `SEG_RANGES` in `scripts/m2_prior_validation.py` and `g1_freeze_config.json`): must reproduce p̂ = 0.0050202 (1005/200,192) EXACTLY. Mismatch ⇒ the probe is invalid: STOP, record, do not proceed to other arms' interpretation. [CORRECTION 2026-09-21 by main thread: the pre-correction text said "first 782 post-skip frames" (0–781), which contradicts the frozen CHAR range; corrected to 1056–1837 — the only range that can satisfy the exact-reproduction gate. No other parameter changed.]
  - **Offset scan** at w=500 (no skip): offset ∈ {50, 25, 75, 0, 100, −50} ps → p̂_off.
  - **Far-offset baseline** at w=500 (no skip): offset ∈ {50 + 409600, 50 − 409600} ps (the census baseline shifts) → full δ-profile + tail rate. This tests the accidental-model assumption directly: uniform accidentals would give tail ≈ 99.7%; a structured far-offset profile falsifies the uniform-accidental reading of the census baseline.
- Statistics per arm: linear AND circular δ-profiles {0, ±1, ±2..k} under LINEAR_ONLY semantics (wrap cells (0,1023)/(1023,0) count as tail); p̂ = tail/n; q+1/q−1 rates. Anchor arm additionally: per-frame tail clustering over the 782 frames — count of frames with ≥1 tail event vs Poisson(λ = p̂×256) expectation; dispersion ratio = observed variance / mean across frames.
- No decoder, no genie/SCL, no prior fit beyond event counts, no window/threshold choice after prereg, no SHG `_2` contact, no protected reads outside SHG `_1`.

## Preregistered readouts (descriptive classification; NO pass/fail, NO claim)

1. **Accidental signature**: p̂ scales ~proportionally with the census accidental estimate across the W-grid (p̂_2000/p̂_200 ≳ 5).
2. **Non-accidental / structure signature**: p̂ roughly flat across the W-grid (ratio ≲ 2) while the accidental estimate rises ~10×.
3. **Alignment signature**: p̂ minimized at the derived offset (+50), rising monotonically with |offset − 50|.
4. **Baseline-artifact signature**: far-offset tail ≪ 99.7% (e.g. within 2× of the in-window tail) ⇒ the census far-offset baseline is NOT uniform and the accidental estimate cannot be read as a uniform-accidental level; far-offset tail ≈ 99.7% ⇒ the uniform-accidental assumption holds and the in-window tail is a genuine mixture component.
5. **Clustering**: anchor dispersion ratio ≫ 1 ⇒ time-clustered/structured tail; ≈ 1 ⇒ independent per-pair process.
The probe reports the five readouts with their arithmetic; the classification is descriptive and binds nothing. Any scientific use requires a later main-thread decision + its own preregistration.

## Budget + stop rules

≤ 300 s wall / 2 GiB RSS, single-threaded (census dual-rule full grid over this acquisition took 42.1 s). Exceeded ⇒ STOP + blocker (no tuning to fit). Anchor mismatch ⇒ STOP (invalid probe). Any FORBIDDEN touch (SHG `_2`, decoder, out-of-root write, post-prereg parameter change) ⇒ STOP + blocker. Ambiguity ⇒ STOP (second return condition).

## Acceptance IDs → evidence

- `S11-P` prereg: `prereg.md` written BEFORE any compute, verbatim question + parameters + command (three-line core per PROBE_TIER).
- `S11-A` anchor: exact reproduction of p̂ = 0.0050202 (or STOP record).
- `S11-B` W-grid: four arms' linear+circular profiles + p̂_w + q±1.
- `S11-C` offset scan: six offsets' p̂_off.
- `S11-D` far-offset baseline: two arms' full profiles + tail rates.
- `S11-E` clustering: anchor dispersion ratio with arithmetic.
- `S11-R` results: ONE `results.json` with per-arm values (mean/std/range N/A — deterministic, no seeds) + the five readouts.

## Return (exactly two)

1. All-complete: per-ID S11-P..S11-R PASS with evidence paths + `results.json` summary + run log. "Still incomplete" is not a report.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision needed.

## Out of scope (later freezes / other agents)

Any prior-form decision (M2 or otherwise); any G2/G3 work; any real-data decode; any decision-log/memory/index update (milestone batch after the focused numerical review); SHG `_2`.
