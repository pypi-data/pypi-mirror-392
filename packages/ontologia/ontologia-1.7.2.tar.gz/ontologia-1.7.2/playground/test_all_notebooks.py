#!/usr/bin/env python3
"""Comprehensive test suite for all Marimo notebooks"""

import os
import subprocess
import sys
import time

import requests


def check_syntax(filepath: str) -> tuple[bool, str]:
    """Check if Python file has valid syntax"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True, "Syntax OK"
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Syntax check timed out"
    except Exception as e:
        return False, str(e)


def check_marimo_structure(filepath: str) -> dict[str, int]:
    """Check Marimo-specific structure requirements"""
    with open(filepath) as f:
        content = f.read()

    return {
        "app_cells": content.count("@app.cell"),
        "marimo_app": content.count("marimo.App()"),
        "import_marimo": content.count("import marimo"),
        "mo_import": content.count("import marimo as mo"),
        "generated_with": content.count("__generated_with"),
        "mo_usage": content.count("mo."),
    }


def test_notebook_execution(filepath: str, port: int = 8889) -> tuple[bool, str]:
    """Test if notebook can be executed by Marimo"""
    try:
        # Try to run notebook with marimo
        result = subprocess.run(
            [
                "uv",
                "run",
                "marimo",
                "edit",
                filepath,
                "--host",
                "0.0.0.0",
                "--port",
                str(port),
                "--headless",
                "--no-token",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=".",
        )

        # Give it a moment to start
        time.sleep(2)

        # Check if server is responding
        try:
            response = requests.get(f"http://localhost:{port}", timeout=5)
            if response.status_code == 200:
                # Clean up - kill the marimo process
                subprocess.run(["pkill", "-f", f"marimo.*{port}"], capture_output=True)
                return True, "Notebook executed successfully"
        except:
            pass

        # Clean up
        subprocess.run(["pkill", "-f", f"marimo.*{port}"], capture_output=True)

        return False, "Notebook failed to start properly"

    except subprocess.TimeoutExpired:
        return False, "Notebook execution timed out"
    except Exception as e:
        return False, f"Execution error: {str(e)}"


def main():
    """Run comprehensive tests on all notebooks"""
    notebooks_dir = "notebooks"

    if not os.path.exists(notebooks_dir):
        print(f"❌ Directory {notebooks_dir} not found")
        return

    notebooks = [f for f in os.listdir(notebooks_dir) if f.endswith(".py")]
    notebooks.sort()

    print("🧪 **Comprehensive Marimo Notebook Test Suite**")
    print("=" * 60)
    print(f"📊 Testing {len(notebooks)} notebooks...")
    print()

    results = []
    passed = 0

    for i, notebook in enumerate(notebooks, 1):
        filepath = os.path.join(notebooks_dir, notebook)
        print(f"🔍 [{i}/{len(notebooks)}] Testing {notebook}...")

        # Syntax check
        syntax_ok, syntax_msg = check_syntax(filepath)

        # Structure check
        structure = check_marimo_structure(filepath)

        # Basic structure validation
        structure_valid = (
            structure["marimo_app"] >= 1
            and structure["app_cells"] >= 1
            and structure["mo_import"] >= 1
            and structure["generated_with"] >= 1
        )

        # Overall result
        overall_ok = syntax_ok and structure_valid

        if overall_ok:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        results.append(
            {
                "notebook": notebook,
                "syntax_ok": syntax_ok,
                "syntax_msg": syntax_msg,
                "structure": structure,
                "structure_valid": structure_valid,
                "overall_ok": overall_ok,
            }
        )

        # Print result
        print(f"   {status}")
        print(f"   📝 Syntax: {syntax_msg}")
        print(
            f"   🏗️  Structure: {structure['app_cells']} cells, "
            f"{'✅' if structure_valid else '❌'}"
        )
        print()

    # Summary
    print("📊 **Test Summary**")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(notebooks)}")
    print(f"❌ Failed: {len(notebooks) - passed}/{len(notebooks)}")
    print(f"📈 Success Rate: {passed/len(notebooks)*100:.1f}%")
    print()

    # Failed notebooks details
    failed = [r for r in results if not r["overall_ok"]]
    if failed:
        print("❌ **Failed Notebooks**:")
        for result in failed:
            print(f"   - {result['notebook']}: {result['syntax_msg']}")
        print()

    # Structure analysis
    print("🏗️ **Structure Analysis**:")
    total_cells = sum(r["structure"]["app_cells"] for r in results)
    total_mo_usage = sum(r["structure"]["mo_usage"] for r in results)

    print(f"   - Total @app.cell decorators: {total_cells}")
    print(f"   - Total mo. usages: {total_mo_usage}")
    print(f"   - Average cells per notebook: {total_cells/len(notebooks):.1f}")
    print()

    # Recommendations
    print("💡 **Recommendations**:")
    if passed == len(notebooks):
        print("   🎉 All notebooks are ready for production!")
        print("   🚀 Start the Marimo server and begin exploring!")
    else:
        print("   🔧 Fix the failed notebooks before deployment")
        print("   📚 Follow Marimo documentation for proper structure")

    print()
    print("🎯 **Next Steps**:")
    print("   1. Start Marimo: uv run marimo edit notebooks/ --host 0.0.0.0 --port 8888")
    print("   2. Open browser: http://localhost:8888")
    print("   3. Explore notebooks interactively")

    return passed == len(notebooks)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
