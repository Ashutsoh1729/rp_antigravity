# Brainstorm: How to Validate Our Simulation Against Reality

How do we know our air-water interface simulation is physically correct? Below are the measurable quantities we can extract from LAMMPS and compare against experimental or well-established computational benchmarks.

---

## 1. Thermodynamic Properties

### 1.1 Bulk Water Density
- **What**: Average mass density in the flat interior of the slab (away from interfaces)
- **Expected**: SPC/E model → **0.998 g/cm³** at 300 K, 1 atm  
  Experimental → 0.997 g/cm³
- **How to measure**: From `density_profile.dat`, take the mean of bins where density > 0.8 g/cm³
- **Sensitivity**: Tells us if the number of molecules and box geometry are correct

### 1.2 Surface Tension (γ)
- **What**: Energy cost per unit area of creating the interface
- **Expected**: SPC/E → **61 ± 3 mN/m** at 300 K  
  Experimental → 72.0 mN/m (SPC/E systematically underestimates)
- **How to measure**: From pressure tensor: γ = ½ · Lz · (Pzz − ½(Pxx + Pyy))
- **Sensitivity**: Most sensitive to force field accuracy, kspace treatment, and slab correction

### 1.3 Pressure
- **What**: Average isotropic pressure in the bulk region
- **Expected**: Near 0 ± ~200 atm (fluctuations are large for small systems in NVT)
- **How to measure**: From thermo output, average `press` over production phase
- **Sensitivity**: Large fluctuations are normal; systematic offset indicates density error

---

## 2. Structural Properties

### 2.1 Density Profile Shape
- **What**: ρ(z) across the box — should show flat bulk + sigmoidal interface
- **Expected**: Hyperbolic tangent profile at each interface:  
  ρ(z) = ½(ρ_l + ρ_v) − ½(ρ_l − ρ_v) · tanh((z − z₀) / d)  
  where d ≈ 2-3 Å (interfacial width, "10-90 thickness")
- **How to measure**: Fit tanh to the density profile edges
- **Sensitivity**: Interface width tells us if the surface is physically realistic

### 2.2 Interfacial Width (10-90 thickness)
- **What**: Distance over which density drops from 90% to 10% of bulk
- **Expected**: ~3-4 Å for SPC/E at 300 K
- **How to measure**: From tanh fit parameter `d`, thickness = 2.197 × d
- **Sensitivity**: Too thin = not equilibrated; too thick = temperature too high or system unstable

### 2.3 Radial Distribution Function g(r)
- **What**: O-O, O-H, H-H pair correlation functions in the bulk region
- **Expected**: First O-O peak at ~2.76 Å, coordination number ~4.5
- **How to measure**: `compute rdf` in LAMMPS, restrict to bulk water region
- **Sensitivity**: Validates force field and structural ordering

### 2.4 Hydrogen Bond Statistics
- **What**: Average number of H-bonds per molecule, bond lifetimes
- **Expected**: ~3.5 H-bonds/molecule for SPC/E at 300 K (exp: ~3.6)
- **How to measure**: Geometric criterion: O-O < 3.5 Å, H-O···O angle < 30°
- **Sensitivity**: Indicates if hydrogen bonding network is realistic

---

## 3. Dynamic Properties

### 3.1 Self-Diffusion Coefficient (D)
- **What**: How fast water molecules move — calculated from mean square displacement
- **Expected**: SPC/E → **2.4 × 10⁻⁵ cm²/s** at 300 K  
  Experimental → 2.3 × 10⁻⁵ cm²/s  
  (SPC/E is known to slightly overestimate)
- **How to measure**: `compute msd` in LAMMPS, fit slope = 6D (3D) 
- **Sensitivity**: Tells us dynamics are correct; sensitive to thermostat coupling

### 3.2 Velocity Autocorrelation Function
- **What**: Correlation of velocity over time — Fourier transform gives vibrational density of states
- **Expected**: Librational peak ~500 cm⁻¹, O-H stretch ~3400 cm⁻¹ (if flexible model)
- **How to measure**: `compute vacf` in LAMMPS
- **Sensitivity**: Validates dynamics, but SPC/E is rigid so O-H stretch is absent

---

## 4. Interfacial Properties

### 4.1 Molecular Orientation at Interface
- **What**: Preferred orientation of water dipole relative to the surface normal
- **Expected**: Water molecules at the interface prefer to point one O-H bond toward the vapor
- **How to measure**: Compute cos(θ) profile where θ = angle between dipole and z-axis
- **Sensitivity**: Directly tests interfacial structure

### 4.2 Capillary Wave Spectrum
- **What**: Fluctuations of the interface position — should follow capillary wave theory
- **Expected**: ⟨|h(q)|²⟩ = k_BT / (γ · q²) for small q
- **How to measure**: Track instantaneous interface position per xy-grid cell over time, Fourier transform
- **Sensitivity**: Advanced validation — confirms surface tension is consistent with interface fluctuations

### 4.3 Surface Excess / Gibbs Dividing Surface
- **What**: Location where the integrated density equals bulk × slab thickness
- **Expected**: Should be at the inflection point of ρ(z)
- **How to measure**: Numerical integration of density profile

---

## 5. Energy and Temperature Checks

### 5.1 Energy Conservation / Drift
- **What**: Total energy should be stable (NVT) or conserved (NVE)
- **Expected**: No systematic drift in total energy over production run
- **How to measure**: Plot total energy vs time from thermo output as well as log file outputs
- **Sensitivity**: Drift means timestep too large, SHAKE not converging, or bad force field

### 5.2 Temperature Distribution
- **What**: Instantaneous temperature should fluctuate around 300 K
- **Expected**: ⟨T⟩ = 300 K, σ_T ≈ √(2/(3N)) × 300 ≈ few K
- **How to measure**: From thermo output
- **Sensitivity**: Wrong fluctuation magnitude = wrong degrees of freedom count

### 5.3 Equipartition Check
- **What**: KE per degree of freedom should be ½k_BT
- **Expected**: KE/N_dof = 0.298 kcal/mol at 300 K
- **How to measure**: Compare KE from thermo to expected value
- **Sensitivity**: SHAKE removes DOF — check that LAMMPS accounts for this

---

## Priority for Our Simulation

| Priority | Metric | Why |
|---|---|---|
| 🔴 P0 | Bulk density | If wrong, everything else is meaningless |
| 🔴 P0 | Surface tension | Primary quantity of interest |
| 🟡 P1 | Density profile shape (tanh fit) | Validates interface structure |
| 🟡 P1 | Energy stability | Ensures simulation is trustworthy |
| 🟢 P2 | RDF g(r) | Structural validation |
| 🟢 P2 | Diffusion coefficient | Dynamic validation |
| 🔵 P3 | Molecular orientation | Advanced interfacial analysis |
| 🔵 P3 | Capillary waves | Research-level validation |
