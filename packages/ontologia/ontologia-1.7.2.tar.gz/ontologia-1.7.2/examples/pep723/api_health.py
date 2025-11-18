# /// script
# dependencies = ["httpx>=0.28,<0.29"]
# ///

"""Simple API health check using PEP 723.

Usage:
  BASE_URL=http://127.0.0.1:8000 uv run examples/pep723/api_health.py
  # or rely on HOST/PORT (defaults 127.0.0.1:8000)
  uv run examples/pep723/api_health.py
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
    with httpx.Client(timeout=5.0) as client:
        root = client.get(f"{url}/")
        health = client.get(f"{url}/health")
    print("/ →", root.status_code, root.headers.get("content-type"))
    print("/health →", health.status_code)
    try:
        data = health.json()
        print("status:", data.get("status"))
        print("details keys:", sorted(data.keys()))
    except Exception:
        pass
    return 0 if health.status_code == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
