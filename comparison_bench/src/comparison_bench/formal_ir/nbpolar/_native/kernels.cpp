// Native (C++) SC/SCL log-domain kernels for the NB-Polar GF(32) decoder.
//
// Authorization: PI ruling 2026-09-29 ("选 B, 可以装一个cargo然后测c++和rust"),
// this session (coder-fast). Equivalence standard B: decisions must agree with
// the frozen sc.py/scl.py reference everywhere except exact-metric ties
// (relative score gap <= 1e-9), and the FER distribution on synthetic data
// must match; bit-identical rounding of every intermediate float is NOT
// required. This module therefore uses a mathematically different but
// equivalent algorithm from sc.py's sequential logaddexp fold:
//
//   sc._minus_block computes, for each row r and output symbol a,
//       out[r,a] = logsumexp_v( first[r, index[a,v]] + second[r,v] )
//   where index[u,v] = u XOR mul_row[v] (mul_row[v] = field.mul(alpha, v)).
//   Because GF(32) addition is bitwise XOR on 5-bit integers (see
//   nonbinary_field.GF2mField.add) and multiplication by a fixed nonzero
//   field element is GF(2)-linear, mul_row is a linear bijection of (Z/2)^5.
//   Substituting w = mul_row[v] gives a genuine XOR-convolution
//       out[r,a] = logsumexp_w( first[r, a XOR w] + second'[r,w] ),
//       second'[r,w] = second[r, mul_row_inv[w]].
//   It is evaluated in the linear domain (exp with per-operand max shift,
//   direct 32x32 sum of positive terms, log back), with an exact log-domain
//   per-entry fallback when the linear value is < 1e-250. Exact -inf
//   (exact-zero support) is preserved: exp(-inf)=0, and the fallback returns
//   -inf iff no pair has both operands finite. See minus_row() for why the
//   Walsh-Hadamard transform was tried and rejected (absolute round-off).
//
// sc._plus_block has no logsumexp (it is a single gather + add); it is
// reimplemented here unchanged in structure, just without the GF2mField
// Python-object call overhead.
//
// No fastmath: this file assumes IEEE-754 semantics for +-inf/NaN
// throughout (per PI ruling, "-inf 的语义必须保持: 不得使用 fastmath 之类会
// 假设没有 inf/NaN 的优化"). Do not add -ffast-math to the build.
//
// Zero third-party dependencies. OpenMP (via libgomp, shipped with g++) is
// used for row-level parallelism if the compiler enables -fopenmp; the code
// compiles and runs correctly single-threaded without it.

#include <cstdint>
#include <cstring>
#include <cmath>
#include <limits>

#if defined(_OPENMP)
#include <omp.h>
#endif

extern "C" {

// Row-stable logsumexp normalization matching sc.py::_normalize_rows
// semantics (subtract logsumexp from finite rows; leave all -inf rows as
// -inf). Uses the max-trick (explicitly permitted under equivalence
// standard B), not the sequential np.logaddexp.reduce fold.
static inline void normalize_row(double* row, int64_t q) {
    double m = -std::numeric_limits<double>::infinity();
    for (int64_t a = 0; a < q; ++a) {
        if (row[a] > m) m = row[a];
    }
    if (!std::isfinite(m)) {
        // all -inf (or NaN, which should not occur): leave row untouched.
        return;
    }
    double s = 0.0;
    for (int64_t a = 0; a < q; ++a) {
        s += std::exp(row[a] - m);
    }
    double lse = m + std::log(s);
    for (int64_t a = 0; a < q; ++a) {
        row[a] -= lse;
    }
}

// One row of the minus (check-node) kernel. Linear-domain direct XOR
// convolution with per-operand max shifts, plus an exact log-domain fallback
// for entries whose linear value is too small to trust.
//
// History (do not "optimize" back without re-reading this): a first version
// used the Walsh-Hadamard transform (O(q log q)). It is mathematically the
// same convolution but has ABSOLUTE round-off ~1e-16 * max(conv), so every
// output entry below ~1e-12 of the row peak was noise or clamped to 0 (=> a
// false -inf). NB-Polar rows are extremely peaked (1e-15 table floor), and a
// false -inf at a disclosed coordinate kills live SCL paths
// (ImpossibleDisclosedValueError observed on the G1R2-matched channel at
// N=256). The direct sum has all-positive terms, hence full RELATIVE accuracy
// for every entry; cost is 1024 multiply-adds/row but no transcendental beyond
// the 2q exp + q log calls the WHT version also needed, so it is not slower
// in practice (see Phase A table in the handoff).
static inline void minus_row(const double* frow, const double* srow,
                             const int64_t* cv_inv, int64_t q, double* orow) {
    const double NEG_INF = -std::numeric_limits<double>::infinity();
    double ls[1024];
    double mA = NEG_INF, mB = NEG_INF;
    for (int64_t w = 0; w < q; ++w) {
        ls[w] = srow[cv_inv[w]];
        if (frow[w] > mA) mA = frow[w];
        if (ls[w] > mB) mB = ls[w];
    }
    if (!std::isfinite(mA) || !std::isfinite(mB)) {
        for (int64_t a = 0; a < q; ++a) orow[a] = NEG_INF;
        return;
    }
    double P[1024], S[1024];
    for (int64_t w = 0; w < q; ++w) {
        P[w] = std::exp(frow[w] - mA);   // exp(-inf) == 0 exactly
        S[w] = std::exp(ls[w] - mB);
    }
    const double shift = mA + mB;
    for (int64_t a = 0; a < q; ++a) {
        double acc = 0.0;
        for (int64_t w = 0; w < q; ++w) acc += P[a ^ w] * S[w];
        if (acc >= 1e-250) {
            orow[a] = std::log(acc) + shift;
        } else {
            // exact log-domain fallback (per entry, max-trick); -inf iff no
            // pair (a^w, w) has both operands finite.
            double m = NEG_INF;
            for (int64_t w = 0; w < q; ++w) {
                double t = frow[a ^ w] + ls[w];
                if (t > m) m = t;
            }
            if (m == NEG_INF) { orow[a] = NEG_INF; continue; }
            double sum = 0.0;
            for (int64_t w = 0; w < q; ++w) sum += std::exp(frow[a ^ w] + ls[w] - m);
            orow[a] = m + std::log(sum);
        }
    }
}

// out[r,a] = normalize_a( logsumexp_v( first[r, a ^ cv[v]] + second[r,v] ) )
// cv[v] = field.mul(alpha_scaled, v) (length q, GF(2)-linear bijection).
// cv_inv is its inverse permutation (cv_inv[cv[v]] == v).
void nbpolar_minus_block_f64(
    const double* first, const double* second,
    int64_t rows, int64_t q,
    const int64_t* cv, const int64_t* cv_inv,
    double* out
) {
    (void)cv;
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static)
#endif
    for (int64_t r = 0; r < rows; ++r) {
        minus_row(first + r * q, second + r * q, cv_inv, q, out + r * q);
        normalize_row(out + r * q, q);
    }
}

// out[r,a] = normalize_a( first[r, beta[r] ^ cv[a]] + second[r,a] )
void nbpolar_plus_block_f64(
    const double* first, const double* second,
    const int64_t* beta,
    int64_t rows, int64_t q,
    const int64_t* cv,
    double* out
) {
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static)
#endif
    for (int64_t r = 0; r < rows; ++r) {
        const double* frow = first + r * q;
        const double* srow = second + r * q;
        double* orow = out + r * q;
        int64_t b = beta[r];
        for (int64_t a = 0; a < q; ++a) {
            orow[a] = frow[b ^ cv[a]] + srow[a];
        }
        normalize_row(orow, q);
    }
}

// Frozen-order polar_transform butterfly: u0 = u0 ^ mul_row[u1] (in place
// over the natural-order recursive structure), matching transform.py's
// exact loop order. u (length n, n a power of two) holds symbols in
// 0..q-1 as int64; mul_row[v] = field.mul(alpha, v).
void nbpolar_polar_transform_f64(
    int64_t* u, int64_t n, int64_t q, const int64_t* mul_row
) {
    (void)q; // kept for symmetry with the Rust cdylib signature (bounds-checked there)
    // Mirrors transform.py::polar_transform exactly: size starts at 1 and
    // doubles up to n (NOT n halving down to 1); only the "u0" slot is
    // overwritten in place, the "u1" slot (out[base+j+size]) is untouched,
    // matching field.add(u1, 0) == u1.
    for (int64_t size = 1; size < n; size *= 2) {
        int64_t step = 2 * size;
        for (int64_t base = 0; base < n; base += step) {
            for (int64_t j = 0; j < size; ++j) {
                int64_t u0 = u[base + j];
                int64_t u1 = u[base + j + size];
                u[base + j] = u0 ^ mul_row[u1];
            }
        }
    }
}

// Batched polar_transform: `rows` independent length-n rows in `u`
// (row-major contiguous). Mirrors nbpolar_polar_transform_batch_f64 (Rust).
void nbpolar_polar_transform_batch_f64(
    int64_t* u, int64_t rows, int64_t n, int64_t q, const int64_t* mul_row
) {
    (void)q;
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static)
#endif
    for (int64_t r = 0; r < rows; ++r) {
        int64_t* row = u + r * n;
        for (int64_t size = 1; size < n; size *= 2) {
            int64_t step = 2 * size;
            for (int64_t base = 0; base < n; base += step) {
                for (int64_t j = 0; j < size; ++j) {
                    int64_t u0 = row[base + j];
                    int64_t u1 = row[base + j + size];
                    row[base + j] = u0 ^ mul_row[u1];
                }
            }
        }
    }
}

} // extern "C"
