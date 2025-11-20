#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


def build_project(project_root: Path) -> None:
    """
    Build the project at project_root using `python -m build` (wheel + sdist).
    """
    project_root = project_root.resolve().parent
    pyproject = project_root / "pyproject.toml"

    if not pyproject.is_file():
        raise FileNotFoundError(
            f"pyproject.toml not found at {pyproject}. "
            "The target project must be a pyproject-based package."
        )

    print(f"[build] Project root: {project_root}")
    print("[build] Running: python -m build --wheel --sdist")

    proc = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--sdist"],
        cwd=str(project_root),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if proc.stdout:
        print(proc.stdout.rstrip())

    if proc.returncode != 0:
        raise RuntimeError(
            f"Command 'python -m build --wheel --sdist' failed with "
            f"exit code {proc.returncode}"
        )

    dist_dir = project_root / "dist"
    if not dist_dir.is_dir():
        raise FileNotFoundError(
            f"Build completed but no 'dist' directory was found at {dist_dir}"
        )

    print("[build] Done. Artifacts are in:", dist_dir)


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build a Python project (wheel + sdist) using `python -m build`."
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Path to the project root (default: current directory).",
    )

    args = parser.parse_args(argv)

    try:
        build_project(Path(args.project_root))
    except Exception as exc:  # noqa: BLE001
        print(f"[build] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
