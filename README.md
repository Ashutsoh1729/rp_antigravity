# PFAS Air-Water Interface Simulation Project

This project automates the setup and execution of Molecular Dynamics simulations for PFAS molecules (specifically PFOA) at an air-water interface using LAMMPS.

## 1. Prerequisites (Installation)

This project uses **go-task** to manage commands. 

**To install Task:**
Please follow the official instructions for your Operating System:
👉 **[Task Installation Guide](https://taskfile.dev/installation/)**

*Quick install for Mac (Homebrew):*
```bash
brew install go-task/tap/go-task
```

## 2. Available Commands

Run these commands from the project root directory.

| Command | Usage | Description |
| :--- | :--- | :--- |
| `task install-lammps` | `task install-lammps` | Automatically downloads and installs LAMMPS on your system. |
| `task prod` | `task prod -- <cores>` | Runs the final 20-PFAS upper interface simulation (using `20pfas_upper.lammps`). |
| `task run` | `task run -- <file> <cores>` | Runs any LAMMPS file with a specified number of CPU cores. |
| `task run-8` | `task run-8 -- <file>` | Shortcut to run a simulation using 8 cores. |
| `task run-4` | `task run-4 -- <file>` | Shortcut to run a simulation using 4 cores. |

---

## 3. Project Structure

```text
.
├── Taskfile.yml           # Automation task definitions
├── analysis/              # Python analysis scripts and result plots
├── docs/                  # Project planning, theory, and error logs (RCAs)
├── scripts/               # Utility scripts (installers, molecule parameterization)
├── src/                   # Simulation source files
│   ├── test/              # Base water data and initial test variants
│   └── pfas/              # PFAS resources (force fields, data files)
│       ├── data/          # Parameterized PFAS molecule data (PFOA_stripped.data)
│       ├── ff_params/     # Force field include files (OPLS-AA/GAFF)
│       └── multi_pfas/    # Multi-molecule simulation environment
│           ├── scripts/   # PFAS insertion tools (insert_pfas.py)
│           ├── lammps/    # Generated LAMMPS simulation scripts
│           └── output/    # Centralized simulation output (trajectories, COM data)
└── README.md              # Project overview and usage guide
```

## 4. Key Files

- **`insert_pfas.py`**: A path-aware Python script to randomly insert molecules into a template.
- **`20pfas_upper.lammps`**: The production-ready LAMMPS script optimized for interface adsorption.
- **`rca_atomic_clash.md`**: Root Cause Analysis of previous simulation crashes and how they were resolved (Minimization).
