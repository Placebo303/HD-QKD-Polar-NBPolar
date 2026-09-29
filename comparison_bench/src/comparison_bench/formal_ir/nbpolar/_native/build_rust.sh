#!/usr/bin/env bash
# Build the zero-dependency Rust cdylib kernel for the NB-Polar native SCL
# decoder. Requires the rustup-installed toolchain at $HOME/.cargo (stable,
# minimal profile; installed 2026-09-29 per PI authorization). Run from WSL.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/rust_kernels"

if [[ -f "$HOME/.cargo/env" ]]; then
    # shellcheck disable=SC1091
    source "$HOME/.cargo/env"
fi

cargo build --release
OUT_DIR="target/release"
if [[ -f "$OUT_DIR/libnbpolar_kernels.so" ]]; then
    cp -f "$OUT_DIR/libnbpolar_kernels.so" ../libnbpolar_kernels_rust.so
    echo "Built $(cd .. && pwd)/libnbpolar_kernels_rust.so"
elif [[ -f "$OUT_DIR/nbpolar_kernels.dll" ]]; then
    cp -f "$OUT_DIR/nbpolar_kernels.dll" ../nbpolar_kernels_rust.dll
    echo "Built $(cd .. && pwd)/nbpolar_kernels_rust.dll"
else
    echo "Rust build did not produce an expected cdylib artifact under $OUT_DIR" >&2
    ls -la "$OUT_DIR" >&2
    exit 1
fi
