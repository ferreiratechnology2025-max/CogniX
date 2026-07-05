---
type: adr
id: adr-001-kernel-design
version: 1.0.0
depends: [project-cognix]
status: active
---
# ADR-001: Design do Microkernel KOS

## CONTEXTO
Precisávamos definir a arquitetura do KOS para maximizar portabilidade e minimizar dependências.

## PROBLEMA
Como criar um sistema de gerenciamento de conhecimento para agentes de IA que seja:
- Independente de ferramenta (Claude, Cursor, Aider)
- Zero dependências
- Extensível por usuários
- Determinístico

## DECISÃO
Adotar um modelo de microkernel com:
- ISA de 6 opcodes (BOOT, LOAD, VALIDATE, EXEC, COMMIT, EXIT)
- Protocolo universal de Resources (type, id, version, depends, status)
- Estado gerenciado via registradores (R0-R7)
- Kernel imutável, programas mutáveis

## ALTERNATIVAS CONSIDERADAS

### 1. Framework com scripts (Rejeitado)
- **Prós:** Automatização
- **Contras:** Quebra portabilidade, exige ferramentas

### 2. Sistema de diretórios semânticos (Rejeitado)
- **Prós:** Organização para humanos
- **Contras:** Kernel precisa conhecer tipos específicos

### 3. Banco de dados (Rejeitado)
- **Prós:** Consultas estruturadas
- **Contras:** Dependência externa, complexidade

## CONSEQUÊNCIAS

### Positivas
- ✅ Portabilidade total (apenas Markdown)
- ✅ Extensibilidade (novos tipos sem mudar Kernel)
- ✅ Baixo consumo de contexto
- ✅ Determinístico (fluxo claro)

### Negativas
- ⚠️ Agente precisa interpretar opcodes
- ⚠️ Validação semântica depende do agente

## SKILLS AFETADAS
- skill-kos (atualizada com a decisão)
- skill-markdown (protocolo de Resources)

## STATUS
Ativo. Esta decisão fundamenta todo o KOS.