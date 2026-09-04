# Ciclo de Vida de Dados e LGPD

Este documento é um ponto de partida técnico e operacional. A versão final de cada SaaS deve ser revisada conforme sua finalidade, seus operadores, os tipos de dados tratados e orientação jurídica aplicável.

## Inventário por finalidade

Cada módulo deve registrar: dado coletado, finalidade, origem, base de tratamento definida pelo responsável, quem acessa, onde é armazenado, com quem é compartilhado, prazo de retenção e procedimento de eliminação.

## Minimização

- Coletar somente o necessário para a funcionalidade declarada.
- Separar campos obrigatórios de opcionais.
- Evitar dados sensíveis quando uma alternativa menos invasiva resolver o problema.
- Não reutilizar dados para IA, marketing ou treinamento sem regra explícita e compatível.

## Direitos do titular

A tabela `data_subject_requests` registra pedidos de acesso, correção, eliminação, portabilidade e revisão. Cada SaaS deve definir responsável, prazo operacional, verificação de identidade, exceções justificadas e evidência de conclusão. A API não fixa prazo legal: isso deve permanecer configurável e ser confirmado antes da produção.

## Retenção e eliminação

As janelas iniciais são configuráveis por ambiente em `AUDIT_RETENTION_DAYS`, `SESSION_RETENTION_DAYS` e `PRIVACY_REQUEST_RETENTION_DAYS`. Os valores do exemplo são referências técnicas, não uma definição jurídica; cada SaaS deve aprová-los conforme sua finalidade e obrigações. A execução automática das rotinas de expiração será conectada à fila de tarefas na Fase 4.

- Retenção deve ser definida por categoria, não por um prazo único para todo o sistema.
- Expiração deve gerar fila controlada, auditoria e possibilidade de suspensão por obrigação legítima.
- Exclusão de conta deve separar anonimização, eliminação e dados que precisam ser preservados.
- Backups devem possuir ciclo próprio para que dados eliminados não permaneçam indefinidamente.

## Incidentes

Preservar evidências sem expor mais dados, conter o acesso, avaliar impacto, registrar decisões e acionar responsáveis. Critérios e comunicações externas devem ser definidos antes da produção com apoio especializado.
