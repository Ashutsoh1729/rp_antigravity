# Root Cause Analysis: Atomic Clash in Multi-PFAS Simulation

## 1. Description of the Error
**Error Message**: `ERROR on proc X: Bond atoms ID1 ID2 missing on proc X at step 1`
**Initial State**: 
- Potential Energy: `~3.87e12` (Extremely high)
- Pressure: `~8.64e11`

## 2. Root Cause
The crash was caused by **High-Energy Atomic Overlaps**. 

When 20 PFAS molecules were placed randomly in the 3D space, several molecules were positioned partially inside each other. Because the force field (LJ + Coulomb) has a very steep repulsive core ($1/r^{12}$), the force between these overlapping atoms was nearly infinite.

At the very first time step (dynamics), this force "shot" the atoms out of their processors so fast that LAMMPS could no longer track their connectivity, leading to the "missing atoms" bond error.

## 3. Evidence
- **Potential Energy**: An e+12 energy is a signature of hard-sphere overlaps.
- **Timing**: The crash occurred at `step 1`, indicating the starting configuration was physically impossible for a standard dynamics run.

## 4. Remediation Plan
1. **Energy Minimization**: Before starting NVE/NVT dynamics, run a `minimize` command in LAMMPS. This uses a conjugate gradient or steepest descent algorithm to gently nudge overlapping atoms apart without calculating momentum.
2. **Template Update**: Add a minimization stage to `src/pfas/multi_pfas/test_multi.lammps`.
3. **Automated Fix**: The updated template will serve as the base for all future randomized insertions, preventing this error by default.

## 5. Prevention
- Always perform energy minimization when using randomized starting configurations.
- Monitor starting Potential Energy (PE) before long production runs.
