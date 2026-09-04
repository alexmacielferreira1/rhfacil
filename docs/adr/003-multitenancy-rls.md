# ADR-003: multi-tenancy com RLS

- Estado: Aceita
- Data: 2026-08-29

## Contexto

Um SaaS atende várias empresas no mesmo sistema. Um filtro esquecido em uma consulta poderia revelar dados de outra empresa, portanto a proteção não pode depender apenas da disciplina de cada rota.

## Decisão

Usar `organization_id` como limite da empresa e aplicar duas camadas: autorização no FastAPI e Row-Level Security (RLS, política do PostgreSQL que filtra linhas) com `FORCE ROW LEVEL SECURITY`. Cada transação da aplicação define `app.current_tenant_id`; as políticas usam esse valor para leitura e escrita. O papel da aplicação não executa migrações nem ignora as políticas.

## Consequências

- Uma consulta sem filtro explícito continua restrita pelo banco.
- Testes de isolamento exercitam o papel real da aplicação.
- Trabalhos assíncronos descobrem empresas por função restrita e processam uma empresa por transação.
- Toda nova tabela com dados de cliente precisa incluir a empresa e receber política antes de ser aprovada.

## Alternativas consideradas

- Somente filtros na aplicação: rejeitados porque um único esquecimento causa vazamento entre clientes.
- Um banco por cliente desde a V1: adiado por custo operacional; poderá ser adotado para exigência contratual específica.
- Usuários globais sem associação explícita: rejeitados; permissões vivem na associação do usuário com a empresa.
