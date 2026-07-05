# AEP Python Implementation v1.0.0

## Descrição

Implementação independente do Agent Execution Protocol (AEP) em Python.

## Instalação

```bash
cd implementations/python
pip install -e .
```

## Uso

### CLI

```bash
# Listar todos os Resources
python -m aep.cli.main --list --base ../../

# Rodar programa completo
python -m aep.cli.main --program --base ../../ --verbose

# Validar um Resource
python -m aep.cli.main --resource project-cognix --base ../../ --verbose

# Validar estado
python -m aep.cli.main --state --base ../../

# Executar opcodes individualmente
python -m aep.cli.main --run boot --base ../../
python -m aep.cli.main --run validate --resource project-cognix --base ../../ --verbose
python -m aep.cli.main --run exec --base ../../ --verbose
python -m aep.cli.main --run commit --base ../../ --verbose
python -m aep.cli.main --run exit --base ../../ --verbose
```

### Em Código

```python
from aep.core.kernel import AEPKernel

kernel = AEPKernel("../../")

# Boot
kernel.boot()

# Load
kernel.load("project-cognix")

# Validate
kernel.validate("project-cognix", verbose=True)

# Exec
kernel.exec(verbose=True)

# Commit
kernel.commit(verbose=True)

# Exit
kernel.exit(verbose=True)
```

## Testes

```bash
python -m pytest tests/
```

## Status

- [x] Core Kernel (6 opcodes)
- [x] State Management (R0-R7)
- [x] Resource Management
- [x] CLI
- [x] Resource Validation
- [ ] Full Conformance Suite