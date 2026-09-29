//! Native (Rust) SC/SCL log-domain kernels for the NB-Polar GF(32) decoder.
//!
//! Authorization: PI ruling 2026-09-29 ("选 B, 可以装一个cargo然后测c++和rust"),
//! this session (coder-fast). Same algorithm and equivalence standard as the
//! sibling C++ kernel in `../kernels.cpp` -- see that file's header comment
//! for the full derivation (GF(32) addition == XOR on 5-bit ints, so
//! sc.py's `_minus_block` logsumexp is a genuine XOR-convolution,
//! evaluated here as a direct linear-domain sum with an exact fallback). Equivalence standard B (PI ruling): decisions must agree with
//! the frozen reference except at metric ties (relative gap <= 1e-9); bit-
//! identical rounding is not required. No fastmath-equivalent assumptions:
//! plain IEEE-754 f64 arithmetic throughout, -inf (exact-zero support) is
//! preserved exactly through exp/log round trips.
//!
//! Zero third-party crates (see Cargo.toml). Row-level parallelism uses only
//! `std::thread` + `std::thread::available_parallelism`, both in `std`.

use std::os::raw::{c_double, c_longlong};

#[inline]
fn normalize_row(row: &mut [f64]) {
    let mut m = f64::NEG_INFINITY;
    for &v in row.iter() {
        if v > m {
            m = v;
        }
    }
    if !m.is_finite() {
        return; // all -inf: leave untouched, matches sc.py::_normalize_rows
    }
    let mut s = 0.0f64;
    for &v in row.iter() {
        s += (v - m).exp();
    }
    let lse = m + s.ln();
    for v in row.iter_mut() {
        *v -= lse;
    }
}

/// One row of the minus kernel: linear-domain direct XOR convolution with
/// per-operand max shifts and an exact log-domain per-entry fallback.
/// (A Walsh-Hadamard version was tried first and rejected: absolute round-off
/// ~1e-16*max turned tiny-but-finite entries into false -inf; see the header
/// comment of ../kernels.cpp `minus_row`.)
fn minus_row(frow: &[f64], srow: &[f64], cv_inv: &[i64], orow: &mut [f64], ls: &mut [f64], p: &mut [f64], s: &mut [f64]) {
    let q = frow.len();
    let mut ma = f64::NEG_INFINITY;
    let mut mb = f64::NEG_INFINITY;
    for w in 0..q {
        ls[w] = srow[cv_inv[w] as usize];
        if frow[w] > ma {
            ma = frow[w];
        }
        if ls[w] > mb {
            mb = ls[w];
        }
    }
    if !ma.is_finite() || !mb.is_finite() {
        for v in orow.iter_mut() {
            *v = f64::NEG_INFINITY;
        }
        return;
    }
    for w in 0..q {
        p[w] = (frow[w] - ma).exp();
        s[w] = (ls[w] - mb).exp();
    }
    let shift = ma + mb;
    let mut total = 0.0f64;
    for a in 0..q {
        let mut acc = 0.0f64;
        for w in 0..q {
            acc += p[a ^ w] * s[w];
        }
        if acc >= 1e-250 {
            total += acc;
            orow[a] = acc.ln() + shift;
        } else {
            let mut m = f64::NEG_INFINITY;
            for w in 0..q {
                let t = frow[a ^ w] + ls[w];
                if t > m {
                    m = t;
                }
            }
            if m == f64::NEG_INFINITY {
                orow[a] = f64::NEG_INFINITY;
                continue;
            }
            let mut sum = 0.0f64;
            for w in 0..q {
                sum += (frow[a ^ w] + ls[w] - m).exp();
            }
            orow[a] = m + sum.ln();
        }
    }
    // Fused row normalization (logsumexp == 0). The row peak of the linear
    // convolution is >= 1 (max P = max S = 1 after the shifts), so `total`
    // is >= 1 and entries below 1e-250 (fallback path) are negligible in it.
    let lse = shift + total.ln();
    for v in orow.iter_mut() {
        *v -= lse;
    }
}

fn minus_block_range(
    first: &[f64],
    second: &[f64],
    q: usize,
    cv_inv: &[i64],
    out: &mut [f64],
    row_lo: usize,
    row_hi: usize,
) {
    let mut ls = vec![0.0f64; q];
    let mut p = vec![0.0f64; q];
    let mut s = vec![0.0f64; q];
    for r in row_lo..row_hi {
        let frow = &first[r * q..r * q + q];
        let srow = &second[r * q..r * q + q];
        let orow = &mut out[r * q..r * q + q];
        minus_row(frow, srow, cv_inv, orow, &mut ls, &mut p, &mut s); // normalizes
    }
}

fn plus_block_range(
    first: &[f64],
    second: &[f64],
    beta: &[i64],
    q: usize,
    cv: &[i64],
    out: &mut [f64],
    row_lo: usize,
    row_hi: usize,
) {
    for r in row_lo..row_hi {
        let frow = &first[r * q..r * q + q];
        let srow = &second[r * q..r * q + q];
        let orow = &mut out[r * q..r * q + q];
        let b = beta[r];
        for a in 0..q {
            orow[a] = frow[(b ^ cv[a]) as usize] + srow[a];
        }
        normalize_row(orow);
    }
}

fn split_ranges(rows: usize, n_chunks: usize) -> Vec<(usize, usize)> {
    let n_chunks = n_chunks.max(1);
    let chunk = (rows + n_chunks - 1) / n_chunks.max(1);
    let mut out = Vec::new();
    let mut lo = 0usize;
    while lo < rows {
        let hi = (lo + chunk).min(rows);
        out.push((lo, hi));
        lo = hi;
    }
    if out.is_empty() {
        out.push((0, 0));
    }
    out
}

/// out[r,a] = normalize_a( logsumexp_v( first[r, a ^ cv[v]] + second[r,v] ) )
/// via direct linear-domain XOR convolution (see minus_row). Pointers must reference `rows*q` f64/i64
/// buffers; `cv_inv` has length `q`. Safety: caller (Python ctypes) owns and
/// sizes every buffer; this function does not resize or reallocate them.
#[no_mangle]
pub extern "C" fn nbpolar_minus_block_f64(
    first: *const c_double,
    second: *const c_double,
    rows: c_longlong,
    q: c_longlong,
    _cv: *const c_longlong,
    cv_inv: *const c_longlong,
    out: *mut c_double,
) {
    let rows = rows as usize;
    let q = q as usize;
    unsafe {
        let first = std::slice::from_raw_parts(first, rows * q);
        let second = std::slice::from_raw_parts(second, rows * q);
        let cv_inv = std::slice::from_raw_parts(cv_inv, q);
        let out = std::slice::from_raw_parts_mut(out, rows * q);

        let n_threads = std::thread::available_parallelism()
            .map(|n| n.get())
            .unwrap_or(1)
            .min(rows.max(1));
        if n_threads <= 1 || rows == 0 {
            minus_block_range(first, second, q, cv_inv, out, 0, rows);
            return;
        }
        let ranges = split_ranges(rows, n_threads);
        // Split `out` into disjoint mutable row-slices, one per thread.
        let mut rest: &mut [f64] = out;
        let mut chunks: Vec<(&[f64], &[f64], &[i64], &mut [f64], usize)> = Vec::new();
        for (lo, hi) in ranges {
            let len = (hi - lo) * q;
            let (chunk_out, remainder) = rest.split_at_mut(len);
            rest = remainder;
            chunks.push((&first[lo * q..hi * q], &second[lo * q..hi * q], cv_inv, chunk_out, hi - lo));
        }
        std::thread::scope(|scope| {
            for (f, s, ci, chunk_out, n) in chunks {
                scope.spawn(move || {
                    minus_block_range(f, s, q, ci, chunk_out, 0, n);
                });
            }
        });
    }
}

/// out[r,a] = normalize_a( first[r, beta[r] ^ cv[a]] + second[r,a] )
#[no_mangle]
pub extern "C" fn nbpolar_plus_block_f64(
    first: *const c_double,
    second: *const c_double,
    beta: *const c_longlong,
    rows: c_longlong,
    q: c_longlong,
    cv: *const c_longlong,
    out: *mut c_double,
) {
    let rows = rows as usize;
    let q = q as usize;
    unsafe {
        let first = std::slice::from_raw_parts(first, rows * q);
        let second = std::slice::from_raw_parts(second, rows * q);
        let beta = std::slice::from_raw_parts(beta, rows);
        let cv = std::slice::from_raw_parts(cv, q);
        let out = std::slice::from_raw_parts_mut(out, rows * q);

        let n_threads = std::thread::available_parallelism()
            .map(|n| n.get())
            .unwrap_or(1)
            .min(rows.max(1));
        if n_threads <= 1 || rows == 0 {
            plus_block_range(first, second, beta, q, cv, out, 0, rows);
            return;
        }
        let ranges = split_ranges(rows, n_threads);
        let mut rest: &mut [f64] = out;
        let mut chunks: Vec<(&[f64], &[f64], &[i64], &[i64], &mut [f64], usize)> = Vec::new();
        for (lo, hi) in ranges {
            let len = (hi - lo) * q;
            let (chunk_out, remainder) = rest.split_at_mut(len);
            rest = remainder;
            chunks.push((&first[lo * q..hi * q], &second[lo * q..hi * q], &beta[lo..hi], cv, chunk_out, hi - lo));
        }
        std::thread::scope(|scope| {
            for (f, s, b, c, chunk_out, n) in chunks {
                scope.spawn(move || {
                    plus_block_range(f, s, b, q, c, chunk_out, 0, n);
                });
            }
        });
    }
}

fn polar_transform_one(u: &mut [i64], n: usize, mul_row: &[i64]) {
    let mut size = 1usize;
    while size < n {
        let step = 2 * size;
        let mut base = 0usize;
        while base < n {
            for j in 0..size {
                let u0 = u[base + j];
                let u1 = u[base + j + size];
                let scaled = mul_row[u1 as usize];
                u[base + j] = u0 ^ scaled;
            }
            base += step;
        }
        size *= 2;
    }
}

/// In-place frozen-order polar_transform butterfly, mirrors transform.py
/// exactly (size starts at 1, doubles up to n; only the "u0" slot is
/// overwritten). `u` has length `n`, `mul_row` has length `q`.
#[no_mangle]
pub extern "C" fn nbpolar_polar_transform_f64(
    u: *mut c_longlong,
    n: c_longlong,
    q: c_longlong,
    mul_row: *const c_longlong,
) {
    let n = n as usize;
    let q = q as usize;
    unsafe {
        let u = std::slice::from_raw_parts_mut(u, n);
        let mul_row = std::slice::from_raw_parts(mul_row, q);
        polar_transform_one(u, n, mul_row);
    }
}

/// Batched polar_transform: `rows` independent length-`n` rows in `u`
/// (row-major, contiguous), same butterfly as `nbpolar_polar_transform_f64`
/// applied to each row independently. Mirrors
/// scl_joint_fast._polar_transform_batch_fast (one call per SCL recursion
/// level across every live path, instead of one call per path).
#[no_mangle]
pub extern "C" fn nbpolar_polar_transform_batch_f64(
    u: *mut c_longlong,
    rows: c_longlong,
    n: c_longlong,
    q: c_longlong,
    mul_row: *const c_longlong,
) {
    let rows = rows as usize;
    let n = n as usize;
    let q = q as usize;
    unsafe {
        let u = std::slice::from_raw_parts_mut(u, rows * n);
        let mul_row = std::slice::from_raw_parts(mul_row, q);
        let n_threads = std::thread::available_parallelism()
            .map(|t| t.get())
            .unwrap_or(1)
            .min(rows.max(1));
        if n_threads <= 1 || rows == 0 {
            for r in 0..rows {
                polar_transform_one(&mut u[r * n..r * n + n], n, mul_row);
            }
            return;
        }
        let ranges = split_ranges(rows, n_threads);
        let mut rest: &mut [i64] = u;
        let mut chunks: Vec<(&mut [i64], usize)> = Vec::new();
        for (lo, hi) in ranges {
            let len = (hi - lo) * n;
            let (chunk, remainder) = rest.split_at_mut(len);
            rest = remainder;
            chunks.push((chunk, hi - lo));
        }
        std::thread::scope(|scope| {
            for (chunk, nrows) in chunks {
                scope.spawn(move || {
                    for r in 0..nrows {
                        polar_transform_one(&mut chunk[r * n..r * n + n], n, mul_row);
                    }
                });
            }
        });
    }
}

// ===========================================================================
// Whole-recursion list-SC decoder (frozen top_l_prune only), mirrors
// scl_joint_fast._scl_decode_fast / scl.scl_decode control flow:
//   - per-path segment-metric stack (blocks shared by Rc between children),
//   - minus/plus batched over every live path at each recursion node,
//   - leaf: candidates (path, symbol) ordered by (metric desc, symbol asc,
//     path asc), keep first `width`, disclosed coordinates forced (+0),
//   - path prefixes kept as a parent-pointer arena (append-only), so a leaf
//     costs O(depth) not O(n) per surviving path.
// Status codes in out_info[0]: 0 ok, 1 impossible disclosed value (position in
// out_info[3]), 2 numeric nonfinite / no finite support (position in
// out_info[3]).
// ===========================================================================

use std::rc::Rc;

#[derive(Clone)]
struct Blk {
    data: Rc<Vec<f64>>,
    off: usize,
}

struct PathS {
    head: u32,
    metric: f64,
    blocks: Vec<Blk>,
}

const NONE_NODE: u32 = u32::MAX;
const PAR_MIN_ROWS: usize = 1024;

struct Ctx<'a> {
    q: usize,
    width: usize,
    cv: &'a [i64],
    cv_inv: &'a [i64],
    known_mask: &'a [i8],
    known_val: &'a [i64],
    nthreads: usize,
    arena_parent: Vec<u32>,
    arena_sym: Vec<u16>,
    live: Vec<PathS>,
    pruned: i64,
    err_pos: usize,
}

fn par_rows<F>(rows: usize, q: usize, nthreads: usize, out: &mut [f64], f: F)
where
    F: Fn(usize, usize, &mut [f64]) + Sync,
{
    if nthreads <= 1 || rows < PAR_MIN_ROWS {
        f(0, rows, out);
        return;
    }
    let n_chunks = nthreads.min(rows);
    let ranges = split_ranges(rows, n_chunks);
    let mut rest: &mut [f64] = out;
    let mut chunks: Vec<(usize, usize, &mut [f64])> = Vec::new();
    for (lo, hi) in ranges {
        let (chunk, rem) = rest.split_at_mut((hi - lo) * q);
        rest = rem;
        chunks.push((lo, hi, chunk));
    }
    let fref = &f;
    std::thread::scope(|scope| {
        for (lo, hi, chunk) in chunks {
            scope.spawn(move || fref(lo, hi, chunk));
        }
    });
}

impl<'a> Ctx<'a> {
    fn decode_leaf(&mut self, position: usize) -> Result<(), i64> {
        let q = self.q;
        let p_count = self.live.len();
        if self.known_mask[position] != 0 {
            let value = self.known_val[position] as usize;
            let mut survivors: Vec<PathS> = Vec::with_capacity(p_count);
            let old = std::mem::take(&mut self.live);
            for pt in old {
                let score = pt.blocks.last().map(|b| b.data[b.off + value]).unwrap();
                if score == f64::NEG_INFINITY {
                    self.pruned += 1;
                    continue;
                }
                if !score.is_finite() {
                    self.err_pos = position;
                    return Err(2);
                }
                let node = self.arena_parent.len() as u32;
                self.arena_parent.push(pt.head);
                self.arena_sym.push(value as u16);
                survivors.push(PathS { head: node, metric: pt.metric + 0.0, blocks: pt.blocks });
            }
            if survivors.is_empty() {
                self.err_pos = position;
                return Err(1);
            }
            self.live = survivors;
            return Ok(());
        }
        // candidates: (metric, symbol, path_idx)
        let mut cands: Vec<(f64, u16, u16)> = Vec::with_capacity(p_count * q);
        for (pi, pt) in self.live.iter().enumerate() {
            let b = pt.blocks.last().unwrap();
            let row = &b.data[b.off..b.off + q];
            for (s, &score) in row.iter().enumerate() {
                if score == f64::NEG_INFINITY {
                    self.pruned += 1;
                    continue;
                }
                if !score.is_finite() {
                    self.err_pos = position;
                    return Err(2);
                }
                cands.push((pt.metric + score, s as u16, pi as u16));
            }
        }
        if cands.is_empty() {
            self.err_pos = position;
            return Err(2);
        }
        cands.sort_by(|a, b| {
            b.0.partial_cmp(&a.0)
                .unwrap()
                .then(a.1.cmp(&b.1))
                .then(a.2.cmp(&b.2))
        });
        let keep_n = self.width.min(cands.len());
        self.pruned += (cands.len() - keep_n) as i64;
        let mut survivors: Vec<PathS> = Vec::with_capacity(keep_n);
        for &(m, s, pi) in cands.iter().take(keep_n) {
            let parent = &self.live[pi as usize];
            let node = self.arena_parent.len() as u32;
            self.arena_parent.push(parent.head);
            self.arena_sym.push(s);
            survivors.push(PathS { head: node, metric: m, blocks: parent.blocks.clone() });
        }
        self.live = survivors;
        Ok(())
    }

    fn decode_segment(&mut self, offset: usize, size: usize) -> Result<(), i64> {
        if size == 1 {
            return self.decode_leaf(offset);
        }
        let q = self.q;
        let half = size / 2;

        // ---- minus, batched over live paths ----
        {
            let p_count = self.live.len();
            let rows = p_count * half;
            let mut out = vec![0.0f64; rows * q];
            {
                let firsts: Vec<&[f64]> = self.live.iter().map(|pt| {
                    let b = pt.blocks.last().unwrap();
                    &b.data[b.off..b.off + half * q]
                }).collect();
                let seconds: Vec<&[f64]> = self.live.iter().map(|pt| {
                    let b = pt.blocks.last().unwrap();
                    &b.data[b.off + half * q..b.off + 2 * half * q]
                }).collect();
                let cv_inv = self.cv_inv;
                par_rows(rows, q, self.nthreads, &mut out, |lo, hi, chunk| {
                    let mut ls = vec![0.0f64; q];
                    let mut pb = vec![0.0f64; q];
                    let mut sb = vec![0.0f64; q];
                    for r in lo..hi {
                        let pi = r / half;
                        let lr = r % half;
                        let frow = &firsts[pi][lr * q..lr * q + q];
                        let srow = &seconds[pi][lr * q..lr * q + q];
                        let orow = &mut chunk[(r - lo) * q..(r - lo) * q + q];
                        minus_row(frow, srow, cv_inv, orow, &mut ls, &mut pb, &mut sb);
                    }
                });
            }
            let shared = Rc::new(out);
            for (i, pt) in self.live.iter_mut().enumerate() {
                pt.blocks.push(Blk { data: shared.clone(), off: i * half * q });
            }
        }
        self.decode_segment(offset, half)?;
        for pt in self.live.iter_mut() {
            pt.blocks.pop();
        }

        // ---- plus, batched over (new) live paths ----
        {
            let p_count = self.live.len();
            let rows = p_count * half;
            let mut betas = vec![0i64; rows];
            for (pi, pt) in self.live.iter().enumerate() {
                let u = &mut betas[pi * half..(pi + 1) * half];
                let mut h = pt.head;
                for i in (0..half).rev() {
                    u[i] = self.arena_sym[h as usize] as i64;
                    h = self.arena_parent[h as usize];
                }
                polar_transform_one(u, half, self.cv);
            }
            let mut out = vec![0.0f64; rows * q];
            {
                let firsts: Vec<&[f64]> = self.live.iter().map(|pt| {
                    let b = pt.blocks.last().unwrap();
                    &b.data[b.off..b.off + half * q]
                }).collect();
                let seconds: Vec<&[f64]> = self.live.iter().map(|pt| {
                    let b = pt.blocks.last().unwrap();
                    &b.data[b.off + half * q..b.off + 2 * half * q]
                }).collect();
                let cv = self.cv;
                let betas_ref = &betas;
                par_rows(rows, q, self.nthreads, &mut out, |lo, hi, chunk| {
                    for r in lo..hi {
                        let pi = r / half;
                        let lr = r % half;
                        let frow = &firsts[pi][lr * q..lr * q + q];
                        let srow = &seconds[pi][lr * q..lr * q + q];
                        let orow = &mut chunk[(r - lo) * q..(r - lo) * q + q];
                        let b = betas_ref[r];
                        for a in 0..q {
                            orow[a] = frow[(b ^ cv[a]) as usize] + srow[a];
                        }
                        normalize_row(orow);
                    }
                });
            }
            let shared = Rc::new(out);
            for (i, pt) in self.live.iter_mut().enumerate() {
                pt.blocks.push(Blk { data: shared.clone(), off: i * half * q });
            }
        }
        self.decode_segment(offset + half, half)?;
        for pt in self.live.iter_mut() {
            pt.blocks.pop();
        }
        Ok(())
    }
}

/// Whole-recursion list-SC decode. `logp` is the validated/normalized (n,q)
/// metric (Python does the metric contract checks). `known_mask[i] != 0`
/// marks disclosed coordinate i with symbol `known_val[i]`. Outputs: ranked
/// u words (row-major width*n, first `survivors` rows valid), path metrics
/// (width), and `out_info = [status, survivors, pruned, err_position]`.
#[no_mangle]
pub extern "C" fn nbpolar_scl_decode_f64(
    logp: *const c_double,
    n: c_longlong,
    q: c_longlong,
    cv: *const c_longlong,
    cv_inv: *const c_longlong,
    width: c_longlong,
    known_mask: *const i8,
    known_val: *const c_longlong,
    nthreads: c_longlong,
    out_u: *mut c_longlong,
    out_metric: *mut c_double,
    out_info: *mut c_longlong,
) {
    let n = n as usize;
    let q = q as usize;
    let width = width as usize;
    unsafe {
        let root = std::slice::from_raw_parts(logp, n * q).to_vec();
        let mut ctx = Ctx {
            q,
            width,
            cv: std::slice::from_raw_parts(cv, q),
            cv_inv: std::slice::from_raw_parts(cv_inv, q),
            known_mask: std::slice::from_raw_parts(known_mask, n),
            known_val: std::slice::from_raw_parts(known_val, n),
            nthreads: (nthreads as usize).max(1),
            arena_parent: Vec::with_capacity(n * width.min(64) + 1),
            arena_sym: Vec::with_capacity(n * width.min(64) + 1),
            live: vec![PathS {
                head: NONE_NODE,
                metric: 0.0,
                blocks: vec![Blk { data: Rc::new(root), off: 0 }],
            }],
            pruned: 0,
            err_pos: 0,
        };
        let info = std::slice::from_raw_parts_mut(out_info, 4);
        match ctx.decode_segment(0, n) {
            Ok(()) => {}
            Err(code) => {
                info[0] = code;
                info[1] = 0;
                info[2] = ctx.pruned;
                info[3] = ctx.err_pos as i64;
                return;
            }
        }
        let mut order: Vec<usize> = (0..ctx.live.len()).collect();
        order.sort_by(|&a, &b| ctx.live[b].metric.partial_cmp(&ctx.live[a].metric).unwrap());
        let out_u = std::slice::from_raw_parts_mut(out_u, width * n);
        let out_metric = std::slice::from_raw_parts_mut(out_metric, width);
        for (rank, &pi) in order.iter().enumerate() {
            out_metric[rank] = ctx.live[pi].metric;
            let mut h = ctx.live[pi].head;
            for i in (0..n).rev() {
                out_u[rank * n + i] = ctx.arena_sym[h as usize] as i64;
                h = ctx.arena_parent[h as usize];
            }
        }
        info[0] = 0;
        info[1] = order.len() as i64;
        info[2] = ctx.pruned;
        info[3] = 0;
    }
}
