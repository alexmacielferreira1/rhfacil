# Telas ampliadas — material de referência (2026-09-04)

11 boards de exploração de UI enviados pelo usuário, mais detalhados que o
conjunto original em `../telas/`. Cobrem tanto recrutamento (002) quanto
gestão de pessoas (003) misturados — a fronteira de escopo continua a
mesma de `docs/SOURCE_CLASSIFICATION.md`: tudo que é vaga/candidato/pipeline
de contratação/entrevista com candidato é **002, não 003**.

Cada board é uma variação/exploração diferente da mesma ideia de produto —
não são telas finais, são referência de amplitude e de padrão de interação.

## O que cada board acrescenta de novo (relevante ao 003) em relação ao que já
estava documentado em `../telas/`

- **board_01, board_05, board_06, board_09**: dashboards e visão por
  setor/gestor em variações de detalhe (algumas com mais indicadores, cores e
  agrupamentos diferentes) — já tínhamos a ideia, aqui há mais variações de
  layout pra escolher.
- **board_02, board_03, board_04, board_09, board_10**: **cadastro/edição de
  colaborador em wizard real** (etapas: dados pessoais → dados profissionais
  → contrato → benefícios → documentos → revisão) e **ficha do colaborador
  com abas** (perfil, dados pessoais, profissional, documentos, dependentes,
  benefícios, contas bancárias, histórico) — bem mais completo que o card
  simples hoje implementado.
- **board_03, board_04, board_09, board_10**: **organograma visual em árvore**
  (não just uma lista com "gestor: fulano") com níveis (diretoria/gerência/
  coordenação/equipe).
- **board_02, board_03, board_04, board_09, board_10**: **fluxo de avaliação
  de desempenho em etapas** (competências → metas → feedback → revisão e nota
  final), não uma nota solta.
- **board_10 (telas 10-14)**: metas com lista + detalhe + fluxo de avaliação
  completo com histórico e feedback do gestor.
- **board_11**: é o mais importante e o mais novo — **modais e ações de
  interação** que nenhum outro board mostra: ações rápidas do gestor sobre um
  colaborador (nova avaliação, nova meta, novo feedback, novo PDI, transferir
  colaborador, alterar gestor, enviar mensagem), confirmações (iniciar
  avaliação?, excluir documento?), fluxo completo de meta (criar → detalhar
  indicador com histórico numérico → editar → concluir), fluxo completo de
  PDI (criar ação → acompanhar → detalhar → concluir), e utilitários
  (transferir colaborador, inativar/reativar, excluir documento, exportar
  relatório, enviar notificação, filtro avançado).
- **board_07**: além das telas, tem um rodapé técnico com sugestão de
  estrutura de pastas/stack — é referência de outra pessoa/IA, **não é o
  padrão deste projeto** (este projeto segue a Base SaaS V1 real, já
  implementada; não seguir a estrutura sugerida nesse board).

## Como usar

Antes de aprofundar cada marco de `docs/MARCOS.md` (organograma, desempenho,
metas, PDI, ficha do colaborador), vale abrir os boards relevantes aqui para
pegar o padrão de interação (não só o layout estático).
