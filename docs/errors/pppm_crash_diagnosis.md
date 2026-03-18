# Why PPPM Works in Your Bulk Water Script But Crashes in Our Slab

## Query 2: Why does this TIP4P/PPPM script run fine but our variant_b crashes?

## Response 2:

### The scripts are solving fundamentally different problems

Your working script is **bulk water** (fully periodic, water fills the entire box). Our script is a **slab geometry** (water slab + vacuum). This difference changes everything about how PPPM operates.

### Side-by-side comparison

| Feature | Your script (works ✅) | Our variant_b (crashes ❌) |
|---|---|---|
| **Geometry** | Bulk water, no vacuum | Water slab + vacuum |
| **Boundary** | `p p p` (fully periodic) | `p p p` → needs `p p f` for slab |
| **Slab correction** | ❌ Not needed | ✅ `kspace_modify slab 3.0` required |
| **PPPM variant** | `pppm/tip4p` | `pppm` |
| **Water model** | TIP4P/2005 (4-site) | SPC/E (3-site) |
| **Ensemble** | NPT (pressure-controlled) | NVT (fixed volume) |
| **Multi-run** | Single `run 20000` | Multiple runs (heat → equil → prod) |

### The crash happens in two stages

**Stage 1 — LAMMPS error** (with `boundary p p p`):
```
ERROR: Incorrect boundaries with slab PPPM
```
PPPM's slab correction (`kspace_modify slab 3.0`) internally stretches the z-dimension by 3× and adds a dipole correction. LAMMPS requires `boundary p p f` for this to work with PPPM.

Your script doesn't use `kspace_modify slab` at all → no boundary conflict → no error.

**Stage 2 — Segfault** (after fixing to `boundary p p f`):
```
Signal 11 (Segmentation fault) in PPPM::init()
```
When PPPM sets up with `boundary p p f` + slab extension (3× z), it creates a very **elongated FFT grid** (the z-dimension of the grid is ~3× larger than x,y). The FFTW3 library on macOS ARM has a bug with this particular grid shape, causing a segfault during FFT plan creation.

Your script uses `boundary p p p` with a cubic/near-cubic box → FFTW gets a normal grid shape → no bug triggered.

### Why your script doesn't need slab correction

```
read_data       1H2O
replicate       8 8 8    # Fills the entire box with water
```

Your box is completely filled with water — there's no interface, no vacuum, no slab. The electrostatic environment is the same in all directions. PPPM with 3D periodicity is physically correct here.

In our script:
```
region          waterbox block 0.5 29.5 0.5 29.5 30.0 90.0   # Water only in z=30-90
# z=0-30 and z=90-120 are vacuum
```

Without `kspace_modify slab`, PPPM computes electrostatic images of the water slab through the z-boundary. These phantom images corrupt the pressure tensor and give 10× wrong surface tension.

### Summary of why it crashes

```
Your script:   PPPM + p p p + no slab   → normal FFT grid → works ✅
Our variant_b: PPPM + p p f + slab 3.0  → elongated FFT grid → FFTW ARM bug → segfault ❌
```

The crash is NOT about PPPM being broken in general. It's specifically the combination of **PPPM + slab correction + macOS ARM FFTW**.

### Solutions

| Option | Effort | Result |
|---|---|---|
| **Use Ewald** (current fix) | None | Works, but 5-10× slower |
| **Rebuild LAMMPS with `cmake -DFFT=KISS`** | Moderate | PPPM works, no FFTW dependency |
| **Run on Linux** | Low (if cluster available) | PPPM + slab works fine |
| **Use `pppm/tip4p` + TIP4P/2005** | Moderate | Different code path, might avoid the bug (untested) |
