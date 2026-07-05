---
type: skill
id: skill-git
version: 1.0.0
depends: []
status: active
---
# SKILL: Git

## OBJETIVO
Fornecer conhecimento sobre Git para versionamento do KOS e projetos, incluindo comandos essenciais, boas práticas e fluxos de trabalho.

## QUANDO USAR
- Ao versionar o KOS ou projetos
- Ao fazer commits, branches ou merges
- Ao revisar histórico de alterações
- Ao colaborar com outros desenvolvedores

## QUANDO NÃO USAR
- Ambientes sem Git instalado
- Repositórios com políticas específicas (usar os comandos do repositório)

## COMANDOS ESSENCIAIS

### Inicialização
```bash
git init
git clone <url>
```

### Status e Histórico
```bash
git status
git log --oneline
git diff
```

### Branches
```bash
git branch <nome>
git checkout <nome>
git switch <nome>        # Git 2.23+
git merge <branch>
git branch -d <nome>     # Deletar branch local
```

### Commits
```bash
git add <arquivo>
git add .                # Todos os arquivos modificados
git commit -m "mensagem"
git commit --amend       # Alterar último commit
```

### Remotos
```bash
git remote add origin <url>
git push origin <branch>
git pull origin <branch>
git fetch origin
```

### Stash
```bash
git stash
git stash pop
git stash list
```

## BOAS PRÁTICAS PARA O KOS

### Mensagens de Commit
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

**Exemplo:**
```
feat(kernel): adicionar opcode VALIDATE

- Verifica campos obrigatórios em Resources
- Valida type, id, version, status
- Retorna OK ou FALHA

Closes #001
```

### Fluxo de Trabalho Recomendado
1. `git status` - verifique o que foi alterado
2. `git add <arquivos>` - adicione apenas Resources modificados
3. `git commit -m "feat(tipo): descrição"` - commit atômico
4. `git push` - envie para o remoto

### .gitignore para KOS
```
# Arquivos temporários
*.tmp
*.log
.DS_Store

# Dependências (se houver)
node_modules/
vendor/

# Arquivos de IDE
.vscode/
.idea/
*.swp
*~

# Arquivos do sistema
Thumbs.db
```

## CHECKLIST DE COMMIT
- [ ] `git status` verificado
- [ ] Apenas Resources relevantes adicionados
- [ ] Mensagem de commit com tipo e escopo
- [ ] Commit atômico (uma mudança por commit)
- [ ] `git push` executado (se necessário)

## EXEMPLO DE FLUXO
```bash
# 1. Verificar status
git status

# 2. Adicionar novo Resource
git add RESOURCES/skill-markdown.md

# 3. Commit
git commit -m "feat(skill): adicionar skill-markdown"

# 4. Enviar
git push origin main
```