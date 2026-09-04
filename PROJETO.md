# Gestão de Funcionários

SaaS multiempresa de gestão interna de colaboradores, parte do "AI People OS" (nome de trabalho), derivado da Base SaaS V1. Cobre ficha do colaborador, organograma, cargos e salários internos, metas, desempenho (autoavaliação, avaliação do gestor e futura 360°/9Box), feedback contínuo, PDI, competências, carreira, treinamentos, benefícios, documentos funcionais, clima, saúde ocupacional, desligamento e People Analytics interno.

## Limite obrigatório

Este projeto não é recrutamento e seleção. Vagas, candidatos, candidaturas, currículos, pipeline de contratação, ranking de IA de candidatos, entrevistas, feedback de candidato e portal público de carreiras pertencem ao `002_IA_RH_RECRUTAMENTO`. Uma contratação no 002 pode produzir um handoff auditável para este projeto (Candidato → Colaborador, reaproveitando só os dados apropriados da candidatura); o 003 não implementa processo seletivo.

Autenticação, usuários, empresa, cargos e histórico são compartilhados conceitualmente com o 002 (mesma origem Base V1), mas cada projeto mantém seu próprio banco e implementação — não há fusão de produtos nem de dados entre 002 e 003.

## Estado

- Cópia limpa da Base V1 (já com o cache de instalação compartilhado do ADR-006) criada em 2026-09-04.
- 15 materiais de origem preservados em `docs_referencias/origem_ai_people_os/`, com manifesto SHA-256.
- Fronteira 002/003 herdada de `docs/SOURCE_CLASSIFICATION.md` (cópia do documento definido durante o 002).
- Domínio de gestão de colaboradores ainda não implementado.

Comece por `AGENTS.md`, `docs/AI_CONTEXT.md`, `docs/PROGRESSO.md`, `docs/DOCUMENTATION_INDEX.md` e `docs/SOURCE_CLASSIFICATION.md`.
