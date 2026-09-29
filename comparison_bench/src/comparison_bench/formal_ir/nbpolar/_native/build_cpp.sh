#!/usr/bin/env bash
# Build the zero-dependency C++ kernel shared library for the NB-Polar
# native SCL decoder. Run from WSL (g++ from the distro's build-essential)
# or from a Windows shell with Strawberry Perl's mingw g++ on PATH.
#
# No fastmath: do not add -ffast-math (see kernels.cpp header for why).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ "$(uname -s)" == "Linux" ]]; then
    OUT="libnbpolar_kernels.so"
    EXTRA_LD=()
else
    OUT="nbpolar_kernels.dll"
    EXTRA_LD=()
fi

CXX="${CXX:-g++}"
OPENMP_FLAGS=()
if echo 'int main(){return 0;}' | "$CXX" -fopenmp -x c++ - -o /tmp/omp_probe_$$ 2>/dev/null; then
    OPENMP_FLAGS=(-fopenmp)
    rm -f /tmp/omp_probe_$$*
fi

echo "Building $OUT with: $CXX -O3 -march=native -std=c++17 ${OPENMP_FLAGS[*]:-} -shared -fPIC kernels.cpp"
"$CXX" -O3 -march=native -std=c++17 "${OPENMP_FLAGS[@]}" -shared -fPIC kernels.cpp -o "$OUT" "${EXTRA_LD[@]}"
echo "Built $(pwd)/$OUT"
