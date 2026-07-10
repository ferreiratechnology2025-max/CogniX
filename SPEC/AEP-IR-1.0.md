# AEP Intermediate Representation Specification v1.0

**Status:** Draft  
**Version:** 1.0.0  
**Date:** 2026-07-07  
**Classification:** Normative Specification

This document defines the Intermediate Representation (IR) for the Agent Execution Protocol (AEP). The IR is the canonical form between the LLM-generated Execution Plan and the compiled artifact consumed by the runtime.

---

## §1. Scope

This specification defines the Intermediate Representation (IR) for the Agent Execution Protocol (AEP). It covers the computational model, Context Bindings, type system, capabilities and effects, canonicalization, validation, and the contracts between the compiler and the runtime. It also establishes the conformance requirements for AEP-compliant implementations.

All implementations of AEP-compliant runtimes MUST adhere to this specification.

---

## §2. Computational Model

### §2.1. Execution Graph

- **Node:** unidade mínima de execução (transformação, chamada de ferramenta, mutação de estado, sincronização)
- **Edge:** dependência de dados entre nodes
- O grafo DEVE ser um DAG (Directed Acyclic Graph)

### §2.2. Execution Semantics

Dois nodes podem ser executados em qualquer ordem (incluindo em paralelo) **se e somente se**:
1. Não existe caminho de dependência entre eles no DAG **E**
2. Não acessam o mesmo Context Binding mutável com pelo menos um WRITE

Definição de conflito:
- Ambos WRITE no mesmo binding mutável
- Um WRITE e outro READ no mesmo binding mutável (independente da ordem)

**Invariante:** A ordem de execução de nodes não-conflitantes NÃO DEVE afetar o estado final de nenhum Context Binding.

### §2.3. Node Structure

```
Node {
  id: string (REQUIRED, unique within the plan)
  type: transformation | tool_call | mutation | sync (REQUIRED)
  effects: Effect[] (REQUIRED)
  capabilities: Capability[] (REQUIRED)
  inputs: BindingRef[] (REQUIRED)
  outputs: BindingRef[] (REQUIRED)
  payload: object (OPTIONAL, typed by node type; sync nodes MUST NOT have payload)
}
```

### §2.4. BindingRef Structure

```
BindingRef {
  binding: string (REQUIRED, name of a binding declared in PlanHeader)
  access: read | write (REQUIRED)
}
```

**Regra de validação cruzada:** Se `access: write`, então:
- O binding referenciado DEVE ter `mutability: mutable`
- O node DEVE declarar effect `WRITE`
- O PlanHeader DEVE declarar a capability correspondente

---

## §3. Context Bindings

```
Binding {
  name: string (REQUIRED)
  type: Type (REQUIRED)
  mutability: readonly | mutable (REQUIRED, default: readonly)
  scope: execution | session | persistent (REQUIRED, default: execution)
  capability: Capability (REQUIRED)
  default: optional<Value>
}
```

**Semântica de scope:**
- **execution:** existe apenas durante a execução do plano atual
- **session:** persiste entre execuções de planos na mesma sessão
- **persistent:** sobrevive entre sessões (requer armazenamento explícito)

**Regras de mutabilidade:**
- **readonly:** não pode ser modificado por nenhum node
- **mutable:** pode ser modificado por nodes que declaram effect WRITE

---

## §4. Type System

### §4.1. Primitive Types

- `string`: texto codificado em UTF-8
- `number`: IEEE 754 double-precision floating point
- `boolean`: true | false
- `null`: ausência de valor

### §4.2. Structured Types

- `object`: mapa chave-valor com chaves string
- `array`: lista ordenada de valores

### §4.3. Type Compatibility

Um valor de tipo T1 é compatível com tipo T2 se:
- T1 == T2
- T1 é `null` e T2 permite null
- T1 é um subtipo de T2 (ex: estrutura de objeto específica)

Incompatibilidades de tipo DEVEM causar falha de validação antes da compilação.

---

## §5. Capabilities and Effects

### §5.1. Capabilities

Capabilities representam **permissões de acesso a recursos**. Respondem: "O que este plano pode acessar?"

Exemplos:
- `identity`: acesso à identidade do usuário
- `memory_rw`: leitura/escrita em memória
- `tool_execution`: permissão para chamar ferramentas externas
- `event_emission`: permissão para emitir eventos

### §5.2. Effects

Effects representam **intenções operacionais**. Respondem: "O que esta operação faz?"

Effects definidos:
- `READ`: leitura de binding ou fonte externa
- `WRITE`: modificação de binding mutável
- `CALL_TOOL`: invocação de ferramenta externa
- `EMIT_EVENT`: produção de evento externo
- `YIELD`: suspensão de execução e requisição de mais ciclos

### §5.3. Separation Rule

Todo node DEVE declarar:
- Quais **capabilities** requer (autorização)
- Quais **effects** produz (comportamento)

O validador DEVE verificar que todas as capabilities requeridas estão declaradas no PlanHeader.

### §5.4. Plan Header

```
PlanHeader {
  ir_version: string (REQUIRED; runtime MUST reject unknown major versions)
  plan_id: string (REQUIRED, unique identifier)
  declared_capabilities: Capability[] (REQUIRED)
  declared_bindings: Binding[] (REQUIRED)
}
```

**NOTA:** Não incluir campo checksum aqui — checksum vive no envelope externo.

---

## §6. Canonical Representation

### §6.1. Canonicalization Standard

A representação canônica do plano DEVE seguir **RFC 8785 (JSON Canonical Scheme — JCS)**.

Requisitos:
- Chaves ordenadas lexicograficamente
- Números sem trailing zeros
- UTF-8 sem BOM
- Sem espaços em branco desnecessários

### §6.2. Compiled Artifact Envelope

Estrutura do artefato compilado:

```json
{
  "plan": { ... canonicalized plan ... },
  "checksum": "sha256-hex-string"
}
```

O checksum é SHA256 do campo `plan` canonicalizado. O plan NÃO contém checksum de si mesmo.

---

## §7. Determinism and Validation

### §7.1. Structural Determinism

IRs idênticas DEVEM produzir representações canônicas idênticas e checksums idênticos.

### §7.2. Execution Determinism

Determinismo de execução **NÃO é garantido** para nodes com effects `CALL_TOOL` ou `EMIT_EVENT` (efeitos externos são inerentemente não-determinísticos).

### §7.3. Type-Effect Consistency Table

| Node type | Effects obrigatórios | Effects proibidos |
|---|---|---|
| transformation | — | CALL_TOOL |
| tool_call | CALL_TOOL | — |
| mutation | WRITE | — |
| sync | (nenhum) | todos |

O validador DEVE aplicar esta tabela de consistência.

### §7.4. Validation Rules

Invariantes globais:

1. O grafo DEVE ser acíclico (DAG válido)
2. Todo binding utilizado DEVE estar declarado
3. Todo node DEVE ter identificador único
4. Todo node DEVE declarar seus effects explicitamente
5. Toda entrada de node DEVE ter origem definida
6. Requirements de capability DEVEM ser satisfeitos
7. Restrições de tipo DEVEM ser satisfeitas
8. Conflitos de binding mutável DEVEM ser detectáveis

Violação de qualquer invariante DEVE causar falha de validação.

### §7.5. Origin Rules

A binding is considered to have a **defined origin** if and only if at least one of the following conditions holds:

1. **Producer**: At least one node in the plan declares a `BindingRef` with `access: write` targeting this binding (i.e., some node produces output to it).
2. **Default value**: The binding declaration in `PlanHeader.declared_bindings` includes a non-null `default` field.
3. **External scope**: The binding has `scope: session` or `scope: persistent`, which implies the value originates from the execution environment or persistent storage outside the current plan.

Bindings with `scope: execution` that have no producer and no default value MUST cause validation failure under rule OR-1.

**Rationale**: Session-scoped and persistent-scoped bindings exist independently of any single plan execution. Their origin is the runtime environment (session state or persistent storage), not the plan itself. This rule prevents false positives when validating plans that consume pre-existing state.

---

## §8. Compiler Contract

O compilador DEVE:
1. Aceitar apenas IRs validadas
2. Produzir representação canônica conforme RFC 8785
3. Calcular checksum SHA256 do plan canonicalizado
4. Gerar envelope com plan + checksum
5. Produzir artefato estático e imutável

O compilador NÃO DEVE:
- Modificar a semântica da IR
- Introduzir não-determinismo
- Permitir execução de planos inválidos

---

## §9. Runtime Contract

O runtime DEVE:
1. Desserializar o artefato compilado
2. Verificar o checksum (SHA256 do plan)
3. Verificar `ir_version` (rejeitar major version desconhecida)
4. Executar nodes conforme dependências do DAG
5. Respeitar a semântica de execução (§2.2)
6. Manter Context Bindings conforme scope e mutabilidade

O runtime NÃO DEVE:
- Modificar o plano compilado
- Executar nodes em ordem que viole dependências
- Permitir acesso a bindings sem capabilities adequadas

O runtime PODE:
- Implementar bindings usando qualquer mecanismo interno (registradores, variáveis, memória, armazenamento persistente)
- Otimizar ordem de execução para nodes não-conflitantes
- Executar nodes em paralelo quando seguro

---

## §10. IR to ISA Mapping

ISA permanece com 7 opcodes. Mapeamento:

| IR Node Type | ISA Opcode | Notes |
|---|---|---|
| transformation | EXEC | effects variados |
| tool_call | EXEC + effect CALL_TOOL | chamada de ferramenta externa |
| mutation | EXEC + effect WRITE | mutação de binding |
| sync | NENHUM | barrier resolvido pelo scheduler na travessia do DAG; não consome budget do watchdog |

YIELD é opcode do agente para pedir ciclos ao watchdog. Effect `YIELD` aparece apenas em nodes que explicitamente pedem budget adicional (ex: tool_call complexo).

---

## §11. Conformance Requirements

Uma implementação é **AEP-IR 1.0 conformant** se:
1. Aceita todos os planos válidos (planos que passam validação)
2. Rejeita todos os planos inválidos (planos que falham validação)
3. Produz representação canônica determinística
4. Preserva todos os invariantes globais durante execução
5. Aplica declarações de capability e effect
6. Mantém semântica de scope e mutabilidade dos bindings

Conformidade é binária: uma implementação ou é conforme ou não é. Conformidade parcial não é definida na v1.0.

---

## §12. References

- AEP-0001: Core Protocol
- AEP-0002: Resource Specification
- AEP-0003: Kernel ISA
- RFC 8785: JSON Canonical Scheme (JCS)

---

### §13. Change Log

```
- 2026-07-07: Initial draft (v1.0.0)
```
