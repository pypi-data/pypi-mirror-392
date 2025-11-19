Release Workflow

- Prereqs: Ensure `uv`, `uvx`, and `twine` are available. Login for PyPI is configured for Twine.
- Quality loop: `just check` runs format, lint, arch guardrails, type check, tests.
- Version bump: `just version-bump patch` (or `minor`/`major`) updates `pyproject.toml` and prepends a stub section to `docs/changelog/CHANGELOG.md`.
- Full release: `just release patch` runs checks, bumps, commits, tags, builds, and verifies artifacts.
- Publish: `just publish` uploads `dist/*` to PyPI.
- Merge: `just merge` merges the current branch into `main` and pushes.

Examples

- Develop + test loop: `just check` (repeat until green), then `git commit` as needed.
- Cut a patch release: `just release patch && just publish && just merge`.
- Set explicit version: `uv run python scripts/semver_bump.py --set 1.8.0`.

Notes

- Git commands in `Justfile` are provided for convenience; ensure you are on the correct branch and have the necessary permissions.
- The changelog entry inserted by the bump script is a placeholder; edit it with real changes before/after publishing.
