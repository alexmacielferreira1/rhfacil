# Base de Segurança

## Proteções já implementadas

- Conta PostgreSQL da aplicação sem privilégios administrativos.
- Isolamento por empresa na API e PostgreSQL RLS forçado.
- Senhas Argon2 e tokens armazenados somente como hash.
- Sessão opaca em cookie HttpOnly, SameSite e Secure obrigatório em produção.
- CSRF separado e obrigatório em ações autenticadas que alteram estado.
- Respostas de login genéricas e bloqueio temporário de força bruta no Redis.
- RBAC genérico com `owner`, `admin` e `member`.
- Cabeçalhos contra clickjacking, MIME sniffing e permissões indevidas.
- Auditoria append-only: a conta da aplicação não pode alterar ou apagar eventos.
- IP utilizado na auditoria somente como hash, sem texto legível.
- Segredos, ambientes, caches, bancos e uploads excluídos do template e do Git.

## Regras obrigatórias de produção

- HTTPS em todo o tráfego e cookies Secure.
- Segredos únicos em cofre de segredos, com rotação e acesso mínimo.
- PostgreSQL e Redis em rede privada, sem portas públicas.
- Firewall/WAF, limites por IP e conta, alertas e proteção contra bots.
- Backups criptografados, restauração testada e política de retenção definida.
- Logs sem senha, token, conteúdo privado, documentos ou prompts completos.
- Verificação de dependências, imagens, licenças e vulnerabilidades no CI.
- Resposta a incidentes com responsáveis, contatos e exercícios periódicos.

## MFA

MFA não é obrigatório no desenvolvimento inicial para não dificultar a criação do produto. Antes da produção, é uma das primeiras ativações obrigatórias, começando por proprietários, administradores e qualquer conta com acesso a dados sensíveis. Recuperação de MFA deve usar códigos de recuperação protegidos e nunca depender apenas de atendimento informal.

## Limites da base

Nenhuma aplicação é “à prova de hackers”. Esta base reduz riscos conhecidos, cria camadas independentes e fornece evidências testáveis. Segurança continua exigindo atualização, monitoramento, revisão de código, testes de restauração e resposta rápida a incidentes.
# Fluxos de entrada de usuários

- Convites e contas iniciadas pelo administrador usam link de ativação de uso único; senhas temporárias não são aceitas nem transmitidas.
- Solicitações públicas exigem link específico da empresa e não existe diretório público de organizações.
- Links inválidos e solicitações duplicadas recebem confirmação pública neutra para evitar enumeração.
- A nona tentativa repetida em cinco minutos recebe bloqueio temporário.
- Somente `owner` e `admin` podem listar, aprovar ou rejeitar solicitações; decisões e convites são auditados e isolados por RLS.
- A aprovação cria convite e trabalho de e-mail na mesma transação. Uma solicitação rejeitada não pode ser posteriormente aprovada.
