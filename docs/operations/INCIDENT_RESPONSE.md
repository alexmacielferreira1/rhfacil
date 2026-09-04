# Resposta a incidentes

## Objetivo

Conter, investigar e recuperar incidentes sem destruir evidências nem ampliar o acesso indevido. Cada SaaS derivado deve preencher responsáveis, contatos, fornecedores, seguradora e assessoria jurídica antes da produção.

## Classificação inicial

- **Crítico:** vazamento confirmado, controle administrativo comprometido, ransomware ou indisponibilidade ampla.
- **Alto:** acesso suspeito privilegiado, isolamento entre empresas em risco ou perda relevante de serviço.
- **Moderado:** abuso limitado, malware bloqueado, falha recuperável ou exposição sem exploração confirmada.
- **Baixo:** tentativa bloqueada ou anomalia sem impacto demonstrado.

## Procedimento

1. **Detectar e registrar:** horário, request IDs, alertas, contas, empresas e sistemas afetados; nunca copiar segredos para o chamado.
2. **Preservar:** restringir acesso às evidências, exportar logs/auditoria de forma íntegra e registrar cadeia de custódia.
3. **Conter:** revogar sessões, suspender contas/tenant quando necessário, bloquear origem e isolar worker ou integração afetada.
4. **Rotacionar:** trocar segredos de sessão, banco, e-mail, IA e fornecedores conforme o alcance; uma rotação do segredo de autenticação encerra sessões e invalida links assinados.
5. **Erradicar:** corrigir a causa com teste de regressão, atualizar dependências/imagens e verificar persistência maliciosa.
6. **Recuperar:** restaurar de cópia validada quando necessário, testar RLS, autenticação, filas e integridade antes de reabrir.
7. **Avaliar LGPD:** documentar natureza, titulares, dados, medidas e riscos; responsável jurídico/DPO decide comunicação à ANPD e aos titulares nos prazos aplicáveis.
8. **Encerrar:** produzir linha do tempo, impacto, decisões, evidências, responsáveis e ações com prazo; realizar retrospectiva sem culpabilização.

## Exercícios obrigatórios antes da produção

- conta administrativa comprometida;
- segredo de sessão exposto;
- tentativa de acesso entre tenants;
- arquivo malicioso enviado;
- provedor de IA/e-mail indisponível ou comprometido;
- banco corrompido e restauração de backup;
- solicitação urgente de revogação e preservação LGPD.

MFA para contas privilegiadas é uma das primeiras medidas antes da produção, conforme já registrado no baseline.
