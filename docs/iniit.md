# PFAS Behavior at the Air-Water Interface

## Goal

Simulate the molecular-level behavior of **PFAS (Per- and Polyfluoroalkyl Substances)** at the air-water interface using LAMMPS molecular dynamics. The end objective is to understand:

1. **How PFAS molecules partition** between bulk water and the interface at varying concentrations
2. **How different PFAS types** (varying chain lengths, head groups) affect interfacial structure
3. **How surface tension changes** as a function of PFAS type and concentration
4. **Competitive adsorption** — when multiple PFAS types are present at different ratios, which dominates the interface?

### Target Simulation

A multi-component PFAS mixture at the air-water interface, for example:

| PFAS Type | Example | Concentration |
|---|---|---|
| Type A (short-chain) | PFBA (C₄) | 0.2% |
| Type B (long-chain) | PFOA (C₈) | 0.5% |
| Type C (sulfonated) | PFOS (C₈-SO₃) | 0.3% |

We will vary these concentrations and types systematically to map out the interfacial behavior.

---

## Method — How We Get There

### Phase 1: Pure Water Baseline ← **WE ARE HERE**
Build a validated air-water interface simulation with SPC/E water. This gives us the reference system (correct density, surface tension) before introducing PFAS.

**Steps:**
1. ~~Create SPC/E water model and LAMMPS input script~~
2. ~~Debug and optimize for macOS ARM (Ewald workaround)~~
3. ~~Achieve correct bulk density (~1.0 g/cm³)~~
4. Achieve correct surface tension (~61 mN/m for SPC/E)
5. Validate structural properties (RDF, interfacial width)

### Phase 2: Single PFAS at Interface
Introduce one PFAS molecule type at the air-water interface. Validate its interfacial behavior.

**Steps:**
1. Select force field for PFAS (OPLS-AA or GAFF with fluorine parameters)
2. Create PFAS molecule template (.mol file) for LAMMPS
3. Place PFAS molecules at/near the interface
4. Equilibrate and verify PFAS adsorption at the interface
5. Measure: surface tension reduction, density profile with PFAS, orientation at interface

### Phase 3: Concentration Dependence
Run the same PFAS type at multiple concentrations to build an adsorption isotherm.

**Steps:**
1. Define concentration series (e.g., 0.01%, 0.05%, 0.1%, 0.5%, 1.0%)
2. Run simulation at each concentration
3. Measure surface tension vs concentration (Gibbs adsorption isotherm)
4. Measure surface excess concentration (Γ)
5. Compare with experimental CMC and surface tension curves

### Phase 4: Multi-Component Mixtures
Introduce 2–3 PFAS types simultaneously at different ratios.

**Steps:**
1. Create molecule templates for each PFAS type (A, B, C)
2. Place molecules at specified ratios
3. Run and observe competitive adsorption
4. Measure: which PFAS dominates the interface? How does chain length affect it?
5. Analyze: interfacial composition vs bulk composition

### Phase 5: Analysis & Publication
Comprehensive analysis and comparison with experimental data.

**Steps:**
1. Compile all results across concentrations and types
2. Calculate free energy of adsorption for each PFAS type
3. Compare with experimental surface tension isotherms
4. Identify trends: chain length effect, head group effect, competitive behavior

---

## Current Position

### ✅ Completed
- SPC/E water model created (`water.mol`)
- LAMMPS input script built and debugged (`air_water_interface.lammps`)
- Ewald kspace workaround for macOS ARM segfault
- **Batch 1**: Initial test run — identified under-dense problem (0.65 g/cm³)
- **Batch 2**: Tighter lattice + multi-phase protocol — density fixed to **0.956 g/cm³**

### 🔄 In Progress (Phase 1)
- Surface tension correction: need `kspace_modify slab 3.0` (batch 2 gives 641 mN/m instead of 61 mN/m)
- Longer production run needed (200+ ps)

### ⏳ Not Started
- Phases 2–5 (PFAS introduction)

---

## Documentation Map

| Path | What |
|---|---|
| `docs/iniit.md` | This file — project overview and navigation |
| `docs/learn/brainstorm.md` | Validation metrics brainstorm |
| `docs/learn/batch1.md` | Batch 1 analysis and learnings |
| `docs/learn/batch2.md` | Batch 2 analysis and learnings |
| `docs/modify/001_batch1_initial.md` | Batch 1 script modification log |
| `docs/modify/002_batch2_improvements.md` | Batch 2 script modification log |
| `docs/outputs.md` | Output file descriptions |
| `analysis/visualize.py` | General visualization script |
| `analysis/batches/batch2.py` | Batch 2 specific analysis |
