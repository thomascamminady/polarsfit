#!/usr/bin/env python3
"""
Test runner for polarsfit with comprehensive reporting.
"""

import subprocess
import sys
from pathlib import Path


def run_test_suite():
    """Run the complete polarsfit test suite with detailed reporting."""
    print("🧪 Running polarsfit comprehensive test suite")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Tests directory not found. Run from project root.")
        return False

    # List available test files
    test_files = list(Path("tests").glob("test_*.py"))
    print(f"📁 Found {len(test_files)} test files:")
    for test_file in sorted(test_files):
        print(f"   • {test_file}")

    print("\n🏃‍♂️ Running tests...")
    print("-" * 60)

    # Run pytest with comprehensive options
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--strict-markers",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Print results
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        # Analyze results
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)

            # Extract test count from output
            output_lines = result.stdout.split("\n")
            for line in output_lines:
                if "passed" in line and (
                    "warning" in line
                    or "failed" in line
                    or line.strip().endswith("passed")
                ):
                    print(f"📊 Result: {line.strip()}")
                    break

            return True
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED")
            print("=" * 60)
            return False

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main entry point."""
    success = run_test_suite()

    if success:
        print("\n🎉 Test suite completed successfully!")
        print("🔧 All FIT parsing functionality is working correctly")
        print("📊 FIT vs CSV comparison validates data accuracy")
    else:
        print("\n⚠️  Some tests failed - see output above for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
