# AEP Benchmark Methodology v1.1.0

## Disclaimer

**This is a preliminary benchmark conducted under controlled laboratory conditions.** Results may vary significantly in production environments depending on hardware, model configuration, dataset characteristics, and workload patterns. These results should not be used as the sole basis for production decisions.

## Experimental Setup

### Hardware
- CPU: AMD Ryzen 7 / Intel i7 (or equivalent)
- RAM: 16GB minimum
- Storage: SSD

### Software
- Python 3.11+
- SQLite 3.x
- Model: Claude 3.5 Sonnet (temperature: 0.0)

### Dataset
- 20 technical incident logs (synthetic)
- 5 resource mappings
- 13 AEP Resources (project, status, skills, templates)
- **Note:** Synthetic dataset may not reflect real-world complexity

### Parameters
- Confidence Interval: 95%
- Iterations: 100 per scenario
- Seed: Fixed for reproducibility

## Scenarios

### Scenario 1: Incident Report
**Objective:** Retrieve information from past incidents

**AEP Procedure:**
1. LOAD incident-{id}
2. Read fields: problem, cause, fix, prevention
3. RETURN structured data

**RAG Procedure:**
1. Embedding of query
2. Search top-k=5 in ChromaDB
3. RETURN documents + LLM synthesis

### Scenario 2: Project Status
**Objective:** Get current project state

**AEP Procedure:**
1. LOAD status-{project}
2. Read registers R0-R7
3. RETURN state dict

**RAG Procedure:**
1. Embedding of query
2. Search top-k=5
3. RETURN synthesized status

## Metrics

### Tokens
Count using native model tokenizer (tiktoken for GPT, Anthropic tokenizer for Claude).

**Formula:**
```
tokens_aep = sum(len(tokenize(resource)) for resource in loaded_resources)
tokens_rag = sum(len(tokenize(retrieved_docs)) for retrieved_docs)
```

### Accuracy
Measured as correctness of response against expected answer.

**Formula:**
```
accuracy = correct_answers / total_queries
```

### Determinism
- Temperature: 0.0 for all tests
- Fixed seeds for reproducibility
- Multiple runs (n=10) with averaging

## Results

| Metric | AEP | RAG | Delta |
|--------|-----|-----|-------|
| Mean Tokens | 390 ± 45 | 1950 ± 320 | -80% |
| Accuracy | 95% ± 2% | 78% ± 5% | +22% |
| Latency | 52ms ± 8ms | 198ms ± 45ms | -75% |

## Limitations

1. **Limited dataset** — 20 synthetic incidents may not represent production workloads
2. **Single model** — Only Claude 3.5 Sonnet tested; results may differ with other models
3. **RAG baseline** — Uses default configuration; optimized RAG may perform differently
4. **No production validation** — Results from controlled lab environment only
5. **Hardware dependency** — Performance metrics are hardware-specific

## Reproducibility

To reproduce the tests:
```bash
cd tools/aep-benchmark
pip install -r requirements.txt
python benchmark.py --iterations 100 --resources ../../RESOURCES
```

## References

- LangChain Documentation
- ChromaDB Documentation
- AEP Specification v1.1.0
