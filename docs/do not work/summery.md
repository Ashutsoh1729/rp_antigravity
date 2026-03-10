# LAMMPS Incompatible Combinations Summary

This document serves to track command combinations in LAMMPS that are fundamentally incompatible and will either cause fatal errors or silently produce incorrect physics.

## 1. `pppm/tip4p` and `kspace_modify slab`

**Status:** FATAL ERROR / Crash
**Context:** Simulating explicit 4-site water models (like TIP4P/2005) at an air-water interface (`p p f` boundaries).

You cannot use the TIP4P-specific long-range solver (`pppm/tip4p`) simultaneously with the Yeh-Berkowitz slab correction (`kspace_modify slab 3.0`). LAMMPS will throw an error or crash. 

**Workaround:**
If you must simulate an interface with a vacuum gap, you are forced to drop back to standard `pppm` and standard `lj/cut/coul/long`. 
*Note:* This means LAMMPS drops the M-site projection and treats the water as a 3-site model, which significantly alters its bulk density (e.g., yielding ~1.12 g/cm³ instead of 0.998 g/cm³) and surface tension. If accurate TIP4P physics are required at an interface, you must use a rigid molecule solver or a different simulation engine.

## 2. `fix wall` (like `wall/lj93`) and `boundary p p p`

**Status:** FATAL ERROR / Crash
**Context:** Attempting to trap molecules in the center of a large vacuum gap when the z-boundary is set to periodic (`p`).

LAMMPS mathematically prohibits placing a fixed wall (e.g., `fix wall/lj93 zlo ...`) on a dimension that is declared periodic (`p`). If you do this, LAMMPS aborts immediately with: `ERROR: Cannot use zlo wall in periodic z dimension`.

**Workaround:**
If you are using `boundary p p p` to bypass the `pppm/tip4p` slab incompatibility (by simply making the z-axis very large to act as a vacuum), you cannot use walls. Simply remove the `fix wall` commands and rely on the large vacuum gap to prevent periodic images from interacting. Stray molecules that evaporate might cross the periodic boundary, but they will not affect the main slab physics.
