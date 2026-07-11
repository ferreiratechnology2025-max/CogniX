"""
AEP Kernel v1.1.0 - Implementação com AEP-0008 (Fault Tolerance)
Conforme AEP-0008 §1.1: R1 decrementa apenas em EXEC.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from .state import StateManager, State
from .resource import ResourceManager


class AEPRuntimeError(Exception):
    """Erro estruturado do runtime AEP"""
    def __init__(self, error_code: str, message: str, watchdog_at_failure: int = 0):
        self.error_code = error_code
        self.message = message
        self.watchdog_at_failure = watchdog_at_failure
        super().__init__(message)


class AEPKernel:
    """AEP Kernel com Watchdog, YIELD e Rollback estruturado"""

    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.state_manager = StateManager(base_path)
        self.resource_manager = ResourceManager(base_path)
        self.loaded_resources = {}
        self.session_id = None
        self.max_watchdog_cycles = 10
        self.yield_history = []

    def boot(self, verbose: bool = False) -> Dict[str, Any]:
        """BOOT opcode - Inicializa o sistema com Watchdog"""
        if verbose:
            print("🔧 BOOT: Initializing AEP system with Fault Tolerance...")

        state = self.state_manager.load_state()

        self.session_id = datetime.now().strftime("%Y-%m-%d-%H-%M")
        state.set_register("R0", self.session_id)

        watchdog_initial = state.get_register("R1") or "5"
        state.set_register("R1", str(watchdog_initial))

        self.yield_history = []

        self.state_manager.save_state(state)

        program = self.state_manager.load_program()

        return {
            "status": "OK",
            "session": self.session_id,
            "watchdog_initial": watchdog_initial,
            "state": state.get_all_registers(),
            "program": program
        }

    def _trigger_exhaustion(self, r1_before: int = 0, opcode: str = "",
                            verbose: bool = False) -> Dict[str, Any]:
        """Trigger an AEP_ERR_WATCHDOG_EXHAUSTION fault with rollback.

        R0, R3, R7 are preserved. R4 gets the structured error.
        """
        state = self.state_manager.load_state()

        r4_error = json.dumps({
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "error_code": "AEP_ERR_WATCHDOG_EXHAUSTION",
            "trace": f"Watchdog exhausted at {opcode or 'EXEC'}, R1 was {r1_before}",
            "watchdog_at_failure": 0
        })
        state.set_register("R4", r4_error)
        state.set_register("R6", "FAIL")
        state.set_register("R7", "EXIT_1_WATCHDOG_TIMEOUT")
        self.state_manager.save_state(state)

        return {
            "status": "FAIL",
            "error": f"Watchdog exhausted: R1 reached 0 before {opcode or 'EXEC'}",
            "error_code": "AEP_ERR_WATCHDOG_EXHAUSTION",
            "rollback": True,
            "watchdog_remaining": 0,
            "state": state.get_all_registers()
        }

    def yield_cycles(self, reason: str, requested_cycles: int = 1, verbose: bool = False) -> Dict[str, Any]:
        """YIELD opcode - Solicita extensão de ciclos do Watchdog.
        Sempre permitido — não verifica R1 (rescue path em R1 == 0).
        """
        if verbose:
            print(f"🔄 YIELD: Requesting {requested_cycles} cycles...")
            print(f"  📋 Reason: {reason}")

        if requested_cycles > 10:
            return {
                "status": "FAIL",
                "error": "YIELD: requested_cycles exceeds maximum (10)"
            }

        state = self.state_manager.load_state()
        current_watchdog = int(state.get_register("R1") or 0)

        total_cycles = sum(y.get("cycles", 0) for y in self.yield_history) + requested_cycles
        if total_cycles > self.max_watchdog_cycles:
            return {
                "status": "FAIL",
                "error": f"YIELD: Total cycles ({total_cycles}) exceeds global limit ({self.max_watchdog_cycles})"
            }

        new_watchdog = current_watchdog + requested_cycles
        state.set_register("R1", str(new_watchdog))
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
        """LOAD opcode - Carrega Resource.
        AEP-0008 §1.1: NÃO decrementa R1. Exaustão bloqueia o opcode.
        """
        if verbose:
            print(f"📂 LOAD: Loading resource '{resource_id}'...")

        state = self.state_manager.load_state()
        watchdog = int(state.get_register("R1") or 0)
        if watchdog <= 0:
            return self._trigger_exhaustion(watchdog, "LOAD", verbose)

        if not self.resource_manager.is_valid_resource_id(resource_id):
            return {
                "status": "FAIL",
                "error": f"Invalid resource id: '{resource_id}'",
                "error_code": "ERR_AEP_0003_E003"
            }

        resource = self.resource_manager.load_resource(resource_id)
        if not resource:
            return {
                "status": "FAIL",
                "error": f"Resource '{resource_id}' not found",
                "error_code": "ERR_AEP_0003_E001"
            }

        dependencies = resource.get("depends", [])
        for dep_id in dependencies:
            dep = self.resource_manager.load_resource(dep_id)
            if not dep:
                return {
                    "status": "FAIL",
                    "error": f"Dependency '{dep_id}' not found for '{resource_id}'",
                    "error_code": "ERR_AEP_0003_E002"
                }
            self.loaded_resources[dep_id] = dep

        self.loaded_resources[resource_id] = resource

        # R1 NOT decremented — only EXEC consumes cycles
        self.state_manager.save_state(state)

        return {
            "status": "OK",
            "resource": resource_id,
            "dependencies": dependencies,
            "loaded_count": len(self.loaded_resources),
            "watchdog_remaining": watchdog
        }

    def validate(self, resource_id: str, verbose: bool = False) -> Dict[str, Any]:
        """VALIDATE opcode - Valida estrutura do Resource.
        AEP-0008 §1.1: NÃO decrementa R1. Exaustão bloqueia o opcode.
        """
        if verbose:
            print(f"🔍 VALIDATE: Validating resource '{resource_id}'...")

        state = self.state_manager.load_state()
        watchdog = int(state.get_register("R1") or 0)
        if watchdog <= 0:
            return self._trigger_exhaustion(watchdog, "VALIDATE", verbose)

        if not self.resource_manager.is_valid_resource_id(resource_id):
            return {
                "status": "FAIL",
                "error": f"Invalid resource id: '{resource_id}'",
                "error_code": "ERR_AEP_0003_E003"
            }

        if resource_id not in self.loaded_resources:
            result = self.load(resource_id)
            if result["status"] == "FAIL":
                return result

        resource = self.loaded_resources[resource_id]
        validation_result = self.resource_manager.validate_resource(resource)

        # R1 NOT decremented — only EXEC consumes cycles
        self.state_manager.save_state(state)

        return {
            "status": "OK" if validation_result["passed"] else "FAIL",
            "resource": resource_id,
            "valid": validation_result["passed"],
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "watchdog_remaining": watchdog
        }

    def exec(self, verbose: bool = False) -> Dict[str, Any]:
        """EXEC opcode - Executa a tarefa atual.
        AEP-0008 §1.1: ÚNICO opcode que decrementa R1.
        Se R1=1, o decremento zera o contador → exaustão imediata.
        O opcode NÃO produz side effects nem executa a tarefa.
        """
        if verbose:
            print("⚡ EXEC: Executing current task...")

        state = self.state_manager.load_state()
        watchdog = int(state.get_register("R1") or 0)

        if watchdog <= 0:
            return self._trigger_exhaustion(watchdog, "EXEC", verbose)

        # Exaustão imediata: consumir o último ciclo aborta este EXEC.
        # Nenhum side effect, a tarefa NÃO é executada.
        if watchdog == 1:
            state.set_register("R1", "0")
            return self._trigger_exhaustion(1, "EXEC", verbose)

        next_act = state.get_register("R2")

        if not next_act:
            return {
                "status": "FAIL",
                "error": "No task defined in R2 [NEXT_ACT]"
            }

        if verbose:
            print(f"  📋 Task: {next_act}")

        new_watchdog = watchdog - 1
        state.set_register("R1", str(new_watchdog))
        state.set_register("R7", datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        self.state_manager.save_state(state)

        return {
            "status": "OK",
            "task": next_act,
            "result": "Task executed successfully",
            "watchdog_remaining": new_watchdog
        }

    def execute_commit(self, modified_files: List[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """COMMIT opcode - Transação ACID com Rollback estruturado.
        AEP-0008 §1.1: NÃO decrementa R1.
        """
        if verbose:
            print("💾 COMMIT: Starting ACID transaction...")

        state = self.state_manager.load_state()
        watchdog = int(state.get_register("R1") or 0)

        stable_snapshot = state.get_register("R3") or "{}"
        if isinstance(stable_snapshot, str):
            try:
                stable_snapshot = json.loads(stable_snapshot)
            except (json.JSONDecodeError, TypeError):
                stable_snapshot = {}

        try:
            # 1. Validação semântica (bouncer)
            if modified_files:
                for file_path in modified_files:
                    resource_id = os.path.splitext(os.path.basename(file_path))[0]
                    resource = self.resource_manager.load_resource(resource_id)
                    if resource:
                        validation = self.resource_manager.validate_resource(resource)
                        if not validation["passed"]:
                            raise AEPRuntimeError(
                                error_code="ERR_AEP_0002_VALIDATION",
                                message=f"Resource '{resource_id}' validation failed: {validation['errors']}"
                            )

            # 2. Persiste no disco
            if modified_files:
                state.set_register("R3", ", ".join(modified_files))

            # 3. Atualiza timestamp e status
            state.set_register("R7", datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
            state.set_register("R6", "OK")

            self.state_manager.save_state(state)

            # 4. Atualiza snapshot estável (R3) para o próximo ciclo
            current_state = state.get_all_registers()
            state.set_register("R3", json.dumps(current_state))

            # Limpa erros se a transação foi bem-sucedida
            state.set_register("R4", None)
            self.state_manager.save_state(state)

            if verbose:
                print("  ✅ Transaction committed successfully")

            return {
                "status": "OK",
                "modified": modified_files or [],
                "watchdog_remaining": watchdog,
                "state": state.get_all_registers()
            }

        except AEPRuntimeError as err:
            if verbose:
                print(f"  ❌ Transaction failed: {err.message}")
                print(f"  🔄 Executing ROLLBACK to stable snapshot...")

            if stable_snapshot:
                for key, value in stable_snapshot.items():
                    if key.startswith("R"):
                        state.set_register(key, str(value))

            state.set_register("R4", json.dumps({
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "error_code": err.error_code,
                "trace": err.message,
                "watchdog_at_failure": err.watchdog_at_failure
            }))

            state.set_register("R7", "ROLLBACK_EXECUTED")
            self.state_manager.save_state(state)

            return {
                "status": "FAIL",
                "error": err.message,
                "error_code": err.error_code,
                "rollback": True,
                "state": state.get_all_registers()
            }

        except Exception as err:
            if verbose:
                print(f"  ❌ Unexpected error: {str(err)}")
                print(f"  🔄 Executing emergency ROLLBACK...")

            state.set_register("R4", json.dumps({
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "error_code": "ERR_SYSTEM_UNEXPECTED",
                "trace": str(err)
            }))

            state.set_register("R7", "ROLLBACK_FORCED")
            self.state_manager.save_state(state)

            return {
                "status": "FAIL",
                "error": str(err),
                "error_code": "ERR_SYSTEM_UNEXPECTED",
                "rollback": True
            }

    def commit(self, modified_files: List[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """COMMIT wrapper - interface pública"""
        return self.execute_commit(modified_files, verbose)

    def exit(self, verbose: bool = False) -> Dict[str, Any]:
        """EXIT opcode - Encerra sessão.
        AEP-0008 §1.1: NÃO decrementa R1.
        """
        if verbose:
            print("🚪 EXIT: Ending session with final health check...")

        state = self.state_manager.load_state()
        watchdog = int(state.get_register("R1") or 0)

        if watchdog <= 0:
            return self._trigger_exhaustion(watchdog, "EXIT", verbose)

        state.set_register("R6", "OK")
        state.set_register("R7", datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        self.state_manager.save_state(state)

        return {
            "status": "OK",
            "session": self.session_id,
            "timestamp": state.get_register("R7"),
            "watchdog_remaining": watchdog,
            "yield_history": self.yield_history
        }

    def run_program(self, program: List[str], verbose: bool = False) -> Dict[str, Any]:
        """Executa um programa completo com exhaustion guard."""
        results = {}

        for i, opcode in enumerate(program):
            parts = opcode.strip().split()
            command = parts[0]

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
                    reason = tokens[0] if tokens else "No reason provided"
                    cycles = int(tokens[1]) if len(tokens) > 1 and tokens[1].isdigit() else 1
                results["YIELD"] = self.yield_cycles(reason, cycles, verbose)
            elif command == "LOAD":
                resource_id = parts[1] if len(parts) > 1 else None
                if resource_id:
                    results["LOAD"] = self.load(resource_id, verbose)
                else:
                    results["LOAD"] = {"status": "FAIL", "error": "No resource ID provided"}
            elif command == "VALIDATE":
                resource_id = parts[1] if len(parts) > 1 else None
                if resource_id:
                    results["VALIDATE"] = self.validate(resource_id, verbose)
                else:
                    results["VALIDATE"] = {"status": "FAIL", "error": "No resource ID provided"}
            elif command == "EXEC":
                results["EXEC"] = self.exec(verbose)
            elif command == "COMMIT":
                results["COMMIT"] = self.commit(verbose=verbose)
            elif command == "EXIT":
                results["EXIT"] = self.exit(verbose)
            else:
                results[command] = {"status": "FAIL", "error": f"Unknown opcode: {command}"}

            result = results.get(command, {})
            if result.get("status") == "FAIL":
                # Parada imediata: exaustão é síncrona dentro do próprio EXEC,
                # não há look-ahead para YIELD. O YIELD deve ser preventivo.
                if verbose:
                    print(f"❌ Program halted at: {command}")
                break

        return results
