# Progresso — Gestão de Funcionários (003)

Atualizado em 2026-09-04 (adendo mais recente ao final).

## Prioridade de execução

O 003 está na Passagem 1 com layout primeiro. Criar rapidamente uma interface navegável e o produto básico, usando testes focados e Docker incremental. Marcos completos e validações extensas ficam para a Passagem 2, depois que 002 e 003 básicos estiverem rodando. Segurança estrutural permanece obrigatória. Ver `docs/DEVELOPMENT_WORKFLOW.md`.

## Estado do projeto 003

- Criado por cópia limpa e independente da Base SaaS V1 em 2026-09-04, já com o cache de instalação compartilhado (ADR-006) herdado da Base.
- Adendo ADR-006 (04/09/2026): adicionado id fixo (`poetry-global-cache`, `npm-global-cache`) aos cache mounts do BuildKit em backend.Dockerfile/frontend.Dockerfile, garantindo cache compartilhado entre projetos mesmo com Dockerfiles ligeiramente diferentes. Ver adendo em `docs/adr/006-cache-instalacao-compartilhado.md`.
- Validacao final ADR-006 (04/09/2026): docker compose build+up rodado no Docker Desktop em 000 (4,1s, up falhou por porta 5432 ja ocupada por outro processo no host, sem relacao com o cache), 001 (2,9s, up OK, cache do poetry e do npm ambos batidos) e 002 (263,8s, up OK; cache do poetry batido, cache do npm nao bateu porque o frontend do 002 tem pacotes novos nunca baixados antes - comportamento esperado, sem vazamento de escopo entre projetos). Detalhe completo em docs/adr/006-cache-instalacao-compartilhado.md. Falta rodar a mesma validacao em 003 e resolver o conflito de porta 5432 do 000 (fora do escopo da ADR-006).
- Identidade `gestao-de-funcionarios` e portas próprias registradas em `.template-origin.json` (Api 10547, Web 11547, Postgres 12547, Redis 13547, Mailpit Web 14547, Mailpit SMTP 15547).
- 15 materiais da referência AI People OS preservados em `docs_referencias/origem_ai_people_os/` (transcrição combinada, ideia original, 11 telas, 2 screenshots), com manifesto SHA-256 em `docs_referencias/source-materials.sha256`.
- Fronteira entre recrutamento (002) e gestão de colaboradores (003) preservada em `docs/SOURCE_CLASSIFICATION.md` (mesmo documento decidido durante o 002).
- `PROJETO.md`, `docs_referencias/contexto_atual.md` e `docs_referencias/requisitos.md` personalizados para o escopo People/Employees + Talent & Career.
- `AGENTS.md`, `CLAUDE.md` e `docs/DOCUMENTATION_INDEX.md` ainda estão no padrão herdado da Base (não personalizados além do que a Base já traz).
- Nenhum domínio de negócio implementado ainda — próxima etapa é inventariar o material combinado (`BASE RH _+_GERENCIAMENTO FUNCIONARIOS.txt`) especificamente sob a ótica do 003, criar a matriz inicial de paridade e planejar o primeiro marco (provável: ficha do colaborador + organograma básico, já que é o que o handoff do 002 alimenta primeiro).
- Ambiente local (venv Python, node_modules, `docker compose build`) ainda não foi instalado/testado neste projeto — precisa rodar no computador do usuário (Docker Desktop), fora do alcance desta sessão.

## Primeira fatia funcional: módulo de colaboradores (employees) — 2026-09-04

Seguindo a decisão de ritmo (essencial e rápido, sem gate de marco), implementado o primeiro domínio de negócio do 003 replicando fielmente o padrão já validado no módulo de recrutamento do 002 (RLS por tenant, SQL cru via `text()`, `set_tenant` por request, RBAC local ao módulo, CSRF, auditoria).

Backend (`backend/app/modules/employees/`):
- `schemas.py`: `EmployeeCreate`, `EmployeeUpdate`, `EmployeeStatusChange`, `EmployeeView` (status: active/inactive/terminated).
- `permissions.py`: `authorize_people`, permissões `people:read/write/manage` mapeadas para os papéis reais do projeto (owner, admin, member — os únicos atribuíveis via convite na Base).
- `router.py`: prefixo `/people`, endpoints `POST/GET /employees`, `GET/PATCH /employees/{id}`, `POST /employees/{id}/status` (ativar/inativar/desligar).
- Migração `migrations/versions/20260904_0011_employees_core.py`: tabela `employees` com RLS habilitado e forçado, política de isolamento por tenant, unique por (organization_id, email normalizado), down_revision correto (`20260828_0010`, última migração herdada da Base).
- Router registrado em `app/api/router.py`.

Frontend (`frontend/src/features/employees/`):
- `employees-api.ts`, `EmployeesPage.tsx` (lista de colaboradores em cards + formulário de cadastro + ações de mudança de status), `EmployeesPage.test.tsx`.
- Rota `/people/employees` adicionada em `app/App.tsx`.
- Reaproveita o CSS genérico da Base (`.shell`, `.card`, `.grid`, `.form-card`) — não usa o sistema "rh-" que é específico do 002.

Verificação real feita nesta sessão (sandbox isolado, cópia completa do frontend com dependências instaladas do zero):
- `npx vitest run`: 3 arquivos de teste, 5 testes, todos passando (incluindo o novo `EmployeesPage.test.tsx`).
- `npm run typecheck` (`tsc -b`): sem erros.
- `npm run build` (vite): build de produção concluído sem erros.
- Backend: sintaxe validada (AST) e lint (`ruff check --select=F,E9`) sem apontamentos nos arquivos novos. Verificação de execução real contra Postgres **não foi feita nesta sessão** — mesma limitação já documentada no 002 (Python 3.14 estável não instalável no sandbox via `uv`, só a release candidate, incompatível com pydantic). A fonte de verdade para validar o backend em execução continua sendo o Docker Desktop do usuário.

Arquivos entregues e já gravados no projeto real (`003_GESTAO_DE_FUNCIONARIOS/`) nesta sessão.

## Correção de usabilidade: login e navegação — 2026-09-04

Revisão pedida pelo usuário ("confere a usabilidade de todo o sistema do 003") encontrou um problema real: o 003 ainda estava no esqueleto genérico da Base — `/` era a tela de health-check, não existia tela de login no frontend (o backend já tinha `/api/v1/auth/login` pronto, herdado da Base) e não havia nenhum menu/navegação ligando as telas. Ou seja: um usuário real não conseguia chegar em `/people/employees` pela interface, e mesmo digitando a URL direto cairia num 401 sem explicação, porque não existia como logar.

Corrigido:
- `frontend/src/features/auth/`: `auth-api.ts` (login/logout) e `LoginPage.tsx` (rota `/login`), usando os componentes genéricos da Base (`.shell`, `.card`, `.form-card`) — mesmo padrão do 002, sem depender do sistema de classes "rh-" que é específico dele.
- `frontend/src/app/NavBar.tsx`: barra de navegação persistente (Início / Colaboradores / Entrar-Sair) renderizada em todas as rotas via `App.tsx`. Detecta sessão pelo cookie `saas_csrf` para alternar entre "Entrar" e "Sair".
- `EmployeesPage.tsx`: erro 401 agora mostra "Sua sessão expirou, entre novamente" com link para `/login`, em vez de um erro genérico sem saída.
- Verificado de novo do zero (sandbox isolado): `npx vitest run` — 4 arquivos, 6 testes, todos passando (incluindo o novo `LoginPage.test.tsx`); `tsc -b` e `vite build` limpos.

Arquivos entregues e já gravados no projeto real nesta sessão.

## Material de referência (mockups SOFTMIND RH) revisitado — 2026-09-04

O usuário lembrou que `docs_referencias/origem_ai_people_os/telas/` (11 imagens, já preservadas na criação do 003) contém mockups detalhados do produto-alvo completo — cobrindo tanto recrutamento (002) quanto gestão de pessoas (003): dashboard executivo, cadastro de colaborador em 5 etapas (dados pessoais/profissionais/contrato/benefícios/documentos), desempenho, PDI, metas, carreira, treinamentos, relatórios analíticos, visão por gestor/setor.

Comparado ao que existe hoje: a implementação atual do 003 é a fatia mínima de UMA dessas telas (cadastro simples de colaborador: nome/e-mail/cargo/departamento/admissão + lista + status), sem os campos mais ricos do mockup (gestor direto, tipo de contratação, salário, centro de custo, nível/grade) nem nenhuma das telas de desempenho/carreira/PDI/relatórios. Isso é esperado e intencional pela decisão de ritmo já registrada (essencial e rápido agora, marcos e profundidade depois) — mas fica documentado aqui para não perder de vista o alvo real ao planejar as próximas fatias.

## Próxima etapa exata

Rodar `docker compose build && docker compose up` no 003 (Docker Desktop do usuário) e confirmar visualmente, logando de verdade pela tela `/login`, que o fluxo completo funciona ponta a ponta contra o Postgres real: login → navegação → cadastro/listagem de colaboradores. Depois, evoluir a fatia do colaborador na direção do mockup 06/09/10 (dados profissionais mais completos: gestor direto, tipo de contratação, salário, nível) antes de avançar para desempenho/carreira/PDI, que ficam para a Passagem 2 junto com os marcos e testes completos.

## Camada visual de demonstração (frontend, dados mocados) — 2026-09-04

Pedido do usuário: preparar o 003 para apresentar a um cliente o mais rápido possível — prioridade no visual (mesmo com mockups), backend real fica para depois. Comparado ao gap descrito na seção anterior ("Material de referência revisitado"), esta fatia cobre visualmente várias das telas do mockup SoftMind RH usando **dados de demonstração** (não vêm do backend).

Adicionado (`frontend/src/`):
- `app/AppShell.tsx`: layout com sidebar (substitui a barra superior `NavBar` nas telas autenticadas), navegação para Visão geral / Colaboradores / Setores e gestores / Meu painel, responsivo (sidebar vira menu retrátil em telas estreitas).
- `mock/people-data.ts`: dataset único de demonstração (headcount, setores, gestores, equipe, avaliações, PDI, carreira, benefícios), documentado no topo do arquivo como mock — trocar por chamadas reais módulo a módulo.
- `features/dashboard/DashboardPage.tsx` (rota `/dashboard`, agora a home `/`): KPIs (colaboradores ativos, avaliações concluídas, PDIs ativos, turnover, engajamento) + gráfico de evolução de headcount, distribuição de avaliações (donut) e colaboradores por setor (barras), usando `recharts` (nova dependência).
- `features/company/CompanyOverviewPage.tsx` (rota `/company`): abas "Por setor" e "Por gestor" com tabelas de indicadores, espelhando os mockups 04/05.
- `features/me/MyPanelPage.tsx` (rota `/me`): portal do colaborador — evolução da avaliação, PDI em andamento, carreira (competências-chave) e benefícios, espelhando os mockups 18-22.
- `EmployeesPage.tsx` migrada para usar o novo `AppShell` (mantém dados reais do backend, sem mudança de comportamento).
- CSS estendido em `styles/index.css` mantendo a identidade já existente (fundo navy `#07111f`, acento cyan `#67e8f9`), com paleta complementar (`#818cf8`, `#fbbf24`, `#fb7185`) só para diferenciar séries em gráfico — sem trocar a marca.
- Rota `/` agora redireciona para `/dashboard` (era a tela de health-check, que passou para `/status`).

Verificação real feita nesta sessão (mesma limitação de sempre: sem Postgres real no sandbox):
- `tsc -b --pretty false`: sem erros.
- `vite build`: build de produção concluído sem erros (aviso de bundle >500kB por causa do `recharts`, aceitável nesta fase — dividir em code-splitting é otimização futura, não bloqueante para demo).
- `npx vitest run`: 4 arquivos, 6 testes, todos passando (foi preciso corrigir `EmployeesPage.test.tsx`, que importava `MemoryRouter` mas não envolvia o componente nele — passou a falhar porque o novo `AppShell` usa `useNavigate`, e isso expôs o teste incompleto).

Não fizeram parte desta fatia (fica para depois, com o usuário definindo prioridade):
- Cadastro completo do colaborador em 5 etapas (mockups 06-09) — o formulário de colaboradores continua no formato simples e ligado ao backend real.
- Import/export CSV de colaboradores (para edição via Excel).
- Deploy de teste no Vercel/Render (depende do kit local do usuário, fora do alcance desta sessão).
- Qualquer ligação real dos números do dashboard/setores/meu painel ao backend — hoje é 100% mock, documentado em `mock/people-data.ts`.

## Dados profissionais do colaborador + import/export CSV (backend) — 2026-09-04

Pedido do usuário: avançar no que dá para fazer de backend sem depender do
Docker Desktop dele, e formalizar o roteiro de marcos do domínio de negócio
(criado em `docs/MARCOS.md`, ver lá o roteiro completo Marco 0 a Marco 11).

Backend (`backend/app/modules/employees/`):
- Migração `20260904_0012_employees_professional_data.py`: colunas
  `manager_id` (auto-FK composta com `organization_id`, garante que o gestor
  é sempre da mesma empresa, `ON DELETE SET NULL`), `contract_type`
  (CLT/PJ/Estágio/Temporário/Outro, `CHECK`), `level`, `cost_center`,
  `salary_amount` (`numeric(12,2)`, `CHECK >= 0`), mais `CHECK` impedindo o
  colaborador ser gestor de si mesmo e índice por `(organization_id, manager_id)`.
- `schemas.py`: `EmployeeCreate`/`EmployeeUpdate`/`EmployeeView` com os novos
  campos; `EmployeeImportRowResult`/`EmployeeImportSummary` para o relatório
  de importação.
- `router.py`: `EMPLOYEE_COLUMNS` passou a fazer `left join` com a própria
  tabela para trazer `manager_name`; `PATCH` valida que ninguém vira gestor
  de si mesmo; dois endpoints novos — `GET /people/employees/export.csv`
  (CSV com `;`, pronto para abrir no Excel) e `POST /people/employees/import`
  (multipart, `on conflict ... do update` por e-mail normalizado, upsert
  linha a linha com relatório criado/atualizado/erro).

Frontend (`frontend/src/features/employees/`):
- Formulário de cadastro ganhou gestor direto (select populado pelos
  colaboradores já cadastrados), tipo de contratação, nível/grade, centro de
  custo e salário.
- Card do colaborador mostra gestor e tipo de contratação.
- Botões "Exportar CSV" / "Importar CSV" na tela, com resumo da importação.
- `lib/api-client.ts` ganhou `apiUpload` (multipart com CSRF) para o import.

Verificação real feita nesta sessão (mesma limitação de sempre — sem
Postgres real no sandbox):
- Backend: sintaxe validada (AST) e `ruff check app/modules/employees/` sem
  apontamentos.
- Frontend: `tsc -b --pretty false` sem erros, `vite build` sem erros,
  `npx vitest run` — 4 arquivos, 6 testes, todos passando (foi preciso
  ajustar `EmployeesPage.test.tsx`: o nome do colaborador agora também
  aparece como opção no seletor de gestor, então o teste precisou apontar
  para o `heading` em vez do texto solto, que ficou ambíguo).

Não verificado nesta sessão (fica para quando o usuário rodar
`docker compose up` de verdade): migração aplicando limpa em cima da
`20260904_0011`, endpoint de import processando um CSV real, comportamento
do `left join` com volume de dados.

Roteiro de marcos formalizado em `docs/MARCOS.md` — próximo marco sugerido
é o organograma (Marco 3), que já tem o dado (`manager_id`) pronto para ser
visualizado em árvore.

## Front muito mais rico + organograma + insights de IA (visual, dado mock) — 2026-09-04

Pedido do usuário: considerar o material de referência original (`IDEIA_AI_PEOPLE_OS.md`
e o TXT combinado — mesmo conteúdo já preservado, sem novidade factual, mas reforça
a visão de "AI People OS" e não recrutamento) e melhorar bastante o front.

Adicionado (`frontend/src/`):
- `mock/people-data.ts`: `aiInsights` (perguntas no estilo AI People OS —
  "quem está pronto pra virar coordenador", risco de turnover, gaps de
  competência, substituição), `orgTree` (estrutura hierárquica) e
  `employeeProfileExtras` (competências, histórico, documentos, desempenho/PDI
  mocados para a ficha do colaborador).
- `features/dashboard/DashboardPage.tsx`: seção "Perguntas que a IA já
  consegue responder" com os 4 insights mocados.
- `features/company/OrgChart.tsx` + aba "Organograma" em
  `CompanyOverviewPage.tsx` (agora com 3 abas: Organograma / Por setor / Por
  gestor) — árvore visual com conectores CSS clássicos, sem biblioteca extra.
- `features/employees/EmployeeProfilePage.tsx` (rota
  `/people/employees/:employeeId`): ficha do colaborador com abas Perfil
  (dado real do backend) / Desempenho / PDI e competências / Documentos
  (mocados, cada aba avisa em qual Marco vira real). Nome do colaborador na
  lista agora é link para essa ficha.
- `features/employees/NewEmployeeWizard.tsx`: cadastro em 3 etapas (Dados
  pessoais → Dados profissionais → Revisão) no lugar do formulário único,
  reaproveitando os mesmos campos reais já ligados ao backend.
- CSS: `.insights-card`, `.org-chart` (conectores clássicos de organograma
  via `::before`/`::after`), `.profile-header`/`.profile-fields`,
  `.wizard-steps`/`.wizard-actions`.

Bug real encontrado e corrigido nesta sessão: o gráfico de rosca (donut) do
dashboard renderizava cortado (~metade do círculo) — Recharts 3.x mudou o
comportamento padrão de ângulo do `Pie`; precisou `startAngle={90}
endAngle={-270}` explícitos. Só foi possível achar isso porque desta vez
consegui um Chromium funcional via Playwright no sandbox e inspecionei o SVG
renderizado (path `d=`) diretamente — vale lembrar disso em telas futuras com
gráfico: sempre conferir visualmente antes de dar como pronto.

Verificação real feita nesta sessão: `tsc -b --pretty false` sem erros,
`vite build` sem erros, `npx vitest run` — 4 arquivos, 6 testes passando.
Screenshot real (Playwright/Chromium) do dashboard e da aba Organograma
conferidos visualmente — organograma renderizou os conectores corretamente
de primeira; o donut precisou da correção acima.

Segue tudo mock nas partes assinaladas — nenhuma mudança de backend nesta
fatia (o Marco 1 — dados profissionais/CSV — segue sendo a única parte do
domínio de colaborador com dado real, mais os campos base do Marco 0).
