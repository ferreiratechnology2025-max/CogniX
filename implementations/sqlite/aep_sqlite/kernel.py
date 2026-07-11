"""
AEP SQLite Kernel v1.1.0 - Watchdog AEP-0008
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from .database import Database
from .resource import ResourceManager
from .state import StateManager


class AEPKernelSQLite:
    """AEP Kernel with SQLite backend and AEP-0008 Watchdog"""

    def __init__(self, db_path: str = "aep.db"):
        self.db = Database(db_path)
        self.resource_manager = ResourceManager(self.db)
        self.state_manager = StateManager(self.db)
        self.loaded_resources = {}
        self.session_id = None
        self.yield_history = []
        self.max_watchdog_cycles = 10

        self.db.initialize()

    def boot(self, verbose: bool = False) -> Dict[str, Any]:
        """BOOT opcode"""
        if verbose:
            print("🔧 BOOT: Initializing AEP system with SQLite...")

        self.session_id = datetime.now().strftime("%Y-%m-%d-%H-%M")

        state = self.state_manager.get_state()
        state['r0_session'] = self.session_id
        state['updated_at'] = datetime.now().isoformat()

        watchdog_raw = state.get('internal_last_action')
        if watchdog_raw is None:
            state['internal_last_action'] = "5"
        else:
            try:
                int(watchdog_raw)
            except (ValueError, TypeError):
                state['internal_last_action'] = "5"

        self.state_manager.save_state(state)

        return {
            "status": "OK",
            "session": self.session_id,
            "state": state
        }

    def _read_r1(self, state: Dict[str, Any]) -> int:
        raw = state.get('internal_last_action')
        if raw is None:
            return 0
        try:
            return int(raw)
        except (ValueError, TypeError):
            return 0

    def _trigger_exhaustion(self, r1_before: int, opcode: str = "EXEC",
                            verbose: bool = False) -> Dict[str, Any]:
        state = self.state_manager.get_state()

        r4_error = json.dumps({
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "error_code": "AEP_ERR_WATCHDOG_EXHAUSTION",
            "trace": f"Watchdog exhausted at {opcode}, R1 was {r1_before}",
            "watchdog_at_failure": 0
        })

        state['r4_blockers'] = r4_error
        state['r6_health'] = 'FAIL'
        state['r7_timestamp'] = 'EXIT_1_WATCHDOG_TIMEOUT'
        self.state_manager.save_state(state)

        self.db.rollback()

        return {
            "status": "FAIL",
            "error": f"Watchdog exhausted: R1 reached 0 before {opcode}",
            "error_code": "AEP_ERR_WATCHDOG_EXHAUSTION",
            "rollback": True,
            "watchdog_remaining": 0,
            "state": state
        }

    def yield_cycles(self, reason: str, requested_cycles: int = 1,
                     verbose: bool = False) -> Dict[str, Any]:
        """YIELD opcode — preventivo, chamado antes do EXEC que zeraria R1"""
        if verbose:
            print(f"🔄 YIELD: Requesting {requested_cycles} cycles...")
            print(f"  📋 Reason: {reason}")

        if requested_cycles > 10:
            return {
                "status": "FAIL",
                "error": "YIELD: requested_cycles exceeds maximum (10)"
            }

        state = self.state_manager.get_state()
        current_watchdog = self._read_r1(state)

        total_cycles = sum(y.get("cycles", 0) for y in self.yield_history) + requested_cycles
        if total_cycles > self.max_watchdog_cycles:
            return {
                "status": "FAIL",
                "error": f"YIELD: Total cycles ({total_cycles}) exceeds global limit ({self.max_watchdog_cycles})"
            }

        new_watchdog = current_watchdog + requested_cycles
        state['internal_last_action'] = str(new_watchdog)
        self.state_manager.save_state(state)

        self.yield_history.append({
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "requested": requested_cycles,
            "approved": requested_cycles,
            "new_watchdog": new_watchdog
        })

        if verbose:
            print(f"  ✅ YIELD approved. Watchdog now: {new_watchdog}")

        return {
            "status": "OK",
            "approved": requested_cycles,
            "new_watchdog": new_watchdog,
            "total_cycles_used": total_cycles + requested_cycles,
            "history": self.yield_history
        }

    def load(self, resource_id: str, verbose: bool = False) -> Dict[str, Any]:
        """LOAD opcode — AEP-0008 §1.1: não decrementa R1"""
        if verbose:
            print(f"📂 LOAD: Loading resource '{resource_id}' from SQLite...")

        resource = self.resource_manager.get_resource(resource_id)
        if not resource:
            return {
                "status": "FAIL",
                "error": f"Resource '{resource_id}' not found"
            }

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
        """VALIDATE opcode — AEP-0008 §1.1: não decrementa R1"""
        if verbose:
            print(f"🔍 VALIDATE: Validating resource '{resource_id}' in SQLite...")

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
        """EXEC opcode — único que decrementa R1.
        Se R1=1, o decremento zera o contador → exaustão imediata.
        Nenhum side effect, a tarefa não é executada.
        """
        if verbose:
            print("⚡ EXEC: Executing current task...")

        state = self.state_manager.get_state()
        watchdog = self._read_r1(state)

        if watchdog <= 0:
            return self._trigger_exhaustion(watchdog, "EXEC", verbose)

        if watchdog == 1:
            state['internal_last_action'] = "0"
            self.state_manager.save_state(state)
            return self._trigger_exhaustion(1, "EXEC", verbose)

        next_act = state.get('r2_next_act')
        if not next_act:
            return {
                "status": "FAIL",
                "error": "No task defined in R2 [NEXT_ACT]"
            }

        if verbose:
            print(f"  📋 Task: {next_act}")

        new_watchdog = watchdog - 1
        state['internal_last_action'] = str(new_watchdog)
        state['r7_timestamp'] = datetime.now().isoformat()
        self.state_manager.save_state(state)

        return {
            "status": "OK",
            "task": next_act,
            "result": "Task executed successfully",
            "watchdog_remaining": new_watchdog
        }

    def commit(self, modified_files: List[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """COMMIT opcode — AEP-0008 §1.1: não decrementa R1"""
        if verbose:
            print("💾 COMMIT: Persisting changes to SQLite...")

        state = self.state_manager.get_state()

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
        """EXIT opcode — AEP-0008 §1.1: não decrementa R1"""
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
        """Executa um programa completo — suporta YIELD preventivo e exaustão imediata"""
        results = {}

        for opcode in program:
            parts = opcode.strip().split()
            command = parts[0] if parts else ""

            if command == "BOOT":
                results["BOOT"] = self.boot(verbose)
            elif command == "YIELD":
                rest = opcode.strip()[5:].strip()
                if rest.startswith("'") or rest.startswith('"'):
                    quote_char = rest[0]
                    end_quote = rest.find(quote_char, 1)
                    reason = rest[1:end_quote].strip() if end_quote > 0 else rest.strip(quote_char)
                    remaining = rest[end_quote+1:].strip() if end_quote > 0 else ""
                    cycles = int(remaining) if remaining.isdigit() else 1
                else:
                    tokens = rest.split()
                    reason = tokens[0] if tokens else "No reason"
                    cycles = int(tokens[1]) if len(tokens) > 1 and tokens[1].isdigit() else 1
                results["YIELD"] = self.yield_cycles(reason, cycles, verbose)
            elif command == "LOAD":
                resource_id = parts[1] if len(parts) > 1 else None
                if resource_id:
                    results["LOAD"] = self.load(resource_id, verbose)
                else:
                    results["LOAD"] = {"status": "FAIL", "error": "No resource ID"}
            elif command == "VALIDATE":
                resource_id = parts[1] if len(parts) > 1 else None
                if resource_id:
                    results["VALIDATE"] = self.validate(resource_id, verbose)
                else:
                    results["VALIDATE"] = {"status": "FAIL", "error": "No resource ID"}
            elif command == "EXEC":
                results["EXEC"] = self.exec(verbose)
            elif command == "COMMIT":
                results["COMMIT"] = self.commit(verbose=verbose)
            elif command == "EXIT":
                results["EXIT"] = self.exit(verbose)
            else:
                results[command] = {"status": "FAIL", "error": f"Unknown opcode: {command}"}

            result = results.get(command, {})
            if result.get("status") == "FAIL" and command != "YIELD":
                if verbose:
                    print(f"❌ Program halted at: {command}")
                break

        return results

    def close(self):
        """Close database connection"""
        self.db.close()
