---
type: incident
id: incident-001-validate-failure
version: 1.0.0
depends: [project-cognix]
status: active
---
# INCIDENTE: Falha na Validação de Resources

## PROBLEMA
Durante a Fase 4 (Teste Completo), o opcode VALIDATE falhou quando um Resource não tinha o campo `depends` corretamente formatado.

## CAUSA RAIZ
O Resource `status-cognix` não tinha a dependência `project-cognix` explicitamente declarada. O agente precisava inferir a relação.

## CORREÇÃO
Corrigido adicionando `depends: [project-cognix]` ao frontmatter de `status-cognix.md`.

## PREVENÇÃO

### 1. Skill atualizada
`skill-kos.md` foi atualizada com checklist de validação que inclui verificação de `depends`.

### 2. Template criado
Foi criado `RESOURCES/template-status.md` com a dependência obrigatória.

### 3. Checklist de QA
Adicionado ao `project-cognix.md`:
```markdown
## CHECKLIST DE QA
- [ ] Todos os Resources têm type, id, version, depends, status
- [ ] depends contém apenas Resources existentes
- [ ] Relação de dependência é acíclica
```

## VACINA APLICADA
- [x] skill-kos.md atualizada com verificação de depends
- [x] template-status.md criado
- [x] project-cognix.md atualizado com checklist de QA

## SKILLS RELACIONADAS
- skill-kos (prevenção)
- skill-validation (nova skill proposta)