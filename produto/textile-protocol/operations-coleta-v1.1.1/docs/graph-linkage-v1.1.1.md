# Especificação de vínculo operacional com o grafo v0.4.1

## Regra principal

A linha da planilha e o registro de candidata não constituem uma `Assertion`.

Os IDs taxonômicos associados às candidatas possuem status:

```text
lead_only_not_asserted
```

Eles servem para organizar aquisição e cobertura. Só se tornam asserções depois do recebimento da amostra e de evidência correspondente.

## Fluxo

```text
CandidateRegistry
→ TextileSample
→ Evidence
→ Assertion
→ Review
→ PublicationDecision
```

A decisão de entrada no conjunto ouro é representada separadamente por `DatasetIntakeDecision`.

## Regras

1. página comercial é lead, não evidência validada;
2. amostra física e documento precisam corresponder pelo código do artigo;
3. `Evidence.artifact_integrity` não confirma autenticidade ou relevância;
4. inferência visual usa `assertion_kind=inferred` e `evidence_status=absent`;
5. resultado determinístico usa `assertion_kind=derived` e `evidence_status=calculated`;
6. nenhuma publicação ocorre sem `PublicationDecision`;
7. a entrada no conjunto ouro exige `DatasetIntakeDecision.outcome=accept`.
