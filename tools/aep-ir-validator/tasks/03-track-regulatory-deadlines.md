# Task 03: Track Regulatory Compliance Deadlines

## Domain
Vigia Legal — Compliance Calendar

## Description
Track all upcoming regulatory deadlines for a portfolio of 5 client companies across 3 jurisdictions (BR, EU, US). For each deadline, verify current compliance status, calculate preparation lead time, and escalate any deadline within 30 days that has <50% preparation progress.

## Expected Tools
- `query_deadline_db(portfolio_id)` — Get all deadlines for a portfolio
- `check_compliance_status(company_id, regulation_id)` — Get current compliance status
- `calculate_lead_time(deadline_date, current_date)` — Calculate preparation lead time
- `escalate(deadline_id, reason, priority)` — Escalate an overdue deadline
- `send_notification(recipient, message)` — Send escalation notification

## Expected Bindings
- `portfolio_db`: readonly, persistent, company portfolio
- `deadlines`: mutable, session, fetched deadlines cache
- `escalations`: mutable, session, escalation records
- `notification_queue`: mutable, execution, pending notifications

## Complexity
High — multi-company, multi-jurisdiction, with conditional escalation logic.
