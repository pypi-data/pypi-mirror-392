
import os, re, platform, subprocess, urllib.request, json, zipfile, tarfile, shutil
from tempfile import TemporaryDirectory
from typing import Optional

def get_firefox_version() -> Optional[str]:
    if platform.system() == "Windows":
        paths = [os.path.join(os.environ.get(k, ""), r"Mozilla Firefox\firefox.exe") 
                 for k in ("PROGRAMFILES", "PROGRAMFILES(X86)")]
        for p in paths:
            if os.path.exists(p):
                try:
                    out = subprocess.check_output([p, "-v"], text=True)
                    m = re.search(r"(\d+\.\d+(\.\d+)?)", out)
                    if m: return m.group(1)
                except Exception: pass
    elif platform.system() == "Darwin":
        cmd = ["/Applications/Firefox.app/Contents/MacOS/firefox", "-v"]
        try:
            out = subprocess.check_output(cmd, text=True)
            m = re.search(r"(\d+\.\d+(\.\d+)?)", out)
            if m: return m.group(1)
        except Exception: pass
    else:
        try:
            out = subprocess.check_output(["firefox", "-v"], text=True)
            m = re.search(r"(\d+\.\d+(\.\d+)?)", out)
            if m: return m.group(1)
        except Exception: pass
    return None

def get_geckodriver_version() -> Optional[str]:
    try:
        out = subprocess.check_output(["geckodriver", "-V"], text=True, stderr=subprocess.STDOUT)
        m = re.search(r"geckodriver\s+(\d+\.\d+\.\d+)", out)
        return m.group(1) if m else None
    except Exception:
        return None

def latest_geckodriver_tag() -> Optional[str]:
    url = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"
    try:
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read())
            return data["tag_name"]  # e.g. "v0.33.0"
    except Exception:
        return None

def get_platform_architecture() -> str:
    sys, mach = platform.system(), platform.machine().lower()
    if sys == "Windows": return "win64" if "64" in mach else "win32"
    if sys == "Darwin": return "macos-aarch64" if "arm" in mach else "macos"
    if sys == "Linux": return "linux64"
    raise RuntimeError(f"Unsupported platform: {sys}")

def download_geckodriver(tag: str, dest_dir: str = ".") -> bool:
    arch = get_platform_architecture()
    ext = "zip" if arch.startswith("win") else "tar.gz"
    url = f"https://github.com/mozilla/geckodriver/releases/download/{tag}/geckodriver-{tag}-{arch}.{ext}"
    print(f"⬇ Downloading: {url}")
    try:
        with urllib.request.urlopen(url) as resp, TemporaryDirectory() as tmp:
            pkg = os.path.join(tmp, f"geckodriver.{ext}")
            open(pkg, "wb").write(resp.read())
            if ext == "zip":
                with zipfile.ZipFile(pkg) as z: z.extractall(tmp)
            else:
                import tarfile; tarfile.open(pkg).extractall(tmp)
            exe = "geckodriver.exe" if platform.system() == "Windows" else "geckodriver"
            src, dst = os.path.join(tmp, exe), os.path.join(dest_dir, exe)
            shutil.move(src, dst)
            if platform.system() != "Windows": os.chmod(dst, 0o755)
            print(f"✔ {exe} saved to: {dst}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    return False

def main() -> None:
    ff_ver = get_firefox_version()
    gd_ver = get_geckodriver_version()
    if not ff_ver:
        print("❌ Firefox not detected.")
        return
    print(f"🧭 Firefox version:     {ff_ver}")
    print(f"🧭 Geckodriver version: {gd_ver or 'N/A'}")
    latest_tag = latest_geckodriver_tag()
    if not latest_tag:
        print("❌ Could not fetch latest geckodriver release info.")
        return
    latest_ver = latest_tag.lstrip("v")
    if gd_ver == latest_ver:
        print("✅ Compatible: latest geckodriver already installed.")
    else:
        print("❗ Installing geckodriver", latest_ver)
        if download_geckodriver(latest_tag):
            print("✅ Geckodriver installed.")
        else:
            print("❌ Installation failed.")

if __name__ == "__main__":
    main()