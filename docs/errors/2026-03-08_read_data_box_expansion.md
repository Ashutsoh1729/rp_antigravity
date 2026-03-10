# LAMMPS Error Report: Box Expansion via `read_data append`

**Date**: March 8, 2026
**Simulation**: PFOA at Air-Water Interface (`pfoa_in_water.lammps`)

## The Problem
When visualizing the simulation trajectory in OVITO, the water slab (originally ~37x37x37 Å) appeared as a small cube sitting in the corner of a massive `113 x 117 x 250 Å` simulation box. The intended vacuum gap was only meant to exist in the Z-direction, not X and Y.

## The Cause
The error was caused by the `read_data append` command used to insert the PFOA molecule into the water box:

```lammps
read_data data/PFOA_stripped.data add append offset 2 1 1 0 0 shift 18.636 18.636 18.5
```

The `PFOA_stripped.data` file originally contained excessively large bounding box dimensions defined in its header:

```lammps
-5.981883226 94.01811677 xlo xhi
-1.849107127 98.15089287 ylo yhi
-2.134384898 97.8656151 zlo zhi
```

**LAMMPS Behavior**: By default, when `read_data ... append` is executed, LAMMPS compares the box bounds defined *inside* the incoming `.data` file with the bounds of the existing simulation box. If the incoming bounds are larger in any dimension, LAMMPS aggressively expands the main simulation box to match them. 

Because the PFOA data file declared bounds up to ~94-98 Å in X and Y, LAMMPS resized the entire 37x37 Å water slab bounding box to 113x117 Å, filling the new empty space in the X and Y directions with vacuum.

## The Solution
The box dimensions listed in a molecule's `.data` file must tightly bound the molecule itself. 

To fix this, the bounding box inside `src/pfas/data/PFOA_stripped.data` was manually shrunk to closely wrap the PFOA atoms:

```lammps
-2.0 2.0 xlo xhi
-8.0 8.0 ylo yhi
-4.0 4.0 zlo zhi
```

With these tight bounds (which are smaller than the 37x37 main box), the `read_data append` command inserts the molecule without triggering any unwanted expansion of the main simulation boundaries.
