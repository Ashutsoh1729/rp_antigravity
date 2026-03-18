# Automated Multi-PFAS Insertion Plan

## 1. Objective
Develop a Python script to automate the insertion of multiple PFAS molecules at random lateral positions within a LAMMPS simulation box. This replaces manual grid-based insertion and allows for flexible scaling of molecule counts.

## 2. Methodology

### 2.1 Inputs
- **Template Script**: `src/pfas/test_multi.lammps` (provides force field, box size, and simulation parameters).
- **PFAS Molecule Data**: `src/pfas/data/PFOA_stripped.data` (atom types, bonds, and geometry).
### 2.1 Inputs
- **Template Script**: `src/pfas/multi_pfas/test_multi.lammps`.
- **PFAS Molecule Data**: `src/pfas/data/PFOA_stripped.data`.
- **Logic**:
    - **Inferred Bounds (X, Y)**: Inferred from `multi_pfas/test_multi.lammps`.
    - **Managed Range (Z)**: User-defined (e.g., Z=5 to Z=30).

### 2.2 Script Logic (`src/pfas/multi_pfas/scripts/insert_pfas.py`)
1. **Dimension Extraction**: Reads the template to find simulation box limits.
2. **3D Randomization**: Generates $N$ random positions ($x, y, z$).
3. **LAMMPS Command Generation**: Construct $N$ `read_data ... add append` commands.
   ```lammps
   read_data data/PFOA_stripped.data add append offset 2 1 1 0 0 shift <X> <Y> <Z>
   ```
4. **Integration**: Replace the existing hardcoded insertion block in the template with the generated commands.

## 3. Implementation Steps

1. **Python Script Development**:
   - Use `argparse` for flexible command-line control.
   - Use `random.uniform` for coordinate generation.
   - Implement simple string replacement or regex to inject the new block into the LAMMPS script.

2. **Validation**:
   - Generate a test script for 8 molecules.
   - Confirm that `delete_atoms overlap` in the template effectively handles any high-energy overlaps from random placement.
   - Visualize the result in OVITO to ensure random distribution.

## 4. Next Phase: Implementation
Upon approval of this plan, we will move to creating the `insert_pfas.py` script.
