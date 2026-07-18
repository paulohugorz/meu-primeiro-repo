# Notas de implementação no repositório

## Arquivos novos

- `.claude/agents/references/compliance-assurance-operating-model.md`
- `.claude/agents/references/compliance-initial-requirements.md`
- oito agentes de compliance e assurance em `.claude/agents/`

## Alterações recomendadas em arquivos existentes

### `.claude/agents/references/agent-operating-model.md`

- Adicionar `chief-compliance-risk-officer` à camada de coordenação.
- Formalizar primeira, segunda e terceira linhas.
- Incluir análise de impacto regulatório, privacidade, IA, evidência e auditoria no fluxo de software.
- Acrescentar no Definition of Done: aprovação dos controles aplicáveis, evidência indexada, retenção definida e mudanças de método versionadas.

### `.claude/agents/references/product-blocks-allocation.md`

- Tornar `chief-compliance-risk-officer`, `regulatory-intelligence-agent`, `evidence-records-governance-agent` e `audit-readiness-agent` contínuos em B0–B4.
- Ativar Privacy e AI Governance desde B0 quando houver dados pessoais ou IA.
- Ativar Third-Party Risk em B1 e intensificar em B2/B4.
- Ativar Internal Audit em B1 com escopo limitado e ampliar em B3/B4.
- Inserir gates de compliance em cada transição.

### `certification-agent.md`

- Manter foco em requisitos do produto.
- Reporte funcional ao Chief Compliance & Risk Officer.
- Proibir que seja único aprovador de sua própria matriz ou teste.

## Ordem sugerida de implantação

1. Compliance Obligations Register e RCM.
2. Evidence Catalog e versionamento de métodos.
3. Inventários de IA, dados e terceiros.
4. CAPA, exceções e management review.
5. Mock audit do fluxo completo DPP.
6. Plano anual de testes independentes.
