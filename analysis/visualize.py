"""
Visualization script for LAMMPS air-water interface simulation outputs.
Generates plots for:
  1. Pressure & surface tension vs time (from surface_tension.dat)
  2. Density profile along z-axis (from density_profile.dat)
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ---------- Style ----------
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
            if not line or line.startswith("#"):
                continue
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
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) == 3:
                # Header line: timestep, n_chunks, total_count
                if current_ts is not None:
                    profiles[current_ts] = (np.array(z_coords), np.array(densities))
                current_ts = int(parts[0])
                z_coords, densities = [], []
            elif len(parts) == 4:
                # Data line: chunk_id, coord, ncount, density
                z_coords.append(float(parts[1]))
                densities.append(float(parts[3]))

    if current_ts is not None:
        profiles[current_ts] = (np.array(z_coords), np.array(densities))

    return profiles


def plot_surface_tension(timesteps, st_vals, outdir):
    """Plot surface tension vs timestep."""
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(timesteps, st_vals, color="#89b4fa", linewidth=1.5, alpha=0.7, label="Instantaneous")

    # Running average
    if len(st_vals) >= 5:
        window = min(10, len(st_vals))
        cumsum = np.cumsum(np.insert(st_vals, 0, 0))
        running_avg = (cumsum[window:] - cumsum[:-window]) / window
        ax.plot(timesteps[window - 1:], running_avg, color="#f38ba8", linewidth=2.5,
                label=f"Running avg (window={window})")

    ax.axhline(y=0, color="#a6adc8", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_xlabel("Timestep")
    ax.set_ylabel("Surface Tension (atm·Å)")
    ax.set_title("Surface Tension vs Time", fontsize=14, fontweight="bold")
    ax.legend(facecolor="#313244", edgecolor="#45475a")
    ax.grid(True, linewidth=0.5)

    plt.tight_layout()
    savepath = os.path.join(outdir, "surface_tension_plot.png")
    fig.savefig(savepath, dpi=150)
    plt.close(fig)
    print(f"  Saved: {savepath}")


def plot_density_profile(profiles, outdir):
    """Plot density profiles — last snapshot + time-averaged."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Last snapshot ---
    last_ts = max(profiles.keys())
    z, rho = profiles[last_ts]
    axes[0].fill_between(z, rho, alpha=0.3, color="#89b4fa")
    axes[0].plot(z, rho, color="#89b4fa", linewidth=2)
    axes[0].set_xlabel("z (Å)")
    axes[0].set_ylabel("Density (g/cm³)")
    axes[0].set_title(f"Density Profile — Timestep {last_ts}", fontsize=13, fontweight="bold")
    axes[0].grid(True, linewidth=0.5)

    # --- Time-averaged (over all snapshots) ---
    all_rho = np.array([profiles[ts][1] for ts in sorted(profiles.keys())])
    avg_rho = np.mean(all_rho, axis=0)
    std_rho = np.std(all_rho, axis=0)

    axes[1].fill_between(z, avg_rho - std_rho, avg_rho + std_rho, alpha=0.2, color="#a6e3a1")
    axes[1].plot(z, avg_rho, color="#a6e3a1", linewidth=2, label="Mean")
    axes[1].axhline(y=1.0, color="#f38ba8", linewidth=1, linestyle="--", alpha=0.6,
                    label="Exp. water (1.0 g/cm³)")
    axes[1].set_xlabel("z (Å)")
    axes[1].set_ylabel("Density (g/cm³)")
    axes[1].set_title("Time-Averaged Density Profile", fontsize=13, fontweight="bold")
    axes[1].legend(facecolor="#313244", edgecolor="#45475a")
    axes[1].grid(True, linewidth=0.5)

    plt.tight_layout()
    savepath = os.path.join(outdir, "density_profile_plot.png")
    fig.savefig(savepath, dpi=150)
    plt.close(fig)
    print(f"  Saved: {savepath}")


def main():
    # Determine data directory
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "output", "batch.1")

    st_file = os.path.join(data_dir, "surface_tension.dat")
    dp_file = os.path.join(data_dir, "density_profile.dat")

    # Output plots into the same data directory
    plot_dir = os.path.join(data_dir, "plots")
    os.makedirs(plot_dir, exist_ok=True)

    print(f"Reading data from: {data_dir}")
    print(f"Saving plots to:   {plot_dir}\n")

    # --- Surface tension / pressure ---
    if os.path.exists(st_file):
        print("[1/2] Plotting surface tension...")
        ts, st = parse_surface_tension(st_file)
        plot_surface_tension(ts, st, plot_dir)
    else:
        print(f"[1/2] SKIP: {st_file} not found")

    # --- Density profile ---
    if os.path.exists(dp_file):
        print("[2/2] Plotting density profile...")
        profiles = parse_density_profile(dp_file)
        plot_density_profile(profiles, plot_dir)
    else:
        print(f"[2/2] SKIP: {dp_file} not found")

    print("\nDone!")


if __name__ == "__main__":
    main()
