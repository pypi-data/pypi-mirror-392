import argparse
from . import env_check, proj_clean, code_search, config_sync


BANNER = r"""

███████╗███╗  ██╗██╗    ╗██╗    ███╗  ██╗██╗  ██╗
██╔════╝████╗ ██║╚██╗  ╗██╔╝    ████╗ ██║╚██╗██╔╝
█████╗  ██╔██╗██║ ╚██  ██╔╝     ██╔██╗██║ ╚███╔╝ 
██╔══╝  ██║╚████║  ╚█  █╔╝      ██║╚████║ ██╔██╗ 
███████╗██║ ╚███║   ████║       ██║ ╚███║██╔╝ ██╗
╚══════╝╚═╝  ╚══╝   ╚═══╝       ╚═╝  ╚══╝╚═╝  ╚═╝
                     ENV-NX
"""


def print_banner():
    print(BANNER)
    print()  # blank line after banner


def main():
    # Show banner for every invocation
    print_banner()

    parser = argparse.ArgumentParser(
        prog="envnx",
        description="EnvNX – small CLI toolkit for real-world dev workflows."
    )
    subparsers = parser.add_subparsers(dest="command")

    # env-check
    p_env = subparsers.add_parser(
        "env-check",
        help="Check Python env vs requirements.txt"
    )
    p_env.add_argument(
        "--requirements",
        "-r",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)",
    )

    # proj-clean
    p_clean = subparsers.add_parser(
        "proj-clean",
        help="Clean project junk files"
    )
    p_clean.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project root (default: current dir)",
    )
    p_clean.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete files",
    )
    p_clean.add_argument(
        "--max-size",
        type=int,
        default=None,
        help="Max file size in MB to consider for deletion (optional)",
    )

    # code-search
    p_search = subparsers.add_parser(
        "code-search",
        help="Search inside code files"
    )
    p_search.add_argument(
        "pattern",
        help="Text pattern to search for",
    )
    p_search.add_argument(
        "--ext",
        nargs="*",
        default=None,
        help="Limit search to given extensions, e.g. --ext .py .js",
    )
    p_search.add_argument(
        "--ignore",
        nargs="*",
        default=[".git", "venv", "__pycache__"],
        help="Directories to ignore",
    )

    # config-sync
    p_cfg = subparsers.add_parser(
        "config-sync",
        help="Manage shared env config"
    )
    cfg_sub = p_cfg.add_subparsers(dest="cfg_cmd")

    cfg_sub.add_parser("init", help="Initialize global config file")
    cfg_sub.add_parser("list", help="List base/env profiles")

    cfg_add = cfg_sub.add_parser("add-env", help="Add a new logical env")
    cfg_add.add_argument("name", help="Name of the env (e.g., projectA)")
    cfg_add.add_argument(
        "--extends",
        default="base",
        help="Base env to extend (default: base)",
    )

    cfg_sync = cfg_sub.add_parser(
        "sync",
        help="Sync project requirements with base env",
    )
    cfg_sync.add_argument("name", help="Env name to sync")
    cfg_sync.add_argument(
        "--requirements",
        "-r",
        default="requirements.txt",
        help="Project requirements file path",
    )

    cfg_act = cfg_sub.add_parser(
        "activate",
        help="Show how to activate an env"
    )
    cfg_act.add_argument("name", help="Env name")

    args = parser.parse_args()

    if args.command == "env-check":
        env_check.run(args)
    elif args.command == "proj-clean":
        proj_clean.run(args)
    elif args.command == "code-search":
        code_search.run(args)
    elif args.command == "config-sync":
        config_sync.run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
