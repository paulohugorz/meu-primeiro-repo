# Evidence e supersessão

Cada `CaptureItem` cria exatamente um `Evidence` com:

```text
artifact_integrity = sha256_recorded
source_authenticity = unreviewed
evidentiary_relevance = unreviewed
review_status = captured_unreviewed_shadow
```

O registro não cria automaticamente `Assertion`, `Review` ou `PublicationDecision`.

Quando uma sessão completa é refeita:

1. a nova sessão aponta `supersedes_session_id`;
2. a anterior permanece ativa enquanto a substituta está incompleta;
3. quando a nova sessão é concluída, a anterior vira `superseded`;
4. cada nova Evidence aponta a Evidence anterior da mesma vista;
5. a Evidence anterior fica `superseded_capture`;
6. nenhum artefato é apagado.
