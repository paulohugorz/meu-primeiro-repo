# USAGE-ANALYTICS-02 — Workspace, Pessoas e Colaboração

**Data:** 2026-07-22  
**Status:** implementado no contrato e dashboard; emissão operacional depende dos módulos IAM  
**Owner:** Produto / Dados  
**Fonte:** `PHYLLOS - Instrumentação de Workspace e Pessoas.pdf`

## Decisão

Adotar `usage-event-v3` para eventos administrativos de Workspace, Pessoas,
Membership e Concorrência, mantendo `usage-event-v2` durante a transição para o
funil produtivo existente.

O registro normativo está em `app/telemetry_contract.py`. Cada evento possui uma
lista fechada de propriedades. Propriedades adicionais, conteúdo livre e chaves
de dados pessoais são rejeitados com HTTP 422.

## Controles

- deduplicação por `event_id` único;
- `received_at` gerado pelo banco;
- contexto analítico por `user_id_hash` e `workspace_id_hash`, sem IDs brutos;
- fonte e ambiente validados;
- eventos v1, v2 e v3 distinguidos, sem reinterpretação retroativa;
- dashboard agregado sem sessões ou identificadores de workspace na resposta;
- migração aditiva para SQLite e PostgreSQL.

## Limite atual

Os módulos operacionais de identidade, Pessoas, Membership e Workspace não estão
presentes na `main` deste repositório na data da implementação. Assim, o coletor,
o contrato e o dashboard estão prontos, mas eventos de sucesso como
`person_created`, `workspace_member_invited` e
`workspace_first_collaborative_action_completed` devem ser emitidos pelo backend
dos módulos IAM somente depois do commit transacional correspondente.

Não é permitido ao frontend afirmar conclusão dessas operações.

## Aceite

- eventos cadastrados aceitos e desconhecidos rejeitados;
- dados pessoais e propriedades desconhecidas rejeitados;
- eventos duplicados não persistidos novamente;
- funil produtivo preservado;
- funis de Workspace, Pessoas e Equipe disponíveis;
- blocos de Workspace, Pessoas, Colaboração e Concorrência disponíveis;
- emissão backend dos módulos IAM permanece como dependência explícita.
