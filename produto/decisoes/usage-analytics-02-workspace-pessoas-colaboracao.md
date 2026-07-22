# USAGE-ANALYTICS-02 — Workspace, Pessoas e Colaboração

**Data:** 2026-07-22  
**Status:** contrato, dashboard e console administrativo persistente implementados
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

## Integração operacional

O protótipo visual originado em `paulohugorz/phyllos-evidence-os-demo`, commit
`947901329a809ec9eaab27041f0870aca1fbd476`, foi portado para um console
administrativo FastAPI. Pessoas, workspaces, convites e memberships deixaram de
usar `localStorage` e passaram a persistir no banco do Evidence OS.

Os eventos `person_created`, `person_updated`, `workspace_created`,
`workspace_member_invited`, `workspace_member_invitation_accepted`, mudanças de
papel, remoções e bloqueio do último owner são emitidos pelo backend somente após
o commit transacional. IDs analíticos são gerados com HMAC-SHA-256 usando
`PHYLLOS_ANALYTICS_HMAC_SECRET`.

O console e as APIs usam a mesma autenticação administrativa HTTP Basic do
dashboard. Esse controle é suficiente para o piloto assistido, mas não substitui
provedor de identidade, sessão individual, RLS e autorização por usuário. A
promoção para uso multiusuário externo continua condicionada ao ciclo
IAM-WORKSPACE-01.

Dados pessoais operacionais (nome e e-mail) ficam restritos às tabelas IAM e não
são copiados para telemetria. Owner de privacidade: `privacy-data-protection-agent`.
A retenção acompanha a relação operacional e deve ser encerrada por arquivamento
ou exclusão conforme a política de retenção vigente antes do uso externo.

## Aceite

- eventos cadastrados aceitos e desconhecidos rejeitados;
- dados pessoais e propriedades desconhecidas rejeitados;
- eventos duplicados não persistidos novamente;
- funil produtivo preservado;
- funis de Workspace, Pessoas e Equipe disponíveis;
- blocos de Workspace, Pessoas, Colaboração e Concorrência disponíveis;
- emissão backend dos módulos IAM permanece como dependência explícita.
