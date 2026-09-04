# Backup e restauração

## Uso local e validação

Execute `scripts/backup.ps1 -BackupFile <caminho-explicito>` para criar um dump PostgreSQL e o arquivo irmão `.sha256`. Execute `scripts/restore-check.ps1 -BackupFile <caminho-explicito>` para verificar o checksum e restaurar somente no banco descartável fixo `base_saas_restore_check`, removido ao final.

O teste reproduzível é `tests/smoke/backup-restore.ps1`. Ele não substitui uma política de produção.

## Requisitos de produção

- Agendar backups automáticos completos e, quando oferecido pelo provedor, recuperação ponto no tempo.
- Criptografar em trânsito e em repouso com chaves gerenciadas fora do servidor da aplicação.
- Armazenar cópias em conta/região separada e impedir que a credencial da aplicação apague o conjunto de backups.
- Definir retenção, RPO e RTO para cada SaaS conforme criticidade e obrigações legais.
- Monitorar falhas e ausência de backups; checksum sozinho detecta corrupção, não prova restauração.
- Executar restauração periódica em ambiente isolado com dados fictícios ou anonimizados e registrar duração e resultado.
- Nunca inserir `.env`, tokens, dumps ou chaves no Git, na pasta-base distribuível ou no relatório compartilhável.

## Recuperação

1. Declarar o incidente e preservar evidências.
2. Escolher o ponto de recuperação aprovado e validar checksum/assinatura.
3. Restaurar em ambiente isolado, aplicar verificações de esquema e consistência.
4. Rotacionar credenciais potencialmente expostas antes de liberar tráfego.
5. Validar saúde, permissões, RLS e fluxos essenciais.
6. Registrar perda estimada, duração, aprovação e ações preventivas.
