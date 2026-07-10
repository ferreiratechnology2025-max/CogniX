# AEP-0006: Simplified Execution Mode

**Status:** Stable
**Version:** 1.0.0
**Date:** 2026-07-05

---

## 1. Introdução

Para casos de uso que não exigem toda a complexidade do protocolo completo, o AEP define um modo simplificado com 3 opcodes essenciais.

## 2. Opcodes Essenciais

### LOAD
- Carrega um Resource e suas dependências
- Equivalente ao LOAD da ISA completa

### EXEC
- Executa a tarefa definida em R2 [NEXT_ACT]
- Equivalente ao EXEC da ISA completa

### COMMIT
- Persiste mudanças e classifica novo conhecimento
- Equivalente ao COMMIT da ISA completa

## 3. Opcodes Opcionais

BOOT, VALIDATE, EXIT são RECOMENDADOS mas não OBRIGATÓRIOS.

## 4. Uso

Agentes podem optar por:
- **Modo Completo:** Todos os 6 opcodes de núcleo
- **Modo Simplificado:** Apenas LOAD, EXEC, COMMIT

A escolha depende da complexidade do caso de uso.

## 5. Quando Usar o Modo Simplificado

- Sessões rápidas de consulta
- Agentes com contexto limitado
- Integrações simples
- Prototipagem rápida

## 6. Quando Usar o Modo Completo

- Sessões longas com múltiplas operações
- Validação estrita de Resources
- Auditoria e rastreabilidade
- Produção enterprise