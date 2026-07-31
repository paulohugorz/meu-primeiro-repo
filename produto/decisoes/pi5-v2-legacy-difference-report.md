# Relatório de diferença — PI5 legado x PI5 v2

**Data:** 2026-07-31

**Escopo:** B1 experimental, somente branch de desenvolvimento.

**Decisão:** sem publicação, deploy, uso comercial, merge em `main` ou claim público.

## Inventário congelado

O registro versionado `produto/metodologia/pi5/pi5-legacy-registry-v1.json`
identifica PI5/ISCM legado, seus defaults, status `experimental_legacy`, limitações e
motivo da retirada futura. O código legado foi preservado para compatibilidade; sua
única correção defensiva faz ausência valer zero ponto, nunca vantagem.

## Comparação das saídas

| Cenário | Legado | PI5 v2 | Readiness | Confidence |
|---|---|---|---|---|
| Completo | score composto | 5 dimensões `complete`; `global_score=null` | avaliado separadamente | avaliada separadamente |
| Parcial | defaults podiam contribuir | dimensão `partial`, lacunas explícitas, sem score | `partial` ou `indeterminate` | `partial` ou `indeterminate` |
| Indeterminado | ausência podia ser mascarada | conflito ou falta total gera `indeterminate`, sem score | independente | independente |

## Exemplos mínimos v2

Completo (todos os dez indicadores obrigatórios presentes):

```json
{"status":"complete","global_score":null,"publication_blockers":[]}
```

Parcial (ex.: `ghg_emissions` presente, `energy_use` ausente):

```json
{"status":"partial","global_score":null,"missing_indicators":["energy_use"]}
```

Indeterminado (ex.: duas fontes conflitantes):

```json
{"status":"indeterminate","global_score":null,"conflicts":1}
```

## Evidência e limites da verificação

- Testes automatizados cobrem os três estados, ausência, conflito, `not_applicable`,
  segregação de reviewer, feature flag, Fabric Intelligence e reversibilidade textual.
- As migrations foram revisadas e testadas estaticamente; **não foram aplicadas em um
  PostgreSQL real** nesta entrega. Aplicação e rollback em cópia limpa/anonimizada são
  condição pendente antes de integração.
- A API v2 é uma avaliação sem persistência e fica deny-by-default. Dual-write/read e
  persistência só podem ser habilitados após migrations testadas e revisão independente.
- Pesos, thresholds, score global e claims continuam bloqueados até calibração e aprovação.
