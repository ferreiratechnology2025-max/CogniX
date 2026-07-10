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
