---
type: rule
id: rule-r3-lifecycle
version: 1.0.0
depends: [project-cognix]
status: active
---
# REGRA: Ciclo de Vida do R3 [MODIFIED]

## DEFINIÇÃO
R3 [MODIFIED] deve conter APENAS os arquivos modificados na sessão atual.

## FUNÇÃO
- Rastrear o delta da sessão
- Permitir que o agente saiba exatamente o que mudou
- Servir como entrada para o COMMIT

## COMPORTAMENTO ESPERADO

### Durante EXEC
- R3 é preenchido com os arquivos modificados
- Exemplo: `R3 [MODIFIED] = RESOURCES/status-cognix.md`

### Durante COMMIT
- R3 é usado para persistir alterações
- **R3 é limpo e substituído pelo delta da sessão**
- Exemplo: `R3 [MODIFIED] = RESOURCES/status-cognix.md` (não acumula)

### Após EXIT
- R3 contém apenas os arquivos da última sessão
- Não há histórico acumulado

## VIOLAÇÃO
Se R3 acumular arquivos de múltiplas sessões, é uma violação do design.

**Exemplo de violação:**
```yaml
R3 [MODIFIED] = KERNEL/STATE.md, RESOURCES/report-test.md, RESOURCES/status-cognix.md, RESOURCES/skill-git.md
```

**Correção:**
1. Limpar R3 manualmente
2. Atualizar apenas o delta da sessão atual

## RAZÃO
O KOS é um microkernel. Estado deve ser mínimo e atual. Histórico não pertence ao estado, pertence ao Git.