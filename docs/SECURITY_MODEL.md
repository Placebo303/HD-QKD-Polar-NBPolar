# Security Model: Finite-Key Security Accounting

## Overview

This document describes the finite-key security accounting methodology used in the HD-QKD Polar pipeline. The security model is based on the layered secure PIE (Photon Information Efficiency) framework.

## Key Concepts

### Photon Information Efficiency (PIE)

PIE measures the amount of secure key information extracted per detected photon coincidence:

$$\text{PIE} = \frac{\text{Secure Key Bits}}{\text{Total Coincidences}}$$

### Secure Key Rate (SKR)

SKR is the rate of secure key generation:

$$\text{SKR} = \frac{\text{Secure Key Bits}}{\text{Acquisition Time (seconds)}}$$

### Layered Secure PIE

The total secure PIE is composed of multiple layers:

$$\text{PIE}_{\text{total}} = \text{PIE}_{\text{time-bin}} + \text{PIE}_{\text{polarization}}$$

where:
- **Time-bin layer**: High-dimensional arrival-time encoding
- **Polarization layer**: Additional binary key register (BBM92-type)

## Security Framework

### Finite-Key Regime

In practical QKD systems, the key length is finite. The finite-key security framework accounts for:

1. **Statistical fluctuations**: Due to finite sample size
2. **Privacy amplification**: Reducing Eve's information
3. **Error correction**: Information leakage during reconciliation

### Security Parameters

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| $\epsilon_{\text{sec}}$ | Security parameter | $10^{-10}$ |
| $\epsilon_{\text{corr}}$ | Correctness parameter | $10^{-10}$ |
| $\epsilon_{\text{EC}}$ | Error correction bound | $10^{-10}$ |

### Zhong-like Security Aggregation

The pipeline implements a Zhong-like security aggregation:

1. **Frame synchronization**: Align time-bin frames
2. **Polar encoding**: Encode key bits using Polar codes
3. **Information reconciliation**: Correct errors between Alice and Bob
4. **Privacy amplification**: Remove Eve's information

## PIE Calculation

### Time-bin PIE

For time-bin encoding with $d$ dimensions:

$$\text{PIE}_{\text{time-bin}} = \log_2(d) - H_{\text{leakage}} - \Delta_{\text{finite-key}}$$

where:
- $\log_2(d)$: Raw information per coincidence
- $H_{\text{leakage}}$: Information leakage during error correction
- $\Delta_{\text{finite-key}}$: Finite-key correction term

### Polarization PIE

For polarization encoding (binary):

$$\text{PIE}_{\text{polarization}} = 1 - H(e) - \Delta_{\text{finite-key}}$$

where:
- $H(e)$: Binary entropy of error rate $e$
- $\Delta_{\text{finite-key}}$: Finite-key correction term

## Security Accounting Modes

### Primary Reporting Mode

The primary reporting mode is `actual_ir_finite_key`:

```
PRIMARY_REPORTING_MODE = actual_ir_finite_key
default main result columns: PIE_main, SKR_main_bps
default main result source: PIE_secure_actual_ir, SKR_secure_actual_ir_bps
```

### Diagnostic Mode

Diagnostic performance proxies:
- `PIE_practical`: Practical PIE without finite-key corrections
- `SKR_measured_bps`: Measured SKR without security guarantees

## References

1. Zhong, T., et al. (2015). Photon-efficient quantum key distribution using time-energy entanglement with high-dimensional encoding. *New Journal of Physics*, 17(2), 022002.

2. Niu, M. Y., et al. (2018). Quantum key distribution with high-dimensional encoding. *Physical Review A*, 98(3), 032314.

3. Xu, F., et al. (2020). Secure quantum key distribution with realistic devices. *Reviews of Modern Physics*, 92(2), 025002.

## NB-Polar M2 CAL / prior accounting (CANDIDATE, descriptive)

This note is descriptive bookkeeping for the NB-Polar M2 ±1 parametric
prior validation track. It changes no claim in this document.

- **M2 is a CANDIDATE, never the baseline.** The incumbent as-deployed
  reference is the M0 raw-MLE table at its own 1024-frame CAL. M2 results
  (if any) are reported against matched-CAL controls and never promote
  M2 by themselves.
- **The 32-frame CAL is SACRIFICED.** M2 fits its per-session triple on
  exactly 32 sacrificed frames (8192 symbols) per session. Sacrificed
  frames are excluded from the key denominator: no key bit is drawn from
  frames that estimated the prior.
- **Reveal bits are diagnostic-only.** The ~18–22 bits
  (params·log2(n) order-of-magnitude parameter-counting diagnostic) are
  reported for scale only and never enter leakage bookkeeping as a
  fitted term.
- **No λ_prior term enters λ_total.** The security aggregation used for
  reporting admits no prior-estimation λ term; the CAL mechanism above
  (sacrifice + exclusion) is the accounting, not a λ addition.
- **Claim scope unchanged.** This note adds no composable net-key claim.
  Any future key claim needs its own freeze with independent review.

### Public-message inventory skeleton (M2 track, 0-bit shape)

Shape pattern: the Release fail-closed exhaustive public-message list
(`docs/nbpolar/MACRO_PLAN_20260921.md` §9 F3) — every public message
listed with producer, key-dependence, size, and seed/mask/code. Rows
below are the skeleton at 0 bits; a later freeze fills values.

| message | producer | key-dependence | size-bits | seed/mask/code | status |
|---|---|---|---|---|---|
| CAL frame list (32 sacrificed frames/session) | operator | excluded from key denominator | 0 | frame IDs at freeze | to-freeze |
| fitted triple (q0, q+1, q−1) per session | estimator | derived from sacrificed CAL only | 0 | CAL frame IDs | to-freeze |
| reveal bits (~18–22, diagnostic) | estimator | diagnostic-only, never λ_total | 0 | params·log2(n) order-of-magnitude | descriptive |
| P16 orders (frozen len-32768 l2_order) | construction freeze | reused, never re-derived in-packet | 0 | P16 artifact ref | frozen |
| (K1, K2) = (319, 6492) | freeze | decoded at frozen K regardless | 0 | frozen pair | frozen |
| Toeplitz tags (64-bit per block) | verifier | per-block tag from frozen TAG_MASTER | 0 | TAG_MASTER at freeze | to-freeze |
