# AEP Benchmark Methodology v1.0.0

## Visão Geral

Este documento descreve a metodologia utilizada no benchmark comparativo entre AEP e RAG (Retrieval-Augmented Generation).

## Experimental Setup

### Hardware
- CPU: AMD Ryzen 7 / Intel i7 (ou equivalente)
- RAM: 16GB mínimo
- Armazenamento: SSD

### Software
- Python 3.11+
- SQLite 3.x
- Modelo de linguagem: Claude 3.5 Sonnet (temperatura: 0.0)

### Dataset
- 20 logs de incidentes técnicos
- 5 mapeamentos de recursos
- 13 Resources AEP (project, status, skills, templates)

## Cenários de Teste

### Cenário 1: Incident Report
**Objetivo:** Recuperar informações de incidentes passados

**Procedimento AEP:**
1. LOAD incident-{id}
2. Ler campos: problem, cause, fix, prevention
3. RETURN structured data

**Procedimento RAG:**
1. Embedding do query
2. Busca top-k=5 no ChromaDB
3. RETURN documents + LLM synthesis

### Cenário 2: Project Status
**Objetivo:** Obter estado atual do projeto

**Procedimento AEP:**
1. LOAD status-{project}
2. Ler registradores R0-R7
3. RETURN state dict

**Procedimento RAG:**
1. Embedding do query
2. Busca top-k=5
3. RETURN synthesized status

## Métricas

### Tokens
Contagem usando o tokenizer nativo do modelo (tiktoken para GPT,Anthropic tokenizer para Claude).

**Fórmula:**
```
tokens_aep = sum(len(tokenize(resource)) for resource in loaded_resources)
tokens_rag = sum(len(tokenize(retrieved_docs)) for retrieved_docs)
```

### Precisão
Medida como acurácia da resposta correta em relação à resposta esperada.

**Fórmula:**
```
accuracy = correct_answers / total_queries
```

### Determinismo
- Temperatura: 0.0 em todos os testes
- Seeds fixas para reprodutibilidade
- Múltiplas execuções (n=10) com média

## Resultados

| Métrica | AEP | RAG | Delta |
|---------|-----|-----|-------|
| Tokens médios | 390 | 1950 | -80% |
| Precisão | 95% | 78% | +22% |
| Latência | ~50ms | ~200ms | -75% |

## Limitações

1. Dataset limitado (20 incidentes)
2. Apenas um modelo testado (Claude 3.5)
3. RAG baseline usa configuração padrão
4. Não testado em produção real

## Reprodutibilidade

Para reproduzir os testes:
```bash
cd tools/aep-benchmark
python benchmark.py --iterations 10 --resources ../../RESOURCES
```

## Referências

- LangChain Documentation
- ChromaDB Documentation
- AEP Specification v1.0.0