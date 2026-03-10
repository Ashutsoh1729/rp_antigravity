# Modification Log — Batch 2

**Date**: 2026-02-13  
**Reference**: [Batch 1 Learnings](../learn/batch1.md)

## What Changed (Batch 1 → Batch 2)

### 1. Tighter Lattice Spacing
```diff
- lattice         sc 3.5
+ lattice         sc 3.1
```
- **Why**: 3.5 Å gave only ~65% of bulk water density. The slab spent the entire batch 1 run contracting.
- **Now**: 3.1 Å is close to the O-O distance in bulk water, giving near-correct initial density (~1.0 g/cm³).
- **Safe because**: We switched from PPPM to Ewald in batch 1, so the FFTW crash that originally required 3.5 Å no longer applies.

### 2. Multi-Phase Simulation Protocol
**Before** (batch 1): Minimize → single combined run (5 ps)

**After** (batch 2):

| Phase | Duration | Purpose |
|---|---|---|
| 1. Minimize | 1000 iters | Remove bad contacts |
| 2. NVT Heating | 10 ps (100→300 K) | Gentle temperature ramp |
| 3. NVT Equilibration | 40 ps (300 K) | Let slab fully relax |
| 4. Production | 10 ps test (300 K) | Collect data |

**Why**: Batch 1 had no pre-equilibration. All 5 ps were essentially transient data.

### 3. Separated Data Collection
```diff
- # Data collection from step 0 (contaminated with equilibration)
+ # Data collection starts only in Phase 4 (after 50 ps equilibration)
```
- **Why**: Batch 1 averaged over the slab contracting, which polluted the density profile and made surface tension meaningless.

### 4. Surface Tension Unit Conversion
```diff
- variable surftens equal 0.5*v_Lz*(v_pzz-0.5*(v_pxx+v_pyy))
+ variable surftens equal 0.5*v_Lz*(v_pzz-0.5*(v_pxx+v_pyy))
+ variable surftens_mNm equal v_surftens*0.101325
```
- **Why**: Raw output was in atm·Å. Now also outputs in mN/m for direct comparison with literature (SPC/E = ~61 mN/m at 300 K).

### 5. Equilibration Trajectory Dump
- Added a separate low-frequency dump (`equil_trajectory.lammpstrj`) during phases 2–3 for monitoring.
- Production trajectory dump starts only in phase 4.

### 6. Extended Minimization
```diff
- minimize 1.0e-4 1.0e-6 200 2000
+ minimize 1.0e-4 1.0e-6 1000 10000
```
- **Why**: 200 iterations was not enough for the tighter lattice. 1000 gives better initial relaxation.

### 7. Output Directory
All outputs → `output/batch.2/`

## Test Run Settings
- Heating: 10 ps, Equilibration: 40 ps, Production: 10 ps
- Total: 60 ps (~60,000 steps)
- For final production: increase phase 4 to 200,000 steps (200 ps)
