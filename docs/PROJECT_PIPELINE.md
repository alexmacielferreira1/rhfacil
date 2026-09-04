# Pipeline obrigatória de cada SaaS

## 1. Preparação

- Ler e aplicar `docs/DOCUMENTATION_POLICY.md`; documentação e referências são parte do produto.
- Criar a pasta somente com o inicializador da Base e confirmar identidade, portas e banco próprios.
- Usar `docs/PROMPT_MESTRE_NOVO_SAAS.md` para planejar o produto em texto antes das imagens e da implementação.
- Preservar a cópia preenchida, as respostas aprovadas e as decisões nos documentos de contexto e requisitos.
- Manter originais e `EXEMPLOS QUE TENHO` somente leitura.
- Inventariar textos, imagens, planilhas, telas e código da referência sem copiar segredos, `.git`, ambientes ou dados.
- Inventariar individualmente os documentos da referência e classificá-los como atuais, substituídos, históricos, futuros ou inaplicáveis.
- Preservar os documentos relevantes em `docs_referencias/`, mantendo estrutura relativa e prova de integridade.
- Criar/personalizar `PROJETO.md`, `docs_referencias/contexto_atual.md` e `docs_referencias/requisitos.md`.
- Criar/personalizar `AGENTS.md`, `CLAUDE.md`, `docs/AI_CONTEXT.md` e `docs/DOCUMENTATION_INDEX.md`.
- Registrar o recorte do produto e o que pertence a outro SaaS.

## 2. Planejamento e execução

- Criar matriz de paridade e plano por marcos pequenos.
- Implementar com testes, RLS, relações tenant-scoped, CSRF, RBAC e auditoria proporcionais ao risco.
- Não transformar mock em dado fictício apresentado como real.
- Registrar decisões mais seguras que substituam pedidos antigos.
- Atualizar `docs/PROGRESSO.md` ao concluir cada marco.

## 3. Aceitação de cada marco

- Rodar testes, lint e tipagem do backend e frontend.
- Aplicar todas as migrations em banco PostgreSQL vazio.
- Construir e verificar os serviços Docker.
- Conferir estados de carregamento, vazio, erro, celular e baixa conectividade.
- Atualizar matriz de paridade e criar relatório do marco.

## 4. Conferência de memória e documentação

- Reler a conversa consolidada, os anexos indicados pelo proprietário e os TXT de referência.
- Comparar promessas com arquivos existentes; não confiar apenas no pedido mais recente.
- Classificar cada item como concluído, substituído com motivo, específico de outro projeto ou pendente.
- Atualizar `CONFERENCIA_FINAL_DOS_PEDIDOS.md` e `docs/REQUIREMENTS_MATRIX.md`.
- Conferir paridade documental: cada documento ou tema legado deve possuir destino ou disposição registrada.
- Executar a verificação de integridade do arquivo histórico e ligar todos os documentos atuais no índice.
- Manter separado o relatório técnico compartilhável e o resumo criativo para imagens.

## 5. Antes da produção

- Executar `docs/PRODUCTION_CHECKLIST.md`, priorizando MFA, segredos exclusivos, TLS, backups,
  restauração, antivírus, monitoramento, dependências e resposta a incidentes.
- Configurar Git/GitHub e novos contextos Codex/Claude somente quando o proprietário autorizar.
- Manter o projeto antigo por semanas e removê-lo apenas após validação humana explícita.
