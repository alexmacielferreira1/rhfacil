# Prompt Mestre para planejar um novo SaaS

Este documento é o roteiro padrão de descoberta de produto da Base SaaS V1. Use-o antes de implementar um novo sistema. Ele transforma uma ideia em produto planejado, conecta telas a regras e preserva as decisões para a IA de programação.

> Não quero apenas ideias de funcionalidades; quero projetar a experiência completa de uso, incluindo o que acontece entre uma tela e outra.

## Como usar

1. Copie o prompt da seção seguinte para uma nova conversa.
2. Substitua `[ESCREVA AQUI O TIPO DE SaaS]` pelo segmento ou ideia.
3. Na primeira resposta, peça somente as etapas 1 a 3. Revise a direção antes de avançar.
4. Continue pelas etapas em texto. Gere imagens apenas depois de aprovar o produto.
5. Guarde as decisões em `PROJETO.md`, `docs_referencias/` e na matriz de requisitos do projeto.
6. Ao final, peça a especificação técnica e confronte-a com a segurança e a arquitetura desta Base.

## Prompt para copiar

```text
PROMPT MESTRE — PLANEJAMENTO COMPLETO DE UM NOVO SaaS

Quero planejar um novo SaaS.

SEGMENTO / IDEIA:
[ESCREVA AQUI O TIPO DE SaaS]

Quero que você desenvolva este produto do zero como um SaaS real, completo, modular, escalável e comercializável.

Não quero apenas ideias de funcionalidades; quero projetar a experiência completa de uso, incluindo o que acontece entre uma tela e outra.

IMPORTANTE:
Não comece gerando imagens. Primeiro planeje detalhadamente o produto em texto. Depois vamos aprofundar telas e funcionalidades. Somente depois começaremos a gerar imagens.

Use como filosofia um sistema que integre operação, gestão, relacionamento, documentos, financeiro, dashboards, automações e IA quando essas áreas fizerem sentido para o segmento.

ETAPA 1 — ENTENDER O NEGÓCIO

Explique com profundidade:
1. visão geral do SaaS;
2. problema que resolve;
3. público-alvo e personas;
4. diferenças entre profissional, gestor, funcionário, cliente/paciente e outros perfis;
5. dores de cada perfil;
6. jornada completa do usuário;
7. fluxo operacional principal;
8. diferenciais competitivos;
9. MVP e itens de versões posteriores.

Pense como Product Manager, UX/UI Designer, arquiteto de software, especialista no segmento, analista de negócios e desenvolvedor SaaS.

ETAPA 2 — ARQUITETURA FUNCIONAL

Detalhe todos os módulos necessários. Para cada módulo, descreva objetivo, funcionalidades, informações, ações, filtros, buscas, status, alertas, notificações, automações, integrações, permissões, relatórios e relação com outros módulos.

Avalie, sem incluir automaticamente: dashboard, agenda, clientes/pacientes, operação principal, documentos, financeiro, comunicação, tarefas, gestão, relatórios, configurações, usuários, perfis e permissões, auditoria, IA, automações e portal do cliente. Adapte tudo ao segmento.

ETAPA 3 — VISÃO DE CADA TIPO DE USUÁRIO

Crie separadamente a experiência de cada perfil. Para cada um, detalhe dashboard inicial, menus, informações prioritárias, ações rápidas, alertas, tarefas, indicadores, histórico, documentos, comunicação, financeiro quando aplicável, experiência mobile e permissões. A interface do cliente não deve ser uma cópia da interface profissional.

ETAPA 4 — MAPA COMPLETO DE TELAS

Inclua telas principais e intermediárias, detalhes, modais, drawers, menus contextuais, confirmações, sucesso, erro, estados vazios, loading/skeleton e mobile. Para cada tela, informe de onde o usuário veio, o que vê, o que pode clicar, o resultado do clique, o que abre, quais dados mudam e o próximo passo.

ETAPA 5 — BOTÕES E INTERAÇÕES

Defina o comportamento de cada ação importante: mudança de status, registros criados, tela aberta, dados carregados, histórico e atualização do dashboard. Cubra hover, disabled, loading, confirmação, sucesso, erro, permissões, ações destrutivas, menus de contexto, cards, gráficos, filtros e drill-down.

ETAPA 6 — DASHBOARDS E VISUALIZAÇÕES

Projete dashboards úteis, não decorativos: operacional (o que fazer agora), gerencial (como está o negócio) e individual (situação da entidade). Detalhe KPIs, gráficos, mapas, timelines, funis, comparações, tendências, alertas, metas, filtros, período e drill-down. Gráficos devem ser clicáveis quando fizer sentido.

ETAPA 7 — REPRESENTAÇÕES VISUAIS DO DOMÍNIO

Avalie mapas, plantas, diagramas, timelines, mapas corporais ou de equipamentos, processos, calendários, kanban, funis, organogramas, árvores, fluxogramas, antes/depois e progresso. Crie representações realmente específicas para o segmento.

ETAPA 8 — IA ÚTIL E SEGURA

Não use apenas um chatbot. Separe IA assistiva, analítica, generativa, busca, automações, detecção de pendências, resumos e sugestões. Para cada função, defina entrada, dados consultados, resultado, ação possível, confirmação humana, riscos e permissões. IA não executa silenciosamente ações críticas.

ETAPA 9 — AUTOMAÇÕES

Modele cada automação como GATILHO → CONDIÇÃO → AÇÃO. Inclua exemplos específicos do segmento para eventos, prazos, inatividade, pagamentos e tarefas, sempre com responsável, registro e possibilidade de auditoria.

ETAPA 10 — IMAGENS

Somente depois de aprovar o produto em texto, gere imagens. A primeira deve mostrar uma visão geral realista. As seguintes devem aprofundar módulos, perfis, dashboards, gráficos, representações, telas intermediárias, modais, drawers, menus, filtros, estados, portal do cliente e mobile, mantendo linguagem visual consistente.

ETAPA 11 — STORYBOARDS DE FLUXOS CLICÁVEIS

Mostre TELA 1 → clique → TELA 2 → clique → TELA 3 → resultado, com números, setas, cursores, botão clicado, modal/drawer, mudança de status e resultado. Produza vários fluxos essenciais do negócio.

ETAPA 12 — DOCUMENTO PARA IA DE PROGRAMAÇÃO

Depois das telas e imagens, produza uma especificação completa para implementar frontend e backend: contexto, arquitetura, banco, entidades, relacionamentos, APIs, schemas, validações, autenticação, multi-tenancy, RBAC, permissões, auditoria, uploads, documentos, dashboards, relatórios, IA, automações, integrações, segurança, testes, Docker/infra, estrutura de pastas e fases.

Stack preferencial:
- Frontend: React, TypeScript, Vite, Tailwind, TanStack Query, React Hook Form, Zod, Recharts e Lucide.
- Backend: Python, FastAPI, SQLAlchemy, Pydantic, Alembic e PostgreSQL.
- Avaliar conforme a necessidade: Redis, workers e armazenamento S3-compatible.

A arquitetura deve ser modular, sem arquivos gigantes.

REGRA FINAL

Pense no produto como algo que realmente será desenvolvido. Não invente botões sem função, dashboards decorativos, gráficos inúteis ou IA apenas por marketing. Não trate mockups como páginas isoladas.

Conecte sempre:
TELA → AÇÃO → REGRA DE NEGÓCIO → API → BANCO → HISTÓRICO → AUDITORIA → FEEDBACK NA INTERFACE.

Na primeira resposta, entregue somente as ETAPAS 1 a 3 em texto, com bastante profundidade. Não gere imagens ainda.
```

## Sequência curta de continuação

1. “Detalha mais a visão do profissional e do cliente.”
2. “Agora detalha todas as funcionalidades e as telas intermediárias antes das imagens.”
3. “Detalha dashboards, gráficos, mapas e representações visuais específicas desse negócio.”
4. “Detalha o que acontece ao clicar nos principais botões.”
5. “Faz a primeira imagem geral.”
6. “Agora faz mais imagens com telas intermediárias e mais detalhes.”
7. “Cria imagens mostrando os cliques dos botões e o que abre depois.”
8. “Continua com outros fluxos importantes.”
9. “Agora mostra dashboards, gráficos, filtros e drill-down.”
10. “Agora mostra o portal/visão do cliente.”
11. “Agora mostra IA, alertas, automações e relatórios.”
12. “Faça o documento técnico completo para uma IA desenvolver frontend e backend com base em tudo que planejamos e nas imagens.”

## Quando houver imagem de referência

Acrescente ao pedido:

```text
Estou enviando uma imagem de referência. Use-a somente para entender estrutura, organização, tipo de representação, densidade de informações e o comportamento visual indicado. Não copie marca, logo ou identidade visual. Se eu apontar especificamente um elemento, preserve esse conceito nas próximas imagens e mantenha consistência com as telas já criadas para este SaaS.
```

## Regras da Base que continuam valendo

- O prompt planeja o produto; ele não substitui os controles de segurança, LGPD, multi-tenancy, RBAC, auditoria, testes e produção da Base.
- O stack é preferencial. Decisões técnicas já aprovadas no projeto prevalecem e devem ser registradas.
- Cada projeto terá banco, segredos, usuários, uploads, integrações e repositório próprios.
- MFA deve entrar entre as primeiras medidas antes da produção, mesmo que seja adiado no desenvolvimento inicial.
- O projeto original e as referências permanecem somente leitura.

## Verificação do planejamento

O planejamento só está pronto para virar código quando existe rastreabilidade entre perfis, telas, ações, regras, APIs, dados, auditoria e retorno visual; os estados de erro, vazio, carregamento, permissão e mobile também precisam estar descritos.

Veja também [Criar um novo SaaS](NEW_SAAS.md) e a [pipeline obrigatória](PROJECT_PIPELINE.md).
