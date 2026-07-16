# Relatório de execução dos agentes — PHYLLOS Ambiental v0.3

## Status geral

**Pacote preparado para distribuição técnica após validação em ambiente limpo.**

## Dependências

- dependência declarada em `requirements.txt`;
- faixa suportada: `jsonschema>=4.18,<5`;
- instruções de instalação incluídas no `README.md`.

## QA ampliado

A suíte cobre:

- schema Draft 2020-12;
- perfil provisório sem cálculo;
- fator inexistente;
- IDs de fatores duplicados;
- referências duplicadas ao mesmo fator;
- IDs de evidências duplicados;
- requisitos de `supplier_specific_estimate`;
- requisitos de `verified_environmental_profile`;
- todos os estados de `calculability_review_status`;
- exigência de aprovação para estados calculados;
- bloqueio de cálculos nos gates não aprovados previstos.

## Decisão operacional

A modelagem permanece aprovada para auditoria, coleta, revisão e implementação estrutural. Cálculos oficiais e alegações ambientais continuam bloqueados. Os sete casos identificados permanecem em `pending_human_review`.

## Confirmação em ambiente limpo

A suíte foi executada em `venv` sem pacotes do sistema, após instalação exclusiva por `requirements.txt`:

- Python 3.13.5;
- jsonschema 4.26.0;
- 16 testes executados;
- 16 aprovados;
- zero falhas e zero erros.
