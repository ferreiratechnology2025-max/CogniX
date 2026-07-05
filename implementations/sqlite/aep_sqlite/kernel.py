"""
AEP SQLite Kernel - Implementation using SQLite storage
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from .database import Database
from .resource import ResourceManager
from .state import StateManager


class AEPKernelSQLite:
    """AEP Kernel with SQLite backend"""
    
    def __init__(self, db_path: str = "aep.db"):
        self.db = Database(db_path)
        self.resource_manager = ResourceManager(self.db)
        self.state_manager = StateManager(self.db)
        self.loaded_resources = {}
        self.session_id = None
        
        # Initialize database
        self.db.initialize()
    
    def boot(self, verbose: bool = False) -> Dict[str, Any]:
        """BOOT opcode"""
        if verbose:
            print("🔧 BOOT: Initializing AEP system with SQLite...")
        
        # Set session
        self.session_id = datetime.now().strftime("%Y-%m-%d-%H-%M")
        
        # Load or create state
        state = self.state_manager.get_state()
        state['r0_session'] = self.session_id
        state['updated_at'] = datetime.now().isoformat()
        self.state_manager.save_state(state)
        
        return {
            "status": "OK",
            "session": self.session_id,
            "state": state
        }
    
    def load(self, resource_id: str, verbose: bool = False) -> Dict[str, Any]:
        """LOAD opcode"""
        if verbose:
            print(f"📂 LOAD: Loading resource '{resource_id}' from SQLite...")
        
        # Load resource from database
        resource = self.resource_manager.get_resource(resource_id)
        if not resource:
            return {
                "status": "FAIL",
                "error": f"Resource '{resource_id}' not found"
            }
        
        # Load dependencies
        dependencies = self.resource_manager.get_dependencies(resource_id)
        for dep_id in dependencies:
            dep = self.resource_manager.get_resource(dep_id)
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
        """VALIDATE opcode"""
        if verbose:
            print(f"🔍 VALIDATE: Validating resource '{resource_id}' in SQLite...")
        
        # Load if not loaded
        if resource_id not in self.loaded_resources:
            result = self.load(resource_id)
            if result["status"] == "FAIL":
                return result
        
        resource = self.loaded_resources[resource_id]
        validation_result = self.resource_manager.validate_resource(resource)
        
        return {
            "status": "OK" if validation_result["passed"] else "FAIL",
            "resource": resource_id,
            "valid": validation_result["passed"],
            "errors": validation_result.get("errors", [])
        }
    
    def exec(self, verbose: bool = False) -> Dict[str, Any]:
        """EXEC opcode"""
        if verbose:
            print("⚡ EXEC: Executing current task...")
        
        state = self.state_manager.get_state()
        next_act = state.get('r2_next_act')
        
        if not next_act:
            return {
                "status": "FAIL",
                "error": "No task defined in R2 [NEXT_ACT]"
            }
        
        if verbose:
            print(f"  📋 Task: {next_act}")
        
        # Execute task (simulated)
        state['r1_last_act'] = f"Executed: {next_act}"
        state['r7_timestamp'] = datetime.now().isoformat()
        self.state_manager.save_state(state)
        
        return {
            "status": "OK",
            "task": next_act,
            "result": "Task executed successfully"
        }
    
    def commit(self, modified_files: List[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """COMMIT opcode"""
        if verbose:
            print("💾 COMMIT: Persisting changes to SQLite...")
        
        state = self.state_manager.get_state()
        
        # Update R3 (delta only)
        if modified_files:
            state['r3_modified'] = ", ".join(modified_files)
            if verbose:
                print(f"  📝 Modified: {', '.join(modified_files)}")
        
        state['r7_timestamp'] = datetime.now().isoformat()
        self.state_manager.save_state(state)
        
        return {
            "status": "OK",
            "state": state
        }
    
    def exit(self, verbose: bool = False) -> Dict[str, Any]:
        """EXIT opcode"""
        if verbose:
            print("🚪 EXIT: Ending session...")
        
        state = self.state_manager.get_state()
        state['r6_health'] = 'OK'
        state['r7_timestamp'] = datetime.now().isoformat()
        state['last_result'] = 'OK'
        self.state_manager.save_state(state)
        
        return {
            "status": "OK",
            "session": self.session_id,
            "timestamp": state['r7_timestamp']
        }
    
    def run_program(self, program: List[str], verbose: bool = False) -> Dict[str, Any]:
        """Run a program flow"""
        results = {}
        
        for opcode in program:
            if opcode == "BOOT":
                results["BOOT"] = self.boot(verbose)
            elif opcode.startswith("LOAD "):
                resource_id = opcode.split(" ", 1)[1]
                results["LOAD"] = self.load(resource_id, verbose)
            elif opcode.startswith("VALIDATE "):
                resource_id = opcode.split(" ", 1)[1]
                results["VALIDATE"] = self.validate(resource_id, verbose)
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
    
    def close(self):
        """Close database connection"""
        self.db.close()