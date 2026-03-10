# Simulation Outputs

All output files are stored in the `output/` directory.

## Output Files

| File | Description |
|---|---|
| **density_profile.dat** | Mass density of water binned along the z-axis (0.5 Å bins). Shows how water density varies from vacuum → bulk water → vacuum, forming the characteristic sigmoidal density profile at each interface. |
| **surface_tension.dat** | Surface tension computed from the pressure tensor anisotropy: γ = ½·Lz·(Pzz − ½(Pxx + Pyy)). Logged every 100 steps. Experimental value for SPC/E water at 300 K is ~63 mN/m. |
| **trajectory.lammpstrj** | Atom trajectories (positions + velocities) dumped every 500 steps. Can be visualized with VMD, OVITO, or similar tools. |
| **final_config.data** | Complete system state (atom positions, types, bonds, angles, velocities) at the end of the simulation. Can be used to restart or continue the run. |
| **restart.equil** | Binary restart file. Use with `read_restart` to continue the simulation from exactly where it stopped. |
| **log.lammps** | LAMMPS log (written to root dir). Contains thermo output (temperature, energy, pressure, surface tension) at every reporting interval. |
