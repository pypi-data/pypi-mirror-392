#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
import getpass
import shutil
from typing import Optional


def _detect_project_root() -> Path:
    # Assumes this file lives in <project_root>/Codebase/...
    return Path(__file__).resolve().parent.parent


def register_to_pypi(
    project_root: Optional[Path | str] = None,
    rebuild: bool = True,
    clean_dist: bool = True,
) -> int:
    """
    Build (optionally) and upload dist/* to the real PyPI using a token provided interactively.

    - If `clean_dist=True`, removes all files from dist/ before rebuilding.
    - If `rebuild=True`, runs `python -m build` first to recreate dist/*.
    - If PyPI returns "File already exists", prints a clear hint to bump version.
    """
    # ---------------- Project root ----------------
    if project_root is None:
        project_root = _detect_project_root()
    project_root = Path(project_root).resolve()

    dist_dir = project_root / "dist"

    print("============================================================", flush=True)
    print(" PyPI Upload Helper (REAL PYPI)", flush=True)
    print("============================================================", flush=True)
    print(f"Project root : {project_root}", flush=True)

    # ---------------- Optional clean + rebuild ----------------
    if rebuild:
        if dist_dir.exists() and clean_dist:
            print(f"Cleaning existing dist/ directory: {dist_dir}", flush=True)
            # Remove contents; keep the directory itself
            for p in dist_dir.iterdir():
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(p)

        # Ensure dist_dir exists (build will create it anyway, but this is safe)
        dist_dir.mkdir(exist_ok=True)

        print("Rebuilding distributions (python -m build)...", flush=True)
        build_cmd = [sys.executable, "-m", "build"]
        print("Running build command:", " ".join(build_cmd), flush=True)
        build_result = subprocess.run(
            build_cmd,
            cwd=project_root,
            check=False,
            text=True,
            capture_output=True,
        )
        if build_result.stdout:
            print(build_result.stdout, end="", flush=True)
        if build_result.stderr:
            print(build_result.stderr, end="", file=sys.stderr, flush=True)

        if build_result.returncode != 0:
            print("[ERROR] Build failed. Aborting upload.", flush=True)
            return build_result.returncode

        print("Build completed successfully.", flush=True)

    # ---------------- Gather files in dist/ ----------------
    if not dist_dir.exists():
        print(f"[ERROR] dist/ directory not found at: {dist_dir}", flush=True)
        print("        Build your package first, e.g. `python -m build`.", flush=True)
        return 1

    files = sorted(dist_dir.glob("*"))
    if not files:
        print(f"[ERROR] No files found in dist/: {dist_dir}", flush=True)
        print("        Run `python -m build` first to create distributions.", flush=True)
        return 1

    print(f"dist/ files  : {[f.name for f in files]}", flush=True)

    # ---------------- Token instructions ----------------
    print("------------------------------------------------------------", flush=True)
    print("1) Open this URL in your browser:", flush=True)
    print("   https://pypi.org/manage/account/#api-tokens", flush=True)
    print("2) Create a new API token (or copy an existing one).", flush=True)
    print("3) Have the token ready in your clipboard.", flush=True)
    print("4) Then come back here and press ENTER to continue.", flush=True)
    print("------------------------------------------------------------", flush=True)
    input("Press ENTER once your PyPI API token is ready... ")

    # ---------------- Prompt for token ----------------
    try:
        if sys.stdin.isatty():
            token = getpass.getpass(
                "Paste your PyPI API token here (input may be hidden): "
            ).strip()
        else:
            raise RuntimeError
    except Exception:
        print("(getpass not available here – your input will be visible)", flush=True)
        token = input("Paste your PyPI API token here: ").strip()

    if not token:
        print("[ERROR] No token entered. Aborting.", flush=True)
        return 1

    # ---------------- Twine command ----------------
    if os.name == "nt":
        python_cmd = ["py", "-m", "twine", "upload"]
    else:
        python_cmd = ["python3", "-m", "twine", "upload"]

    cmd = python_cmd + [str(f) for f in files]

    print("------------------------------------------------------------", flush=True)
    print(f"Running upload: {' '.join(cmd)}", flush=True)
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
            text=True,
            capture_output=True,
        )
    except FileNotFoundError as e:
        print("[ERROR] Failed to run twine command.", flush=True)
        print("       Make sure 'twine' is installed in your environment:", flush=True)
        print("         pip install twine", flush=True)
        print(f"Details: {e}", flush=True)
        return 1

    if result.stdout:
        print(result.stdout, end="", flush=True)
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr, flush=True)

    if result.returncode == 0:
        print("✅ Upload to PyPI completed successfully.", flush=True)
        return 0

    # -------- Special-case "File already exists" from PyPI --------
    stderr_text = result.stderr or ""
    if "File already exists" in stderr_text:
        print("\n[INFO] PyPI reports that this exact file already exists.", flush=True)
        print("      This is about the COPY on PyPI, not your local dist/ folder.", flush=True)
        print("      PyPI does NOT allow overwriting existing files.", flush=True)
        print("      To upload again you must:", flush=True)
        print("        1) Bump the version in pyproject.toml (e.g. 0.1.0 -> 0.1.1)", flush=True)
        print("        2) Re-run this script (it will clean & rebuild dist/ for you).", flush=True)

    print(f"\n❌ twine exited with code {result.returncode}.", flush=True)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    project_root = argv[0] if argv else None
    return register_to_pypi(project_root=project_root, rebuild=True, clean_dist=True)


if __name__ == "__main__":
    raise SystemExit(main())
