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
