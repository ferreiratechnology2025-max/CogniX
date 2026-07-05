#!/usr/bin/env python3
"""
AEP Validator CLI
"""

from validator import validate_resource, validate_state
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: aep-validator <file>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    if 'STATE' in file_path.upper():
        valid, errors, warnings = validate_state(file_path)
    else:
        valid, errors, warnings = validate_resource(file_path)

    print(f"Result: {'PASS' if valid else 'FAIL'}")
    for e in errors:
        print(f"  ERROR: {e}")
    for w in warnings:
        print(f"  WARN: {w}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()