# AEP SDK for Python

High-level Python SDK for the Agent Execution Protocol.

## Installation

```bash
pip install aep-sdk
```

## Quick Start

```python
from aep import AEPClient

client = AEPClient("path/to/kos")

# Boot the system
client.boot()

# Load a resource
client.load("project-cognix")

# Validate
result = client.validate("project-cognix")
print(result)  # {'status': 'OK', 'valid': True, ...}

# List resources
resources = client.list_resources()
print(resources)  # ['project-cognix', 'status-cognix', ...]
```

## API

### AEPClient(base_path)
Initialize client with KOS installation path.

### boot()
Initialize the system. Returns status dict.

### load(resource_id)
Load a resource by ID. Returns status dict.

### validate(resource_id)
Validate a resource structure. Returns validation result.

### list_resources()
List all available resources. Returns list of resource IDs.

### get_state()
Get current state registers. Returns state dict.