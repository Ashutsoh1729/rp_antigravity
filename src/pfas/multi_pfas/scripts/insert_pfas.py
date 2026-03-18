import argparse
import random
import re
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Insert PFAS molecules into a LAMMPS simulation box randomly.")
    parser.add_argument("--template", default="../test_multi.lammps", help="Path to the LAMMPS template file.")
    parser.add_argument("--pfas_data", default="../../data/PFOA_stripped.data", help="Path to the PFAS data file.")
    parser.add_argument("--num_molecules", type=int, default=8, help="Number of molecules to insert.")
    parser.add_argument("--z_range", nargs=2, type=float, default=[5.0, 30.0], help="Z-range for random placement (min max).")
    parser.add_argument("--output", default="sim_random.lammps", help="Name of the generated LAMMPS script.")
    return parser.parse_args()

def infer_box_bounds(template_content):
    """
    Attempts to infer X and Y bounds from the LAMMPS template.
    Looks for 'replicate' command and assumes a 3.106 unit cell (standard for TIP4P/2005 water data used here).
    """
    x_size, y_size = 62.12, 62.12 # Default based on replicate 20 20
    
    # Check for replicate command
    replicate_match = re.search(r"replicate\s+(\d+)\s+(\d+)\s+(\d+)", template_content)
    if replicate_match:
        nx = int(replicate_match.group(1))
        ny = int(replicate_match.group(2))
        # Assuming unit cell size 3.106 Angstroms (standard for this project's TIP4P/2005 water)
        x_size = nx * 3.106
        y_size = ny * 3.106
    
    return (0.0, x_size), (0.0, y_size)

def generate_script(args):
    # 1. Setup absolute paths for key project locations
    script_dir = os.path.dirname(os.path.abspath(__file__))               # src/pfas/multi_pfas/scripts
    pfas_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))      # src/pfas
    src_dir = os.path.abspath(os.path.join(pfas_dir, ".."))               # src
    
    # Resolve the template path
    template_path = args.template
    if not os.path.isabs(template_path):
        abs_path = os.path.abspath(template_path)
        if not os.path.exists(abs_path):
            template_path = os.path.abspath(os.path.join(script_dir, template_path))
        else:
            template_path = abs_path

    try:
        with open(template_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading template: {e}")
        return

    # 2. Setup output directory
    output_dir = os.path.abspath(os.path.join(script_dir, "..", "lammps"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.basename(args.output))

    # 3. Calculate shifts (relative paths from output_dir to targets)
    to_pfas = os.path.relpath(pfas_dir, output_dir)  # Should lead to ../..
    to_src = os.path.relpath(src_dir, output_dir)    # Should lead to ../../..

    # Resolve pfas_data path
    pfas_data_path = args.pfas_data
    if not os.path.isabs(pfas_data_path):
        abs_path = os.path.abspath(pfas_data_path)
        if not os.path.exists(abs_path):
            pfas_data_path = os.path.abspath(os.path.join(script_dir, pfas_data_path))
        else:
            pfas_data_path = abs_path
    
    pfas_data_rel = os.path.relpath(pfas_data_path, output_dir)

    print(f"Generating script at: {output_path}")

    # --- GENERATE INSERTION BLOCK ---
    x_bounds, y_bounds = infer_box_bounds(content)
    z_min, z_max = args.z_range
    
    insertion_block = f"# Automated Insertion of {args.num_molecules} molecules\n"
    for i in range(args.num_molecules):
        x = random.uniform(x_bounds[0], x_bounds[1])
        y = random.uniform(y_bounds[0], y_bounds[1])
        z = random.uniform(z_min, z_max)
        command = f"read_data {pfas_data_rel} add append offset 2 1 1 0 0 shift {x:.3f} {y:.3f} {z:.3f}\n"
        insertion_block += command

    # Replace grid insertion
    pattern = r"# Insert 8 PFOA molecules.*?(?=\n\s*# =+)"
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, insertion_block, content, flags=re.DOTALL)
    else:
        new_content = content + "\n" + insertion_block

    # --- AUTOMATIC PATH FIXES ---
    # Fix output: output/ -> ../output/
    new_content = new_content.replace("shell mkdir -p output", "shell mkdir -p ../output")
    new_content = new_content.replace("output/", "../output/")

    # Fix resources:
    # 1. Water data: ../test/ -> {to_src}/test/
    new_content = new_content.replace("../test/", f"{to_src}/test/")
    
    # 2. Force fields: ff_params/ -> {to_pfas}/ff_params/
    new_content = new_content.replace("ff_params/", f"{to_pfas}/ff_params/")
    
    # 3. Local data: data/ -> {to_pfas}/data/
    new_content = re.sub(r"(?<!/)\bdata/", f"{to_pfas}/data/", new_content)

    with open(output_path, 'w') as f:
        f.write(new_content)
    
    print(f"Success: Generated simulation script {output_path}")

if __name__ == "__main__":
    args = parse_args()
    generate_script(args)
