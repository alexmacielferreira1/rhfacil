# Access Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar convite, conta iniciada pelo administrador e solicitação de entrada com ativação segura e auditável.

**Architecture:** O PostgreSQL mantém solicitações, convites e trabalhos de e-mail na mesma transação e aplica RLS por empresa. Rotas públicas recebem apenas identificador aleatório da empresa, enquanto decisões administrativas reutilizam sessão, CSRF e RBAC existentes.

**Tech Stack:** Python 3.14, FastAPI assíncrono, SQLAlchemy/asyncpg, PostgreSQL 16 com RLS, Redis, Alembic, Pydantic, pytest e React/TypeScript.

**Spec:** `docs/superpowers/specs/2026-08-27-access-onboarding-design.md`

## Global Constraints

- Não iniciar Git até autorização posterior; substituir passos de commit por registro em `docs/PROGRESSO.md`.
- Nunca persistir ou enviar senha temporária.
- Tokens brutos existem apenas no link entregue; banco e auditoria recebem somente hashes ou identificadores não secretos.
- `owner` e `admin` decidem; `member` não decide.
- Não criar busca ou diretório público de empresas.
- Todos os dados de empresa usam dupla proteção: contexto da API e RLS forçado.

---

### Task 1: Solicitações de entrada e identificador público

**Files:**
- Create: `backend/migrations/versions/20260827_0009_access_requests.py`
- Modify: `backend/app/core/models.py`
- Test: `backend/tests/integration/test_access_request_schema.py`

**Interfaces:**
- Consumes: `set_tenant(connection, organization_id)`.
- Produces: tabelas `organization_access_links` e `access_requests` com estados controlados e unicidade de solicitação pendente.

- [ ] **Step 1: Write the failing test**

```python
rows = await connection.execute(text("""
select relname, relrowsecurity from pg_class
where relname in ('organization_access_links', 'access_requests') order by relname
"""))
assert rows.all() == [('access_requests', True), ('organization_access_links', True)]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `poetry run pytest -q tests/integration/test_access_request_schema.py`
Expected: FAIL because the tables do not exist.

- [ ] **Step 3: Write minimal implementation**

Create tenant-owned tables. `organization_access_links` stores `token_hash`, `active`, `expires_at`; `access_requests` stores normalized email, optional name/reason, status, decision actor/reason and timestamps. Add status check, forced RLS and a partial unique index for one `pending` request per organization/e-mail.

- [ ] **Step 4: Run test to verify it passes**

Run Alembic upgrade, then the targeted test. Expected: PASS.

- [ ] **Step 5: Record checkpoint**

Record migration, test count and absence of changes to examples in `docs/PROGRESSO.md`.

### Task 2: Public request with abuse protection

**Files:**
- Create: `backend/app/modules/access_requests/schemas.py`
- Create: `backend/app/modules/access_requests/router.py`
- Modify: `backend/app/api/router.py`
- Test: `backend/tests/integration/test_public_access_request.py`

**Interfaces:**
- Consumes: hashed public organization link and Redis rate limiter.
- Produces: `POST /api/v1/access/request/{public_token}` returning the same generic response for accepted and duplicate submissions.

- [ ] **Step 1: Write the failing tests**

```python
response = await client.post(f'/api/v1/access/request/{token}', json={
    'email': 'person@example.test', 'name': 'Pessoa', 'reason': 'Participar do time'
})
assert response.status_code == 202
assert response.json() == {'message': 'Solicitação recebida para análise.'}
```

Add independent cases for invalid token returning the same public message, duplicate request not creating a second row, and the ninth attempt receiving 429.

- [ ] **Step 2: Run tests to verify they fail**

Run: `poetry run pytest -q tests/integration/test_public_access_request.py`
Expected: FAIL with route not found.

- [ ] **Step 3: Write minimal implementation**

Normalize email, hash the public token, apply Redis counter keyed by token/e-mail/IP hashes, insert with conflict-safe semantics and write `access.request.created` audit without storing raw IP.

- [ ] **Step 4: Run targeted tests**

Expected: all public request tests PASS.

- [ ] **Step 5: Record checkpoint**

Document endpoint, response anti-enumeration and rate limit in `docs/PROGRESSO.md`.

### Task 3: Administrative creation, approval and rejection

**Files:**
- Create: `backend/app/modules/access_requests/admin_router.py`
- Modify: `backend/app/api/router.py`
- Modify: `backend/app/modules/auth/router.py`
- Test: `backend/tests/integration/test_access_request_admin.py`

**Interfaces:**
- Consumes: `authorize_role`, `validate_csrf`, `enqueue_job` and existing invitations.
- Produces: `GET /api/v1/access/requests`, `PATCH /api/v1/access/requests/{id}` and `POST /api/v1/auth/pending-users`.

- [ ] **Step 1: Write failing authorization and transition tests**

```python
response = await admin.patch(f'/api/v1/access/requests/{request_id}',
    json={'decision': 'approved', 'role': 'member'}, headers={'X-CSRF-Token': csrf})
assert response.status_code == 200
assert response.json()['status'] == 'approved'
```

Add cases proving member receives 403, rejection cannot later approve, repeated approval returns the original invitation/job, and cross-tenant identifiers return 404.

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL with routes not found.

- [ ] **Step 3: Write minimal implementation**

Lock the request row, validate transition from `pending`, create one hashed invitation token on approval, enqueue `email.access_activation` with idempotency key `access-request:{id}`, and audit approval/rejection. The pending-user endpoint uses the same invitation-and-job service and never accepts a password field.

- [ ] **Step 4: Run targeted tests**

Expected: approval, rejection, idempotency, RBAC and tenant isolation PASS.

- [ ] **Step 5: Record checkpoint**

Update security and progress documents with the no-temporary-password decision.

### Task 4: Activation pages and full acceptance

**Files:**
- Create: `frontend/src/features/access/RequestAccessPage.tsx`
- Create: `frontend/src/features/access/ActivateAccountPage.tsx`
- Create: `frontend/src/features/access/ManageAccessRequestsPage.tsx`
- Modify: `frontend/src/app/router.tsx`
- Test: `frontend/src/features/access/AccessFlows.test.tsx`
- Modify: `docs/security/SECURITY_BASELINE.md`

**Interfaces:**
- Consumes: the public request, invitation acceptance and administrative endpoints.
- Produces: accessible pages for requesting, activating and deciding access.

- [ ] **Step 1: Write failing UI tests**

```tsx
render(<RequestAccessPage organizationToken="public-token" />)
await user.type(screen.getByLabelText(/e-mail/i), 'person@example.test')
await user.click(screen.getByRole('button', { name: /enviar solicitação/i }))
expect(await screen.findByText('Solicitação recebida para análise.')).toBeVisible()
```

Add activation password validation and admin approve/reject interaction tests.

- [ ] **Step 2: Run UI tests to verify they fail**

Run: `npm test -- AccessFlows.test.tsx`
Expected: FAIL because components do not exist.

- [ ] **Step 3: Implement minimal accessible UI**

Use labels, keyboard-accessible controls, generic public messages, disabled pending actions and existing visual tokens. Never display raw password, persisted token or internal rejection details.

- [ ] **Step 4: Run complete acceptance**

Run `scripts/verify.ps1`, rebuild Docker and run `tests/smoke/compose-health.ps1`. Expected: backend, frontend, PostgreSQL, Redis and Mailpit healthy with all tests passing.

- [ ] **Step 5: Record checkpoint**

Update roadmap and `docs/PROGRESSO.md`; do not initialize Git.
