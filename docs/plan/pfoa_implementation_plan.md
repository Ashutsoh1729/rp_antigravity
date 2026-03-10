# Implementation Plan: PFAS (PFOA) at the Air-Water Interface

This implementation plan covers the strategy to simulate a single PFOA molecule inserted into the bulk region of the pre-validated TIP4P/2005 water slab.

## Proposed Changes

### 1. PFOA Molecule Definition (`src/pfas/PFOA.mol` / `.data`)
- **[NEW] `src/pfas/PFOA.mol`**:
  - Contains the full OPLS-AA parameterized structure for Perfluorooctanoic Acid (PFOA).
  - Atoms: Fluorines, Carbons (tail), Carbon (head), Oxygens (head), Hydrogen.
  - OPLS-AA provides all bond, angle, and dihedral types, along with partial charges.
  - Coordinate source: Will use a pre-relaxed linear zigzag/helical structure.

### 2. Simulation Script (`src/pfas/pfoa_in_water.lammps`)
- **[NEW] `src/pfas/pfoa_in_water.lammps`**:
  - Builds on the successful `variant_c.lammps` logic.
  - Loads the TIP4P/2005 water box (`read_data`).
  - Implements the OPLS-AA pair styles alongside the TIP4P/long pair styles.
  - **Insertion**: Uses the `molecule` and `create_atoms` or `deposit` command to drop the PFOA molecule into the exact center of the water slab.
  - **Overlap Removal**: Runs `delete_atoms overlap` to remove any water molecules directly clashing with the inserted PFOA.
  - **Equilibration**: Runs a rigorous `minimize` phase followed by a short NPT or NVT equilibration step to let the water adapt to the newly formed cavity.
  - **Production**: Runs for a short validation period (e.g., 200ps) to track immediate stability and the beginning of migration, with extensive outputs (trajectory, COM tracking).

### 3. Analysis Code (`analysis/codes/analyze_pfoa_in_water.py`)
- **[NEW] `analysis/codes/analyze_pfoa_in_water.py`**:
  - A new python script specifically designed to validate the `pfas_criteria.md`.
  - Parses the PFOA's Center of Mass z-position over time.
  - Parses the Oxygen(PFOA) to Hydrogen(Water) RDF.
  - Verifies bulk density remains stable.

---

## Verification Plan

### Automated Tests
1. **LAMMPS Run**: Execute `mpirun -np 6 lmp_mpi -in pfoa_in_water.lammps` and ensure it runs without `NaN` energies or segmentation faults.
2. **Analysis Script**: Run `uv run python analysis/codes/analyze_pfoa_in_water.py src/pfas/output/pfoa src/pfas/output/pfoa`, verifying that the script successfully extracts Center of Mass logic and calculates the RDF.

### Validation Criteria Checks (against `docs/plan/criteria/pfas_criteria.md`)
1. **Density**: Must remain close to `0.997 g/cm³`.
2. **Energy Stability**: Energy must stabilize quickly after the `minimize` phase.
3. **Migration (COM)**: Check the output COM chart; it should either remain stable in the bulk or show slight directional drift towards the surface over 200ps.
