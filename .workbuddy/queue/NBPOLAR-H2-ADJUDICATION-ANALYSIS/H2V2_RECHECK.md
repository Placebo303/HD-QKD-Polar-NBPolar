# H2V2_RECHECK: PASS_WITH_FINDINGS (2026-09-20)

- Verdict: `H2V2_RECHECK: PASS_WITH_FINDINGS`
- Date: 2026-09-20
- Reviewer: reviewer-go, independent recheck
- Reviewer session: `ses_f44aa4832ffeidyigKTYTP3ucx`
- Run root: `workspace/h2/497eecf4-d060-42a2-a862-49e8059590b7/` (run_uuid `497eecf4-d060-42a2-a862-49e8059590b7`)
- Scope: read-only descriptive re-adjudication on 59 rows (56 archive: P20N 16 + P20O 20 + P20Q 20; plus 3 P20S/R1 full-block rows). Zero decoder calls, zero protected opens (IR-5 `.bin` bytes never opened — manifest/sha-level only). P20R read-only context, not joined.

## Adjudications (one line each)

1. H2a REFUTED — evaluable 8→9 via the P20S block (gap −0.00277, ordering-consistent, operational-only identical); anomaly rule still fires 8/9.
2. H2b SUPPORTED — n 37→38 via P20S B r_fail 0.5853 (below-1 point inside v1 range); median 2.2835→2.2651, stays >> 1.10.
3. H2c SUPPORTED — frac_inX 35/38 = 0.921 ≥ 0.50; new datum is the 3rd out-of-X L2 fail archive-wide, first on a spike-local order arm (coord 0, out under both domain flags).
4. H2d SUPPORTED-flat — n_pairs 37→38 via P20S d=0; mean_abs_diff 0.002128 ≤ 0.05.
5. H2e truncated-scope REFUTED-geometry-incoherent STANDS AS-IS — inputs unchanged (IR-4 66/320 = 0.206 < 0.50 with IR-2 median 0.883 ≥ 0.50, AND-conjunction not met; continuity re-verified exact).
6. H2e full-block-scope (n=1, new question) REFUTED-geometry-incoherent — IR-4 0/48 vs IR-2 0.4322, conjunction not met, n=1 caveat (observed values only, no sampling claim).
7. X10 continuity — P20N+P20O subset recomputed gaps match v1 literals exactly (abs_diff 0.0 on all 4 blocks); prior verdicts stand.

## Non-blocking observations (3)

1. Doc typo (now fixed): `h2a_table.md` line 24 said `n_exact=2` for the P20S operational-only slice; correct is `n_exact=1` (A exact, B fail; O oracle excluded), matching `h2a_table.json` `p20s_block_operational_only`. JSON was already correct; no numeric impact.
2. Plan-text attribution correction (no numeric impact): the 0.99966/0.32919 IR-2 extremes cited in the plan as P20Q A/B are P20R arms (A_frozen 0.99966, B_new 0.32919, recomputed from P20R artifacts, not joined).
3. Evidence-size exclusion: `h2v2_record_table.json` is 2,973,931 bytes (> 2 MB standing rule) and is NOT committed; digest + row count recorded instead — sha256 `74be86226f18c5f64c4e43a3d11fed2688cdff067711b3a0da95b1e5d450743a`, n_rows 59 (`rows` list length 59; keys: run_uuid, n_rows, row_counts, field_note, rows). All other run-root files (each ≤ 2 MB) are committed with this batch.

## Interpretation guardrail

treat v2 as descriptive re-adjudication only — the P20S block adds one consistency datum (H2a), one below-1 ratio that barely moves the median (H2b), one out-of-X fail (H2c), one zero floor-diff (H2d), and one n=1 full-block geometry contrast (H2e); no FER, efficiency, leakage, key-rate, reliability, or deployment conclusion is licensed, oracles stay diagnostic-only, and truncated vs full-block scopes must never be pooled.
