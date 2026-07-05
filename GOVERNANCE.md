# AEP Governance

## Princípios

1. **Protocolo sobre Implementação** — A especificação é o produto
2. **Evidência sobre Opinião** — Mudanças baseadas em dados
3. **Consenso sobre Votação** — Decisões por consenso técnico

## Estrutura de Decisão

### Comitê Técnico
- Responsável por revisar propostas
- Avaliar impactos de mudanças
- Garantir conformidade com os princípios

### Processo de Mudança

#### 1. Proposta (AEPR)
Qualquer pessoa pode submeter uma proposta de mudança.

**Formato:**
```
AEPR-XXX: Título
Status: Draft | Review | Approved | Rejected
Author: [Nome]
Date: [Data]
```

#### 2. Discussão
- Mínimo de 2 semanas para discussão
- Feedback da comunidade
- Análise de impacto

#### 3. Implementação
- Mudança na especificação
- Implementação de referência
- Atualização dos testes de conformidade

#### 4. Validação
- Pelo menos uma implementação independente
- Testes de conformidade passando
- Documentação atualizada

#### 5. Aprovação
- Consenso do comitê técnico
- Documentação finalizada

## Tipos de Mudança

### Errata
- Correções de erros de digitação
- Esclarecimentos semânticos
- Sem impacto no protocolo

### Patch
- Correções de bugs na especificação
- Sem alteração de contratos

### Minor
- Adição de novos tipos de Resource
- Adição de novos campos opcionais
- Compatível com versões anteriores

### Major (Breaking)
- Novos opcodes
- Mudanças em contratos existentes
- Quebra de compatibilidade

## Depreciação

Resources podem ser depreciados seguindo o processo:

1. Marcar como `deprecated` no status
2. Adicionar aviso na documentação
3. Manter por pelo menos 6 meses
4. Remover apenas em versão major

## Versionamento

- **1.0.0** → Primeira versão estável
- **1.x.x** → Patches e minors compatíveis
- **2.0.0** → Breaking changes