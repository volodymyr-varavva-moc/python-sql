#!/usr/bin/env python3
"""
Test runner script with coverage reporting
"""
import sys
import subprocess
import os

def run_tests():
    """Run tests with coverage and generate report"""
    print("Running tests with coverage...")
    
    # Make sure test database doesn't exist
    if os.path.exists("test.db"):
        os.remove("test.db")
    
    # Run tests
    result = subprocess.run(
        ["pytest", "--cov=app", "--cov-report=term", "--cov-report=html", "tests/"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Print output
    print(result.stdout)
    
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    # Check for coverage minimum
    if "TOTAL" in result.stdout:
        coverage_line = next((line for line in result.stdout.split('\n') if "TOTAL" in line), None)
        if coverage_line:
            coverage_parts = coverage_line.split()
            coverage_percentage = float(coverage_parts[3].strip('%'))
            
            print(f"Total coverage: {coverage_percentage:.2f}%")
            
            if coverage_percentage < 60:
                print(f"Coverage is below the required 60% minimum ({coverage_percentage:.2f}%)")
                return 1
            else:
                print(f"Coverage meets the required minimum (>= 60%)")
    
    return 0 if result.returncode == 0 else 1

if __name__ == "__main__":
    sys.exit(run_tests())
