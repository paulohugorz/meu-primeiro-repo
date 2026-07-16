# PHYLLOS — Validações semânticas v0.3

O JSON Schema valida estrutura, tipos e condicionais dentro de um perfil. Ele não garante, sozinho, que referências entre arrays apontem para objetos existentes nem que IDs sejam únicos.

O script `validate_environmental_profile_v0_3.py` executa as verificações adicionais:

| Regra | Referência | Destino | Erro |
|---|---|---|---|
| SEM-001 | `composition.components[].evidence_id` | `evidence[].evidence_id` | `dangling_evidence_reference` |
| SEM-002 | `physical_properties.evidence_ids[]` | `evidence[].evidence_id` | `dangling_evidence_reference` |
| SEM-003 | `supply_chain[].evidence_ids[]` | `evidence[].evidence_id` | `dangling_evidence_reference` |
| SEM-004 | `calculations[].factor_ids[]` | `environmental_factors[].factor_id` | `dangling_factor_reference` |
| SEM-005 | `evidence[].evidence_id` | IDs únicos | `duplicate_evidence_id` |
| SEM-006 | `environmental_factors[].factor_id` | IDs únicos | `duplicate_factor_id` |
| SEM-007 | `calculations[].factor_ids[]` | Referências únicas por cálculo | `duplicate_factor_reference` |

O schema também:

- exige evidência de origem permitida para `supplier_specific_estimate`;
- exige evidência com autenticidade `verified` e relevância `sufficient` para `verified_environmental_profile`;
- exige `calculability_review_status = approved` para estados com cálculo;
- bloqueia `calculations` em `pending_human_review`, `rejected` e `not_applicable`.

A suíte `test_environmental_profile_v0_3.py` cobre as regras acima e todos os valores do gate de revisão.
