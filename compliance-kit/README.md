# AEP Compliance Kit v1.1.0

## Purpose

The Compliance Kit validates whether an implementation correctly follows the AEP specification. It provides an automated test suite and report generation.

## Structure

```
compliance-kit/
├── tests/                  # Test definitions (YAML)
│   ├── 001-boot.yaml
│   ├── 002-load.yaml
│   ├── 003-validate.yaml
│   ├── 004-exec.yaml
│   ├── 005-commit.yaml
│   ├── 006-exit.yaml
│   ├── 007-complete.yaml
│   ├── 008-dependencies.yaml
│   ├── 009-error-handling.yaml
│   ├── 010-yield.yaml
│   └── 011-rollback.yaml
├── vectors/                # Test data
│   ├── valid-resource.md
│   ├── invalid-resource.md
│   └── state-template.md
├── runner/                 # Test runner
│   ├── runner.py
│   └── requirements.txt
├── expected/
│   └── snapshots/
└── report/
    └── template.json
```

## Usage

```bash
# Install dependencies
pip install -r runner/requirements.txt

# Run all compliance tests
python runner/runner.py --implementation /path/to/runtime

# Generate report
python runner/runner.py --implementation /path/to/runtime --report

# Run specific test
python runner/runner.py --implementation /path/to/runtime --test 010-yield
```

## Expected Output

```
AEP Compliance Kit v1.1.0
Implementation: /path/to/runtime
Tests: 11/11 passed
Status: CONFORMANT
```

## Test Coverage

| Test ID | Name | Validates |
|---------|------|-----------|
| TC-001 | BOOT | System initialization, session creation |
| TC-002 | LOAD | Resource loading, missing resource handling |
| TC-003 | VALIDATE | Schema validation, error detection |
| TC-004 | EXEC | Task execution, R2 reading |
| TC-005 | COMMIT | State persistence, R3 delta |
| TC-006 | EXIT | Session termination, health check |
| TC-007 | COMPLETE | Full program execution |
| TC-008 | DEPENDENCIES | Dependency resolution |
| TC-009 | ERROR-HANDLING | Structured error output (R4) |
| TC-010 | YIELD | Watchdog extension |
| TC-011 | ROLLBACK | ACID rollback on failure |

## Adding a New Implementation

1. Implement the AEP specification
2. Run the compliance kit: `python runner/runner.py --implementation /path`
3. Ensure all 11 tests pass
4. Submit results with your implementation

## Compliance Badge

```markdown
[![AEP Conformant v1.1.0](https://img.shields.io/badge/AEP-Conformant%20v1.1.0-brightgreen)]()
```
