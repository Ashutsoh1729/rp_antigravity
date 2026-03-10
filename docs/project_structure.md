# Project Directory Structure

This document outlines the organization of the air-water interface simulation project. Following this structure ensures clean separation of concerns between simulation execution, data analysis, and documentation.

## Directory Layout

```text
.
├── src/                # Simulation configuration and data files
│   ├── test/           # Test and validation simulations (e.g., pure water variants)
│   └── pfas/           # PFAS interface simulations (e.g., PFOA in water slab)
│       └── PFOA.data   # LAMMPS data files containing topological information
│       └── *.lammps    # Main simulation LAMMPS input scripts
│
├── analysis/           # Post-simulation analysis
│   ├── codes/          # Variant-specific analysis scripts (e.g., analyze_variant_c.py)
│   ├── output/         # Generated output from scripts (plots, reports, organized by variant)
│   └── instruction.md  # Guidelines for the AI agent to write analysis scripts
│
├── scripts/            # Helper scripts used before or outside the simulation run
│   └── generate_molecules/
│       └── generate_pfoa.py  # Python scripts to build the LAMMPS `.data` files
│
└── docs/               # Project documentation and plans
    ├── plan/           
    │   ├── project_plan.md   # Overall simulation strategy and physics logic
    │   └── criteria/         # Validation criteria targets
    │       ├── aw_interface_criteria.md  # Targets for pure water simulations
    │       └── pfas_criteria.md          # Targets for PFAS insertion simulations
```

## Core Principles

1. **`src/` is for Simulation Only**: Only LAMMPS input scripts (`.lammps`), starting geometries (`.data`, `.xyz`, `.mol`), and molecule definitions belong here. Scripting logic (Python tools) should be kept out.
2. **`scripts/` is for Pre-processing**: Code used to generate molecules (like OpenFF scripts), build complex starting positions, or manipulate files before sending them to LAMMPS.
3. **`analysis/` is for Post-processing**: Once a simulation generates output (`log.lammps`, `trajectory.lammpstrj`, `.dat` files), all logic to process and plot that data lives in `analysis/codes/`, writing strictly to `analysis/output/`.
4. **`docs/` is the Source of Truth**: AI agents will regularly poll `docs/plan/criteria/` to understand what success looks like. Always keep these updated with the latest physical targets.
