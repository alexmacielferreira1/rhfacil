# Entrada de usuários e aprovação de acesso

## Objetivo

Oferecer três formas seguras e auditáveis de entrada em qualquer SaaS derivado da Base V1, sempre vinculadas a uma empresa específica e sem expor um diretório público de clientes.

## Fluxos aprovados

1. **Convite por link:** proprietário ou administrador informa e-mail e papel; o sistema gera token de uso único com expiração e envia um link para o usuário definir a própria senha.
2. **Conta iniciada pelo administrador:** o administrador cadastra nome, e-mail e papel, mas não conhece nem transmite uma senha. O usuário recebe um link de ativação de uso único e define a senha no primeiro acesso. Enquanto isso, a conta permanece pendente e não pode iniciar sessão.
3. **Solicitação de entrada:** o interessado acessa uma página específica da empresa por link ou código não enumerável, informa seus dados mínimos e envia a solicitação. Proprietário ou administrador aprova ou rejeita. A aprovação gera um convite de ativação; a rejeição não revela informações internas.

Não haverá pesquisa pública de empresas. Cadastro público global continuará desativado por padrão.

## Estados e dados

As solicitações terão estados `pending`, `approved`, `rejected`, `expired` e `cancelled`. Registrarão empresa, e-mail normalizado, nome opcional, justificativa curta opcional, datas, responsável pela decisão e motivo administrativo opcional. Dados públicos serão minimizados e protegidos por limites contra abuso.

Convites e ativações continuarão armazenando apenas o hash do token. Aprovação será idempotente: repetir a operação não criará várias contas ou vários convites ativos. Solicitações duplicadas pendentes para o mesmo e-mail e empresa serão consolidadas.

## Segurança e permissões

- Somente `owner` e `admin` podem criar contas pendentes, aprovar ou rejeitar solicitações.
- A página pública usa identificador aleatório da empresa, rate limiting por IP e identidade, resposta genérica e proteção contra automação.
- Nunca enviar senha temporária em texto; o próprio usuário define a senha por link de uso único.
- Papel concedido é escolhido pelo administrador e validado pelo RBAC genérico.
- Toda criação, solicitação, aprovação, rejeição, ativação e expiração gera auditoria append-only.
- MFA continua sendo prioridade obrigatória antes da produção para contas privilegiadas.

## Integração

Os links de ativação e decisões usam a fila persistente de e-mail da Fase 4. A criação do registro e do trabalho de e-mail ocorre na mesma transação do PostgreSQL. O frontend terá páginas genéricas de solicitação, ativação e administração, personalizáveis pelos projetos derivados.

## Falhas e privacidade

Respostas externas não confirmam se um e-mail já possui conta. Tokens inválidos, usados ou expirados recebem a mesma mensagem. Falha no envio permanece na fila para repetição e não desfaz a decisão administrativa. Solicitações antigas seguem política de retenção configurável e o fluxo LGPD.

## Testes de aceitação

- Cada um dos três fluxos conclui uma ativação válida.
- Senha nunca aparece em banco, fila, auditoria ou e-mail.
- Token bruto nunca é persistido.
- Membro comum não aprova, rejeita nem cria contas.
- Empresa A não acessa solicitações da empresa B, inclusive sob RLS.
- Duplicação e repetição não criam usuários ou e-mails adicionais.
- Força bruta e enumeração recebem bloqueio e respostas genéricas.
