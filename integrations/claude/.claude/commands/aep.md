# AEP Command

Execute AEP operations.

## Usage

```
/aep <command> [args]
```

## Commands

- `boot` - Initialize AEP system
- `load <resource>` - Load a resource
- `validate <resource>` - Validate a resource
- `list` - List all resources
- `status` - Show current state

## Examples

```
/aep boot
/aep load project-cognix
/aep validate project-cognix
/aep list
/aep status
```

## Implementation

When this command is invoked:

1. Read KERNEL/STATE.md for current state
2. Read KERNEL/PROGRAM.md for execution flow
3. Execute the requested command
4. Update state registers as needed