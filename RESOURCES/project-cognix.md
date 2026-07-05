---
type: project
id: project-cognix
version: 0.2.0
depends: [skill-markdown, skill-kos, skill-git]
status: active
---
# PROJETO: CogniX - Knowledge Operating System

## OBJETIVO
Construir um sistema de gerenciamento de conhecimento para agentes de IA baseado em Markdown puro.

## ESCOPO
- Kernel com ISA de 6 opcodes
- Protocolo universal de Resources
- Sistema de Skills extensível
- Integração com qualquer CLI de IA
- ADRs para decisões arquiteturais
- Incidentes com vacinas

## STACK
- Linguagem: Markdown
- Versionamento: Git
- Documentação: Auto-descritiva

## REGRAS
1. Nunca use scripts ou ferramentas externas
2. Todos os Resources devem seguir o protocolo
3. O Kernel deve ser imutável
4. Novos tipos de Resource podem ser criados via metadados

## RESOURCES DISPONÍVEIS
- **Projetos:** project-cognix
- **Status:** status-cognix
- **Skills:** skill-markdown, skill-git, skill-kos
- **ADRs:** adr-001-kernel-design
- **Incidentes:** incident-001-validate-failure
- **Templates:** template-project, template-status, template-skill

## CHECKLIST INICIAL
- [x] Estrutura base criada
- [x] Kernel instalado
- [x] Resources validados
- [x] Fluxo testado
- [x] Documentação do usuário final
- [x] ADRs e Incidentes criados
- [x] Templates disponíveis

## CHECKLIST DE QA
- [ ] Todos os Resources têm type, id, version, depends, status
- [ ] depends contém apenas Resources existentes
- [ ] Relação de dependência é acíclica
- [ ] Versões estão em SemVer
- [ ] Status é válido (draft, active, deprecated, archived)