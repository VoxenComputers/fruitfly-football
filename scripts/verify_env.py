"""Environment & Dependency Verification Script for Drosophila SNN Pipeline."""

import sys
import platform

def verify_all():
    print("=" * 60)
    print("Drosophila Connectome SNN Pipeline - Environment Verification")
    print("=" * 60)

    # 1. Check Python version
    py_version = sys.version_info
    print(f"[*] Python Version: {platform.python_version()} on {platform.system()} ({platform.machine()})")
    if py_version < (3, 10):
        print(f"[!] ERROR: Python >= 3.10 is required. Detected: {py_version.major}.{py_version.minor}")
        return False
    else:
        print("[+] Python version requirement (>= 3.10) satisfied.")

    # 2. Check Core Dependencies
    modules = [
        ("torch", "PyTorch Core"),
        ("torchvision", "PyTorch Vision"),
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("navis", "NAVIS (Neuron Analysis and Visualization)"),
        ("fafbseg", "FAFBSEG (FlyWire Connectomics)"),
        ("cv2", "OpenCV (Vision Processor)"),
        ("mss", "MSS (Low-Latency Screen Capture)"),
        ("ppadb", "Pure Python ADB (Emulator Bridge)"),
        ("matplotlib", "Matplotlib (Plotting & Diagnostics)"),
        ("rich", "Rich (CLI Telemetry & Terminal UI)"),
    ]

    all_passed = True
    print("\n[*] Testing module imports:")
    for mod_name, desc in modules:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "unknown")
            print(f"  [+] {desc:<45} : OK (v{ver})")
        except ImportError as e:
            print(f"  [-] {desc:<45} : FAILED ({e})")
            all_passed = False

    # 3. Check Acceleration / Compute Device
    print("\n[*] Compute Device Availability:")
    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        if cuda_avail:
            device_name = torch.cuda.get_device_name(0)
            capability = torch.cuda.get_device_capability(0)
            mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  [+] CUDA GPU Acceleration: ENABLED ({device_name})")
            print(f"  [+] Compute Capability   : {capability[0]}.{capability[1]}")
            print(f"  [+] VRAM Available       : {mem_gb:.2f} GB")
        else:
            print("  [-] CUDA unavailable. Vectorized CPU PyTorch engine will be used.")
    except Exception as e:
        print(f"  [!] PyTorch device check error: {e}")

    # 4. ADB Host Availability
    print("\n[*] ADB Connectivity Check:")
    try:
        from ppadb.client import Client as AdbClient
        client = AdbClient(host="127.0.0.1", port=5037)
        devices = client.devices()
        print(f"  [+] ADB Server responding. Attached devices: {len(devices)}")
        for d in devices:
            print(f"      - Device ID: {d.serial}")
    except Exception as e:
        print(f"  [i] Note: Local ADB server not running ({e}). Pipeline will use synthetic/OS fallback.")

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All environment requirements and headers verified with 0 missing dependencies.")
    else:
        print("[FAILURE] Some dependencies failed to import. Please check requirements.")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)
