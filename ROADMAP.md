# AEP Roadmap

## Visão

O AEP (Agent Execution Protocol) tem como visão se tornar o protocolo padrão para execução determinística de agentes de IA sobre conhecimento persistente.

## Fases

### Fase 1: Especificação (✅ Concluída)
- Definição do Core Protocol (AEP-0001)
- Resource Specification (AEP-0002)
- Kernel ISA (AEP-0003)
- Conformance Tests (AEP-0004)
- Resource Lifecycle (AEP-0005)

### Fase 2: Implementações (✅ Concluída)
- Implementação de referência (Markdown/KOS v6.0)
- Runtime independente (Python)
- Runtime independente (SQLite)
- Independência de formato demonstrada

### Fase 3: Ecossistema (✅ Concluída)
- Python SDK
- TypeScript SDK
- AEP Validator
- AEP Visualizer
- Integrações (Claude Code, Cursor)

### Fase 4: Validação Externa (🔄 Em Andamento)
- Implementação por terceiros
- Projetos reais em produção
- Feedback da comunidade

### Fase 5: Padronização (⏳ Futuro)
- Submissão como padrão aberto
- Ecossistema de implementações independentes
- Governança formalizada

## Estabilidade

### AEP v1.x
- **Status:** Estável
- **Mudanças:** Apenas correções editoriais e errata
- **Sem novos opcodes**
- **Sem quebras de compatibilidade**

### AEP v2.x (Experimental)
- **Status:** Futuro
- **Pode incluir:** Novos opcodes, mudanças no protocolo
- **Baseado em:** Evidências e feedback da v1.x

## Critérios para v2.0

Uma nova versão do protocolo só será considerada se:
1. Houver necessidade comprovada por casos reais
2. A mudança for implementada e testada
3. Existir pelo menos uma implementação independente
4. A comunidade concordar com a mudança