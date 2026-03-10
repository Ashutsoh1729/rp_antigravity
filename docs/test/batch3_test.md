# Batch 3 — Test Scripts

**Date**: 2026-02-13  
**Reference**: [Batch 3 Plan](../plan/batch3_plan.md) | [Batch 2 Learnings](../learn/batch2.md)

## What Was Done

Created two test input scripts in `src/test/` to validate the batch 3 fixes before committing to a full production run.

### Files Created

| File | Purpose |
|---|---|
| `src/test/variant_a.lammps` | Ewald + SPC/E + slab correction (safe, guaranteed to work) |
| `src/test/variant_b.lammps` | PPPM + SPC/E + slab correction (faster, may crash on macOS ARM) |
| `src/test/output/variant_a/` | Output directory for Variant A |
| `src/test/output/variant_b/` | Output directory for Variant B |

### Key Changes from Batch 2

Both variants add:
- `kspace_modify slab 3.0` — fixes the 10× surface tension error
- `pair_modify tail yes` — LJ long-range tail correction

Variant B additionally uses:
- `pppm` instead of `ewald` — 5-10× faster
- 12 Å cutoff instead of 10 Å — better accuracy

### Test Run Settings

| Phase | Duration | Purpose |
|---|---|---|
| Minimize | 500 iters | Remove bad contacts |
| Heat | 5 ps (100→300 K) | Gentle temperature ramp |
| Equilibrate | 10 ps (300 K) | Let slab relax |
| Production | 10 ps (300 K) | Collect data |
| **Total** | **~25 ps** | Quick validation |

### How to Run

```bash
cd src/test
mpirun -np 4 lmp_mpi -in variant_a.lammps   # run this first
mpirun -np 4 lmp_mpi -in variant_b.lammps   # then try this
```

### What to Check in Output

| Metric | Pass | Fail |
|---|---|---|
| Surface tension | 40–80 mN/m | >200 or <0 mN/m |
| Bulk density | 0.95–1.05 g/cm³ | <0.9 or >1.1 |
| No crash (Variant B) | Completes | Segfault |

### Next Step

Once a variant passes → use it as the base for the full production input script in `src/`.
