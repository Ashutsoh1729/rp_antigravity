# PFAS Insertion Script Guide

This script automates the creation of LAMMPS input files by inserting multiple PFAS molecules at random positions (X, Y, Z) within the simulation box.

## Script Location
`src/pfas/multi_pfas/scripts/insert_pfas.py`

## Usage

Run the script from the project root or the `scripts/` directory:

```bash
python3 src/pfas/multi_pfas/scripts/insert_pfas.py [arguments]
```

### Arguments

| Argument | Default | Description |
| :--- | :--- | :--- |
| `--template` | `../test_multi.lammps` | Path to the base LAMMPS script. |
| `--pfas_data` | `../../data/PFOA_stripped.data` | Path to the PFAS molecule data file. |
| `--num_molecules` | `8` | Number of molecules to insert. |
| `--z_range` | `5.0 30.0` | Min and Max Z-coordinates for random placement. |
| `--output` | `sim_random.lammps` | Filename for the generated script. |

### Output
The generated script will be automatically saved in the `src/pfas/multi_pfas/lammps/` directory.

## Examples

**Insert 20 molecules in a specific Z-range:**
```bash
python3 src/pfas/multi_pfas/scripts/insert_pfas.py --num_molecules 20 --z_range 10.0 25.0 --output 20pfoa_test.lammps
```

## How it Works
1. **Dimension Inference**: The script reads the `--template` and calculates the lateral box size (X, Y) based on the `replicate` command.
2. **3D Randomization**: For each molecule, it generates random $X, Y, \text{and } Z$ coordinates.
3. **Template Injection**: It replaces the hardcoded grid-based insertion block in the template with the new randomized `read_data` commands.
