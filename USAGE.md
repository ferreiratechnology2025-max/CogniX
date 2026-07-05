# Guia de Uso do KOS

## Índice
1. [Conceitos Fundamentais](#conceitos-fundamentais)
2. [Criando um Projeto](#criando-um-projeto)
3. [Gerenciando Resources](#gerenciando-resources)
4. [Criando Skills](#criando-skills)
5. [Fluxo de Trabalho](#fluxo-de-trabalho)
6. [Exemplos Práticos](#exemplos-praticos)

## Conceitos Fundamentais

### Resource
Todo artefato no KOS é um Resource. A diferença entre um projeto, uma skill e um ADR é apenas o `type` no cabeçalho.

```yaml
---
type: project    # project, status, skill, adr, incident, rule, template
id: meu-recurso
version: 1.0.0
depends: []
status: active
---
# Conteúdo específico do recurso
```

### Kernel
O Kernel é imutável. Ele define:
- A ISA (conjunto de opcodes)
- O programa atual (fluxo)
- O estado global (projeto ativo, sessão, etc.)

### Programa
O programa é a sequência de opcodes que o agente executa. Você pode ter múltiplos programas:
- `padrao` - Fluxo completo
- `review` - Apenas validação
- `deploy` - Fluxo de implantação

## Criando um Projeto

### Passo 1: Defina o projeto
Crie `RESOURCES/project-meuprojeto.md`:
```yaml
---
type: project
id: project-meuprojeto
version: 0.1.0
depends: [skill-markdown]
status: active
---
# PROJETO: Meu Projeto

## OBJETIVO
Descreva o objetivo do projeto

## ESCOPO
O que está dentro e fora do escopo

## STACK
Tecnologias utilizadas

## REGRAS
1. Regra 1
2. Regra 2
```

### Passo 2: Crie o status
Crie `RESOURCES/status-meuprojeto.md`:
```yaml
---
type: status
id: status-meuprojeto
version: 0.1.0
depends: [project-meuprojeto]
status: active
---
# STATE REGISTERS

R0 [SESSION] = <timestamp>
R1 [LAST_ACT] = <última ação>
R2 [NEXT_ACT] = <próxima ação>
R3 [MODIFIED] = <arquivos modificados>
R4 [BLOCKERS] = <bloqueios>
R5 [ACTIVE_SK] = <skill ativa>
R6 [HEALTH] = OK
R7 [TIMESTAMP] = <timestamp>
```

### Passo 3: Ative o projeto
Edite `KERNEL/STATE.md`:
```yaml
ACTIVE_PROJECT: project-meuprojeto
ACTIVE_STATUS: status-meuprojeto
```

## Gerenciando Resources

### Criar um Resource
1. Crie o arquivo em `RESOURCES/`
2. Adicione o frontmatter YAML
3. Adicione o conteúdo Markdown
4. Atualize as dependências se necessário

### Validar um Resource
O agente executa automaticamente `VALIDATE` durante o fluxo. Para validar manualmente, o programa deve incluir `VALIDATE <resource-id>`.

### Atualizar um Resource
1. Edite o arquivo
2. Atualize `version` (ex: 0.1.0 → 0.1.1)
3. O agente fará `COMMIT` durante a próxima execução

## Criando Skills

### Estrutura de uma Skill
```yaml
---
type: skill
id: skill-exemplo
version: 1.0.0
depends: []
status: active
---
# SKILL: Exemplo

## OBJETIVO
O que esta skill ensina

## QUANDO USAR
Situações apropriadas

## QUANDO NÃO USAR
Situações a evitar

## PROCEDIMENTO
1. Passo 1
2. Passo 2
3. Passo 3

## CHECKLIST
- [ ] Item 1
- [ ] Item 2

## EXEMPLOS
Exemplo de uso
```

### Exemplo: Skill para Validar Resources
```yaml
---
type: skill
id: skill-validation
version: 1.0.0
depends: [skill-kos]
status: active
---
# SKILL: Validação de Resources

## OBJETIVO
Como validar Resources no KOS

## PROCEDIMENTO
1. Verifique type (deve ser válido)
2. Verifique id (único)
3. Verifique version (semver)
4. Verifique depends (todos existem)
5. Verifique status (draft, active, deprecated, archived)

## CHECKLIST
- [ ] Type válido
- [ ] ID único
- [ ] Version no formato X.Y.Z
- [ ] Dependências existem
- [ ] Status é válido
```

## Fluxo de Trabalho

### Ciclo de Desenvolvimento
1. **BOOT** - Inicia sessão
2. **LOAD** - Carrega projeto e status
3. **VALIDATE** - Verifica estrutura
4. **EXEC** - Executa tarefa (R2)
5. **COMMIT** - Persiste alterações
6. **EXIT** - Encerra sessão

### Atualizando o Estado
Durante `COMMIT`, você deve atualizar:
- `R1` - Última ação realizada
- `R2` - Próxima ação planejada
- `R3` - Arquivos modificados
- `R7` - Timestamp

### Classificando Novo Conhecimento
Durante `COMMIT`, o agente classifica automaticamente:
- Decisão → ADR
- Procedimento → Skill
- Erro → Incident
- Regra → Rule

## Exemplos Práticos

### Exemplo 1: Iniciar um Novo Projeto

**1. Crie o projeto Resource**
```bash
# RESOURCES/project-novo.md
---
type: project
id: project-novo
version: 0.1.0
depends: []
status: draft
---
# PROJETO: Novo Projeto
...
```

**2. Crie o status Resource**
```bash
# RESOURCES/status-novo.md
---
type: status
id: status-novo
version: 0.1.0
depends: [project-novo]
status: draft
---
# STATE REGISTERS
...
```

**3. Ative no STATE.md**
```bash
# KERNEL/STATE.md
ACTIVE_PROJECT: project-novo
ACTIVE_STATUS: status-novo
```

**4. Execute**
```bash
claude "Leia AGENTS.md e execute a tarefa"
```

### Exemplo 2: Adicionar uma Skill

**1. Crie a Skill**
```bash
# RESOURCES/skill-docker.md
---
type: skill
id: skill-docker
version: 1.0.0
depends: []
status: active
---
# SKILL: Docker
...
```

**2. Adicione ao projeto**
```bash
# RESOURCES/project-novo.md (atualizado)
---
type: project
id: project-novo
version: 0.1.1
depends: [skill-docker]
status: active
---
...
```

**3. Valide**
O próximo `VALIDATE` verificará se skill-docker existe.

### Exemplo 3: Registrar um Incidente

**1. Crie o Incident**
```bash
# RESOURCES/incident-001.md
---
type: incident
id: incident-001
version: 1.0.0
depends: [project-novo]
status: active
---
# INCIDENTE: Descrição

## PROBLEMA
O que aconteceu

## CAUSA RAIZ
Por que aconteceu

## CORREÇÃO
Como foi corrigido

## PREVENÇÃO
Como evitar no futuro
```

**2. Link ao projeto**
```bash
# RESOURCES/project-novo.md (atualizado)
depends: [skill-docker, incident-001]
```

### Exemplo 4: Registrar uma Decisão (ADR)

**1. Crie o ADR**
```bash
# RESOURCES/adr-001.md
---
type: adr
id: adr-001
version: 1.0.0
depends: [project-novo]
status: active
---
# ADR: Decisão

## PROBLEMA
O que precisávamos decidir

## DECISÃO
O que decidimos

## ALTERNATIVAS
O que consideramos

## CONSEQUÊNCIAS
Impacto da decisão
```

## Dicas e Boas Práticas

### Organização
- Use IDs descritivos: `project-api-core`, `skill-jwt`, `adr-014-cors`
- Mantenha versions em semver: `0.1.0`, `1.0.0`, `2.1.3`
- Atualize `version` em cada alteração

### Dependências
- Use `depends` apenas quando necessário
- Evite dependências circulares
- Skills podem depender de outras Skills

### Estado
- Atualize `STATUS.md` a cada `COMMIT`
- Mantenha `R6 [HEALTH] = OK` sempre que possível
- Registre blockers em `R4`

### Performance
- O Kernel é leve - mantenha-o imutável
- Resources podem crescer - divida Skills grandes
- Use `CACHE` para Resources opcionais em `PROGRAM.md`

## Resolução de Problemas

### VALIDATE falha
- Verifique o frontmatter YAML
- Confirme que todos os campos obrigatórios existem
- Verifique dependências (todos os IDs existem)

### LOAD falha
- Confirme que o Resource existe em RESOURCES/
- Verifique o ID no frontmatter
- Veja se o arquivo tem extensão `.md`

### EXEC falha
- Verifique R2 [NEXT_ACT] em STATUS.md
- Confirme que a tarefa é clara
- Skills devem estar carregadas

### COMMIT falha
- Verifique permissões de escrita
- Confirme que os Resources são válidos
- STATE.md deve ser acessível