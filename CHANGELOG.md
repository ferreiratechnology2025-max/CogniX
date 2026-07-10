# Changelog

## [1.1.0] - 2026-07-06

### Added
- AEP-0006 (Simplified Execution Mode): Modo de execução simplificado para edge agents
- AEP-0007 (Compliance Profiles): Perfis de conformidade (Lite, Extended)
- AEP-0008 (Fault Tolerance): Watchdog Timer, transações atômicas de validação, ROLLBACK→R4
- Opcode YIELD: Permite agentes solicitarem ciclos adicionais ao watchdog
- Conformance Suite: 9 normative test cases, executed against 2 runtimes (18 executions)
- Compliance Kit: validação estrutural de definições de teste (não executa implementações; conformidade de runtime via suíte normativa + pytest)

### Changed
- R1 [WATCHDOG]: Agora extensível via instrução YIELD (antes fixo)

### Deprecated
Nenhum

### Removed
Nenhum

### Fixed
Nenhum

### Security
Nenhuma vulnerabilidade conhecida

## [1.0.0] - 2026-07-05

### Added
- **Core Protocol (AEP-0001)**: Especificação do protocolo base
- **Resource Specification (AEP-0002)**: Formato universal de Resources
- **Kernel ISA (AEP-0003)**: 6 opcodes (BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT)
- **Conformance Tests (AEP-0004)**: Suíte normativa de testes
- **Resource Lifecycle (AEP-0005)**: Ciclo de vida dos Resources
- **Implementação de referência**: KOS v6.0 (Markdown)
- **Runtime Python**: Implementação independente
- **Runtime SQLite**: Implementação com independência de formato
- **Conformance Suite**: 9 testes normativos
- **Python SDK**: Cliente AEP para Python
- **TypeScript SDK**: Cliente AEP para TypeScript
- **AEP Validator**: Ferramenta de validação de Resources
- **AEP Visualizer**: Visualização de grafos de dependência
- **Integrações**: Claude Code e Cursor
- **Governança**: ROADMAP.md, GOVERNANCE.md, SECURITY.md

### Changed
- **R3 [MODIFIED]**: Agora contém apenas o delta da sessão (não histórico)
- **Error Handling**: Formato padronizado (ERROR: EXXX: mensagem)

### Deprecated
- Nenhum

### Removed
- Nenhum

### Fixed
- TC-009: Alinhamento de formato de erro entre runtimes
- R3: Ciclo de vida corrigido para evitar acúmulo de histórico

### Security
- Nenhuma vulnerabilidade conhecida

## [0.x.x] - Pré-lançamento

### 0.6.0 - 2026-07-04
- Estrutura base do KOS v6.0
- Primeiros Resources (project, status, skills)
- Documentação inicial (README, USAGE, CONTRIBUTING)

### 0.1.0 - 2026-07-03
- Inicialização do projeto
- Conceito inicial do microkernel