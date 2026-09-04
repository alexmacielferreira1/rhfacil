# Design da reconstrução do Media Mind AI sobre a Base V1

## Estado

Aprovado por autorização autônoma do proprietário em 29/08/2026. A referência em `EXEMPLOS QUE TENHO/MediaMindAI` é somente leitura.

## Objetivo

Criar `001_MEDIA_MIND_AI` como SaaS independente derivado da Base V1, preservando o valor funcional e visual comprovado da referência, corrigindo os riscos conhecidos e separando claramente implementação real, mocks demonstrativos e visão futura.

## Abordagens avaliadas

### 1. Cópia limpa da Base e migração por domínio — escolhida

A Base fornece identidade, empresas, RLS, auditoria, LGPD, fila, arquivos, IA neutra, assinaturas, testes e operação. Cada domínio do Media Mind é redesenhado sobre esses contratos e validado antes do próximo.

Vantagens: segurança nasce correta, migrations começam limpas, multi-tenancy é estrutural e regressões ficam localizadas. Custo: exige mapear os modelos antigos em vez de apenas mover arquivos.

### 2. Copiar o legado e inserir componentes da Base

Rejeitada porque preservaria JWT exposto ao frontend, SQLite/estrutura antiga, mídia pública, reset de senha inseguro, mocks misturados e ausência de tenant em dezenas de tabelas.

### 3. Executar Base e legado como dois serviços

Rejeitada porque duplicaria autenticação, usuários, banco, auditoria e deploy, criando sincronização difícil antes de existir necessidade de microserviços.

## Princípios invariáveis

- Nenhuma escrita na referência.
- Nenhuma funcionalidade é declarada preservada sem teste ou comparação observável.
- Nenhum mock é promovido silenciosamente a funcionalidade real.
- Nenhum dado ou migration antigo é descartado sem matriz de mapeamento.
- Autenticação da Base substitui JWT do legado; conta global + associação por empresa substituem o usuário isolado antigo.
- Toda entidade do Media Mind pertence a uma organização e recebe RLS forçado.
- Arquivos usam metadados e quarentena da Base; `/media` público não será reproduzido.
- IA permanece opcional e fail-closed; processamento local pesado entra por adaptadores e fila.
- Papéis do produto são permissões específicas sobre a associação, sem enfraquecer `owner/admin/member` da Base.
- Git/GitHub/Claude/Codex não serão configurados agora.

## Estado real da referência

A referência contém backend funcional e frontend amplo, mas documentos antigos subestimam o que foi implementado. O código atual possui:

- entidades de usuários, grupos e regras de acesso;
- projetos, assets, roteiros, workspaces e layouts;
- clips, publicações e contas sociais;
- tarefas, entregas e anexos;
- bibliotecas, logs, buscas salvas;
- pacotes, arquivos e trabalhos de ingest;
- pipelines opcionais Whisper, OCR, YOLO e LLM;
- páginas de início, entregas, workspace, acervo, grafo, timeline, clips, publicação, relatórios, gestão, Corp, administração, monitoramento e ingest.

Parte das telas ainda usa mocks ou botões sem efeito. Há riscos conhecidos no legado: bypass de login, token de reset devolvido na resposta, mídia pública, ausência de revogação JWT, tenant incompleto e dependências locais pesadas.

## Arquitetura do novo produto

O backend permanece monólito modular da Base:

```text
app/modules/
├── identity e operações comuns da Base
├── media_assets
├── productions
├── ingest
├── editorial
├── workspaces
├── distribution
├── social
├── media_operations
└── media_ai
```

### Núcleo de domínio

- `Production`: unidade editorial central. Absorve a evolução pretendida de `Project` sem perder o mapeamento do legado.
- `MediaAsset`: mídia ou documento catalogado, relacionado a produção, biblioteca e derivados.
- `IngestPackage`: lote controlado de entrada; seus arquivos geram assets somente após validação.
- `EditorialScript` e `TimelineItem`: roteiro e estrutura temporal.
- `Workspace` e `WorkspaceLayout`: ambiente de trabalho e preferência visual.
- `Clip`: derivado de um asset, com versão, intervalo e estado editorial.
- `Publication` e `SocialAccount`: preparação e registro de distribuição; publicação real fica desativada sem credenciais.
- `MediaTask`, `Delivery` e anexos: coordenação operacional.
- `Library`, `SavedSearch` e regras específicas: organização e acesso dentro do tenant.

## Migração de dados

A V1 do novo projeto terá migrations próprias, baseadas na Base e não no histórico Alembic antigo. Um documento de mapeamento relacionará tabela/campo antigo ao novo. Migração de dados reais será um passo posterior e separado; nesta reconstrução, seeds descartáveis provarão paridade sem tocar no banco da referência.

## Frontend

O frontend visual da referência será preservado seletivamente, mantendo identidade, navegação e fluxos reconhecíveis. Primeiro será conectado à sessão da Base. Depois cada tela será classificada:

- real e conectada: portar com contrato novo;
- real parcial: portar com indisponibilidades explícitas;
- mock útil: manter como demonstração sinalizada ou converter em fase própria;
- legado/duplicado: arquivar somente no novo projeto após prova de que não há consumidor.

Login bypass e fluxo de reset inseguro não serão portados. Convite, ativação e solicitação de acesso da Base serão incorporados ao produto.

## IA e processamento de mídia

Whisper, OCR, YOLO e Ollama serão adaptadores opcionais. A instalação padrão do SaaS não puxará Torch, modelos ou binários pesados. Trabalhos entram na fila, registram progresso e nunca liberam mídia automaticamente quando o processador falha. Prompts, transcrições e dados biométricos exigem política específica antes de produção.

## Fases de entrega

1. Criar cópia limpa e inventário/matriz de paridade.
2. Portar catálogo: produções, assets, bibliotecas e buscas.
3. Portar ingest seguro e processamento assíncrono.
4. Portar editorial: roteiros, timeline, workspaces e clips.
5. Portar operação: tarefas, entregas, publicações, social e relatórios.
6. Portar frontend por fluxo, eliminando bypass e distinguindo mocks.
7. Validar segurança, isolamento, migrations, Docker e paridade.

## Critérios de conclusão

- Projeto nasce da Base V1 e registra linhagem.
- Referência permanece sem alteração.
- Toda tabela de produto tem tenant e RLS.
- Fluxos funcionais escolhidos têm testes de backend e interface.
- Nenhum segredo ou credencial social de referência é copiado.
- Docker e banco vazio funcionam com portas próprias.
- Matriz informa preservado, substituído, mock sinalizado, futuro ou não aplicável para cada recurso relevante.
