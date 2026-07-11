#!/usr/bin/env python3
"""
AEP SQLite CLI
"""

import sys
import os
import json
import argparse
from pathlib import Path

from .kernel import AEPKernelSQLite


def main():
    # Ensure UTF-8 stdout/stderr so opcode logs (which include Unicode glyphs)
    # do not crash on legacy code pages (e.g. cp1252 on Windows).
    for stream in (sys.stdout, sys.stderr):
        if getattr(stream, "encoding", None) and stream.encoding.lower() != "utf-8":
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, ValueError):
                pass

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
        help='Run the default program (or a custom JSON program list)',
        nargs='?',
        const='default',
        default=None
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
        if args.program == 'default':
            program = ["BOOT", "LOAD project-cognix", "VALIDATE project-cognix",
                       "EXEC", "COMMIT", "EXIT"]
            results = kernel.run_program(program, args.verbose)
            print(json.dumps(results, indent=2, default=str))
            # Default program: preserve legacy return code (0 always)
            return 0
        else:
            try:
                program = json.loads(args.program)
                if not isinstance(program, list):
                    print("Error: --program value must be a JSON array of opcodes")
                    return 1
            except json.JSONDecodeError:
                print(f"Error: invalid JSON for --program: {args.program}")
                return 1

            results = kernel.run_program(program, args.verbose)
            print(json.dumps(results, indent=2, default=str))
            exit_code = 0
            for key, val in results.items():
                if isinstance(val, dict) and val.get("status") == "FAIL":
                    exit_code = 1
                    break
            return exit_code

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
