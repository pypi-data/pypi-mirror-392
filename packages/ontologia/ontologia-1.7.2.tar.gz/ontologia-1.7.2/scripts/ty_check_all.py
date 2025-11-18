#!/usr/bin/env python3
"""
SotA Type Checking Script - Astral Ty
Run comprehensive type checking across the entire Ontologia project
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, cwd=None):
    """Run a command and handle results"""
    print(f"🔍 {description}...")
    print(f"   💻 Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"   ✅ SUCCESS: {description}")
            if result.stdout.strip():
                print(f"   📝 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ FAILED: {description}")
            if result.stderr.strip():
                print(f"   🚨 Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   💥 EXCEPTION: {description} - {e}")
        return False


def main():
    """Run comprehensive SotA type checking"""
    print("🚀 SotA TYPE CHECKING - ASTRAL TY")
    print("=" * 60)
    print("Running comprehensive type checking across Ontologia project")
    print()

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print(f"📁 Project Root: {project_root}")
    print()

    # Define components to check
    components = [
        {
            "name": "Core Ontologia Package",
            "paths": ["ontologia"],
            "description": "Main domain logic and models",
        },
        {
            "name": "API Packages",
            "paths": ["packages/ontologia_api"],
            "description": "FastAPI endpoints and services",
        },
        {
            "name": "CLI Package",
            "paths": ["packages/ontologia_cli"],
            "description": "Command-line interface",
        },
        {"name": "SDK Package", "paths": ["packages/ontologia_sdk"], "description": "Python SDK"},
        {
            "name": "Playground Notebooks",
            "paths": ["playground/notebooks"],
            "description": "Marimo notebooks and demos",
        },
        {"name": "Scripts", "paths": ["scripts"], "description": "Utility and automation scripts"},
    ]

    # Results tracking
    results = []

    for component in components:
        print(f"📦 Checking: {component['name']}")
        print(f"   📝 {component['description']}")

        # Check if paths exist
        existing_paths = []
        for path in component["paths"]:
            if os.path.exists(path):
                existing_paths.append(path)

        if not existing_paths:
            print(f"   ⚠️  No paths found for {component['name']}")
            results.append((component["name"], False, "No paths found"))
            print()
            continue

        # Run Ty check
        cmd = ["ty", "check"] + existing_paths
        success = run_command(cmd, f"Ty check - {component['name']}", cwd=project_root)

        results.append((component["name"], success, "Checked" if success else "Type errors found"))
        print()

    # Summary
    print("📊 SotA TYPE CHECKING SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print()

    if successful:
        print("🎉 COMPONENTS WITH CLEAN TYPES:")
        for name, _, status in successful:
            print(f"   ✅ {name}: {status}")
        print()

    if failed:
        print("⚠️  COMPONENTS WITH TYPE ISSUES:")
        for name, _, status in failed:
            print(f"   ❌ {name}: {status}")
        print()

    # Recommendations
    print("🎯 SotA RECOMMENDATIONS:")

    if len(successful) == len(results):
        print("   🏆 PERFECT: All components have clean types!")
        print("   🚀 Ready for production deployment")
    elif len(successful) > len(failed):
        print("   ✅ GOOD: Most components are type-safe")
        print("   🔧 Fix remaining issues for full SotA compliance")
    else:
        print("   🔧 WORK NEEDED: Multiple type issues found")
        print("   💡 Focus on core components first")

    print()
    print("🔗 ASTRAL TY DOCUMENTATION:")
    print("   https://github.com/astral-sh/ty")
    print()
    print("💡 SotA TIPS:")
    print("   • Run 'ty check <path>' for specific files")
    print("   • Use 'ty check --fix' for auto-fixes (when available)")
    print("   • Check pyproject.toml for Ty configuration")
    print("   • All new code should pass Ty checks")

    return len(failed) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
