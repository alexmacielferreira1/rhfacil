# Segurança de arquivos

## Fluxo padrão

Todo upload autenticado é limitado por tamanho e por tipos explicitamente permitidos, recebe nome interno aleatório e entra como `quarantined`. O nome informado pelo usuário é reduzido ao nome do arquivo e nunca é usado como caminho de armazenamento. O sistema registra tamanho e SHA-256 para integridade e auditoria.

Arquivos em quarentena não podem ser baixados. Apenas `owner` ou `admin`, com sessão e CSRF válidos, pode registrar veredito `clean` ou `malicious`. Somente o veredito limpo muda o estado para `available`; conteúdo rejeitado permanece indisponível. Downloads válidos exigem a mesma empresa do usuário, passam pelo RLS e geram auditoria.

## Antivírus opcional

A Base funciona com revisão manual no desenvolvimento. Em produção com arquivos de terceiros, recomenda-se conectar ClamAV ou serviço equivalente antes de liberar qualquer arquivo. O adaptador deve operar sobre a cópia em quarentena, rejeitar falha fechada, registrar versão/resultado do scanner e usar o mesmo fluxo auditável de veredito. A ausência ou indisponibilidade do scanner nunca deve liberar automaticamente um arquivo.

## Produção

- Armazenamento privado, criptografado e fora da raiz pública do servidor web.
- Limites diferentes por finalidade e plano, sem confiar apenas no cabeçalho MIME.
- Validação de assinatura real do formato quando cada produto definir seus arquivos aceitos.
- Política de retenção e eliminação para arquivo, metadados, cópias derivadas e backups.
- URLs temporárias ou streaming autenticado; nenhum endereço permanente público.
