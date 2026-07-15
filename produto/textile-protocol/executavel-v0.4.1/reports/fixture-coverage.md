# Cobertura das fixtures

## Resultado

- 20 fixtures válidas aceitas.
- 20 fixtures inválidas rejeitadas pela regra esperada.
- JSON Schema Draft 2020-12 aprovado.
- Integridade referencial do dicionário aprovada.

## Casos inválidos

| Fixture | Regra esperada | Descrição |
|---|---|---|
| `invalid.001` | `rule.assertion.inferred_no_evidence_elevation` | Inferência visual marcada indevidamente como resultado calculado. |
| `invalid.002` | `rule.assertion.verified_requirements` | Asserção verificada sem revisão humana aceita. |
| `invalid.003` | `rule.assertion.probability_requires_calibration` | Probabilidade numérica sem calibração. |
| `invalid.004` | `rule.publication.composition_inferred_withhold` | Composição inferida publicada. |
| `invalid.005` | `rule.publication.function_missing_context_withhold` | Função sem método publicada. |
| `invalid.006` | `rule.publication.function_missing_context_withhold` | Função sem fonte publicada. |
| `invalid.007` | `rule.publication.capture_insufficient_request` | Captura insuficiente classificada. |
| `invalid.008` | `rule.publication.commercial_high_ambiguity_request` | Nome comercial de alta ambiguidade publicado sem nova evidência. |
| `invalid.009` | `rule.publication.open_conflict_block` | Conflito aberto com publicação. |
| `invalid.010` | `rule.tactile.no_image_only` | Atributo tátil baseado somente em imagem. |
| `invalid.011` | `schema.required_field` | Medição sem unidade. |
| `invalid.012` | `rule.assertion.inferred_requires_execution` | Inferência sem execução rastreável. |
| `invalid.013` | `semantic.execution_unknown_model` | Execução aponta para modelo inexistente. |
| `invalid.014` | `schema.publication_policy` | Decisão pública sem política válida. |
| `invalid.015` | `semantic.publication_assertion_mismatch` | Decisão de publicação aponta para outra asserção. |
| `invalid.016` | `rule.history.supersedes_preserves_old` | Nova asserção substitui registro que não está superseded. |
| `invalid.017` | `rule.history.correction_requires_replacement` | Revisão corrected sem nova asserção substituta. |
| `invalid.018` | `rule.benchmark.versioned_capability` | Leno fora do benchmark fundamenta classify. |
| `invalid.019` | `rule.cardinality.dimension` | Duas famílias estruturais ativas. |
| `invalid.020` | `schema.additional_property` | Campo publicability antigo permanece em Assertion. |


## Correção 0.4.1

- `inferred` aceita somente `evidence_status=absent`.
- `calculated` é reservado a `derived` com método/fórmula versionada e asserções de origem.
- `valid.001` demonstra uma derivação determinística válida.
- `invalid.001` testa diretamente a proibição de `inferred + calculated`.
- `documented` significa que um artefato preserva a observação ou declaração; não significa verificação da propriedade têxtil.
