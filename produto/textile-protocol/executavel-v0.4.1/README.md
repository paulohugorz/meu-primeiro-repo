# PHYLLOS — Taxonomia Têxtil v0.3 / Modelagem em Grafo v0.4.1

Este pacote preserva a **taxonomia têxtil v0.3** e o **benchmark 1**, atualizando apenas o contrato de dados e proveniência para a modelagem em grafo v0.4.

## Mudanças principais

- identidade estável separada de revisão imutável;
- `Assertion` como unidade atômica;
- remoção de `publicability` da asserção;
- publicação representada por `PublicationDecision` e `PublicationPolicyVersion`;
- inferências ligadas a `Execution`, `ModelVersion`, `PromptVersion` e evidências consumidas;
- revisão humana e atores modelados explicitamente;
- conflitos reificados;
- `SUPERSEDES` reservado à evolução temporal;
- medições, composição e acabamentos especializados sempre atravessam uma asserção;
- benchmark representado por `BenchmarkVersion` e política de capacidade.

## Entregáveis

```text
taxonomia-textil-v0.3.json
taxonomia-textil-v0.3.schema.json
fixtures/
  validas/     # 20
  invalidas/   # 20
validate.py
docs/
reports/
```

## Executar validação

```bash
python -m pip install -r requirements.txt
python validate.py --all
```

O validador executa JSON Schema Draft 2020-12 e invariantes semânticos da modelagem v0.4.1.

## Gate

O pacote não libera interface nem classificador. O protótipo pode avançar após aprovação humana de Data Platform e Certification, especialmente quanto a política de publicação e equivalências normativas ABNT.


## Semântica corrigida de evidência

- `inferred + absent`: classificação produzida por inferência, inclusive por modelo visual. A execução registra imagens consumidas, modelo e prompt, mas não transforma a inferência em cálculo.
- `derived + calculated`: resultado determinístico e reproduzível, com método ou fórmula versionada e asserções de origem explícitas.
- `observed + documented`: existe artefato preservado que documenta a observação. Uma imagem documenta que a observação foi realizada; não verifica, por si só, a propriedade têxtil.
- `verified`: exige evidência aceita e suficiente, método aplicável e revisão humana aceita.

A integridade SHA-256 de um arquivo confirma apenas que o artefato não mudou desde o cálculo do hash. Ela não confirma autenticidade, relevância ou veracidade do conteúdo.
