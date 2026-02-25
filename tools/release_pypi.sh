#!/usr/bin/env bash
set -euo pipefail

# Standard PyPI release flow for this project.
# Equivalent to setup.py-based workflows, but uses pyproject/hatchling build.

REPOSITORY="${1:-pypi}"

python -m pip install --upgrade build twine
rm -rf dist
python -m build
python -m twine check dist/*
python -m twine upload dist/* -r "${REPOSITORY}"
