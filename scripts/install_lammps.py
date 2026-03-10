import platform
import subprocess
import sys
import urllib.request
import os

def install_lammps_mac():
    print("Installing LAMMPS on macOS via Homebrew...")
    subprocess.run(["brew", "install", "lammps"], check=True)

def install_lammps_windows():
    print("Installing LAMMPS on Windows...")
    
    # Try Conda first
    try:
        subprocess.run(["conda", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Conda found. Installing via conda-forge...")
        subprocess.run(["conda", "install", "-c", "conda-forge", "lammps", "-y"], check=True)
        return
    except FileNotFoundError:
        pass
        
    print("Conda not found. Downloading Windows executable...")
    url = "https://rpm.lammps.org/windows/64bit/LAMMPS-64bit-latest.exe"
    exe_path = "LAMMPS-64bit-latest.exe"
    
    print(f"Downloading from {url}...")
    urllib.request.urlretrieve(url, exe_path)
    
    print("Running installer silently...")
    try:
        subprocess.run([exe_path, "/S"], check=True)
        print("Installation complete. Please add the LAMMPS bin directory (e.g., C:\\Program Files\\LAMMPS 64-bit\\bin) to your PATH.")
    finally:
        if os.path.exists(exe_path):
            os.remove(exe_path)

def install_lammps_linux():
    print("Installing LAMMPS on Linux via apt...")
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "lammps"], check=True)

if __name__ == "__main__":
    system = platform.system()
    try:
        if system == "Darwin":
            install_lammps_mac()
        elif system == "Windows":
            install_lammps_windows()
        elif system == "Linux":
            install_lammps_linux()
        else:
            print(f"Unsupported operating system: {system}")
            sys.exit(1)
        print("\nLAMMPS installation script finished successfully.")
    except Exception as e:
        print(f"\nError during installation: {e}")
        sys.exit(1)
