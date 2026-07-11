# Architecture Decision Records

## ADR-001 — KMC is Passive Behavioral Oracle

**Status:** Accepted  
**Context:** Validar invariantes do protocolo sem depender de nenhuma implementação concreta. Oracles ativos que executam side effects ou acoplam lógica de validação ao kernel criam risco de falso-positivo por contaminação do ambiente.  
**Decision:** O KMC (Kernel Metamorphic Oracle) é um checker passivo que opera exclusivamente sobre `TraceEvent` — dados de execução imutáveis. Ele importa zero código do kernel e nunca modifica estado. Sua validação é metamórfica: compara execuções válidas contra mutantes deliberados para provar que cada invariante tem dentes.  
**Consequences:** Portável entre runtimes sem adaptação. Não produz falsos positivos por interferência. A desvantagem é que o oracle não detecta violações que não produzem traços observáveis.

---

## ADR-002 — Specification Before Implementation

**Status:** Accepted  
**Context:** Em ecossistemas multi-runtime, o código existente tende a ser tratado como a "fonte da verdade" normativa, levando a drift entre especificação e implementação. O risco é que um runtime dominante defina o protocolo por inércia, não por contrato.  
**Decision:** A suíte de conformidade normativa e a especificação formal (AEP-0001 a AEP-0008) determinam a validade de uma implementação, não o código atual de qualquer runtime. Nenhum runtime tem precedência normativa sobre a especificação. A KMC oracle reforça esta decisão validando invariantes independentemente de qualquer runtime específico.  
**Consequences:** A especificação pode evoluir sem ser refém de débitos de implementação. O custo é que novos runtimes precisam atingir conformidade contra especificação + testes, não contra uma implementação de referência.

---

## ADR-003 — Separate AEP and KOS Runtime State

**Status:** Accepted  
**Context:** O `StateManager` do AEP runtime originalmente lia e escrevia em `KERNEL/STATE.md` — o mesmo arquivo usado pelo meta-kernel KOS para orquestração de sessão. Durante a auditoria da Fase 2, um estado residual de HEALTH=FAIL no KOS (deixado por um teste destrutivo) contaminou a leitura do AEP, gerando um falso-positivo que interrompeu a análise por horas.  
**Decision:** O estado do runtime AEP foi movido para `AEP/runtime_state/state.md`, fisicamente separado de `KERNEL/STATE.md`. O caminho é parametrizável via variável de ambiente `AEP_STATE_PATH` para suporte a sandboxes limpas em CI/CD. KOS e AEP runtime são agora mutuamente invisíveis em termos de estado. Oito testes de regressão em `test_kos_isolation.py` provam imunidade a qualquer conteúdo de `KERNEL/STATE.md` (lixo, HEALTH=FAIL, vazio, binário).  
**Consequences:** Falso-positivo por interferência cruzada eliminado. CI/CD pode injetar `AEP_STATE_PATH` para cada execução, garantindo isolamento total. A dívida restante é que o carregamento de programa (`load_program`) ainda lê de `KERNEL/PROGRAM.md` — mas este é um artefato de orquestração deliberado, não um acoplamento acidental.

---

## ADR-004 — Runtime-Neutral Watchdog Contract

**Status:** Accepted  
**Context:** AEP-0008 define o Watchdog Timer (R1) como mecanismo de bounding de loops. Diferentes runtimes (Python, SQLite, referência Markdown) precisam implementar a mesma semântica de watchdog sem depender de características específicas de cada linguagem ou armazenamento.  
**Decision:** O contrato de watchdog é puramente determinístico e agnóstico a runtime: (a) R1 é decrementado **apenas** no opcode EXEC (§1.1); (b) LOAD, VALIDATE, COMMIT, EXIT e YIELD não consomem ciclos; (c) YIELD é preventivo — não há look-ahead nem rescue após exaustão; (d) exaustão em R1=0 é imediata e síncrona, retornando `AEP_ERR_WATCHDOG_EXHAUSTION` com rollback preservando R0, R3, R7. A KMC oracle (KMC-001) valida este contrato com traços de execução.  
**Consequences:** Qualquer runtime que implemente o contrato é intercambiável. O custo é que otimizações específicas de runtime (ex.: lazy decrement no SQLite) não são permitidas — o decremento deve ocorrer no EXEC, ponto de chamada.

---

## ADR-005 — Protocol Errors vs Oracle Errors

**Status:** Accepted  
**Context:** Durante o desenvolvimento, dois tipos de falhas eram frequentemente confundidas: (a) erros de execução do protocolo (ex.: watchdog exhaustion, validation rollback, resource not found) e (b) violações de invariantes capturadas pelo KMC tracer (ex.: R1 decrementado em LOAD, R2 executado pelo kernel). Tratá-las como a mesma categoria dificulta diagnóstico e cria ruído em pipelines de CI.  
**Decision:** Erros de protocolo são estruturados com `error_code` no namespace `AEP_ERR_*` e escritos em R4 [BLOCKERS] com timestamp e trace. Violações de oracle são reportadas pelo KMC em campo separado (`behavioral_valid`, `failure_mode`, `assertions_passed/failed`) e não modificam o estado do runtime. O normative runner exibe ambas as camadas lado a lado: `PASS`/`FAIL` para protocolo, `[PASS]`/`[FAIL]` para KMC — mantendo a distinção explícita no relatório de conformidade.  
**Consequences:** Diagnóstico preciso de falhas: um PASS com KMC [FAIL] indica invariante quebrada mesmo com execução nominal bem-sucedida. Um FAIL com KMC [PASS] indica erro de protocolo que o oracle não cobre. A separação elimina a ambiguidade que atrasou a auditoria inicial da Fase 2.
