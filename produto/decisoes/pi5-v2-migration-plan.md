# PI5 v2 — metodologia, compatibilidade e rollback

**Status:** experimental; não aprovado para produção, claim público ou calibração científica.
**Método:** `phyllos-impact-v2@2.0.0-experimental`.
**Readiness:** metodologia PHYLLOS independente; não reproduz ITM, pesos, questionário, score ou dados.

## Separação obrigatória

PI5 Impact, PHYLLOS Evidence Readiness e Evidence Confidence são contratos e
saídas independentes. Readiness ou confiança nunca aumentam, reduzem ou limitam
numericamente impacto. O score global v2 permanece `null` até calibração e
aprovação de pesos e política de cobertura.

## Compatibilidade

- API existente permanece inalterada.
- `/api/v2/impact/evaluate` é aditiva e deny-by-default por `PI5_V2_ENABLED=false`.
- ISCM e PI5 v0.1 ficam `experimental_legacy`; ausência passou a valer zero no
  legado ISCM para remover o comportamento favorável, sem promover o resultado.
- Migração v2 não reescreve histórico e possui SQL de rollback.

## Migração operacional

1. Aplicar migration em cópia limpa e cópia anonimizada de banco existente.
2. Ativar dual-write somente em ambiente de teste.
3. Comparar legado e v2 em shadow; divergência é evidência, não erro a ocultar.
4. Validar confidencialidade, conflito, expiração e segregação de reviewer.
5. Exigir revisão independente antes de habilitar API v2 fora de teste.

## Rollback

Desativar `PI5_V2_ENABLED`, interromper dual-write e executar o SQL `_down` se
for necessário retirar as tabelas aditivas. APIs e registros legados permanecem.

## Diferença de saída

- Legado: score composto mesmo com defaults e ausência.
- v2 completo: dimensões completas, mas `global_score=null` até calibração.
- v2 parcial: dimensão parcial, lista de indicadores ausentes e bloqueio.
- v2 indeterminado: ausência total ou conflito; nunca converte lacuna em zero.
