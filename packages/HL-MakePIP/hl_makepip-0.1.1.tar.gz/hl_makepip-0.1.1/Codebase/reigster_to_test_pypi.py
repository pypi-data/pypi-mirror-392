#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
import getpass
from typing import Optional


def register_to_test_pypi(project_root: Optional[Path | str] = None) -> int:
    """
    Upload dist/* to TestPyPI using a token provided interactively.

    Equivalent to:
      Windows: py -m twine upload --repository testpypi dist/*
      Linux:   python3 -m twine upload --repository testpypi dist/*
    """
    # Detect project root if not given
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent
    project_root = Path(project_root).resolve()

    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        print(f"[ERROR] dist/ directory not found at: {dist_dir}", flush=True)
        print("        Build your package first, e.g. `python -m build`.", flush=True)
        return 1

    print("============================================================", flush=True)
    print(" TestPyPI Upload Helper", flush=True)
    print("============================================================", flush=True)
    print("1) Open this URL in your browser:", flush=True)
    print("   https://test.pypi.org/manage/account/#api-tokens", flush=True)
    print("2) Create a new API token (or copy an existing one).", flush=True)
    print("3) Have the token ready in your clipboard.", flush=True)
    print("4) Then come back here and press ENTER to continue.", flush=True)
    print("------------------------------------------------------------", flush=True)
    input("Press ENTER once your TestPyPI API token is ready... ")

    # Prompt for token (hidden when possible)
    token: str
    try:
        if sys.stdin.isatty():
            token = getpass.getpass(
                "Paste your TestPyPI API token here (input may be hidden): "
            ).strip()
        else:
            raise RuntimeError
    except Exception:
        print("(getpass not available here – your input will be visible)", flush=True)
        token = input("Paste your TestPyPI API token here: ").strip()

    if not token:
        print("[ERROR] No token entered. Aborting.", flush=True)
        return 1

    # Collect files in dist/ instead of relying on shell globbing
    files = sorted(dist_dir.glob("*"))
    if not files:
        print(f"[ERROR] No files found in dist/: {dist_dir}", flush=True)
        print("        Run `python -m build` first to create distributions.", flush=True)
        return 1

    # Choose Python launcher based on OS
    if os.name == "nt":
        python_cmd = ["py", "-m", "twine", "upload", "--repository", "testpypi"]
    else:
        python_cmd = ["python3", "-m", "twine", "upload", "--repository", "testpypi"]

    cmd = python_cmd + [str(f) for f in files]

    print("------------------------------------------------------------", flush=True)
    print(f"Project root : {project_root}", flush=True)
    print(f"dist/ files  : {[f.name for f in files]}", flush=True)
    print(f"Running      : {' '.join(cmd)}", flush=True)
    print("------------------------------------------------------------", flush=True)
    print("NOTE: Using username '__token__' and your API token as password.", flush=True)
    print("============================================================", flush=True)

    env = os.environ.copy()
    env["TWINE_USERNAME"] = "__token__"
    env["TWINE_PASSWORD"] = token

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            env=env,
            check=False,
        )
    except FileNotFoundError as e:
        print("[ERROR] Failed to run twine command.", flush=True)
        print("       Make sure 'twine' is installed in your environment:", flush=True)
        print("         pip install twine", flush=True)
        print(f"Details: {e}", flush=True)
        return 1

    if result.returncode == 0:
        print("✅ Upload to TestPyPI completed successfully.", flush=True)
    else:
        print(f"❌ twine exited with code {result.returncode}.", flush=True)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Optional: allow passing project root as first argument
    project_root = argv[0] if argv else None
    return register_to_test_pypi(project_root=project_root)


if __name__ == "__main__":
    raise SystemExit(main())
