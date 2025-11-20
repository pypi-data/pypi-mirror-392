# HL-MakePIP
Makes a project pip project


pip install "git+https://github.com/USERNAME/REPO_NAME.git@BRANCH_OR_TAG"


ENTRY POINTS:
setup_project_env() - Sets up the project env. (pyproject.toml) User customizes.
build_project() - Builds the project into a proper environment.
register_to_test_pypi() - Registers to test PYPI. Requires API Key.
register_to_pypi() - Registers to PYPI. Requires API Key.


Future experimentation w/ github workflows. 
- Workflow creation automated. (.github/workflows/publish.yml) already.
- Exact workflow to compile succuessfully w/ "Trusted Publisher" automatically not figured out.

RQS NOT Automated.

