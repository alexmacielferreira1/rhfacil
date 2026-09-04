# ADR-001: stack e monólito modular

- Estado: Aceita
- Data: 2026-08-29

## Contexto

A base precisa iniciar produtos diferentes com baixo custo operacional, testes locais reproduzíveis e limites claros entre domínios. Separar serviços cedo demais multiplicaria deploys, contratos de rede e pontos de falha antes de existir escala que justificasse isso.

## Decisão

Usar Python 3.14, FastAPI, SQLAlchemy assíncrono, PostgreSQL 16, Alembic e Poetry no backend; React, TypeScript e Vite no frontend; Redis para limites e coordenação temporária; Docker Compose para desenvolvimento. O backend permanece um monólito modular: um processo implantável, com módulos de negócio separados sob `app/modules`.

## Consequências

- Uma cópia inicia com poucas peças operacionais e uma única migração de banco ordenada.
- Limites de módulo permitem extrair um serviço no futuro sem pagar esse custo agora.
- Falha ou deploy do backend ainda afeta todos os módulos; escala seletiva exige extração posterior.
- Cada produto derivado pode acrescentar módulos próprios sem contaminar a Base V1.

## Alternativas consideradas

- Microserviços desde o início: rejeitados por complexidade prematura de rede, observabilidade e consistência.
- Biblioteca central compartilhada entre todos os SaaS: adiada até existirem contratos estáveis e repetidos.
- Supabase como plataforma principal: não adotado; autenticação, banco e isolamento permanecem controlados pelo projeto sem depender desse fornecedor.
