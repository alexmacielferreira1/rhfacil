# ADR-004: IA independente de fornecedor

- Estado: Aceita
- Data: 2026-08-29

## Contexto

Os produtos terão usos diferentes de inteligência artificial. Fixar OpenAI, Anthropic ou outro fornecedor no núcleo criaria dependência comercial e poderia enviar dados antes de cada produto definir consentimento, retenção e finalidade.

## Decisão

Definir uma interface de provedor e iniciar com `DisabledAIProvider`. Sem configuração explícita, a chamada falha com segurança. O gateway limita tokens por empresa e registra somente fornecedor, modelo, contagens, estado e hash com chave; não persiste prompt nem resposta. Cada produto decide o provedor e a política de dados posteriormente.

## Consequências

- A Base funciona e é testável sem chave externa.
- Trocar fornecedor não altera as rotas de negócio que usam o gateway.
- Custos podem ser limitados e medidos por empresa sem guardar conteúdo sensível.
- Funcionalidades que precisem de histórico, RAG ou agentes exigirão desenho específico de consentimento, retenção e acesso.

## Alternativas consideradas

- Integrar um fornecedor diretamente na Base: rejeitado por dependência e risco de transmissão acidental.
- Guardar prompts para auditoria: rejeitado por aumentar a superfície de dados pessoais e segredos.
- Não contabilizar uso: rejeitado porque impede controlar custo e abuso por empresa.
