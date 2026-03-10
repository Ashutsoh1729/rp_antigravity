# Simulation Analysis: AI Agent Instruction Guide

This document is a **context and instruction manual for AI agents** tasked with analyzing LAMMPS simulations in this project. 

When you (the AI agent) are asked to analyze a simulation output directory, follow these generalized steps. This workflow is designed to adapt as the project evolves from simple air-water interfaces to complex PFAS-water-air systems.

---

## 1. 🔍 Context Gathering (Read First!)

Before writing any analysis code, you MUST read the current project criteria:

1. **Read the Appropriate Validation Criteria**: Explore the `@docs/plan/criteria/` directory.
   - For pure water calibration, use `aw_interface_criteria.md`.
   - For PFAS systems, use `pfas_criteria.md` or other specific criteria files as they emerge.
   - These documents define what "success" looks like for the current phase.

2. **Understand the Simulation Setup**: Check the `.lammps` input script inside the specific simulation's directory (e.g., `src/test/variant_c.lammps`).
   - Note the chosen water model, kspace style, temperature, and any specific groups (e.g., `gH2O`, `pfas_head`).
   - Note which `fix ave/time` or `fix ave/chunk` commands were used so you know what the `.dat` files contain.

3. **Check Existing Analysis Code**: Review scripts in the `analysis/codes/` directory.
   - Analysis scripts MUST be named according to their specific simulation variant (e.g., `analyze_variant_c.py` for `variant_c`), to help manage multiple variants.
   - Reuse existing parsers and plotting functions whenever possible.
   - If a requested metric isn't covered by existing scripts (e.g., calculating Diffusion from MSD), you will need to write a new variant-specific Python script.

---

## 2. 📂 Locating the Data

A simulation output directory typically contains:
- `density_profile.dat` (Z-axis spatial bins)
- `surface_tension.dat` (Pressure tensor derived)
- `rdf.dat` (Radial distribution function)
- `msd.dat` (Mean squared displacement)
- `energy_stability.dat` (Thermodynamic tracking)
- `trajectory.lammpstrj` (Atom positions)
- `log.lammps` (Terminal output)

When the user provides an output directory (e.g., `src/test/output/variant_c`), assume all these data files reside directly within it.

---

## 3. 🐍 Execution Environment (UV) & Code Placement

- All variant-specific analysis code **MUST** be placed in the `analysis/codes/` directory.
- The script **MUST** be named after the variant it analyzes (e.g., `analyze_variant_c.py` for `variant_c`).

This project uses `uv` for Python dependency management. 
**Never use global python or pip.** 

To run an existing script or a new script you've written, use:
```bash
# Run from the project root
uv run python analysis/codes/<script_name>.py <path_to_data_dir> <path_to_save_analysis_output>
```

If you need to write a *new* script that requires dependencies not already in `pyproject.toml`, you can use `uv run --with <package>` or instruct the user to add the dependency.

---

## 4. 📊 Analysis Protocol

When analyzing a simulation, execute the following workflow:

### Step 1: Write and execute variant-specific analysis scripts
If an analysis script for the current variant doesn't exist, create one in `analysis/codes/analyze_<variant_name>.py`.
Run the script via `uv`, passing the specific data directory and the target output directory (e.g., `analysis/output/<variant_name>`) as arguments. Ensure the script saves all its generated outputs (plots, calculated numerical values, and markdown reports detailing what was analyzed) into that specified output folder.

### Step 2: Compare against Appropriate Criteria
Extract the final numerical results (e.g., the converged running average of surface tension, the bulk density value, the RDF peak location). 
Compare these directly against the expected targets found in the relevant file inside `docs/plan/criteria/`.

### Step 3: Identify Anomalies
- **Density**: Is the bulk density correct? Is the interface smooth (sigmoidal)? 
- **Thermodynamics**: Did the temperature stay stable? Is there energy drift indicating a bad integration timestep?
- **Equilibration**: Did the metric (like surface tension) converge, or is it still drifting linearly?

### Step 4: Report to the User
Provide a concise markdown summary to the user:
1. State whether the P0 criteria (Density & Surface Tension) were met.
2. Embed the generated plots.
3. If criteria failed, explicitly hypothesize why based on the simulation script (e.g., "The density is 0.8 g/cm³ because the lattice spacing in the input script was too wide for NVT").
4. Suggest next steps (e.g., "The surface tension is still drifting; recommend running for 500 ps instead of 20 ps").

### Step 5: Save Summary Document
Always write a `report_summary.md` file in the generated output directory (e.g. `analysis/output/variant_d/report_summary.md`) containing the summary you provided to the user in Step 4. This will serve as a physical artifact for future reference.
