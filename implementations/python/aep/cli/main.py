#!/usr/bin/env python3
"""
AEP CLI - Command Line Interface for AEP Python Implementation
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aep.core.kernel import AEPKernel


def main():
    parser = argparse.ArgumentParser(
        description="AEP (Agent Execution Protocol) v1.0.0 - Python Implementation"
    )
    
    parser.add_argument(
        '--state',
        help='Path to state file (for validation)',
        type=str
    )
    
    parser.add_argument(
        '--resource',
        help='Path to resource file (for validation)',
        type=str
    )
    
    parser.add_argument(
        '--run',
        help='Run a command (boot, load, validate, exec, commit, exit)',
        type=str,
        choices=['boot', 'load', 'validate', 'exec', 'commit', 'exit']
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
        '--verbose',
        help='Show detailed output',
        action='store_true'
    )
    
    parser.add_argument(
        '--base',
        help='Base path to KOS installation',
        default='.'
    )
    
    args = parser.parse_args()
    
    kernel = AEPKernel(args.base)
    
    if args.program:
        # Run default program
        program = ["BOOT", "LOAD project-cognix", "VALIDATE project-cognix", "EXEC", "COMMIT", "EXIT"]
        results = kernel.run_program(program, args.verbose)
        print(json.dumps(results, indent=2, default=str))
        return 0
    
    if args.list:
        resources = kernel.resource_manager.list_resources()
        print("Available resources:")
        for r in resources:
            print(f"  - {r}")
        return 0
    
    if args.run:
        if args.run == 'boot':
            result = kernel.boot()
            print(json.dumps(result, indent=2, default=str))
        elif args.run == 'load':
            print("Load requires a resource ID. Use --resource <id>")
            return 1
        elif args.run == 'validate':
            if not args.resource:
                print("Error: --resource required for validation")
                return 1
            result = kernel.validate(args.resource, args.verbose)
            print(json.dumps(result, indent=2, default=str))
        elif args.run == 'exec':
            result = kernel.exec(args.verbose)
            print(json.dumps(result, indent=2, default=str))
        elif args.run == 'commit':
            result = kernel.commit(verbose=args.verbose)
            print(json.dumps(result, indent=2, default=str))
        elif args.run == 'exit':
            result = kernel.exit(args.verbose)
            print(json.dumps(result, indent=2, default=str))
        return 0
    
    if args.resource:
        # Validate resource
        resource_id = os.path.splitext(os.path.basename(args.resource))[0]
        result = kernel.validate(resource_id, args.verbose)
        print(json.dumps(result, indent=2, default=str))
        return 0
    
    if args.state:
        # Show state
        from aep.core.state import StateManager
        manager = StateManager(args.base)
        state = manager.load_state()
        print("Current state:")
        for reg, value in state.get_all_registers().items():
            print(f"  {reg}: {value}")
        return 0
    
    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())