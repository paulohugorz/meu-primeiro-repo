# PHYLLOS — Operação de coleta de 70 amostras têxteis v1.1.1

**Status operacional:** `prepared_not_sent`

## Estado atual

- 70 candidatas;
- 0 amostras recebidas;
- 0 solicitações enviadas;
- 0 evidências validadas;
- 0 candidatas aceitas no conjunto ouro.

## Gate executável de entrada no conjunto ouro

`DatasetIntakeDecision.outcome = accept` somente é válido quando o registro contém:

1. amostra física recebida;
2. data e local de armazenamento;
3. código do artigo do fornecedor;
4. ao menos uma evidência;
5. ao menos um hash SHA-256 de artefato;
6. ao menos uma `Assertion`;
7. ao menos uma `Review`;
8. ator e data da decisão;
9. revisão aceita ou corrigida vinculada a uma asserção existente.

O JSON Schema bloqueia os requisitos estruturais.  
`validate_operations.py` executa as validações referenciais e de portfólio.

## Regra de concentração

Nenhum fornecedor pode representar mais de **35% das amostras aceitas**.

A regra:

- é calculada apenas sobre `intake_status = Aceita` ou `mapping_status = accepted_gold`;
- não se aplica enquanto nenhuma amostra tiver sido aceita;
- bloqueia novas aceitações quando o limite for ultrapassado;
- exige revisão do portfólio antes de nova inclusão.

A concentração entre candidatas não substitui a medição entre amostras aceitas.

## URLs e documentos

As URLs atuais permanecem classificadas como leads comerciais.  
Elas não são `Evidence` validada até que o artefato correspondente seja recebido, preservado, hasheado e revisado.

## Cobertura

Famílias presentes nas 70 candidatas:

- tecido plano;
- malha de trama;
- não tecido;
- estrutura composta;
- entrelaçado/trançado.

Lacunas registradas:

- malha de urdume;
- costurado/stitch-bonded.

## Onda 1

As quatro ondas permanecem preparadas e não enviadas.  
O envio depende de autorização explícita posterior.
