# Changelog — PHYLLOS Environmental Data v0.3

## Distribuição e dependências

- adicionado `requirements.txt` com `jsonschema>=4.18,<5`;
- adicionadas instruções reproduzíveis para ambiente virtual limpo;
- mensagem amigável quando a dependência não estiver instalada.

## QA

- suíte ampliada para fatores inexistentes;
- fatores declarados com IDs duplicados;
- referências duplicadas ao mesmo fator em um cálculo;
- evidências com IDs duplicados;
- requisitos positivos e negativos de `supplier_specific_estimate`;
- requisitos positivos e negativos de `verified_environmental_profile`;
- cobertura explícita de todos os estados de `calculability_review_status`;
- confirmação de que os estados calculados exigem `approved`;
- confirmação de bloqueio de cálculos nos gates não aprovados previstos no schema.

## Segurança epistêmica

- os sete casos continuam provisórios, com revisão humana pendente;
- nenhum cálculo oficial ou alegação ambiental foi autorizado.
