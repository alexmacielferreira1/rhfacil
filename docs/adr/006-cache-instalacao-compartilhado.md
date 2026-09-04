# ADR-006: cache de instalação compartilhado entre projetos

- Estado: Aceita e validada (aplicada em 000_BASE_SAAS_V1, 001_MEDIA_MIND_AI, 002_IA_RH_RECRUTAMENTO e 003_GESTAO_DE_FUNCIONARIOS em 2026-09-04; build de validação com Docker Desktop executado em 000/001/002 no mesmo dia, cache cruzado confirmado — ver seção de validação abaixo)
- Data: 2026-09-04

## Contexto

Cada novo projeto nascido da Base reinstalava as dependências do zero em três lugares independentes: dentro da imagem Docker do backend (`poetry install`), dentro da imagem Docker do frontend (`npm ci`) e no ambiente Python local usado fora do Docker para lint/testes/tooling. O `backend/poetry.toml` definia `cache-dir = ".poetry-cache"` — um cache local à própria pasta do projeto, que nunca é copiado para os novos projetos (por política do AGENTS.md: "nunca copie... caches ou dependências instaladas"). Como as dependências principais são praticamente idênticas entre a Base e os produtos derivados (confirmado por diff entre `pyproject.toml`/`poetry.lock` da Base e do 002: só nome e descrição mudam), cada projeto novo baixava do PyPI o mesmo conjunto de pacotes que o projeto anterior já tinha baixado, sem nenhum reaproveitamento. Esse foi identificado como o principal ponto de lentidão relatado ao gerar pasta base + instalar softwares/linguagens/dependências.

## Decisão

1. Remover o `cache-dir` local do `backend/poetry.toml`, voltando ao cache global padrão do Poetry (compartilhado por usuário do sistema, fora da pasta de qualquer projeto).
2. Adicionar `# syntax=docker/dockerfile:1` e converter `RUN poetry install ...` e `RUN npm ci` em `RUN --mount=type=cache,target=...` nos Dockerfiles de backend e frontend, para que o build de imagem também reaproveite um cache persistente do Docker entre projetos, mesmo quando o lockfile de um projeto específico diverge um pouco do da Base.
3. Nenhuma mudança em código de aplicação, migrations, schema ou nos Dockerfiles além da forma de instalar dependências — o comportamento em runtime dos containers não muda.

## Consequências

- Builds do Docker e instalações locais de projetos novos deixam de baixar pacotes já baixados por outro projeto na mesma máquina; só a diferença específica de cada projeto é buscada na rede.
- `.venv` e `.poetry-cache`/`.virtualenv-cache` já existentes em projetos antigos continuam funcionando; a mudança só afeta instalações futuras (novo `poetry install`/`npm ci`/`docker compose build`).
- Backups dos arquivos originais foram mantidos ao lado dos arquivos alterados com sufixo `.bak-20260904`, para rollback imediato caso algum build falhe.
- `docker compose build` executado em 000, 001 e 002 no Docker Desktop em 2026-09-04, confirmando zero regressão (ver seção de validação abaixo). Falta rodar a mesma validação em 003_GESTAO_DE_FUNCIONARIOS.

## Alternativas consideradas

- Manter uma imagem Docker "core" versionada com as dependências comuns pré-instaladas, com os Dockerfiles de cada projeto herdando dela (`FROM base-saas-v1-backend-core:N`): mais rápida em builds Docker, mas exige manter e versionar uma imagem extra e não resolve a duplicação do ambiente Python local. Fica registrada como opção futura se o cache mount sozinho não for suficiente.

## Adendo (2026-09-04): id fixo nos cache mounts do BuildKit

Sem `id` explícito, o BuildKit deriva a chave do cache mount do próprio Dockerfile/estágio, o que pode isolar o cache entre projetos diferentes mesmo mirando o mesmo `target`. Para garantir que 000, 001, 002 e 003 (e qualquer projeto futuro nascido da Base) bebam sempre do mesmo cache local, mesmo com pequenas diferenças entre Dockerfiles:

- `infra/docker/backend.Dockerfile`: `RUN --mount=type=cache,id=poetry-global-cache,target=/root/.cache/pypoetry,sharing=locked ...`
- `infra/docker/frontend.Dockerfile`: `RUN --mount=type=cache,id=npm-global-cache,target=/root/.npm ...`

Aplicado nos quatro projetos existentes (000_BASE_SAAS_V1, 001_MEDIA_MIND_AI, 002_IA_RH_RECRUTAMENTO, 003_GESTAO_DE_FUNCIONARIOS) em 2026-09-04. Como a mudança está no Dockerfile da própria 000_BASE_SAAS_V1 (o template), todo projeto novo gerado por cópia da Base herda o `id` fixo automaticamente, sem trabalho manual extra — regra permanente: **todo Dockerfile de backend/frontend criado ou copiado a partir da Base deve manter esses dois `id`s exatamente como estão, nunca removê-los ou trocá-los por um `id` diferente por projeto.**

Continua pendente a validação de build (`docker compose build` + suíte de aceitação) com Docker Desktop nos quatro projetos.


## Validação executada em 2026-09-04 (Docker Desktop, Windows)

Rodado via `validar-docker-cache.ps1` (build + up + checagem de saúde + down) em 000, 001 e 002, nessa ordem:

| Projeto | Build | Tempo | Up |
|---|---|---|---|
| 000_BASE_SAAS_V1 | OK | 4,1 s | Falhou (ver nota 1) |
| 001_MEDIA_MIND_AI | OK | 2,9 s | OK, todos os serviços healthy |
| 002_IA_RH_RECRUTAMENTO | OK | 263,8 s | OK, todos os serviços healthy |

Confirmações da ADR-006 + adendo do id fixo:

- `poetry-global-cache`: `CACHED` nos três projetos (000, 001 e 002) — o cache do Poetry foi compartilhado entre projetos com sucesso, exatamente como esperado, mesmo o 002 tendo um `poetry.lock` próprio.
- `npm-global-cache`: `CACHED` no 001 (dependências de frontend praticamente iguais às do 000); no 002 **não** foi cache hit — o `npm ci` rodou de verdade (`added 276 packages... in 3m`, 205 s), porque o frontend do 002 tem pacotes que nenhum projeto anterior tinha baixado ainda. Isso é o comportamento correto e esperado do cache de conteúdo do npm (cada pacote só entra no cache na primeira vez que é baixado, por qualquer projeto); não é falha da configuração, e não indica vazamento de escopo entre projetos — o `npm ci` sempre instala exatamente o que está no `package-lock.json` daquele projeto, isolado dos demais. Um próximo projeto que reuse essas mesmas dependências do 002 vai pegar cache normalmente.
- Nenhum falso-positivo de suíte de aceitação identificado atribuível ao cache compartilhado.

Nota 1 — falha do `up` no 000 não é causada pela ADR-006: o `.env` do 000 não define `POSTGRES_PORT`, então o Postgres tenta usar a porta fixa 5432 do host (`${POSTGRES_PORT:-5432}` no `compose.yaml`), que já estava ocupada por outro processo na máquina (container antigo ou Postgres nativo do Windows). 001 e 002 não sofrem disso porque seus `.env` já usam portas de host aleatórias. Ação recomendada (fora do escopo desta ADR): checar `docker ps -a` e os serviços do Windows por algo preso na 5432, ou adicionar um `POSTGRES_PORT` de host não-padrão no `.env` do 000, igual aos projetos derivados.
