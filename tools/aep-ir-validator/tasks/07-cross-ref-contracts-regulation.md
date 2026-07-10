# Task 07: Cross-Reference Client Contracts with New Regulation

## Domain
Vigia Legal — Contract Portfolio Review

## Description
Cross-reference all active client service agreements (47 contracts) against the new LGPD fine calculation methodology (ANPD Resolution CD/ANPD No. 12/2026). Identify contracts whose liability/indemnification clauses need revision to reflect the new penalty framework. Prioritize contracts by revenue exposure.

## Expected Tools
- `list_contracts(client_id, status)` — List all active contracts
- `read_contract(contract_id)` — Read contract text
- `extract_clause(contract_text, clause_type)` — Extract specific clause types
- `compare_against_regulation(clause_text, regulation_text)` — Compare clause vs regulation
- `prioritize_by_risk(contracts, criteria)` — Prioritize by revenue exposure
- `generate_amendment_schedule(contracts, priority)` — Produce amendment plan

## Expected Bindings
- `contracts_db`: readonly, persistent, client contract repository
- `regulation_text`: readonly, session, ANPD resolution text
- `affected_contracts`: mutable, execution, identified contracts needing revision
- `amendment_plan`: mutable, execution, prioritized amendment schedule

## Complexity
High — large batch processing (47 documents) with cross-referencing and prioritization.
