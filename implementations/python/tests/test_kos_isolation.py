#!/usr/bin/env python3
"""
Teste de regressao: Isolamento entre namespace KOS e runtime AEP.

O StateManager do AEP (state.py) ja nao le de KERNEL/STATE.md.
Este teste corrompe intencionalmente o arquivo KERNEL/STATE.md e verifica
que o runtime AEP permanece 100% estavel — comprovando imunidade total
ao estado residual do meta-kernel KOS.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from aep.core.kernel import AEPKernel
from aep.core.state import State, StateManager


class TestKOSIsolation(unittest.TestCase):

    KOS_STATE_PATH = "KERNEL/STATE.md"

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.resources_path = os.path.join(self.test_dir, "RESOURCES")
        self.kos_state_path = os.path.join(self.test_dir, self.KOS_STATE_PATH)
        os.makedirs(self.resources_path, exist_ok=True)

        # Clear AEP_STATE_PATH so StateManager derives path from test_dir
        self._old_aep_state_path = os.environ.pop("AEP_STATE_PATH", None)

        self._create_valid_aep_state()
        self.kernel = AEPKernel(self.test_dir)

    def _create_valid_aep_state(self):
        """Cria estado AEP valido em AEP/runtime_state/state.md"""
        state = State()
        state.set_register("R0", "isolation-test")
        state.set_register("R1", "5")
        state.set_register("R2", "Testar isolamento KOS")
        state.set_register("R3", "{}")
        state.set_register("R4", None)
        state.set_register("R5", "skill-kos")
        state.set_register("R6", "OK")
        state.set_register("R7", "2026-07-11T00:00:00Z")
        state.type = "state"
        state.id = "kernel-state"
        state.version = "1.0.0"
        state.status = "active"

        manager = StateManager(self.test_dir)
        manager.save_state(state)

    def tearDown(self):
        if self._old_aep_state_path is not None:
            os.environ["AEP_STATE_PATH"] = self._old_aep_state_path

    def _corrupt_kos_state(self, content: str):
        """Escreve lixo no KERNEL/STATE.md do KOS"""
        os.makedirs(os.path.dirname(self.kos_state_path), exist_ok=True)
        with open(self.kos_state_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _aep_state(self):
        """Carrega o estado atual do AEP runtime"""
        return self.kernel.state_manager.load_state()

    def test_aep_ignores_corrupt_kos_state(self):
        """KERNEL/STATE.md corrompido com lixo -> AEP runtime permanece OK"""
        self._corrupt_kos_state("LIXO TOTAL — este arquivo deveria ser JSON\n" * 50)
        state = self._aep_state()
        self.assertEqual(state.get_register("R6"), "OK")

    def test_aep_ignores_kos_health_fail(self):
        """KERNEL/STATE.md com HEALTH=FAIL -> AEP runtime ignora"""
        kos_fail = """---
type: state
id: kernel-state
version: 1.0.0
status: active
---
# ESTADO GLOBAL DO KERNEL

R0 [SESSION] = 2026-07-11-14-40
R1 [LAST_ACT] = 0
R2 [NEXT_ACT] = alguma tarefa
R3 [MODIFIED] = {}
R4 [BLOCKERS] = {"error_code": "AEP_ERR_WATCHDOG_EXHAUSTION"}
R5 [ACTIVE_SK] = skill-kos
R6 [HEALTH] = FAIL
R7 [TIMESTAMP] = EXIT_1_WATCHDOG_TIMEOUT
"""
        self._corrupt_kos_state(kos_fail)
        state = self._aep_state()
        self.assertEqual(state.get_register("R6"), "OK")

    def test_aep_ignores_kos_empty_state(self):
        """KERNEL/STATE.md vazio -> AEP runtime permanece estavel"""
        self._corrupt_kos_state("")
        state = self._aep_state()
        self.assertEqual(state.get_register("R6"), "OK")

    def test_aep_exec_after_kos_corruption(self):
        """Apos KERNEL/STATE.md corrompido, EXEC funciona normalmente"""
        self._corrupt_kos_state("garbage data that would crash any parser\n")
        result = self.kernel.exec()
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["watchdog_remaining"], 4)

    def test_aep_yield_after_kos_corruption(self):
        """Apos KERNEL/STATE.md corrompido, YIELD funciona normalmente"""
        self._corrupt_kos_state("TOTAL GARBAGE\n" * 20)
        result = self.kernel.yield_cycles("isolation test", 2)
        self.assertEqual(result["status"], "OK")
        state = self._aep_state()
        self.assertEqual(int(state.get_register("R1") or 0), 7)

    def test_aep_state_path_env_var(self):
        """Variavel de ambiente AEP_STATE_PATH sobrepoe o caminho padrao"""
        alt_dir = tempfile.mkdtemp()
        alt_state = os.path.join(alt_dir, "custom-state.md")

        old_env = os.environ.get("AEP_STATE_PATH")
        try:
            os.environ["AEP_STATE_PATH"] = alt_state

            state = State()
            state.set_register("R0", "env-test")
            state.set_register("R1", "10")
            state.set_register("R6", "OK")
            manager = StateManager(self.test_dir)
            manager.save_state(state)

            self.assertTrue(os.path.exists(alt_state),
                            "AEP_STATE_PATH nao foi respeitado")

            loaded = manager.load_state()
            self.assertEqual(loaded.get_register("R0"), "env-test")
            self.assertEqual(loaded.get_register("R1"), "10")
        finally:
            if old_env is None:
                del os.environ["AEP_STATE_PATH"]
            else:
                os.environ["AEP_STATE_PATH"] = old_env

    def test_aep_runtime_state_is_not_kos_state(self):
        """Arquivos de estado do AEP e do KOS sao fisicamente distintos"""
        aep_path = self.kernel.state_manager.state_path
        self.assertNotEqual(aep_path, self.kos_state_path)
        self.assertNotIn("KERNEL", aep_path)
        self.assertIn("AEP", aep_path)

    def test_complete_program_after_kos_corruption(self):
        """Programa completo (BOOT..EXIT) funciona apos KOS KERNEL/STATE.md corrompido"""
        self._corrupt_kos_state("BINARY GARBAGE \x00\x01\x02 NOT A STATE FILE\n")

        resource_content = """---
type: project
id: isolation-resource
version: 1.0.0
status: active
---
# Isolation Resource
"""
        with open(os.path.join(self.resources_path, "isolation-resource.md"), "w") as f:
            f.write(resource_content)

        program = [
            "BOOT",
            "YIELD 'kos isolation prep' 2",
            "LOAD isolation-resource",
            "VALIDATE isolation-resource",
            "EXEC",
            "COMMIT",
            "EXIT"
        ]

        results = self.kernel.run_program(program, verbose=False)

        self.assertEqual(results["BOOT"]["status"], "OK")
        self.assertEqual(results["YIELD"]["status"], "OK")
        self.assertEqual(results["LOAD"]["status"], "OK")
        self.assertEqual(results["VALIDATE"]["status"], "OK")
        self.assertEqual(results["EXEC"]["status"], "OK")


if __name__ == "__main__":
    unittest.main()
