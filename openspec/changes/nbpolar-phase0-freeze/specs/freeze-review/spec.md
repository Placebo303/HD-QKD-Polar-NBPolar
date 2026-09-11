# Delta spec: freeze-review gate

## Requirement: granularity (doc-only slice)

The change SHALL be a doc-only freeze-review of the `formal-ir-nbpolar-mvp` Phase0 packet slice. It SHALL create no `.py`, load no Model-F/CAL/real data, execute no decoder, create no result root, and duplicate no MVP Phase1/2 implementation task. Any code/Model-F/decoder/real-data clause SHALL be stripped as scope creep before Freeze ACCEPT.

## Requirement: literature disposition

ARCHITECTURE mathematical references SHALL resolve the Park-Barg zero-hit blocker exactly one way for this freeze: state count 3→2 with an explicit non-dependency sentence (Mori-Tanaka = kernel condition; Bravo-Santos = source polarization/SC; Park-Barg not a Phase0 dependency). A Park-Barg citation SHALL NOT be invented without a read source + use statement.

## Requirement: path discipline

Normative NB-Polar paths SHALL be relative POSIX (`comparison_bench/...`, `docs/...`, `openspec/...`). Windows absolute paths SHALL NOT appear as new defaults; sibling checkouts SHALL appear only as provenance (`../HD-QKD_Polar_Comparison`, `../HD-QKD_Polar_Release`), never as code dependencies. Pre-existing absolute hits are triaged per design.md D3 (fix-intent vs marked provenance).

## Requirement: 1e-12 reproducibility

Every `1e-12` gate SHALL mean absolute tolerance (`max|a-b| <= 1e-12`); `1e-9` likewise absolute. The internal metric SHALL be float64 natural log with `logsumexp(row)=0`; bits appear only at the entropy/disclosure report boundary. D4R2 SHALL be cited exactly as formula provenance (`build_f` at `comparison_bench/src/comparison_bench/formal_ir/v72p2d4r2_cal_gf32_model_rate_audit.py:329`: `(counts+lambda*p_global)/(n_b+lambda)`; numbers per `RESULT_SUMMARY_R2.md:21-28` — inner `selected_lam=137.3823795883264` at :21, CE means L1 3.814742/L2 3.347605/total 7.162347 at :28) and SHALL NOT be claimed as NB-Polar evidence.

## Requirement: isolation

Normative NB-Polar text SHALL contain zero reuse of: H1/H2/H_inc, PEG/QC/degree, BP/schedule/seeds, H[:k] disclosure, LDPC leakage formula, Cascade parity/bisection/look-back, binary XOR/PW/BSC-LLR/CA-SCL-CRC, polar_existing作q-ary后端禁用. Permitted occurrences are: mentions inside this ban list, `ASSET_MAP.md` §Do not reuse, and boundary/provenance prose that explicitly states non-reuse (e.g. `ARCHITECTURE.md:136,145`, `README.md:32,40,77,81`, `CRITICAL_PATH.md:30,39,41`). Any normative reuse as implementation (category (c) per `tasks.md` F0-5 triage) is forbidden. `polar_existing` SHALL NOT serve as a q-ary backend.

## Requirement: task binding and verdict

Each of the 6 tasks (F0-1..F0-6) SHALL bind frozen inputs + exact command + budget + return artifact + stop rule per `tasks.md`. Overall verdict SHALL be exactly one of `FREEZE_ACCEPT → Phase1 judgment unlocked` (all 6 PASS) or `BLOCKED(<single root cause>)`. Lifecycle flags SHALL remain false (no implementation/decoder/real-data/result authorized by this change).
