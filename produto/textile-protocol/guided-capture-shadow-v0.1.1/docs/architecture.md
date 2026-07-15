# Arquitetura — captura guiada e verification_tasks

## Componentes

```text
Web/mobile capture
    ↓
Capture API
    ↓
CaptureSession ── HAS_CAPTURE ──> CaptureItem
    ↓ completion gate
Baseline export

Rule-first predictions
    ↓
OfficialDecisionSnapshot (imutável)
    ↓ triggers
VerificationTask (shadow)
    ↓ review
ShadowResolution / ShadowEvaluation
```

## Separação crítica

`VerificationTask` não é `Review`, `Assertion` nem `PublicationDecision`.

A tarefa representa trabalho pendente para obter ou revisar evidência. A resolução pode produzir uma proposta de mudança, mas essa proposta permanece em `ShadowEvaluation`. Nenhuma aresta operacional promove automaticamente a proposta para a decisão oficial.

## Persistência

SQLite foi escolhido para o protótipo por:

- transações locais;
- integridade referencial;
- triggers de imutabilidade;
- execução sem infraestrutura externa;
- portabilidade para testes de campo.

A migração posterior para PostgreSQL deve preservar os mesmos invariantes.
