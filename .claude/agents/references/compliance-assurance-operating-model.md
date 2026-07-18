---
name: compliance-assurance-operating-model
description: Modelo operacional da célula de compliance, riscos, auditoria e assurance da PHYLLOS.
metadata:
  type: governance
  version: 1.0.0
  last_reviewed: 2026-07-18
  owner: founder
---

# PHYLLOS — Modelo operacional de Compliance & Assurance

## 1. Objetivo

Preparar a PHYLLOS para avaliações de clientes, parceiros, auditores, organismos de certificação, autoridades e investidores, mantendo rastreabilidade dos métodos, decisões, dados, modelos, controles e evidências.

## 2. Princípios

1. **Independência:** quem desenha ou opera um controle não emite sozinho a conclusão de auditoria sobre esse controle.
2. **Evidência antes de declaração:** toda conclusão deve apontar fonte, versão, responsável, data, teste e artefato verificável.
3. **Escopo explícito:** cada avaliação informa sistema, período, produto, jurisdição, norma e limitações.
4. **Risco proporcional:** controles são priorizados por impacto, probabilidade, obrigação e exposição reputacional.
5. **Reprodutibilidade:** cálculos, classificações e avaliações precisam ser reproduzíveis a partir de entradas versionadas.
6. **Correção rastreável:** não conformidades geram owner, causa, plano, prazo, evidência de correção e teste de eficácia.
7. **Sem autodeclaração enganosa:** agentes não emitem certificação, parecer jurídico ou garantia de conformidade.

## 3. Modelo de três linhas

### Primeira linha — propriedade e operação

Product, Engineering, Data, Operations, Security, Customer Success e demais owners implementam e operam controles.

### Segunda linha — supervisão e desafio

Compliance, Risk, Privacy, AI Governance, Evidence Governance e Third-Party Risk definem políticas, requisitos, testes de desenho e monitoramento.

### Terceira linha — auditoria interna independente

Internal Audit & Assurance avalia amostras e controles sem assumir sua operação. Reporta diretamente ao founder e registra conflitos de independência.

## 4. Célula permanente

| Agente | Linha | Missão principal |
|---|---:|---|
| `chief-compliance-risk-officer` | 2 | Sistema de compliance, mapa de obrigações, risco e reporte executivo |
| `regulatory-intelligence-agent` | 2 | Radar regulatório e análise de aplicabilidade |
| `privacy-data-protection-agent` | 2 | Privacidade, LGPD, ciclo de vida e direitos dos titulares |
| `ai-governance-model-risk-agent` | 2 | Inventário de IA, risco de modelos, avaliação e monitoramento |
| `evidence-records-governance-agent` | 2 | Proveniência, retenção, integridade e cadeia de custódia |
| `third-party-risk-agent` | 2 | Due diligence e monitoramento de fornecedores e parceiros |
| `audit-readiness-agent` | 2 | Data room, PBC list, walkthroughs e coordenação de auditorias externas |
| `internal-audit-assurance-agent` | 3 | Programa independente de auditoria e teste de eficácia |

O `certification-agent` continua responsável por traduzir requisitos de produto em campos, validações e evidências. Ele passa a responder funcionalmente ao `chief-compliance-risk-officer` e operacionalmente ao `product-director`.

## 5. Artefatos mínimos

- Compliance Obligations Register.
- Risk & Control Matrix (RCM).
- Inventário de políticas, padrões, procedimentos e owners.
- Inventário de sistemas, dados, modelos de IA, fornecedores e subprocessadores.
- Catálogo de evidências com hash, origem, versão, retenção e autorização.
- Plano anual de compliance e auditoria baseado em risco.
- Registro de não conformidades, incidentes, exceções e ações corretivas.
- Data room indexado e pacote de auditoria por escopo.
- Management Review trimestral.
- Declaração de escopo e limitações para qualquer assessment externo.

## 6. Fluxo de auditoria

1. Registrar pedido e autoridade do avaliador.
2. Definir escopo, critérios, período, amostragem, confidencialidade e canal de evidências.
3. Fazer readiness assessment e gap analysis.
4. Congelar índice de evidências e versões relevantes.
5. Executar walkthroughs e testes.
6. Classificar achados: observação, oportunidade, menor, maior ou crítico.
7. Criar CAPA com causa raiz, owner, prazo e teste de eficácia.
8. Responder formalmente, preservando fatos, inferências e limitações.
9. Encerrar apenas após evidência de correção ou aceitação explícita de risco.
10. Registrar lições e atualizar controles.

## 7. Gates obrigatórios

### Gate de produto

Nenhum PRD é Ready sem requisitos regulatórios, privacidade, segurança, IA, evidência, retenção e auditoria aplicáveis.

### Gate de mudança

Mudanças em cálculo, schema, modelo, classificação, claim, fonte ou política exigem análise de impacto e trilha de aprovação.

### Gate de publicação

Nenhum claim regulatório, ambiental, técnico ou de IA é publicado sem owner, evidência, escopo, data e regra de expiração.

### Gate de auditoria

Nenhuma resposta a órgão ou auditor é enviada sem revisão do Audit Readiness e aprovação humana responsável.

## 8. Métricas

- Obrigações com fonte, aplicabilidade, owner e controle.
- Controles testados no período e taxa de eficácia.
- Achados vencidos, reincidentes e críticos.
- Tempo para produzir evidência solicitada.
- Percentual de artefatos reproduzíveis e com cadeia de custódia.
- Fornecedores críticos avaliados.
- Modelos de IA inventariados e monitorados.
- Exceções abertas e tempo de resolução.

## 9. Referenciais de desenho

A PHYLLOS usa como referências estruturais, sem declarar certificação automática: ISO 37301 para sistema de gestão de compliance; ISO 19011 para programa e condução de auditorias; ISO/IEC 42001 e NIST AI RMF para governança e risco de IA; além de requisitos legais, contratuais e setoriais aplicáveis a cada mercado.
