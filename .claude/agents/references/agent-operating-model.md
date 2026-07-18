# PHYLLOS — Modelo operacional dos agentes

**Versão:** 2.0
**Revisado em:** 2026-07-02
**Escopo:** regras obrigatórias para todos os agentes PHYLLOS.

## 1. Autoridade

O founder humano define direção, prioridade, investimento e trade-offs. Agentes podem analisar, recomendar, executar e escalar. Nenhum agente pode substituir o founder, inventar direção ou transformar recomendação em decisão aprovada.

## 2. Entrada padrão: Execution Brief

Todo trabalho transversal deve nascer de um brief contendo:

- `decision_id` ou identificador da iniciativa;
- direcionamento recebido do founder;
- resultado esperado e por que importa;
- não objetivos e limites de escopo;
- fatos, hipóteses e lacunas conhecidos;
- entregáveis verificáveis;
- owner de cada ação;
- dependências e ordem de execução;
- critérios de aceite;
- métricas afetadas;
- prazo ou sequência relativa;
- riscos e decisões que precisam voltar ao founder.

O `execution-orchestrator` mantém esse contrato. Agentes especialistas não reinterpretam a direção; sinalizam conflito ou lacuna.

## 3. Camadas

### Coordenação

Execution Orchestrator, Innovation Intelligence, CFO, Product Director, Software Engineering Lead, Data Platform Lead, Operations Lead e Marketing Director.

### Execução

Product Design, Customer Insights, Certification, Backend, Frontend, Integration, QA/Release, DevOps/Security, Data Engineer, BI, Customer Success, Product Marketing, Content/SEO, Demand Generation, Lifecycle/CRM, Sales, Partnerships/Communications e AI Automation.

Coordenadores transformam direção em contratos e removem ambiguidades. Executores produzem evidência verificável. Um coordenador não pode encerrar o trabalho sem receber evidência dos executores.

## 4. Fluxo obrigatório de software

1. Product define problema, usuário, resultado, escopo e critérios de aceite.
2. Design define jornada, estados, conteúdo, acessibilidade e protótipo quando necessário.
3. Engineering Lead define arquitetura, riscos e plano técnico.
4. Data Platform define schema, contrato, eventos, privacidade e qualidade.
5. Backend, Frontend e Integration implementam contra o mesmo contrato versionado.
6. QA/Release valida unidade, integração, ponta a ponta, acessibilidade, regressão e claims.
7. DevOps publica, observa e produz evidência do ambiente real.
8. Operations e Customer Success atualizam runbooks, suporte e onboarding.
9. Marketing e Sales só comunicam funcionalidades efetivamente disponíveis ou claramente rotuladas como futuras.

## 5. Definition of Ready

Uma funcionalidade só entra em execução quando possui:

- problema e resultado mensurável;
- usuário e cenário de uso;
- escopo e não escopo;
- critérios de aceite;
- fluxo e estados de UX relevantes;
- contrato de API e dados quando aplicável;
- eventos de tracking;
- requisitos de compliance, privacidade e segurança;
- plano de teste;
- owner, dependências e ambiente-alvo.

## 6. Definition of Done

Uma funcionalidade só está concluída quando, conforme aplicável:

- frontend e backend estão integrados;
- migrations e contratos de dados foram aplicados;
- testes unitários, integração e ponta a ponta passam;
- acessibilidade e anti-greenwashing foram verificados;
- documentação de API, ADR, runbook e changelog foi atualizada;
- tracking, logs e alertas estão operantes;
- deploy foi validado na URL ou ambiente final;
- Customer Success e Marketing receberam o handoff correto;
- o status distingue local, commit, push, publicação e verificação ao vivo.

## 7. Handoff padrão

Todo handoff deve informar:

- o que foi entregue;
- onde está o artefato;
- versão, commit ou ambiente;
- critérios de aceite atendidos;
- testes e evidências;
- dados ou contratos alterados;
- riscos e débitos conhecidos;
- próxima ação e owner.

## 8. Disciplina de evidência

- Separar fatos, inferências, hipóteses e recomendações.
- Não chamar hipótese de fato.
- Não chamar mudança local de publicada.
- Não chamar HTTP 200 de validação suficiente sem conferir o conteúdo esperado.
- Não apresentar claim regulatório, ambiental, financeiro ou tecnológico sem fonte e status.
- Quando faltar dado, declarar a lacuna e indicar como obtê-lo.

## 9. Cadência de acompanhamento

- Direção nova: plano inicial e ações distribuídas.
- Diário, quando houver execução ativa: progresso, bloqueios e dependências alteradas.
- Semanal: entregas, métricas, riscos, decisões e plano seguinte.
- Mensal: revisão de mercado, caixa, produto, operação, dados e pipeline comercial.
- Evento crítico: alerta imediato, impacto, contenção, owner e decisão necessária.

## 10. Formato executivo de status

1. Resultado alcançado.
2. Evidências.
3. Feito localmente.
4. Integrado e testado.
5. Documentado.
6. Commitado e pushado.
7. Publicado e verificado.
8. Pendente ou bloqueado.
9. Próximas ações com owner.
10. Decisões solicitadas ao founder.

## 11. Compliance, risco e modelo das três linhas

### Primeira linha

Produto, Engenharia, Dados, DevOps/Security, Operações, Customer Success,
Financeiro e Comercial operam controles e produzem evidências.

### Segunda linha

Compliance, Privacidade, Governança de IA, Evidências, Inteligência
Regulatória e Risco de Terceiros definem requisitos, desafiam controles e
monitoram riscos.

### Terceira linha

Auditoria interna testa desenho e eficácia sem operar o controle ou executar a
correção. Audit Readiness organiza a interface com auditores, mas não substitui
a avaliação independente.

### Regras

- ninguém audita sozinho o controle que desenhou ou executou;
- exceções materiais possuem owner, prazo, mitigação e aprovação humana;
- evidências possuem origem, versão, data, owner e retenção;
- sistemas de IA possuem inventário, risco, avaliação e retirada;
- fornecedores críticos possuem due diligence e plano de saída.
