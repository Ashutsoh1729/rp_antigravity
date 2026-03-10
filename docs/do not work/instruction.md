# `do not work` Directory Instructions

This directory is intended to serve as a graveyard and reference guide for LAMMPS simulation setups and command combinations that **do not work together**.

When an AI agent discovers a fundamentally incompatible setup or a command combination that leads to crashes or incorrect physics:

1. **Short Incompatibilities**: If the issue is simple and can be explained in just a few sentences, append it directly to `summery.md`.
2. **Complex Incompatibilities**: If the issue is complex and requires detailed explanations, extensive log outputs, or code examples, create a **separate, distinctly named Markdown file** in this directory to thoroughly document it.

Before embarking on modifying simulation setups (especially around different `kspace_style` or `boundary` parameters), AI agents should always consult the files in this directory to avoid repeating known mistakes.
