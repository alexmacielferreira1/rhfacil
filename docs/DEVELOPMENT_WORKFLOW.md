# Fluxo rápido em duas passagens — projeto 003

O 003 está na Passagem 1. A prioridade é colocar rapidamente a gestão básica de funcionários em funcionamento de ponta a ponta, separada do recrutamento do 002.

## Layout primeiro

Antes de aprofundar os marcos, criar uma versão visual navegável com dashboard, lista e ficha de colaboradores, estrutura/organograma e telas essenciais. Estados de demonstração devem ser identificados e depois substituídos por APIs reais. O proprietário deve conseguir abrir e avaliar o layout do 003 cedo.

- Usar marcos como roteiro, não como barreiras.
- Implementar cadastro/ficha, estrutura e fluxos essenciais com dados reais e testes focados.
- Não esperar a conclusão integral do domínio ou dos relatórios de marco para disponibilizar o layout navegável.
- Usar Docker incremental, reconstruindo apenas o serviço alterado e preservando serviços, volumes e cache.
- Adiar suíte integral, banco vazio, rebuild total, todos os smokes e relatórios extensos para checkpoints e para a Passagem 2.
- Atualizar o progresso ao pausar, mudar de fase ou tomar decisão importante.

Segurança estrutural não é adiada: autenticação, autorização, CSRF, RLS, relações por empresa, validação e proteção de dados pessoais continuam obrigatórios.

Depois que 002 e 003 básicos estiverem funcionando, a Passagem 2 completará recursos avançados, marcos, validação integral, segurança/LGPD aprofundadas, acessibilidade, paridade e documentação final.
