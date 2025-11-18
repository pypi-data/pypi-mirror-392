import os
from pathlib import Path


def run(args):
    pattern = args.pattern
    exts = set(args.ext) if args.ext else None
    ignore_dirs = set(args.ignore or [])

    start = Path(".").resolve()
    print(f"[code-search] Searching for '{pattern}' in {start}")

    matches = 0
    for dirpath, dirnames, filenames in os.walk(start):
        # filter ignored dirs
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        for f in filenames:
            path = Path(dirpath) / f
            if exts is not None and path.suffix not in exts:
                continue
            try:
                text = path.read_text(errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue

            for i, line in enumerate(text.splitlines(), start=1):
                if pattern in line:
                    print(f"{path}:{i}: {line.strip()}")
                    matches += 1

    if matches == 0:
        print("[code-search] No matches found.")
    else:
        print(f"[code-search] {matches} matches found ✅")
