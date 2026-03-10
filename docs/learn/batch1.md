# Batch 1 — Analysis & Learnings

## What the Data Shows

### Density Profile

| Observation | Detail |
|---|---|
| **Slab position** | Started at z = 30–90 Å, contracted to z ≈ 35–83 Å by timestep 5000 |
| **Bulk density** | Time-averaged ~0.65 g/cm³, rising to ~0.8–0.98 g/cm³ at the end |
| **Expected** | SPC/E water at 300 K should be ~1.0 g/cm³ |
| **Interface shape** | Rough but present; sigmoidal edges visible at both surfaces |
| **Slab thickness** | Shrinking over time — the slab is collapsing inward because it was initialized under-dense |

**The slab is contracting** because we placed water on a 3.5 Å lattice (lower than bulk density). The attractive forces pull molecules inward, compressing the slab. By timestep 5000, density is approaching ~0.9 g/cm³ but hasn't equilibrated yet.

### Surface Tension

| Observation | Detail |
|---|---|
| **Early values** | Negative (−7500 to −1700 atm·Å) — unphysical, system far from equilibrium |
| **Trend** | Steadily increasing, not converged (still drifting upward at step 5000) |
| **Late values** | ~8000–30000 atm·Å — wildly fluctuating |
| **Expected** | SPC/E at 300 K ≈ 61 mN/m ≈ ~610 atm·Å (after unit conversion) |
| **Currently** | Orders of magnitude too high — the slab is still restructuring |

**The surface tension is meaningless in this run** because:
1. The system hasn't equilibrated (slab is still contracting)
2. 5 ps is far too short — surface tension needs >100 ps of *equilibrated* data
3. The pressure tensor is dominated by structural rearrangement, not the actual interface

---

## Root Causes

1. **Under-dense initial state** — 3.5 Å lattice gives ~65% of bulk water density. The slab spends the entire run trying to reach the correct density.
2. **No pre-equilibration** — We go straight from minimization into the production run. There's no separate NPT/NVT equilibration to let the slab reach a stable state before collecting data.
3. **Too short** — 5 ps is not enough for even basic structural relaxation of water. Water dynamics typically need 50–100 ps just to equilibrate.
4. **NVT on under-dense system** — NVT holds volume constant. Since we start under-dense, the slab can't reach proper density by expanding. Instead it contracts into a denser, thinner slab, shifting the interfaces.

---

## Suggested Modifications for Batch 2

### Priority 1: Fix the Initial Density
- Use `lattice sc 3.1` (the original value) but now with Ewald instead of PPPM, so the FFTW crash won't happen
- OR use `lattice fcc 4.4` which packs more molecules at correct density
- **Goal**: Start as close to 1.0 g/cm³ as possible

### Priority 2: Add a Proper Equilibration Protocol
Split the simulation into phases:
1. **Minimization** — 1000 steps (CG)
2. **NVT heating** — 20 ps, ramp 100→300 K, let the structure relax
3. **NVT equilibration** — 50 ps at 300 K, let the slab stabilize
4. **Production** — 200+ ps at 300 K, collect data only here

### Priority 3: Longer Production Run
- Minimum 200 ps (200,000 steps) for meaningful surface tension
- Better: 500 ps–1 ns for converged statistics
- Collect density profile every 1000 steps (not every 100)

### Priority 4: Correct Surface Tension Units
- Current output is in atm·Å — convert to **mN/m** by multiplying by **0.101325** (1 atm·Å = 0.101325 mN/m)
- Update `visualize.py` to do this conversion automatically

### Priority 5: Separate Data Collection from Equilibration
- Only start `fix ave/chunk` and `fix ave/time` *after* equilibration is complete
- Equilibration data contaminates the averages

### Optional: Performance
- Ewald is O(N²), will be slow for large systems
- If PPPM crash is resolved (e.g., updating LAMMPS or FFTW), switch back for 10× speedup
- For now, Ewald is fine for ~1000 molecules

---

## Expected Outcome After Fixes
- Bulk density: ~1.0 g/cm³ (flat in the middle of the slab)
- Surface tension: ~55–65 mN/m (SPC/E literature value at 300 K)
- Density profile: smooth sigmoidal interface, 10-90 width ~3–4 Å
- No slab migration or contraction
