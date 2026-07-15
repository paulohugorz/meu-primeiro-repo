# Critérios de aceite

## Captura guiada

- seis etapas são apresentadas na ordem;
- arquivos permitidos são persistidos e recebem SHA-256;
- qualidade é avaliada por etapa;
- captura rejeitada não satisfaz o gate;
- sessão incompleta fica em `quality_review`;
- sessão completa exporta os campos de captura do baseline;
- observações estruturais continuam `unknown` até avaliação apropriada.

## Verification tasks

- gatilhos derivam tarefas esperadas;
- execução repetida não duplica tarefas;
- toda tarefa tem `mode=shadow`;
- `affects_official_decision=false`;
- `user_notification_sent=false`;
- snapshots oficiais não podem ser alterados ou excluídos;
- eventos não podem ser alterados ou excluídos;
- resolução pode registrar `would_change`;
- não existe promoção automática.

## Gate futuro

A saída de shadow mode exige política nova, revisão humana e teste de rollback. Não é uma alteração de configuração simples.
