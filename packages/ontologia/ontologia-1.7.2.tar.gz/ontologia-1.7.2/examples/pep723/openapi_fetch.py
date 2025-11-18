# /// script
# dependencies = ["httpx>=0.28,<0.29"]
# ///

"""Fetch and summarize OpenAPI schema.

Usage:
  BASE_URL=http://127.0.0.1:8000 uv run examples/pep723/openapi_fetch.py
"""

from __future__ import annotations

import os

import httpx


def base_url() -> str:
    if url := os.getenv("BASE_URL"):
        return url.rstrip("/")
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "8000")
    return f"http://{host}:{port}"


def main() -> int:
    url = base_url()
    with httpx.Client(timeout=10.0) as client:
        r = client.get(f"{url}/openapi.json")
    if r.status_code != 200:
        print("Failed:", r.status_code)
        return 1
    doc = r.json()
    paths = doc.get("paths", {})
    tags = {t.get("name") for t in doc.get("tags", []) if isinstance(t, dict)}
    print("title:", doc.get("info", {}).get("title"))
    print("version:", doc.get("info", {}).get("version"))
    print("paths:", len(paths))
    print("tags:", ", ".join(sorted(t for t in tags if t)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
