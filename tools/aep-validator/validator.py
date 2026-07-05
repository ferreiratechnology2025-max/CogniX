#!/usr/bin/env python3
"""
AEP Validator - Validate AEP resources and state
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


VALID_TYPES = ['project', 'status', 'skill', 'adr', 'incident', 'rule', 'template']
VALID_STATUS = ['draft', 'review', 'active', 'deprecated', 'archived']


def validate_resource(file_path: str) -> Tuple[bool, List[str], List[str]]:
    """Validate an AEP resource file"""
    errors = []
    warnings = []

    if not os.path.exists(file_path):
        return False, [f"File not found: {file_path}"], []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    match = re.search(r'^---\n([\s\S]*?)\n---', content)
    if not match:
        return False, ["No frontmatter found"], []

    frontmatter = match.group(1)
    parsed = {}
    for line in frontmatter.split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            parsed[key.strip()] = value.strip()

    # Validate type
    if 'type' not in parsed:
        errors.append("Missing required field: type")
    elif parsed['type'] not in VALID_TYPES:
        errors.append(f"Invalid type: {parsed['type']}")

    # Validate id
    if 'id' not in parsed:
        errors.append("Missing required field: id")
    elif not re.match(r'^[a-z][a-z0-9-]*$', parsed['id']):
        errors.append(f"Invalid id format: {parsed['id']}")

    # Validate version
    if 'version' not in parsed:
        errors.append("Missing required field: version")
    elif not re.match(r'^\d+\.\d+\.\d+$', parsed['version']):
        errors.append(f"Invalid version: {parsed['version']}")

    # Validate status
    if 'status' not in parsed:
        errors.append("Missing required field: status")
    elif parsed['status'] not in VALID_STATUS:
        errors.append(f"Invalid status: {parsed['status']}")

    return len(errors) == 0, errors, warnings


def validate_state(file_path: str) -> Tuple[bool, List[str], List[str]]:
    """Validate an AEP state file"""
    errors = []
    warnings = []

    if not os.path.exists(file_path):
        return False, [f"File not found: {file_path}"], []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for registers
    registers = re.findall(r'^R([0-7])\s*\[', content, re.MULTILINE)
    required = [str(i) for i in range(8)]

    for reg in required:
        if reg not in registers:
            warnings.append(f"Register R{reg} not found")

    return len(errors) == 0, errors, warnings


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AEP Validator")
    parser.add_argument('path', help='File or directory to validate')
    parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args()
    path = Path(args.path)

    if path.is_file():
        if 'STATE' in path.name.upper():
            valid, errors, warnings = validate_state(str(path))
        else:
            valid, errors, warnings = validate_resource(str(path))
        
        print(f"{'PASS' if valid else 'FAIL'}: {path.name}")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN: {w}")
    elif path.is_dir():
        for file in path.glob("*.md"):
            valid, errors, warnings = validate_resource(str(file))
            print(f"{'PASS' if valid else 'FAIL'}: {file.name}")
            if args.verbose:
                for e in errors:
                    print(f"  ERROR: {e}")
    else:
        print(f"Path not found: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()