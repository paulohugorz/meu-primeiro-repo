# Migração do modelo de grafo v0.3 para v0.4

| Campo anterior | Destino v0.4 |
|---|---|
| `dimension_id` | `dimension_revision_id` |
| `tipo_de_evidencia` | `assertion_kind` + `evidence_status` |
| `confianca` | `confidence_level` |
| `qualidade_da_captura` | `capture_quality` |
| `publicavel` | removido; criar `PublicationDecision` |
| evidência aninhada | registro em `evidence[]` e referência por ID |
| inferência visual como fonte | `Execution` consumindo `Evidence` de imagem |
| conflito booleano | `AssertionConflict` |
| correção in-place | nova `Assertion` com `supersedes_assertion_id` |

Registros históricos não devem ser alterados silenciosamente. A migração cria novas entidades e mantém os IDs de origem em uma tabela de correspondência quando necessário.
