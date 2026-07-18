# PHYLLOS — Requisitos iniciais de Compliance, Auditoria e Assurance

**Versão:** 1.0  
**Data:** 2026-07-18

## P0 — Obrigatórios agora

1. Criar o Compliance Obligations Register com jurisdição, obrigação, fonte oficial, vigência, aplicabilidade, owner, controle, evidência e status.
2. Criar Risk & Control Matrix para produto, dados, segurança, IA, claims, operação e terceiros.
3. Definir taxonomia documental: política, padrão, procedimento, runbook, registro, evidência e relatório.
4. Implantar versionamento e aprovação de métodos, fórmulas, regras, datasets, prompts, modelos e critérios de decisão.
5. Registrar inventário de IA e automações, com finalidade, owner, entradas, saídas, risco, supervisão humana e limitações.
6. Implantar trilha de auditoria imutável para criação, alteração, revisão, publicação, revogação e acesso a evidências críticas.
7. Definir retenção, descarte, legal hold e cadeia de custódia.
8. Criar processo CAPA para não conformidade, incidente, reclamação, erro de método e falha de controle.
9. Criar data room indexado com política de acesso e lista padrão de documentos solicitados em auditoria.
10. Realizar readiness review antes de qualquer avaliação externa.

## P1 — Próximo ciclo

- Programa anual de testes de controles baseado em risco.
- Due diligence de fornecedores, subprocessadores e fontes de dados.
- Privacy impact assessment e AI impact assessment para mudanças materiais.
- Segregação de funções em aprovações críticas.
- Gestão formal de exceções e aceitação de risco.
- Treinamento e confirmação periódica de responsabilidades.
- Canal de incidentes, denúncias e escalonamento.
- Métricas e management review trimestral.
- Simulação de auditoria externa e exercício de resposta a evidências.

## P2 — Preparação para escala e certificações

- Mapeamento cruzado entre controles PHYLLOS e frameworks/contratos prioritários.
- Continuous control monitoring onde houver dados confiáveis.
- Portal de assurance para clientes enterprise.
- Relatórios de controles e transparência por escopo.
- Auditorias independentes e certificações selecionadas por demanda de mercado.

## Critérios mínimos de um controle

Todo controle deve registrar: `control_id`, risco tratado, objetivo, owner, executor, frequência, entrada, procedimento, sistema, evidência, retenção, teste, resultado, exceções e ação corretiva.

## Requisitos específicos dos métodos PHYLLOS

- Fonte e versão de cada parâmetro.
- Unidade, transformação, fórmula e arredondamento.
- Hipóteses, limites de validade e incerteza.
- Dataset ou amostra de validação, quando aplicável.
- Reprodutibilidade por versão.
- Aprovação humana e segregação de funções.
- Monitoramento de drift, erro, conflito e recaptura.
- Histórico de alterações e justificativa.
- Proibição de promover estimativa experimental como fato verificado.
