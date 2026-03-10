# Modification Log — Batch 1 Initial Run

**Date**: 2026-02-13
**Files changed**: `air_water_interface.lammps`

## Changes Made (cumulative from initial version)

### 1. Fixed PPPM/FFTW Segfault on macOS ARM
- **Before**: `kspace_style pppm 1.0e-5`
- **After**: `kspace_style ewald 1.0e-4`
- **Why**: LAMMPS + FFTW3 on macOS ARM has a bug where the FFT destructor segfaults during PPPM reinitialization between runs. Ewald summation avoids FFTW entirely.

### 2. Fixed Initial Atom Overlaps
- **Before**: `lattice sc 3.1`
- **After**: `lattice sc 3.5`
- **Why**: 3.1 Å is too tight for 3-atom water molecules (~1.6 Å span), causing severe overlaps and the minimizer energy to explode to 123 million.

### 3. Merged Equilibration + Production into Single Run
- **Before**: Two separate `run` commands (equilibration + production)
- **After**: One `run 5000` command
- **Why**: Each `run` command triggers kspace reinitialization, which caused the FFTW segfault. Merging avoids any reinit.

### 4. Reduced Steps for Test Run
- Minimize: 200 iterations (was 2000)
- Run: 5000 steps (was 250,000 total)
- Output frequency scaled down proportionally

### 5. Output Redirected to `output/` Directory
- All `.dat`, `.lammpstrj`, `.data`, and restart files now go to `output/`

## Result
Simulation completed successfully. 1088 water molecules, 3264 atoms total.
