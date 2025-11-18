#!/usr/bin/env python3
import os, re, subprocess, platform, urllib.request, zipfile, shutil
from tempfile import TemporaryDirectory

def get_chrome_version():
    """Detect installed Chrome full version."""
    version = None
    system = platform.system()
    if system == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            winreg.CloseKey(key)
        except Exception:
            version = None
        if not version:
            paths = [
                os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe"),
                os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Google\\Chrome\\Application\\chrome.exe")
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
    elif system == "Darwin":
        try:
            output = subprocess.check_output(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"], text=True)
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
            if match:
                version = match.group(1)
        except Exception:
            pass
    elif system == "Linux":
        try:
            output = subprocess.check_output(["google-chrome", "--version"], text=True)
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
            if match:
                version = match.group(1)
        except Exception:
            pass
    return version

def get_chromedriver_version():
    """Check version of chromedriver in PATH."""
    try:
        output = subprocess.check_output(["chromedriver", "--version"], stderr=subprocess.STDOUT, text=True)
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        return match.group(1) if match else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

def get_platform_architecture():
    """Return architecture string used in ChromeDriver URL."""
    system = platform.system()
    if system == "Windows":
        return "win64" if platform.machine().endswith("64") else "win32"
    elif system == "Darwin":
        try:
            out = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
            return "mac-arm64" if "Apple" in out else "mac-x64"
        except Exception:
            return "mac-x64"
    elif system == "Linux":
        return "linux64"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def download_chromedriver(chrome_version, dest_dir="."):
    """Download matching ChromeDriver from Google for Testing storage."""
    arch = get_platform_architecture()
    url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/{arch}/chromedriver-{arch}.zip"
    print(f"⬇ Downloading: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            with TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "chromedriver.zip")
                with open(zip_path, "wb") as f:
                    f.write(response.read())
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmpdir)
                exe_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
                # Locate inside folder like chromedriver-<arch>/chromedriver
                for root, _, files in os.walk(tmpdir):
                    if exe_name in files:
                        src = os.path.join(root, exe_name)
                        dst = os.path.join(dest_dir, exe_name)
                        shutil.move(src, dst)
                        print(f"✔ {exe_name} saved to: {dst}")
                        return True
                print("❌ Driver executable not found in extracted contents.")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
    return False

def main():
    chrome_ver = get_chrome_version()
    driver_ver = get_chromedriver_version()

    if not chrome_ver:
        print("❌ Could not detect installed Chrome version.")
        return

    print(f"🧭 Chrome version:       {chrome_ver}")
    if driver_ver:
        print(f"🧭 ChromeDriver version: {driver_ver}")
    else:
        print("⚠ ChromeDriver not found in PATH.")

    if chrome_ver == driver_ver:
        print("✅ Compatible: versions match.")
    else:
        print("❗ Incompatible or missing driver. Attempting download...")
        if download_chromedriver(chrome_ver):
            print("✅ Successfully downloaded matching ChromeDriver.")
        else:
            print("❌ Could not download matching ChromeDriver.")

if __name__ == "__main__":
    main()
