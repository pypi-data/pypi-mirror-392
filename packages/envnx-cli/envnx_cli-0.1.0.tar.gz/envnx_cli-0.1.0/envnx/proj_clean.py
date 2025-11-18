import os
from pathlib import Path

JUNK_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".ipynb_checkpoints",
}

JUNK_FILES = {
    ".DS_Store",
}


def run(args):
    root = Path(args.path).resolve()
    apply = args.apply
    max_size_bytes = args.max_size * 1024 * 1024 if args.max_size else None

    print(f"[proj-clean] Scanning: {root}")
    to_delete = []

    for dirpath, dirnames, filenames in os.walk(root):
        # collect junk dirs
        for d in list(dirnames):
            if d in JUNK_DIRS:
                full = Path(dirpath) / d
                to_delete.append(full)

        # collect junk files
        for f in filenames:
            full = Path(dirpath) / f
            if f in JUNK_FILES:
                to_delete.append(full)
            elif full.suffix in {".log", ".tmp"}:
                if max_size_bytes is not None and full.is_file():
                    try:
                        size = full.stat().st_size
                    except OSError:
                        continue
                    if size > max_size_bytes:
                        to_delete.append(full)
                else:
                    to_delete.append(full)

    if not to_delete:
        print("[proj-clean] Nothing to clean.")
        return

    print("\nFound junk:")
    for p in to_delete:
        print(f"  - {p}")

    if not apply:
        print("\n[proj-clean] Dry run only. Use --apply to delete.")
        return

    print("\n[proj-clean] Deleting...")
    for p in to_delete:
        try:
            if p.is_dir():
                # remove dir tree
                for subdir, subdirs, files in os.walk(p, topdown=False):
                    for f in files:
                        Path(subdir, f).unlink(missing_ok=True)
                    for d in subdirs:
                        Path(subdir, d).rmdir()
                p.rmdir()
            else:
                p.unlink(missing_ok=True)
        except Exception as e:
            print(f"  ! Failed to delete {p}: {e}")
    print("[proj-clean] Done ✅")
