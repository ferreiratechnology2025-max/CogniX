---
type: skill
id: skill-markdown
version: 1.0.0
depends: []
status: active
---
# SKILL: Markdown

## OBJETIVO
Fornecer conhecimento sobre Markdown, incluindo sintaxe, boas práticas e padrões para documentação técnica.

## QUANDO USAR
- Ao criar qualquer Resource no KOS
- Ao documentar projetos
- Ao escrever ADRs ou Incidentes
- Ao formatar textos para IA

## QUANDO NÃO USAR
- Textos que exigem formatação complexa (HTML, LaTeX)
- Documentos que precisam de layout específico (PDF, Word)

## SINTAXE BÁSICA

### Cabeçalhos
```markdown
# Título 1
## Título 2
### Título 3
```

### Ênfase
```markdown
*itálico* ou _itálico_
**negrito** ou __negrito__
~~riscado~~
```

### Listas
```markdown
- Item 1
- Item 2
  - Subitem 2.1

1. Item 1
2. Item 2
```

### Links e Imagens
```markdown
[Texto do link](https://exemplo.com)
![Texto alternativo](imagem.png)
```

### Código
```markdown
`código inline`

```python
print("código em bloco")
```
```

### Tabelas
```markdown
| Coluna 1 | Coluna 2 |
|----------|----------|
| Valor 1  | Valor 2  |
```

## BOAS PRÁTICAS PARA KOS
1. Use frontmatter YAML para metadados (type, id, version, depends, status)
2. Separe metadados do conteúdo com `---`
3. Use cabeçalhos para organizar seções
4. Prefira listas a parágrafos longos
5. Use code blocks para exemplos de código
6. Mantenha uma linha em branco entre seções
7. Use comentários HTML para notas que não devem aparecer no output (opcional)

## EXEMPLO DE RESOURCE BEM FORMATADO
```markdown
---
type: skill
id: skill-exemplo
version: 1.0.0
depends: []
status: active
---
# SKILL: Exemplo

## OBJETIVO
Demonstrar um Resource bem formatado.

## CONTEÚDO
- Lista organizada
- Código com syntax highlighting
- Seções claras
```

## CHECKLIST DE FORMATAÇÃO
- [ ] Frontmatter YAML com type, id, version, depends, status
- [ ] Título principal com #
- [ ] Seções com ##
- [ ] Listas com - ou 1.
- [ ] Código com ``` 
- [ ] Links com [texto](url)
- [ ] Linhas em branco entre seções