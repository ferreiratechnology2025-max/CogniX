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

## Interoperabilidade

- ✅ Importa Resources do Markdown KOS v6.0
- ✅ Mesmos opcodes e contratos
- ✅ Compatível com Conformance Suite