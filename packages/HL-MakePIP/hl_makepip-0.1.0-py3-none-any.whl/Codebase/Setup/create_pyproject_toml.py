PYPROJECT_CONTENT = """\
[project]
name = "HL-MakePIP"
version = "0.1.0"
description = "Library to setup and export HL project environments to PIP."
authors = [{ name = "StevenNaliwajka", email = "ConvexBurrito5@gmail.com" }]
readme = "README.md"
requires-python = ">=3.9"
dependencies = ["build>=1.2.1"]

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project.scripts]
# Console script entry point: `piphelper` CLI
piphelper = "Codebase.cli:main"

[tool.setuptools.packages.find]
# Look for packages starting at project root, but only include Codebase package tree
where = ["."]
include = ["Codebase*"]
"""


def create_pyproject_toml(folder, pyproject_path, force: bool):
    # Ensure target folder exists
    folder.mkdir(parents=True, exist_ok=True)

    if pyproject_path.exists() and not force:
        print(f"[setup-project-env] {pyproject_path} already exists. "
              f"Use --force to overwrite.")
        return

    # Otherwise create or overwrite
    action = "Overwriting" if pyproject_path.exists() else "Creating"
    print(f"[setup-project-env] {action} {pyproject_path}")
    pyproject_path.write_text(PYPROJECT_CONTENT, encoding="utf-8")
