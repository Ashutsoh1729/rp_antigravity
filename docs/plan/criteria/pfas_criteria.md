# Validation Criteria: PFAS (PFOA) in Air-Water Interface

This document specifies the validation criteria for a simulation where a single PFAS molecule (initially PFOA) is inserted into the bulk region of the water slab.

---

## 1. P0 Criteria: Basic Integrity

### 1.1 Bulk Water Density Verification
- **What**: The addition of PFAS must not ruin the underlying water structure.
- **Expected**: Bulk density of water should remain near **~0.997 g/cm³**.
- **How to measure**: `density_profile.dat` core region.

### 1.2 System Energy Stability (No overlaps)
- **What**: Upon insertion, the PFAS molecule must not drastically overlap with water molecules or cause the energy to blow up.
- **Expected**: Total Energy should equilibrate quickly and remain stable without dramatic spikes.
- **How to measure**: `energy_stability.dat`.

---

## 2. P1 Criteria: Adsorption Kinetics and Thermodynamics

### 2.1 Center of Mass (COM) Migration
- **What**: The z-coordinate of the PFAS molecule's Center of Mass (COM).
- **Expected**: PFOA should thermodynamically prefer the interface. Over time (1-10 ns), its COM should migrate from the bulk (z ~ center of slab) to the interfacial region (z near the edges of the slab).
- **How to measure**: Tracking the `z` coordinate of the PFAS molecule from trajectory or `fix ave/time`.

### 2.2 Molecular Orientation at Interface
- **What**: How the molecule sits once reaching the interface.
- **Expected**:
  - The hydrophilic head (-COO⁻) should remain anchored in the liquid water.
  - The hydrophobic perfluoroalkyl tail (-CF₂-CF₃) should point out into the vacuum (air).
- **How to measure**: Compute the angle of the tail-to-head vector relative to the z-axis.

---

## 3. P2 Criteria: Intermolecular Structure

### 3.1 Head Group Hydration (RDF)
- **What**: The radial distribution function of the PFOA Oxygen atoms against water H atoms.
- **Expected**: A strong characteristic peak around 1.8 - 2.0 Å, indicating strong hydrogen bonding between the carboxylate head and water.
- **How to measure**: `rdf.dat` matching O(PFOA) - H(Water).

### 3.2 Tail Expulsion
- **What**: The tail should have minimal water around it once adsorbed.
- **Expected**: F atoms should have very low coordination with water Oxygen/Hydrogen compared to the bulk state.

---

## 4. Execution Guidance
- **Equilibration**: Inserting a bulky molecule into water requires initial energy minimization (`minimize`) followed by short `fix npt` or NVT relaxation to heal the cavity.
- **Production time**: Migration from bulk to interface takes nanoseconds. A 100-200 ps run is only enough to see the *start* of the process or the initial solvation state, not necessarily the full adsorption.
