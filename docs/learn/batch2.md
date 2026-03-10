# Batch 2 — Analysis & Learnings

**Run duration**: 60 ps total (10 ps heating + 40 ps equilibration + 10 ps production)  
**Changes from Batch 1**: Tighter lattice (3.1 Å), multi-phase protocol, data collection only during production, surface tension in mN/m

---

## Density Profile Analysis

### Last Snapshot (Timestep 60000)
- **Slab position**: z ≈ 30–90 Å — exactly where we placed it. **No drift or contraction.** ✅
- **Bulk density**: Fluctuating between 0.87–1.04 g/cm³ across bins — noisy but centered around the right value
- **Interface shape**: Clean sigmoidal edges on both sides — much sharper than batch 1

### Time-Averaged Profile
- **Bulk average**: **0.956 g/cm³** (vs 0.65 g/cm³ in batch 1) — 47% improvement
- **Gap from experimental**: Only ~4.4% below 1.0 g/cm³
- **Interfacial width**: Looks like ~4–5 Å (10-90 thickness) — reasonable for SPC/E
- **Standard deviation**: Small in the bulk (tight shaded band), larger near interfaces — expected behavior

### Batch 1 vs Batch 2 Comparison
The comparison plot makes the improvement visually obvious:

| Metric | Batch 1 | Batch 2 |
|---|---|---|
| Bulk density | ~0.65 g/cm³ | **0.956 g/cm³** |
| Slab width | Contracting over time | Stable |
| Interface shape | Jagged, rough | Clean sigmoidal |
| Data quality | Contaminated by equilibration transients | Clean production-only data |

**Root cause of improvement**: The tighter lattice (3.1 Å vs 3.5 Å) gave near-correct initial density, eliminating the need for the slab to contract. The 50 ps equilibration then let the structure fully relax before data collection.

---

## Surface Tension Analysis

| Timestep | γ (atm·Å) | γ (mN/m) |
|---|---|---|
| 55000 | 5583.89 | 565.8 |
| 60000 | 7075.81 | 717.0 |
| **Average** | **6329.85** | **641.4** |
| **Expected (SPC/E)** | ~600 | ~61 |

### What's wrong

The surface tension is **~10× too high**. This is a severe quantitative error. The density is nearly correct, but γ is wildly off.

**Primary suspect: Missing kspace slab correction.**

Without `kspace_modify slab 3.0`, the Ewald solver treats the system as fully 3D periodic. This means:
1. The water slab at z = 30–90 sees an electrostatic **image** of itself across the z-boundary (only ~30 Å of vacuum separating them)
2. This creates an artificial dipole-dipole interaction between slab images
3. The spurious interaction inflates the anisotropy of the pressure tensor (Pzz becomes much larger than Pxx, Pyy)
4. Since γ = ½ · Lz · (Pzz − ½(Pxx + Pyy)), the inflated Pzz gives inflated γ

**Secondary factors**:
- Only 2 data points — far too few for convergence. Surface tension needs hundreds of samples over 200+ ps
- 10 ps production is not enough for the pressure tensor to sample ergodically

---

## Energy and Temperature

From the log file (Phase 3 equilibration):
- **Temperature**: Fluctuating around 300 K ± 8 K — well-controlled by Nosé-Hoover ✅
- **Potential energy**: Stabilized around −17,700 kcal/mol — no systematic drift ✅
- **Pressure**: Oscillating around −100 ± 200 atm — typical for NVT (no barostat)

---

## Key Takeaways

### What worked ✅
1. **Density is correct** — 0.956 g/cm³ is within 5% of experiment
2. **Slab is stable** — no contraction, no drift, interfaces stay put
3. **Multi-phase protocol worked** — clean separation of equilibration and production
4. **Temperature is well-controlled** — Nosé-Hoover thermostat works correctly

### What needs fixing ❌
1. **Missing `kspace_modify slab 3.0`** — likely responsible for 10× surface tension error
2. **Production too short** — 10 ps gives only 2 averaged data points
3. **Not enough statistics** — need hundreds of surface tension samples to converge

---

## Recommendations for Batch 3

| Change | Why |
|---|---|
| Add `kspace_modify slab 3.0` | Fix spurious slab-image electrostatic interaction |
| Production: 200 ps minimum | Get ~40 averaged surface tension data points |
| Consider `kspace_modify slab/volfactor 3.0` | Alternative syntax if `slab` alone doesn't work |
| Add RDF calculation | Structural validation (O-O, O-H pair correlations) |
| Add tanh fit to density profile | Quantify interfacial width |
