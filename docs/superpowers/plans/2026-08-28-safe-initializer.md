# Safe SaaS Initializer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar uma cópia independente, limpa e identificada da Base V1 exigindo somente nome e destino.

**Architecture:** Um script PowerShell valida destino novo, normaliza identificador, sugere portas determinísticas e copia por allow/exclude seguro. A cópia recebe manifesto de origem e configurações locais próprias, sem instalar dependências nem criar Git.

**Tech Stack:** PowerShell 7/Windows PowerShell, robocopy, JSON, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-08-26-base-saas-v1-design.md`

## Global Constraints

- Nunca sobrescrever destino existente.
- Nunca copiar `.git`, `.env`, ambientes, dependências, caches, uploads, backups, bancos ou configurações pessoais de IA.
- Nunca gerar segredo ou credencial de produção; valores locais continuam descartáveis.
- Não inicializar Git nem instalar dependências.
- Registrar Base V1 como origem e política sem atualização automática.

### Task 1: Cópia limpa e identidade

**Files:**
- Create: `scripts/new-saas.ps1`
- Create: `tests/smoke/new-saas.ps1`
- Modify: `compose.yaml`
- Modify: `.env.example`

**Interfaces:**
- Consumes: `-Name <string>` e `-Destination <caminho-novo>`.
- Produces: cópia limpa, `.template-origin.json`, nome/slug e portas locais sugeridas.

- [x] Criar smoke que executa o inicializador em destino descartável e valida conteúdo, exclusões, manifesto e portas.
- [x] Executar e confirmar falha porque `scripts/new-saas.ps1` não existe.
- [x] Parametrizar portas PostgreSQL/Redis no Compose e exemplo de ambiente.
- [x] Implementar validação, normalização, cópia com exclusões e substituições de identidade.
- [x] Executar o smoke e confirmar destino limpo; testar que destino existente é recusado.

### Task 2: Prova executável e documentação

**Files:**
- Create: `docs/NEW_SAAS.md`
- Modify: `README.md`
- Modify: `tests/smoke/test_template_hygiene.ps1`
- Modify: `docs/PROGRESSO.md`

**Interfaces:**
- Consumes: cópia criada pela Task 1.
- Produces: instrução de criação, instalação posterior e validação da cópia.

- [x] Documentar comando, exclusões, linhagem e próximos passos `poetry install`, `npm install`, `.env` e verificação.
- [x] Estender higiene para proteger o próprio template de artefatos proibidos sem ler diretórios excluídos.
- [x] Criar uma cópia descartável, executar higiene/Compose nela e removê-la com alvo absoluto validado.
- [ ] Executar verificação integral da Base e registrar evidências sem Git.
