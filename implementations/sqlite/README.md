# AEP SQLite Implementation v1.0.0

## Descrição

Implementação do Agent Execution Protocol (AEP) usando SQLite como backend.

**Características:**
- ✅ Armazenamento em SQLite (sem Markdown)
- ✅ 6 core opcodes implementados
- ✅ Schema normalizado (Resources + Dependencies)
- ✅ Importação de Resources Markdown
- ✅ Independente de formato

## Instalação

```bash
cd implementations/sqlite
pip install -e .
```

## Uso

### CLI

```bash
# Inicializar banco
python -m aep_sqlite.cli --init

# Importar Resources do Markdown
python import_from_markdown.py

# Listar Resources
python -m aep_sqlite.cli --list

# Rodar programa
python -m aep_sqlite.cli --program --verbose
```

### Em Código

```python
from aep_sqlite.kernel import AEPKernelSQLite

kernel = AEPKernelSQLite("aep.db")
kernel.boot()
kernel.load("project-cognix")
kernel.validate("project-cognix")
```

## Schema

```sql
resources (id, type, version, status, content)
resource_dependencies (resource_id, depends_on)
kernel_state (r0-r7 registers)
```

## AEP-0008 (Fault Tolerance) — Not Implemented

⚠️ **This runtime does NOT implement AEP-0008 Fault Tolerance.**

- **R1 [WATCHDOG] is unsupported.** There is no instruction counter, no
  watchdog decrement, no YIELD opcode, and no cycle enforcement.
- The internal column `internal_last_action` stores a descriptive string of
  the last executed opcode — it is **not** R1 and MUST NOT be read or written
  through the R1 register interface.
- **Register R1 is officially unimplemented** in this environment. Calling
  `get_register("R1")` returns `None`.
- **COMMIT has no rollback.** Validation failures are reported but state is
  not atomically restored.
- Full AEP-0008 conformance is out of scope for this backend in its current
  version. See `AEP/conformance-matrix-0008.md` for the waiver registry.

## Interoperabilidade

- ✅ Importa Resources do Markdown KOS v6.0
- ✅ Mesmos opcodes e contratos (excluindo AEP-0008)
- ⚠️ Conformance Suite: passa apenas testes dos 6 opcodes core (TC-001 a
  TC-010); testes AEP-0008 (TC-011 em diante) falham deliberadamente