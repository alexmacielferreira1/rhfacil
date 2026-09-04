# Requisitos permanentes para este projeto

## Herdados da Base SaaS V1 (não remover)

1. Preservar isolamento por empresa no banco e na API.
2. Usar sessão opaca HttpOnly e CSRF; integrações externas podem receber autenticação própria.
3. Oferecer convite, conta iniciada pelo administrador via link de ativação e solicitação de acesso por link empresarial.
4. Nunca enviar senha temporária conhecida pelo administrador; o usuário define a própria senha no primeiro acesso.
5. Manter MFA como uma das primeiras exigências antes da produção.
6. Arquivos nascem em quarentena e só são usados após liberação.
7. IA e integrações externas falham fechadas quando não configuradas.
8. Não registrar segredo, prompt, resposta privada, conteúdo de arquivo ou caminho físico em auditoria.
9. Toda mudança de banco usa migration reversível e teste em banco vazio.
10. Todo projeto mantém `PROJETO.md`, contexto, requisitos, progresso, matriz de requisitos, decisões, operações e segurança.
11. Antes de encerrar um marco, executar a rotina descrita em `docs/PROJECT_PIPELINE.md`.

## Específicos do AI People OS aplicáveis ao 003 (extraídos do material de origem e do ADR de fronteira com o 002)

12. Transição Candidato → Colaborador (Employee), vinda do 002, é controlada e explícita; só os
    dados apropriados da candidatura são reaproveitados no perfil do colaborador — o histórico do
    colaborador é independente do processo seletivo a partir da contratação.
13. Dashboards (do RH, de equipe, individual) nunca guardam dados próprios: todo indicador é
    calculado a partir das entidades reais (avaliações, PDIs, treinamentos, metas, competências,
    promoções) no momento da consulta.
14. Dashboard de RH deve suportar troca de contexto de análise (empresa toda, setor, equipe,
    indivíduo) sem duplicar lógica de cálculo.
15. Autenticação, usuários, empresa, cargos e histórico são compartilhados conceitualmente com o
    002, mas cada projeto mantém banco e implementação próprios; nenhuma integração acopla os dois
    bancos diretamente.
16. Manter People/Employees e Talent & Career como módulos distintos no backend — nunca colapsar
    tudo em um módulo único de "employees".
17. Menus/modelos de Recrutamento (vagas, candidatos, pipeline, ranking de IA de candidatos,
    entrevistas, portal público) não pertencem a este projeto — ver `docs/SOURCE_CLASSIFICATION.md`.

## Escopo do MVP (não expandir sem decisão explícita)

- Entra: ficha do colaborador, cargo/organograma básico, avaliação de desempenho (auto + gestor),
  metas, competências, PDI, mapa de carreira básico (cargo atual, próximos níveis, competências
  faltantes), dashboard de RH.
- Fica para depois (pertence ao 003, mas entra em fase posterior): folha de pagamento, ponto,
  benefícios, férias, avaliação 360°/9Box completa, documentos funcionais, clima, saúde
  ocupacional, desligamento, People Analytics avançado (turnover preditivo, sucessão).

## Pendências conhecidas que precisam de decisão antes de virar requisito travado

- Nome definitivo do produto (hoje "AI People OS" é nome de trabalho, compartilhado com o 002).
- Detalhamento do Portal do Colaborador depende de informações que o proprietário está coletando
  com profissionais de RH reais — o material de origem deixa isso explicitamente em aberto.
- Estrutura final de avaliação (autoavaliação, avaliação do gestor, futura avaliação 360°).
- Formato exato do handoff Candidato → Colaborador vindo do 002 (quais campos, quando ocorre,
  quem aprova) ainda não foi desenhado.
