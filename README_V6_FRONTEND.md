# Gestão de Funcionários — V6 Frontend

A V6 amplia o front-end para uma experiência de People OS navegável e apresentável, usando dados demonstrativos locais para funcionar mesmo sem o backend.

## Telas entregues

- Visão geral / dashboard executivo
- Colaboradores: tabela, cards, busca, filtros, importação, novo colaborador e ações
- Ficha completa do colaborador com 10 abas
- Ações rápidas: avaliação, meta, feedback, PDI, transferência e edição
- Desempenho: ciclo, indicadores, evolução, competências e status das avaliações
- Metas: quadro Kanban, lista detalhada, indicadores e modal de criação/detalhe
- PDI e carreira: planos, ações, competências, prazos e mapa de carreira
- Organograma: árvore hierárquica, visão por setor e gestores
- Relatórios e analytics: relatório executivo, gráficos, insights e exportações
- Meu painel: avaliação, metas, PDI, carreira e benefícios
- Configurações: empresa, ciclos, competências, cargos, benefícios, permissões e integrações
- Login visual com entrada em modo demonstração

## Referências usadas

A implementação foi ampliada tomando como referência os boards de UI presentes em `docs_referencias/origem_ai_people_os/telas_ampliadas/`, especialmente a amplitude de dashboards, ficha do colaborador, organograma, avaliações, metas, PDI e modais de ação.

## Rodar

```bash
cd frontend
npm install
npm run dev
```

Depois acesse a URL mostrada pelo Vite (normalmente `http://localhost:5173`).

A aplicação abre diretamente em `/dashboard` e usa dados mock locais. O backend original permanece no projeto para integração posterior.

> Observação: `node_modules` não é incluído no ZIP. Em uma máquina limpa, execute `npm install` antes de `npm run dev`.
