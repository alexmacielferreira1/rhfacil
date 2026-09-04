# Generic Subscriptions and Feature Flags Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar o domínio genérico de assinatura e funcionalidades sem integrar pagamento real.

**Architecture:** Planos definem limites; cada tenant possui assinatura com trial e estado controlado. Funcionalidades são chaves genéricas habilitadas por plano ou sobrescritas por tenant. Uma interface de provedor permanece desativada/local por padrão.

**Tech Stack:** PostgreSQL 16/RLS, Alembic, FastAPI assíncrono, Pydantic e pytest.

**Spec:** `docs/superpowers/specs/2026-08-26-base-saas-v1-design.md`

## Global Constraints

- Sem Stripe, cobrança, cartão ou credencial real na V1.
- Todos os registros de assinatura/flags são isolados por tenant com RLS forçado.
- Estados válidos: `trialing`, `active`, `past_due`, `cancelled`, `suspended`.
- Falha fechada para funcionalidade desconhecida ou assinatura inativa.

### Task 1: Esquema e regras de acesso

**Files:**
- Create: `backend/migrations/versions/20260828_0010_subscriptions_features.py`
- Create: `backend/tests/integration/test_subscription_schema.py`

**Interfaces:**
- Produces: `tenant_subscriptions`, `plan_features` e `tenant_feature_overrides`.

- [x] Escrever teste vermelho de tabelas, constraints e RLS.
- [x] Criar migration reversível com trial, estado, datas e feature keys.
- [x] Aplicar migration e aprovar teste de esquema/isolamento.

### Task 2: Serviço e provedor neutro

**Files:**
- Create: `backend/app/modules/billing/service.py`
- Create: `backend/app/modules/billing/providers.py`
- Create: `backend/tests/integration/test_feature_access.py`

**Interfaces:**
- Produces: `has_feature(connection, organization_id, feature_key) -> bool` e `DisabledBillingProvider`.

- [x] Escrever testes vermelhos para trial ativo, suspensão, flag desconhecida e override explícito.
- [x] Implementar resolução fail-closed e provedor local sem efeitos externos.
- [x] Executar testes, Ruff e mypy.

### Task 3: Administração e documentação

**Files:**
- Create: `backend/app/modules/billing/router.py`
- Create: `backend/app/modules/billing/schemas.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/integration/test_subscription_admin.py`
- Modify: `docs/REQUIREMENTS_MATRIX.md`

**Interfaces:**
- Produces: leitura administrativa da assinatura/funcionalidades; nenhuma cobrança externa.

- [x] Escrever testes vermelhos de RBAC e isolamento.
- [x] Implementar endpoint somente `owner/admin`, auditável e sem dados financeiros.
- [x] Executar regressão completa e atualizar a matriz.
