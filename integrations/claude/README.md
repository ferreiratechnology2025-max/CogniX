# Claude Code Integration for AEP

This integration allows Claude Code to execute AEP commands directly.

## Installation

Copy the `.claude/` directory to your project root.

## Usage

```
/aep boot
/aep load project-cognix
/aep validate project-cognix
/aep list
/aep status
```

## How It Works

The `/aep` command reads AEP files and executes the requested operation. It maintains state across sessions using the KERNEL/STATE.md file.