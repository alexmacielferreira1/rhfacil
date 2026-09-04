# Criar um novo SaaS a partir da Base V1

Antes de começar, leia `DOCUMENTATION_POLICY.md`. Código funcional sem inventário, preservação e paridade documental não encerra uma migração.

Use um destino que ainda não exista:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/new-saas.ps1 `
  -Name "Nome do Novo SaaS" `
  -Destination "C:\caminho\NOVO_PROJETO"
```

O nome e o destino são os únicos dados obrigatórios. O inicializador sugere identificador técnico e portas locais, personaliza o Compose e `.env.example`, atualiza `docs/BASE_LINEAGE.md` e cria `.template-origin.json`.

Antes de escrever código, preencha e execute o [Prompt Mestre para planejar um novo SaaS](PROMPT_MESTRE_NOVO_SAAS.md). Registre o resultado nos documentos de contexto e requisitos da nova cópia.

## O que não é copiado

- `.git` ou qualquer repositório/identidade anterior;
- `.env` e variações potencialmente secretas;
- `.codex`, `.claude`, `.agents` e configurações pessoais;
- `.venv`, Poetry cache, `node_modules` e builds;
- caches de testes, cobertura e Python;
- uploads, backups, bancos, dumps e arquivos SQLite.

O script recusa destino existente. Ele não instala dependências, não cria usuários, não copia bancos e não inicia Git.

## Preparar a nova cópia

```powershell
cd "C:\caminho\NOVO_PROJETO"
Copy-Item .env.example .env
cd backend
poetry install
cd ..\frontend
npm install
cd ..
docker compose up --build -d
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Os valores do `.env.example` são apenas para desenvolvimento local. Gere segredos exclusivos e use serviços gerenciados/protegidos antes da produção. Cada cópia evolui independentemente: uma futura Base V2 não a altera automaticamente.
