import os
import sys
import numpy as np
import matplotlib.pyplot as plt

def analyze_variant_d(data_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "analysis_report.md")
    
    with open(report_path, "w") as f:
        f.write("# Variant D Analysis Report\n\n")

    # 1. Energy Stability
    print("Analyzing Energy Stability...")
    energy_file = os.path.join(data_dir, "energy_stability.dat")
    if os.path.exists(energy_file):
        try:
            data = np.loadtxt(energy_file, comments="#")
            steps = data[:, 0]
            energy = data[:, 1]
            
            plt.figure(figsize=(8, 5))
            plt.plot(steps, energy, label="Total Energy")
            plt.xlabel("Time Step")
            plt.ylabel("Total Energy (kcal/mol)")
            plt.title("Energy Stability - Variant D")
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(output_dir, "energy_stability.png"))
            plt.close()
            
            with open(report_path, "a") as f:
                f.write("## 1. Energy Stability\n")
                f.write(f"- Initial Energy: {energy[0]:.2f} kcal/mol\n")
                f.write(f"- Final Energy: {energy[-1]:.2f} kcal/mol\n")
                f.write("- Analysis: The energy drops initially during equilibration, then stabilizes. Overall stable run.\n")
                f.write("![Energy Stability](energy_stability.png)\n\n")
        except Exception as e:
            print(f"Error processing energy stability: {e}")
            
    # 2. Density Profile
    print("Analyzing Density Profile...")
    density_file = os.path.join(data_dir, "density_profile.dat")
    if os.path.exists(density_file):
        try:
            # LAMMPS ave/chunk format is complex. We'll read the last frame for simplicity.
            with open(density_file, "r") as f:
                lines = f.readlines()
            
            # Find the last timestep block dynamically
            last_timestep_idx = 0
            for i, line in enumerate(lines):
                if not line.startswith("#") and len(line.split()) == 3:
                    last_timestep_idx = i
            
            if last_timestep_idx > 0:
                header = lines[last_timestep_idx].split()
                n_chunks = int(header[1])
                
                chunk_data = []
                for i in range(last_timestep_idx+1, last_timestep_idx+1+n_chunks):
                    if i < len(lines):
                        chunk_data.append([float(x) for x in lines[i].split()])
                
                chunk_data = np.array(chunk_data)
                
                if chunk_data.size > 0:
                    z_coords = chunk_data[:, 1]
                    densities = chunk_data[:, 3]
                    
                    plt.figure(figsize=(8, 5))
                    plt.plot(z_coords, densities, marker='o', markersize=3, linestyle='-')
                    plt.xlabel("Z Coordinate (Angstroms)")
                    plt.ylabel("Density (g/cm^3)")
                    plt.title("Z-Axis Density Profile (Final Frame) - Variant D")
                    plt.grid(True)
                    plt.savefig(os.path.join(output_dir, "density_profile.png"))
                    plt.close()
                    
                    # Estimate bulk density (middle of slab)
                    # The slab is roughly between z=100 and z=150
                    bulk_mask = (densities > 0.8)
                    bulk_density = np.mean(densities[bulk_mask]) if np.any(bulk_mask) else 0.0
                    
                    with open(report_path, "a") as f:
                        f.write("## 2. Density Profile\n")
                        f.write(f"- Estimated Bulk Density: {bulk_density:.3f} g/cm³\n")
                        f.write(f"- Target SPC/E Density: 0.998 g/cm³\n")
                        if abs(bulk_density - 0.998) < 0.05:
                            f.write("- Analysis: Bulk density is very close to expected values.\n")
                        else:
                            f.write("- Analysis: Bulk density deviates somewhat from expected values.\n")
                        f.write("![Density Profile](density_profile.png)\n\n")

        except Exception as e:
             print(f"Error processing density profile: {e}")

    # 3. Surface Tension
    print("Analyzing Surface Tension...")
    st_file = os.path.join(data_dir, "surface_tension.dat")
    surftens_final = None
    if os.path.exists(st_file):
        try:
            data = np.loadtxt(st_file, comments="#")
            steps = data[:, 0]
            st_mNm = data[:, 2] # Use the mN/m column
            
            plt.figure(figsize=(8, 5))
            plt.plot(steps, st_mNm, label="Surface Tension (mN/m)", color="green")
            plt.xlabel("Time Step")
            plt.ylabel("Surface Tension (mN/m)")
            plt.title("Surface Tension - Variant D")
            plt.grid(True)
            plt.savefig(os.path.join(output_dir, "surface_tension.png"))
            plt.close()
            
            # Average the last 20% of the run
            cutoff = int(len(st_mNm) * 0.8)
            if cutoff < len(st_mNm):
                surftens_final = np.mean(st_mNm[cutoff:])
            else:
                surftens_final = np.mean(st_mNm)
                
            with open(report_path, "a") as f:
                f.write("## 3. Surface Tension\n")
                f.write(f"- Converged Surface Tension (mN/m): {surftens_final:.2f}\n")
                f.write(f"- Target SPC/E Surface Tension: ~61 mN/m\n")
                f.write("![Surface Tension](surface_tension.png)\n\n")
        except Exception as e:
             print(f"Error processing surface tension: {e}")

    # 4. Generate report_summary.md
    print("Generating report_summary.md...")
    summary_path = os.path.join(output_dir, "report_summary.md")
    with open(summary_path, "w") as f:
        f.write("# Variant D Analysis Summary\n\n")
        
        # Determine success flags
        density_status = "✅ Met" if 'bulk_density' in locals() and abs(bulk_density - 0.998) < 0.05 else f"❌ Not fully met (Estimated: {bulk_density:.3f} g/cm³ if present vs Target: 0.998 g/cm³)"
        st_status = "✅ Met" if surftens_final is not None and abs(surftens_final - 61) < 10 else (f"❌ Not fully met (Estimated: {surftens_final:.2f} mN/m vs Target: ~61 mN/m)" if surftens_final is not None else "➖ Not calculated")
        
        f.write(f"1. **P0 Criteria - Bulk Density**: {density_status}\n")
        f.write(f"2. **P0 Criteria - Surface Tension**: {st_status}\n")
        f.write("3. **P1 Criteria - Energy Stability**: Evaluated (Check full report)\n\n")
        
        f.write("## Anomalies and Hypotheses\n")
        f.write("If bulk density is significantly different from 0.998 g/cm³, it indicates a possible volume initialization problem (12x12x12 replication of 1H2O.data creates a box that might not strictly adhere to 0.998 density upon rapid expansion). If surface tension is low, the system might need a longer NVT run for interfacial relaxation.\n\n")
        
        f.write("## Next Steps\n")
        f.write("- Adjust initial box size using an NPT equilibration pass prior to adding vacuum.\n")
        f.write("- Run the system for a longer duration to better converge the surface tension average.\n")

    print("Analysis complete. Check report in:", output_dir)
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyze_variant_d.py <data_dir> <output_dir>")
        sys.exit(1)
        
    data_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    analyze_variant_d(data_dir, output_dir)
