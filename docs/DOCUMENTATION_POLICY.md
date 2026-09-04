# Política obrigatória de documentação e contexto

Esta política faz parte da Base SaaS V1 e deve permanecer em todo projeto derivado.

## Regra central

Documentação, especificações, decisões, imagens de referência e arquivos de contexto são parte do produto. Uma migração não está completa apenas porque o código funciona.

Nenhum documento de referência pode ser omitido ou descartado por parecer antigo. Antes, ele deve ser classificado como **atual**, **substituído** (com motivo), **histórico**, **futuro** ou **inaplicável** (com justificativa).

## Estrutura mínima de todo projeto

- `AGENTS.md`: regras permanentes e ponto de entrada para agentes.
- `CLAUDE.md`: encaminhamento do Claude para as mesmas regras.
- `docs/AI_CONTEXT.md`: resumo curto do produto, estado e decisões que não podem regredir.
- `docs/DOCUMENTATION_INDEX.md`: índice e roteamento por tema.
- `docs/PROGRESSO.md`: estado executável, evidências e próximo passo.
- `docs/REQUIREMENTS_MATRIX.md`: requisitos e classificação.
- `docs_referencias/`: fontes preservadas, marcadas como históricas/somente leitura.
- Manifesto e verificação automática quando a referência possuir vários documentos.

## Processo obrigatório de migração

1. Inventariar documentos e ativos relevantes com filtros que excluam dependências, caches, ambientes, segredos e Git.
2. Preservar os originais na fonte, sempre somente leitura.
3. Copiar documentos relevantes à área histórica do novo projeto, mantendo caminhos relativos.
4. Registrar onde ficou cada tema no projeto atual.
5. Criar contexto atual curto; não obrigar a IA a reler todo o legado em cada sessão.
6. Conferir quantidade e integridade da cópia.
7. Atualizar o índice quando um documento for criado, movido, substituído ou arquivado.
8. Não encerrar a migração sem paridade funcional e documental registrada.

## Economia de tokens sem perda de memória

Agentes leem primeiro contexto curto, progresso e índice. Documentos grandes e históricos são abertos apenas conforme o tema. Resumos não apagam fontes; apenas apontam para elas.

## Manutenção contínua

Uma mudança de código que altere requisito, arquitetura, banco, segurança ou estado atualiza a documentação correspondente na mesma tarefa. Documento novo sem ligação no índice é documentação incompleta.
