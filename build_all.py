import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_command(cmd, desc):
    print(f"\n[BUILD] {desc}...")
    result = subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"[ERROR] Step failed with return code {result.returncode}: {desc}")
        sys.exit(result.returncode)
    print(f"[SUCCESS] {desc} completed.")

def main():
    print("=" * 60)
    print("  RetailBill - Automated Build System")
    print("=" * 60)

    # 1. Generate assets if needed
    assets_dir = os.path.join(BASE_DIR, "assets")
    if not os.path.exists(os.path.join(assets_dir, "icon.ico")):
        run_command(f'"{sys.executable}" generate_assets.py', "Generating Icons and Assets")

    # 2. Run Test Suite
    run_command(f'"{sys.executable}" test_retailbill.py', "Running Unit Tests and Validations")

    # 3. Build Standalone Executable using PyInstaller
    pyinstaller_cmd = (
        f'"{sys.executable}" -m PyInstaller '
        f'--noconfirm --onedir --windowed '
        f'--name "RetailBill" '
        f'--icon "assets/icon.ico" '
        f'--add-data "assets;assets" '
        f'--hidden-import "PIL" '
        f'--hidden-import "qrcode" '
        f'--hidden-import "reportlab" '
        f'--hidden-import "sqlite3" '
        f'main.py'
    )
    run_command(pyinstaller_cmd, "Compiling RetailBill.exe with PyInstaller")

    # Copy root assets to dist/RetailBill
    dist_assets = os.path.join(BASE_DIR, "dist", "RetailBill", "assets")
    if not os.path.exists(dist_assets):
        shutil.copytree(assets_dir, dist_assets)

    # 4. Find Inno Setup Compiler
    iscc_candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 7", "ISCC.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"),
        r"C:\Program Files\Inno Setup 7\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        "ISCC.exe"
    ]
    iscc_path = None
    for cand in iscc_candidates:
        if os.path.exists(cand):
            iscc_path = cand
            break
        elif shutil.which(cand):
            iscc_path = cand
            break

    if not iscc_path:
        print("[WARNING] Inno Setup compiler (ISCC.exe) not found in standard paths.")
        print("Please install Inno Setup 6 or 7 to compile the setup installer.")
        return

    # 5. Compile Inno Setup Script
    iss_file = os.path.join(BASE_DIR, "setup.iss")
    run_command(f'"{iscc_path}" "{iss_file}"', "Compiling RetailBill-Setup.exe with Inno Setup")

    # 6. Verify Artifacts
    exe_file = os.path.join(BASE_DIR, "dist", "RetailBill", "RetailBill.exe")
    setup_file = os.path.join(BASE_DIR, "dist-installer", "RetailBill-Setup.exe")

    print("\n" + "=" * 60)
    print("  BUILD VERIFICATION SUMMARY")
    print("=" * 60)
    if os.path.exists(exe_file):
        print(f"  [PASS] RetailBill.exe generated: {exe_file} ({os.path.getsize(exe_file):,} bytes)")
    else:
        print(f"  [FAIL] RetailBill.exe missing!")

    if os.path.exists(setup_file):
        print(f"  [PASS] RetailBill-Setup.exe generated: {setup_file} ({os.path.getsize(setup_file):,} bytes)")
    else:
        print(f"  [FAIL] RetailBill-Setup.exe missing!")
    print("=" * 60)

if __name__ == "__main__":
    main()
