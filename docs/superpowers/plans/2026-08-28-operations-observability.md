# Operations and Observability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar a operação segura da Base V1 com métricas sem dados pessoais, retenção executável, backup/restauração verificáveis e resposta a incidentes.

**Architecture:** Métricas são calculadas por consultas agregadas e expostas apenas a administradores. A manutenção roda pelo worker com operações idempotentes por tenant. Backup e restauração ficam em scripts separados, com verificação de integridade e documentação de produção.

**Tech Stack:** FastAPI assíncrono, PostgreSQL 16/RLS, Redis, worker Python, PowerShell, pytest e Docker Compose.

**Spec:** `docs/superpowers/specs/2026-08-26-base-saas-v1-design.md`

## Global Constraints

- Não registrar e-mail, token, prompt, resposta de IA, nome de arquivo ou IP bruto em métricas.
- Retenção nunca remove auditoria fora da política configurada e toda execução gera evento administrativo.
- Backup local é somente demonstração; produção exige armazenamento criptografado e credenciais separadas.
- Não iniciar Git e não alterar `EXEMPLOS QUE TENHO`.

---

### Task 1: Métricas administrativas sem dados pessoais

**Files:**
- Create: `backend/app/modules/operations/router.py`
- Create: `backend/app/modules/operations/schemas.py`
- Modify: `backend/app/api/router.py`
- Test: `backend/tests/integration/test_operations_metrics.py`

**Interfaces:**
- Consumes: sessão, `authorize_role`, `set_tenant` e tabelas agregáveis.
- Produces: `GET /api/v1/operations/metrics` com contagens e estado operacional do tenant.

- [x] Escrever teste que exige 403 para `member` e resposta agregada para `admin`, sem campos pessoais.
- [x] Executar o teste e confirmar falha 404.
- [x] Implementar consultas `count(*)` e somas de tokens, protegidas por tenant e RBAC.
- [x] Executar teste, Ruff e mypy até aprovação.
- [x] Registrar o checkpoint em `docs/PROGRESSO.md` sem commit Git.

### Task 2: Retenção automatizada e auditável

**Files:**
- Create: `backend/app/modules/maintenance/retention.py`
- Modify: `backend/app/worker.py`
- Test: `backend/tests/integration/test_retention.py`

**Interfaces:**
- Consumes: prazos positivos de `Settings` e conexão com tenant definido.
- Produces: `apply_retention(connection, organization_id, settings) -> RetentionResult`.

- [x] Escrever teste com registros dentro e fora dos prazos e resultado literal esperado.
- [x] Confirmar que falha pela função ausente.
- [x] Implementar eliminação de sessões revogadas/expiradas e pedidos LGPD encerrados; preservar auditoria append-only e registrar execução.
- [x] Executar teste e suíte de regressão.
- [x] Documentar que políticas legais específicas de cada SaaS prevalecem.

### Task 3: Backup e restauração verificáveis

**Files:**
- Create: `scripts/backup.ps1`
- Create: `scripts/restore-check.ps1`
- Create: `docs/operations/BACKUP_RESTORE.md`
- Test: `tests/smoke/backup-restore.ps1`

**Interfaces:**
- Consumes: PostgreSQL do Compose e diretório explícito fornecido pelo operador.
- Produces: dump com checksum SHA-256 e restauração descartável validada.

- [x] Escrever smoke test em diretório temporário que falha porque os scripts não existem.
- [x] Implementar backup sem segredos no argumento/arquivo e gerar checksum.
- [x] Implementar restauração apenas em banco descartável explicitamente nomeado.
- [x] Executar backup, restauração, consultas de sanidade e remoção do banco descartável.
- [x] Documentar criptografia, separação de credenciais, periodicidade e teste de recuperação em produção.

### Task 4: Resposta a incidentes e aceitação

**Files:**
- Create: `docs/operations/INCIDENT_RESPONSE.md`
- Modify: `docs/security/SECURITY_BASELINE.md`
- Modify: `docs/PROGRESSO.md`
- Modify: `docs/superpowers/plans/2026-08-26-base-saas-v1-roadmap.md`

**Interfaces:**
- Consumes: sessões revogáveis, auditoria, request IDs, backups e configuração de segredos.
- Produces: procedimento operacional de detecção, classificação, contenção, preservação, recuperação e avaliação LGPD/ANPD.

- [x] Documentar papéis, severidades, evidências, bloqueio de sessões, rotação de chaves e comunicação.
- [x] Executar `scripts/verify.ps1` e todos os smokes Docker.
- [x] Confirmar migrations e serviços saudáveis.
- [x] Marcar a Fase 5 concluída somente com todas as evidências registradas.
