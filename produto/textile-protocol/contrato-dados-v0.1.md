# Contrato de dados v0.1

## Princípios

- Confiança é registrada por afirmação, nunca globalmente por amostra.
- Confiança do modelo e nível de evidência são independentes.
- Uma avaliação concluída é imutável; correções criam nova versão ligada à anterior.
- Nenhuma composição pode ser confirmada por foto ou triagem doméstica.

## Compatibilidade com a taxonomia v0.3

O envelope transversal da taxonomia v0.3 complementa o contrato, mas não substitui `evidence_status`. O contrato deve armazenar separadamente:

- natureza da afirmação: observada, inferida, declarada ou derivada;
- estado canônico PHYLLOS: ausente, declarado, calculado, documentado ou verificado;
- confiança e qualidade da captura;
- decisão de publicação e motivo de abstenção.

Mapeamento provisório:

| Envelope v0.3 | `assertion_kind` | `evidence_status` máximo automático |
|---|---|---|
| `observado` | `observed` | `declared` após revisão humana |
| `inferido` | `inferred` | não eleva evidência |
| `declarado_nao_verificado` | `declared` | `declared` |
| `declarado_verificado` | `declared` | depende da fonte: `documented` ou `verified` |

`declarado_verificado` nunca gera `verified` apenas pelo nome. O artefato, método, emissor, escopo e revisão continuam obrigatórios.

## Entidades mínimas

### `textile_sample`

- `sample_id`
- `organization_id`
- `external_reference`
- `sample_kind`: `physical_sample | product_image_only | document_only`
- `received_at`
- `created_at`

### `artifact`

- `artifact_id`, `sample_id`
- `artifact_type`: `image | video | document | measurement_file`
- `view_type`: `face | reverse | macro_weave | transmitted_light | edge_selvage | drape | stretch | label | other`
- `sha256`, `mime_type`, `byte_size`, `captured_at`
- `source_type`, `source_actor_id`
- dispositivo, iluminação, distância, ampliação e presença de escala
- `license_or_consent`
- `quality_flags[]`

### `assessment`

- `assessment_id`, `sample_id`
- `protocol_version`, `taxonomy_version`, `contract_version`
- `model_id`, `model_version`, `prompt_version`
- `assessor_type`: `human | model | hybrid`
- `assessor_id`
- `status`: `draft | insufficient_evidence | provisional | confirmed | rejected`
- `parent_assessment_id`
- timestamps e limitações

### `field_assertion`

- `assertion_id`, `assessment_id`
- `attribute_code`, `value`, `unit_code`
- `assertion_kind`: `observed | measured | inferred | declared | derived`
- `method_code`
- `evidence_status`: `absent | declared | calculated | documented | verified`
- `source_artifact_ids[]`, `source_assertion_ids[]`
- `raw_model_score`
- `calibrated_probability`, `calibration_version`
- intervalo de incerteza
- `review_state`, reviewer e timestamps

### `hypothesis_set`

- `target_code`: `fiber_composition | commercial_name | finish | weave_variant`
- `semantics`: `exclusive_probability | compatibility_score`
- `normalization_rule`: `sum_to_one | independent_scores`
- `unknown_score`
- candidatos, evidências favoráveis e contrárias
- `calibration_version` quando houver probabilidade

### `test_event`

- método e versão
- operador e timestamps
- `safety_class`: `safe | supervised | laboratory_only`
- resultado, unidade, réplicas e artefatos
- nível de evidência

### `decision_event`

- `decision`: `request_more_images | request_test | provisional_classification | confirm | abstain | reject_input`
- afirmações e hipóteses selecionadas
- regra, motivos e timestamp

## Invariantes

- Todo artefato possui hash e origem.
- Toda afirmação não ausente aponta para fonte.
- Valor calculado registra método, fórmula e inputs.
- `verified` exige documento ou ensaio aceito e revisão humana.
- Probabilidades exclusivas, incluindo `unknown`, somam 1 ± 0,001.
- `compatibility_score` não é chamado de probabilidade.
- Probabilidade calibrada exige `calibration_version`.
- Não existe `confidence` global.
- Correções preservam a avaliação anterior.
- Conceito desconhecido retorna `unknown/other`, não uma classe inventada.

## Gate de saída da Semana 01

- contrato validado contra fixtures válidas e inválidas;
- conceitos com definição, pai, exemplos e contraexemplos;
- duas revisões especializadas e divergências adjudicadas;
- 100% das afirmações rastreáveis a fonte, método, ator e versão;
- zero probabilidade exposta sem calibração;
- zero composição confirmada por imagem;
- todos os cenários insuficientes retornam abstenção ou pedido de evidência;
- limitações e classes fora de distribuição documentadas.
