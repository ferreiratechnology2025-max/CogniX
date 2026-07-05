# AEP SDK for TypeScript

High-level TypeScript SDK for the Agent Execution Protocol.

## Installation

```bash
npm install aep-sdk
```

## Quick Start

```typescript
import { AEPClient } from 'aep-sdk';

const client = new AEPClient('path/to/kos');

// Boot the system
client.boot();

// Load a resource
client.load('project-cognix');

// Validate
const result = client.validate('project-cognix');
console.log(result);  // { status: 'OK', valid: true, ... }

// List resources
const resources = client.listResources();
console.log(resources);  // ['project-cognix', 'status-cognix', ...]
```

## API

### AEPClient(basePath?)
Initialize client with KOS installation path.

### boot(): AEPResult
Initialize the system.

### load(resourceId): AEPResult
Load a resource by ID.

### validate(resourceId): AEPResult
Validate a resource structure.

### listResources(): string[]
List all available resources.

### getState(): State
Get current state registers.