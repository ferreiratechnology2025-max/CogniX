# LLM Prompt Template: Generate AEP IR Execution Plan

Use this prompt to ask an LLM to generate an AEP IR (Intermediate Representation) Execution Plan for a given task.

---

You are an AEP IR Execution Planner. Your task is to generate a valid AEP-IR v1.0 Execution Plan for the given task description.

Output ONLY the `plan` object (plan_header + nodes + edges). Do NOT include a checksum field. Do NOT wrap the plan in an envelope. The checksum will be computed externally by the runtime.

## PlanHeader

```json
{
  "plan_header": {
    "ir_version": "1.0.0",
    "plan_id": "plan-<unique-id>",
    "declared_capabilities": ["capability_1", "capability_2", ...],
    "declared_bindings": [ ... ]
  }
}
```

## Binding Structure

```json
{
  "name": "binding_name",
  "type": "string | number | boolean | null | object | array",
  "mutability": "readonly | mutable",
  "scope": "execution | session | persistent",
  "capability": "required_capability",
  "default": null
}
```

## Node Structure

```json
{
  "id": "node-001",
  "type": "transformation | tool_call | mutation | sync",
  "effects": ["READ", "WRITE", "CALL_TOOL", "EMIT_EVENT", "YIELD"],
  "capabilities": ["capability_1"],
  "inputs": [{ "binding": "binding_name", "access": "read | write" }],
  "outputs": [{ "binding": "binding_name", "access": "read | write" }],
  "payload": { ... }
}
```

## Type-Effect Consistency Rules

| Node type       | Required effects | Prohibited effects |
|-----------------|------------------|--------------------|
| transformation  | —                | CALL_TOOL          |
| tool_call       | CALL_TOOL        | —                  |
| mutation        | WRITE            | —                  |
| sync            | (none)           | ALL                |

## Global Validation Rules

1. Graph must be a valid DAG (no cycles)
2. Every binding used by a node must be declared in PlanHeader
3. Every node must have a unique ID
4. Every node must declare its effects explicitly
5. Every node's inputs must have defined origins
6. Capability requirements must be satisfied by PlanHeader
7. Type restrictions must be satisfied
8. Mutable binding conflicts must be detectable

---

## Task

{task_description}

---

## Instructions

1. Analyze the task and decompose it into a DAG of nodes.
2. Identify all required Context Bindings and declare them in `plan_header.declared_bindings`.
3. For each node:
   - Assign a unique `id` (e.g., "node-001", "node-002")
   - Choose the correct `type` based on the operation
   - Declare appropriate `effects`
   - Declare required `capabilities`
   - Set `inputs` and `outputs` as BindingRefs
   - Populate `payload` with relevant parameters
4. Define `edges` to capture data dependencies between nodes.
5. Ensure all capabilities used across nodes are declared in `plan_header.declared_capabilities`.
6. Ensure the graph is acyclic.

## Important Rules

- Output ONLY the `plan` object — no checksum, no envelope.
- sync nodes MUST NOT have a payload.
- transformation nodes MUST NOT declare CALL_TOOL effect.
- tool_call nodes MUST declare CALL_TOOL effect.
- mutation nodes MUST declare WRITE effect.
- If a node has `access: "write"` on a binding, that binding must have `mutability: "mutable"`.

## Output Format

You MUST respond with ONLY the valid JSON object. No explanations, no markdown formatting:

```json
{
  "plan_header": {
    "ir_version": "1.0.0",
    "plan_id": "plan-monitor-legislation-001",
    "declared_capabilities": ["memory_rw", "tool_execution"],
    "declared_bindings": [
      {
        "name": "legislation_feed",
        "type": "object",
        "mutability": "readonly",
        "scope": "session",
        "capability": "memory_rw"
      },
      {
        "name": "analysis_result",
        "type": "object",
        "mutability": "mutable",
        "scope": "execution",
        "capability": "memory_rw",
        "default": {}
      }
    ]
  },
  "nodes": [
    {
      "id": "node-001",
      "type": "tool_call",
      "effects": ["CALL_TOOL", "READ", "WRITE"],
      "capabilities": ["tool_execution", "memory_rw"],
      "inputs": [{"binding": "legislation_feed", "access": "read"}],
      "outputs": [{"binding": "analysis_result", "access": "write"}],
      "payload": {"tool": "fetch_legislation", "params": {"topic": "data_privacy"}}
    }
  ],
  "edges": []
}
```


---

### TAREFA A SER EXECUTADA:

# Task 04: Review Court Ruling for Precedent Relevance

## Domain
Vigia Legal — Precedent Analysis

## Description
Analyze a newly published STJ (Superior Court of Justice) ruling on software taxation (ISS vs ICMS). Determine if it constitutes binding precedent (TEMA/REPETITIVO), identify which ongoing client cases it affects, and generate a legal memo assessing impact on pending litigation.

## Expected Tools
- `fetch_ruling(court, ruling_id)` — Fetch full ruling text from court database
- `classify_precedent(text)` — Determine precedent type (binding/persuasive/none)
- `search_affected_cases(taxonomy, jurisdiction)` — Find cases affected by the ruling
- `generate_memo(ruling, affected_cases, analysis)` — Produce legal memo

## Expected Bindings
- `court_db`: readonly, persistent, access to court rulings
- `client_cases_db`: readonly, persistent, active client litigation
- `precedent_assessment`: mutable, execution, precedent classification
- `memo_draft`: mutable, execution, the legal memo content

## Complexity
Medium — requires legal reasoning chain: read → classify → cross-reference → document.


---

**INSTRUCAO FINAL**: Retorne APENAS o JSON puro do plano (plan_header + nodes + edges).
NAO inclua checksum. NAo envolva em envelope. O checksum sera calculado externamente.