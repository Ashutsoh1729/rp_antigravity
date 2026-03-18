# Plan for Multi-PFAS Simulation at Air-Water Interface

## Overview
This plan outlines the transition from a single PFAS molecule simulation to a multi-molecule setup. The goal is to observe collective behavior, packing at the interface, and concentration-dependent effects as defined in the overall project goals (`docs/init.md`).

## 1. Simulation Box and Water Slab Dimensions

To accommodate multiple molecules without artificial lateral constraints or immediate crowding, we will expand the X and Y dimensions of the water slab while maintaining the thickness.

- **Current Setup**: 12x12x12 replication (~37 Å x 37 Å x 37 Å water slab).
- **Proposed Setup**: **20x20x12** replication.
    - **Lateral Dimensions (X, Y)**: ~62.12 Å x 62.12 Å (based on 3.106 Å unit cell).
    - **Slab Thickness (Z)**: ~37.27 Å.
    - **Total Water Molecules**: 4,800 molecules (increased from 1,728).
    - **Total Z-Box Height**: 250 Å (keeps large vacuum gap for periodic decoupling).

## 2. PFAS Molecule Count

For this initial multi-molecule test, we will insert **8 PFOA molecules**. 

- **Concentration**: This translates to a surface density of ~0.2 molecules/nm², which is a good starting point for observing adsorption without being at full monolayer coverage.

## 3. Placement Strategy

The molecules will be placed at a deeper initial position as requested, and distributed across the slab to allow independent equilibration.

- **Depth (Z-Coordinate)**: **28.0 Å**.
    - With the interface at ~37.3 Å, this puts the molecules ~9.3 Å below the surface.
    - This is deeper than the previous test (32.0 Å, which was only ~5.3 Å deep) and provides more "bulk-like" surroundings initially.
- **X-Y Distribution**: 2x4 Grid.
    - To avoid overlaps and ensure uniform starting conditions, molecules will be placed at the following approximate coordinates:
        - **X-columns**: 15.0 Å, 45.0 Å
        - **Y-rows**: 7.5 Å, 22.5 Å, 37.5 Å, 52.5 Å
- **Orientation**: Random or surface-parallel orientations to avoid bias (LAMMPS `rotate` can be used if needed during insertion).

## 4. Key Simulation Parameters

- **Units**: real
- **Force Field**: TIP4P/2005 for water; OPLS-AA/GAFF for PFOA.
- **Ensemble**: NVT at 300K (Nose-Hoover).
- **Time Step**: 1.0 fs.
- **Phases**:
    1. **Cavity Healing**: 0.5 ps with short-range cutoffs and `delete_atoms overlap`.
    2. **Ramp Run**: 1.0 ps to stabilize timestep.
    3. **Production Equilibration**: 100+ ps to observe migration to the interface.

## 5. Next Steps
1. Update the LAMMPS script to use the new replication factors.
2. Implement multiple `read_data ... add append` commands or a loop for PFOA insertion.
3. Verify lack of initial overlaps before long production runs.
