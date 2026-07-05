# AEP — Agent Execution Protocol (v1.1.0)

**Status:** Stable Specification  
**Version:** 1.1.0  
**Classification:** Execution Protocol & Fault-Tolerant Sandbox for AI Agents

[![Status: Stable](https://img.shields.io/badge/status-stable-brightgreen)]()
[![Version: 1.1.0](https://img.shields.io/badge/version-1.1.0-blue)]()
[![Conformity: 18/18](https://img.shields.io/badge/conformity-18%2F18-brightgreen)]()
[![Implementations: 3](https://img.shields.io/badge/implementations-3-blue)]()

---

> **AEP is an Execution Protocol for AI Agents.** It defines how agents can persist state, share knowledge, and execute tasks deterministically — using only structured files.

---

## Current State

| Component | Status | Description |
|-----------|--------|-------------|
| Specification | ✅ AEP-0001 to AEP-0008 | Core, Profiles, and Fault Tolerance |
| Python Runtime | ✅ 18/18 conformant | Now featuring RTOS-like capabilities |
| SQLite Runtime | ✅ Conformant | Indexer & complex resource querying |
| Resiliency (NEW) | ✅ Watchdog & ACID | Prevention of infinite loops and state corruption |

---

## Overview

AEP is a protocol for deterministic execution of AI agents over persistent knowledge resources. Based on:

- **Structured files** — Markdown, JSON, YAML, or any structured format
- **Universal Resource protocol** — all artifacts follow the same pattern
- **6 opcodes** — boot, load, validate, exec, commit, exit (3 essential: LOAD, EXEC, COMMIT)
- **Immutable kernel** — the kernel never changes, only programs and resources
- **Minimal state** — registers maintain only the current session delta

## Fault Tolerance & Execution Guarantees (AEP-0008)

Differing from standard LLM frameworks, the AEP core doesn't just prompt the agent — it bounds it within a deterministic sandbox run by the OS:
* **Watchdog Timer (R1):** Prevents token-draining infinite loops. Agents must issue a `YIELD` instruction to request more CPU cycles if a task is valid but complex.
* **ACID Transactions:** Buffers all changes. If the LLM generates an invalid resource schema, the runtime triggers a `ROLLBACK` to the last stable state (`R3`) and dumps a structured stack trace into `R4` (AEP Stderr) for self-correction.

## Filosofia

> **"O contexto é um programa declarativo que a IA interpreta."**

Em vez de o agente descobrir o contexto (crawler), o contexto define o programa (processor). Isso reduz o consumo de tokens, elimina ambiguidades e torna o comportamento determinístico.

---

## Specification Documents

| Document | Description |
|----------|-------------|
| [AEP-0001](AEP/AEP-0001-core.md) | Core Protocol |
| [AEP-0002](AEP/AEP-0002-resource.md) | Resource Specification |
| [AEP-0003](AEP/AEP-0003-isa.md) | Kernel ISA |
| [AEP-0004](AEP/AEP-0004-conformance.md) | Conformance Tests |
| [AEP-0005](AEP/AEP-0005-lifecycle.md) | Resource Lifecycle |
| [AEP-0006](AEP/AEP-0006-simplified.md) | Simplified Execution Mode |
| [AEP-0007](AEP/AEP-0007-profiles.md) | Compliance Profiles |
| [AEP-0008](AEP/AEP-0008-fault-tolerance.md) | Fault Tolerance & Execution Guarantees |

---

## Compliance Profiles

| Profile | Opcodes | Use Case |
|---------|---------|----------|
| **Lite** | LOAD, EXEC, COMMIT | Edge agents, prototyping |
| **Extended** | LOAD, VALIDATE, EXEC, COMMIT, EXIT | Enterprise, auditing |

---

## Benchmark Methodology

In our internal benchmark (v1.0.0-baseline), using a controlled scenario of 20 technical incident logs, 5 resource mappings, and Claude 3.5 Sonnet as execution engine:

| Metric | AEP | RAG Baseline | Improvement |
|--------|-----|--------------|-------------|
| Tokens | 390 | 1950 | -80% |
| Accuracy | 95% | 78% | +22% |
| Latency | ~50ms | ~200ms | -75% |

**Methodology:** [METHODOLOGY.md](tools/aep-benchmark/METHODOLOGY.md)

**Note:** Results from controlled lab environment. Production results may vary.

---

## Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd CogniX
```

### 2. Estrutura pronta
O KOS já vem com:
- Kernel (4 arquivos em KERNEL/)
- Resources de exemplo (em RESOURCES/)
- Skills básicas (markdown, git, kos)
- Templates para novos Resources

### 3. Configure seu projeto
Edite `KERNEL/STATE.md` para apontar para seu projeto:
```yaml
ACTIVE_PROJECT: seu-projeto-id
ACTIVE_STATUS: seu-status-id
```

---

## Uso Básico

### Iniciar uma sessão
```bash
# Com Claude Code
claude "Leia AGENTS.md e execute a tarefa"

# Com Cursor
cursor "Leia AGENTS.md e execute a tarefa"

# Com Aider
aider --message "Leia AGENTS.md e execute a tarefa"
```

### Criar um novo Resource
1. Crie um arquivo em `RESOURCES/`
2. Siga o protocolo:
```yaml
---
type: project | status | skill | adr | incident | rule | template
id: <identificador-unico>
version: <semver>
depends: [<resource-id>, ...]
status: draft | active | deprecated | archived
---
# CONTEÚDO
...
```

### Executar o fluxo padrão
O `KERNEL/PROGRAM.md` define o fluxo atual:
```
BOOT
LOAD [ACTIVE_PROJECT]
LOAD [ACTIVE_STATUS]
VALIDATE [ACTIVE_PROJECT]
VALIDATE [ACTIVE_STATUS]
EXEC
COMMIT
  ├── Atualiza R0-R7
  ├── Limpa R3 (apenas arquivos desta sessão)
  └── Persiste alterações
EXIT
```

---

## Arquitetura

### Kernel (4 arquivos)
| Arquivo | Função |
|---------|--------|
| `KERNEL/BOOT.md` | Sequência de inicialização |
| `KERNEL/ISA.md` | Definição dos opcodes e contratos |
| `KERNEL/PROGRAM.md` | Fluxo atual do programa |
| `KERNEL/STATE.md` | Estado global do sistema |

### Opcodes (6 instruções)
| Opcode | Função |
|--------|--------|
| `BOOT` | Inicializa o sistema |
| `LOAD` | Carrega um Resource pelo ID |
| `VALIDATE` | Verifica estrutura do Resource |
| `EXEC` | Executa a tarefa definida |
| `COMMIT` | Persiste alterações e classifica conhecimento |
| `EXIT` | Encerra a sessão |

### Resources
Todos os artefatos seguem o mesmo protocolo:
- **project**: Definição do projeto (objetivo, escopo, stack, regras)
- **status**: Estado atual (registradores R0-R7)
- **skill**: Conhecimento reutilizável (objetivo, procedimento, exemplos)
- **adr**: Decisão arquitetural (problema, decisão, alternativas)
- **incident**: Registro de erro (problema, causa, correção)
- **rule**: Regra do projeto
- **template**: Template para novos Resources

### Registradores de Estado (R0-R7)
| Registrador | Função | Regra |
|-------------|--------|-------|
| R0 [SESSION] | Identificador da sessão | Gerado a cada BOOT |
| R1 [LAST_ACT] | Última ação realizada | Atualizado no COMMIT |
| R2 [NEXT_ACT] | Próxima ação planejada | Definido pelo agente |
| R3 [MODIFIED] | Arquivos modificados nesta sessão | **APENAS delta da sessão atual** |
| R4 [BLOCKERS] | Bloqueios atuais | Atualizado quando necessário |
| R5 [ACTIVE_SK] | Skill ativa | Definido pelo agente |
| R6 [HEALTH] | Saúde do sistema | OK ou FALHA |
| R7 [TIMESTAMP] | Timestamp da sessão | Atualizado no COMMIT |

**Importante:** R3 [MODIFIED] deve conter APENAS os arquivos modificados na sessão atual. Histórico pertence ao Git, não ao estado.

---

## Exemplo de Sessão

```bash
# 1. Iniciar
claude "Leia AGENTS.md e execute a tarefa"

# 2. O agente executa o fluxo
# BOOT → Carrega estado
# LOAD project-cognix → Carrega projeto
# LOAD status-cognix → Carrega status
# VALIDATE → Verifica estrutura
# EXEC → Executa tarefa (R2 - NEXT_ACT)
# COMMIT → Persiste alterações, limpa R3
# EXIT → Encerra

# 3. Resultado
# Recursos atualizados, R3 contém apenas delta da sessão
```

---

## Recursos Disponíveis

### Projetos
- `project-cognix` — Projeto de referência do KOS

### Status
- `status-cognix` — Estado atual do CogniX

### Skills
- `skill-markdown` — Sintaxe e boas práticas de Markdown
- `skill-kos` — Como operar o KOS
- `skill-git` — Comandos e fluxos Git

### ADRs
- `adr-001-kernel-design` — Decisão de design do microkernel

### Incidentes
- `incident-001-validate-failure` — Falha de validação + vacina

### Templates
- `template-project` — Template para projetos
- `template-status` — Template para status
- `template-skill` — Template para skills

### Regras
- `rule-r3-lifecycle` — Ciclo de vida do R3 [MODIFIED]

---

## Roadmap

### Phase 1: Specification (✅ Complete)
- Core protocol defined
- Resource format specified
- ISA documented
- Conformance tests designed
- Lifecycle defined

### Phase 2: Implementation (🔄 In Progress)
- Reference implementation (Markdown) — ✅
- JSON implementation — ⏳
- SQLite implementation — ⏳
- YAML implementation — ⏳

### Phase 3: Interoperability (⏳ Pending)
- Cross-runtime resource exchange
- Conformance suite automation
- Compatibility certification

### Phase 4: Standardization (⏳ Pending)
- Community adoption
- Independent implementations
- Formal standards submission

---

## Próximos Passos

1. Read `AEP/` for the full specification
2. Read `USAGE.md` for practical guidance
3. Read `CONTRIBUTING.md` for how to help
4. Try the reference implementation (KOS v6.0)
5. Build an independent implementation

---

## Licença

MIT

---

## Status do Projeto

| Component | Status |
|-----------|--------|
| Specification (AEP-0001 to AEP-0008) | ✅ Complete |
| Reference Implementation (Markdown) | ✅ Functional |
| Python Runtime (AEP-0008) | ✅ 18/18 tests passed |
| Validation (Claude Code) | ✅ Passed |
| Independent Implementations | ⏳ Pending |
| Interoperability | ⏳ Not demonstrated |
| Conformance Suite | ⏳ In development |

**Estágio: Especificação Estável com Garantias de Tolerância a Falhas**

> AEP v1.1.0 é uma especificação estável com garantias de sistema operacional (ACID), Watchdog Timer e proteção contra loops/alucinações. Pronto para adoção em produção.