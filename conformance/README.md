# AEP Conformance Suite v1.0.0

## Descrição

O Conformance Suite valida se uma implementação segue o protocolo AEP v1.0.0.

## Estrutura

```
conformance/
├── runner/
│   ├── conformance-runner.js    # Script principal
│   └── validators/
│       ├── state-validator.js   # Validação de estado
│       └── resource-validator.js # Validação de Resources
├── tests/                       # Testes de conformidade
└── package.json
```

## Uso

### Validar um arquivo de estado

```bash
node runner/conformance-runner.js --state ../KERNEL/STATE.md
```

### Validar um Resource

```bash
node runner/conformance-runner.js --resource ../RESOURCES/project-cognix.md
```

### Rodar todos os testes

```bash
npm test
```

## Saída Esperada

```
============================================================
AEP Conformance Runner v1.0.0
============================================================

ℹ️  Validating state file: ../KERNEL/STATE.md
✅ State validation passed

============================================================
Summary
============================================================

ℹ️  Total: 1
✅ Passed: 1
✅ All validations passed
```

## Testes Implementados

- [x] State Validation (R0-R7)
- [x] Resource Validation (type, id, version, depends, status)
- [ ] Boot Test
- [ ] Load Test
- [ ] Validate Test
- [ ] Execute Test
- [ ] Commit Test
- [ ] Exit Test
- [ ] Complete Flow Test