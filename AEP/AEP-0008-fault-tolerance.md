# AEP-0008: Garantias de Execução, Tolerância a Falhas e Recuperação

**Status:** Active  
**Version:** 1.0.0  
**Date:** 2026-07-05  

---

## 1. O Watchdog Timer Abstrato (Registrador R1)

O Registrador R1 atua como o contador de instruções estrito (Instruction Counter/Quantum). Cada ciclo de execução `EXEC` consome obrigatoriamente 1 unidade de R1.

### 1.1 A Instrução YIELD

Se o agente identificar que a complexidade computacional da tarefa exige mais ciclos do que o teto atual de R1, ele DEVE emitir o opcode `YIELD` antes que `R1 == 0`.

```yaml
# Sintaxe
instruction: YIELD
payload:
  reason: "String descritiva da necessidade de extensão"
  requested_cycles: Integer (Max: 10)
```

### 1.2 Exemplo de Uso

```python
# Solicita extensão de 3 ciclos para processamento complexo
result = kernel.yield_cycles(
    reason="Validating complex dependency graph",
    requested_cycles=3
)
```

### 1.3 Limites

- Máximo de ciclos por YIELD: **10**
- Limite global de ciclos: **20** (configurável via `max_watchdog_cycles`)
- Histórico de YIELD mantido para auditoria

---

## 2. Transações ACID e o "Stderr" de Validação (R4)

O opcode `COMMIT` opera de forma atômica. Qualquer mutação sugerida no estado só se torna persistente após validação sintática e semântica do Runtime.

### 2.1 Fluxo de Falha e Rollback Estruturado

Caso a validação falhe:

1. **Rollback:** Runtime descarta alterações e restaura o snapshot estável de R3
2. **Injeção de Stderr:** Runtime escreve o erro estruturado em **R4**
3. **Loop de Autocorreção:** Agente lê R4 no próximo ciclo e corrige

### 2.2 Exemplo de Stderr em R4

```json
{
  "timestamp": "2026-07-05T01:18:03Z",
  "error_code": "ERR_AEP_0002_DANGLING_DEP",
  "trace": "Resource 'incident-04' has dangling dependency: 'recurso-que-nao-existe'",
  "watchdog_at_failure": 2
}
```

### 2.3 Snapshot Estável (R3)

Antes de cada COMMIT, o Runtime captura o estado atual como snapshot estável em R3. Em caso de falha, o estado é restaurado para este snapshot.

---

## 3. Códigos de Erro

| Código | Descrição |
|--------|-----------|
| ERR_AEP_0002_VALIDATION | Falha na validação do Resource |
| ERR_AEP_0003_E001 | Resource não encontrado |
| ERR_AEP_0003_E002 | Dependência não encontrada |
| ERR_AEP_0008_TIMEOUT | Watchdog expirado |
| ERR_SYSTEM_UNEXPECTED | Falha inesperada do sistema |

---

## 4. Ciclo de Vida com Fault Tolerance

```
BOOT → YIELD? → LOAD → VALIDATE → EXEC → COMMIT → EXIT
                  ↑                   ↓
                  └── Watchdog > 0 ───┘
                        ↓ (se = 0)
                    YIELD ou HALT
```

### 4.1 Estados de Saída

| Estado | Significado |
|--------|-------------|
| EXIT_0_SUCCESS | Sessão encerrada com sucesso |
| EXIT_1_WATCHDOG_TIMEOUT | Sessão encerrada por timeout do Watchdog |
| ROLLBACK_EXECUTED | Rollback executado devido a falha |
| ROLLBACK_FORCED | Rollback forçado por erro inesperado |

---

## 5. Implementação de Referência

Veja `implementations/python/aep/core/kernel.py` para a implementação completa.

### 5.1 Métodos Principais

| Método | Opcode | Descrição |
|--------|--------|-----------|
| `boot()` | BOOT | Inicializa sistema com Watchdog |
| `yield_cycles()` | YIELD | Solicita extensão de ciclos |
| `load()` | LOAD | Carrega Resource com validação |
| `validate()` | VALIDATE | Valida estrutura do Resource |
| `exec()` | EXEC | Executa tarefa com Watchdog |
| `execute_commit()` | COMMIT | Transação ACID com Rollback |
| `exit()` | EXIT | Encerra sessão |
