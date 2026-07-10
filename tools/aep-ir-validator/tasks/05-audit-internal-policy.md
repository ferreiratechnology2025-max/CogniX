# Task 05: Audit Internal Policy vs New Regulation

## Domain
Vigia Legal — Compliance Audit

## Description
Audit the client's internal data retention policy against the newly enacted Marco Legal da Segurança Cibernética (MLSC). Identify specific policy sections that need revision, assess the gap severity, and produce an action plan with recommended amendments.

## Expected Tools
- `read_policy(uri)` — Read internal policy document
- `read_regulation(uri)` — Read regulation text
- `compare_documents(policy_text, regulation_text, scope)` — Compare document pair
- `assess_gap_severity(gap)` — Rate gap severity (critical/high/medium/low)
- `generate_action_plan(gaps, recommendations)` — Produce remediation plan

## Expected Bindings
- `policy_document`: readonly, session, internal policy
- `regulation_text`: readonly, session, the MLSC regulation
- `gap_analysis`: mutable, execution, identified gaps
- `action_plan`: mutable, execution, remediation action plan

## Complexity
Medium-high — document comparison requires semantic understanding and severity judgment.
