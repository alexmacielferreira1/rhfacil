# Gestão de Funcionários

Template versionado para criar produtos SaaS independentes, seguros e reproduzíveis.

## Criar uma cópia limpa

```powershell
powershell -ExecutionPolicy Bypass -File scripts/new-saas.ps1 `
  -Name "Nome do Novo SaaS" `
  -Destination "C:\caminho\NOVO_PROJETO"
```

O procedimento completo e as exclusões de segurança estão em [docs/NEW_SAAS.md](docs/NEW_SAAS.md).

Antes de implementar um produto, use o [Prompt Mestre para planejar um novo SaaS](docs/PROMPT_MESTRE_NOVO_SAAS.md). Ele é copiado pela Base para todos os projetos derivados.

As decisões que sustentam a arquitetura estão no [índice de ADRs](docs/adr/README.md).

O [relatório técnico compartilhável](RELATORIO_TECNICO_COMPARTILHAVEL_BASE_SAAS_V1.md) resume a implementação e as provas. O [resumo dos demais SaaS](RESUMO_DEMAIS_SAAS_PARA_IMAGENS.md) organiza os conceitos para criação de imagens.

A [conferência final dos pedidos](CONFERENCIA_FINAL_DOS_PEDIDOS.md) separa o que foi concluído na Base do que ainda pertence aos projetos derivados.

## Início rápido

```powershell
Copy-Item .env.example .env
docker compose up --build
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Serviços locais:

- Interface: http://localhost:5173
- API: http://localhost:8000/api/v1/health
- Documentação da API: http://localhost:8000/docs
- Caixa de e-mail local: http://localhost:8025

## Pré-requisitos

- Docker Desktop
- Python 3.14.7
- Poetry
- Node.js LTS

## Configuração local

O arquivo `.env.example` contém somente valores locais e descartáveis. Ele não contém credenciais de produção.

Quando o ambiente executável estiver concluído, crie a configuração local com:

```powershell
Copy-Item .env.example .env
```

Nunca reutilize a senha de demonstração em produção e nunca envie `.env` ao Git.

Se alguma porta estiver ocupada, altere somente `API_PORT`, `WEB_PORT` ou `MAILPIT_WEB_PORT` no `.env` local. PostgreSQL e Redis são vinculados apenas a `127.0.0.1` e nunca devem ser expostos publicamente.

Ambientes virtuais, `node_modules`, caches e `.env` são instalações locais. Uma nova cópia deve executar `poetry install` e `npm install`; copiar esses artefatos entre projetos causa incompatibilidades e não faz parte do template distribuível.

## Regra de independência

Cada cópia desta base deve possuir banco, segredos, usuários, uploads, integrações e repositório Git próprios. Atualizações futuras da base não sobrescrevem automaticamente projetos existentes.

Cada projeto derivado deve manter `docs/BASE_LINEAGE.md`, informando a versão de origem. Uma futura Base V2 será avaliada e migrada projeto por projeto, com testes e plano de reversão.
