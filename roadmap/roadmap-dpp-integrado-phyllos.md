# Roadmap e Cronograma - PHYLLOS DPP Integrado

**Data:** 2026-07-14
**Status:** plano executivo v0.4 - atualizado para o sistema operacional de agentes 3.0
**Premissa:** toda a tecnologia deve ser desenvolvida internamente com apoio de Codex, Claude e agentes PHYLLOS.
**Produto:** DPP middleware para moda - importacao/input tecnico, calculo por peca, evidencia, QR e passaporte público.
**Versao atual do prototipo:** `phyllos/dpp-studio.html`, hash `560add24d6e31860fee858805644270b31e030b0a5d0d5ab273d21d52194b8c2`, conforme `produto/decisoes/dpp-studio-versao-canonica-2026-06-25.md`.

---

## 1. Decisao executiva dos lideres

Os lideres recomendam abandonar o Motor de Moldes como primeiro produto e concentrar a V1 em DPP integrado.

Motivo: a PHYLLOS consegue desenvolver internamente a primeira versao com Codex/Claude se o escopo for software de dados, calculo, upload, normalizacao, QR e pagina publica. Editar molde, criar CAD ou interpretar geometria complexa eleva risco, prazo e necessidade de especialista externo.

## 2. Capacidade real com Codex e Claude

### O que e viavel internamente agora

- Prototipos HTML/CSS/JS e UX funcional.
- FastAPI ou backend equivalente.
- SQLite local evoluindo para Postgres/Supabase.
- Modelagem de dados.
- Upload e armazenamento de arquivos.
- CRUD de produtos, materiais, lotes e DPPs.
- Calculo deterministico de area, perda, peso, agua, energia e carbono.
- Geracao de QR.
- Pagina publica de passaporte público.
- Testes unitarios e regressao basica.
- Documentacao tecnica, ADRs, runbooks e criterios de aceite.

### O que e viavel depois, ainda internamente

- Parser de CSV/XLSX.
- Parser parcial de PDF estruturado.
- Exportacao JSON/CSV.
- Dashboard interno.
- Integracao simples por API.
- Autenticacao e permissoes.
- Multiusuario e multiempresa.

### O que nao deve ser promessa da V1

- Parser robusto de todos os DXF/AAMA/ASTM.
- Calculo oficial de ACV.
- Auditoria ambiental.
- Compliance juridico garantido.
- Integracao nativa com todos os softwares de modelagem.
- Edicao de molde ou desenho.

## 3. Departamentos, agentes e responsabilidades

| Departamento / owner | Responsabilidade no roadmap | Entregavel principal |
|---|---|---|
| Founder humano | Direção, prioridades, investimento e go/no-go | decisões e limites aprovados |
| Founder humano / Product & Data | Problema, resultado, funcionalidades, métricas, prioridades e critérios de aceite | PRD do DPP Integrado e decisões de produto |
| Founder humano / Product Design | UX, UI, jornadas, estados e design QA | protótipo e especificação de experiência |
| Execution Orchestrator | Decomposição, owners, dependências e acompanhamento | Execution Brief e cadência semanal |
| Tech Lead Full-stack & Data | arquitetura, plano técnico, qualidade, dados e release | ADRs, contrato técnico e backlog integrado |
| Backend & Data Engineer | APIs, schema, cálculos, validações, trilha de auditoria e pipelines | API, migrations, data contract e data dictionary |
| Frontend & Integrations Engineer | telas, integrações, portal público, QR e estados de evidência | experiência implementada e integrada |
| DevOps & Security Agent | ambientes, CI/CD, observabilidade, backup, permissões e incidentes | runbook, deploy controlado e evidências de ambiente |
| Regulatory Specialist + Regulatory Analyst | fontes, interpretação, critérios de evidência e risco de claims | matriz regulatória e critérios por campo |
| Sales & Partnerships | ICP, contas, parcerias, demanda, pipeline e posicionamento B2B | plano comercial, pipeline e objeções |
| Implementation & Customer Success | piloto, onboarding, adoção, suporte, feedback e readiness operacional | plano de implementação e health score |
| Finance & Administration | realizado, comprometido, forecast, premissas, runway e unit economics | controles, orçamento e gatilhos financeiros |

O founder humano decide. O Execution Orchestrator organiza e acompanha a execução, sem substituir essa autoridade.

---

## 4. Arquitetura recomendada

### Stack inicial

- Frontend: bundle HTML canonico no prototipo; depois fonte editavel/app web leve com paridade funcional.
- Backend: FastAPI.
- Banco: SQLite no desenvolvimento; Postgres/Supabase quando houver usuario real.
- Arquivos: armazenamento local no MVP; bucket futuro.
- QR: biblioteca server-side ou geracao por endpoint.
- Calculos: modulo deterministico testado, sem IA.
- IA: apenas assistencia interna para extrair/organizar texto quando houver revisao humana.

### Modulos

```text
DPP Studio
├── Product Registry
├── Material Registry
├── Technical File Intake
├── Area/Loss Calculator
├── Indicator Engine
├── Evidence Ledger
├── DPP Publisher
├── Passport Viewer
└── QA / Audit Log
```

---

## 5. Cronograma recomendado

### Fase 0 - Alinhamento e base de decisao (semana 1)

Objetivo: travar a tese correta antes de construir.

Entregas:

- Premissa DPP integrada registrada em `.claude/agents/references/dpp-integrado-strategic-premises.md`.
- Roadmap vigente criado.
- PRD v0 registrado em `produto/decisoes/prd-dpp-integrado-v0.md`.
- Criterios de aceite do MVP registrados em `produto/decisoes/prd-dpp-integrado-v0.md`.
- Contrato de dados registrado em `produto/decisoes/dpp-data-contract-v0.md`.
- QA anti-greenwashing registrado em `produto/decisoes/dpp-anti-greenwashing-qa-v0.md`.
- Backlog Codex registrado em `produto/decisoes/backlog-codex-dpp-2026-06-25.md`.
- Lista de 5 usuarios/pilotos-alvo.

Responsaveis:

- Execution Orchestrator.
- Founder humano / Product & Data.
- Founder humano / Product Design.
- Tech Lead Full-stack & Data.
- Backend & Data Engineer.
- Regulatory Specialist.
- Sales & Partnerships Lead.
- Finance & Administration.

Critério de aceite:

- todos os lideres sabem que V1 nao edita molde;
- backlog inicial organizado por fases;
- riscos juridicos e de greenwashing declarados.

### Fase 1 - Prototipo navegavel e modelo de dados (semanas 2-3)

Objetivo: transformar a tese em fluxo testavel.

Entregas:

- `phyllos/dpp-studio.html` substituido pela versao canonica fornecida pelo founder e validado por hash.
- fluxo demonstrado: intencao -> tipo de peca -> materiais -> especificacoes -> indicadores -> dossie/QR.
- contrato futuro segue mirando: upload/input tecnico -> produto -> material -> calculo -> evidencia -> passaporte público.
- schema conceitual em SQL/Markdown, a partir de `produto/decisoes/dpp-data-contract-v0.md`.
- dicionario de dados, a partir de `produto/decisoes/dpp-data-contract-v0.md`.
- formulas documentadas.
- criterios de evidencia por campo.

Responsaveis:

- Founder humano / Product Design.
- Tech Lead Full-stack & Data.
- Backend & Data Engineer.
- Regulatory Specialist.
- Frontend & Integrations Engineer.

Uso de Codex/Claude:

- Codex preserva o bundle canonico, implementa schema e validacoes ao redor dele, e so altera a UI com nova decisao/hash.
- Claude auxilia em PRD, copies, criterios de aceite e entrevistas.

Critério de aceite:

- 3 pessoas entendem o fluxo sem explicacao longa;
- calculos atualizam ao alterar area/perda/material;
- passaporte deixa claro o que e estimado/declarado/documentado.

### Fase 2 - Backend interno MVP (semanas 4-6)

Objetivo: sair de prototipo estatico para app interno funcional.

Entregas:

- FastAPI com entidades: produto, material, arquivo tecnico, lote, indicador, DPP, passaporte público.
- SQLite com migrations simples.
- endpoint para calcular indicadores.
- endpoint para gerar DPP rascunho.
- endpoint de pagina publica por slug/codigo.
- upload de arquivo com metadados.
- testes unitarios dos calculos.

Responsaveis:

- Tech Lead Full-stack & Data.
- Backend & Data Engineer.
- Frontend & Integrations Engineer.
- DevOps & Security Agent.

Uso de Codex/Claude:

- Codex desenvolve backend, testes e rotas.
- Claude revisa especificacoes, edge cases e documentacao.

Critério de aceite:

- criar DPP completo por API;
- recalcular indicadores com teste deterministico;
- salvar arquivo/metadados;
- publicar passaporte em rota local.

### Fase 3 - Studio interno e QR funcional (semanas 7-9)

Objetivo: criar a ferramenta utilizavel por uma marca/atelie piloto.

Entregas:

- tela interna de cadastro de produto.
- tela de material/fatores.
- tela de arquivo tecnico e area/perda.
- preview do passaporte.
- QR apontando para pagina publica local/staging.
- status de evidencia por campo.
- exportacao simples JSON/CSV.

Responsaveis:

- Founder humano / Product Design.
- Tech Lead Full-stack & Data.
- Frontend & Integrations Engineer.
- Backend & Data Engineer.
- DevOps & Security Agent.

Critério de aceite:

- usuario cria DPP sem tocar no codigo;
- QR abre pagina publica;
- campos ausentes aparecem como lacunas;
- interface funciona em desktop e tablet.

### Fase 4 - Piloto com dados reais (semanas 10-12)

Objetivo: validar se a PHYLLOS resolve dor real.

Entregas:

- plano operacional de piloto em `produto/decisoes/phyllos-dpp-v1-estrategia-piloto.md`;
- 3 a 5 produtos reais cadastrados.
- pelo menos 2 tipos de arquivo/input tecnico usados.
- matriz de materiais com fatores reais ou declarados.
- relatorio de lacunas por produto.
- feedback de usuarios piloto.
- decisao go/no-go para MVP publico.

Responsaveis:

- Founder humano / Product & Data.
- Sales & Partnerships Lead.
- Account Executive & Partnerships.
- Implementation & Customer Success Lead.
- Implementation & Customer Success Analyst.
- Regulatory Specialist.
- Tech Lead Full-stack & Data.
- Execution Orchestrator, que leva o go/no-go ao founder.

Critério de aceite:

- 5 DPPs rascunho gerados com dados reais;
- onboarding medio abaixo de 60 minutos para dados Tier 1;
- 2 QRs compartilhados espontaneamente em canal real;
- 1 marca pede cadastro de segunda peca;
- usuários entendem o valor do passaporte;
- lacunas recorrentes viram backlog;
- nenhuma claim ambiental e publicada sem status de evidencia.

### Fase 5 - MVP fechado / beta privado (meses 4-5)

Objetivo: preparar produto para usuarios externos controlados.

Entregas:

- login simples.
- organizacao/empresa.
- permissoes basicas.
- historico de versoes do DPP.
- storage de arquivos.
- logs de alteracao.
- termos e aviso de dados.
- deploy controlado.

Responsaveis:

- Tech Lead Full-stack & Data.
- Founder humano / Product Design.
- Backend & Data Engineer.
- Frontend & Integrations Engineer.
- DevOps & Security Agent.
- Implementation & Customer Success Lead.
- Implementation & Customer Success Analyst.
- Finance & Administration.

Critério de aceite:

- beta com 3 marcas/atelies;
- 20 DPPs gerados;
- custo mensal de infra controlado;
- bugs criticos zerados antes de expandir.

### Fase 6 - Integracoes e parsers (meses 6-8)

Objetivo: reduzir trabalho manual.

Entregas:

- parser CSV/XLSX de encaixe.
- importacao padrao de ficha tecnica.
- leitura parcial de PDF quando estruturado.
- API externa para criar DPP.
- conectores documentados.

Responsaveis:

- Tech Lead Full-stack & Data.
- Backend & Data Engineer.
- Frontend & Integrations Engineer.
- DevOps & Security Agent.

Critério de aceite:

- importar ao menos 2 formatos reais recorrentes;
- reduzir tempo de criacao de DPP em 50%;
- erros de importacao tratados com fallback manual.

---

## 6. Cronograma resumido

| Periodo | Marco | Resultado |
|---|---|---|
| Semana 1 | Alinhamento | tese e lideres sincronizados |
| Semanas 2-3 | Prototipo + dados | fluxo testavel e schema |
| Semanas 4-6 | Backend MVP | API, banco, calculos e DPP rascunho |
| Semanas 7-9 | Studio interno | interface, QR e passaporte público |
| Semanas 10-12 | Piloto real | 5 DPPs com dados reais |
| Meses 4-5 | Beta privado | multiusuario basico e deploy |
| Meses 6-8 | Parsers/integracoes | importacao parcial e API |

---

## 7. Backlog por prioridade

### P0 - precisa existir para MVP

- Schema de produto/material/DPP.
- Formula de indicadores.
- Upload de arquivo.
- Input manual de area/perda.
- Cadastro de material com fatores.
- Calculo por peca.
- Status de evidencia.
- QR e pagina publica.
- Testes dos calculos.

### P1 - melhora piloto

- Exportacao JSON/CSV.
- Historico de versao.
- Dashboard de lacunas.
- Templates de passaporte.
- Importacao CSV/XLSX.
- Autenticacao simples.

### P2 - futuro

- Parser DXF/AAMA/ASTM.
- Integracoes nativas com ferramentas de modelagem.
- Assinatura/verificacao.
- JSON-LD completo.
- Multiempresa robusto.
- API para parceiros.

---

## 8. Riscos e mitigacoes

| Risco | Mitigacao |
|---|---|
| Usuario espera que PHYLLOS edite molde | copy e onboarding: "importa dados, nao edita desenho" |
| Indicadores virarem greenwashing | estados de evidencia obrigatorios |
| Dados de area/perda virem chute | campo de origem: arquivo, declarado ou estimado |
| Arquivos tecnicos variam demais | comecar com input manual + CSV/XLSX antes de parser complexo |
| Compliance regulatorio incerto | vender "DPP-ready" e transparencia, nao conformidade garantida |
| Escopo crescer para PLM | manter P0 estreito e go/no-go semanal |

---

## 9. Cadencia de gestao

### Semanal

- segunda: Founder + Product + Tech revisam prioridade.
- quarta: checkpoint tecnico Codex/Claude.
- sexta: demo, bugs, decisoes e prox semana.

### Por fase

- abertura: criterio de aceite escrito.
- meio: risco e ajuste de escopo.
- fechamento: demo + QA + decisao de avancar.

### Artefatos fixos

- PRD.
- ADRs.
- schema.
- backlog.
- changelog.
- plano de QA.
- relatorio de piloto.
- estrategia de piloto.

---

## 10. Proxima acao recomendada

PRD v0, contrato de dados, QA anti-greenwashing, backlog Codex e estrategia de piloto ja foram registrados em `produto/decisoes/`.

Proxima acao operacional: preparar um piloto assistido com 3 a 5 marcas reais usando `produto/decisoes/phyllos-dpp-v1-estrategia-piloto.md` como roteiro. A decisao de ambiente e Railway agora, com `DPP_BASE_URL=https://phyllos-production.up.railway.app`; dominio proprio fica para depois do primeiro sinal real.

Ordem:

1. subir o app no Railway e validar `GET /p/{uuid}`;
2. selecionar 5 marcas independentes com 1 a 3 pecas prontas ou quase prontas;
3. rodar onboarding assistido de 60 minutos com uma peca por marca;
4. publicar DPP Tier 1 por SKU/UUID, com GTIN opcional e status de evidencia visivel;
5. registrar tempo, lacunas, objecoes e uso real do QR em `outputs/piloto-dpp-v1.csv`;
6. decidir entre produto pago por DPP, concierge DPP ou organizacao tecnica/PLM lite.
