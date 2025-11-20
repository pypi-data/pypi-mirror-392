#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from Codebase.Setup.create_publish_yml import create_publish_yml
from Codebase.Setup.create_pyproject_toml import create_pyproject_toml

def setup_project_env(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    force = False
    if "--force" in argv:
        force = True
        argv = [a for a in argv if a != "--force"]

    if argv:
        project_root = Path(argv[0])
    else:
        # default to repo root: two levels up from this file
        project_root = Path(__file__).resolve().parent.parent

    """
        Create or overwrite pyproject.toml in the given project_root.

        Returns:
            0 on success
            1 if pyproject.toml already exists and force is False
        """
    project_root = project_root.resolve()
    pyproject_path = project_root / "pyproject.toml"
    publish_path = project_root / ".github" / "workflows" / "publish.yml"
    print(pyproject_path)
    print(publish_path)

    create_pyproject_toml(project_root, pyproject_path, force)
    ## NOT needed YET: this is for github actions for automatically syncing w/ PIP.
    #create_publish_yml(project_root, publish_path, force)

if __name__ == "__main__":
    setup_project_env()
