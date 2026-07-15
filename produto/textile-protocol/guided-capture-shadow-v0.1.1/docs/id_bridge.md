# Ponte persistida de identificadores

Cada candidata possui três identificadores equivalentes:

```text
OPS-TX-001
sample:ops-tx-001
textile-sample:ops-tx-001
```

A tabela `sample_id_mappings` persiste a equivalência e aceita consulta por qualquer um dos três.

As 70 candidatas reais estão carregadas com:

```text
operations_status = prepared_not_sent
physical_sample_received = false
capture_allowed = false
```

Portanto, a presença do mapeamento não autoriza captura nem cria `Evidence`.

As cinco fixtures usam namespace separado `OPS-SYN-*` e são marcadas como sintéticas.
