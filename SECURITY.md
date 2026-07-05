# AEP Security Policy

## Escopo

O AEP (Agent Execution Protocol) é um protocolo de dados e contexto. Ele não executa código arbitrário, apenas define contratos para agentes de IA.

## Limitações

### O Protocolo Não
- Executa comandos do sistema
- Acessa dados sensíveis
- Oferece sandboxing
- Autentica usuários

### Responsabilidades
- **Agente/CLI**: Responsável por executar comandos com segurança
- **Usuário**: Responsável por revisar Resources antes de carregar
- **Implementação**: Responsável por validar entrada e sanitizar saída

## Vulnerabilidades Conhecidas

Nenhuma vulnerabilidade conhecida no protocolo v1.0.0.

## Reportando uma Vulnerabilidade

Se você descobrir uma vulnerabilidade no AEP:

1. **Não** abra uma issue pública
2. Envie um email para security@aep.io (ou contato direto)
3. Aguarde confirmação de recebimento (máximo 48h)
4. Trabalhe com a equipe para resolver

### Processo de Divulgação

1. **T+0**: Vulnerabilidade reportada
2. **T+48h**: Confirmação e análise inicial
3. **T+7 dias**: Correção e patch (se aplicável)
4. **T+14 dias**: Divulgação pública coordenada

## Práticas Recomendadas

### Para Usuários
- Revise Resources antes de usar
- Use apenas Resources de fontes confiáveis
- Mantenha o KERNEL/ imutável
- Use Git para histórico, não o estado

### Para Implementadores
- Valide entrada sempre (nunca confie em Resources)
- Sanitize saída
- Use os testes de conformidade
- Mantenha o protocolo atualizado

## Contato

Para questões de segurança, entre em contato diretamente com os mantenedores.