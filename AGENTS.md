# PHYLLOS — Instruções globais para agentes

Este é o ponto de entrada para qualquer agente de código ou automação que
trabalhe neste repositório.

## Autoridade

O founder humano decide direção, prioridade, investimento, contratos,
aceitação de risco e go/no-go. Agentes analisam, recomendam, executam dentro
do escopo aprovado e escalam decisões.

## Referências obrigatórias

Leia antes de executar trabalho material:

1. `CLAUDE.md`
2. `.claude/agents/README.md`
3. `.claude/agents/references/agent-operating-model.md`
4. `.claude/agents/references/product-blocks-allocation.md`
5. `.claude/agents/references/compliance-assurance-operating-model.md`
6. `.claude/agents/references/compliance-initial-requirements.md`

## Entrada operacional

Demandas transversais devem passar pelo `execution-orchestrator`.

O Execution Brief deve incluir, quando aplicável:

- obrigação regulatória;
- risco afetado;
- controle preventivo ou detectivo;
- evidência esperada;
- owner do controle;
- retenção da informação;
- necessidade de revisão independente;
- exceção que exija decisão humana.

## Roteamento obrigatório

- risco corporativo ou exceção material:
  `chief-compliance-risk-officer`;
- mudança regulatória ampla:
  `regulatory-intelligence-agent`;
- requisito regulatório por campo do produto:
  `certification-agent`;
- dado pessoal, finalidade, retenção ou direito de titular:
  `privacy-data-protection-agent`;
- modelo, agente, prompt, automação ou método algorítmico:
  `ai-governance-model-risk-agent`;
- proveniência, cadeia de custódia ou retenção:
  `evidence-records-governance-agent`;
- fornecedor, subprocessador, cloud, API ou fonte externa:
  `third-party-risk-agent`;
- auditoria, diligência, certificação ou data room:
  `audit-readiness-agent`;
- teste independente de controle:
  `internal-audit-assurance-agent`.

## Segregação de funções

Quem desenha ou executa um controle não pode ser a única parte a testar sua
eficácia. Auditoria interna não implementa a correção que posteriormente
avaliará.

## Regras de evidência

Nenhuma entrega termina apenas porque código ou documento foi produzido.
Distinguir: local, integrado, testado, documentado, commitado, pushado,
publicado e verificado.

Toda afirmação regulatória, ambiental, tecnológica, financeira ou de
desempenho deve registrar fonte, versão, escopo, limitações e evidência.

## Métodos e IA

Todo cálculo, classificação, recomendação ou estimativa material deve possuir
identificador, versão, owner, fontes, entradas, fórmula ou prompt, hipóteses,
limites, validação, aprovação, changelog e critérios de retirada ou rollback.

Estimativas não calibradas devem ser rotuladas como experimentais.
