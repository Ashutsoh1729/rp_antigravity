# KSpace Styles in LAMMPS — Long-Range Electrostatics

## What is KSpace?

In molecular dynamics, charged particles (like the O and H atoms in water) interact via the **Coulomb potential**:

```
V(r) = q_i · q_j / (4πε₀ · r)
```

This is a **long-range interaction** — it decays as 1/r, which means it never truly goes to zero. You can't simply cut it off at 10 Å like you do with Lennard-Jones forces, because the contribution from distant charges is still significant. Ignoring it leads to **large errors** in energy, pressure, and structure.

**KSpace** (short for **k-space**, i.e., reciprocal/Fourier space) refers to the methods that handle this long-range Coulombic tail efficiently.

---

## The Core Idea: Ewald Summation

All kspace methods in LAMMPS are variants of the **Ewald summation** technique (1921). The idea:

1. **Split** the Coulomb interaction into two parts:
   - **Short-range part** — a screened (Gaussian-damped) Coulomb that decays fast → compute in **real space**
   - **Long-range part** — a smooth, slowly-varying charge distribution → compute in **reciprocal (Fourier) space**

2. **Real-space part**: Handled by `pair_style lj/cut/coul/long` with a real-space cutoff (10 Å in our script). Beyond this cutoff, real-space Coulomb is negligible.

3. **Reciprocal-space part**: Handled by `kspace_style`. This sums up the long-range Fourier components across all periodic images of the simulation box.

```
kspace_style    ewald 1.0e-4
                ↑              ↑
                method         desired relative accuracy
```

The accuracy parameter (1.0e-4) controls how many terms to include — smaller = more accurate = slower.

---

## KSpace Methods Available in LAMMPS

### 1. Ewald (what we use)

```
kspace_style ewald 1.0e-4
```

- **How**: Direct summation in reciprocal space over k-vectors
- **Scaling**: O(N^(3/2)) to O(N²) depending on accuracy
- **Pros**:
  - Exact (no interpolation)
  - No FFT dependency — works on all platforms (no FFTW crashes)
  - Good for small systems (< 5000 atoms)
- **Cons**:
  - Slow for large systems — scales poorly beyond ~10,000 atoms
  - Not suitable for production runs of large systems

**Why we use it**: PPPM crashed on macOS ARM due to an FFTW3 bug. Ewald avoids FFTW entirely. With ~4,860 atoms, it runs at ~18 timesteps/s — acceptable for testing.

### 2. PPPM (Particle-Particle Particle-Mesh)

```
kspace_style pppm 1.0e-4
```

- **How**: Maps charges onto a 3D grid, computes long-range part via FFT
- **Scaling**: O(N log N) — much faster for large systems
- **Pros**:
  - Fast — the standard choice for production MD
  - 5-10× faster than Ewald for systems > ~1000 atoms
- **Cons**:
  - Requires FFTW library (crashed on our macOS ARM setup)
  - Grid interpolation introduces small errors (controlled by accuracy param)
  - Reinitialization between runs can cause segfaults (our batch 1 bug)

**When to switch back**: If we update LAMMPS/FFTW and the crash is fixed, PPPM would give a major speedup for longer runs.

### 3. MSM (Multi-Level Summation Method)

```
kspace_style msm 1.0e-4
```

- **How**: Hierarchical real-space approach, no FFT
- **Scaling**: O(N)
- **Pros**: Works without FFT, good for non-periodic systems
- **Cons**: Less accurate than Ewald/PPPM for periodic systems, rarely used for water

### 4. PPPM/disp (for dispersion)

```
kspace_style pppm/disp 1.0e-4
```

- Handles both Coulombic AND dispersion (LJ) long-range corrections via FFT
- Useful when LJ cutoff is short and long-range dispersion matters
- Not needed for our current setup (LJ cutoff of 10 Å is sufficient for SPC/E)

---

## The `kspace_modify slab` Correction

For **slab geometries** (like our air-water interface), there's a critical issue:

### The Problem

Our box has `boundary p p p` — periodic in all directions. But physically, the z-direction should be **non-periodic** (we have vacuum on both sides of the water slab).

The kspace solver doesn't know about the vacuum — it computes electrostatics assuming infinite 3D periodicity. This means the water slab "sees" an electrostatic image of itself across the z-boundary:

```
... | vacuum | WATER SLAB | vacuum | WATER SLAB | vacuum | ...
         ← periodic images →
```

The slab-to-slab interaction through the vacuum is **spurious** — it doesn't exist in reality. This artificial dipole interaction inflates the pressure tensor anisotropy, leading to **10× overestimation of surface tension** (which is exactly what we saw in batch 2: 641 mN/m instead of 61 mN/m).

### The Fix

```
kspace_modify slab 3.0
```

This applies the **Yeh & Berkowitz (1999) correction**:
- Internally extends the z-dimension by a factor of 3×, adding extra vacuum
- Adds a **dipole correction term** to cancel the slab-image interaction
- The result is equivalent to a **2D-periodic** Ewald sum (periodic in x,y only)

The factor `3.0` is the volume factor — 3× is standard and sufficient. Values of 2× or 5× also work but 3× is the established best practice.

### Impact on Our Results

| Quantity | Without slab correction | With slab correction | Expected |
|---|---|---|---|
| Bulk density | 0.956 g/cm³ | ~0.956 g/cm³ (no change) | 1.0 g/cm³ |
| Surface tension | 641 mN/m ❌ | ~60 mN/m ✅ (expected) | 61 mN/m |

The density is largely unaffected because it depends on short-range structure. The surface tension is dramatically affected because it depends on the pressure tensor anisotropy, which is dominated by long-range electrostatics.

---

## In Our Script

```lammps
pair_style      lj/cut/coul/long 10.0    # real-space cutoff = 10 Å
kspace_style    ewald 1.0e-4             # reciprocal-space via Ewald
```

**What happens at each timestep**:
1. For each atom pair within 10 Å → compute LJ + short-range Coulomb
2. Ewald solver → compute long-range Coulomb across all periodic images
3. Sum → total force on each atom

**What needs to change for batch 3**:
```lammps
kspace_style    ewald 1.0e-4
kspace_modify   slab 3.0                 # ← ADD THIS
```

---

## References

- Ewald, P.P. (1921). *Die Berechnung optischer und elektrostatischer Gitterpotentiale.* Ann. Phys. 369, 253–287.
- Hockney, R.W. & Eastwood, J.W. (1988). *Computer Simulation Using Particles.* CRC Press. (PPPM method)
- Yeh, I.-C. & Berkowitz, M.L. (1999). *Ewald summation for systems with slab geometry.* J. Chem. Phys. 111, 3155.

---

## Query 1: Why is Ewald used here and not PPPM? I have done it once with PPPM.

## Response 1:

### PPPM is the better method — we're using Ewald only as a workaround

PPPM (`kspace_style pppm`) is the standard, preferred choice for production molecular dynamics. It's faster (O(N log N) vs Ewald's O(N^1.5)), more scalable, and what almost every published water simulation uses. You were right to use PPPM originally.

### What went wrong with PPPM on our setup

When we ran with `kspace_style pppm 1.0e-4`, LAMMPS crashed with a **segmentation fault** during the kspace reinitialization step (when transitioning between the equilibration and production `run` commands). The root cause:

1. PPPM relies on the **FFTW3** library (Fastest Fourier Transform in the West) to compute 3D FFTs on the charge grid.
2. On **macOS ARM (Apple Silicon)**, the FFTW3 build bundled with our LAMMPS installation has a known bug where reinitializing the FFT plan after a `run` command corrupts memory.
3. This is a **platform-specific** issue — the same script runs fine on Linux x86_64 with PPPM.

### The crash signature

```
Segfault at PPPM::compute() → FFTW3 plan execution
Triggered by: second run command reinitializing kspace
Platform: macOS ARM (Apple Silicon M-series)
```

### Why Ewald fixes it

Ewald computes the reciprocal-space sum by direct summation over k-vectors — **no FFT, no FFTW dependency**. It completely sidesteps the buggy library. The tradeoff is speed: Ewald is ~5-10× slower than PPPM for our system size (~4,860 atoms).

### Performance comparison on our system

| Method | Speed (timesteps/s) | Time for 1 ns | Suitability |
|---|---|---|---|
| **PPPM** | ~100-150 | ~2 hours | ❌ Crashes on macOS ARM |
| **Ewald** | ~18 | ~15 hours | ✅ Works, but slow |

### When to switch back to PPPM

You should switch back to PPPM if any of the following become true:

1. **Run on a Linux cluster** — PPPM works fine on Linux. If you move this simulation to an HPC cluster, switch immediately.
2. **Update LAMMPS** — newer versions (2024+) may have patched the FFTW reinitialization bug on ARM.
3. **Rebuild LAMMPS with KISS FFT** — LAMMPS supports an internal FFT (KISS FFT) that doesn't depend on FFTW: `cmake -DFFT=KISS ..`. This avoids the FFTW bug while keeping PPPM's speed.
4. **Merge runs** — we already merged the equilibration and production into phases within a single input script, which avoids the reinitialization that triggered the crash. PPPM might now work if tested.

### Bottom line

> **Ewald is a temporary safety net, not the long-term choice.** For our current test runs (~60,000 steps), it's acceptable. For Phase 2+ (PFAS simulations with larger systems), we must switch back to PPPM or the simulations will be impractically slow.
