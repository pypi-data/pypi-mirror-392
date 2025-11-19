#!/usr/bin/env python3
"""
SotA Type Checking - ENTIRE CODEBASE
Astral Ty type checking across ALL Ontologia project components
"""

import os
import subprocess
import sys
import time
from pathlib import Path


class CodebaseTyChecker:
    """SotA Type Checker for entire Ontologia codebase"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)
        self.results = {}

    def run_ty_check(self, paths, description, timeout=60):
        """Run Ty check with timeout and error handling"""
        print(f"🔍 {description}...")
        print(f"   📁 Paths: {', '.join(paths)}")

        cmd = ["ty", "check"] + paths

        try:
            start_time = time.time()
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, cwd=self.project_root
            )
            duration = time.time() - start_time

            if result.returncode == 0:
                print(f"   ✅ SUCCESS in {duration:.1f}s: {description}")
                if result.stdout.strip():
                    # Show key output
                    lines = result.stdout.strip().split("\n")
                    for line in lines[:3]:
                        if line.strip():
                            print(f"   📝 {line}")
                return True, result.stdout, duration
            else:
                print(f"   ❌ FAILED in {duration:.1f}s: {description}")
                if result.stderr.strip():
                    # Show key errors
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

    def check_entire_codebase(self):
        """Check entire codebase with comprehensive breakdown"""
        print("🚀 SotA TYPE CHECKING - ENTIRE CODEBASE")
        print("=" * 80)
        print("Astral Ty type checking across ALL Ontologia components")
        print(f"📁 Project Root: {self.project_root}")
        print()

        # Define all components to check
        components = [
            {
                "name": "Core Domain",
                "paths": ["ontologia/domain"],
                "description": "Business logic and domain models",
                "priority": "HIGH",
            },
            {
                "name": "Application Layer",
                "paths": ["ontologia/application"],
                "description": "Application services and use cases",
                "priority": "HIGH",
            },
            {
                "name": "Infrastructure",
                "paths": ["ontologia/infrastructure"],
                "description": "Database, persistence, external services",
                "priority": "MEDIUM",
            },
            {
                "name": "API Package",
                "paths": ["packages/ontologia_api"],
                "description": "FastAPI endpoints and API services",
                "priority": "HIGH",
            },
            {
                "name": "CLI Package",
                "paths": ["packages/ontologia_cli"],
                "description": "Command-line interface tools",
                "priority": "MEDIUM",
            },
            {
                "name": "SDK Package",
                "paths": ["packages/ontologia_sdk"],
                "description": "Python SDK for external use",
                "priority": "MEDIUM",
            },
            {
                "name": "Edge Package",
                "paths": ["packages/ontologia_edge"],
                "description": "Edge node management and IoT capabilities",
                "priority": "LOW",
            },
            {
                "name": "Dagster Package",
                "paths": ["packages/ontologia_dagster"],
                "description": "Data pipeline orchestration",
                "priority": "LOW",
            },
            {
                "name": "Playground",
                "paths": ["playground"],
                "description": "Marimo notebooks and demos",
                "priority": "MEDIUM",
            },
            {
                "name": "Scripts",
                "paths": ["scripts"],
                "description": "Automation and utility scripts",
                "priority": "LOW",
            },
            {
                "name": "Tests",
                "paths": ["tests"],
                "description": "Test suites and test utilities",
                "priority": "LOW",
            },
        ]

        # Check each component
        total_duration = 0
        for component in components:
            # Check if paths exist
            existing_paths = []
            for path in component["paths"]:
                full_path = self.project_root / path
                if full_path.exists():
                    existing_paths.append(path)

            if not existing_paths:
                print(f"⚠️  {component['name']}: No paths found")
                self.results[component["name"]] = {
                    "success": False,
                    "error": "No paths found",
                    "duration": 0,
                    "priority": component["priority"],
                }
                print()
                continue

            # Run Ty check
            success, output, duration = self.run_ty_check(
                existing_paths,
                f"{component['name']} ({component['priority']} priority)",
                timeout=120 if component["priority"] == "HIGH" else 60,
            )

            self.results[component["name"]] = {
                "success": success,
                "output": output,
                "duration": duration,
                "priority": component["priority"],
                "paths": existing_paths,
            }

            total_duration += duration
            print()

        # Generate comprehensive report
        self.generate_report(total_duration)

        return self.results

    def generate_report(self, total_duration):
        """Generate comprehensive SotA report"""
        print("📊 SotA TYPE CHECKING REPORT - ENTIRE CODEBASE")
        print("=" * 80)

        # Categorize results
        successful = {}
        failed = {}
        by_priority = {"HIGH": [], "MEDIUM": [], "LOW": []}

        for name, result in self.results.items():
            if result["success"]:
                successful[name] = result
            else:
                failed[name] = result

            by_priority[result["priority"]].append((name, result["success"]))

        # Summary statistics
        total_components = len(self.results)
        successful_count = len(successful)
        failed_count = len(failed)
        success_rate = (successful_count / total_components) * 100 if total_components > 0 else 0

        print("📈 OVERALL STATISTICS:")
        print(f"   📦 Total Components: {total_components}")
        print(f"   ✅ Successful: {successful_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Total Duration: {total_duration:.1f}s")
        print()

        # Priority breakdown
        print("🎯 PRIORITY BREAKDOWN:")
        for priority in ["HIGH", "MEDIUM", "LOW"]:
            components = by_priority[priority]
            if components:
                passed = sum(1 for _, success in components if success)
                total = len(components)
                rate = (passed / total) * 100 if total > 0 else 0
                icon = "🔥" if priority == "HIGH" else "⚡" if priority == "MEDIUM" else "💡"
                print(f"   {icon} {priority}: {passed}/{total} ({rate:.1f}%)")
        print()

        # Successful components
        if successful:
            print("🎉 SUCCESSFUL COMPONENTS:")
            for name, result in successful.items():
                priority_icon = (
                    "🔥"
                    if result["priority"] == "HIGH"
                    else "⚡" if result["priority"] == "MEDIUM" else "💡"
                )
                print(f"   ✅ {priority_icon} {name}: {result['duration']:.1f}s")
                if result.get("paths"):
                    print(f"      📁 {', '.join(result['paths'])}")
            print()

        # Failed components
        if failed:
            print("⚠️  COMPONENTS NEEDING ATTENTION:")
            for name, result in failed.items():
                priority_icon = (
                    "🔥"
                    if result["priority"] == "HIGH"
                    else "⚡" if result["priority"] == "MEDIUM" else "💡"
                )
                print(f"   ❌ {priority_icon} {name}: {result.get('error', 'Type errors found')}")
                if result.get("paths"):
                    print(f"      📁 {', '.join(result['paths'])}")
            print()

        # SotA Assessment
        print("🏆 SotA ASSESSMENT:")

        high_priority_success = sum(1 for _, success in by_priority["HIGH"] if success)
        high_priority_total = len(by_priority["HIGH"])

        if high_priority_success == high_priority_total and success_rate >= 80:
            print("   🏆 EXCELLENT: Core components are type-safe!")
            print("   🚀 Ready for production deployment")
        elif high_priority_success >= high_priority_total - 1 and success_rate >= 60:
            print("   ✅ GOOD: Most critical components are type-safe")
            print("   🔧 Minor fixes needed for full SotA compliance")
        elif high_priority_success >= high_priority_total // 2:
            print("   ⚠️  DEVELOPING: Core components partially type-safe")
            print("   💡 Focus on HIGH priority components first")
        else:
            print("   🔧 WORK IN PROGRESS: Significant type safety issues")
            print("   🎯 Address HIGH priority components urgently")

        print()
        print("🎯 SotA RECOMMENDATIONS:")

        if failed:
            high_failed = [name for name, result in failed.items() if result["priority"] == "HIGH"]
            if high_failed:
                print(f"   🔥 URGENT: Fix HIGH priority components: {', '.join(high_failed)}")

            medium_failed = [
                name for name, result in failed.items() if result["priority"] == "MEDIUM"
            ]
            if medium_failed:
                print(f"   ⚡ IMPORTANT: Address MEDIUM priority: {', '.join(medium_failed)}")

            low_failed = [name for name, result in failed.items() if result["priority"] == "LOW"]
            if low_failed:
                print(f"   💡 NICE TO HAVE: Fix LOW priority: {', '.join(low_failed)}")

        print("   📚 Use 'ty check <path>' for detailed error analysis")
        print("   🔧 Configure overrides in pyproject.toml for specific rules")
        print("   🚀 All new code should pass Ty checks by default")

        print()
        print("🔗 ASTRAL TY DOCUMENTATION:")
        print("   https://github.com/astral-sh/ty")

        return success_rate >= 60  # Consider 60% as acceptable baseline


def main():
    """Main entry point"""
    checker = CodebaseTyChecker()
    success = checker.check_entire_codebase()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
