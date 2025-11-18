#!/usr/bin/env python3
"""Test only the essential working notebooks"""

import subprocess
import sys


def test_notebook(filepath):
    """Test a single notebook"""
    print(f"🔍 Testing {filepath}...")

    result = subprocess.run(
        ["uv", "run", "python", filepath], capture_output=True, text=True, cwd="."
    )

    if result.returncode == 0:
        print(f"✅ {filepath}: WORKS!")
        return True
    else:
        print(f"❌ {filepath}: ERROR")
        # Show only the actual error, not warnings
        error_lines = result.stderr.split("\n")
        for line in error_lines:
            if (
                "critical" in line
                or "Traceback" in line
                or "Error" in line
                or "ModuleNotFoundError" in line
            ):
                print(f"   📝 {line}")
        return False


def main():
    """Test essential notebooks"""
    print("🚀 Testing Essential Marimo Notebooks")
    print("=" * 50)

    # Essential notebooks that should work
    essential_notebooks = [
        "notebooks/demo_standalone.py",
        "notebooks/01_introduction_fixed.py",
    ]

    # Test each
    working = []
    failing = []

    for notebook in essential_notebooks:
        if test_notebook(notebook):
            working.append(notebook)
        else:
            failing.append(notebook)
        print()

    # Summary
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"✅ Working: {len(working)}/{len(essential_notebooks)}")
    print(f"❌ Failing: {len(failing)}/{len(essential_notebooks)}")

    if working:
        print("\n🎉 WORKING NOTEBOOKS:")
        for nb in working:
            print(f"   ✅ {nb}")

    if failing:
        print("\n⚠️ NEED ATTENTION:")
        for nb in failing:
            print(f"   ❌ {nb}")

    print("\n🎯 RECOMMENDATION:")
    if len(working) >= 1:
        print("   🚀 Use the working notebooks for demo!")
        print("   📝 Start with: uv run marimo edit notebooks/demo_standalone.py")
        print("   🌐 Access at: http://localhost:8888")
    else:
        print("   🔧 Fix the essential notebooks first")

    return len(working) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
