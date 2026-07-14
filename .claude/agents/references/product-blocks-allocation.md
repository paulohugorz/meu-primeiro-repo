---
name: product-blocks-allocation
description: Alocação dos agentes PHYLLOS por bloco de produto, com founder/product/data e product design mantidos como funções humanas.
metadata:
  type: project
  version: 3.0.0
  last_reviewed: 2026-07-14
---

# PHYLLOS - Blocos de produto e alocação operacional

## Princípio

Agente contínuo não significa trabalho artificial. Significa manter uma rotina mínima de observação, controle ou preparação. Como founder/product/data e product design são funções humanas, os agentes devem preparar insumos e evidências para essas decisões, não substituí-las.

## Funções contínuas

| Agente | Rotina mínima permanente |
|---|---|
| `execution-orchestrator` | Plano, owners, dependências, status, riscos e decisões pendentes |
| `tech-lead-fullstack-data` | Arquitetura, padrões, critérios técnicos, dívida e coordenação de engenharia |
| `regulatory-specialist` | Critérios de evidência, risco de claims e atualizações regulatórias relevantes |
| `sales-partnerships-lead` | ICP, pipeline, forecast, parcerias e objeções estratégicas |
| `implementation-cs-lead` | Readiness de cliente, adoção, riscos, health score e feedback operacional |
| `finance-administration` | Caixa, orçamento, compromissos, runway, custos e métricas SaaS |

## B0 - Fundação

**Resultado:** saber o que construir, para quem, com qual evidência, dentro de qual limite financeiro e operacional.

| Frente | Entregáveis |
|---|---|
| Direção humana | Problema, prioridade, produto, dados estratégicos, design e go/no-go |
| Execução | Execution Brief, mapa de dependências e sequência validada |
| Regulação | fontes oficiais, matriz preliminar de obrigações e critérios de evidência |
| Engenharia | arquitetura, ADRs, contrato de API, schema e plano de teste |
| Implementação | plano piloto, critérios de sucesso, riscos de onboarding e suporte |
| Comercial | ICP, lista inicial de contas, objeções esperadas e playbook preliminar |
| Finanças | orçamento, caixa, premissas e limites do piloto |

**Gate B0 -> B1:** direção aprovada pelo founder humano; regulação, engenharia, implantação, comercial e finanças possuem owner, evidência esperada e critério de aceite.

## B1 - Passaporte mínimo

**Resultado:** uma marca publica, o buyer lê, o QR funciona e cada campo mostra seu nível de evidência.

Agentes principais:

- `backend-data-engineer`: APIs, dados, cálculos, validações e trilha de auditoria.
- `frontend-integrations-engineer`: fluxo de coleta, dashboard, portal público e estados de evidência.
- `regulatory-analyst`: pesquisa de fontes e atualização de cronogramas.
- `regulatory-specialist`: critérios de evidência e bloqueio de claims frágeis.
- `implementation-cs-analyst`: checklist, treinamento, coleta de dados e registros de cliente.
- `devops-security-agent`: ambiente, observabilidade, backup, permissões e segurança.

**Gate B1 -> B2:** fluxo completo validado em ambiente publicado; documentação, tracking, runbook, critérios de evidência e uso real registrados.

## B2 - Auto-serviço e cobrança

**Resultado:** a marca cadastra, publica e paga com menos dependência do founder humano.

Entregáveis adicionais:

- autenticação, organização e permissões;
- cadastro multi-SKU;
- pagamento, recibo e controle administrativo;
- CRM de ativação;
- funil aquisição -> cadastro -> publicação -> pagamento;
- suporte, alertas e operação de incidentes;
- forecast e unit economics atualizados com dados reais.

**Gate B2 -> B3:** receita real, onboarding mensurado, CAC e custo de servir conhecidos, regressão aprovada e suporte operável.

## B3 - Retenção

**Resultado:** histórico, renovação, uso recorrente e gestão de compliance sustentam assinatura.

Entregáveis adicionais:

- histórico versionado e alertas de vencimento;
- dashboard por marca;
- rotinas de sucesso, suporte e business review;
- análises de cohort, churn e LTV quando houver dados suficientes;
- conteúdo e cases baseados em evidência;
- expansão de contas dentro de escopo aprovado.

**Gate B3 -> B4:** retenção e margem comprovadas; segurança, dados e operação preparados para contratos maiores.

## B4 - Plataforma

**Resultado:** API B2B, integrações e contratos enterprise.

Entregáveis adicionais:

- API pública versionada e documentação para developers;
- conectores priorizados por demanda comprovada;
- observabilidade, SLA e segurança contratual;
- governança de dados compatível com mercados atendidos;
- parcerias estratégicas e vendas enterprise;
- tese de captação somente se ativada pelo founder humano.

## Regra de status

Nenhum agente pode declarar entrega apenas porque produziu um documento. O status deve separar: feito localmente, integrado, testado, documentado, commitado, pushado, publicado e verificado ao vivo.
