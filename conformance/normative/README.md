# AEP Normative Test Suite v1.0.0

## Descrição

A Normative Test Suite define o comportamento esperado do AEP através de casos de teste executáveis. Qualquer implementação compatível deve passar nestes testes.

## Estrutura

```
normative/
├── test_cases/          # Casos de teste YAML
├── snapshots/           # Snapshots de estado
│   ├── expected/
│   └── actual/
├── runtimes/            # Adaptadores para runtimes
└── test_runner.py       # Executor de testes
```

## Casos de Teste

| ID | Nome | Descrição |
|----|------|-----------|
| TC-001 | Boot | System initialization |
| TC-002 | Load | Resource loading |
| TC-003 | Validate | Resource validation |
| TC-004 | Exec | Task execution |
| TC-005 | Commit | State persistence |
| TC-006 | Exit | Session end |
| TC-007 | Complete Flow | Full program |
| TC-008 | Dependencies | Dependency resolution |
| TC-009 | Error Handling | Error scenarios |

## Uso

```bash
# Testar todos os runtimes
python test_runner.py --runtime all --verbose

# Testar apenas Python
python test_runner.py --runtime python

# Gerar relatório
python test_runner.py --runtime all --report
```

## Criar Novos Testes

1. Criar arquivo YAML em `test_cases/`
2. Definir preconditions e expected
3. Executar runner
4. Verificar snapshots