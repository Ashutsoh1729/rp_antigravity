# Air-Water Interface Simulation — Summary

## Files Created

### `water.mol` — Water Molecule Template
- **Model**: SPC/E (Extended Simple Point Charge)
- **Atoms**: 3 (1 Oxygen, 2 Hydrogen)
- **Topology**: 2 O-H bonds, 1 H-O-H angle
- **Charges**: O = −0.8476 e, H = +0.4238 e
- **Geometry**: O-H bond length ≈ 1.0 Å, H-O-H angle = 109.47°

### `air_water_interface.lammps` — LAMMPS Input Script
Sets up and runs a full air-water interface MD simulation:

| Stage | Details |
|---|---|
| **Box** | 30 × 30 × 120 Å (elongated z-axis) |
| **Water slab** | Placed in z = 30–90 Å; vacuum above & below forms the "air" |
| **Force field** | SPC/E: LJ + Coulomb (PPPM) |
| **Constraints** | SHAKE on O-H bonds and H-O-H angles |
| **Minimization** | 1000 steps (CG) |
| **Equilibration** | 50 ps NVT at 300 K |
| **Production** | 200 ps NVT at 300 K |

### Output Files (generated at runtime)
- `density_profile.dat` — mass-density binned along z
- `surface_tension.dat` — surface tension from pressure tensor anisotropy
- `trajectory.lammpstrj` — atom trajectories
- `final_config.data` — final state data file
- `restart.equil` — restart file

## How to Run

```bash
lammps -in air_water_interface.lammps
```
