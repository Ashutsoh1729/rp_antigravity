# Molecule Generation Dependency Errors Log

This document records the cascading dependency errors encountered while attempting to dynamically generate the LAMMPS `PFOA.data` file for the pure PFAS simulation, and the solutions implemented to resolve them.

## 1. The `openff-interchange` Pip Yank Error (uv/pip Failure)
Initially, `uv` (which proxies pip) was used to install `openff-toolkit` and `openff-interchange`. However, the pip version of `openff-interchange` was completely yanked from PyPI by its authors because it requires complex C++ bindings that pip cannot compile easily on Apple Silicon.
- **Error output:** `Because only openff-interchange==0.5.1 is available and was yanked... your project's requirements are unsatisfiable.`
- **Result:** Pure pip/uv environments are unsuitable for modern OpenFF parameterization.

## 2. The `mbuild` / `oset` Python 3.13 Rot (Alternative strategy failure)
To avoid OpenFF's pip issues, the Python script was rewritten to use older, pip-friendly libraries (`mbuild` and `foyer`). However, `mbuild` silently depends on a tiny legacy library called `oset`.
- **The Issue:** `oset` explicitly imports `collections.MutableSet`. That specific class was permanently deleted from Python in version 3.10. Since the environment was running Python 3.13, `import mbuild` instantly crashed with an `ImportError`. 
- **Temporary fix attempted:** Monkey-patching Python (`collections.MutableSet = collections.abc.MutableSet`) resolved the `oset` crash, but the stack immediately crashed on another strictly missing dependency (`ele`).
- **Result:** `mbuild` is experiencing severe bit-rot on modern Python.

## 3. The Move to Micromamba (The Solution)
Because standard Python package managers (pip/uv) were failing identically on complex C++ scientific stacks, a local, isolated instance of `micromamba` was installed directly inside `scripts/generate_molecules/`.
- **Why:** Micromamba pulls directly from `conda-forge`, which hosts perfectly pre-compiled Apple Silicon binaries for all `openff` modules.

## 4. The Final Hurdle (`pkg_resources` missing)
When `generate_pfoa.py` was executed inside the new pristine micromamba environment, OpenFF threw one final error:
- **Error output:** `ModuleNotFoundError: No module named 'pkg_resources'`
- **Why:** The conda-forge environment installed pure Python and OpenFF, but unlike a full Anaconda release, it omitted the `setuptools` module (which provides `pkg_resources`).
- **Fix:** Explicitly running `micromamba install -y -n pfas setuptools -c conda-forge`.
