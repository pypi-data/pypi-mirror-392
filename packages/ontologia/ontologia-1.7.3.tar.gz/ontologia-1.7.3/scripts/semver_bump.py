#!/usr/bin/env python3
import argparse
import datetime as _dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "docs" / "changelog" / "CHANGELOG.md"


SEMVER_RE = re.compile(r"^(?P<maj>\d+)\.(?P<min>\d+)\.(?P<pat>\d+)(?P<rest>.*)$")


def _read_pyproject_text() -> str:
    return PYPROJECT.read_text(encoding="utf-8")


def _extract_version(text: str) -> tuple[str, int]:
    """Return (version, offset) from the first version assignment under [project].

    This is a simple regex-based approach to avoid re-serializing the TOML file.
    """
    # Search only within the [project] section for safety
    m_proj = re.search(r"(?ms)^\[project\].*?(?=^\[|\Z)", text)
    scope = m_proj.group(0) if m_proj else text
    m = re.search(r"(?m)^version\s*=\s*\"([^\"]+)\"", scope)
    if not m:
        raise SystemExit("Could not find version in pyproject.toml [project] section")
    version = m.group(1)
    # Calculate absolute offset
    start = (m_proj.start() if m_proj else 0) + m.start(0)
    return version, start


def bump_semver(version: str, part: str) -> str:
    m = SEMVER_RE.match(version)
    if not m:
        raise SystemExit(f"Current version '{version}' is not a valid semver x.y.z*")
    maj, min_, pat, rest = (
        int(m.group("maj")),
        int(m.group("min")),
        int(m.group("pat")),
        m.group("rest"),
    )
    # Drop any suffix on bump
    rest = ""
    if part == "major":
        return f"{maj + 1}.0.0"
    if part == "minor":
        return f"{maj}.{min_ + 1}.0"
    if part == "patch":
        return f"{maj}.{min_}.{pat + 1}"
    raise SystemExit("part must be one of: major, minor, patch")


def write_pyproject_version(new_version: str) -> None:
    text = _read_pyproject_text()

    # Replace only the first version assignment under [project]
    def _repl(match: re.Match) -> str:
        return f'version = "{new_version}"'

    def _sub_in_scope(scope_text: str) -> str:
        return re.sub(r"(?m)^version\s*=\s*\"[^\"]+\"", _repl, scope_text, count=1)

    m_proj = re.search(r"(?ms)^\[project\].*?(?=^\[|\Z)", text)
    if m_proj:
        scope = m_proj.group(0)
        new_scope = _sub_in_scope(scope)
        new_text = text[: m_proj.start()] + new_scope + text[m_proj.end() :]
    else:
        new_text = re.sub(r"(?m)^version\s*=\s*\"[^\"]+\"", _repl, text, count=1)
    PYPROJECT.write_text(new_text, encoding="utf-8")


def update_changelog(new_version: str) -> None:
    if not CHANGELOG.exists():
        return
    today = _dt.date.today().isoformat()
    header = f"## [{new_version}] - {today}\n\n- Placeholder: summarize changes.\n\n"
    existing = CHANGELOG.read_text(encoding="utf-8")
    # Avoid duplicating if the top already matches the new version
    if existing.lstrip().startswith(f"## [{new_version}]"):
        return
    CHANGELOG.write_text(header + existing, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump semantic version in pyproject.toml")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "part", nargs="?", choices=["major", "minor", "patch"], help="Which part to bump"
    )
    group.add_argument("--set", dest="set_version", help="Set an explicit version (x.y.z)")
    parser.add_argument("--no-changelog", action="store_true", help="Do not update CHANGELOG.md")
    args = parser.parse_args()

    current_text = _read_pyproject_text()
    current_version, _ = _extract_version(current_text)

    if args.set_version:
        new_version = args.set_version
    else:
        new_version = bump_semver(current_version, args.part)

    if new_version == current_version:
        print(new_version)
        return

    write_pyproject_version(new_version)
    if not args.no_changelog:
        update_changelog(new_version)

    print(new_version)


if __name__ == "__main__":
    main()
