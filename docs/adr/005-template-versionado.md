# ADR-005: template versionado e projetos independentes

- Estado: Aceita
- Data: 2026-08-29

## Contexto

A pasta base será copiada para produtos diferentes. Atualizar automaticamente todas as cópias quando surgir uma Base V2 poderia quebrar vários sistemas ao mesmo tempo e misturar bancos, segredos ou repositórios.

## Decisão

Tratar a Base V1 como template versionado. `scripts/new-saas.ps1` cria uma cópia limpa, recusa sobrescrita e exclui Git, segredos, dependências instaladas, caches e dados locais. Cada derivado registra origem em `docs/BASE_LINEAGE.md` e `.template-origin.json`; depois passa a ter configuração, banco, dados e futuro repositório próprios. Uma Base V2 não altera derivados automaticamente.

## Consequências

- Cada SaaS evolui e pode ser revertido sem afetar os demais.
- Correções futuras da base exigem avaliação e migração explícita em cada projeto.
- Dependências são reinstaladas a partir dos arquivos de lock; ambientes virtuais e `node_modules` não são copiados.
- A linhagem permite saber de qual base o projeto nasceu e planejar V1 para V2.

## Alternativas consideradas

- Sincronização automática da base para todos os projetos: rejeitada pelo risco de quebra em massa.
- Copiar a pasta inteira com `.env`, Git e dados: rejeitado por risco de vazamento e colisão.
- Um único repositório para todos os SaaS: não imposto; cada produto terá seu próprio repositório quando as conexões forem criadas.
