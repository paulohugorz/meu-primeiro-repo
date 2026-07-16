# Relatório de testes — PHYLLOS Environmental Data v0.3

## Ambiente limpo

- ambiente: `venv` criada sem `--system-site-packages`;
- Python: `3.13.5`;
- dependência instalada exclusivamente por `requirements.txt`;
- jsonschema instalado: `4.26.0`, dentro da faixa `>=4.18,<5`.

## Resultado

- testes executados: **16**;
- aprovados: **16**;
- falhas: **0**;
- erros: **0**;
- resultado: **OK**.

## Cobertura confirmada

- validade do JSON Schema Draft 2020-12;
- caso provisório sem cálculo;
- fatores inexistentes;
- IDs de fatores duplicados;
- referências repetidas ao mesmo fator em um cálculo;
- IDs de evidências duplicados;
- requisitos de `supplier_specific_estimate`;
- requisitos de `verified_environmental_profile`;
- todos os estados de `calculability_review_status`;
- exigência de `approved` para estados que contêm cálculo;
- bloqueio de cálculos nos gates não aprovados previstos.

O log integral está em `clean-environment-test-output.txt`.
