# KOS — Knowledge Operating System v6.0

**Kernel mínimo para agentes de IA baseado em Markdown puro.**

## Visão Geral

KOS é um sistema operacional de conhecimento que transforma seu repositório em um ambiente executável para agentes de IA. Baseado em:

- **Markdown puro** — zero dependências
- **Protocolo universal de Resources** — todos os artefatos seguem o mesmo padrão
- **ISA de 6 opcodes** — boot, load, validate, exec, commit, exit
- **Microkernel imutável** — o kernel nunca muda, apenas o programa e os resources

## Filosofia

> **"O contexto é um programa declarativo que a IA interpreta."**

Em vez de o agente descobrir o contexto (crawler), o contexto define o programa (processor). Isso reduz o consumo de tokens, elimina ambiguidades e torna o comportamento determinístico.

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

### 3. Configure seu projeto
Edite `KERNEL/STATE.md` para apontar para seu projeto:
```yaml
ACTIVE_PROJECT: seu-projeto-id
ACTIVE_STATUS: seu-status-id
```

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
EXIT
```

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
# COMMIT → Persiste alterações
# EXIT → Encerra

# 3. Resultado
# Recursos atualizados, novo estado salvo
```

## Próximos Passos

1. Leia `USAGE.md` para exemplos detalhados
2. Leia `CONTRIBUTING.md` para como contribuir
3. Explore os Resources em `RESOURCES/`
4. Crie seu primeiro projeto com KOS

## Licença

MIT

## Status do Projeto

✅ Kernel v6.0 instalado  
✅ Protocolo de Resources validado  
✅ Skills básicas disponíveis  
✅ Fluxo completo testado  
✅ Documentação completa