# Guia de Contribuição — KOS

Obrigado por considerar contribuir para o KOS! Este guia explica como você pode ajudar.

## Como Contribuir

### 1. Reportar Issues
- Use o sistema de issues do GitHub
- Descreva o problema claramente
- Inclua logs ou screenshots se aplicável
- Marque com labels apropriadas

### 2. Sugerir Melhorias
- Crie uma issue com a tag `enhancement`
- Descreva a melhoria e o motivo
- Explique como isso beneficia o KOS
- Considere a compatibilidade com a ISA

### 3. Adicionar Resources
- Crie novos Resources em RESOURCES/
- Siga o protocolo (type, id, version, depends, status)
- Atualize dependências se necessário
- Adicione exemplos de uso

### 4. Melhorar Skills
- Skills são conhecimento coletivo
- Atualize Skills existentes com novas informações
- Crie novas Skills para preencher lacunas
- Mantenha o formato do template

### 5. Refatorar o Kernel
- O Kernel é imutável por design
- Mudanças no Kernel precisam de discussão
- Crie uma issue primeiro
- Proponha alterações na ISA com justificativa

## Padrões de Código

### Resources
Todos os Resources devem seguir o protocolo:

```yaml
---
type: <tipo>
id: <identificador-unico>
version: <semver>
depends: [<resource-id>, ...]
status: draft | active | deprecated | archived
---
# CONTEÚDO
...
```

### Convenções de Nomenclatura
- **IDs**: Use `kebab-case` (ex: `project-api-core`)
- **Versions**: Use SemVer (ex: `1.2.3`)
- **Arquivos**: Use o ID como nome do arquivo (ex: `project-api-core.md`)

### Estrutura de Conteúdo
1. Título principal com `#`
2. Seções com `##`
3. Subseções com `###`
4. Listas com `-` ou `1.`
5. Código com ` ``` `
6. Links com `[texto](url)`

### Tipos de Resource Válidos
| Type | Descrição |
|------|-----------|
| `project` | Definição do projeto |
| `status` | Estado atual |
| `skill` | Conhecimento reutilizável |
| `adr` | Decisão arquitetural |
| `incident` | Registro de erro |
| `rule` | Regra do projeto |
| `template` | Template para criação |

## Fluxo de Trabalho de Contribuição

### 1. Fork e Clone
```bash
git clone <seu-fork>
cd CogniX
```

### 2. Crie um Branch
```bash
git checkout -b feature/minha-contribuicao
```

### 3. Faça Suas Alterações
- Atualize ou crie Resources
- Siga o protocolo
- Mantenha o Kernel imutável (a menos que seja aprovado)

### 4. Teste
```bash
claude "Leia AGENTS.md e execute a tarefa"
```
Verifique se:
- `VALIDATE` passa
- `EXEC` funciona
- `COMMIT` persiste

### 5. Commit
```bash
git add RESOURCES/
git commit -m "feat(resource): adicionar nova skill"
```

### 6. Push e Pull Request
```bash
git push origin feature/minha-contribuicao
```
Crie um Pull Request com:
- Descrição clara do que mudou
- Referência a issues relacionadas
- Checklist de verificação

## Padrões de Commit

Use mensagens descritivas:

```
<tipo>(<escopo>): <descrição>

[corpo opcional]
[rodapé opcional]
```

**Tipos:**
- `feat`: novo Resource ou funcionalidade
- `fix`: correção de Resource
- `docs`: documentação
- `refactor`: refatoração sem mudança de comportamento
- `chore`: tarefas de manutenção
- `test`: testes ou validação

**Escopos:**
- `resource`: mudanças em Resources
- `kernel`: mudanças no Kernel (raro)
- `skill`: mudanças em Skills
- `doc`: mudanças em documentação

## Critérios de Aceite para PRs

- [ ] Resources válidos (type, id, version, depends, status)
- [ ] Dependências existentes
- [ ] Formatação Markdown correta
- [ ] Testes executados (VALIDATE passou)
- [ ] Mensagens de commit claras
- [ ] Documentação atualizada (se aplicável)

## Roadmap de Desenvolvimento

### Fase 5 - Documentação (Atual)
- [x] README.md
- [x] USAGE.md
- [x] CONTRIBUTING.md

### Fase 6 - Integração Git
- [ ] .gitignore
- [ ] Commit inicial
- [ ] Workflow de PR

### Fase 7 - Agentes Reais
- [ ] Teste com Claude Code
- [ ] Teste com Cursor
- [ ] Teste com Aider

### Fase 8 - Novos Resources
- [ ] Templates para todos os tipos
- [ ] Skills avançadas
- [ ] ADRs e Incidentes de exemplo

## Agradecimentos

Contribuições são bem-vindas! O KOS é um projeto colaborativo para melhorar a interação com agentes de IA.

## Licença

MIT