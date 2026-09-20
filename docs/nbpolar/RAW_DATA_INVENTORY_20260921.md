# RAW Data Inventory — 13 PI-supplied candidate locations (2026-09-21)

> AMENDMENT 2026-09-21 — **PI RULING: Type0 and SHG are only SOURCE differences
> and have NO effect on the IR process ⇒ ALL 10 acquisitions are in scope.**
> This supersedes every `TYPE0_SOURCE_UNVERIFIED_NEEDS_PI_CONFIRMATION` flag in
> this doc (§2 table cells, Q2, §4). The `Type0_nofilter` directory-name labels
> themselves are unchanged facts.

- Inventory date (UTC): 2026-09-20. Method: `ls`, `find`, `stat` ONLY on the data paths
  (+ `grep`/`ls` on **repo** files for curation cross-check — never on data-folder contents).
- **RESULTS-FILES-READ CONFIRMATION: NONE. Zero results/analysis/output file contents were opened.
  Only directory/file NAMES were listed via `ls`/`find`. No number from any data-folder artifact
  is quoted or used anywhere in this report.** All sizes below are `stat` sizes of `.ttbin` files only.
- Nothing was executed: no pipeline, no decoder, no `longrun_*`/`minrerun_*`, no parsing of any raw file.
- Nothing was written to `results/` or `comparison_bench/outputs_comparison/`.
  Only two NEW files were created: this report + `workspace/data_intake_20260921/inventory.json` (scratch).
- Paths below are POSIX/WSL. Windows originals: replace `/mnt/d/` with `D:\` and `/` with `\`.
- Env note: the repo has no `.venv` in this checkout; stdlib-only `/usr/bin/python3` was used
  solely to assemble the scratch JSON from already-observed `stat` values (no numpy/pytest needed,
  no data parsing performed).
- Frozen sessions for match-check: `20260123_1M_600k_0dB` (1M), `20260107_PPLN_1p5M` (1.5M),
  `20260123_2M_1p2M_0dB` (2M) — per `v71_data_registry.json`; provenance pairs live under
  `comparison_bench/outputs_comparison/v55_intake_20260828/pairs/` (that dir is ABSENT in this
  checkout — `ls` returns "No such file or directory"; registry provenance is therefore by-record only).

## 1. Per-file table (all 20 `.ttbin` files)

| # | WSL absolute path | bytes | human | mtime (ISO, +08:00 file tz) | segment |
|---|-------------------|-------|-------|-----------------------------|---------|
| 1 | `/mnt/d/Data/Raw Data/2026.1.12/Type2PPLN_3s_2026-01-12_165236.ttbin` | 8,160 | 8.0 KiB | 2026-01-12T16:52:36 | primary |
| 2 | `/mnt/d/Data/Raw Data/2026.1.12/Type2PPLN_3s_2026-01-12_165236.1.ttbin` | 16,909,712 | 16.1 MiB | 2026-01-12T16:53:06 | continuation `.1` |
| 3 | `/mnt/d/Data/Raw Data/2026.1.13/SHG_Type2PPLN_3s_2026-01-13_162106/SHG_Type2PPLN_3s_2026-01-13_162106.ttbin` | 8,256 | 8.1 KiB | 2026-01-13T16:21:06 | primary |
| 4 | `/mnt/d/Data/Raw Data/2026.1.13/SHG_Type2PPLN_3s_2026-01-13_162106/SHG_Type2PPLN_3s_2026-01-13_162106.1.ttbin` | 59,329,744 | 56.6 MiB | 2026-01-13T16:21:09 | continuation `.1` |
| 5 | `/mnt/d/Data/Raw Data/2026.1.13/SHG_Type2PPLN_3s_2_2026-01-13_162148/SHG_Type2PPLN_3s_2_2026-01-13_162148.ttbin` | 8,160 | 8.0 KiB | 2026-01-13T16:21:48 | primary |
| 6 | `/mnt/d/Data/Raw Data/2026.1.13/SHG_Type2PPLN_3s_2_2026-01-13_162148/SHG_Type2PPLN_3s_2_2026-01-13_162148.1.ttbin` | 60,113,104 | 57.3 MiB | 2026-01-13T16:21:51 | continuation `.1` |
| 7 | `/mnt/d/Data/Raw Data/2026.1.20/Type0_nofilter_500K_3s_2026-01-20_193050/Type0_nofilter_500K_3s_2026-01-20_193050.ttbin` | 21,072 | 20.6 KiB | 2026-01-20T19:30:50 | primary |
| 8 | `/mnt/d/Data/Raw Data/2026.1.20/Type0_nofilter_500K_3s_2026-01-20_193050/Type0_nofilter_500K_3s_2026-01-20_193050.1.ttbin` | 13,240,624 | 12.6 MiB | 2026-01-20T19:30:53 | continuation `.1` |
| 9 | `/mnt/d/Data/Raw Data/2026.1.20/Type0_nofilter_1M_3s_2026-01-20_192857/Type0_nofilter_1M_3s_2026-01-20_192857.ttbin` | 21,072 | 20.6 KiB | 2026-01-20T19:28:57 | primary |
| 10 | `/mnt/d/Data/Raw Data/2026.1.20/Type0_nofilter_1M_3s_2026-01-20_192857/Type0_nofilter_1M_3s_2026-01-20_192857.1.ttbin` | 23,285,488 | 22.2 MiB | 2026-01-20T19:29:00 | continuation `.1` |
| 11 | `/mnt/d/Data/Raw Data/2026.1.20/Type0_nofilter_1_5M_3s_2026-01-20_193255/Type0_nofilter_1_5M_3s_2026-01-20_193255.ttbin` | 21,072 | 20.6 KiB | 2026-01-20T19:32:55 | primary |
| 12 | `/mnt/d/Data/Raw Data/2026.1.20/Type0_nofilter_1_5M_3s_2026-01-20_193255/Type0_nofilter_1_5M_3s_2026-01-20_193255.1.ttbin` | 33,469,312 | 31.9 MiB | 2026-01-20T19:32:58 | continuation `.1` |
| 13 | `/mnt/d/Data/Raw Data/2026.1.20/Type0_nofilter_2M_3s_2026-01-20_193411/Type0_nofilter_2M_3s_2026-01-20_193411.ttbin` | 21,072 | 20.6 KiB | 2026-01-20T19:34:11 | primary |
| 14 | `/mnt/d/Data/Raw Data/2026.1.20/Type0_nofilter_2M_3s_2026-01-20_193411/Type0_nofilter_2M_3s_2026-01-20_193411.1.ttbin` | 47,920,192 | 45.7 MiB | 2026-01-20T19:34:14 | continuation `.1` |
| 15 | `/mnt/d/Data/Raw Data/2026.1.21/Type2_1-5M_3s_2026-01-21_183806/Type2_1-5M_3s_2026-01-21_183806.ttbin` | 21,264 | 20.8 KiB | 2026-01-21T18:38:06 | primary |
| 16 | `/mnt/d/Data/Raw Data/2026.1.21/Type2_1-5M_3s_2026-01-21_183806/Type2_1-5M_3s_2026-01-21_183806.1.ttbin` | 31,014,064 | 29.6 MiB | 2026-01-21T18:38:09 | continuation `.1` |
| 17 | `/mnt/d/Data/Raw Data/2026.1.21/Type2_1M_3s_2026-01-21_184040/Type2_1M_3s_2026-01-21_184040.ttbin` | 21,264 | 20.8 KiB | 2026-01-21T18:40:40 | primary |
| 18 | `/mnt/d/Data/Raw Data/2026.1.21/Type2_1M_3s_2026-01-21_184040/Type2_1M_3s_2026-01-21_184040.1.ttbin` | 22,025,840 | 21.0 MiB | 2026-01-21T18:40:43 | continuation `.1` |
| 19 | `/mnt/d/Data/Raw Data/2026.1.21/Type2_2M_3s_2026-01-21_183657/Type2_2M_3s_2026-01-21_183657.ttbin` | 21,264 | 20.8 KiB | 2026-01-21T18:36:57 | primary |
| 20 | `/mnt/d/Data/Raw Data/2026.1.21/Type2_2M_3s_2026-01-21_183657/Type2_2M_3s_2026-01-21_183657.1.ttbin` | 41,768,912 | 39.8 MiB | 2026-01-21T18:37:00 | continuation `.1` |

Segment convention (per task brief): `<stem>.ttbin` + `<stem>.1.ttbin` = one acquisition split across
two files. **OBSERVED anomaly (reported, not interpreted): in all 10 acquisitions the primary
`.ttbin` is tiny (8–21 KiB) while the `.1.ttbin` carries ~99.9% of bytes.** Whether the tiny primary
is a header/first-chunk or something else REQUIRES parser confirmation — no bytes were read.

> PARSER CONFIRMATION 2026-09-21 (Stage A on `20260112_Type2PPLN_3s` only;
> no other acquisition parsed): `FileReader` auto-follows `.1` — reading
> EITHER file yields the identical full acquisition (3,836,088 events each,
> identical channel histograms and timestamp span); concatenating both reads
> duplicates everything (7,672,176 = exact 2×) ⇒ read the primary
> `<stem>.ttbin` ONLY. Whether the same holds for the other 9 acquisitions is
> assumed by the census merge rule, not re-verified here.

## 2. Acquisition groups (same stem ⇒ one acquisition; 10 total)

| acq_id | date | source type (verbatim from dir name) | brightness token | dur | files (primary + `.1`) | total bytes | untrusted results present? | session match |
|--------|------|--------------------------------------|------------------|-----|------------------------|-------------|----------------------------|---------------|
| `20260112_Type2PPLN_3s` | 2026-01-12 | `Type2PPLN` | none in name | 3s | 8,160 + 16,909,712 | 16,917,872 (~16.1 MiB) | YES — names only (histograms, `jti_*`, `*.CSV`, `*.opju`; full name list in JSON) | LIKELY_NEW_SESSION — date differs from 01-07/01-23 frozen sessions; stem absent from registries |
| `20260113_SHG_Type2PPLN_3s` | 2026-01-13 16:21:06 | `SHG_Type2PPLN` | none in name | 3s | 8,256 + 59,329,744 | 59,338,000 (~56.6 MiB) | none observed | LIKELY_NEW_SESSION — same reason |
| `20260113_SHG_Type2PPLN_3s_2` | 2026-01-13 16:21:48 | `SHG_Type2PPLN` (2nd same-day run, `_2`) | none (`_2` = run index, NOT brightness) | 3s | 8,160 + 60,113,104 | 60,121,264 (~57.3 MiB) | YES — names only (`pie_skr_scan_ch1_5*.csv`, `*.meta.json`, `SHG_Type2PPLN_3s_PIESKR.opju`) | LIKELY_NEW_SESSION — same reason (v65a scout ref is exploratory only, not registration) |
| `20260120_Type0_nofilter_500K_3s` | 2026-01-20 | `Type0_nofilter` | `500K` | 3s | 21,072 + 13,240,624 | 13,261,696 (~12.6 MiB) | YES — names only (`e2e_new_ttbin_fullgrid_20260305_031909/`) | LIKELY_NEW_SESSION |
| `20260120_Type0_nofilter_1M_3s` | 2026-01-20 | `Type0_nofilter` | `1M` | 3s | 21,072 + 23,285,488 | 23,306,560 (~22.2 MiB) | YES — names only (`e2e_new_ttbin_fullgrid_20260304_231635/`) | LIKELY_NEW_SESSION |
| `20260120_Type0_nofilter_1_5M_3s` | 2026-01-20 | `Type0_nofilter` | `1_5M` | 3s | 21,072 + 33,469,312 | 33,490,384 (~31.9 MiB) | YES — names only (`e2e_new_ttbin_fullgrid_20260305_055352/`) | LIKELY_NEW_SESSION |
| `20260120_Type0_nofilter_2M_3s` | 2026-01-20 | `Type0_nofilter` | `2M` | 3s | 21,072 + 47,920,192 | 47,941,264 (~45.7 MiB) | YES — names only (`e2e_new_ttbin_fullgrid_20260305_011024/`) | LIKELY_NEW_SESSION |
| `20260121_Type2_1-5M_3s` | 2026-01-21 | `Type2` | `1-5M` | 3s | 21,264 + 31,014,064 | 31,035,328 (~29.6 MiB) | config sidecar `run_config.json` present (NOT read); no results subdirs | LIKELY_NEW_SESSION — date 01-21 differs; stem absent from registries |
| `20260121_Type2_1M_3s` | 2026-01-21 | `Type2` | `1M` | 3s | 21,264 + 22,025,840 | 22,047,104 (~21.0 MiB) | YES, HEAVY — 100+ `results_*` dirs + analysis `*.csv`/`*.md` + `run_config*.json` (full name list in JSON; contents never opened) | LIKELY_NEW_SESSION — same reason |
| `20260121_Type2_2M_3s` | 2026-01-21 | `Type2` | `2M` | 3s | 21,264 + 41,768,912 | 41,790,176 (~39.9 MiB) | config sidecar `run_config.json` present (NOT read); no results subdirs | LIKELY_NEW_SESSION — same reason |

Source-type wording discipline: the table states exactly what each directory name says.
No physics is inferred (in particular, whether `SHG_Type2PPLN` is Type-II SPDC is NOT stated).

## 3. Answers to the five questions

**Q1 — `.ttbin` files nested deeper than the given paths?**
NO. A recursive `find -name '*.ttbin*'` over all four date dirs (`2026.1.12`, `2026.1.13`,
`2026.1.20`, `2026.1.21`) returns exactly the 20 files in §1 — every one sits at the top level
of its acquisition directory. There are NO `.2.ttbin`/`.3.ttbin` (or higher) segments anywhere,
and the `e2e_new_ttbin_fullgrid_*` / `results_*` subdirs contain zero `.ttbin` files.
Side note (names only): the date dirs contain extra non-ttbin acquisition byproducts that were
NOT among the 13 supplied paths — `2026.1.13/20260113_{165733,170216,170828}/` and
`2026.1.21/20260121_{175713,180507,181033,182048}/` (each holding `heralded_g2_cw_*` files),
`Type0-SHG.opju`, histograms/`opju`/`xlsx` files. Listed by name only, contents never opened.

**Q2 — Is `Type0` a different source type from the Type-II SPDC of the frozen sessions?**
**PI RULING 2026-09-21 (SUPERSEDES the earlier
`TYPE0_SOURCE_UNVERIFIED_NEEDS_PI_CONFIRMATION` flag): Type0 and SHG are only
SOURCE differences and have NO effect on the IR process ⇒ ALL 10 acquisitions
are in scope.** What the names say (unchanged fact): the four 2026-01-20
directories are labeled `Type0_nofilter_…`, which is a different source label
from the `Type2*` labels of the other six acquisitions and from the Type-II
SPDC identity of the frozen sessions. The label difference stands; the
usability exclusion is withdrawn — no PI confirmation is outstanding.

**Q3 — Which acquisitions have BOTH `.ttbin` AND ≥1 `.N.ttbin` continuation?**
ALL 10. Every acquisition is complete-looking: one primary `<stem>.ttbin` plus exactly one
`<stem>.1.ttbin` continuation; no acquisition is missing either half; no `.2+` segments exist.

**Q4 — Total raw volume + frame estimate?**
Total = **349,249,648 bytes ≈ 333.1 MiB (≈ 0.349 GB)** across 20 files / 10 acquisitions
(Type-II-labeled: 231,249,744 B ≈ 220.5 MiB; Type0-labeled: 117,999,904 B ≈ 112.5 MiB).
Frame/pair-count estimate: **`REQUIRES_PARSING_NOT_PERFORMED`** — estimating frames from size
alone would require assuming the ttbin record format, and no byte of any raw file was read.

**Q5 — Curation status vs repo (`v67_manifest.json`, `v71_data_registry.json`, `pairs/` dirs)?**
**All 10: `NOT_REGISTERED`.** Exact-stem grep hits in `v67_manifest.json`: 0; in
`v71_data_registry.json`: 0; no `pairs/` dir exists for any new stem in this checkout
(the v55 `pairs/` root itself is absent here). Two non-registry repo references exist
(project files, not data results, so reading them was permitted):
- `scripts/v65a_scout.py` + `docs/research_cycles/V65AR1/v65a_registry_stage0.json` +
  `openspec/changes/formal-ir-v65a-alternative-typeii-working-point-scout/` reference
  `SHG_Type2PPLN_3s_2_2026-01-13_162148` as decoder-free scout candidate #1 (exploratory only —
  NOT a registration, NOT a pairs entry).
- `experiments/run_golden_sweep_four_datasets.py` (lines 22–25) lists the four Type0 directory
  stems as sweep inputs under a different root prefix (`D:\Data\2026.1.20\…`; also not a registry).

## 4. Explicitly NOT determined (needs parsing / PI / follow-up — none performed here)

- Frame/pair counts per acquisition (`REQUIRES_PARSING_NOT_PERFORMED`).
- ttbin record/header semantics; meaning of the tiny primary vs bulk `.1` split.
- Whether `SHG_Type2PPLN` / `Type2` acquisitions are Type-II SPDC and ToA-pipeline-compatible.
- Whether `Type0_nofilter` data is pipeline-usable: RESOLVED by PI RULING
  2026-09-21 — Type0/SHG are source-only differences, no IR effect, all 10
  acquisitions in scope (supersedes `TYPE0_SOURCE_UNVERIFIED_NEEDS_PI_CONFIRMATION`).
- Loss setting: no `_0dB`-style token appears in any of the 10 new names.
- Contents/validity of every untrusted artifact listed (never opened, never used).

## 5. Blockers

None. All 13 supplied locations exist and were stat-able; no permission errors.
(No checksums computed — files are tens of MB; size+mtime recorded instead, per brief.)
