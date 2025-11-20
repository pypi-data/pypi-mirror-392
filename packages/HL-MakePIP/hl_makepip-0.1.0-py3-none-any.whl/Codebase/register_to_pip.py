#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


def _run_cmd(cmd: list[str], cwd: Path, verbose: bool = True) -> None:
    """
    Run a subprocess command, raising a nice error if it fails.
    """
    if verbose:
        print(f"[register_to_pip] Running: {' '.join(cmd)} (cwd={cwd})")

    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if verbose and proc.stdout:
        print(proc.stdout.rstrip())

    if proc.returncode != 0:
        raise RuntimeError(
            f"Command {' '.join(cmd)!r} failed with exit code {proc.returncode}"
        )


def register_to_pip(
    project_root: Path,
    *,
    verbose: bool = True,
) -> None:
    """
    Build a Python project (using `python -m build`).

    This is now designed for a Trusted Publisher setup, where the actual
    upload to (Test)PyPI is handled by a GitHub Actions workflow
    (e.g. .github/workflows/publish.yml).

    Parameters
    ----------
    project_root:
        Path to the project you want to build. Must contain pyproject.toml.
    verbose:
        If True, prints progress and command output.
    """
    project_root = project_root.resolve()

    if verbose:
        print(f"[register_to_pip] Project root: {project_root}")

    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        raise FileNotFoundError(
            f"pyproject.toml not found at {pyproject}. "
            "The target project must be a pyproject-based package."
        )

    # 1) Build the project (wheel + sdist)
    if verbose:
        print("[register_to_pip] Step 1/1: Building project with `python -m build`")

    _run_cmd(
        [sys.executable, "-m", "build", "--wheel", "--sdist"],
        cwd=project_root,
        verbose=verbose,
    )

    dist_dir = project_root / "dist"
    if not dist_dir.is_dir():
        raise FileNotFoundError(
            f"Build completed but no 'dist' directory was found at {dist_dir}"
        )

    if verbose:
        print("[register_to_pip] Build complete.")
        print(f"[register_to_pip] Artifacts are in: {dist_dir}")

        publish_workflow = project_root / ".github" / "workflows" / "publish.yml"
        if publish_workflow.is_file():
            print(
                "[register_to_pip] Detected GitHub Actions workflow at "
                f"{publish_workflow}"
            )
            print(
                "[register_to_pip] To publish, push your changes (and any required "
                "tag/branch) so the workflow can upload to (Test)PyPI."
            )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a Python project (wheel + sdist). "
            "Publishing is handled by your GitHub Actions workflow."
        )
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Path to the project root (default: current directory).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output (still shows errors).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    project_root = Path(args.project_root)
    verbose = not args.quiet

    try:
        register_to_pip(
            project_root=project_root,
            verbose=verbose,
        )
    except Exception as exc:
        print(f"[register_to_pip] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
