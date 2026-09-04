# Contexto atual

Módulo de **People/Employees + Talent & Career** do "AI People OS" — a metade do sistema de RH
que trata da relação interna com o colaborador depois da contratação (o outro módulo,
Recruitment/ATS, é o `002_IA_RH_RECRUTAMENTO`, projeto irmão derivado da mesma Base).

Sistema de RH pequeno/médio (até ~100 funcionários na primeira versão). Compartilha conceito de
autenticação, usuários, empresa, cargos e histórico com o 002, mas com banco, permissões e
experiências completamente separados — não há um módulo único "employees" fundindo os dois
produtos.

Handoff de entrada: quando um candidato é contratado no 002, ocorre uma transição controlada
Candidato → Colaborador (Employee), reaproveitando apenas os dados apropriados da candidatura; a
partir daí o histórico do colaborador é totalmente independente do processo seletivo que o
originou.

Portal do colaborador organizado em 4 blocos: Identidade e trajetória, Desempenho, Desenvolvimento
e Carreira (com mapa de carreira, próximo cargo sugerido e competências faltantes).

Dashboard de RH é módulo central, não card decorativo — e **não possui dados próprios**: todo
indicador é calculado em cima das entidades reais (avaliações, PDIs, treinamentos, metas,
competências, promoções), evitando números duplicados/inconsistentes. Deve permitir mudar o
contexto de análise (empresa toda, setor, equipe, indivíduo).

Perguntas que a camada de IA deveria conseguir responder (isolada do resto da aplicação, para
trocar modelo/provedor sem reescrever o sistema): quem está pronto para uma promoção/mudança de
cargo, quem tem risco de turnover, quais competências estão faltando num setor, quem poderia
substituir um colaborador específico, quais treinamentos priorizar.

Stack técnico: o mesmo esquema da Base SaaS V1/MediaMind AI/002 — FastAPI, Python, SQLAlchemy,
PostgreSQL, JWT, Alembic, Pytest no backend; React, TypeScript, Vite, Tailwind no frontend.

Escopo do MVP: colaborador (ficha, cargo, histórico) → desempenho básico → PDI/competências →
carreira básica → dashboard de RH. Fora do MVP inicial (mas pertencem conceitualmente ao 003, só
entram depois): folha de pagamento, ponto, benefícios, férias — evitar que o projeto "exploda de
tamanho" antes do núcleo funcionar.

O detalhamento completo (fluxos de módulo, telas de navegação, exemplos de dashboard e a análise
de um concorrente real — Sólides/RHGestor) está na transcrição de origem preservada em
`docs_referencias/origem_ai_people_os/BASE RH _+_GERENCIAMENTO FUNCIONARIOS.txt`, e a ideia
original do "AI People OS" em `docs_referencias/origem_ai_people_os/IDEIA_AI_PEOPLE_OS.md`.
