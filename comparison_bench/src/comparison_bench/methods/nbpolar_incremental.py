"""Thin ``IRMethod`` adapter for the frozen Phase 6 fixed incremental protocol.

Input contract (documented, no signature changes to ``FrameBatch`` /
``IRRunConfig`` / ``IRRunResult``):

- ``batch.dimension == 1024``: physical single-layer label alphabet;
- ``batch.frame_len_symbols == 256``: the frozen ``N``;
- ``batch.alice_symbols[f, j]``: Alice truth label ``32 * x_j`` (low half
  constant zero per the single-layer synthetic convention);
- ``batch.bob_symbols[f, j]``: observed label ``32 * x_obs`` or ``-1`` at an
  erasure. The per-frame metric is built from this observation only: one-hot
  at the observed GF32 symbol, uniform on erased coordinates.

``IRRunResult`` mapping (documented, never a silent promotion):

- ``n_frames_success = exact`` only. A verified non-exact block is
  ``undetected`` and is **never** success; it stays in metadata.
- ``n_frames_failed_decode = decode_failed``, ``n_frames_failed_verify =
  verify_failed``; both stay disjoint from success and from each other.
- ``leak_EC_actual_bits`` = sum of key-dependent bits (nested disclosures plus
  tag invocations, including the fail-closed partial disclosure of a
  ``decode_failed`` block).
- ``beta_eff_empirical`` is derived, never hand-filled:
  ``1 - leak / (n_input_bits * H2(raw_ber))`` via the shared
  ``metrics.leakage.compute_beta_eff_empirical``.
- ``raw_ser``/``raw_ber`` are the pre-IR label error rates of the raw channel
  MAP observation; ``post_ir_ser``/``post_ir_ber`` apply decoded labels for
  exact/undetected frames and keep the raw labels for rejected or failed
  frames.
- Metadata reports the tag-invocation, feedback-control and public seed
  accounting split; the verification union bound is **not** claimed here.

The Phase 6-R1 variant (:class:`NBPolarIncrementalR1Method`) keeps the same
input contract and ``IRRunResult`` mapping but runs the decode-reject-advance
block semantics (non-final ``ImpossibleDisclosedValueError`` advances after
one public feedback request; no candidate and no tag at the rejected level;
final K=45 stays ``decode_failed``). Signatures of ``FrameBatch`` /
``IRRunConfig`` / ``IRRunResult`` are untouched, and the strict-stop method
output is unchanged.

The label helpers and observation metric are reused unchanged from the
accepted Phase 5 adapter. Synthetic/injected data only: no stored evidence
file, real-frame, DEV/EVAL or output-file path exists in this module.
"""

from __future__ import annotations

import time

from ..formal_ir.nbpolar import incremental as incremental_mod
from ..formal_ir.nbpolar.algebra import make_gf32
from ..metrics.leakage import compute_beta_eff_empirical
from ..types import FrameBatch, IRRunConfig, IRRunResult
from .base import IRMethod
from .nbpolar_static import _observation_metric, _validate_labels

LABEL_DIMENSION = 1024
VERIFY_MODE = "toeplitz64"


def unavailable_result(batch: FrameBatch, cfg: IRRunConfig, error: str) -> IRRunResult:
    return IRRunResult(
        dataset_id=batch.dataset_id,
        method="nbpolar_incremental",
        method_variant=cfg.method_variant,
        frame_len_symbols=int(batch.frame_len_symbols),
        frame_len_bits=int(batch.frame_len_symbols) * incremental_mod.LABEL_BITS,
        n_frames_total=int(batch.alice_symbols.shape[0]),
        n_frames_attempted=0,
        n_frames_success=0,
        n_frames_failed_decode=0,
        n_frames_failed_verify=0,
        raw_ser=float("nan"),
        raw_ber=float("nan"),
        post_ir_ser=float("nan"),
        post_ir_ber=float("nan"),
        leak_EC_actual_bits=0.0,
        leak_EC_per_frame=0.0,
        leak_EC_per_input_bit=0.0,
        beta_eff_empirical=float("nan"),
        runtime_s=0.0,
        throughput_input_bits_per_s=0.0,
        throughput_output_bits_per_s=0.0,
        metadata={"method_status": "unavailable", "error_message": error},
    )


class NBPolarIncrementalMethod(IRMethod):
    """Frozen nested disclosure + fresh SC per level + one tag per invoked level."""

    METHOD_NAME = "nbpolar_incremental"
    BACKEND_STATUS = "nbpolar_incremental_protocol_synthetic"
    NOTES = (
        "fixed nested incremental synthetic Phase 6 protocol; success=exact only; "
        "verified non-exact is undetected and never success"
    )

    def _run_block(self, frame_index, alice_symbols, bob_symbols, *, field, n, nested):
        return incremental_mod.run_incremental_block(
            frame_index,
            alice_symbols // incremental_mod.LABEL_SCALE,
            _observation_metric(bob_symbols, n),
            field=field,
            n=n,
            nested=nested,
        )

    def _extra_metadata(self, *, rejected_counts, terminating_counts, levels) -> dict:
        """R1-only metadata hook; the strict-stop method adds nothing."""
        return {}

    def run(self, batch: FrameBatch, cfg: IRRunConfig) -> IRRunResult:
        if cfg.verify_mode != VERIFY_MODE:
            raise ValueError(
                f"NB-Polar incremental protocol requires verify_mode='{VERIFY_MODE}'; "
                f"got {cfg.verify_mode!r} (the comparison crc32 default is not this protocol)"
            )
        if int(batch.dimension) != LABEL_DIMENSION:
            raise ValueError(f"batch dimension must be {LABEL_DIMENSION}, got {batch.dimension}")
        n = int(batch.frame_len_symbols)
        if n != incremental_mod.DEFAULT_N:
            raise ValueError(
                f"Phase 6 incremental protocol is frozen at N={incremental_mod.DEFAULT_N}, got {n}"
            )
        frames = int(batch.alice_symbols.shape[0])
        if frames < 1:
            raise ValueError("batch must contain at least one frame")
        alice = _validate_labels(batch.alice_symbols, frames, n, allow_erasure=False, name="alice_symbols")
        bob = _validate_labels(batch.bob_symbols, frames, n, allow_erasure=True, name="bob_symbols")

        field = make_gf32()
        nested = incremental_mod.build_nested_schedule(n=n)
        start = time.perf_counter()
        totals = {name: 0 for name in incremental_mod.OUTCOMES}
        accepted_histogram = {str(level): 0 for level in range(len(nested.sizes))}
        rejected_counts: dict[str, int] = {}
        terminating_counts: dict[str, int] = {}
        rejected_total = 0
        key_dependent = 0
        public_seed = 0
        feedback_bits = 0
        tag_invocations = 0
        feedback_invocations = 0
        pre_symbol_errors = 0
        pre_bit_errors = 0
        post_symbol_errors = 0
        post_bit_errors = 0
        error_types: dict[str, int] = {}

        for frame_index in range(frames):
            result = self._run_block(
                frame_index, alice[frame_index], bob[frame_index], field=field, n=n, nested=nested
            )
            totals[result.outcome] += 1
            if result.accepted_level >= 0:
                accepted_histogram[str(result.accepted_level)] += 1
            for level in result.rejected_levels:
                rejected_counts[str(int(level))] = rejected_counts.get(str(int(level)), 0) + 1
            terminating = incremental_mod.terminating_level(result, nested)
            terminating_counts[str(terminating)] = terminating_counts.get(str(terminating), 0) + 1
            rejected_total += int(result.decode_rejected_continue_count)
            key_dependent += int(result.key_dependent_bits)
            public_seed += int(result.public_seed_bits)
            feedback_bits += int(result.feedback_control_bits)
            tag_invocations += int(result.tag_invocations)
            feedback_invocations += int(result.feedback_control_invocations)
            pre_symbol_errors += int(result.pre_symbol_errors)
            pre_bit_errors += int(result.pre_bit_errors)
            corrected = result.outcome in ("exact", "undetected")
            post_symbol_errors += int(result.symbol_errors if corrected else result.pre_symbol_errors)
            post_bit_errors += int(result.bit_errors if corrected else result.pre_bit_errors)
            if result.error_type:
                error_types[result.error_type] = error_types.get(result.error_type, 0) + 1
        runtime_s = time.perf_counter() - start

        attempted = frames - totals["resource_abort"]
        n_input_bits = frames * n * incremental_mod.LABEL_BITS
        raw_ser = pre_symbol_errors / (frames * n)
        raw_ber = pre_bit_errors / n_input_bits
        post_ser = post_symbol_errors / (frames * n)
        post_ber = post_bit_errors / n_input_bits
        leak = float(key_dependent)
        verified_union = totals["exact"] + totals["undetected"]
        metadata = {
            "method_status": "ok",
            "backend_status": self.BACKEND_STATUS,
            "notes": self.NOTES,
            "outcome_totals": {name: int(totals[name]) for name in incremental_mod.OUTCOMES},
            "verified_union": int(verified_union),
            "verification_invocations": int(tag_invocations),
            "feedback_control_invocations": int(feedback_invocations),
            "feedback_control_bits": int(feedback_bits),
            "public_seed_bits_total": int(public_seed),
            "public_control_bits_total": int(public_seed + feedback_bits),
            "key_dependent_bits_total": int(key_dependent),
            "schedule_sizes": [int(v) for v in incremental_mod.FROZEN_K],
            "accepted_level_histogram": accepted_histogram,
            "ser_ber_definition": (
                "pre = raw channel MAP labels; post = decoded labels for exact/undetected, "
                "raw labels kept for verify_failed/decode_failed frames"
            ),
            "beta_eff_formula": "1 - leak_EC_actual_bits / (n_input_bits * H2(raw_ber))",
            "decode_error_types": error_types,
            "verify_mode": VERIFY_MODE,
        }
        metadata.update(
            self._extra_metadata(
                rejected_counts=rejected_counts,
                terminating_counts=terminating_counts,
                levels=len(nested.sizes),
            )
        )
        return IRRunResult(
            dataset_id=batch.dataset_id,
            method=self.METHOD_NAME,
            method_variant=cfg.method_variant,
            frame_len_symbols=n,
            frame_len_bits=n * incremental_mod.LABEL_BITS,
            n_frames_total=frames,
            n_frames_attempted=attempted,
            n_frames_success=totals["exact"],
            n_frames_failed_decode=totals["decode_failed"],
            n_frames_failed_verify=totals["verify_failed"],
            raw_ser=raw_ser,
            raw_ber=raw_ber,
            post_ir_ser=post_ser,
            post_ir_ber=post_ber,
            leak_EC_actual_bits=leak,
            leak_EC_per_frame=(leak / attempted) if attempted else float("nan"),
            leak_EC_per_input_bit=leak / n_input_bits,
            beta_eff_empirical=compute_beta_eff_empirical(leak, n_input_bits, raw_ber),
            runtime_s=runtime_s,
            throughput_input_bits_per_s=(n_input_bits / runtime_s) if runtime_s > 0 else 0.0,
            throughput_output_bits_per_s=(
                (totals["exact"] * n * incremental_mod.LABEL_BITS) / runtime_s
            )
            if runtime_s > 0
            else 0.0,
            metadata=metadata,
        )


class NBPolarIncrementalR1Method(NBPolarIncrementalMethod):
    """Phase 6-R1 decode-reject-advance variant of the same ``IRMethod`` contract.

    Non-final ``ImpossibleDisclosedValueError`` advances after one public
    feedback request with no candidate and no tag; the final K=45 error stays
    ``decode_failed``. ``n_frames_success`` is still ``exact`` only; rejections
    are never success and never a result bucket.
    """

    METHOD_NAME = "nbpolar_incremental_r1"
    BACKEND_STATUS = "nbpolar_incremental_r1_protocol_synthetic"
    NOTES = (
        "decode-reject-advance synthetic Phase 6-R1 protocol; success=exact only; "
        "a non-final impossible disclosed value advances with one public feedback request "
        "and no tag; verified non-exact is undetected and never success"
    )

    def _run_block(self, frame_index, alice_symbols, bob_symbols, *, field, n, nested):
        return incremental_mod.run_incremental_r1_block(
            frame_index,
            alice_symbols // incremental_mod.LABEL_SCALE,
            _observation_metric(bob_symbols, n),
            field=field,
            n=n,
            nested=nested,
        )

    def _extra_metadata(self, *, rejected_counts, terminating_counts, levels) -> dict:
        return {
            "decode_rejected_continue_count": int(sum(rejected_counts.values())),
            "rejected_level_histogram": {
                str(level): int(rejected_counts.get(str(level), 0)) for level in range(levels - 1)
            },
            "terminating_level_histogram": {
                str(level): int(terminating_counts.get(str(level), 0))
                for level in range(-1, levels)
            },
        }
