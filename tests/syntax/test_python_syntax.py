#!/usr/bin/env python3
"""Tests for Python syntax validation.

Checks that all Python files in the project have valid syntax.
"""

import sys
import os
import py_compile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


def find_python_files(root_dir):
    """Find all Python files in the given directory and subdirectories.
    
    Args:
        root_dir: Root directory to search for Python files.
        
    Returns:
        List of Path objects for all .py files found.
    """
    root_path = Path(root_dir)
    return list(root_path.rglob('*.py'))


def test_python_syntax():
    """Test: All Python files have valid syntax."""
    print("Testing: Python Syntax Validation...")
    
    # Get project root (two directories up from tests/syntax/)
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / 'src'
    tests_dir = project_root / 'tests'
    
    # Find all Python files in src and tests
    src_files = find_python_files(src_dir)
    test_files = find_python_files(tests_dir)
    all_files = src_files + test_files
    
    print(f"  → Found {len(src_files)} files in src/")
    print(f"  → Found {len(test_files)} files in tests/")
    print(f"  → Checking {len(all_files)} total Python files...")
    print()
    
    errors = []
    
    for python_file in all_files:
        try:
            py_compile.compile(str(python_file), doraise=True)
            print(f"  ✓ {python_file.relative_to(project_root)}")
        except py_compile.PyCompileError as e:
            error_msg = f"{python_file.relative_to(project_root)}: {e.msg}"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")
    
    print()
    
    if errors:
        print(f"   ❌ FAILED: {len(errors)} file(s) with syntax errors")
        for error in errors:
            print(f"      - {error}")
        return False
    else:
        print(f"   ✅ PASSED: All {len(all_files)} files have valid syntax")
        return True


def test_specific_files():
    """Test: Specific critical files have valid syntax."""
    print("Testing: Critical Files Syntax...")
    
    project_root = Path(__file__).parent.parent.parent
    
    critical_files = [
        project_root / 'src' / 'helper' / 'cli_print_utility.py',
        project_root / 'src' / 'core' / 'kernel.py',
        project_root / 'src' / 'package_managers' / 'dnf.py',
        project_root / 'src' / 'helper' / 'runner.py',
        project_root / 'src' / 'helper' / 'sudo_keepalive.py',
    ]
    
    errors = []
    
    for python_file in critical_files:
        if not python_file.exists():
            errors.append(f"{python_file.name}: File not found")
            print(f"  ✗ {python_file.name}: File not found")
            continue
            
        try:
            py_compile.compile(str(python_file), doraise=True)
            print(f"  ✓ {python_file.name}")
        except py_compile.PyCompileError as e:
            errors.append(f"{python_file.name}: {e.msg}")
            print(f"  ✗ {python_file.name}: {e.msg}")
    
    print()
    
    if errors:
        print(f"   ❌ FAILED: {len(errors)} critical file(s) with errors")
        return False
    else:
        print(f"   ✅ PASSED: All {len(critical_files)} critical files are valid")
        return True


def test_no_common_syntax_errors():
    """Test: Check for common Python syntax issues."""
    print("Testing: Common Syntax Error Patterns...")
    
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / 'src'
    
    # Find all Python files
    all_files = find_python_files(src_dir)
    
    issues = []
    
    for python_file in all_files:
        with open(python_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
            
            # Check for common issues
            for i, line in enumerate(lines, 1):
                # Check for mixing tabs and spaces (simplified check)
                if '\t' in line and '    ' in line:
                    issues.append(f"{python_file.name}:{i}: Mixed tabs and spaces")
                
                # Check for common typos
                if 'improt ' in line or 'form ' in line:
                    issues.append(f"{python_file.name}:{i}: Likely import typo")
    
    if issues:
        print(f"   ⚠️  WARNING: {len(issues)} potential issue(s) found")
        for issue in issues[:5]:  # Show first 5
            print(f"      - {issue}")
        return True  # Don't fail on warnings
    else:
        print("   ✅ PASSED: No common syntax error patterns found")
        return True


def main():
    """Run all syntax validation tests."""
    print("=" * 60)
    print("Python Syntax Validation Tests")
    print("=" * 60)
    print()

    results = []
    results.append(("Python Syntax Validation", test_python_syntax()))
    print()
    results.append(("Critical Files Syntax", test_specific_files()))
    print()
    results.append(("Common Syntax Errors", test_no_common_syntax_errors()))
    print()

    # Print summary
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Results: {passed}/{total} passed")
    print("=" * 60)

    return 0 if all(result for _, result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
