import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse

def analyze_z_movement(com_file, output_img):
    try:
        # Read the com.dat file, skipping LAMMPS headers
        df = pd.read_csv(com_file, sep=r'\s+', comment='#', 
                         names=['TimeStep', 'c_pfoa_com[1]', 'c_pfoa_com[2]', 'c_pfoa_com[3]'])
        
        # Convert steps to time (Assuming 1.0 fs timestep)
        df['Time_ps'] = df['TimeStep'] / 1000.0
        
        # Plot Z-coordinate vs Time
        plt.figure(figsize=(10, 6))
        plt.plot(df['Time_ps'], df['c_pfoa_com[3]'], color='blue', linewidth=1.5, label='PFOA Z-Center of Mass')
        
        # Add visual markers for the interface
        # Water slab is roughly Z=0 to Z=37. Interface is around Z=35-37 and Z=0-2
        plt.axhspan(35, 40, color='lightblue', alpha=0.3, label='Air-Water Interface Region')
        plt.axhspan(-2, 2, color='lightblue', alpha=0.3)
        plt.axhline(32, color='red', linestyle='--', alpha=0.5, label='Initial Position (Center of Bulk)')
        
        plt.xlabel('Time (ps)', fontsize=14)
        plt.ylabel('Z Coordinate (Å)', fontsize=14)
        plt.title('PFOA Center of Mass Z-Migration', fontsize=16, fontweight='bold', pad=15)
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.6)
        
        # Save output
        plt.savefig(output_img, dpi=300, bbox_inches='tight')
        print(f"Successfully generated analysis plot at {output_img}")
        
    except Exception as e:
        print(f"Error analyzing COM file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze PFOA Z-Axis Movement')
    parser.add_argument('--input', default='/Users/ashutoshhota/Work/rp/practice/aw_interface/src/pfas/output/pfoa/com.dat', help='Path to com.dat')
    parser.add_argument('--output', default='/Users/ashutoshhota/.gemini/antigravity/brain/669eacfe-8351-4bee-99f8-079c0d2ade92/pfoa_z_movement.png', help='Output image path')
    args = parser.parse_args()
    
    analyze_z_movement(args.input, args.output)
