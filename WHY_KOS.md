# Why KOS?

**Version:** 1.0.0  
**Status:** Active  

---

## The Problem

AI agents (Claude Code, Cursor, Aider, Gemini CLI) have a fundamental limitation:

> They don't share state between sessions.

Each time you start a new session, the agent has to rediscover:
- What project you're working on
- What was done before
- What needs to be done next
- What decisions were made
- What knowledge is relevant

### Symptoms
- **Wasted tokens**: Repeating the same context over and over
- **Inconsistent behavior**: Different agents, different results
- **Lost knowledge**: Insights disappear between sessions
- **Frustration**: Re-explaining the same things

### Root Cause
There is no standard way for agents to:
- Persist knowledge across sessions
- Share context between different agents
- Execute tasks deterministically

---

## The Solution

KOS defines a **protocol** that any AI agent can use to share state and execute tasks deterministically.

### How it works

1. **Resources** store knowledge (projects, status, skills, decisions, incidents)
2. **Opcodes** define operations (BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT)
3. **Programs** define execution flows
4. **State** persists between sessions via registers (R0-R7)

### Key Insight

> The problem isn't organization. The problem is **state persistence**.

KOS solves this by giving agents a shared memory that survives between sessions.

---

## Why Protocol, Not Framework?

| Framework | Protocol |
|-----------|----------|
| Dictates how | Defines what |
| Depends on implementation | Independent of implementation |
| Becomes outdated | Lasts longer |
| Forces a way of working | Allows flexibility |

A protocol is:
- More flexible
- More durable
- More portable

KOS is a protocol because:
- It works with any agent
- It works with any format
- It can be implemented in many ways

---

## Why Markdown?

- **Universal**: Any agent can read Markdown
- **Zero dependencies**: No libraries, no scripts
- **Versionable**: Works with Git
- **Human-readable**: People can understand it
- **Portable**: Works anywhere text works

---

## The Value Proposition

### For Developers
- Never re-explain context
- Consistent agent behavior
- Knowledge persists between sessions

### For Teams
- Shared context across team members
- Consistent execution across all agents
- Knowledge accumulates over time

### For AI Agents
- Deterministic execution envelope
- Persistent state
- Clear contracts

---

## What KOS Is

- ✅ A protocol
- ✅ A specification
- ✅ A contract between agents
- ✅ A way to persist knowledge
- ✅ A way to share state

## What KOS Is Not

- ❌ A tool
- ❌ A script
- ❌ A framework
- ❌ A platform
- ❌ A database

---

## Getting Started

1. Read `SPECIFICATION.md` for the full protocol
2. Read `CONFORMANCE.md` for agent requirements
3. Explore `RESOURCES/` for examples
4. Use `USAGE.md` for practical guidance
5. Run: `claude "Leia AGENTS.md e execute a tarefa"`

---

## FAQ

### Is KOS only for software projects?
No. KOS is domain-agnostic. It works for legal, marketing, research, or any domain where knowledge needs to persist.

### Do I need to install anything?
No. KOS is pure Markdown. Just clone the repository and start using it.

### Which agents can use KOS?
Any agent that can read files and follow instructions:
- Claude Code
- Cursor
- Aider
- Gemini CLI
- Codex CLI
- Any LLM with file access

### What if I already have a project?
You can migrate it to KOS:
1. Create the KOS structure
2. Add Resources for your project
3. Start using the protocol

### Does KOS replace Git?
No. KOS and Git work together:
- Git: history of changes
- KOS: current state of knowledge

### Is KOS a database?
No. KOS is a protocol for agents to share state. The implementation can be files (Markdown, JSON, YAML) or a database (SQLite, PostgreSQL, Neo4j). The protocol stays the same.

---

## The Vision

KOS aims to become a **standard protocol** for agent execution:

1. Any agent can use it
2. Any format can implement it
3. Any project can adopt it
4. Any team can benefit

---

## License

MIT — Use it freely, share it widely.