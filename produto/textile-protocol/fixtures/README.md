# Fixtures da modelagem v0.4

As fixtures validam apenas o contrato estrutural da asserção. Regras que dependem de dimensão, política de publicação, tipo de evidência ou relações do grafo também devem ser testadas na camada de serviço.

## Válidas

- `valid/inferred-structural-family.json`: inferência visual rastreada até execução, sem evidência elevada.
- `valid/verified-composition.json`: composição verificada, revisada e apoiada por evidência.

## Inválidas

- `invalid/inferred-as-verified.json`: tenta promover inferência a verificada.
- `invalid/uncalibrated-probability.json`: apresenta probabilidade sem versão de calibração.
- `invalid/insufficient-capture-with-high-confidence.json`: captura insuficiente com confiança alta.

O próximo lote deve cobrir política de publicação, acabamento funcional, nome comercial ambíguo, conflito, supersessão e versionamento da taxonomia.
