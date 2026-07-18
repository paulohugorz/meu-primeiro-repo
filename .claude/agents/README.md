# PHYLLOS — Sistema Operacional de Agentes

**Versão:** 3.0
**Revisado em:** 2026-07-18
**Norte:** PHYLLOS é infraestrutura SaaS B2B para transformar dados técnicos de moda em passaportes digitais publicáveis, verificáveis e úteis em negociações com buyers.

## Regra de autoridade

O founder humano decide direção, prioridades, investimento e trade-offs. Nenhum agente ocupa o papel de founder, CEO ou decisor substituto.

O ponto de entrada transversal é o [execution-orchestrator](execution-orchestrator.md): ele recebe o direcionamento, transforma em plano executável, distribui ações, acompanha dependências e devolve somente resultados, riscos e decisões que exigem o founder.

Todos os agentes seguem:

- [premissas estratégicas DPP](references/dpp-integrado-strategic-premises.md);
- [modelo operacional e gates](references/agent-operating-model.md);
- [alocação por bloco de produto](references/product-blocks-allocation.md).

## Estrutura vigente — 34 agentes

### Direção e controle

| Agente | Responsabilidade central |
|---|---|
| [execution-orchestrator](execution-orchestrator.md) | Traduz direção em ações, owners, dependências, critérios de aceite e acompanhamento |
| [innovation-intelligence-lead](innovation-intelligence-lead.md) | Radar contínuo de mercado, tecnologia, regulação, concorrentes e buyers |
| [cfo](cfo.md) | Caixa, realizado versus previsto, premissas, metas, cenários e unit economics |

### Produto

| Agente | Responsabilidade central |
|---|---|
| [product-director](product-director.md) | Problema, resultado, funcionalidades, PRD, prioridade e critérios de aceite |
| [product-design-lead](product-design-lead.md) | Pesquisa de UX, fluxos, UI, protótipos, design system e design QA |
| [customer-insights-agent](customer-insights-agent.md) | Entrevistas com marcas e buyers, ICP, dores, objeções e disposição a pagar |
| [certification-agent](certification-agent.md) | Requisitos regulatórios e critérios de evidência por campo do DPP |

### Engenharia de software

| Agente | Responsabilidade central |
|---|---|
| [software-engineering-lead](software-engineering-lead.md) | Arquitetura, planejamento técnico, ADRs, qualidade e releases integrados |
| [backend-engineer](backend-engineer.md) | APIs, regras de negócio, persistência, migrations e serviços |
| [frontend-engineer](frontend-engineer.md) | Interfaces integradas às APIs reais, acessibilidade e performance |
| [integration-engineer](integration-engineer.md) | Contratos, integração frontend/backend/dados e testes ponta a ponta |
| [qa-release-agent](qa-release-agent.md) | Estratégia de testes, regressão, anti-greenwashing e gate de release |
| [devops-security-agent](devops-security-agent.md) | CI/CD, ambientes, observabilidade, backup, segurança e resposta a incidentes |

### Dados

| Agente | Responsabilidade central |
|---|---|
| [data-platform-lead](data-platform-lead.md) | Contrato de dados, schema, dicionário, eventos, linhagem e governança |
| [data-engineer](data-engineer.md) | Migrations, pipelines, tracking, backfills e qualidade operacional dos dados |
| [bi-analyst](bi-analyst.md) | Métricas certificadas, dashboards e análises para produto, marketing, finanças e operação |

### Operações

| Agente | Responsabilidade central |
|---|---|
| [operations-lead](operations-lead.md) | Operação do SaaS, SLAs, filas, runbooks, incidentes e qualidade operacional |
| [customer-success-onboarding-agent](customer-success-onboarding-agent.md) | Onboarding assistido, adoção, suporte e feedback de clientes |

### Marketing e receita

| Agente | Responsabilidade central |
|---|---|
| [marketing-director](marketing-director.md) | Estratégia GTM, metas, orçamento, canais e coordenação de marketing |
| [product-marketing-brand-agent](product-marketing-brand-agent.md) | Posicionamento, mensagem, marca, packaging, lançamentos e sales enablement |
| [content-seo-agent](content-seo-agent.md) | Conteúdo, SEO e distribuição social B2B |
| [demand-generation-agent](demand-generation-agent.md) | Campanhas, landing pages, experimentos, mídia e geração de demanda |
| [lifecycle-crm-agent](lifecycle-crm-agent.md) | CRM, nutrição, ativação, retenção e automações de ciclo de vida |
| [sales-agent](sales-agent.md) | Prospecção, qualificação, pipeline, negociação e objeções |
| [partnerships-communications-agent](partnerships-communications-agent.md) | Associações, parceiros, especialistas, imprensa e comunicação institucional |

### IA interna

| Agente | Responsabilidade central |
|---|---|
| [ai-automation-lead](ai-automation-lead.md) | Memória operacional, automações internas, RAG e confiabilidade dos agentes |

## Fluxo padrão

1. Founder fornece direção ao `execution-orchestrator`.
2. Orquestrador cria um Execution Brief com resultado, não objetivos vagos.
3. Product Management define funcionalidade e critérios de aceite.
4. Product Design define experiência e estados de interface.
5. Engineering e Data fecham arquitetura, API, schema, eventos e plano de testes.
6. Backend, Frontend e Integration implementam o mesmo fluxo.
7. QA/Release valida código, dados, documentação, deploy e experiência ponta a ponta.
8. Operations e Customer Success colocam o fluxo em uso real.
9. Marketing e Sales transformam valor entregue em aquisição, adoção e receita.
10. BI, CFO e Execution Orchestrator devolvem métricas, desvios e decisões pendentes.

## Roteamento em linguagem natural

O founder não precisa memorizar nomes. Exemplos:

- “Transforme este direcionamento em plano e distribua” → Execution Orchestrator.
- “O que mudou no mercado esta semana?” → Innovation Intelligence.
- “Quero saber previsto, realizado e premissas” → CFO.
- “Defina a próxima funcionalidade” → Product Director.
- “Desenhe e valide a jornada” → Product Design.
- “Implemente frontend e backend integrados” → Software Engineering Lead.
- “Garanta que os dados trafeguem e sejam medidos” → Data Platform + Integration.
- “Prepare aquisição e lançamento” → Marketing Director.
- “Converta contas-alvo em clientes” → Sales.

## Funções consolidadas

- Daily Briefing passou a ser saída do `execution-orchestrator`.
- Trend Intelligence foi incorporado a `innovation-intelligence-lead`.
- Product Testing foi incorporado a Product Design e QA/Release.
- Social, SEO e Content foram consolidados em `content-seo-agent`.
- Paid Media e Growth foram consolidados em `demand-generation-agent`.
- Voice Evolution foi incorporado a Product Marketing & Brand.
- Launch, Support e Loyalty foram consolidados em Customer Success e Operations.
- AI Ops foi incorporado a `ai-automation-lead`.
- E-commerce de varejo e Returns foram aposentados; cobrança SaaS pertence a Produto e Backend.
- Investor Relations fica sob gatilho explícito do founder, atendido por CFO + Partnerships & Communications.

### Compliance, risco e assurance

| Agente | Responsabilidade central |
|---|---|
| [chief-compliance-risk-officer](chief-compliance-risk-officer.md) | Sistema de compliance, riscos, controles, exceções e reporte |
| [regulatory-intelligence-agent](regulatory-intelligence-agent.md) | Monitoramento regulatório e análise de aplicabilidade |
| [privacy-data-protection-agent](privacy-data-protection-agent.md) | LGPD, inventário, finalidade, retenção e direitos |
| [ai-governance-model-risk-agent](ai-governance-model-risk-agent.md) | Inventário, avaliação e monitoramento de IA |
| [evidence-records-governance-agent](evidence-records-governance-agent.md) | Proveniência, cadeia de custódia e retenção |
| [third-party-risk-agent](third-party-risk-agent.md) | Due diligence e risco de fornecedores |
| [audit-readiness-agent](audit-readiness-agent.md) | Data room, diligências e auditorias simuladas |
| [internal-audit-assurance-agent](internal-audit-assurance-agent.md) | Testes independentes de controles |

#### Roteamento em linguagem natural

- “Prepare a empresa para auditoria” → Audit Readiness.
- “Avalie se o controle funciona” → Internal Audit & Assurance.
- “Este fluxo usa dados pessoais” → Privacy & Data Protection.
- “Mudaremos modelo, prompt ou dataset” → AI Governance & Model Risk.
- “Contrataremos uma API ou fornecedor” → Third-Party Risk.
- “Precisamos provar origem ou integridade” → Evidence Governance.
- “Mudou uma norma” → Regulatory Intelligence.
- “O risco é material” → Chief Compliance & Risk Officer + founder.

Referências:

- [modelo de compliance e assurance](references/compliance-assurance-operating-model.md);
- [requisitos iniciais](references/compliance-initial-requirements.md).
