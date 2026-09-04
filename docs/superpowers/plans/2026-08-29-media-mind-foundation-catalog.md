# Media Mind Foundation and Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o projeto independente `001_MEDIA_MIND_AI` e entregar o primeiro recorte funcional multi-tenant de produções, assets e bibliotecas sobre a Base V1.

**Architecture:** O inicializador cria uma cópia limpa da Base. O domínio de catálogo entra em migrations e módulos novos, sempre com `organization_id`, RLS forçado e rotas autenticadas. A referência antiga informa campos e comportamento, mas nenhum arquivo de execução é copiado diretamente nesta fase.

**Tech Stack:** Python 3.14, FastAPI 0.136, SQLAlchemy assíncrono, PostgreSQL 16/RLS, Alembic, React 19, TypeScript, Vite, pytest e Docker Compose.

**Spec:** `docs/superpowers/specs/2026-08-29-media-mind-migration-design.md`

## Global Constraints

- `EXEMPLOS QUE TENHO/MediaMindAI` é somente leitura.
- O destino exato é `C:\Users\Alex\Desktop\PROJETOS SAAS\001_MEDIA_MIND_AI`.
- Não copiar `.git`, `.env`, banco, mídia, cache, dependências instaladas ou credenciais sociais.
- Não configurar Git/GitHub/Claude/Codex.
- Toda tabela do produto usa `organization_id` e RLS forçado.
- Toda escrita autenticada usa CSRF e toda administração respeita RBAC.
- O primeiro marco não executa publicação social nem modelos locais de IA.

---

### Task 1: Projeto limpo e linhagem

**Files:**
- Create: `001_MEDIA_MIND_AI/**` por `000_BASE_SAAS_V1/scripts/new-saas.ps1`
- Modify: `001_MEDIA_MIND_AI/docs/BASE_LINEAGE.md`
- Create: `001_MEDIA_MIND_AI/docs/migration/LEGACY_INVENTORY.md`
- Create: `001_MEDIA_MIND_AI/docs/migration/FEATURE_PARITY_MATRIX.md`
- Test: `001_MEDIA_MIND_AI/tests/smoke/test_template_hygiene.ps1`

**Interfaces:**
- Consumes: `new-saas.ps1 -Name -Destination`.
- Produces: projeto independente com slug `media-mind-ai`, portas próprias e inventário auditável.

- [ ] Executar o inicializador com nome `Media Mind AI` e destino exato.
- [ ] Confirmar que o destino não contém `.git`, `.env`, `.venv`, `node_modules`, SQLite ou mídia da referência.
- [ ] Registrar a referência somente leitura, os 386 arquivos inventariados e a data da Base V1.
- [ ] Criar matriz inicial com estados `preservar`, `substituir`, `mock sinalizado`, `futuro` e `não aplicável`.
- [ ] Executar higiene e `docker compose config` no novo projeto.

### Task 2: Vocabulário e esquema do catálogo

**Files:**
- Create: `backend/migrations/versions/20260829_0011_media_catalog.py`
- Create: `backend/tests/integration/test_media_catalog_schema.py`
- Create: `backend/app/modules/media_catalog/__init__.py`

**Interfaces:**
- Produces: tabelas `media_productions`, `media_libraries`, `media_assets` e `media_library_assets`.
- Estados de asset: `pending`, `indexed`, `reviewing`, `reviewed`, `error`, `archived`.

- [ ] Escrever teste vermelho que exige tabelas, constraints, índices e RLS forçado.
- [ ] Executar o teste e confirmar falha por tabelas ausentes.
- [ ] Criar migration reversível com UUIDs, timestamps, relações tenant-scoped e constraints.
- [ ] Aplicar Alembic e aprovar o teste de esquema.
- [ ] Provar isolamento cruzado usando o papel restrito da aplicação.

### Task 3: Produções

**Files:**
- Create: `backend/app/modules/media_catalog/production_schemas.py`
- Create: `backend/app/modules/media_catalog/production_router.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/integration/test_media_productions.py`

**Interfaces:**
- Produces: `POST /api/v1/media/productions`, `GET /api/v1/media/productions` e `GET/PATCH /api/v1/media/productions/{id}`.
- Campos iniciais: `name`, `description`, `status`, `program_name`, `episode`, `scheduled_at`.

- [ ] Escrever testes vermelhos de criação, listagem, edição, CSRF e isolamento.
- [ ] Implementar schemas com limites de tamanho e status explícitos.
- [ ] Implementar rotas autenticadas e consultas sempre vinculadas à organização atual.
- [ ] Auditar criação e alteração sem armazenar conteúdo desnecessário no evento.
- [ ] Executar testes, Ruff e mypy.

### Task 4: Bibliotecas e assets

**Files:**
- Create: `backend/app/modules/media_catalog/library_schemas.py`
- Create: `backend/app/modules/media_catalog/library_router.py`
- Create: `backend/app/modules/media_catalog/asset_schemas.py`
- Create: `backend/app/modules/media_catalog/asset_router.py`
- Create: `backend/tests/integration/test_media_libraries.py`
- Create: `backend/tests/integration/test_media_assets.py`

**Interfaces:**
- Produces: CRUD protegido de bibliotecas; criação/listagem/detalhe/edição de metadados de assets; associação asset-biblioteca.
- Consumes: arquivo liberado de `stored_files` quando um asset apontar para binário real.

- [ ] Escrever testes vermelhos de biblioteca, asset, associação, status e tenant.
- [ ] Implementar bibliotecas sem caminhos físicos fornecidos pelo usuário.
- [ ] Implementar metadados editoriais e técnicos do asset sem servir `/media` público.
- [ ] Exigir arquivo liberado quando `stored_file_id` for informado.
- [ ] Executar testes e regressão do catálogo.

### Task 5: Primeiro frontend do produto

**Files:**
- Modify: `frontend/src/app/App.tsx`
- Create: `frontend/src/features/media/MediaDashboardPage.tsx`
- Create: `frontend/src/features/media/ProductionsPage.tsx`
- Create: `frontend/src/features/media/AssetsPage.tsx`
- Create: `frontend/src/features/media/media-api.ts`
- Create: `frontend/src/features/media/MediaCatalog.test.tsx`

**Interfaces:**
- Consumes: rotas de produções, bibliotecas e assets.
- Produces: navegação autenticada inicial com estados vazio, carregando, erro e dados.

- [ ] Escrever teste vermelho da navegação e estados observáveis.
- [ ] Aplicar identidade visual Media Mind sem copiar bypass de login.
- [ ] Conectar páginas às APIs reais; nenhum dado mock será exibido sem selo explícito.
- [ ] Executar Vitest, ESLint, TypeScript e build.

### Task 6: Aceitação do primeiro marco

**Files:**
- Modify: `docs/migration/FEATURE_PARITY_MATRIX.md`
- Modify: `docs/PROGRESSO.md`
- Create: `docs/migration/MILESTONE_01_REPORT.md`

**Interfaces:**
- Produces: evidência reproduzível para iniciar o plano de ingest.

- [ ] Executar verificação completa do projeto.
- [ ] Criar banco vazio e aplicar todas as migrations.
- [ ] Reconstruir Docker nas portas próprias e aprovar saúde dos seis serviços.
- [ ] Atualizar a matriz somente com evidência observada.
- [ ] Registrar lacunas e preparar o plano separado de ingest seguro.
