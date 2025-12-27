#!/usr/bin/env python3
"""Test runner for Fedora Update Control Kit.

This script discovers and runs all tests in the tests/ directory.
It organizes tests by category and provides a comprehensive summary.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Tuple


class TestRunner:
    """Test runner that executes all test files and collects results."""
    
    def __init__(self, project_root: Path):
        """Initialize test runner.
        
        Args:
            project_root: Root directory of the project.
        """
        self.project_root = project_root
        self.tests_dir = project_root / 'tests'
        self.results: List[Tuple[str, str, bool]] = []  # (category, name, passed)
    
    def find_test_files(self) -> List[Tuple[str, Path]]:
        """Find all test files organized by category.
        
        Returns:
            List of tuples (category, file_path) for all test files.
        """
        test_files = []
        
        # Find all test_*.py files in subdirectories
        for test_file in self.tests_dir.rglob('test_*.py'):
            # Get category from parent directory
            category = test_file.parent.name
            test_files.append((category, test_file))
        
        # Sort by category, then by filename
        test_files.sort(key=lambda x: (x[0], x[1].name))
        
        return test_files
    
    def run_test_file(self, category: str, test_file: Path) -> bool:
        """Run a single test file.
        
        Args:
            category: Test category name.
            test_file: Path to the test file.
            
        Returns:
            True if all tests passed, False otherwise.
        """
        test_name = test_file.stem.replace('test_', '').replace('_', ' ').title()
        
        print(f"\n{'=' * 60}")
        print(f"Running: {category}/{test_file.name}")
        print(f"{'=' * 60}")
        
        try:
            # Run the test file
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            passed = result.returncode == 0
            self.results.append((category, test_name, passed))
            
            return passed
            
        except Exception as e:
            print(f"❌ Error running test: {e}")
            self.results.append((category, test_name, False))
            return False
    
    def print_summary(self):
        """Print a comprehensive summary of all test results."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        # Group results by category
        categories = {}
        for category, name, passed in self.results:
            if category not in categories:
                categories[category] = []
            categories[category].append((name, passed))
        
        # Print results by category
        for category in sorted(categories.keys()):
            print(f"\n{category.upper()}:")
            for name, passed in categories[category]:
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"  {status}: {name}")
        
        # Overall statistics
        total = len(self.results)
        passed = sum(1 for _, _, p in self.results if p)
        failed = total - passed
        
        print("\n" + "=" * 60)
        print(f"Total: {total} test suites")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print("=" * 60)
        
        if failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {failed} test suite(s) failed!")
    
    def run_all(self) -> int:
        """Run all tests and return exit code.
        
        Returns:
            0 if all tests passed, 1 otherwise.
        """
        print("=" * 60)
        print("FEDORA UPDATE CONTROL KIT - TEST SUITE")
        print("=" * 60)
        
        test_files = self.find_test_files()
        
        if not test_files:
            print("⚠️  No test files found!")
            return 1
        
        print(f"\nFound {len(test_files)} test file(s)")
        
        # Run all tests
        all_passed = True
        for category, test_file in test_files:
            passed = self.run_test_file(category, test_file)
            if not passed:
                all_passed = False
        
        # Print summary
        self.print_summary()
        
        return 0 if all_passed else 1


def main():
    """Main entry point for test runner."""
    # Get project root (parent of tests directory)
    project_root = Path(__file__).parent.parent
    
    # Create and run test runner
    runner = TestRunner(project_root)
    exit_code = runner.run_all()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
