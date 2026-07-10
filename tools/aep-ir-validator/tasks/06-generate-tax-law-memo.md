# Task 06: Generate Legal Memo on Tax Law Change

## Domain
Vigia Legal — Legal Research

## Description
A new tax reform bill (PLP 68/2026) modifies IBS (Imposto sobre Bens e Serviços) rates for technology services. Research the approved amendments, analyze the impact on the client's current tax structure (simples nacional vs lucro real), and generate a legal memo advising on optimal tax regime transition.

## Expected Tools
- `search_legislative_db(query)` — Search for bill amendments
- `read_document(uri)` — Read bill text
- `analyze_tax_impact(bill_text, client_profile)` — Analyze tax impact
- `compare_tax_regimes(options, criteria)` — Compare tax regimes
- `generate_memo(analysis, recommendation)` — Produce legal memo

## Expected Bindings
- `legislative_db`: readonly, persistent, bill database
- `client_tax_profile`: readonly, session, client tax information
- `impact_analysis`: mutable, execution, tax impact assessment
- `memo_draft`: mutable, execution, the final memo

## Complexity
High — requires deep tax domain knowledge and multi-criteria recommendation.
