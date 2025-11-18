"""
Test runner for emsify v1.2.0 enhancements
Run all tests and generate report
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_all_tests():
    """Run all test suites"""
    import pytest
    
    test_files = [
        "tests/test_security_fixes.py",
        "tests/test_ems_automation_v12.py"
    ]
    
    print("=" * 70)
    print("EMSIFY v1.2.0 - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    
    # Run with verbose output and coverage
    args = [
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "-x",  # Stop on first failure
        "--color=yes"  # Colored output
    ] + test_files
    
    result = pytest.main(args)
    
    print()
    print("=" * 70)
    if result == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    return result


def run_security_tests_only():
    """Run only security-related tests"""
    import pytest
    
    print("=" * 70)
    print("SECURITY TESTS ONLY")
    print("=" * 70)
    
    result = pytest.main([
        "tests/test_security_fixes.py",
        "-v",
        "--tb=short"
    ])
    
    return result


def run_architecture_tests_only():
    """Run only architecture-related tests"""
    import pytest
    
    print("=" * 70)
    print("ARCHITECTURE TESTS ONLY")
    print("=" * 70)
    
    result = pytest.main([
        "tests/test_ems_automation_v12.py",
        "-v",
        "--tb=short"
    ])
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run emsify tests")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--architecture", action="store_true", help="Run architecture tests only")
    
    args = parser.parse_args()
    
    if args.security:
        sys.exit(run_security_tests_only())
    elif args.architecture:
        sys.exit(run_architecture_tests_only())
    else:
        sys.exit(run_all_tests())
