---
type: template
id: template-status
version: 1.0.1
depends: []
status: active
---
# TEMPLATE: Status Resource

## REGRAS
- R3 [MODIFIED] deve conter APENAS o delta da sessão atual
- NUNCA acumule histórico em R3
- Use Git para histórico, não R3

## USO
Copie este template para criar um novo Status Resource.

## TEMPLATE
```markdown
---
type: status
id: status-[nome-do-projeto]
version: 0.1.0
depends: [project-[nome-do-projeto]]
status: draft
---
# STATE REGISTERS — [Nome do Projeto]

R0 [SESSION] = [YYYY-MM-DD-HH-MM]
R1 [LAST_ACT] = [Última ação realizada]
R2 [NEXT_ACT] = [Próxima ação planejada]
R3 [MODIFIED] = [APENAS arquivos desta sessão]
R4 [BLOCKERS] = [Bloqueios atuais]
R5 [ACTIVE_SK] = [Skill ativa]
R6 [HEALTH] = OK
R7 [TIMESTAMP] = [YYYY-MM-DDTHH:MM:SSZ]
```