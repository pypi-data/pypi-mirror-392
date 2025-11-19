#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ALLOWED = (
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "revert",
    "style",
    "test",
)


PATTERN = re.compile(rf"^(?:({'|'.join(ALLOWED)})(?:\([a-z0-9_.-]+\))?: .+|Merge .+)$")


def main() -> int:
    # pre-commit passes the commit message path as .git/COMMIT_EDITMSG implicitly when using language: system and stages: commit-msg
    # To be robust, we read the default path.
    msg_file = Path(".git/COMMIT_EDITMSG")
    if not msg_file.exists():
        return 0
    first_line = msg_file.read_text(encoding="utf-8", errors="replace").splitlines()[0].strip()
    if PATTERN.match(first_line):
        return 0
    sys.stderr.write(
        "\n✖ Commit message must follow Conventional Commits.\n"
        "  Allowed types: " + ", ".join(ALLOWED) + "\n"
        "  Example: feat(api): add traversal endpoint\n"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
