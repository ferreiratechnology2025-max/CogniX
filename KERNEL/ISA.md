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
- Atualiza Resources existentes
- Cria novos Resources quando necessário
- Atualiza STATE.md

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