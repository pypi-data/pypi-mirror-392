import os

import pytest


def pytest_collection_modifyitems(config, items):
    # Gate performance tests behind RUN_BENCHMARK to avoid flaky CI and plugin
    # constraints (e.g., pytest-benchmark fixture single-use limitations).
    run = os.getenv("RUN_BENCHMARK", "").lower() in {"1", "true", "yes", "on"}
    if run:
        return
    skip_marker = pytest.mark.skip(reason="Benchmarks disabled; set RUN_BENCHMARK=true to enable")
    for item in items:
        item.add_marker(skip_marker)

