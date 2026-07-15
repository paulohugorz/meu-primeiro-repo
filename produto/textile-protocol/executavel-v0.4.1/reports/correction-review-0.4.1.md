# Parecer de correção — Grafo v0.4.1

## Correção obrigatória aplicada

O estado `calculated` deixou de ser aceito em asserções `inferred`.

Contrato vigente:

```yaml
assertion_kind: inferred
evidence_status: absent
```

Para resultado determinístico e reproduzível:

```yaml
assertion_kind: derived
evidence_status: calculated
method_version_id: <método ou fórmula versionada>
derived_from_assertion_ids: [<asserções de entrada>]
```

## Interpretação de `documented`

`documented` significa que existe um artefato preservado sustentando que uma observação ou declaração ocorreu. Uma imagem pode documentar a observação visual, mas não verifica, sozinha, a estrutura, composição ou função do material.

## Reprodutibilidade

O pacote inclui `requirements.txt` com a dependência `jsonschema`. A validação integral deve ser executada após instalar as dependências.
