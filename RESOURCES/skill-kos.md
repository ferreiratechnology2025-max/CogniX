---
type: skill
id: skill-kos
version: 1.0.0
depends: [skill-markdown]
status: active
---
# SKILL: Knowledge Operating System

## OBJETIVO
Fornecer o conhecimento necessário para operar o KOS v6.0.

## QUANDO USAR
- Ao iniciar um novo projeto com KOS
- Ao criar novos Resources
- Ao validar a estrutura do Kernel
- Ao ensinar outros agentes sobre o KOS

## QUANDO NÃO USAR
- Projetos que não utilizam Markdown
- Sistemas que exigem scripts ou ferramentas
- Ambientes sem suporte a Markdown

## PROCEDIMENTO
1. Verifique a estrutura do Kernel
2. Leia o protocolo de Resources em KERNEL/ISA.md
3. Crie Resources seguindo o protocolo
4. Valide a estrutura com VALIDATE
5. Atualize STATE.md com COMMIT

## CHECKLIST
- [ ] Kernel instalado
- [ ] Resources criados
- [ ] Estado inicial definido
- [ ] Fluxo testado
- [ ] Próximo passo identificado

## EXEMPLOS

### Criar um novo Project Resource
```markdown
---
type: project
id: project-exemplo
version: 0.1.0
depends: []
status: draft
---
# PROJETO: Exemplo
...
```

### Validar um Resource
LOAD project-exemplo
VALIDATE project-exemplo

### Atualizar Status
COMMIT status-exemplo