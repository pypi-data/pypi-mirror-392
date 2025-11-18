import subprocess
from pathlib import Path


def parse_requirements(path: Path):
    required = {}
    if not path.exists():
        print(f"[env-check] No requirements file found at {path}")
        return required

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" in line:
            pkg, ver = line.split("==", 1)
            required[pkg.lower()] = ("==", ver.strip())
        elif ">=" in line:
            pkg, ver = line.split(">=", 1)
            required[pkg.lower()] = (">=", ver.strip())
        else:
            # no version constraint
            required[line.lower()] = (None, None)
    return required


def get_installed_packages():
    try:
        out = subprocess.check_output(["pip", "freeze"], text=True)
    except Exception as e:
        print(f"[env-check] Failed to run 'pip freeze': {e}")
        return {}
    installed = {}
    for line in out.splitlines():
        if "==" not in line:
            continue
        pkg, ver = line.split("==", 1)
        installed[pkg.lower()] = ver.strip()
    return installed


def run(args):
    req_path = Path(args.requirements)
    required = parse_requirements(req_path)
    installed = get_installed_packages()

    print(f"[env-check] Using requirements: {req_path.resolve()}")
    missing = []
    mismatched = []
    extra = []

    # check required
    for pkg, (op, ver) in required.items():
        inst_ver = installed.get(pkg)
        if inst_ver is None:
            missing.append((pkg, op, ver))
        elif op == "==" and ver is not None and inst_ver != ver:
            mismatched.append((pkg, ver, inst_ver))
        elif op == ">=" and ver is not None:
            # basic string compare (simple, not perfect)
            if inst_ver < ver:
                mismatched.append((pkg, f">={ver}", inst_ver))

    # extras
    for pkg, ver in installed.items():
        if pkg not in required:
            extra.append((pkg, ver))

    if not required:
        print("[env-check] No requirements found to compare.")
        return

    if missing:
        print("\nMissing packages:")
        for pkg, op, ver in missing:
            if op and ver:
                print(f"  - {pkg} ({op}{ver})")
            else:
                print(f"  - {pkg}")

    if mismatched:
        print("\nVersion mismatches:")
        for pkg, req, inst in mismatched:
            print(f"  - {pkg}: required {req}, installed {inst}")

    if extra:
        print("\nExtra installed packages (not in requirements):")
        for pkg, ver in extra:
            print(f"  - {pkg}=={ver}")

    if not (missing or mismatched or extra):
        print("[env-check] Everything looks consistent ✅")
