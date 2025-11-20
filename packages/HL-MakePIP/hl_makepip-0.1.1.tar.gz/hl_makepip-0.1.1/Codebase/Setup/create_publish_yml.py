from pathlib import Path

PUBLISH_YML_CONTENT = """\
name: Publish to PyPI

on:
  push:
    tags:
      - "v*.*.*"   # e.g. v0.1.0, v1.2.3

permissions:
  contents: read
  id-token: write    # REQUIRED for trusted publisher (OIDC)

jobs:
  build-and-publish:
    name: Build and publish Python package
    runs-on: ubuntu-latest
    environment: pypi   # must match the “Environment name” in your screenshot

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install build backend
        run: |
          python -m pip install --upgrade pip
          python -m pip install build

      - name: Build sdist and wheel
        run: |
          python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # NOTE: no password / token needed when using trusted publisher


"""


def create_publish_yml(project_root: Path, publish_path: Path, force: bool) -> None:
    # Ensure project root exists
    project_root.mkdir(parents=True, exist_ok=True)

    # Ensure the directory for publish.yml exists, e.g. .github/workflows
    publish_path.parent.mkdir(parents=True, exist_ok=True)

    if publish_path.exists() and not force:
        print(f"[setup-project-env] {publish_path} already exists. "
              f"Use --force to overwrite.")
        return

    action = "Overwriting" if publish_path.exists() else "Creating"
    print(f"[setup-project-env] {action} {publish_path}")
    publish_path.write_text(PUBLISH_YML_CONTENT, encoding="utf-8")
