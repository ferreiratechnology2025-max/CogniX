# Task 10: Verify Software Licensing Compliance

## Domain
Vigia Legal — License Audit

## Description
Perform a compliance audit of the client's open-source software dependencies (1,247 packages from SBOM). Identify any packages with license types incompatible with the client's commercial distribution model (GPL-3.0 → AGPL-3.0 risk). For each incompatible license, determine if the usage pattern triggers the copyleft provision (linking vs aggregation). Generate a compliance report with remediation steps.

## Expected Tools
- `parse_sbom(uri)` — Parse Software Bill of Materials
- `classify_license(license_id)` — Classify license type (permissive/copyleft/proprietary)
- `analyze_usage_pattern(package_id, sbom)` — Determine how a package is used (linked/aggregated)
- `check_copyleft_trigger(usage_pattern, license_type)` — Assess if copyleft is triggered
- `generate_report(packages, risks, remediation)` — Produce compliance report

## Expected Bindings
- `sbom_document`: readonly, session, the SBOM JSON
- `license_db`: readonly, persistent, SPDX license classification data
- `risk_assessment`: mutable, session, identified license risks
- `compliance_report`: mutable, execution, final report

## Complexity
Very high — large dataset (1,247 packages), complex legal distinctions (linking vs aggregation), requires parallel processing.
