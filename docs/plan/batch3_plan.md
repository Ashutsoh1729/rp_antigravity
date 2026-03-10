# Batch 3 Plan — Method Comparison & Implementation

## Two Approaches Compared

We have two scripts that model the air-water interface using different setups:

| Parameter | **Our Script (Batches 1-2)** | **Previous Script (PPPM/TIP4P)** |
|---|---|---|
| Water model | SPC/E (3-site) | TIP4P (4-site, virtual site on O) |
| Pair style | `lj/cut/coul/long 10.0` | `lj/cut/tip4p/long 1 2 1 1 0.1546 12.0` |
| KSpace | `ewald 1.0e-4` | `pppm/tip4p 1.0e-4` |
| Cutoff | 10.0 Å | 12.0 Å |
| LJ tail correction | ❌ No | ✅ `pair_modify tail yes` |
| Slab correction | ❌ Missing | ❌ Missing |
| Neighbor skin | 2.0 Å | 3.0 Å |
| Box creation | `lattice sc` + `create_atoms` | `read_data` + `replicate 9×9×9` |
| Slab creation | Place water in z=30–90 of 120 Å box | `change_box z final 0 70` to expand z |
| Equilibration | 50 ps multi-phase | None (direct NVT at 298 K) |
| SHAKE | Yes | Yes |

---

## Which Gives More Accurate Results?

### Water Model Accuracy

| Property | SPC/E | TIP4P | TIP4P/2005 | Experiment |
|---|---|---|---|---|
| Density (g/cm³) | 0.998 | 1.001 | 0.997 | 0.997 |
| Surface tension (mN/m) | 61 | 55 | 68 | 72 |
| Diffusion (10⁻⁵ cm²/s) | 2.4 | 3.3 | 2.1 | 2.3 |
| Dielectric constant | 71 | 53 | 58 | 78 |

**Verdict**: Neither SPC/E nor TIP4P is clearly superior overall.
- **SPC/E** is better for surface tension (61 vs 55, closer to 72)
- **TIP4P** is better for density
- **TIP4P/2005** is the best 4-site model — closest to experiment on most properties

> If accuracy is the priority, **TIP4P/2005** is the recommended model for air-water interface simulations. It gives γ ≈ 68 mN/m, closest to the experimental 72 mN/m.

### KSpace Accuracy

| Method | Accuracy | Speed | Our constraint |
|---|---|---|---|
| Ewald | Exact (no interpolation) | Slow (O(N^1.5)) | ✅ Works on macOS ARM |
| PPPM | Grid interpolation (controlled by accuracy) | Fast (O(N log N)) | ❌ Crashed on macOS ARM |
| PPPM/TIP4P | Same as PPPM but handles TIP4P virtual site | Fast | ❌ Same crash risk |

**Verdict**: At the same accuracy (1.0e-4), both give identical results. PPPM is just faster. The crash was platform-specific (FFTW on macOS ARM), not an accuracy issue.

### Cutoff Comparison

| Cutoff | LJ accuracy | Coulomb accuracy | Cost |
|---|---|---|---|
| 10.0 Å | Good for SPC/E (σ=3.166) | OK with Ewald | Lower |
| 12.0 Å | Better — less truncation error | Better — less real-space error | ~40% more pairs |

**Verdict**: 12 Å is more accurate but slower. With `pair_modify tail yes`, the analytical LJ tail correction compensates for the shorter cutoff, so 10 Å + tail correction ≈ 12 Å in practice.

### Missing from Both Scripts

| Item | Impact | Fix |
|---|---|---|
| `kspace_modify slab 3.0` | 10× surface tension error | Must add — critical |
| `pair_modify tail yes` (ours) | LJ truncation error on pressure | Should add |
| Separate equilibration (theirs) | Transient data in production | Should add multi-phase |

---

## What's New / Available Now

### 1. TIP4P/2005 — Best Water Model for Interfaces
- Most accurate surface tension among rigid models (68 mN/m)
- Same computational cost as TIP4P
- Well-parameterized: ε = 0.1852 kcal/mol, σ = 3.1589 Å, q_H = 0.5564e, q_M = -1.1128e

### 2. PPPM with Merged Runs
- We already merged equilibration + production into one input file (no kspace reinit)
- **PPPM may now work** since the crash was triggered by kspace reinit between separate `run` commands
- Worth testing before committing to slow Ewald

### 3. `kspace_modify slab 3.0`
- Yeh-Berkowitz correction for slab geometry
- Works with both Ewald and PPPM
- Must be added for any slab simulation

### 4. `pair_modify tail yes`
- Analytical long-range LJ correction
- Adds a pressure and energy correction for LJ interactions beyond the cutoff
- Standard practice — should always be used

### 5. RDF Computation in LAMMPS
- `compute rdf` — validates water structure
- Can restrict to bulk region to avoid interface artifacts

---

## Decision: Batch 3 Strategy

We test **two variants** to find the best setup going forward:

### Variant A: Ewald + SPC/E (safe, known to work)
- Keep Ewald (guaranteed no crash)
- Add `kspace_modify slab 3.0`
- Add `pair_modify tail yes`
- Extend production to 200 ps

### Variant B: PPPM + TIP4P/2005 (faster, more accurate, but may crash)
- Switch to `pppm/tip4p 1.0e-4`
- TIP4P/2005 parameters
- Add `kspace_modify slab 3.0`
- Add `pair_modify tail yes`
- Same multi-phase protocol

**Run Variant A first** (guaranteed to work). Then test Variant B. If PPPM doesn't crash with our merged-run approach, adopt Variant B for all future batches.

---

## Batch 3 Test Input — What to Create

### File: `src/batch3_test.lammps`

**Changes from batch 2:**

```diff
  kspace_style    ewald 1.0e-4
+ kspace_modify   slab 3.0

  pair_coeff      1 1 0.1553 3.166   # O-O
  pair_coeff      2 2 0.0    0.0
  pair_coeff      1 2 0.0    0.0
+ pair_modify     tail yes
```

**Output directory**: `output/batch.3/`

**Production**: 50,000 steps (50 ps) — short enough for a test, long enough for ~10 surface tension data points.

**Additional measurements to add:**

```lammps
# RDF — O-O pair correlation (structural validation)
compute         rdf_OO oxygen rdf 100 1 1
fix             rdf_avg all ave/time 100 50 5000 c_rdf_OO[*] &
                file output/batch.3/rdf_OO.dat mode vector

# Temperature per component (equipartition check)
compute         temp_water water temp
```

### Parameters to Measure in Output

| Measurement | File | What to check |
|---|---|---|
| Surface tension (mN/m) | `surface_tension.dat` | Should be ~61 ± 20 mN/m (SPC/E) |
| Density profile | `density_profile.dat` | Bulk ~1.0 g/cm³, clean sigmoidal |
| O-O RDF | `rdf_OO.dat` | First peak at 2.76 Å, coord ~4.5 |
| Thermo (energy drift) | log file | No systematic drift in total energy |
| Pressure | log file | Average ~0 ± 200 atm |

### Success Criteria for Batch 3

| Metric | Pass | Fail |
|---|---|---|
| Surface tension | 40–80 mN/m | >200 or <0 mN/m |
| Bulk density | 0.95–1.05 g/cm³ | <0.9 or >1.1 |
| RDF first peak | 2.6–2.9 Å | Outside this range |
| Energy drift | <1% over production | Systematic trend |
