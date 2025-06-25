#!/usr/bin/env python3
"""
Simple test runner for PLua
"""

import sys
import subprocess
import argparse


def run_tests(args):
    """Run pytest with the given arguments"""
    cmd = ["pytest"] + args
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest first:")
        print("  pip install pytest pytest-asyncio pytest-cov")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run PLua tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage")
    parser.add_argument("--fast", action="store_true", help="Run only fast tests (exclude slow)")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--file", "-f", help="Run specific test file")
    parser.add_argument("--function", "-k", help="Run tests matching pattern")
    parser.add_argument("--pdb", action="store_true", help="Drop into debugger on failures")
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = []
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.coverage:
        pytest_args.extend(["--cov=plua", "--cov=extensions", "--cov-report=term-missing"])
    
    if args.fast:
        pytest_args.append("-m")
        pytest_args.append("not slow")
    
    if args.unit:
        pytest_args.append("-m")
        pytest_args.append("unit")
    
    if args.integration:
        pytest_args.append("-m")
        pytest_args.append("integration")
    
    if args.file:
        pytest_args.append(args.file)
    
    if args.function:
        pytest_args.append("-k")
        pytest_args.append(args.function)
    
    if args.pdb:
        pytest_args.append("--pdb")
    
    # Run tests
    return run_tests(pytest_args)


if __name__ == "__main__":
    sys.exit(main()) 