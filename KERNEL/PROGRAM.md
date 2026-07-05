# PROGRAMA: Padrão — KOS v6.0

## FLUXO
BOOT
LOAD [ACTIVE_PROJECT]
LOAD [ACTIVE_STATUS]
VALIDATE [ACTIVE_PROJECT]
VALIDATE [ACTIVE_STATUS]
EXEC
COMMIT
  ├── Atualiza R0-R7
  ├── Limpa R3 (apenas arquivos desta sessão)
  └── Persiste alterações
EXIT

## OBSERVAÇÕES
- [ACTIVE_PROJECT] é obtido de KERNEL/STATE.md
- [ACTIVE_STATUS] é obtido de KERNEL/STATE.md
- Se não houver projeto ativo, EXEC deve solicitar definição
- R3 [MODIFIED] NUNCA acumula histórico - apenas delta da sessão