# Execution Brief — Semana 01

**Decision ID:** `PHYLLOS-DEC-PTIP-DISCOVERY-S1-2026-07-15`

**Status:** `in_execution — week_01`

**Horizonte:** uma semana de fundação; discovery total limitado a seis semanas

## Resultado esperado

Entregar um contrato validável para o Protocolo PHYLLOS de Observação e Verificação Têxtil: taxonomia revisada, protocolo seguro de captura, matriz campo × método × teto de evidência, contrato mínimo de dados e desenho do benchmark.

O protocolo deve transformar incerteza têxtil em tarefas estruturadas de coleta e verificação dentro do DPP Studio, sem transformar hipótese visual em composição comprovada.

## Escopo

Incluído:

- família estrutural e ligamento aparente;
- atributos visuais suportados;
- captura controlada e critérios de insuficiência;
- hipóteses, alternativas e abstenção;
- proveniência por afirmação;
- geração de `verification_tasks`;
- benchmark e métricas.

Fora desta fase:

- identificação conclusiva de fibras por imagem;
- autopreenchimento da composição no DPP;
- publicação de hipótese visual como fato;
- modelo de visão ou laboratório próprios;
- catálogo comercial independente;
- claims de precisão ainda não calibrados.

## Owners

| Papel | Responsabilidade |
|---|---|
| Founder | Direção, teto de esforço, política de risco e go/no-go |
| Execution Orchestrator | Escopo, dependências, evidências e gate semanal |
| Product Director | Fluxo interno, abstenção e tarefa de verificação |
| Especialista têxtil | Taxonomia, protocolo e adjudicação técnica |
| Certification Agent | Teto de evidência, linguagem e bloqueios públicos |
| Data Platform / AI | Contrato, proveniência, confiança e benchmark |
| Pilot Operations | Amostras, consentimentos e ground truth |
| QA | Casos adversariais e teste de não publicação |

## Entregáveis

1. Taxonomia v0.1.
2. Matriz campo × método × teto de evidência.
3. Protocolo de captura e segurança.
4. Contrato de dados v0.1.
5. Plano de benchmark cego.
6. Fluxo interno até `verification_tasks`.
7. Registro de riscos e decisões abertas.
8. Memorando `proceed / adjust / stop`.

## Critérios de aceite

- Todos os atributos possuem definição e opção `indeterminado`.
- Estrutura, ligamento, nome comercial, composição e acabamento não são misturados.
- Todo método possui teto explícito de evidência.
- O contrato distingue observação, medição, inferência, fonte e revisão.
- Nenhuma composição visual pode ser confirmada ou publicada.
- O fluxo consegue abster-se e pedir evidência adicional.
- A captura informa quando o material não pode ser avaliado.
- O benchmark prevê ground truth independente, cegamento e casos fora de distribuição.
- Nenhuma probabilidade é exibida sem calibração versionada.

## Riscos prioritários

| Risco | Mitigação |
|---|---|
| Falsa precisão | Copy controlada, abstenção e calibração |
| Taxonomia inconsistente | Revisão por dois especialistas |
| Ground truth fraco | Separar declaração, documento e ensaio |
| Dispersão do produto central | Teto de seis semanas e shadow mode |
| Hipótese chegar ao passaporte | Separação lógica e teste QA |
| Testes destrutivos | Excluir do fluxo doméstico |
| Viés de câmera e iluminação | Captura padronizada e conjunto adversarial |

## Decisões reservadas ao founder

1. Confirmar o protocolo como capacidade interna, não produto autônomo.
2. Aprovar teto de seis semanas e limite de custo/esforço.
3. Confirmar que hipótese visual nunca autopreenche composição pública.
4. Aprovar parceria para especialista e ground truth laboratorial.
5. Manter testes destrutivos fora do piloto com usuários.

## Gate de saída

- `PROCEED`: taxonomia, matriz, contrato, captura e owners da Semana 02 aprovados, sem impacto no caminho crítico do passaporte.
- `ADJUST`: fundação viável, mas falta especialista, amostra ou contrato necessário.
- `STOP/PAUSE`: o valor depende de alegar composição por foto, falta ground truth confiável ou o esforço compete com o passaporte usado por buyers.
