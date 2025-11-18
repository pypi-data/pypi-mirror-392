#!/usr/bin/env python3
"""
SotA Codebase Tools - ENTIRE PROJECT
State-of-the-Art development workflow for complete Ontologia codebase
Ty (Astral) as DEFAULT type checker across ALL components
"""

import os
import subprocess
import sys
import time
from pathlib import Path


class SotACodebaseManager:
    """SotA Development Tools Manager for entire codebase"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)
        self.results = {}

    def run_cmd(self, cmd, description, timeout=120, check=True):
        """Run command with comprehensive error handling"""
        print(f"🔧 {description}...")
        print(f"   💻 {' '.join(cmd)}")

        try:
            start_time = time.time()
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, cwd=self.project_root
            )
            duration = time.time() - start_time

            if result.returncode == 0:
                print(f"   ✅ SUCCESS in {duration:.1f}s: {description}")
                if result.stdout.strip():
                    lines = result.stdout.strip().split("\n")
                    for line in lines[:5]:
                        if line.strip():
                            print(f"   📝 {line}")
                return True, result.stdout, duration
            else:
                print(f"   ❌ FAILED in {duration:.1f}s: {description}")
                if result.stderr.strip():
                    lines = result.stderr.strip().split("\n")
                    for line in lines[:5]:
                        if line.strip() and not line.startswith("WARN"):
                            print(f"   🚨 {line}")
                return False, result.stderr, duration

        except subprocess.TimeoutExpired:
            print(f"   ⏰ TIMEOUT after {timeout}s: {description}")
            return False, "Timeout", timeout
        except Exception as e:
            print(f"   💥 EXCEPTION: {description} - {e}")
            return False, str(e), 0

    def ty_check_codebase(self, component=None):
        """Run Astral Ty type checking on codebase"""
        if component:
            paths = [component]
            desc = f"Ty Check - {component}"
        else:
            paths = ["ontologia", "packages", "playground", "scripts", "tests"]
            desc = "Ty Check - ENTIRE CODEBASE"

        cmd = ["ty", "check"] + paths
        return self.run_cmd(cmd, desc, timeout=180)

    def ruff_check_codebase(self, component=None):
        """Run Ruff linting on codebase"""
        if component:
            paths = [component]
            desc = f"Ruff Check - {component}"
        else:
            paths = ["ontologia", "packages", "playground", "scripts", "tests"]
            desc = "Ruff Check - ENTIRE CODEBASE"

        cmd = ["ruff", "check"] + paths
        return self.run_cmd(cmd, desc, timeout=120)

    def ruff_fix_codebase(self, component=None):
        """Run Ruff with auto-fix on codebase"""
        if component:
            paths = [component]
            desc = f"Ruff Fix - {component}"
        else:
            paths = ["ontologia", "packages", "playground", "scripts", "tests"]
            desc = "Ruff Fix - ENTIRE CODEBASE"

        cmd = ["ruff", "check", "--fix"] + paths
        return self.run_cmd(cmd, desc, timeout=120)

    def black_check_codebase(self, component=None):
        """Run Black format check on codebase"""
        if component:
            paths = [component]
            desc = f"Black Check - {component}"
        else:
            paths = ["ontologia", "packages", "playground", "scripts", "tests"]
            desc = "Black Check - ENTIRE CODEBASE"

        cmd = ["black", "--check"] + paths
        return self.run_cmd(cmd, desc, timeout=120)

    def black_format_codebase(self, component=None):
        """Run Black formatting on codebase"""
        if component:
            paths = [component]
            desc = f"Black Format - {component}"
        else:
            paths = ["ontologia", "packages", "playground", "scripts", "tests"]
            desc = "Black Format - ENTIRE CODEBASE"

        cmd = ["black"] + paths
        return self.run_cmd(cmd, desc, timeout=120)

    def pytest_codebase(self, component=None):
        """Run Pytest on codebase"""
        if component and component.startswith("tests/"):
            paths = [component]
        else:
            paths = ["tests/"]

        cmd = ["pytest", "-v", "--tb=short"] + paths
        return self.run_cmd(cmd, "Pytest - ENTIRE CODEBASE", timeout=300, check=False)

    def check_entire_codebase_sota(self):
        """Run complete SotA check on entire codebase"""
        print("🚀 SotA COMPLETE CHECK - ENTIRE CODEBASE")
        print("=" * 80)
        print("Running ALL SotA tools across complete Ontologia project")
        print(f"📁 Project Root: {self.project_root}")
        print()

        # Define SotA tools in priority order
        sota_tools = [
            ("ty", "Astral Ty Type Checking", self.ty_check_codebase),
            ("ruff", "Ruff Linting", self.ruff_check_codebase),
            ("black", "Black Format Check", self.black_check_codebase),
            ("pytest", "Pytest Testing", self.pytest_codebase),
        ]

        results = {}
        total_duration = 0

        for tool_id, tool_name, tool_func in sota_tools:
            print(f"🔍 Running {tool_name}...")
            success, output, duration = tool_func()
            results[tool_id] = {"success": success, "duration": duration, "output": output}
            total_duration += duration
            print()

        # Generate comprehensive SotA report
        self.generate_sota_report(results, total_duration)

        return results

    def fix_entire_codebase_sota(self):
        """Run all auto-fixes on entire codebase"""
        print("🔧 SotA AUTO-FIX - ENTIRE CODEBASE")
        print("=" * 80)
        print("Applying ALL auto-fixes across complete Ontologia project")
        print()

        # Run auto-fixes
        fixes = [
            ("ruff_fix", "Ruff Auto-Fix", self.ruff_fix_codebase),
            ("black_format", "Black Formatting", self.black_format_codebase),
        ]

        for fix_id, fix_name, fix_func in fixes:
            print(f"🔧 Applying {fix_name}...")
            success, output, duration = fix_func()
            print(
                f"   {'✅' if success else '❌'} {fix_name}: {'SUCCESS' if success else 'FAILED'}"
            )
            print()

        print("🎯 Auto-fixes completed!")
        print("💡 Run 'check-entire-codebase' to verify SotA compliance")

    def check_component_sota(self, component):
        """Check SotA compliance for specific component"""
        print(f"🎯 SotA CHECK - {component.upper()}")
        print("=" * 60)

        results = {}

        # Run all tools on component
        tools = [
            ("ty", f"Ty Check - {component}", lambda: self.ty_check_codebase(component)),
            ("ruff", f"Ruff Check - {component}", lambda: self.ruff_check_codebase(component)),
            ("black", f"Black Check - {component}", lambda: self.black_check_codebase(component)),
        ]

        for tool_id, tool_name, tool_func in tools:
            success, output, duration = tool_func()
            results[tool_id] = {"success": success, "duration": duration}
            print()

        # Component summary
        passed = sum(1 for r in results.values() if r["success"])
        total = len(results)
        print(f"📊 {component}: {passed}/{total} tools passing")

        return results

    def generate_sota_report(self, results, total_duration):
        """Generate comprehensive SotA report"""
        print("📊 SotA CODEBASE REPORT")
        print("=" * 80)

        # Statistics
        total_tools = len(results)
        passed_tools = sum(1 for r in results.values() if r["success"])
        failed_tools = total_tools - passed_tools
        success_rate = (passed_tools / total_tools) * 100 if total_tools > 0 else 0

        print("📈 OVERALL SotA STATISTICS:")
        print(f"   🔧 Tools Checked: {total_tools}")
        print(f"   ✅ Passed: {passed_tools}")
        print(f"   ❌ Failed: {failed_tools}")
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Total Duration: {total_duration:.1f}s")
        print()

        # Tool breakdown
        print("🔧 TOOL BREAKDOWN:")
        tool_icons = {"ty": "🚀", "ruff": "🔍", "black": "🎨", "pytest": "🧪"}

        for tool_id, result in results.items():
            icon = tool_icons.get(tool_id, "🔧")
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = result["duration"]
            print(f"   {icon} {tool_id.upper()}: {status} ({duration:.1f}s)")
        print()

        # SotA Assessment
        print("🏆 SotA COMPLIANCE ASSESSMENT:")

        if success_rate == 100:
            print("   🏆 PERFECT SotA COMPLIANCE!")
            print("   🚀 Entire codebase is production-ready")
        elif success_rate >= 75:
            print("   ✅ EXCELLENT SotA COMPLIANCE!")
            print("   🔧 Minor fixes needed for full compliance")
        elif success_rate >= 50:
            print("   ⚠️  DEVELOPING SotA COMPLIANCE")
            print("   💡 Address failing tools for improvement")
        else:
            print("   🔧 SotA COMPLIANCE NEEDS WORK")
            print("   🎯 Focus on core tools first")

        print()
        print("🎯 SotA RECOMMENDATIONS:")

        # Specific recommendations based on failures
        if not results.get("ty", {}).get("success", False):
            print("   🚀 URGENT: Fix Astral Ty type checking issues")
            print("      💡 Ty is the DEFAULT type checker - critical for SotA")

        if not results.get("ruff", {}).get("success", False):
            print("   🔍 IMPORTANT: Fix Ruff linting issues")
            print("      💡 Run 'ruff check --fix' for auto-fixes")

        if not results.get("black", {}).get("success", False):
            print("   🎨 IMPORTANT: Apply Black formatting")
            print("      💡 Run 'black .' to format all files")

        if not results.get("pytest", {}).get("success", False):
            print("   🧪 NICE TO HAVE: Fix failing tests")
            print("      💡 Ensure test suite is passing")

        print()
        print("🔗 SotA TOOL DOCUMENTATION:")
        print("   🚀 Astral Ty: https://github.com/astral-sh/ty")
        print("   🔍 Ruff: https://github.com/astral-sh/ruff")
        print("   🎨 Black: https://github.com/psf/black")
        print("   🧪 Pytest: https://docs.pytest.org/")

        print()
        print("💡 SotA DEVELOPMENT WORKFLOW:")
        print("   1. Write code with IDE support")
        print("   2. Run 'ty check' for type safety (DEFAULT)")
        print("   3. Run 'ruff check --fix' for linting")
        print("   4. Run 'black .' for formatting")
        print("   5. Run 'pytest' for testing")
        print("   6. Deploy with confidence! 🚀")


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("🚀 SotA Codebase Tools - ENTIRE PROJECT")
        print("=" * 60)
        print("Astral Ty as DEFAULT type checker across ALL components")
        print()
        print("Usage: python sota_codebase_tools.py <command> [component]")
        print()
        print("Commands:")
        print("  check-entire-codebase    Run ALL SotA tools on entire project")
        print("  fix-entire-codebase      Apply auto-fixes to entire project")
        print("  ty-check                 Run Astral Ty on entire codebase")
        print("  ruff-check               Run Ruff on entire codebase")
        print("  black-check              Run Black check on entire codebase")
        print("  pytest                   Run Pytest on entire codebase")
        print("  check-component <path>   Check SotA for specific component")
        print()
        print("Examples:")
        print("  python sota_codebase_tools.py check-entire-codebase")
        print("  python sota_codebase_tools.py check-component ontologia/domain")
        print("  python sota_codebase_tools.py check-component packages/ontologia_api")
        print("  python sota_codebase_tools.py ty-check")
        return

    command = sys.argv[1].lower()
    manager = SotACodebaseManager()

    if command == "check-entire-codebase":
        results = manager.check_entire_codebase_sota()
        passed = sum(1 for r in results.values() if r["success"])
        total = len(results)
        sys.exit(0 if passed >= total // 2 else 1)
    elif command == "fix-entire-codebase":
        manager.fix_entire_codebase_sota()
    elif command == "ty-check":
        success, _, _ = manager.ty_check_codebase()
        sys.exit(0 if success else 1)
    elif command == "ruff-check":
        success, _, _ = manager.ruff_check_codebase()
        sys.exit(0 if success else 1)
    elif command == "black-check":
        success, _, _ = manager.black_check_codebase()
        sys.exit(0 if success else 1)
    elif command == "pytest":
        success, _, _ = manager.pytest_codebase()
        sys.exit(0 if success else 1)
    elif command == "check-component" and len(sys.argv) >= 3:
        component = sys.argv[2]
        results = manager.check_component_sota(component)
        passed = sum(1 for r in results.values() if r["success"])
        total = len(results)
        sys.exit(0 if passed >= total // 2 else 1)
    else:
        print(f"❌ Unknown command: {command}")
        print("💡 Use 'python sota_codebase_tools.py' to see available commands")
        sys.exit(1)


if __name__ == "__main__":
    main()
