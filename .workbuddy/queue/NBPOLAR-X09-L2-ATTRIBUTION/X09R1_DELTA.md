# X09R1_DELTA.md — delta-successor for NBPOLAR-X09-L2-ATTRIBUTION (AGENTS.md §10.4 fast path)

Same-point semantic correction only. Everything not listed as changed (D1–D5)
is inherited from X09: same frozen inputs, zero protected opens, no decoder/RNG/tag,
one run, writes only in the new probe root, focused numerical review, no claims,
no factor selection, no commit/push.

## Deltas (only these)
- **D1 H1 clean margins.** Inventory every NLL/CE-ish field in the P20M 9 records;
  for each arm select the SINGLE authoritative "L2 NLL under the true/decided path"
  field (cite its writer file:line); per-record `margin_bits = capacity_bits -
  l2_nll_bits` (G1 35164, G2 33509; G0 descriptively with its own 5*6492+64=32524)
  keyed by `block_index` + arm; report margins individually — NO summing across
  fields anywhere. Also report N*H2 = 32768*0.8003665547495433 bits, the ratio,
  and (separately, labeled descriptive) any secondary NLL fields.
- **D2 block key.** Use `block_index` (fixes X09 null-block defect).
- **D3 H3 floor comparison.** Compare floor exposure on the INTERSECTION of field
  names actually present on both sides (P20M vs in-sample P20H/I/J/K records):
  per-field coverage counts (n_present per side), compare on shared fields only;
  P20M-only fields (e.g. floor_hit_rate, if one-sided) reported separately as
  one-sided context. No rule may require a field both sides lack.
- **D4 first_error_coord semantics.** Read `first_error_coordinate` in
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_order_1p5m.py`
  (≈:1399, incl. the hits computation and all call sites) and state precisely the
  index space returned (natural block symbol index vs L1/L2 decode-order position)
  with exact lines; if genuinely ambiguous, state exactly why and what single
  citation would settle it.
- **D5 H2.** Keep H2 NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS with the precise reason
  (order positions are per-block index space; per-block Bob/truth sequences are not
  persisted; the npz is a 1024×1024 cell table) and the instrumentation requirement
  (persist per-position hazard scalars / disclosed-prefix membership at decode time
  in a successor packet).

## Inherited contract (from X09, unchanged)
- Inputs: the same 16 files (P20M 5 record/plan/identity/report + npz + orders json;
  P20I/J/K/H per_block_arm_outcomes.jsonl; 5 runner .py files), each stat size/mtime_ns.
- Forbidden: any parquet/pairs content; any DEV/VAL/HOLD/1M/V25-counts/2M open, stat,
  or listing in any form; decoder/RNG/tag calls; writes outside the new probe root
  (+ this packet dir for packet docs); commit/push.
- Command shape (exact, once; execution-error rerun allowed and recorded):
  `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && timeout 120
  /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python
  workspace/probes/nbpolar_x09_l2_attribution_r1/body.py`
- results.json schema: probe_id, tier "X", complete status, question, delta_ref,
  prereg_sha256, body_sha256, body_sha_match, artifact_inventory
  (path/size/mtime_ns + protected_opens_attempted:false), d1 (field inventory,
  authoritative selection + citations, per-record margins, budget arithmetic),
  d2 note, d3 (shared-field list, coverage, comparison), d4 (function source,
  call sites, index-space statement), d5 (reason + requirement), hypothesis_table,
  next_packet_requirements, command, interpreter, wall_s, rss_bytes, decoder_calls 0,
  rng_calls 0, tag_calls 0, writes, notes. results.json is the ONLY file body.py writes.
- Stop: missing/absent file, unreadable JSON/JSONL, npz key-set surprise, nonfinite
  → STOP results.json, no repair. Review: focused numerical (commands, completeness,
  arithmetic, write-scope); descriptive support labels only, no verdict on the next
  scientific factor.
