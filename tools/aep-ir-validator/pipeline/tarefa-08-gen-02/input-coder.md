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

# Task 08: Monitor ANPD (Data Protection Authority) Decisions

## Domain
Vigia Legal — Regulatory Intelligence

## Description
Monitor the Brazilian Data Protection Authority (ANPD) for new enforcement decisions published in the last 7 days. For each decision, extract the violation type, penalty amount, and mitigating/aggravating factors. Cross-reference against the client's current data processing activities to identify similar risk patterns. Generate a weekly intelligence brief.

## Expected Tools
- `fetch_anpd_decisions(date_from)` — Get recent ANPD decisions
- `extract_penalty_details(decision_text)` — Extract penalty metadata
- `match_risk_pattern(decision, dpia_report)` — Match decision to existing risks
- `assess_exposure(risk_score, client_revenue)` — Calculate financial exposure
- `generate_brief(decisions, risks, exposure)` — Produce intelligence brief

## Expected Bindings
- `anpd_db`: readonly, persistent, ANPD decisions database
- `client_dpia`: readonly, session, client DPIA report
- `risk_register`: mutable, session, accumulated risk assessments
- `intelligence_brief`: mutable, execution, the weekly brief

## Complexity
Medium — periodic batch with multi-document extraction and pattern matching.


---

**INSTRUCAO FINAL**: Retorne APENAS o JSON puro do plano (plan_header + nodes + edges).
NAO inclua checksum. NAo envolva em envelope. O checksum sera calculado externamente.