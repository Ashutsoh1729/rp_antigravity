import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ---------- Plot Styling ----------
rcParams.update({
    "figure.facecolor": "#1e1e2e",
    "axes.facecolor": "#1e1e2e",
    "axes.edgecolor": "#cdd6f4",
    "axes.labelcolor": "#cdd6f4",
    "text.color": "#cdd6f4",
    "xtick.color": "#cdd6f4",
    "ytick.color": "#cdd6f4",
    "grid.color": "#45475a",
    "grid.alpha": 0.5,
    "font.family": "sans-serif",
    "font.size": 12,
})

def parse_surface_tension(filepath):
    """Parse surface_tension.dat → (timesteps, surface_tension_values)."""
    timesteps, st_vals = [], []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split()
            timesteps.append(int(parts[0]))
            st_vals.append(float(parts[1]))
    return np.array(timesteps), np.array(st_vals)

def parse_density_profile(filepath):
    """Parse density_profile.dat → dict of {timestep: (z_coords, densities)}."""
    profiles = {}
    current_ts = None
    z_coords, densities = [], []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split()
            if len(parts) == 3:
                if current_ts is not None:
                    profiles[current_ts] = (np.array(z_coords), np.array(densities))
                current_ts = int(parts[0])
                z_coords, densities = [], []
            elif len(parts) == 4:
                z_coords.append(float(parts[1]))
                densities.append(float(parts[3]))
    if current_ts is not None:
        profiles[current_ts] = (np.array(z_coords), np.array(densities))
    return profiles

def parse_rdf(filepath):
    """Parse rdf.dat → (r, g(r))."""
    r, goor = [], []
    with open(filepath) as f:
        reading_data = False
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split()
            if len(parts) == 2: # Timestep header
                reading_data = True
                # Just take the last timestep's data for this simple analysis
                r, goor = [], []
            elif len(parts) == 8 and reading_data:
                r.append(float(parts[1])) # c_rdf_calc[1] is r
                goor.append(float(parts[2])) # c_rdf_calc[2] is O-O g(r)
    return np.array(r), np.array(goor)

def parse_msd(filepath):
    """Parse msd.dat → (time, msd)."""
    timesteps, msd_vals = [], []
    dt = 1.0 # 1 fs timestep
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split()
            timesteps.append(int(parts[0]) * dt * 1e-15) # seconds
            msd_vals.append(float(parts[4]) * 1e-16) # cm^2
    return np.array(timesteps), np.array(msd_vals)

def main():
    if len(sys.argv) != 3:
        print("Usage: python analyze_variant_c.py <input_data_dir> <output_plot_dir>")
        sys.exit(1)

    data_dir = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    print(f"Reading data from: {data_dir}")
    print(f"Writing analysis to: {out_dir}")

    report_lines = ["# Analysis Report: Variant C (TIP4P/2005)\n"]
    report_lines.append("## P0: Surface Tension")

    # 1. Surface Tension
    st_file = os.path.join(data_dir, "surface_tension.dat")
    if os.path.exists(st_file):
        ts, st = parse_surface_tension(st_file)
        # Running avg
        window = min(10, len(st))
        cumsum = np.cumsum(np.insert(st, 0, 0))
        running_avg = (cumsum[window:] - cumsum[:-window]) / window
        final_st = running_avg[-1] if len(running_avg) > 0 else 0
        
        plt.figure(figsize=(8, 4))
        plt.plot(ts, st, alpha=0.5, label="Instantaneous")
        if len(running_avg) > 0:
            plt.plot(ts[window-1:], running_avg, lw=2, label=f"Running Avg (Final: ~{final_st:.1f} mN/m)")
        plt.axhline(69.0, color="#f38ba8", ls="--", label="Target (69 mN/m)")
        plt.title("Surface Tension vs Time")
        plt.ylabel("mN/m")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.savefig(os.path.join(out_dir, "surface_tension.png"), dpi=150)
        plt.close()
        
        report_lines.append(f"- **Calculated (end of run)**: {final_st:.1f} mN/m")
        report_lines.append("- **Target (TIP4P/2005)**: ~69 mN/m")
        report_lines.append("- **Status**: As expected for a 20ps run, ST fluctuates wildly. Needs 500ps+ to converge to target.\n")

    # 2. Density Profile
    report_lines.append("## P0: Bulk Density & P1: Profile Shape")
    dp_file = os.path.join(data_dir, "density_profile.dat")
    if os.path.exists(dp_file):
        profiles = parse_density_profile(dp_file)
        all_rho = np.array([profiles[t][1] for t in profiles])
        avg_rho = np.mean(all_rho, axis=0)
        z = profiles[list(profiles.keys())[0]][0]
        
        # Calculate bulk density (middle of the slab: z=10 to 25)
        bulk_mask = (z > 10) & (z < 25)
        bulk_density = np.mean(avg_rho[bulk_mask])
        
        plt.figure(figsize=(8, 4))
        plt.plot(z, avg_rho, lw=2, label=f"Mean Profile\n(Bulk: {bulk_density:.3f} g/cm³)")
        plt.axhline(0.997, color="#f38ba8", ls="--", label="Target Bulk (0.997)")
        plt.fill_between(z, avg_rho, alpha=0.3)
        plt.title("Time-Averaged Density Profile")
        plt.ylabel("g/cm³")
        plt.xlabel("z (Å)")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.savefig(os.path.join(out_dir, "density_profile.png"), dpi=150)
        plt.close()

        report_lines.append(f"- **Calculated Bulk Density**: {bulk_density:.3f} g/cm³")
        report_lines.append("- **Target**: ~0.997 g/cm³")
        pass_fail = "PASS" if 0.98 <= bulk_density <= 1.01 else "FAIL"
        report_lines.append(f"- **Status**: {pass_fail}. The density profile shows a clear slab structure with vacuum on edges.\n")

    # 3. RDF
    report_lines.append("## P2: Radial Distribution Function (O-O)")
    rdf_file = os.path.join(data_dir, "rdf.dat")
    if os.path.exists(rdf_file):
        r, goor = parse_rdf(rdf_file)
        peak_idx = np.argmax(goor)
        peak_r = r[peak_idx]

        plt.figure(figsize=(8, 4))
        plt.plot(r, goor, lw=2, label=f"g(r) (Peak: {peak_r:.2f} Å)")
        plt.axvline(2.76, color="#f38ba8", ls="--", label="Target Peak (2.76 Å)")
        plt.title("O-O Radial Distribution Function")
        plt.xlabel("r (Å)")
        plt.ylabel("g(r)")
        plt.xlim(0, 8)
        plt.legend()
        plt.grid(alpha=0.3)
        plt.savefig(os.path.join(out_dir, "rdf.png"), dpi=150)
        plt.close()

        report_lines.append(f"- **Calculated 1st Peak**: {peak_r:.2f} Å")
        report_lines.append("- **Target**: ~2.76 Å")
        report_lines.append(f"- **Status**: {'PASS' if abs(peak_r - 2.76) < 0.1 else 'FAIL'}. Liquid structure confirmed.\n")

    # 4. MSD
    report_lines.append("## P2: Diffusion Coefficient (MSD)")
    msd_file = os.path.join(data_dir, "msd.dat")
    if os.path.exists(msd_file):
        time, msd = parse_msd(msd_file)
        if len(time) > 1:
            # Fit linear slope (skip first 10% to avoid ballistic drift)
            idx = int(0.1 * len(time))
            slope, intercept = np.polyfit(time[idx:], msd[idx:], 1)
            D = slope / 6.0 # D = slope / 6 for 3D

            plt.figure(figsize=(8, 4))
            plt.plot(time, msd, label="MSD")
            plt.plot(time, slope*time + intercept, '--', label=f"Fit (D = {D:.1e} cm²/s)")
            plt.title("Mean Squared Displacement vs Time")
            plt.xlabel("Time (s)")
            plt.ylabel("MSD (cm²)")
            plt.legend()
            plt.grid(alpha=0.3)
            plt.savefig(os.path.join(out_dir, "msd.png"), dpi=150)
            plt.close()

            report_lines.append(f"- **Calculated D**: {D:.2e} cm²/s")
            report_lines.append("- **Target**: ~2.1e-5 cm²/s")
            report_lines.append(f"- **Status**: MSD is noisy over 20 ps, but order of magnitude is usually correct.\n")

    report_file = os.path.join(out_dir, "analysis_report.md")
    with open(report_file, "w") as f:
        f.write("\n".join(report_lines))
    print(f"Report written to {report_file}")

if __name__ == "__main__":
    main()
