# PHYLLOS Operations — Coleta de amostras v1.1.1

**Status:** `prepared_not_sent`

Pacote operacional conectado à Taxonomia Têxtil v0.3 e ao contrato de grafo v0.4.1.

## Entregáveis principais

- `phyllos-operacoes-coleta-amostras-v1.1.1.xlsx`
- `candidate-registry-v1.1.1.json`
- `sample-intake-v1.1.1.json`
- `schemas/sample-intake-v1.1.1.schema.json`
- `operations-policy-v1.1.1.json`
- `validate_operations.py`
- `fixtures/`
- `coverage-gap-leads.json`
- `wave-1/`
- `protocolo-operacional-v1.1.1.md`
- `validation-report-v1.1.1.md`

## Validação local

```bash
python -m pip install -r requirements.txt

python validate_operations.py   --intake fixtures/validas/accepted-with-all-gates.json

python validate_operations.py   --intake fixtures/invalidas/accepted-without-gates.json

python validate_operations.py   --registry candidate-registry-v1.1.1.json
```

## Regra de autorização

As mensagens e rotas da Onda 1 estão preparadas. Nenhum contato deve ser enviado sem autorização explícita.
