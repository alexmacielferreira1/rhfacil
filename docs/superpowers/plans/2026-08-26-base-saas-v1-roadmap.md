# Base SaaS V1 — Roteiro de Implementação

**Especificação:** `docs/superpowers/specs/2026-08-26-base-saas-v1-design.md`

## Princípio de execução

Cada fase produz software funcional e testável. Uma fase só começa depois que os testes, verificações de segurança e documentação da anterior estiverem aprovados.

## Fases

1. **Fundação executável (CONCLUÍDA EM 2026-08-26)** — estrutura limpa, backend, frontend, PostgreSQL, Redis, Mailpit, Docker, qualidade e teste ponta a ponta de saúde.
2. **Identidade e multi-tenancy (CONCLUÍDA EM 2026-08-26)** — usuários, empresas, convites, sessões em cookies, CSRF, RBAC e isolamento duplo FastAPI + PostgreSQL RLS.
3. **Segurança, auditoria e LGPD (CONCLUÍDA EM 2026-08-27)** — força bruta, limites, trilha de auditoria, ciclo de vida dos dados e solicitações dos titulares.
4. **E-mail, tarefas e arquivos (CONCLUÍDA EM 2026-08-27)** — adaptador de e-mail, fila, repetição/idempotência, uploads, quarentena, antivírus opcional e downloads autorizados.
5. **IA, planos e observabilidade (CONCLUÍDA EM 2026-08-29)** — gateway seguro de IA, orçamento, assinatura, feature flags, métricas, rastreamento, retenção, backups e incidentes.
6. **Template e validação final (CONCLUÍDA EM 2026-08-29)** — inicializador guiado, ADRs, documentação, checklist, banco vazio e prova de criação de um SaaS limpo.
7. **Migração do Media Mind AI** — plano próprio, posterior à aprovação da Base V1.
8. **Migração do RH** — plano próprio, posterior à validação do Media Mind AI.
9. **Separação da gestão de funcionários** — retirar do novo `002_IA_RH_RECRUTAMENTO` o módulo de gerenciamento interno de funcionários e reconstruí-lo como o projeto independente `003_GESTAO_DE_FUNCIONARIOS`, também derivado da Base V1 e do material de referência existente.
10. **Clínica Gabrielli** — projeto posterior aos três SaaS anteriores, planejado separadamente a partir do material que será fornecido pelo proprietário.

## Evidência do marco da fundação

- `scripts/verify.ps1`: aprovado com 4 testes de backend, Ruff, mypy, ESLint, TypeScript, 1 teste de frontend e build de produção.
- `tests/smoke/compose-health.ps1`: aprovado com API, frontend, PostgreSQL, Redis e Mailpit reais.
- Alembic: upgrade, teste do esquema, downgrade e novo upgrade aprovados.
- Imagens executadas como usuários sem privilégios; portas locais vinculadas a `127.0.0.1`.
- Nenhuma pasta de exemplo, backup ou identidade Git foi alterada.
- Fase 2: 20 testes de backend aprovados; login, logout, sessão HttpOnly, CSRF, força bruta, RBAC, convites de uso único e identidade do tenant foram validados em PostgreSQL e Redis reais.
- Fase 3: 26 testes de backend aprovados; auditoria append-only, eventos sensíveis, pedidos LGPD, administração restrita e retenção configurável foram validados. Frontend: lint, tipagem, teste e build aprovados.
- Fase 4: 38 testes de backend aprovados; fila transacional, worker, SMTP/Mailpit real, uploads em quarentena, revisão e downloads autorizados foram validados. Seis serviços Docker ficaram operacionais.
- Fases 5 e 6: aceitação final com 65 testes de backend, 4 testes de frontend, lint, tipagem, build, seis serviços, backup/restauração, banco vazio e inicializador aprovados.

## Regras invariáveis

- Projetos originais no Desktop e cópias em `EXEMPLOS QUE TENHO` são somente leitura.
- Nenhum Git, GitHub, Codex ou Claude novo será configurado antes da etapa autorizada pelo proprietário.
- Nenhum segredo, dado real, cache, ambiente virtual, upload ou identidade Git será copiado.
- Decisões específicas de produto não entram na base genérica.
- Cada fase usa desenvolvimento orientado por testes e termina com validação reproduzível.
- Cada projeto derivado registra de forma legível e estruturada a versão exata da base que lhe deu origem. Uma Base V2 não altera projetos V1 automaticamente; ela produz documentação de diferenças e cada migração é planejada, aprovada e testada individualmente.
- Ao final do processo será gerado um relatório reutilizável para análise por outra IA, contendo decisões, arquitetura, etapas, problemas, soluções e evidências de teste, sem segredos ou dados privados dos projetos.
