# GOKIT Release Checklist

## Pre-release
1. Update version in `pyproject.toml` and `src/gokit/__init__.py`.
2. Run local checks:
   - `PYTHONPATH=src python3 -m compileall -q src tests`
   - `PYTHONPATH=src pytest`
3. Verify CI green on all Python versions.
4. Confirm plot smoke lane passes.
5. Update `README.md` and migration notes if CLI behavior changed.

## Tag
1. Create tag: `git tag vX.Y.Z`

## Publish
1. Standard publish flow:
   - `python -m pip install --upgrade build twine`
   - `rm -rf dist`
   - `python -m build`
   - `python -m twine check dist/*`
   - `python -m twine upload dist/* -r pypi`
2. Optional TestPyPI:
   - `python -m twine upload dist/* -r testpypi`
3. Equivalent helper script:
   - `./tools/release_pypi.sh` (defaults to `pypi`)
   - `./tools/release_pypi.sh testpypi`
4. Publish GitHub release notes summarizing:
   - new commands/options
   - compatibility notes
   - plotting/reporting highlights

## Post-release
1. Bump to next dev version.
2. Archive release artifacts for the release commit.
