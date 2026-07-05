---
type: template
id: template-project
version: 1.0.0
depends: []
status: active
---
# TEMPLATE: Project Resource

## USO
Copie este template para criar um novo Project Resource.

## TEMPLATE
```markdown
---
type: project
id: project-[nome-do-projeto]
version: 0.1.0
depends: [skill-[skill-1], skill-[skill-2]]
status: draft
---
# PROJETO: [Nome do Projeto]

## OBJETIVO
[Descreva o objetivo do projeto]

## ESCOPO
[O que está dentro e fora do escopo]

## STACK
- [Tecnologia 1]
- [Tecnologia 2]
- [Tecnologia 3]

## REGRAS
1. [Regra 1]
2. [Regra 2]
3. [Regra 3]

## CHECKLIST INICIAL
- [ ] Estrutura base criada
- [ ] Kernel instalado
- [ ] Resources validados
- [ ] Fluxo testado
- [ ] Documentação do usuário final
```