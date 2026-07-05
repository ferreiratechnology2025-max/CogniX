#!/usr/bin/env python3
"""
AEP SQLite CLI
"""

import sys
import os
import argparse
import json
from pathlib import Path

from .kernel import AEPKernelSQLite


def main():
    parser = argparse.ArgumentParser(
        description="AEP v1.0.0 - SQLite Implementation"
    )
    
    parser.add_argument(
        '--db',
        help='Path to SQLite database file',
        default='aep.db'
    )
    
    parser.add_argument(
        '--init',
        help='Initialize database schema',
        action='store_true'
    )
    
    parser.add_argument(
        '--program',
        help='Run the default program',
        action='store_true'
    )
    
    parser.add_argument(
        '--list',
        help='List all resources',
        action='store_true'
    )
    
    parser.add_argument(
        '--add',
        help='Add a resource from JSON file',
        type=str
    )
    
    parser.add_argument(
        '--verbose',
        help='Show detailed output',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    kernel = AEPKernelSQLite(args.db)
    
    if args.init:
        print("✅ Database initialized")
        return 0
    
    if args.list:
        resources = kernel.resource_manager.list_resources()
        print("Resources in SQLite:")
        for r in resources:
            deps = kernel.resource_manager.get_dependencies(r['id'])
            print(f"  {r['id']} ({r['type']}) v{r['version']} -> {deps}")
        return 0
    
    if args.add:
        with open(args.add, 'r') as f:
            data = json.load(f)
        resource = kernel.resource_manager.add_resource(data)
        print(f"✅ Added resource: {resource['id']}")
        return 0
    
    if args.program:
        program = ["BOOT", "LOAD project-cognix", "VALIDATE project-cognix", "EXEC", "COMMIT", "EXIT"]
        results = kernel.run_program(program, args.verbose)
        print(json.dumps(results, indent=2, default=str))
        return 0
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())