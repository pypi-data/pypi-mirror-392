
# **EnvNX CLI**

### A Lightweight Developer Workflow Toolkit for Environment, Project & Code Management

```

███████╗███╗  ██╗██╗    ╗██╗    ███╗  ██╗██╗  ██╗
██╔════╝████╗ ██║╚██╗  ╗██╔╝    ████╗ ██║╚██╗██╔╝
█████╗  ██╔██╗██║ ╚██  ██╔╝     ██╔██╗██║ ╚███╔╝ 
██╔══╝  ██║╚████║  ╚█  █╔╝      ██║╚████║ ██╔██╗ 
███████╗██║ ╚███║   ████║       ██║ ╚███║██╔╝ ██╗
╚══════╝╚═╝  ╚══╝   ╚═══╝       ╚═╝  ╚══╝╚═╝  ╚═╝
                     ENV-NX
```

EnvNX is a simple, fast, dependency-free command-line toolkit designed for developers who want clean projects, consistent environments, fast code searches, and shared environment configurations across multiple projects — without using heavy tools.

It works on Windows, macOS, and Linux.

---

# **Why EnvNX?**

Developers often repeat the same tasks:

* Checking for missing or extra packages
* Cleaning project junk (`__pycache__`, logs, temp files, etc.)
* Searching code without using heavy tools
* Managing multiple Python environments with shared base packages

EnvNX solves these pain points in one small CLI.

No LLMs
No external APIs
No cloud
No heavy dependencies

Just a pure Python development productivity toolkit.

---

# **Features**

## 1. Environment Check (`env-check`)

Compare installed Python packages with `requirements.txt`.

* Shows missing packages
* Shows extra installed packages
* Helps maintain clean and reproducible environments

---

## 2. Project Cleanup (`proj-clean`)

Automatically removes common clutter:

* `__pycache__`
* `.log` files
* `.tmp` files
* Build artifacts
* Junk folders

Dry-run by default.
Use `--apply` to delete.

---

## 3. Code Search (`code-search`)

Fast and simple grep-style text search:

* Search for any pattern across code files
* Supports `--ext` filters (e.g., `.py`)
* Ignores unwanted folders (`.git`, venv, `__pycache__`)

---

## 4. Config Sync (`config-sync`)

A small environment-sharing system:

* One global base environment
* Multiple project-specific logical environments
* Sync project requirements against the base
* Stores project-specific extras
* Reduces disk usage by avoiding duplicate installs

---

# **Installation**

## Install from PyPI (recommended)

```bash
pip install envnx-cli
```

Check:

```bash
envnx --help
```

---

## Install from GitHub

```bash
pip install git+https://github.com/<your-username>/envnx-cli.git
```

---

## Install Locally (development)

```bash
git clone https://github.com/<your-username>/envnx-cli.git
cd envnx-cli
pip install -e .
```

---

# **Usage**

View help:

```bash
envnx --help
```

Commands:

```
env-check        Check Python env vs requirements.txt
proj-clean       Clean project junk files
code-search      Search inside code files
config-sync      Manage shared env config
```

---

# **1. Environment Check**

Default usage:

```bash
envnx env-check
```

With custom requirements file:

```bash
envnx env-check -r requirements-dev.txt
```

Output example:

```
Missing:
  - numpy==1.26.4

Extra:
  - setuptools==69.5.0
  - click==8.3.1
```

---

# **2. Project Cleanup**

Dry-run:

```bash
envnx proj-clean .
```

Delete junk:

```bash
envnx proj-clean . --apply
```

---

# **3. Code Search**

Search for a function:

```bash
envnx code-search "train_model"
```

Limit to Python files:

```bash
envnx code-search "train_model" --ext .py
```

Ignore paths:

```bash
envnx code-search "token" --ignore venv .git
```

---

# **4. Config Sync**

Initialize global config:

```bash
envnx config-sync init
```

Add a new environment:

```bash
envnx config-sync add-env projectA
```

List environments:

```bash
envnx config-sync list
```

Sync requirements:

```bash
envnx config-sync sync projectA -r requirements.txt
```

Activate instructions:

```bash
envnx config-sync activate projectA
```

---

# **Project Structure**

```
envnx/
 ├── cli.py
 ├── env_check.py
 ├── proj_clean.py
 ├── code_search.py
 ├── config_sync.py
 └── __init__.py
pyproject.toml
README.md
```

---

# **Development Guide**

Install in editable mode:

```bash
pip install -e .
```

Build package:

```bash
python -m build
```

Upload to PyPI:

```bash
python -m twine upload dist/*
```

---

# **Versioning**

EnvNX uses semantic versioning:

* Major: breaking changes
* Minor: new features
* Patch: fixes and improvements

---

# **License**

EnvNX is licensed under the MIT License.

---

# **Author**

Created and maintained by **Nithin Sai Adupa**.

For issues or contributions, please submit a pull request or open a GitHub issue.