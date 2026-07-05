# AEP-0007: Compliance Profiles

**Status:** Stable
**Version:** 1.0.0
**Date:** 2026-07-05

---

## 1. Introdução

O AEP define dois perfis de conformidade para atender diferentes necessidades de implementação.

## 2. AEP Lite Profile

### 2.1 Descrição
Perfil mínimo para agentes com restrição de recursos.

### 2.2 Opcodes Obrigatórios
- `LOAD` — Carrega Resource
- `EXEC` — Executa tarefa
- `COMMIT` — Persiste mudanças

### 2.3 Opcodes Opcionais
- `BOOT` — Não obrigatório
- `VALIDATE` — Não obrigatório
- `EXIT` — Não obrigatório

### 2.4 Casos de Uso
- Agentes de borda (edge)
- Micro-automações
- Ambientes com restrição de memória
- Prototipagem rápida

### 2.5 Exigências
- Pelo menos 1 implementação
- Conformidade com AEP-0001 (Core)
- Suporte a Resources

## 3. AEP Extended Profile

### 3.1 Descrição
Perfil completo para sistemas enterprise.

### 3.2 Opcodes Obrigatórios
- `LOAD` — Carrega Resource
- `VALIDATE` — Valida estrutura
- `EXEC` — Executa tarefa
- `COMMIT` — Persiste mudanças
- `EXIT` — Encerra sessão

### 3.3 Opcodes Opcionais
- `BOOT` — Recomendado

### 3.4 Casos de Uso
- Sistemas corporativos
- Ambientes multi-agente
- Auditoria rigorosa
- Produção enterprise

### 3.5 Exigências
- Conformidade com AEP-0001 a AEP-0005
- Suíte de conformidade completa
- Validação de Resources obrigatória

## 4. Seleção de Perfil

| Critério | Lite | Extended |
|----------|------|----------|
| Opcodes | 3 | 5+ |
| Validação | Opcional | Obrigatória |
| Auditoria | Básica | Completa |
| Complexidade | Baixa | Alta |
| Uso recomendado | Prototipagem | Produção |

## 5. Declaração de Conformidade

Implementações devem declarar seu perfil:

```yaml
---
type: project
id: my-implementation
version: 1.0.0
profile: lite  # ou extended
status: active
---
```