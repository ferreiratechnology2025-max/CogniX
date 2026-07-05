---
type: template
id: template-status
version: 1.0.0
depends: []
status: active
---
# TEMPLATE: Status Resource

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
R3 [MODIFIED] = [Arquivos modificados]
R4 [BLOCKERS] = [Bloqueios atuais]
R5 [ACTIVE_SK] = [Skill ativa]
R6 [HEALTH] = OK
R7 [TIMESTAMP] = [YYYY-MM-DDTHH:MM:SSZ]
```