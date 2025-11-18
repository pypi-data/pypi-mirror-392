import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".envnx" / "config-sync.json"


def load_config():
    if not CONFIG_PATH.exists():
        return {"base_env": None, "envs": {}}
    try:
        return json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError:
        print(f"[config-sync] Corrupted config file at {CONFIG_PATH}, resetting.")
        return {"base_env": None, "envs": {}}


def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def run(args):
    cfg = load_config()

    if args.cfg_cmd == "init":
        if cfg.get("base_env") is None:
            cfg["base_env"] = {
                "name": "base",
                "path": str(Path.home() / ".envnx" / "envs" / "base"),
                "requirements": [],
            }
            save_config(cfg)
            print(f"[config-sync] Initialized config at {CONFIG_PATH}")
        else:
            print(f"[config-sync] Config already exists at {CONFIG_PATH}")
        return

    if args.cfg_cmd == "list":
        print(f"[config-sync] Config file: {CONFIG_PATH}")
        base = cfg.get("base_env")
        if base:
            print("\nBase env:")
            print(f"  name: {base['name']}")
            print(f"  path: {base['path']}")
            print(f"  common packages: {len(base.get('requirements', []))}")
        else:
            print("No base env defined.")

        print("\nEnvs:")
        for name, env in cfg.get("envs", {}).items():
            print(f"  - {name} (extends {env.get('extends', 'base')})")
        return

    if args.cfg_cmd == "add-env":
        name = args.name
        if name in cfg.get("envs", {}):
            print(f"[config-sync] Env '{name}' already exists.")
            return
        cfg.setdefault("envs", {})[name] = {
            "extends": args.extends,
            "extra_requirements": [],
        }
        save_config(cfg)
        print(f"[config-sync] Added env '{name}' extending '{args.extends}'")
        return

    if args.cfg_cmd == "sync":
        name = args.name
        env = cfg.get("envs", {}).get(name)
        base = cfg.get("base_env")
        if env is None:
            print(f"[config-sync] Unknown env: {name}")
            return
        if base is None:
            print("[config-sync] No base env defined. Run 'envnx config-sync init' first.")
            return

        req_path = Path(args.requirements)
        if not req_path.exists():
            print(f"[config-sync] Requirements file not found: {req_path}")
            return

        required = []
        for line in req_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            required.append(line)

        base_pkgs = set(base.get("requirements", []))
        extra = [line for line in required if line not in base_pkgs]

        env["extra_requirements"] = extra
        cfg.setdefault("envs", {})[name] = env
        save_config(cfg)

        extra_file = req_path.with_name(f"{req_path.stem}.{name}.extra.txt")
        extra_file.write_text("\n".join(extra) + ("\n" if extra else ""))
        print(f"[config-sync] Synced env '{name}'.")
        print(f"  Base-shared packages: {len(required) - len(extra)}")
        print(f"  Extra packages for {name}: {len(extra)} (saved to {extra_file})")
        return

    if args.cfg_cmd == "activate":
        name = args.name
        env = cfg.get("envs", {}).get(name)
        base = cfg.get("base_env")
        if env is None or base is None:
            print("[config-sync] Env or base not defined. Run init/add-env first.")
            return

        print("[config-sync] Suggested activation steps:\n")
        print("1) Activate base env:")
        print(
            f"   source {base['path']}/bin/activate   "
            f"# (on Windows: {base['path']}\\Scripts\\activate)"
        )
        print("\n2) Install extra packages for this env (if file exists):")
        print(f"   pip install -r requirements.{name}.extra.txt")
        return

    print("[config-sync] No subcommand given. Use --help.")
