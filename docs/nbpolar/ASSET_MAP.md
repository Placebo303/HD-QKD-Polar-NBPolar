# Three-project asset map

## Direct reuse

| Asset | Source | Reuse contract |
|---|---|---|
| GF arithmetic | `Comparison/comparison_bench/src/comparison_bench/formal_ir/nonbinary_field.py` (`FieldSpec`, `GF2mField`) | Reuse arithmetic and GF32 polynomial 37; add a Polar-neutral spec wrapper so NB-LDPC method metadata is not the Polar identity. |
| Empirical counts | `Comparison/.../v72p2d5_model_f_input.py` (`counts_ab`, `p_b`) | Preserve `counts_ab[A,B]` shape `(1024,1024)`, CAL frame range, and axis declaration. |
| Model-F concentration estimate | `Comparison/.../v72p2d4r2_cal_gf32_model_rate_audit.py` (`build_f`) | Use `(counts + lambda*p_global)/(n_b+lambda)`; do not call the older cell-wise pseudocount function for new evidence. |
| Frame and result types | `comparison_bench/src/comparison_bench/types.py`, `methods/base.py` | Keep `FrameBatch`, `IRRunConfig`, `IRRunResult`, and `IRMethod.run` signatures stable; add NB-Polar-specific data in a separate result payload. |
| Dataset framing | `comparison_bench/src/comparison_bench/io/dataset_builder.py` | Reuse column normalization and frame grouping; pass priors explicitly rather than hiding them in metadata. |
| Verification primitives | `Comparison/.../formal_ir/shared.py` (`toeplitz_tag`, `verification_result`, `canonical_event`) | Reuse after freezing q-ary symbol-to-bit packing and verification invocation accounting. |
| Binary protocol evidence | `Release/src/reconciliation/verification.py`, `pipelines/current/round1b_run_actual_ir_replay.py` | Reuse final-tag and public/key-dependent accounting ideas, not the binary decoder. |
| Independent decoder diagnostics | `Comparison/.../v72p2d7_gf32_decoder_certification.py` and D7-B/C harnesses | Reuse independent enumeration, hard/soft separation, provenance, and failure precedence. |

## Reuse only after refactoring

| Area | Existing limitation | Required NB-Polar change |
|---|---|---|
| Prior adapter | Model-F has several historical smoothing and axis contracts | Expose `P(A|B)`, `P(A|B,context)`, floor, smoothing policy, symbol order, and provenance as explicit fields. |
| Decoder result | NB-LDPC `final_beliefs` can be `PRIOR_ONLY`; hard output is not APP | Return `channel_metric`, `posterior_metric` only when justified, `hard_decision`, constraint state, and `metric_provenance`. |
| Disclosure | LDPC uses check rows and Cascade uses binary parity events | Count disclosed GF32 coordinates at 5 bits each; keep public control and 64-bit tag separate. |
| Benchmark method | `IRRunConfig.verify_mode` defaults to comparison CRC32 | Create an NB-Polar config with explicit decoder, construction, prior, and verification modes. |
| Release replay | Assumes binary `mask_u8`, BSC/asymmetric LLR, and binary PW order | Keep the protocol skeleton only; replace bit-plane mask/metric with q-ary symbol coordinates. |
| Sidecar metric | `chan_ll_table[b,a]` is row-max log metric from strict TTBin, not CAL-only | Convert with an explicit adapter and freeze CAL/DEV/EVAL provenance before construction or evaluation. |

## Ideas only

- D5's `U1/U2` entropy chain and D7's paired marginal/oracle diagnostic.
- Binary MLC's error-propagation and conditional-entropy diagnostics.
- Release C++ SCL path-state and contiguous batch validation patterns.
- Cascade's fail-fast configuration, transcript event, and final verification
  accounting.

## Do not reuse

- NB-LDPC `H1/H2/H_inc`, PEG/QC/degree topology, GF32 coefficients, BP
  messages, row schedules, graph seeds, `H[:k]` disclosure, and LDPC row-count
  leakage formulas.
- Cascade parity/bisection/look-back state machine, `passes`, and `q_handling`.
- Release binary XOR transform, fixed PW order, binary BSC LLR, CA-SCL CRC
  selection, or `polar_existing` as a q-ary backend.
- Truth-centered D7 priors as performance data.
- Any historical V54/V64, V37, V7/V9/V10/V11, D5, D6, or D7 result as an
  NB-Polar result.

## Ownership and archive rule

The archived Comparison draft `formal-ir-future-nbpolar-app-transfer` is kept
for provenance only. It required an accepted NB-LDPC/V62 dependency and began
with a hybrid APP transfer. The independent GF32 SC path in this worktree
supersedes that entry order. The Release checkout keeps its historical
research-line documents untouched as crosstalk provenance, per its AGENTS.md.

