# DELTA — G1R2 (w=200 / CIRCULAR) vs the accepted G1 contract

Predecessor contract: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1_freeze.md`
(executed once, adjudicated `NBPOLAR_M2_PRIOR_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`).
Successor packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/`.
Per AGENTS.md §10.4 (delta-successor fast path): **everything not listed as CHANGED below is INHERITED verbatim.**

## Why (one paragraph)

G1's δ-tail FAIL (p̂=0.0050202 vs B_tail=2.0e-4 at w=500) is adjudicated. The Tier-X probe S11
(`NBPOLAR_S11_SHG_TAIL_NATURE_COMPLETE_DESCRIPTIVE`, focused review PASS) then showed the tail is a
**pairing-contamination signature**, not channel structure: it scales with the window
(p̂ = 0.0002389 / 0.0050155 / 0.0168189 / 0.0394334 at w=200/500/1000/2000; ratio 165.07), is
offset-insensitive (min at offset 0, spread 10.83%), unclustered (dispersion 0.94269) and
independent-per-pair consistent. At w=200 the CIRCULAR tail is **exactly 0** on the full
1,259,992-pair stream. Additionally the PI confirms **200 ps is the experiment's conventional
coincidence window** — w=500 was the deviation, not w=200. This is a same-point semantic
correction of the pairing/MOD contract, not a new hypothesis.

## CHANGED (delta list — 8 items)

| # | Key / item | G1 | G1R2 | Basis |
|---|---|---|---|---|
| 1 | `pairing_window_primary` | 500 | **200** | S11: contamination scaling; w=200 circular tail = 0; PI confirmation that ±200 ps is the lab's conventional window |
| 2 | `pairing_window_sensitivity` | 200 | **500** | the former primary becomes the sensitivity readout (no switching) |
| 3 | `mod_boundary` | LINEAR_ONLY | **CIRCULAR** | circular distance is the physical neighbour structure on a periodic time axis; wrap events are a deterministic function of the applied +50 ps offset (S11 offset scan: −1023 counts 40/154/294/466/632 at offset 0/25/50/75/100, mirrored to +1023:351 at offset −50) ⇒ they are ±1 time-bin errors, not multi-bin tail |
| 4 | `tag_master` | 2026102201 | **2026103001** | rule TAG_MASTER = EVAL_SEED + 10000; EVAL_SEED 2026092201 → **2026093001** (fresh; collides with no existing packet tag master) |
| 5 | Post-skip ledger expectation | 4,256 frames | **4,219 frames** | floor((1,259,992 − 702×256)/256) = floor(1,080,280/256) = 4,219 (216 trailing pairs dropped). Tier 4,219 ≥ 1,982 ⇒ FULL. RESERVE **4190–4218** = **29** frames (was 66) |
| 6 | 16-block infeasibility arithmetic | deficit 190 | **deficit 227** | 16-block total 4,446 > 4,219; CHAR-shrink variant (587-frame CHAR) 4,251 > 4,219 (deficit 32) ⇒ 16 blocks infeasible under BOTH char sizes; `g2_blocks` stays **14** (the deficit is larger than G1's, so the deviation is cleaner, not weaker) |
| 7 | Reproduction-gate literals | w=500: 1,269,268 / 4,958 | **w=200: 1,259,992 / 4,921** | disclosed plainly in §Reproduction-gate literals; counted here as a contract change (the pair/frame literals the gate compares against) |
| 8 | **Runner re-parameterization (code change)** | G1 science constants hardcoded in `scripts/m2_prior_validation.py` | **window/ledger/packet-driven; G1 path preserved** | REVISION 1 (2026-09-21): the first delta claimed "the runner is already G1-capable and must NOT be modified". Independent delta review (DELTA_FAIL, blocking G) proved that false — four hardcodes make the packet unexecutable at w=200: (1) `REPRO_GATE` (:335-341) pins w=500 `n_pairs 1269268 / n_frames 4958`, compared bit-exact in both `run_closure` (:1126-1144) and `run_g1_science` (:1322-1327) ⇒ both phases refuse at w=200; (2) `SEG_RESERVE = ("reserve", 4190, 4255)` (:351) would emit 66 reserve ids incl. 37 non-existent frames 4219–4255; (3) `G1_PACKET_DIR` (:358) writes the filled config to the G1 packet dir (destructive overwrite of the adjudicated G1 config) and never to the successor path; plus (4) the Phase-A input file `g1r2_freeze_config.json` did not exist. Adopted rework (reviewer option a): list the runner change explicitly, implement as a separately reviewed code change, keep G1's accepted record and code path intact, author the 19-key G1R2 bootstrap config, then re-review. **G1's executed/adjudicated evidence is untouched.** |

**UNCHANGED segment ranges** (the layout arithmetic is window-independent because frames are
defined by pair count): A1-CAL 0–1023 | CAL32 1024–1055 | CHAR 1056–1837 | HELDOUT 1838–2397 |
EVAL 2398–4189 | RESERVE 4190–4218. Closure re-emits the four list keys against these same ranges.

**New reproduction-gate literals** (w=200, from `workspace/census_20260921/20260113_SHG_Type2PPLN_3s/dual_rule_census.json`
+ S11 `results.json` `wgrid_offset50.200`): n_pairs **1,259,992**; pre-skip n_frames **4,921**;
accidental_fraction **0.0058**; far yields 7,259 / 7,366; linear profile {0: 950276, +1: 306566,
−1: 2849, tail: 301 (=−1023:293 + +1023:8)}; circular {0: 950276, +1: 306859, −1: 2857, **tail: 0**};
alignment unchanged (peak 50 / σ 112.45189572400645 / status ok).

## INHERITED (explicitly not re-argued)

- All 19 TO-FREEZE keys and their enforcement; the unified `--freeze-config` contract (null/absent ⇒ exit 2, never a default); `--authorized` store_true; flag↔key cross-checks; K pin 319/6492; out-root confinement; import purity.
- Gates: `B_tail` **2.0e-4** (same derivation: 40.4214 × p × 32768 ≤ 1% × 26214; under CIRCULAR the tail is |δ_circ| ≥ 2, budget logic unchanged); `delta_min` **0.020** bits/symbol; Wilson rules (z=1.96) for the later G2.
- `cal_split_rule` RULE-FIT32-SCORE-HELDOUT; `skip_frames` 702 (INHERITED_NOT_DERIVED); `char_sample_pairs` 200,192; `g2_blocks` 14; `g2_arms` [A1_M0_1024f_incumbent, A2_M0_32f_matched, B_M2_32f_candidate]; `block_formation_fallback`.
- Two-phase design (closure → verification gate → execution), budgets (closure ≤ 300 s; execution ≤ 600 s / 2 GiB per acquisition), stop rules, remainder-population NLL/H check (exempt, no gate), SHG `_2` frozen for G3, M2 CANDIDATE, descriptive/non-claim, no FER/efficiency language.
- K decision (fixed-f vs fixed-K) DEFERRED; construction re-derivation deferred (frozen P16 order).

## Expected δ-tail outcome (recorded in advance — not a result, a consequence of S11)

S11 measured the **full-stream** w=200 CIRCULAR tail = 0. CHAR (frames 1056–1837, 200,192 pairs) is a
subset of that stream, so its CIRCULAR tail is **0 by inclusion** ⇒ p̂ = 0, U = 3/200,192 = 1.4986e-5
(13.3× under B_tail) ⇒ **PASS is arithmetically forced, not hoped for**. The G1R2 value therefore lies
in the NEW measurements S11 could not make (decoder-free, no prior fitting): CAL32 FIT triple,
H1/H2/H_total for both models, and the held-out NLL under the w=200/CIRCULAR contract — the inputs
the later G2 freeze needs and the K_total question depends on.

## Caveats carried into G1R2

1. **Truncation**: w=200 keeps a subset of pairs. Mitigating measurement: c0 is identical (950,276)
   across w=200/500/1000/2000, so no δ=0 pair is lost by narrowing — but the kept population is a
   timing-truncated sample, and any rate/efficiency reading must say so.
2. **CIRCULAR wrap pricing**: wrap events are priced at the pooled q+1/q−1. Justified by the offset-scan
   asymmetry above; if the applied offset ever changes, the wrap split must be re-measured.
3. **Far-offset baseline is structured** (S11 R4: tail ≈ 0.40, not uniform 0.997) ⇒ the census accidental
   estimate for w=200 (0.0058) must not be read as a uniform-accidental level.
4. G1's bounded negative stands on its own contract (w=500/LINEAR_ONLY); G1R2 does not retroactively
   change it, and S11/G1R2 must never be read as "the G1 FAIL was wrong" — it was correct under the
   contract it was frozen at.
