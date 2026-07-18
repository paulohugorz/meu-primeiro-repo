---
name: product-blocks-allocation
description: Alocação dos agentes PHYLLOS por bloco de produto, com funções contínuas e entregáveis ativados por fase.
metadata:
  type: project
  version: 2.0.0
  last_reviewed: 2026-07-02
---

# PHYLLOS — Blocos de produto e alocação operacional

## Princípio

Agente contínuo não significa trabalho artificial. Significa manter uma rotina mínima de observação, controle ou preparação. Agentes executores são acionados por entregável, mas nunca ficam desconectados do fluxo principal.

## Funções contínuas em todos os blocos

| Agente | Rotina mínima permanente |
|---|---|
| `execution-orchestrator` | Plano, owners, dependências, status, riscos e decisões pendentes |
| `innovation-intelligence-lead` | Alertas materiais, resumo semanal e radar mensal |
| `cfo` | Caixa semanal, premissas, forecast e desvios |
| `product-director` | Resultado de produto, backlog e critérios de aceite |
| `data-platform-lead` | Contratos de dados, eventos e qualidade por funcionalidade |
| `operations-lead` | Readiness operacional, runbooks, filas e incidentes |
| `marketing-director` | ICP, mensagem, canais, calendário e pipeline de demanda |
| `ai-automation-lead` | Memória, automações e integridade do sistema de agentes |

## B0 — Fundação

**Resultado:** saber o que construir, para quem, com qual evidência e dentro de qual limite financeiro.

| Frente | Entregáveis |
|---|---|
| Execução | Execution Brief, mapa de dependências e sequência validada |
| Produto | ICP, PRD, jornada assistida e critérios de aceite Tier 1 |
| Design | Fluxo navegável e estados de erro, evidência e publicação |
| Engenharia | arquitetura, ADRs, contrato de API e backlog técnico |
| Dados | schema, dicionário, migrations iniciais e catálogo de eventos |
| Operações | runbook do piloto, filas, responsabilidades e plano de incidente |
| Marketing | posicionamento inicial, lista de contas e plano de recrutamento do piloto |
| Finanças | orçamento, caixa, premissas e limites do piloto |

**Gate B0 → B1:** direção aprovada pelo founder; PRD, UX, API, dados, teste, operação, aquisição e orçamento possuem owner e critério de aceite.

## B1 — Passaporte mínimo

**Resultado:** uma marca publica, o buyer lê, o QR funciona e cada campo mostra seu nível de evidência.

Agentes de execução principais: `backend-engineer`, `frontend-engineer`, `integration-engineer`, `data-engineer`, `qa-release-agent`, `devops-security-agent`, `customer-success-onboarding-agent`.

Agentes de descoberta e mercado: `customer-insights-agent`, `product-marketing-brand-agent`, `content-seo-agent`, `demand-generation-agent`, `sales-agent`.

**Gate B1 → B2:** fluxo completo validado em ambiente publicado; documentação, tracking e runbook atualizados; uso real e objeções registrados.

## B2 — Auto-serviço e cobrança

**Resultado:** a marca cadastra, publica e paga sem depender do founder.

Entregáveis adicionais:

- autenticação, organização e permissões;
- cadastro multi-SKU;
- pagamento e recibo;
- CRM de ativação;
- funil aquisição → cadastro → publicação → pagamento;
- suporte, alertas e operação de incidentes;
- forecast e unit economics atualizados com dados reais.

**Gate B2 → B3:** receita real, onboarding mensurado, CAC e custo de servir conhecidos, regressão aprovada e suporte operável.

## B3 — Retenção

**Resultado:** histórico, renovação, uso recorrente e gestão de compliance sustentam assinatura.

Entregáveis adicionais:

- histórico imutável e alertas de vencimento;
- dashboard por marca;
- lifecycle CRM e customer success;
- análises de cohort, churn e LTV;
- conteúdo e cases baseados em evidência;
- upsell e expansão de contas.

**Gate B3 → B4:** retenção e margem comprovadas; segurança, dados e operação preparados para contratos maiores.

## B4 — Plataforma

**Resultado:** API B2B, integrações e contratos enterprise.

Entregáveis adicionais:

- API pública versionada e documentação para developers;
- conectores priorizados por demanda comprovada;
- observabilidade, SLA e segurança contratual;
- data residency e governança compatíveis com mercados atendidos;
- parcerias estratégicas e vendas enterprise;
- tese de captação somente se ativada pelo founder.

## Regra de status

Nenhum agente pode declarar entrega apenas porque produziu um documento. O status deve separar: feito localmente, integrado, testado, documentado, commitado, pushado, publicado e verificado ao vivo.

## Compliance e assurance em todos os blocos

| Bloco | Gate adicional |
|---|---|
| B0 | obrigações, inventários, matriz de riscos/controles, charters e owners |
| B1 | proveniência por campo, logs, gate de claims e segregação de aprovação |
| B2 | LGPD, permissões, pagamentos, retenção e due diligence |
| B3 | histórico imutável, revalidação, revisão de acessos e auditoria simulada |
| B4 | controles enterprise, data residency, subprocessadores e plano de auditoria |

Nenhum bloco é aprovado com risco crítico sem owner, controle, evidência ou
decisão explícita do founder.
