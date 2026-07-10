# Task 02: Analyze Contract for Liability Clauses

## Domain
Vigia Legal — Contract Analysis

## Description
Review a software licensing agreement (SLA) for liability limitation clauses. Identify any clause that caps liability below the industry standard (3x contract value), flag indemnification gaps, and assess whether the governing law clause creates jurisdictional risk.

## Expected Tools
- `parse_contract(uri)` — Parse contract into clause-level sections
- `classify_clause(text, taxonomy)` — Classify a clause by legal category
- `assess_risk(clause_text, threshold)` — Assess risk level for a clause
- `generate_report(analyses)` — Produce structured risk report

## Expected Bindings
- `contract_document`: readonly, session, the contract text
- `risk_thresholds`: readonly, persistent, risk assessment parameters
- `analysis_results`: mutable, execution, per-clause analysis data
- `report_draft`: mutable, execution, the final report

## Complexity
Medium — single document, multi-clause parallel analysis with aggregation.
