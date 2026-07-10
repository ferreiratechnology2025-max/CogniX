# Task 01: Monitor New Data Privacy Legislation

## Domain
Vigia Legal — Regulatory Monitoring

## Description
Monitor the Brazilian Congress for new legislative proposals (PLs) related to data privacy and algorithmic accountability. Cross-reference each new proposal against the client's existing compliance framework (LGPD), flagging articles that conflict with current policies.

## Expected Tools
- `search_legislative_db(query, date_from)` — Search Congress database for proposals
- `read_document(uri)` — Read full text of a legislative proposal
- `cross_reference(text, framework)` — Compare article text against a compliance framework
- `flag_conflict(article_id, policy_id, reason)` — Register a compliance conflict

## Expected Bindings
- `legislation_db`: readonly, session, access to legislative search
- `compliance_framework`: readonly, persistent, the client's LGPD framework
- `flags_register`: mutable, session, accumulation of flagged conflicts
- `report_draft`: mutable, execution, draft of monitoring report

## Complexity
Medium — requires sequential read-analyze-flag pipeline across multiple proposals.
