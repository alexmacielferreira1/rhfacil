# Matriz consolidada de requisitos

Revisão de 2026-08-29 baseada na conversa consolidada, nos dois históricos anexados, no TXT de ideias, nas especificações e no software executável.

## Concluído na Base V1

| Tema | Estado | Evidência/resumo |
|---|---|---|
| Python, FastAPI, SQLAlchemy, PostgreSQL, Poetry e Alembic | Concluído | Backend assíncrono, migrations e stack Docker. |
| Frontend | Concluído | React/TypeScript/Vite, rotas e testes. |
| Autenticação segura | Concluído | Sessões opacas HttpOnly, CSRF, Argon2 e revogação persistente. |
| Empresas, RBAC e multi-tenancy | Concluído | `owner/admin/member`, contexto API e RLS forçado no PostgreSQL. |
| Convite, conta iniciada e pedido de acesso | Concluído | Link de uso único, aprovação/rejeição, proteção antiabuso e auditoria. |
| Segurança e força bruta | Concluído | Limites Redis, respostas anti-enumeração, headers, segredos validados e usuário DB mínimo. |
| Auditoria e LGPD | Concluído | Auditoria append-only, solicitações do titular, ciclo de dados e retenção. |
| E-mail, fila e worker | Concluído | SMTP neutro, Mailpit, outbox, idempotência, repetição e worker contínuo. |
| Arquivos | Concluído | Allowlist, tamanho, hash, quarentena, revisão e download autorizado. |
| IA segura | Concluído | Gateway neutro, provedor desativado por padrão, cota e uso sem armazenar conteúdo. |
| Métricas e rastreamento | Concluído | Request ID e métricas agregadas sem dados pessoais. |
| Backup e incidentes | Concluído | Dump/checksum/restauração testada e procedimentos operacionais. |
| Inicializador seguro | Concluído | Cópia limpa, portas/slug, linhagem e recusa de sobrescrita. |
| Base V1/V2 independente | Concluído | Linhagem e nenhuma atualização automática de derivados. |
| Assinatura genérica | Concluído | Trial e estados controlados, consulta administrativa auditada e provedor externo desativado por padrão. |
| Feature flags por empresa | Concluído | Recursos por plano e exceção por tenant, com RLS forçado e resolução que falha fechada. |
| ADRs | Concluído | Cinco registros cobrem stack, sessão, isolamento, IA neutra e versionamento independente. |
| Banco vazio | Concluído | Smoke cria banco descartável, aplica Alembic de zero até `20260828_0010`, valida o esquema e remove o alvo validado. |

## Substituído por decisão mais segura

| Pedido original | Decisão atual | Motivo |
|---|---|---|
| JWT no navegador | Sessão opaca em cookie HttpOnly + CSRF | Reduz exposição do token ao JavaScript e permite revogação real. JWT pode existir futuramente para integrações específicas. |
| Senha temporária criada pelo administrador | Link de ativação de uso único | Evita transmitir ou conhecer senha alheia. A pessoa define a própria senha. |
| Base atualizando todos os projetos | Template versionado e projetos independentes | Impede quebra simultânea; migrações V1→V2 são avaliadas individualmente. |
| Biblioteca compartilhada desde o início | Monólito modular copiado | Evita complexidade prematura; extração só ocorrerá quando houver contratos estáveis entre produtos. |

## Pendências da Base V1

Nenhuma pendência bloqueante de desenvolvimento local. A Base V1 foi aprovada em 29/08/2026. Os itens de produção abaixo continuam deliberadamente futuros e devem ser tratados antes de publicar um SaaS real.

## Extensões futuras, não prometidas como prontas

- RAG, embeddings, Document AI, agentes, forecasting, recommendation e Business Analyst: capacidades do futuro AI Core, implementadas apenas quando um produto tiver caso de uso, dados e avaliação próprios.
- Webhooks, WhatsApp, redes sociais, publicação, pagamentos reais e outros fornecedores: adaptadores específicos, desativados até configuração segura.
- MFA: prioridade obrigatória antes da produção, especialmente para contas privilegiadas; não bloqueia desenvolvimento local.
- SAST, auditoria de dependências e imagens: integrar ao pipeline quando Git/CI for autorizado.

## Específico dos produtos derivados

- `001_MEDIA_MIND_AI`: mídia/broadcast, ingest, produção, edição, publicação, relatórios e papéis específicos.
- `002_IA_RH_RECRUTAMENTO`: recrutamento e seleção; não conterá gestão interna de funcionários.
- `003_GESTAO_DE_FUNCIONARIOS`: cadastro, carreira, desempenho, competências, sucessão e People Analytics.
- Clínica Gabrielli: somente depois dos três projetos e do recebimento do material específico.
- Os demais SaaS do TXT são ideias de portfólio, não módulos obrigatórios da Base.

## Limites confirmados

- Projetos antigos e `EXEMPLOS QUE TENHO` permanecem somente leitura.
- Git, GitHub e novas conexões Codex/Claude continuam adiados por decisão do proprietário.
- Nenhum segredo, ambiente, dependência instalada, banco, upload ou contexto pessoal entra nas cópias.
