# Contrato de `would_change`

A comparação aceita somente:

- `structure_family`;
- `construction_primary`;
- `visual_transparency`;
- `capture_quality`;
- `decision`.

Campos desconhecidos interrompem a execução.

Todos os valores são validados contra:

```text
benchmark-version:benchmark-1:v1.0.0
```

A comparação usa apenas a projeção congelada dessas dimensões.  
Metadados, reason codes, IDs ou campos adicionais não podem aumentar artificialmente `would_change`.
