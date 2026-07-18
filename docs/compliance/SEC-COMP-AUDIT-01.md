# PHYLLOS — Segurança, Compliance e Readiness para Auditorias Externas

**Pacote:** SEC-COMP-AUDIT-01
**Versão:** 0.1.0
**Data:** 2026-07-18
**Status:** baseline operacional para revisão e aprovação humana

## Finalidade

Este pacote materializa a missão conjunta dos agentes de Compliance, Risco, Segurança, Privacidade, Governança de IA, Evidências, Terceiros, Audit Readiness e Auditoria Interna.

Ele cria a arquitetura documental inicial para avaliações de clientes, parceiros, investidores, autoridades, organismos de certificação e diligências enterprise. Não representa certificação, parecer jurídico ou confirmação de eficácia dos controles.

## Modelo de três linhas

1. **Primeira linha:** Produto, Engenharia, Dados, IA, Segurança, Operações e CS implementam e operam controles.
2. **Segunda linha:** Compliance, Privacidade, AI Governance, Evidence Governance, Third-Party Risk e Audit Readiness definem requisitos e supervisionam.
3. **Terceira linha:** Internal Audit & Assurance avalia desenho e eficácia sem operar os controles.

## Estrutura

- `policies/`: 30 políticas P0 em estado `draft`.
- `registers/`: obrigações, riscos/controles, políticas, ativos, IA e terceiros.
- `audit-readiness/`: brief, PBC list, data room e mock audit.
- `control-evidence/`: catálogo e regras para evidências.
- `internal-audit/`: plano inicial de assurance baseado em risco.
- `governance/`: template, taxonomia e critérios de aprovação.

## Gates

- **Produto:** nenhum PRD é Ready sem requisitos aplicáveis de segurança, privacidade, IA, evidência e retenção.
- **Mudança:** alteração material exige análise de impacto, revisão, versão e rollback.
- **Publicação:** nenhum claim técnico, ambiental, regulatório ou de IA sem evidência, escopo, owner, validade e expiração.
- **Auditoria:** nenhuma resposta material é enviada sem revisão do Audit Readiness e aprovação humana.

## Estados permitidos para controles

- `implemented_and_tested`
- `implemented_not_tested`
- `partially_implemented`
- `planned`
- `not_applicable`
- `not_implemented`

A ausência de controle ou evidência deve permanecer visível. `draft` não equivale a implementado.

## Próxima decisão humana

O founder deve aprovar owners, apetite de risco, escopo inicial, prioridades de implementação e referenciais externos escolhidos. Depois, a auditoria interna executará a primeira avaliação independente.
