# Relatório técnico compartilhável — Base SaaS V1

## Objetivo

A Base SaaS V1 é um template local e versionado para iniciar produtos SaaS independentes. Ela não contém lógica específica do Media Mind, RH ou outros verticais. Cada novo produto recebe uma cópia limpa, registra sua linhagem e passa a evoluir com banco, segredos, dados, configuração e futuro repositório próprios.

Este relatório pode ser fornecido a outra IA para análise. Ele não inclui segredos pessoais nem depende de Supabase.

## Arquitetura

- Backend: Python 3.14, FastAPI, SQLAlchemy assíncrono, Alembic e Poetry.
- Dados: PostgreSQL 16 e Redis.
- Frontend: React 19, TypeScript, Vite, React Query, React Hook Form e Zod.
- Ambiente local: Docker Compose com backend, worker, frontend, PostgreSQL, Redis e Mailpit.
- Organização: monólito modular; módulos de domínio separados, um fluxo de migrations e poucos componentes operacionais.

## Segurança e identidade

- Sessão web opaca e revogável em cookie `HttpOnly`; produção exige cookie `Secure` e segredo forte.
- Proteção CSRF nas operações que alteram estado.
- Hash de senha com Argon2.
- Rate limit contra força bruta e resposta de autenticação sem revelar se usuário existe.
- RBAC inicial com `owner`, `admin` e `member`; produtos derivados podem acrescentar papéis específicos.
- Convite com link de uso único e expiração.
- Conta iniciada pelo administrador sem senha temporária: a pessoa define a própria senha pelo link.
- Solicitação pública de acesso por link da empresa, com aprovação ou rejeição administrativa.
- MFA está documentado como uma das primeiras exigências para produção, mas não bloqueia desenvolvimento local.
- Cabeçalhos de segurança, validação de configuração de produção e prevenção de injeção em cabeçalhos de e-mail.

## Isolamento entre empresas

Cada registro de cliente usa `organization_id`. O backend autoriza a empresa e o PostgreSQL aplica Row-Level Security com `FORCE ROW LEVEL SECURITY`. A transação define a empresa atual, e o papel restrito da aplicação não pode ignorar a política. Testes exercitam leitura e escrita com o papel real da aplicação.

Essa defesa cobre identidade, associações, sessões, convites, auditoria, solicitações LGPD, fila, arquivos, planos, uso de IA, pedidos de acesso, assinaturas e funcionalidades.

## Auditoria, LGPD e dados

- Trilha de auditoria append-only para eventos sensíveis.
- Fluxos de solicitação do titular com administração restrita.
- Prazos de retenção configuráveis por ambiente.
- Automação remove somente sessões expiradas/revogadas e pedidos LGPD encerrados além do prazo; auditoria é preservada.
- Documentação separa finalidade, minimização, retenção, resposta a incidente e avaliação de comunicação à ANPD/titulares.
- Métricas operacionais são agregadas e não retornam e-mails ou dados pessoais.

## E-mail, tarefas e arquivos

- Adaptador SMTP independente de fornecedor; Mailpit é usado somente no ambiente local.
- Fila PostgreSQL transacional com idempotência, concorrência segura, tentativas e reagendamento.
- Convite e trabalho de e-mail nascem na mesma transação; token bruto não é persistido na fila.
- Upload autenticado com tamanho máximo, allowlist, nome interno aleatório, SHA-256 e quarentena.
- Download somente após liberação e com autorização.
- Antivírus é um adaptador opcional de produção; indisponibilidade nunca libera arquivo automaticamente.

## IA, planos e assinaturas

- Gateway de IA independente de fornecedor; sem configuração, falha com segurança.
- Cota mensal por empresa e registro de contagem de tokens.
- Prompt e resposta não são persistidos; registra-se hash com chave, estado, modelo e contagens.
- Assinatura genérica possui `trialing`, `active`, `past_due`, `cancelled` e `suspended`.
- Funcionalidades são habilitadas por plano ou sobrescritas por empresa.
- Recurso desconhecido ou assinatura inativa falha fechado.
- Consulta administrativa é restrita a dono/administrador e auditada.
- Provedor de cobrança está desativado: não há Stripe, cartão, cobrança real ou credencial financeira na V1.

## Operação e recuperação

- Identificador único de requisição para rastrear falhas.
- Métricas agregadas de membros, pedidos, fila, arquivos e consumo de IA.
- Backup PostgreSQL com checksum SHA-256.
- Smoke restaura o backup em banco descartável e valida a revisão do esquema.
- Procedimento de incidente cobre classificação, evidências, contenção, rotação, recuperação e comunicação.
- Checklist de produção exige segredos externos, TLS, MFA, backups protegidos, antivírus quando aplicável, observabilidade e revisão de retenção.

## Inicialização de novos projetos

`scripts/new-saas.ps1` recebe nome e destino, recusa uma pasta já existente, gera slug e portas sugeridas, personaliza configuração e registra origem. A cópia exclui `.git`, `.env`, configurações pessoais de IA, ambientes virtuais, `node_modules`, caches, uploads, backups e bancos locais.

Dependências não são copiadas como software instalado. O novo projeto reinstala versões declaradas pelos locks. Essa escolha evita incompatibilidade entre máquinas e projetos.

Uma futura Base V2 não sobrescreve projetos V1. Cada produto é analisado, recebe plano reversível e migra individualmente.

## Evidência de validação em 29/08/2026

- 65 testes de backend aprovados.
- Ruff aprovado.
- mypy estrito aprovado em 55 arquivos-fonte.
- 4 testes de frontend aprovados.
- ESLint, TypeScript e build Vite aprovados.
- Seis serviços Docker saudáveis: API, worker, frontend, PostgreSQL, Redis e Mailpit.
- Backup e restauração em banco descartável aprovados.
- Banco totalmente vazio migrado de zero até `20260828_0010` e removido após a prova.
- Inicializador criou uma cópia descartável, aprovou higiene e `docker compose config`, e removeu apenas o alvo de teste.

Existe um aviso não bloqueante da biblioteca Starlette sobre futura transição de `httpx` para `httpx2`; nenhum teste falhou.

## Decisões que diferem do pedido inicial

- JWT no navegador foi substituído por sessão opaca `HttpOnly` + CSRF, mais adequada ao app web e revogável. JWT continua possível para integração futura específica.
- Senha temporária foi substituída por link de ativação de uso único.
- Biblioteca compartilhada entre todos os SaaS foi adiada; a V1 usa monólito modular copiado.
- Atualização automática de todos os projetos foi rejeitada; versões da base são independentes.

## Itens deliberadamente futuros

MFA real, provedor de pagamento, provedor de IA, antivírus, armazenamento de objetos, e-mail de produção, SSO, webhooks públicos, RAG, embeddings e agentes só entram quando um produto ou ambiente de produção definir necessidade, fornecedor, consentimento, segredos e testes. Não devem ser simulados como se estivessem prontos.

## Próximos projetos

1. `001_MEDIA_MIND_AI`: reconstrução controlada sobre a Base V1, preservando funções da referência.
2. `002_IA_RH_RECRUTAMENTO`: recrutamento e seleção, sem gestão interna de funcionários.
3. `003_GESTAO_DE_FUNCIONARIOS`: produto independente com o material retirado do RH.
4. Clínica Gabrielli: planejada depois dos três anteriores.

Os projetos originais e `EXEMPLOS QUE TENHO` permanecem somente leitura por semanas como referência e ponto de retorno. GitHub, Claude e Codex novos serão configurados posteriormente, conforme decisão do proprietário.
