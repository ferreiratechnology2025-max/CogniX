# 🧬 INSTRUCTION SET ARCHITECTURE — KOS v6.0

## OPCODES

### BOOT
Inicializa o sistema, carrega STATE e PROGRAM

### LOAD
Carrega um Resource pelo ID (inclui dependências declaradas)
- Formato: LOAD <resource-id>
- Exemplo: LOAD project-api-core

### VALIDATE
Verifica estrutura do Resource (campos obrigatórios)
- Formato: VALIDATE <resource-id>
- Exemplo: VALIDATE project-api-core
- Verifica: type, id, version, status

### EXEC
Executa a tarefa definida no PROGRAM
- Baseado no estado atual (R2 - NEXT_ACT)
- Gera resultado

### COMMIT
Persiste alterações e classifica novo conhecimento

**Comportamento:**
1. Atualiza Resources existentes (ex: STATUS.md)
2. **Limpa R3 [MODIFIED]** → substitui pelo delta da sessão atual
3. Cria novos Resources quando necessário
4. Atualiza STATE.md

**Regras:**
- R3 [MODIFIED] deve conter APENAS os arquivos modificados nesta sessão
- R1 [LAST_ACT] deve refletir a ação atual
- R7 [TIMESTAMP] deve ser atualizado
- R3 NUNCA deve acumular histórico (histórico fica no Git)

**Exemplo correto:**
```yaml
# Antes do COMMIT
R3 [MODIFIED] = KERNEL/STATE.md

# Durante COMMIT - agente modificou status-cognix.md

# Após COMMIT (correto)
R3 [MODIFIED] = RESOURCES/status-cognix.md
```

**Exemplo incorreto (acúmulo):**
```yaml
# Após COMMIT (errado)
R3 [MODIFIED] = KERNEL/STATE.md, RESOURCES/report-test.md, RESOURCES/status-cognix.md
```

### EXIT
Encerra a sessão
- Registra timestamp
- Salva estado final

## CONTRATOS DOS OPCODES

| Opcode | Entrada | Saída | Efeito Colateral |
|--------|---------|-------|------------------|
| BOOT | STATE.md, PROGRAM.md | Estado inicial | Nenhum |
| LOAD | Resource ID | Resource carregado | Nenhum |
| VALIDATE | Resource ID | OK / FALHA | Nenhum |
| EXEC | Tarefa | Resultado | Modifica arquivos |
| COMMIT | Alterações | Resources persistidos | Escreve arquivos |
| EXIT | Nenhum | Sessão encerrada | Salva STATE.md |

## TIPOS DE RESOURCE (definidos por metadados)
- project
- status
- skill
- adr
- incident
- rule
- template
- (qualquer outro definido pelo usuário)

## ESTRUTURA PADRÃO DE UM RESOURCE
```yaml
---
type: <tipo>
id: <identificador-unico>
version: <semver>
depends: [<resource-id>, ...]
status: draft | active | deprecated | archived
---
# CONTEÚDO
...
```