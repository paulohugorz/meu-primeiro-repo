# Changelog

## Graph model 0.4.1 — 2026-07-15

- Corrigido o contrato para impedir `assertion_kind=inferred` com `evidence_status=calculated`.
- `inferred` agora exige `evidence_status=absent`.
- `calculated` foi reservado a `assertion_kind=derived` com método/fórmula versionada e asserções de origem.
- Fixtures de família estrutural, ligamento e demais inferências visuais migradas para `evidence_status=absent`.
- Adicionado caso válido de derivação determinística e caso inválido específico para `inferred + calculated`.
- Documentado que `documented` preserva o artefato da observação, mas não verifica a propriedade têxtil.
- Adicionado `requirements.txt` para reprodução da validação integral.

## Graph model 0.4.0 — 2026-07-15

- Preservada taxonomia v0.3 e benchmark 1.
- Separadas identidades e revisões imutáveis.
- Removido `publicability` de `Assertion`.
- Adicionadas decisões e políticas de publicação versionadas.
- Adicionados Execution, ModelVersion, PromptVersion, CalibrationVersion, Review, Actor e AssertionConflict.
- Migradas fixtures para o contrato v0.4.
- Adicionadas regras de histórico, calibração, integridade e publicação.
