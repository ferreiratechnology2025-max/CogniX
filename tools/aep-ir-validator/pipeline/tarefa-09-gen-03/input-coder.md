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

# Task 09: Assess Patent Infringement Litigation Risk

## Domain
Vigia Legal — IP Litigation Risk

## Description
A competitor has filed a patent infringement lawsuit against the client regarding algorithmic recommendation technology. Analyze the patent claims, map them against the client's product architecture, assess validity of the patent (prior art search), estimate legal exposure, and recommend litigation strategy (settle, defend, or countersue).

## Expected Tools
- `read_patent(uri)` — Read patent document
- `analyze_claims(patent_text)` — Extract and classify patent claims
- `map_product_architecture(client_id)` — Get client product technical specs
- `search_prior_art(claims, databases)` — Search for prior art
- `estimate_exposure(claims, revenue_data)` — Estimate financial exposure
- `recommend_strategy(validity, exposure, costs)` — Produce litigation recommendation

## Expected Bindings
- `patent_document`: readonly, session, the patent in question
- `product_db`: readonly, persistent, client product architecture
- `prior_art_results`: mutable, session, prior art search cache
- `exposure_assessment`: mutable, execution, financial exposure estimate
- `strategy_recommendation`: mutable, execution, recommended course of action

## Complexity
High — multi-step legal-technical analysis with significant domain expertise required.


---

**INSTRUCAO FINAL**: Retorne APENAS o JSON puro do plano (plan_header + nodes + edges).
NAO inclua checksum. NAo envolva em envelope. O checksum sera calculado externamente.