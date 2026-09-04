# Marcos do domínio de negócio — 003 Gestão de Funcionários

Roteiro do escopo definido em `PROJETO.md` (ficha do colaborador, organograma,
cargos/salários, metas, desempenho, feedback, PDI, competências, carreira,
treinamentos, benefícios, documentos funcionais, clima, saúde ocupacional,
desligamento, People Analytics). Marcos são roteiro, não barreira — a ordem
pode mudar conforme prioridade do usuário (ex.: pedido de apresentar a um
cliente adiantou a camada visual antes do previsto).

Convenção de status: `Concluído` (código real, com dado real quando aplicável),
`Visual (mock)` (tela pronta, dado de demonstração, sem backend próprio),
`Não iniciado`.

## Marco 0 — Núcleo do colaborador
**Status: Concluído** (04/09/2026)
Cadastro, listagem e mudança de status (ativo/inativo/desligado) de
colaboradores, com RLS por tenant, RBAC local, CSRF e auditoria. Login e
navegação ligando as telas.

## Marco 1 — Dados profissionais + dados manipuláveis via Excel
**Status: Concluído** (04/09/2026)
- Colaborador ganhou gestor direto (auto-relacionamento validado por tenant),
  tipo de contratação (CLT/PJ/Estágio/Temporário/Outro), nível/grade, centro
  de custo e salário fixo — campos do mockup 07 (Dados Profissionais).
- `GET /people/employees/export.csv` e `POST /people/employees/import`:
  exportação e importação em CSV (delimitador `;`, compatível com Excel),
  com relatório linha a linha (criado/atualizado/erro).
- Frontend: formulário de cadastro com os novos campos, seletor de gestor,
  botões "Exportar CSV" / "Importar CSV" na tela de colaboradores.
- Verificado nesta sessão só por AST + `ruff` (backend) e `tsc`/`vitest`/`vite build`
  (frontend) — sem Postgres real. Falta rodar `docker compose up` de verdade e
  testar a importação com uma planilha real exportada do próprio sistema.

## Marco 2 — Camada visual de demonstração (múltiplas telas, dado mock)
**Status: Visual (mock)** (04/09/2026)
Dashboard executivo, visão por setores/gestores e portal do colaborador
("meu painel"), com sidebar de navegação — dado 100% mocado em
`frontend/src/mock/people-data.ts`, documentado como tal. Serve para
apresentação a cliente; cada número aqui precisa virar API real nos marcos
seguintes.

## Marco 3 — Organograma
**Status: Não iniciado**
Visualização em árvore da hierarquia (usa o `manager_id` já existente no
Marco 1), com níveis diretoria/gerência/coordenação/equipe — ver
`docs_referencias/origem_ai_people_os/telas_ampliadas/board_03.png`,
`board_04.png`, `board_09.png` e `board_10.png`.

## Marco 4 — Desempenho (avaliação simples)
**Status: Não iniciado**
Fluxo em etapas, não uma nota solta: competências avaliadas (peso + nota +
comentário) → metas do ciclo → feedback → revisão e nota final. 360°/9Box
ficam para depois (Passagem 2), conforme já registrado em `PROJETO.md`. Ver
`board_02`, `board_03`, `board_04`, `board_09`, `board_10` e o fluxo completo
de modais em `board_11` (seção C: novo → competências → metas → feedback →
revisão → confirmação).

## Marco 5 — Metas
**Status: Não iniciado**
Cadastro de metas por colaborador/ciclo, acompanhamento de progresso com
histórico numérico (valor atual x meta ao longo do tempo), vínculo com a
avaliação de desempenho. Ver `board_10` (telas 10-14) e o fluxo completo de
modais em `board_11` (seção D: criar → detalhar indicador → acompanhar →
editar → concluir).

## Marco 6 — PDI e competências
**Status: Não iniciado**
Plano de desenvolvimento individual com ações (curso/mentoria/prática),
prazos e status — troca o mock da tela "Meu painel" por dado real. Ver o
fluxo completo de modais em `board_11` (seção E: criar ação → acompanhar →
detalhar → concluir).

## Marco 7 — Carreira
**Status: Não iniciado**
Trilha de cargos/níveis, requisitos para o próximo passo, histórico de
promoções.

## Marco 8 — Treinamentos
**Status: Não iniciado**
Catálogo de treinamentos, inscrições, conclusões — alimenta o indicador
"treinamentos concluídos" hoje mocado no dashboard.

## Marco 9 — Benefícios e documentos funcionais
**Status: Não iniciado**
Benefícios por colaborador (hoje mocado em "Meus benefícios") e documentos
obrigatórios (RG, CPF, comprovantes) com status de envio, espelhando os
mockups 08/09.

## Marco 10 — Clima, saúde ocupacional e desligamento
**Status: Não iniciado**
Pesquisas de clima, acompanhamento de saúde ocupacional, fluxo estruturado
de desligamento (hoje é só uma mudança de status).

## Marco 11 — People Analytics real
**Status: Não iniciado**
Troca definitiva de todo dado mocado do dashboard/setores/gestores por
consultas reais agregando os marcos 3-10.

## Marco 12 — Ações rápidas e modais de gestor
**Status: Não iniciado**
Camada de interação que aparece pela primeira vez em `board_11` (não estava
nos boards anteriores): menu de ações rápidas do gestor sobre um colaborador
(nova avaliação, nova meta, novo feedback, novo PDI, transferir colaborador,
alterar gestor, enviar mensagem), confirmações antes de ações destrutivas
(excluir documento, inativar colaborador) e utilitários (exportar relatório,
notificação, filtro avançado). Faz mais sentido implementar depois que os
Marcos 4-6 (desempenho/metas/PDI) já existirem de verdade — são as ações que
operam sobre esses dados.

## Fora do escopo do 003
Recrutamento, vagas, candidatos e portal público de carreiras pertencem ao
`002_IA_RH_RECRUTAMENTO` (ver `docs/SOURCE_CLASSIFICATION.md`).
