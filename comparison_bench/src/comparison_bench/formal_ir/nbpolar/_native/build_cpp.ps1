# Build the zero-dependency C++ kernel DLL on native Windows using
# Strawberry Perl's bundled mingw g++ (no Visual Studio / MSVC required).
# Run: powershell -File build_cpp.ps1
#
# No fastmath: do not add -ffast-math (see kernels.cpp header for why).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$gxx = $null
foreach ($candidate in @("D:\software\Strawberry\c\bin\g++.exe", "C:\Strawberry\c\bin\g++.exe")) {
    if (Test-Path $candidate) { $gxx = $candidate; break }
}
if (-not $gxx) {
    $cmd = Get-Command g++ -ErrorAction SilentlyContinue
    if ($cmd) { $gxx = $cmd.Source }
}
if (-not $gxx) {
    Write-Error "No mingw g++ found (checked Strawberry Perl install paths and PATH). Install Strawberry Perl or point this script at a g++.exe."
    exit 1
}

Write-Host "Building nbpolar_kernels_win.dll with: $gxx -O3 -std=c++17 -fopenmp -shared kernels.cpp"
& $gxx -O3 -std=c++17 -fopenmp -shared -o nbpolar_kernels_win.dll kernels.cpp
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Built $PSScriptRoot\nbpolar_kernels_win.dll"
