---
policy_id: POL-SEC-004
title: "Acessos Privilegiados e Segregação de Funções"
version: 0.1.0
status: draft
classification: internal
owner: devops-security
approver: founder
second_line_review: chief-compliance-risk-officer
independent_assurance: internal-audit-assurance-agent
issued_on: 2026-07-18
review_cycle: annual_or_material_change
---

# POL-SEC-004 — Acessos Privilegiados e Segregação de Funções

## 1. Objetivo

Controlar privilégios elevados e conflitos entre criação, aprovação, publicação e auditoria.

## 2. Escopo

Aplica-se às pessoas, agentes, sistemas, dados, integrações e terceiros da PHYLLOS relacionados ao domínio **Segurança**. Exclusões devem ser documentadas no Statement of Applicability e aprovadas conforme risco.

## 3. Princípios

- risco proporcional e menor privilégio;
- evidência antes de declaração;
- escopo, versão e limitações explícitos;
- segregação entre operação, supervisão e auditoria;
- correção rastreável e aprendizado;
- nenhuma autodeclaração de certificação ou conformidade integral.

## 4. Requisitos mandatórios e controles

- **POL-SEC-004-C01:** Inventariar contas privilegiadas.
- **POL-SEC-004-C02:** Separar implementação, aprovação e promoção quando material.
- **POL-SEC-004-C03:** Registrar sessões ou ações administrativas críticas.
- **POL-SEC-004-C04:** Revogar privilégios temporários ao final da necessidade.

## 5. Papéis

- **Owner:** `devops-security` — mantém a política e supervisiona a implementação.
- **Executores:** owners dos processos e sistemas abrangidos — operam os controles.
- **Segunda linha:** `chief-compliance-risk-officer` — desafia, monitora e registra exceções.
- **Terceira linha:** `internal-audit-assurance-agent` — testa independentemente, sem operar o controle.
- **Aprovação material:** founder humano.

## 6. Evidências mínimas

- política aprovada e histórico de versões;
- registro de execução do controle e responsável;
- logs, tickets, relatórios, revisões ou atas aplicáveis;
- exceções, incidentes, achados e CAPAs relacionados;
- evidência de revisão periódica e teste de eficácia.

Toda evidência crítica deve registrar origem, autor, data, versão, hash quando aplicável, autorização, retenção e vínculo com risco/controle.

## 7. Métricas

- percentual de controles executados no prazo;
- exceções abertas e vencidas;
- achados por severidade e reincidência;
- tempo para produzir evidência;
- CAPAs vencidas e eficácia confirmada.

## 8. Exceções e aceitação de risco

A exceção deve ter justificativa, risco, owner, controle compensatório, aprovação, validade e data de expiração. Riscos materiais ou críticos dependem de decisão humana documentada.

## 9. Violações, incidentes e CAPA

Desvios devem ser registrados, classificados e tratados pelo processo de não conformidade/CAPA. Evidências desfavoráveis não podem ser ocultadas, removidas ou reclassificadas para alterar uma conclusão.

## 10. Revisão e mudança material

Revisão anual ou após mudança relevante de legislação, contrato, produto, arquitetura, dados, modelo, fornecedor, claim ou incidente. Alterações devem preservar histórico e justificativa.
