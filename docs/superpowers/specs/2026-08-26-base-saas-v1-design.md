# Especificação de Arquitetura — Base SaaS V1

## 1. Objetivo

A `000_BASE_SAAS_V1` será um template versionado, funcional, seguro e copiável para a criação de novos produtos SaaS. Cada cópia será um projeto independente, com seu próprio repositório Git, banco, configurações, segredos, contexto de IA e ciclo de evolução.

A base define o padrão para projetos novos. Ela não atualiza nem sobrescreve automaticamente projetos existentes. Mudanças estruturais futuras originarão novas versões da base, e a migração de cada produto será analisada e executada separadamente.

## 2. Limites e proteção dos projetos existentes

- Os projetos originais no Desktop permanecem intocados durante toda a construção e validação.
- As pastas em `EXEMPLOS QUE TENHO` são referências somente de leitura.
- A base não reutilizará identidades Git, conexões do Codex ou Claude, bancos, usuários, uploads, caches, ambientes virtuais ou segredos dos exemplos.
- A exclusão dos projetos antigos será uma decisão futura e exclusiva do proprietário, depois de semanas de validação dos novos sistemas.

## 3. Estratégia escolhida

A base será construída de forma limpa, usando os dois projetos funcionais como referências. O Media Mind contribui com cobertura funcional, uploads, IA e fluxos mais amplos. O RH contribui com uma organização modular mais clara. Nenhum deles será copiado integralmente como base.

Alternativas rejeitadas:

- Transformar diretamente o Media Mind em base: herdaria domínio específico, artefatos temporários, duplicações e dependências pesadas.
- Transformar diretamente o RH em base: exigiria acrescentar grande parte da infraestrutura e dos módulos comuns.
- Construir simultaneamente base e dois produtos: dificultaria distinguir defeitos da base de defeitos de migração.

## 4. Arquitetura do repositório

Cada SaaS será um monorepositório independente. Backend, frontend, banco, infraestrutura, documentação e testes do mesmo produto ficarão juntos.

Estrutura de alto nível:

```text
PROJETO/
├── backend/
├── frontend/
├── database/
├── infra/
├── scripts/
├── tests/
├── docs/
├── compose.yaml
├── .env.example
├── .gitignore
└── README.md
```

O backend será um monólito modular. Cada módulo terá finalidade e interface claras, evitando dependências circulares e arquivos que concentrem responsabilidades demais.

## 5. Tecnologias oficiais

### Backend

- Python 3.14.7 como versão inicial reproduzível.
- FastAPI assíncrono.
- SQLAlchemy assíncrono.
- PostgreSQL.
- Alembic para evolução do esquema.
- Poetry para dependências e ambiente Python.
- Pydantic para contratos e configuração.
- Pytest para testes.
- Ruff e verificação rigorosa de tipos.

### Frontend

- React.
- TypeScript.
- Vite.
- React Router.
- TanStack Query.
- React Hook Form e Zod.
- Tailwind CSS e componentes acessíveis reutilizáveis.
- Vitest e Testing Library.

As versões exatas das bibliotecas serão verificadas quanto a compatibilidade e segurança durante a implementação e registradas em arquivos de bloqueio reproduzíveis.

### Serviços locais

- Docker como ambiente padrão de desenvolvimento, sem impedir execução direta quando útil.
- PostgreSQL para persistência.
- Redis para filas, cache e limites distribuídos.
- Serviço de tarefas em segundo plano.
- Mailpit para capturar e-mails localmente sem envio real.

## 6. Módulos comuns

A base incluirá módulos genéricos para:

- autenticação e sessões;
- empresas e multi-tenancy;
- usuários, convites e perfis;
- papéis e permissões;
- auditoria;
- solicitações de titulares e governança LGPD;
- arquivos e uploads;
- notificações e e-mail;
- tarefas em segundo plano;
- gateway de IA;
- planos, limites e estados de assinatura;
- configurações e feature flags;
- saúde, métricas e observabilidade.

Papéis iniciais: superadministrador da plataforma, proprietário da empresa, administrador da empresa, gestor, usuário e somente leitura. Produtos derivados poderão criar papéis próprios sem modificar o motor de permissões.

## 7. Autenticação e sessões

- Cadastro por convite será o padrão.
- Cadastro público poderá ser habilitado por projeto, com confirmação de e-mail e controles contra abuso.
- Tokens serão transportados em cookies `HttpOnly`, `Secure` e `SameSite` adequados ao ambiente.
- Operações mutáveis terão proteção CSRF.
- Tokens de acesso terão curta duração; tokens de renovação serão rotativos e revogáveis.
- Senhas usarão algoritmo moderno de derivação resistente a ataques.
- Recuperação de senha, confirmação de e-mail e convites usarão tokens de uso único e prazo curto.
- MFA estará preparado estruturalmente, desativado no desenvolvimento inicial e destacado como uma das primeiras exigências para produção, principalmente para administradores.

## 8. Multi-tenancy e autorização

O isolamento entre empresas terá duas camadas obrigatórias:

1. FastAPI validará identidade, empresa ativa, papel e permissão em cada operação.
2. PostgreSQL aplicará Row-Level Security nas tabelas multi-tenant.

Todo registro multi-tenant terá identificador de empresa. O contexto da empresa será estabelecido de forma segura na transação do banco. Testes negativos tentarão ler e alterar registros pertencentes a outra empresa e deverão falhar nas duas camadas.

O frontend apenas oculta ou exibe ações por conveniência; a autorização real sempre ocorre no servidor e no banco.

## 9. Segurança de aplicação e infraestrutura

A segurança seguirá defesa em profundidade, orientada por OWASP ASVS, OWASP API Security Top 10 e boas práticas atuais.

Controles mínimos:

- validação estrita de entradas e respostas;
- consultas parametrizadas pelo ORM;
- proteção contra XSS, CSRF, SSRF, injeções e redirecionamentos inseguros;
- CORS restritivo por ambiente;
- cabeçalhos de segurança;
- limites por IP, usuário, empresa, rota e custo;
- atraso e bloqueio progressivo contra força bruta;
- CAPTCHA adaptativo somente quando necessário;
- privilégios mínimos para banco, serviços e tarefas;
- segredos fora do código e do frontend;
- rotação e revogação de credenciais;
- bloqueio de documentação e endpoints administrativos em produção quando apropriado;
- análise de dependências, segredos, código, contêineres e licenças;
- arquivos de bloqueio de dependências reproduzíveis;
- atualização automatizada somente com revisão e testes.

A aplicação será independente de fornecedor. A documentação de produção recomendará uma camada de borda como Cloudflare para TLS, WAF, mitigação de DDoS e limites adicionais, sem torná-la obrigatória.

## 10. Arquivos e conteúdo não confiável

- Tipos, dimensões e tamanhos serão configuráveis.
- O conteúdo real será validado, sem confiar apenas na extensão ou no tipo declarado.
- Nomes internos serão gerados pelo sistema.
- Arquivos ficarão fora de áreas executáveis e não serão servidos diretamente sem autorização.
- Arquivos potencialmente perigosos passarão por quarentena e verificação antivírus quando aplicável.
- Downloads usarão autorização e links temporários.
- Processamentos serão isolados, limitados e executados em segundo plano.

## 11. IA segura e independente de fornecedor

Chamadas de IA passarão por um gateway central no backend. O frontend não receberá chaves de provedores nem chamará modelos diretamente.

O gateway controlará:

- provedores e modelos permitidos;
- mascaramento ou remoção de dados pessoais;
- limites de custo, volume e concorrência por empresa e usuário;
- proteção contra instruções maliciosas em documentos e entradas;
- separação entre instruções confiáveis e conteúdo não confiável;
- validação de ferramentas e saídas antes de ações com efeito;
- logs com metadados mínimos e sem conteúdo sensível desnecessário;
- cancelamento, timeout, repetição controlada e acompanhamento de uso.

Dependências pesadas de IA local serão opcionais e instaladas apenas pelos produtos que precisarem delas.

## 12. LGPD e ciclo de vida dos dados

A base apoiará privacidade desde a concepção:

- inventário e classificação de dados;
- finalidade e base legal configuradas por produto;
- minimização da coleta;
- consentimento quando ele for a base aplicável;
- registro das operações de tratamento;
- canal e fluxo para solicitações do titular;
- acesso, correção, exportação, anonimização, exclusão e revogação quando aplicáveis;
- validação de identidade e aprovação administrativa para operações sensíveis;
- retenção configurável por categoria;
- exclusão lógica inicial, seguida de anonimização ou descarte definitivo;
- preservação apenas do mínimo legal e operacional necessário.

A implementação fornece mecanismos técnicos, mas cada produto deverá documentar finalidades, bases legais, prazos e responsabilidades conforme seu contexto. Conformidade jurídica não será presumida apenas pela existência do código.

## 13. Auditoria, observabilidade e incidentes

A trilha de auditoria registrará eventos de segurança e negócio relevantes, sem senhas, tokens ou conteúdo pessoal desnecessário. Eventos incluirão autenticação, falhas, alterações de acesso, ações administrativas, exportações, exclusões, solicitações LGPD e mudanças críticas.

Logs estruturados terão identificadores de correlação. Métricas, rastreamento e endpoints de saúde permitirão diagnosticar falhas sem expor informações internas.

O plano de incidentes contemplará detecção, classificação, contenção, bloqueio de sessões, rotação de chaves, preservação de evidências, recuperação, análise de impacto e avaliação de comunicação à ANPD e aos titulares.

## 14. Backups e recuperação

- Backups de produção serão automáticos, criptografados e separados do servidor principal.
- Retenção será configurável.
- Procedimentos de restauração serão documentados e testados periodicamente.
- Credenciais do aplicativo não deverão permitir excluir facilmente todos os backups.
- Desenvolvimento e testes usarão dados fictícios ou anonimizados.

## 15. Planos e cobrança

A base terá um domínio genérico de planos e assinatura, sem integração real de pagamento na V1:

- planos e limites;
- período de teste;
- assinatura por empresa;
- estados ativa, atrasada, cancelada e suspensa;
- funcionalidades por plano;
- interface para futuros provedores de pagamento;
- modo local sem cobrança.

## 16. Inicializador de novos projetos

Um assistente seguro criará a identidade de uma cópia da base. Apenas o nome do SaaS será obrigatório. Identificador técnico, portas e valores de demonstração serão sugeridos automaticamente.

O inicializador não copiará ou gerará identidade Git, credenciais de produção, banco real, usuários reais, uploads, caches ou configurações de ferramentas pessoais. Integrações desconhecidas permanecerão desativadas com padrões seguros.

## 17. Fluxo principal

```text
Navegador
  → camada de borda opcional em produção
  → frontend
  → API FastAPI
  → autenticação + empresa + autorização
  → serviços dos módulos
  → transação com contexto de tenant
  → PostgreSQL com RLS

Operações demoradas
  → fila Redis
  → trabalhador
  → atualização de status e auditoria
```

Erros internos serão convertidos em respostas padronizadas, sem stack traces ou detalhes sensíveis. Falhas transitórias terão repetição limitada; tarefas deverão ser idempotentes quando houver risco de execução duplicada.

## 18. Estratégia de testes

A base somente será considerada funcional após testes de:

- unidades de domínio e serviços;
- integração com PostgreSQL e Redis reais em contêineres;
- endpoints e contratos da API;
- autenticação, sessões e CSRF;
- isolamento multi-tenant no backend e no RLS;
- papéis e permissões;
- migrations de avanço e restauração quando viável;
- frontend e acessibilidade básica;
- fluxos completos essenciais no navegador;
- uploads e conteúdo malicioso simulado;
- filas, repetição e idempotência;
- limites e tentativas de abuso;
- varreduras de segurança e dependências;
- criação de um SaaS de demonstração a partir do inicializador.

## 19. Documentação obrigatória

- visão geral e início rápido;
- arquitetura e limites dos módulos;
- decisões arquiteturais em ADRs;
- modelo de dados e multi-tenancy;
- autenticação, autorização e segurança;
- LGPD e ciclo de vida dos dados;
- desenvolvimento, testes e solução de problemas;
- backup, restauração e incidentes;
- publicação e checklist de produção;
- criação de novo SaaS;
- guia de migração entre versões da base.

## 20. Critérios de conclusão da Base V1

A base estará pronta quando:

- iniciar em uma máquina limpa seguindo a documentação;
- serviços locais subirem de forma reproduzível;
- migrations criarem o banco do zero;
- interface e API funcionarem juntas;
- autenticação, empresa, usuários e permissões estiverem completas;
- isolamento multi-tenant for provado por testes negativos;
- auditoria e fluxo LGPD estiverem operacionais;
- e-mails locais, filas, uploads e gateway de IA tiverem fluxos demonstráveis;
- planos e limites funcionarem sem cobrança real;
- verificações automatizadas passarem;
- o inicializador gerar uma cópia limpa e testável;
- nenhuma informação dos projetos de exemplo tiver sido incorporada indevidamente.

## 21. Ordem de execução

1. Planejar e implementar a Base SaaS V1.
2. Validar a base de forma independente.
3. Migrar o Media Mind para `001_MEDIA_MIND_AI`, preservando funcionalidades específicas.
4. Validar a migração contra o exemplo funcional.
5. Migrar o RH para `002_IA_RH_RECRUTAMENTO`, preservando funcionalidades específicas.
6. Validar a migração contra o exemplo funcional.
7. Criar novas conexões GitHub, Codex e Claude para cada projeto.
8. Manter originais e exemplos intactos por todo o período de segurança definido pelo proprietário.

