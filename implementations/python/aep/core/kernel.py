"""
AEP Kernel - Core execution engine
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from .state import StateManager, State
from .resource import ResourceManager


class AEPKernel:
    """AEP Kernel implementation with 6 opcodes"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.state_manager = StateManager(base_path)
        self.resource_manager = ResourceManager(base_path)
        self.loaded_resources = {}
        self.session_id = None
        
    def boot(self) -> Dict[str, Any]:
        """
        BOOT opcode - Initialize the system
        """
        print("🔧 BOOT: Initializing AEP system...")
        
        # Load state
        state = self.state_manager.load_state()
        
        # Set session
        self.session_id = datetime.now().strftime("%Y-%m-%d-%H-%M")
        state.set_register("R0", self.session_id)
        
        # Load program
        program = self.state_manager.load_program()
        
        return {
            "status": "OK",
            "session": self.session_id,
            "state": state.get_all_registers(),
            "program": program
        }
    
    def load(self, resource_id: str, verbose: bool = False) -> Dict[str, Any]:
        """
        LOAD opcode - Load a Resource by ID
        """
        if verbose:
            print(f"📂 LOAD: Loading resource '{resource_id}'...")
        
        # Load resource
        resource = self.resource_manager.load_resource(resource_id)
        if not resource:
            return {
                "status": "FAIL",
                "error": f"Resource '{resource_id}' not found"
            }
        
        # Load dependencies
        dependencies = resource.get("depends", [])
        for dep_id in dependencies:
            dep = self.resource_manager.load_resource(dep_id)
            if not dep:
                return {
                    "status": "FAIL",
                    "error": f"Dependency '{dep_id}' not found for '{resource_id}'"
                }
            self.loaded_resources[dep_id] = dep
        
        self.loaded_resources[resource_id] = resource
        
        return {
            "status": "OK",
            "resource": resource_id,
            "dependencies": dependencies,
            "loaded_count": len(self.loaded_resources)
        }
    
    def validate(self, resource_id: str, verbose: bool = False) -> Dict[str, Any]:
        """
        VALIDATE opcode - Validate Resource structure
        """
        if verbose:
            print(f"🔍 VALIDATE: Validating resource '{resource_id}'...")
        
        # Load resource if not loaded
        if resource_id not in self.loaded_resources:
            result = self.load(resource_id)
            if result["status"] == "FAIL":
                return result
        
        resource = self.loaded_resources[resource_id]
        validation_result = self.resource_manager.validate_resource(resource)
        
        if validation_result["passed"]:
            if verbose:
                print(f"  ✅ Resource '{resource_id}' is valid")
            return {"status": "OK", "resource": resource_id}
        else:
            if verbose:
                print(f"  ❌ Resource '{resource_id}' is invalid: {validation_result['errors']}")
            return {
                "status": "FAIL",
                "resource": resource_id,
                "errors": validation_result["errors"]
            }
    
    def exec(self, verbose: bool = False) -> Dict[str, Any]:
        """
        EXEC opcode - Execute the current task
        """
        if verbose:
            print("⚡ EXEC: Executing current task...")
        
        # Read R2 [NEXT_ACT]
        state = self.state_manager.load_state()
        next_act = state.get_register("R2")
        
        if not next_act:
            return {
                "status": "FAIL",
                "error": "No task defined in R2 [NEXT_ACT]"
            }
        
        if verbose:
            print(f"  📋 Task: {next_act}")
        
        # Execute task (simulated)
        state.set_register("R1", f"Executed: {next_act}")
        state.set_register("R7", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        
        self.state_manager.save_state(state)
        
        return {
            "status": "OK",
            "task": next_act,
            "result": "Task executed successfully"
        }
    
    def commit(self, modified_files: List[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """
        COMMIT opcode - Persist changes and classify new knowledge
        """
        if verbose:
            print("💾 COMMIT: Persisting changes...")
        
        state = self.state_manager.load_state()
        
        # Update registers
        if modified_files:
            # R3 should be delta only
            state.set_register("R3", ", ".join(modified_files))
            if verbose:
                print(f"  📝 Modified: {', '.join(modified_files)}")
        
        state.set_register("R7", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        
        # Save state
        self.state_manager.save_state(state)
        
        return {
            "status": "OK",
            "state": state.get_all_registers()
        }
    
    def exit(self, verbose: bool = False) -> Dict[str, Any]:
        """
        EXIT opcode - End session
        """
        if verbose:
            print("🚪 EXIT: Ending session...")
        
        state = self.state_manager.load_state()
        state.set_register("R6", "OK")
        state.set_register("R7", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        
        self.state_manager.save_state(state)
        
        return {
            "status": "OK",
            "session": self.session_id,
            "timestamp": state.get_register("R7")
        }
    
    def run_program(self, program_flow: List[str], verbose: bool = False) -> Dict[str, Any]:
        """
        Run a program flow
        """
        results = {}
        
        for opcode in program_flow:
            if opcode == "BOOT":
                results["BOOT"] = self.boot()
            elif opcode.startswith("LOAD"):
                resource_id = opcode.split(" ")[1] if len(opcode.split(" ")) > 1 else None
                if resource_id:
                    result = self.load(resource_id, verbose)
                    results["LOAD"] = result
                else:
                    results["LOAD"] = {"status": "FAIL", "error": "No resource ID provided"}
            elif opcode.startswith("VALIDATE"):
                resource_id = opcode.split(" ")[1] if len(opcode.split(" ")) > 1 else None
                if resource_id:
                    result = self.validate(resource_id, verbose)
                    results["VALIDATE"] = result
                else:
                    results["VALIDATE"] = {"status": "FAIL", "error": "No resource ID provided"}
            elif opcode == "EXEC":
                results["EXEC"] = self.exec(verbose)
            elif opcode == "COMMIT":
                results["COMMIT"] = self.commit(verbose=verbose)
            elif opcode == "EXIT":
                results["EXIT"] = self.exit(verbose)
            else:
                results[opcode] = {"status": "FAIL", "error": f"Unknown opcode: {opcode}"}
            
            # Stop on failure
            if results.get(opcode, {}).get("status") == "FAIL":
                break
        
        return results