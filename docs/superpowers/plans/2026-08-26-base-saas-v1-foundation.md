# Base SaaS V1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar uma aplicação mínima completa, reproduzível e testada, com API FastAPI, frontend React, PostgreSQL, Redis, Mailpit e execução por Docker.

**Architecture:** Um monorepositório independente contém um backend assíncrono modular e um frontend organizado por funcionalidades. A primeira fatia vertical oferece configuração validada, endpoint de saúde, tela de estado dos serviços e testes locais; módulos de identidade e negócio entram apenas nas fases seguintes.

**Tech Stack:** Python 3.14.7, Poetry, FastAPI, Pydantic Settings, SQLAlchemy assíncrono, PostgreSQL, Alembic, Redis, React, TypeScript, Vite, TanStack Query, Vitest, Testing Library, Docker Compose e Mailpit.

**Spec:** `docs/superpowers/specs/2026-08-26-base-saas-v1-design.md`

## Global Constraints

- Python inicial fixado em 3.14.7; nenhuma atualização de versão principal é automática.
- A aplicação é independente de fornecedor externo.
- Segredos reais, bancos, usuários, uploads, caches, ambientes virtuais e identidades Git não pertencem ao template.
- Projetos em `EXEMPLOS QUE TENHO` e originais no Desktop são somente leitura.
- Desenvolvimento local usa Docker, mas backend e frontend também podem executar diretamente.
- Código e documentação usam UTF-8 e caminhos compatíveis com Windows.
- Dependências pesadas de IA não pertencem à fundação.
- Cada tarefa começa por um teste observável, implementa o mínimo e termina com a suíte relevante verde.

---

## Mapa de arquivos da fundação

```text
000_BASE_SAAS_V1/
├── backend/
│   ├── app/
│   │   ├── api/router.py
│   │   ├── core/config.py
│   │   ├── core/database.py
│   │   ├── core/redis.py
│   │   ├── modules/health/router.py
│   │   ├── modules/health/schemas.py
│   │   └── main.py
│   ├── migrations/env.py
│   ├── tests/api/test_health.py
│   ├── tests/core/test_config.py
│   ├── tests/integration/test_services.py
│   ├── alembic.ini
│   └── pyproject.toml
├── frontend/
│   ├── src/app/App.tsx
│   ├── src/app/providers.tsx
│   ├── src/features/health/HealthPage.tsx
│   ├── src/features/health/health-api.ts
│   ├── src/features/health/HealthPage.test.tsx
│   ├── src/lib/api-client.ts
│   ├── src/test/setup.ts
│   ├── src/main.tsx
│   ├── package.json
│   └── vite.config.ts
├── infra/docker/backend.Dockerfile
├── infra/docker/frontend.Dockerfile
├── scripts/verify.ps1
├── tests/smoke/compose-health.ps1
├── compose.yaml
├── .env.example
├── .gitignore
├── Makefile
└── README.md
```

Responsabilidades:

- `core/config.py` é a única fonte de configuração do backend.
- `core/database.py` cria e encerra o pool PostgreSQL.
- `core/redis.py` cria e encerra o cliente Redis.
- `modules/health` expõe somente o contrato de saúde.
- `api/router.py` agrega módulos HTTP sem conter regra de negócio.
- `health-api.ts` contém a integração HTTP da funcionalidade de saúde.
- `HealthPage.tsx` renderiza estados de carregamento, sucesso e falha.
- `compose.yaml` descreve somente serviços locais reproduzíveis.
- `verify.ps1` executa a verificação completa da fundação.

---

### Task 1: Contrato do repositório e proteção contra artefatos locais

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `tests/smoke/test_template_hygiene.ps1`

**Interfaces:**
- Consumes: nenhuma.
- Produces: variáveis `APP_ENV`, `APP_NAME`, `API_PORT`, `WEB_PORT`, `POSTGRES_*`, `REDIS_URL`, `DATABASE_URL` e `MAILPIT_*`; regras de higiene usadas por todas as tarefas.

- [ ] **Step 1: Criar o teste de higiene que falha enquanto o contrato não existe**

```powershell
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$required = @('.gitignore', '.env.example', 'README.md')
foreach ($name in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $name))) {
        throw "Arquivo obrigatório ausente: $name"
    }
}

$forbidden = @('.env', '.git', '.venv', 'node_modules', '__pycache__')
foreach ($name in $forbidden) {
    if (Test-Path -LiteralPath (Join-Path $root $name)) {
        throw "Artefato proibido na raiz do template: $name"
    }
}
```

- [ ] **Step 2: Executar o teste e confirmar a falha**

Run: `powershell -ExecutionPolicy Bypass -File tests/smoke/test_template_hygiene.ps1`

Expected: FAIL informando que `.gitignore`, `.env.example` ou `README.md` está ausente.

- [ ] **Step 3: Criar o contrato mínimo do ambiente**

`.env.example` deve conter valores não secretos:

```dotenv
APP_ENV=development
APP_NAME=Base SaaS V1
API_PORT=8000
WEB_PORT=5173
POSTGRES_DB=base_saas
POSTGRES_USER=base_saas
POSTGRES_PASSWORD=local_only_change_me
DATABASE_URL=postgresql+asyncpg://base_saas:local_only_change_me@postgres:5432/base_saas
REDIS_URL=redis://redis:6379/0
MAILPIT_SMTP_HOST=mailpit
MAILPIT_SMTP_PORT=1025
MAILPIT_WEB_PORT=8025
```

`.gitignore` deve excluir, no mínimo:

```gitignore
.env
.env.*
!.env.example
.git/
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
htmlcov/
.coverage
node_modules/
dist/
coverage/
*.log
uploads/
storage/
backups/
*.sqlite3
```

O `README.md` deve declarar que a pasta é um template, listar os pré-requisitos Docker Desktop, Python 3.14.7, Poetry e Node.js LTS, e afirmar que `.env.example` contém somente credenciais locais descartáveis.

- [ ] **Step 4: Executar o teste de higiene**

Run: `powershell -ExecutionPolicy Bypass -File tests/smoke/test_template_hygiene.ps1`

Expected: PASS sem saída de erro.

- [ ] **Step 5: Registrar checkpoint local**

Não executar `git init`. Registrar no plano que o checkpoint está pronto para commit quando o novo repositório for autorizado.

---

### Task 2: Configuração validada e aplicação FastAPI mínima

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/router.py`
- Create: `backend/app/modules/__init__.py`
- Create: `backend/app/modules/health/__init__.py`
- Create: `backend/app/modules/health/schemas.py`
- Create: `backend/app/modules/health/router.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/core/test_config.py`
- Create: `backend/tests/api/test_health.py`

**Interfaces:**
- Consumes: variáveis definidas em `.env.example`.
- Produces: `Settings`, `get_settings() -> Settings`, `HealthResponse`, `GET /api/v1/health`, `create_app() -> FastAPI`.

- [ ] **Step 1: Escrever testes de configuração e saúde**

```python
from app.core.config import Settings


def test_settings_rejects_unknown_environment() -> None:
    try:
        Settings(app_env='invalid', database_url='postgresql+asyncpg://x:x@x/x')
    except ValueError as exc:
        assert 'app_env' in str(exc)
    else:
        raise AssertionError('invalid environment was accepted')
```

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_contract() -> None:
    with TestClient(create_app()) as client:
        response = client.get('/api/v1/health')

    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'service': 'Base SaaS V1',
        'environment': 'test',
    }
```

- [ ] **Step 2: Executar os testes e confirmar falha de importação**

Run: `cd backend; poetry run pytest tests/core/test_config.py tests/api/test_health.py -v`

Expected: FAIL porque `app.core.config` e `app.main` ainda não existem.

- [ ] **Step 3: Definir dependências e ferramentas do backend**

`pyproject.toml` deve declarar Python `>=3.14,<3.15`, FastAPI, Uvicorn, SQLAlchemy asyncio, Psycopg, Alembic, Pydantic Settings, Redis, HTTPX e dependências de desenvolvimento Pytest, pytest-asyncio, pytest-cov, Ruff e mypy. Configurar Ruff com linha 100, mypy estrito e Pytest restrito a `tests`.

- [ ] **Step 4: Implementar configuração e endpoint mínimos**

```python
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_env: Literal['development', 'test', 'production'] = 'development'
    app_name: str = 'Base SaaS V1'
    database_url: str
    redis_url: str = 'redis://localhost:6379/0'


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

```python
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
```

`create_app()` deve construir o FastAPI sem efeitos colaterais de importação, incluir o roteador em `/api/v1` e retornar o contrato de saúde usando `get_settings()`.

- [ ] **Step 5: Executar testes e verificações estáticas**

Run: `cd backend; poetry run pytest tests/core/test_config.py tests/api/test_health.py -v`

Expected: PASS.

Run: `cd backend; poetry run ruff check .; poetry run mypy app`

Expected: ambos PASS.

- [ ] **Step 6: Registrar checkpoint local**

Não criar Git. Anotar os arquivos concluídos para o futuro commit `feat: bootstrap FastAPI application`.

---

### Task 3: PostgreSQL, Redis e ciclo de vida assíncrono

**Files:**
- Create: `backend/app/core/database.py`
- Create: `backend/app/core/redis.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/modules/health/schemas.py`
- Modify: `backend/app/modules/health/router.py`
- Create: `backend/tests/integration/test_services.py`

**Interfaces:**
- Consumes: `Settings.database_url`, `Settings.redis_url`.
- Produces: `create_engine(settings) -> AsyncEngine`, `create_redis(settings) -> Redis`, lifespan que armazena `db_engine` e `redis` em `app.state`, resposta de saúde com `database` e `redis`.

- [ ] **Step 1: Escrever teste de integração dos serviços**

```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_health_reports_database_and_redis() -> None:
    app = create_app()
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url='http://test'
        ) as client:
            response = await client.get('/api/v1/health/services')

    assert response.status_code == 200
    assert response.json()['services'] == {
        'database': 'ok',
        'redis': 'ok',
    }
```

- [ ] **Step 2: Executar com PostgreSQL e Redis ativos e confirmar falha**

Run: `cd backend; poetry run pytest tests/integration/test_services.py -v`

Expected: FAIL com rota `/api/v1/health/services` ausente.

- [ ] **Step 3: Implementar fábricas e lifespan**

`create_engine` deve usar `create_async_engine` com `pool_pre_ping=True`. `create_redis` deve usar cliente assíncrono com respostas decodificadas. O lifespan deve criar recursos no início e executar `engine.dispose()` e `redis.aclose()` no encerramento.

O endpoint `/health/services` deve executar `SELECT 1` e `PING`, devolver `200` quando ambos responderem e `503` com estado individual quando algum serviço falhar. Detalhes de exceção nunca entram na resposta.

- [ ] **Step 4: Executar teste de integração**

Run: `cd backend; poetry run pytest tests/integration/test_services.py -v`

Expected: PASS com PostgreSQL e Redis reais.

- [ ] **Step 5: Executar a suíte do backend**

Run: `cd backend; poetry run pytest -v; poetry run ruff check .; poetry run mypy app`

Expected: todos PASS.

- [ ] **Step 6: Registrar checkpoint local**

Preparar futuro commit `feat: add async PostgreSQL and Redis lifecycle` sem iniciar Git.

---

### Task 4: Alembic reproduzível e migration inicial

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/migrations/env.py`
- Create: `backend/migrations/script.py.mako`
- Create: `backend/migrations/versions/20260826_0001_bootstrap.py`
- Create: `backend/tests/integration/test_migrations.py`

**Interfaces:**
- Consumes: `Settings.database_url` e metadata futura importada por `migrations/env.py`.
- Produces: migration `20260826_0001` que cria extensão necessária e tabela de controle `app_schema_version` sem dados de negócio.

- [ ] **Step 1: Escrever teste de banco vazio até head**

```python
from sqlalchemy import text


async def test_migration_creates_schema_version(async_engine) -> None:
    async with async_engine.connect() as connection:
        exists = await connection.scalar(
            text("select to_regclass('public.app_schema_version')")
        )
    assert exists == 'app_schema_version'
```

- [ ] **Step 2: Executar migration e teste para confirmar falha inicial**

Run: `cd backend; poetry run alembic upgrade head; poetry run pytest tests/integration/test_migrations.py -v`

Expected: FAIL porque a configuração do Alembic ou a tabela ainda não existe.

- [ ] **Step 3: Implementar Alembic assíncrono e migration**

A migration deve criar:

```python
op.create_table(
    'app_schema_version',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('installed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
)
```

O downgrade deve remover somente `app_schema_version`. `env.py` deve ler a URL das configurações e executar migrations com conexão assíncrona.

- [ ] **Step 4: Provar upgrade, downgrade e novo upgrade**

Run: `cd backend; poetry run alembic upgrade head; poetry run pytest tests/integration/test_migrations.py -v; poetry run alembic downgrade base; poetry run alembic upgrade head`

Expected: todos os comandos PASS.

- [ ] **Step 5: Registrar checkpoint local**

Preparar futuro commit `feat: add reproducible async migrations` sem iniciar Git.

---

### Task 5: Frontend mínimo e contrato com a API

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/app/App.tsx`
- Create: `frontend/src/app/providers.tsx`
- Create: `frontend/src/lib/api-client.ts`
- Create: `frontend/src/features/health/health-api.ts`
- Create: `frontend/src/features/health/HealthPage.tsx`
- Create: `frontend/src/features/health/HealthPage.test.tsx`
- Create: `frontend/src/test/setup.ts`
- Create: `frontend/src/styles/index.css`

**Interfaces:**
- Consumes: `GET /api/v1/health` e `GET /api/v1/health/services`.
- Produces: `getHealth(): Promise<HealthStatus>` e página que apresenta API, PostgreSQL e Redis.

- [ ] **Step 1: Escrever teste da página de saúde**

```tsx
import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'

import { HealthPage } from './HealthPage'
import * as healthApi from './health-api'

vi.spyOn(healthApi, 'getHealth').mockResolvedValue({
  api: 'ok',
  database: 'ok',
  redis: 'ok',
})

test('shows every foundation service as operational', async () => {
  render(<HealthPage />)
  expect(await screen.findByText('API operacional')).toBeInTheDocument()
  expect(screen.getByText('PostgreSQL operacional')).toBeInTheDocument()
  expect(screen.getByText('Redis operacional')).toBeInTheDocument()
})
```

- [ ] **Step 2: Executar o teste e confirmar falha**

Run: `cd frontend; npm test -- --run src/features/health/HealthPage.test.tsx`

Expected: FAIL porque `HealthPage` e `health-api` ainda não existem.

- [ ] **Step 3: Criar configuração e dependências do frontend**

`package.json` deve definir scripts `dev`, `build`, `lint`, `typecheck` e `test`. Dependências devem incluir React, React DOM, TanStack Query e Zod; dependências de desenvolvimento devem incluir TypeScript, Vite, plugin React, ESLint, Vitest, JSDOM e Testing Library.

- [ ] **Step 4: Implementar cliente e página**

`api-client.ts` deve usar `fetch` com `credentials: 'include'`, timeout via `AbortController` e erro tipado sem incluir corpo sensível. `health-api.ts` deve combinar os dois endpoints e produzir:

```ts
export type HealthStatus = {
  api: 'ok' | 'error'
  database: 'ok' | 'error'
  redis: 'ok' | 'error'
}
```

`HealthPage` deve tratar carregamento, sucesso e falha e usar texto visível além de cor para acessibilidade.

- [ ] **Step 5: Executar testes e build**

Run: `cd frontend; npm test -- --run; npm run typecheck; npm run lint; npm run build`

Expected: todos PASS.

- [ ] **Step 6: Registrar checkpoint local**

Preparar futuro commit `feat: add React foundation health page` sem iniciar Git.

---

### Task 6: Ambiente Docker completo

**Files:**
- Create: `infra/docker/backend.Dockerfile`
- Create: `infra/docker/frontend.Dockerfile`
- Create: `compose.yaml`
- Create: `tests/smoke/compose-health.ps1`
- Modify: `README.md`

**Interfaces:**
- Consumes: `.env.example`, backend na porta interna 8000, frontend na 5173, PostgreSQL 5432, Redis 6379 e Mailpit 1025/8025.
- Produces: serviços `postgres`, `redis`, `mailpit`, `backend` e `frontend`; teste de fumaça HTTP.

- [ ] **Step 1: Escrever o teste de fumaça antes do Compose**

```powershell
$api = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/health' -TimeoutSec 10
if ($api.status -ne 'ok') { throw 'API não está saudável' }

$web = Invoke-WebRequest -Uri 'http://localhost:5173' -TimeoutSec 10
if ($web.StatusCode -ne 200) { throw 'Frontend não respondeu 200' }

$mailpit = Invoke-WebRequest -Uri 'http://localhost:8025/api/v1/info' -TimeoutSec 10
if ($mailpit.StatusCode -ne 200) { throw 'Mailpit não está saudável' }
```

- [ ] **Step 2: Executar e confirmar falha de conexão**

Run: `powershell -ExecutionPolicy Bypass -File tests/smoke/compose-health.ps1`

Expected: FAIL porque os serviços ainda não existem.

- [ ] **Step 3: Implementar imagens e Compose**

O Compose deve usar healthchecks, volumes nomeados, rede interna, dependências condicionadas à saúde e somente portas necessárias expostas ao host. PostgreSQL e Redis não recebem credenciais de produção. Backend executa migrations antes de servir; frontend aponta para a API por configuração.

Os Dockerfiles devem usar usuário não-root, copiar apenas manifests antes do código para aproveitar cache e ter comandos explícitos. Nenhuma imagem inclui `.env`, `.git`, caches ou dados dos exemplos.

- [ ] **Step 4: Construir e iniciar serviços**

Run: `Copy-Item .env.example .env; docker compose up --build -d`

Expected: cinco serviços iniciados; `docker compose ps` mostra serviços saudáveis ou em execução conforme o healthcheck.

- [ ] **Step 5: Executar teste de fumaça**

Run: `powershell -ExecutionPolicy Bypass -File tests/smoke/compose-health.ps1`

Expected: PASS.

- [ ] **Step 6: Encerrar sem excluir volumes**

Run: `docker compose down`

Expected: contêineres e rede removidos; volumes preservados.

- [ ] **Step 7: Remover o `.env` local descartável**

Run: `Remove-Item -LiteralPath .env`

Expected: `.env` ausente e `.env.example` preservado.

- [ ] **Step 8: Registrar checkpoint local**

Preparar futuro commit `feat: add reproducible local stack` sem iniciar Git.

---

### Task 7: Verificação única da fundação

**Files:**
- Create: `scripts/verify.ps1`
- Modify: `README.md`
- Modify: `tests/smoke/test_template_hygiene.ps1`

**Interfaces:**
- Consumes: comandos de teste definidos nas tarefas 1 a 6.
- Produces: `scripts/verify.ps1`, o único comando de aceitação da fundação.

- [ ] **Step 1: Estender o teste de higiene**

Adicionar verificação recursiva que falha se encontrar `.env`, `.git`, `.venv`, `node_modules`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `dist`, `htmlcov`, uploads, backups ou arquivos SQLite dentro do template, exceto artefatos transitórios criados e removidos pelo próprio processo de verificação.

- [ ] **Step 2: Criar o orquestrador de verificação**

```powershell
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

& powershell -ExecutionPolicy Bypass -File (Join-Path $root 'tests/smoke/test_template_hygiene.ps1')

Push-Location (Join-Path $root 'backend')
try {
    poetry run ruff check .
    poetry run mypy app
    poetry run pytest -v
} finally { Pop-Location }

Push-Location (Join-Path $root 'frontend')
try {
    npm run lint
    npm run typecheck
    npm test -- --run
    npm run build
} finally { Pop-Location }
```

O script deve propagar qualquer código de falha e remover apenas artefatos que ele próprio gerar. Não deve apagar volumes, bancos ou arquivos do usuário.

- [ ] **Step 3: Executar a verificação completa**

Run: `powershell -ExecutionPolicy Bypass -File scripts/verify.ps1`

Expected: backend, frontend e higiene PASS.

- [ ] **Step 4: Executar a prova integrada por Docker**

Run: `Copy-Item .env.example .env; docker compose up --build -d; powershell -ExecutionPolicy Bypass -File tests/smoke/compose-health.ps1; docker compose down; Remove-Item -LiteralPath .env`

Expected: teste de fumaça PASS e `.env` removido ao final.

- [ ] **Step 5: Atualizar o README com o caminho feliz**

Documentar exatamente:

```powershell
Copy-Item .env.example .env
docker compose up --build
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Incluir URLs da interface, API, documentação local e Mailpit, além de solução para portas ocupadas e instrução explícita para nunca usar as credenciais locais em produção.

- [ ] **Step 6: Registrar aceite da fase**

A fundação só está concluída quando `scripts/verify.ps1` e `tests/smoke/compose-health.ps1` passam em uma inicialização limpa. Preparar futuro commit `test: verify foundation end to end` sem iniciar Git.

---

## Aceite da fase

- A raiz contém somente arquivos pertencentes ao template.
- Backend inicia com Python 3.14.7 e configuração validada.
- PostgreSQL e Redis são verificados por integração real.
- Migrations funcionam de banco vazio até `head`.
- Frontend apresenta o estado da plataforma e cobre sucesso e falha.
- Docker inicia API, frontend, PostgreSQL, Redis e Mailpit.
- Um comando executa lint, tipos, testes e build.
- Nenhum projeto de exemplo foi alterado.
- Nenhuma identidade Git foi criada.
