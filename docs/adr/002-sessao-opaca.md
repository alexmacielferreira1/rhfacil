# ADR-002: sessão opaca no navegador

- Estado: Aceita
- Data: 2026-08-29

## Contexto

Tokens legíveis pelo JavaScript ampliam o dano de uma injeção de script e dificultam revogação imediata. O navegador precisa autenticar solicitações sem expor a credencial principal à aplicação React.

## Decisão

Usar uma sessão opaca, aleatória e revogável em cookie `HttpOnly`. Em produção o cookie é `Secure`; o ambiente valida segredo forte. Solicitações que alteram estado exigem token CSRF separado. A sessão expira, pode ser revogada no logout e não contém permissões confiáveis no cliente.

## Consequências

- JavaScript não lê a credencial de sessão.
- Logout e resposta a incidente conseguem invalidar acesso no servidor.
- O backend consulta estado de sessão e associação à empresa em vez de confiar em claims antigos.
- APIs para integrações externas poderão usar outra credencial, inclusive JWT, em contrato separado.

## Alternativas consideradas

- JWT persistido em armazenamento do navegador: rejeitado para a sessão web por exposição a scripts e revogação mais difícil.
- Senha temporária criada pelo administrador: substituída por link de ativação de uso único, para que só a pessoa convidada defina a senha.
