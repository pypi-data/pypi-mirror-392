#!/usr/bin/env python3
"""
SotA Development Tools Script
State-of-the-Art development workflow for Ontologia project
Includes Ty, Ruff, Black, Pytest integration
"""

import os
import subprocess
import sys
from pathlib import Path


class SotATools:
    """State-of-the-Art development tools manager"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)

    def run_cmd(self, cmd, description, check=True):
        """Run command with error handling"""
        print(f"🔧 {description}...")
        print(f"   💻 {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)

            if result.stdout.strip():
                # Show first few lines of output
                lines = result.stdout.strip().split("\n")
                for line in lines[:5]:
                    print(f"   📝 {line}")
                if len(lines) > 5:
                    print(f"   ... ({len(lines)-5} more lines)")

            print(f"   ✅ {description} - SUCCESS")
            return True, result.stdout, result.stderr

        except subprocess.CalledProcessError as e:
            print(f"   ❌ {description} - FAILED")
            if e.stderr.strip():
                print(f"   🚨 Error: {e.stderr.strip()}")
            return False, e.stdout, e.stderr
        except Exception as e:
            print(f"   💥 {description} - EXCEPTION: {e}")
            return False, "", str(e)

    def ty_check(self, paths=None):
        """Run Astral Ty type checking"""
        if paths is None:
            paths = ["ontologia", "packages", "playground", "scripts"]

        cmd = ["ty", "check"] + paths
        return self.run_cmd(cmd, "Astral Ty Type Checking")

    def ruff_check(self, paths=None):
        """Run Ruff linting"""
        if paths is None:
            paths = ["ontologia", "packages", "playground", "scripts"]

        cmd = ["ruff", "check"] + paths
        return self.run_cmd(cmd, "Ruff Linting")

    def ruff_fix(self, paths=None):
        """Run Ruff with auto-fix"""
        if paths is None:
            paths = ["ontologia", "packages", "playground", "scripts"]

        cmd = ["ruff", "check", "--fix"] + paths
        return self.run_cmd(cmd, "Ruff Auto-Fix")

    def black_check(self, paths=None):
        """Run Black formatting check"""
        if paths is None:
            paths = ["ontologia", "packages", "playground", "scripts"]

        cmd = ["black", "--check"] + paths
        return self.run_cmd(cmd, "Black Format Check")

    def black_format(self, paths=None):
        """Run Black formatting"""
        if paths is None:
            paths = ["ontologia", "packages", "playground", "scripts"]

        cmd = ["black"] + paths
        return self.run_cmd(cmd, "Black Formatting")

    def pytest_run(self, paths=None):
        """Run Pytest"""
        if paths is None:
            paths = ["tests/"]

        cmd = ["pytest", "-v"] + paths
        return self.run_cmd(cmd, "Pytest Testing", check=False)

    def check_all(self, paths=None):
        """Run all SotA checks"""
        print("🚀 SotA COMPLETE CHECK")
        print("=" * 60)

        results = {}

        # 1. Ty Type Checking
        results["ty"] = self.ty_check(paths)[0]
        print()

        # 2. Ruff Linting
        results["ruff"] = self.ruff_check(paths)[0]
        print()

        # 3. Black Formatting
        results["black"] = self.black_check(paths)[0]
        print()

        # 4. Pytest
        results["pytest"] = self.pytest_run(paths)[0]
        print()

        # Summary
        print("📊 SotA CHECK SUMMARY")
        print("=" * 60)

        for tool, success in results.items():
            status = "✅" if success else "❌"
            tool_name = tool.upper()
            print(f"{status} {tool_name}: {'PASS' if success else 'FAIL'}")

        total_passed = sum(results.values())
        total_tools = len(results)

        print(f"\n📈 Overall: {total_passed}/{total_tools} tools passing")

        if total_passed == total_tools:
            print("🏆 PERFECT SotA COMPLIANCE!")
            print("🚀 Ready for production deployment")
        elif total_passed >= total_tools - 1:
            print("✅ EXCELLENT SotA COMPLIANCE!")
            print("🔧 Minor fixes needed for full compliance")
        else:
            print("⚠️  SotA COMPLIANCE NEEDS WORK")
            print("💡 Address failing tools before deployment")

        return total_passed == total_tools

    def fix_all(self, paths=None):
        """Run all auto-fixes"""
        print("🔧 SotA AUTO-FIX")
        print("=" * 60)

        # 1. Ruff auto-fix
        self.ruff_fix(paths)
        print()

        # 2. Black formatting
        self.black_format(paths)
        print()

        print("✅ Auto-fixes completed!")
        print("💡 Run 'check_all' to verify compliance")

    def playground_check(self):
        """Check only playground notebooks"""
        print("🎯 PLAYGROUND SotA CHECK")
        print("=" * 60)

        paths = ["playground/notebooks"]
        return self.check_all(paths)

    def core_check(self):
        """Check only core packages"""
        print("🏛️  CORE SotA CHECK")
        print("=" * 60)

        paths = ["ontologia", "packages"]
        return self.check_all(paths)


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("🚀 SotA Development Tools")
        print("=" * 60)
        print("Usage: python sota_tools.py <command>")
        print()
        print("Commands:")
        print("  check-all      Run all SotA checks (Ty, Ruff, Black, Pytest)")
        print("  fix-all        Run auto-fixes (Ruff fix, Black format)")
        print("  ty-check       Run Astral Ty type checking")
        print("  ruff-check     Run Ruff linting")
        print("  black-check    Run Black format check")
        print("  pytest         Run Pytest")
        print("  playground     Check playground notebooks only")
        print("  core           Check core packages only")
        print()
        print("Examples:")
        print("  python sota_tools.py check-all")
        print("  python sota_tools.py playground")
        print("  python sota_tools.py fix-all")
        return

    command = sys.argv[1].lower()
    tools = SotATools()

    if command == "check-all":
        success = tools.check_all()
        sys.exit(0 if success else 1)
    elif command == "fix-all":
        tools.fix_all()
    elif command == "ty-check":
        tools.ty_check()
    elif command == "ruff-check":
        tools.ruff_check()
    elif command == "black-check":
        tools.black_check()
    elif command == "pytest":
        tools.pytest_run()
    elif command == "playground":
        success = tools.playground_check()
        sys.exit(0 if success else 1)
    elif command == "core":
        success = tools.core_check()
        sys.exit(0 if success else 1)
    else:
        print(f"❌ Unknown command: {command}")
        print("💡 Use 'python sota_tools.py' to see available commands")
        sys.exit(1)


if __name__ == "__main__":
    main()
