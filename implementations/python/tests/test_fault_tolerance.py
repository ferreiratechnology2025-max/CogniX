#!/usr/bin/env python3
"""
Testes de Tolerância a Falhas (AEP-0008)
"""

import os
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from aep.core.kernel import AEPKernel, AEPRuntimeError
from aep.core.state import State, StateManager


class TestAEP0008FaultTolerance(unittest.TestCase):

    def setUp(self):
        """Configura ambiente de teste"""
        self.test_dir = tempfile.mkdtemp()
        self.state_path = os.path.join(self.test_dir, "KERNEL", "STATE.md")
        self.resources_path = os.path.join(self.test_dir, "RESOURCES")
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        os.makedirs(self.resources_path, exist_ok=True)

        self._create_initial_state()
        self.kernel = AEPKernel(self.test_dir)

    def _create_initial_state(self):
        """Cria um estado inicial válido"""
        state = State()
        state.set_register("R0", "2026-07-05-00-00")
        state.set_register("R1", "5")
        state.set_register("R2", "Testar watchdog")
        state.set_register("R3", "{}")
        state.set_register("R4", None)
        state.set_register("R5", "skill-kos")
        state.set_register("R6", "OK")
        state.set_register("R7", "2026-07-05T00:00:00Z")

        state.type = "state"
        state.id = "kernel-state"
        state.version = "1.0.0"
        state.status = "active"

        manager = StateManager(self.test_dir)
        manager.save_state(state)

    def test_watchdog_decrement_on_load(self):
        """Testa que LOAD decrementa o Watchdog"""
        # Cria um resource válido para load
        resource_content = """---
type: project
id: test-resource
version: 1.0.0
status: active
---
# Test Resource
"""
        with open(os.path.join(self.resources_path, "test-resource.md"), "w") as f:
            f.write(resource_content)

        result = self.kernel.load("test-resource")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["watchdog_remaining"], 4)

    def test_watchdog_timeout_on_expired(self):
        """Testa que operações falham com Watchdog expirado"""
        state = self.kernel.state_manager.load_state()
        state.set_register("R1", "0")
        self.kernel.state_manager.save_state(state)

        result = self.kernel.load("nonexistent")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("Watchdog timer expired", result["error"])

    def test_yield_extension(self):
        """Testa que YIELD estende o Watchdog"""
        state = self.kernel.state_manager.load_state()
        initial_watchdog = int(state.get_register("R1") or 0)

        result = self.kernel.yield_cycles("Teste de extensão", 3)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["approved"], 3)

        state = self.kernel.state_manager.load_state()
        new_watchdog = int(state.get_register("R1") or 0)
        self.assertEqual(new_watchdog, initial_watchdog + 3)

    def test_yield_global_limit(self):
        """Testa que YIELD respeita o limite global"""
        result = self.kernel.yield_cycles("Teste de limite", 20)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("exceeds maximum", result["error"])

    def test_rollback_on_invalid_commit(self):
        """Testa que COMMIT com dados invalidos faz rollback"""
        # Cria resource INVALIDO (sem campo type) para forcar falha de validacao
        invalid_resource = "---\nid: recurso-invalido\nversion: 1.0.0\nstatus: active\n---\n# Bad Resource"
        with open(os.path.join(self.resources_path, "recurso-invalido.md"), "w", encoding="utf-8") as f:
            f.write(invalid_resource)

        result = self.kernel.execute_commit(modified_files=["recurso-invalido.md"])
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result.get("rollback", False))

        state = self.kernel.state_manager.load_state()
        r4 = state.get_register("R4")
        self.assertIsNotNone(r4)

        r4_data = json.loads(r4)
        self.assertIn("error_code", r4_data)
        self.assertIn("trace", r4_data)
        self.assertEqual(r4_data["error_code"], "ERR_AEP_0002_VALIDATION")

        self.assertEqual(state.get_register("R7"), "ROLLBACK_EXECUTED")

    def test_yield_history_tracking(self):
        """Testa que o histórico de YIELD é mantido"""
        self.kernel.yield_cycles("Primeiro yield", 2)
        self.kernel.yield_cycles("Segundo yield", 1)

        self.assertEqual(len(self.kernel.yield_history), 2)
        self.assertEqual(self.kernel.yield_history[0]["reason"], "Primeiro yield")
        self.assertEqual(self.kernel.yield_history[1]["reason"], "Segundo yield")

    def test_yield_metadata_in_exit(self):
        """Testa que EXIT inclui histórico de YIELD"""
        self.kernel.yield_cycles("Teste para exit", 2)
        result = self.kernel.exit()

        self.assertEqual(result["status"], "OK")
        self.assertIn("yield_history", result)
        self.assertEqual(len(result["yield_history"]), 1)

    def test_exec_watchdog_decrement(self):
        """Testa que EXEC decrementa o Watchdog"""
        result = self.kernel.exec()
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["watchdog_remaining"], 4)

    def test_exec_does_not_interpret_r2(self):
        """AEP-0003 s3.4: EXEC MUST treat R2 as opaque (never execute it).

        Sets R2 to an executable-looking payload and asserts the kernel runs
        the EXEC cycle normally, returns R2 unchanged, and produces no side
        effect from R2's contents. This is the mechanical enforcement of the
        Execution Boundary: if any implementation makes EXEC eval/dispatch R2,
        this test breaks.
        """
        payload = "rm -rf / ; __import__('os').system('touch pwned')"

        state = self.kernel.state_manager.load_state()
        state.set_register("R2", payload)
        self.kernel.state_manager.save_state(state)

        result = self.kernel.exec()

        # Cycle completes normally, R2 returned verbatim (opaque).
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["task"], payload)
        # Watchdog decremented exactly once (5 -> 4).
        self.assertEqual(result["watchdog_remaining"], 4)
        # No side effect from R2's contents: the payload's "touch pwned"
        # must never have run.
        self.assertFalse(
            os.path.exists(os.path.join(self.test_dir, "pwned")),
            "EXEC executed R2 contents — Execution Boundary violated",
        )

    def test_complete_program_with_yield(self):
        """Testa um programa completo com YIELD"""
        # Cria resource válido
        resource_content = """---
type: project
id: test-resource
version: 1.0.0
status: active
---
# Test Resource
"""
        with open(os.path.join(self.resources_path, "test-resource.md"), "w") as f:
            f.write(resource_content)

        program = [
            "BOOT",
            "YIELD 'Load resources needed' 2",
            "LOAD test-resource",
            "VALIDATE test-resource",
            "EXEC",
            "COMMIT",
            "EXIT"
        ]

        results = self.kernel.run_program(program, verbose=False)

        self.assertIn("BOOT", results)
        self.assertIn("YIELD", results)
        self.assertIn("LOAD", results)
        self.assertIn("VALIDATE", results)
        self.assertIn("EXEC", results)
        self.assertIn("COMMIT", results)
        self.assertIn("EXIT", results)

        self.assertEqual(results["YIELD"]["status"], "OK")
        self.assertEqual(results["LOAD"]["status"], "OK")
        self.assertEqual(results["VALIDATE"]["status"], "OK")


if __name__ == "__main__":
    unittest.main()
