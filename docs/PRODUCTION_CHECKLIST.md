# Checklist antes da produção

Esta lista é um gate técnico; não substitui revisão jurídica, de privacidade ou de negócio do SaaS específico.

## Identidade e acesso

- [ ] Segredo de autenticação único, aleatório, com pelo menos 32 caracteres e armazenado em cofre.
- [ ] Cookies seguros e HTTPS obrigatório na borda.
- [ ] MFA habilitado prioritariamente para `owner`, `admin` e equipe operacional.
- [ ] Contas, convites, papéis e acessos de suporte revisados.
- [ ] Procedimento de revogação de sessões e rotação de chaves ensaiado.

## Infraestrutura e rede

- [ ] PostgreSQL e Redis não expostos publicamente; TLS e controles de rede configurados.
- [ ] Usuário de migration separado do usuário limitado da aplicação.
- [ ] CORS, domínio, proxy confiável, cabeçalhos e limites de requisição revisados.
- [ ] Imagens fixadas, atualizadas, examinadas e executadas sem privilégios.
- [ ] E-mail, arquivos e provedor de IA configurados com credenciais mínimas.

## Dados, LGPD e segurança

- [ ] Inventário, finalidade, base legal, operadores, retenção e descarte definidos por categoria.
- [ ] Termos, privacidade, cookies e canal do titular revisados por responsável competente.
- [ ] RLS e isolamento entre empresas testados no ambiente de publicação.
- [ ] Uploads mantêm quarentena fechada quando antivírus/validação falha.
- [ ] Logs, métricas e auditoria não armazenam senhas, tokens, prompts ou dados desnecessários.
- [ ] Dependências, SAST, segredos e imagens passam por varredura no pipeline.

## Continuidade e incidentes

- [ ] Backups automáticos criptografados, separados e protegidos contra exclusão pela aplicação.
- [ ] RPO, RTO e retenção aprovados; restauração real cronometrada e registrada.
- [ ] Alertas de saúde, erros, filas, abuso, uso de IA, armazenamento e ausência de backup configurados.
- [ ] Responsáveis e contatos do plano de incidente preenchidos; exercício realizado.
- [ ] Avaliação LGPD/ANPD e comunicação a titulares possuem responsáveis definidos.

## Aceitação

- [ ] Migrations aplicadas do zero e rollback praticado quando seguro.
- [ ] `scripts/verify.ps1`, smokes Docker e fluxos críticos no navegador aprovados.
- [ ] Segredos locais, `.env`, bancos, dumps, uploads, caches e dados reais ausentes do artefato.
- [ ] Plano de implantação, reversão e monitoramento pós-publicação aprovado.
