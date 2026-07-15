# Relatório de validação — Operations Coleta v1.1.1

## Status

`prepared_not_sent`

## Dados operacionais

- 70 candidatas;
- 70 IDs operacionais únicos;
- 6 grupos fornecedores;
- 5 famílias cobertas;
- 2 famílias com lacunas explícitas;
- 4 ondas preparadas;
- 0 solicitações enviadas;
- 0 amostras recebidas;
- 0 evidências validadas;
- 0 amostras aceitas.

## Correções executadas

### Gate de aceite no JSON Schema

Quando `DatasetIntakeDecision.outcome = accept`, o schema exige:

- `TextileSample.received = true`;
- data de recebimento;
- local de armazenamento;
- código do artigo;
- pelo menos uma Evidence;
- pelo menos um hash SHA-256;
- pelo menos uma Assertion;
- pelo menos uma Review;
- ator e data da decisão.

O validador semântico confirma que:

- as Evidence referenciadas pelas Assertions existem;
- há Review aceita ou corrigida para uma Assertion existente;
- o ator da decisão existe.

### Concentração por fornecedor

- limite: 35%;
- denominador: somente amostras aceitas;
- nenhuma amostra aceita: regra não aplicável;
- violação: bloqueio de nova aceitação e revisão do portfólio.

Teste negativo executado:

```text
Supplier A = 2/3 aceitas = 66,7%
Resultado: INVALID
```

### Área útil da planilha

O workbook foi reconstruído em arquivo novo. Últimas células com conteúdo:

- Dashboard: `N25`;
- Registro de Amostras: `AD71`;
- Matriz de Diversidade: `E17`;
- Protocolo de Coleta: `E11`;
- Checklist Evidências: `E13`;
- Contato Fornecedores: `I5`;
- Listas: `F7`;
- Lacunas e Leads: `J9`;
- Onda 1: `H8`.

Não há conteúdo ou formatação operacional planejada até `Z200` ou `AD200`.

## Testes

- JSON Schema Draft 2020-12: válido;
- `validate_operations.py`: compila;
- fixture válida com todos os gates: aceita;
- fixture inválida sem gates: rejeitada;
- cadastro atual sem amostras aceitas: válido;
- cenário de concentração acima de 35%: rejeitado;
- planilha: nenhuma fórmula com erro.
