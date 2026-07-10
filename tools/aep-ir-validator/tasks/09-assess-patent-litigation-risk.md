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
