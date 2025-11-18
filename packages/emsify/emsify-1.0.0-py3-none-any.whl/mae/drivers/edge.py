#!/usr/bin/env python3
import os, re, subprocess, platform, urllib.request, zipfile, shutil
from tempfile import TemporaryDirectory

def get_edge_version():
    """Detect Microsoft Edge full version from system."""
    version = None
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Edge\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            winreg.CloseKey(key)
        except Exception:
            version = None
        if not version:
            paths = [
                os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Microsoft\\Edge\\Application\\msedge.exe"),
                os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Microsoft\\Edge\\Application\\msedge.exe")
            ]
            for path in paths:
                if os.path.exists(path):
                    try:
                        output = subprocess.check_output([path, "--version"], stderr=subprocess.STDOUT, text=True)
                        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
                        if match:
                            version = match.group(1)
                            break
                    except Exception:
                        continue
    elif platform.system() == "Darwin":  # macOS
        try:
            output = subprocess.check_output(["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "--version"], text=True)
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
            if match:
                version = match.group(1)
        except Exception:
            pass
    return version

def get_msedgedriver_version():
    """Detect installed msedgedriver version if available in PATH."""
    try:
        output = subprocess.check_output(["msedgedriver", "--version"], stderr=subprocess.STDOUT, text=True)
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        return match.group(1) if match else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

def get_platform_architecture():
    """Return architecture string used in driver URL."""
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Windows":
        return "win64" if "64" in machine else "win32"
    elif system == "Darwin":
        return "mac64_m1" if "arm" in machine else "mac64"
    elif system == "Linux":
        return "linux64"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def download_msedgedriver(edge_version, dest_dir="."):
    """Download matching MSEdgeDriver based on full version and platform."""
    arch = get_platform_architecture()
    zip_url = f"https://msedgedriver.microsoft.com/{edge_version}/edgedriver_{arch}.zip"
    print(f"⬇ Downloading: {zip_url}")
    try:
        with urllib.request.urlopen(zip_url) as response:
            with TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "msedgedriver.zip")
                with open(zip_path, "wb") as f:
                    f.write(response.read())
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmpdir)
                exe_name = "msedgedriver.exe" if platform.system() == "Windows" else "msedgedriver"
                src = os.path.join(tmpdir, exe_name)
                dst = os.path.join(dest_dir, exe_name)
                if os.path.exists(src):
                    shutil.move(src, dst)
                    print(f"✔ {exe_name} saved to: {dst}")
                    return True
                else:
                    print(f"❌ Driver file not found inside zip.")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ Failed to download driver: {e}")
    return False

def main():
    edge_ver = get_edge_version()
    driver_ver = get_msedgedriver_version()

    if not edge_ver:
        print("❌ Could not detect installed Edge version.")
        return

    print(f"🧭 Edge version:         {edge_ver}")
    if driver_ver:
        print(f"🧭 MSEdgeDriver version: {driver_ver}")
    else:
        print("⚠ MSEdgeDriver not found in PATH.")

    if edge_ver == driver_ver:
        print("✅ Compatible: versions match.")
    else:
        print("❗ Incompatible or missing driver. Attempting download...")
        if download_msedgedriver(edge_ver):
            print("✅ Successfully downloaded matching MSEdgeDriver.")
        else:
            print("❌ Could not download matching MSEdgeDriver.")

if __name__ == "__main__":
    main()
