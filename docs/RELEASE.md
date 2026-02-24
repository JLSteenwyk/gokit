# GOKIT Release Checklist

## Pre-release
1. Update version in `pyproject.toml` and `src/gokit/__init__.py`.
2. Run local checks:
   - `PYTHONPATH=src python3 -m compileall -q src tests`
   - `PYTHONPATH=src pytest`
3. Verify CI green on all Python versions.
4. Confirm plot smoke lane passes.
5. Update `README.md` and migration notes if CLI behavior changed.

## Tag and build
1. Create tag: `git tag vX.Y.Z`
2. Build artifacts:
   - `python -m pip install --upgrade build`
   - `python -m build`
3. Validate artifacts:
   - `python -m pip install --upgrade twine`
   - `twine check dist/*`

## Publish
1. Upload to PyPI/TestPyPI using trusted publisher or token.
2. Publish GitHub release notes summarizing:
   - new commands/options
   - compatibility notes
   - plotting/reporting highlights

## Post-release
1. Bump to next dev version.
2. Archive release artifacts for the release commit.
