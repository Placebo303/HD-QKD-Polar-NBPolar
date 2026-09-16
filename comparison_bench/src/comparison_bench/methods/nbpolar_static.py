"""Thin ``IRMethod`` adapter for the frozen Phase 5 static NB-Polar protocol.

Input contract (documented, no signature changes to ``FrameBatch`` /
``IRRunConfig`` / ``IRRunResult``):

- ``batch.dimension == 1024``: physical single-layer label alphabet;
- ``batch.frame_len_symbols == 256``: the frozen ``N`` (K = 45 static set);
- ``batch.alice_symbols[f, j]``: Alice truth label ``32 * x_j`` (low half
  constant zero per the single-layer synthetic convention);
- ``batch.bob_symbols[f, j]``: observed label ``32 * x_obs`` or ``-1`` at an
  erasure. The per-frame SC metric is built from this observation only:
  one-hot at the observed GF32 symbol, uniform on erased coordinates.

``IRRunResult`` mapping (documented, never a silent promotion):

- ``n_frames_success = exact`` only. A verified non-exact block is
  ``undetected`` and is **never** success (P5-A07); it stays in metadata.
- ``n_frames_failed_decode = decode_failed``, ``n_frames_failed_verify =
  verify_failed``; both stay disjoint from success and from each other.
- ``n_frames_attempted`` = executed frames; ``resource_abort`` is metadata.
- ``leak_EC_actual_bits`` = sum of key-dependent bits (disclosure + tag).
- ``beta_eff_empirical`` is derived, never hand-filled:
  ``1 - leak / (n_input_bits * H2(raw_ber))`` via the shared
  ``metrics.leakage.compute_beta_eff_empirical``.
- ``raw_ser``/``raw_ber`` are the pre-IR label error rates of the raw
  channel MAP observation; ``post_ir_ser``/``post_ir_ber`` apply decoded
  labels for exact/undetected frames and keep the raw labels for rejected
  (verify_failed) or failed (decode_failed) frames.

Synthetic/injected data only: no artifact, real-frame, DEV/EVAL, benchmark
or output-file path exists in this module.
"""

from __future__ import annotations

import time

import numpy as np

from ..formal_ir.nbpolar import protocol as protocol_mod
from ..formal_ir.nbpolar.algebra import make_gf32
from ..metrics.leakage import compute_beta_eff_empirical
from ..types import FrameBatch, IRRunConfig, IRRunResult
from .base import IRMethod

LABEL_DIMENSION = 1024
VERIFY_MODE = "toeplitz64"


def _validate_labels(values, frames: int, n: int, *, allow_erasure: bool, name: str) -> np.ndarray:
    arr = np.asarray(values)
    if arr.dtype.kind == "b" or arr.shape != (frames, n):
        raise ValueError(f"{name} must have integer shape ({frames}, {n}), got {arr.shape}")
    arr = arr.astype(np.int64)
    if allow_erasure:
        usable = arr[arr >= 0]
        if arr.min() < -1 or (usable.size and (usable.max() >= LABEL_DIMENSION or (usable % 32).any())):
            raise ValueError(
                f"{name} entries must be -1 or single-layer labels 0..1023 with low half zero"
            )
    else:
        if arr.min() < 0 or arr.max() >= LABEL_DIMENSION or (arr % 32).any():
            raise ValueError(f"{name} entries must be single-layer labels 0..1023 with low half zero")
    return arr


def _observation_metric(bob_row: np.ndarray, n: int) -> np.ndarray:
    """Bob-only metric from the raw observation; Alice truth never enters."""
    logp = np.full((n, protocol_mod.DEFAULT_Q), -np.log(protocol_mod.DEFAULT_Q))
    observed = bob_row >= 0
    if np.any(observed):
        logp[observed, :] = -np.inf
        logp[observed, bob_row[observed] // 32] = 0.0
    return logp


def unavailable_result(batch: FrameBatch, cfg: IRRunConfig, error: str) -> IRRunResult:
    return IRRunResult(
        dataset_id=batch.dataset_id,
        method="nbpolar_static",
        method_variant=cfg.method_variant,
        frame_len_symbols=int(batch.frame_len_symbols),
        frame_len_bits=int(batch.frame_len_symbols) * protocol_mod.LABEL_BITS,
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


class NBPolarStaticMethod(IRMethod):
    """Frozen static disclosure + one SC + one Toeplitz tag per frame."""

    def run(self, batch: FrameBatch, cfg: IRRunConfig) -> IRRunResult:
        if cfg.verify_mode != VERIFY_MODE:
            raise ValueError(
                f"NB-Polar static protocol requires verify_mode='{VERIFY_MODE}'; "
                f"got {cfg.verify_mode!r} (the comparison crc32 default is not this protocol)"
            )
        if int(batch.dimension) != LABEL_DIMENSION:
            raise ValueError(f"batch dimension must be {LABEL_DIMENSION}, got {batch.dimension}")
        n = int(batch.frame_len_symbols)
        if n != protocol_mod.DEFAULT_N:
            raise ValueError(
                f"Phase 5 static protocol is frozen at N={protocol_mod.DEFAULT_N}, got {n}"
            )
        frames = int(batch.alice_symbols.shape[0])
        if frames < 1:
            raise ValueError("batch must contain at least one frame")
        alice = _validate_labels(batch.alice_symbols, frames, n, allow_erasure=False, name="alice_symbols")
        bob = _validate_labels(batch.bob_symbols, frames, n, allow_erasure=True, name="bob_symbols")

        field = make_gf32()
        k = protocol_mod.DEFAULT_K
        start = time.perf_counter()
        totals = {name: 0 for name in protocol_mod.OUTCOMES}
        key_dependent = 0
        public_control = 0
        pre_symbol_errors = 0
        pre_bit_errors = 0
        post_symbol_errors = 0
        post_bit_errors = 0
        error_types: dict[str, int] = {}

        for frame_index in range(frames):
            result = protocol_mod.run_static_block(
                frame_index,
                alice[frame_index] // protocol_mod.LABEL_SCALE,
                _observation_metric(bob[frame_index], n),
                field=field,
                n=n,
                k=k,
            )
            totals[result.outcome] += 1
            key_dependent += int(result.key_dependent_bits)
            public_control += int(result.public_control_bits)
            pre_symbol_errors += int(result.pre_symbol_errors)
            pre_bit_errors += int(result.pre_bit_errors)
            corrected = result.outcome in ("exact", "undetected")
            post_symbol_errors += int(result.symbol_errors if corrected else result.pre_symbol_errors)
            post_bit_errors += int(result.bit_errors if corrected else result.pre_bit_errors)
            if result.error_type:
                error_types[result.error_type] = error_types.get(result.error_type, 0) + 1
        runtime_s = time.perf_counter() - start

        attempted = frames - totals["resource_abort"]
        n_input_bits = frames * n * protocol_mod.LABEL_BITS
        raw_ser = pre_symbol_errors / (frames * n)
        raw_ber = pre_bit_errors / n_input_bits
        post_ser = post_symbol_errors / (frames * n)
        post_ber = post_bit_errors / n_input_bits
        leak = float(key_dependent)
        verified_union = totals["exact"] + totals["undetected"]
        return IRRunResult(
            dataset_id=batch.dataset_id,
            method="nbpolar_static",
            method_variant=cfg.method_variant,
            frame_len_symbols=n,
            frame_len_bits=n * protocol_mod.LABEL_BITS,
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
                (totals["exact"] * n * protocol_mod.LABEL_BITS) / runtime_s
            )
            if runtime_s > 0
            else 0.0,
            metadata={
                "method_status": "ok",
                "backend_status": "nbpolar_static_protocol_synthetic",
                "notes": (
                    "static synthetic Phase 5 protocol; success=exact only; "
                    "verified non-exact is undetected and never success"
                ),
                "outcome_totals": {name: int(totals[name]) for name in protocol_mod.OUTCOMES},
                "verified_union": int(verified_union),
                "verification_invocations": int(
                    totals["exact"] + totals["undetected"] + totals["verify_failed"]
                ),
                "public_control_bits_total": int(public_control),
                "key_dependent_bits_total": int(key_dependent),
                "disclosure_coordinates": [
                    int(v) for v in protocol_mod.static_disclosure_coordinates(n, k)
                ],
                "ser_ber_definition": (
                    "pre = raw channel MAP labels; post = decoded labels for exact/undetected, "
                    "raw labels kept for verify_failed/decode_failed frames"
                ),
                "beta_eff_formula": "1 - leak_EC_actual_bits / (n_input_bits * H2(raw_ber))",
                "decode_error_types": error_types,
                "verify_mode": VERIFY_MODE,
            },
        )
