# Handoff de Engineering

## Rodar localmente

```bash
python src/cli.py init-db
python src/cli.py serve
```

Abrir `http://127.0.0.1:8765`.

## Integrar com baseline

```bash
python src/cli.py ingest-baseline \
  --samples ../phyllos-baseline-human-rule-first-v0.1.0/data/demo/samples.csv \
  --predictions ../phyllos-baseline-human-rule-first-v0.1.0/outputs/demo_rule_predictions.csv
```

## Próximas integrações

1. autenticação de operador;
2. armazenamento de objetos;
3. captura de metadados EXIF com política de privacidade;
4. fila assíncrona;
5. painel de custo e tempo por tarefa;
6. vinculação formal ao grafo PHYLLOS;
7. exportação para `Evidence`, `Review` e `Execution`, sem elevar evidência indevidamente.
