# PHYLLOS Evidence OS — Catálogo de funcionalidades e telemetria v1

**Versão:** `evidence-os-feature-telemetry-catalog-v1`

**Data:** 2026-07-22

**Bloco:** B1

**Status:** conjunto prioritário B1 implementado localmente; validação em ambiente publicado pendente

**Owner do contrato:** Data Platform Lead

**Owners de uso:** Product Director, Product Design Lead e BI Analyst

**Revisões obrigatórias:** Privacy & Data Protection e Evidence & Records Governance

## 1. Execution Brief

- **decision_id:** `EVIDENCE-OS-TELEMETRY-CATALOG-2026-07-22`
- **Direcionamento do founder:** catalogar as funcionalidades desenvolvidas no Evidence OS e definir os eventos necessários para melhorar a experiência do usuário.
- **Resultado esperado:** permitir medir descoberta, adoção, conclusão, abandono, erros e tempo até valor em cada fluxo relevante.
- **Não objetivos:** publicidade comportamental, gravação de sessão, captura de conteúdo digitado, inferência de atributos pessoais ou mudança imediata do código de telemetria.
- **Escopo verificado:** interface do Ateliê/Evidence OS, APIs de produto, fornecedores, materiais, modelagem, publicação, QR, etiqueta e passaporte público presentes no repositório.
- **Evidência esperada:** contrato versionado, eventos validados no cliente e servidor, consulta de qualidade e dashboard de UX.
- **Risco afetado:** decisões de produto baseadas em eventos ambíguos; coleta excessiva; perda de eventos de resultado; impossibilidade de distinguir falha de abandono.
- **Controles:** taxonomia em allowlist, minimização de propriedades, validação no backend, deduplicação, versionamento, retenção aprovada e teste independente.
- **Retenção proposta:** 90 dias para eventos brutos; agregados não identificáveis por até 24 meses. Depende de aprovação de Privacidade.

## 2. Estado atual da instrumentação

O contrato `usage-event-v1` aceita oito eventos genéricos: `page_view`, `ui_click`, `form_submit`, `field_change`, `api_error`, `js_error`, `flow_complete` e `visibility_end`.

Em 2026-07-22 foi implementado localmente o contrato `usage-event-v2`, mantendo compatibilidade de ingestão com a v1. A v2 adiciona eventos semânticos prioritários, normaliza rotas com identificadores, valida propriedades e enums no backend e correlaciona intenção, sucesso, bloqueio, falha e recuperação nos fluxos críticos. Esta implementação ainda não foi publicada nem verificada com uso real.

### Cobertura comprovada

- `page_view`, viewport e duração aproximada por página;
- cliques em botões, links e elementos com `data-telemetry`;
- mudanças em inputs, selects e textareas, sem seus valores;
- submissões de elementos `form`;
- respostas HTTP não exitosas feitas via `window.fetch`;
- erros globais de JavaScript sem mensagem ou stack;
- sucesso do fluxo de publicação quando a URL termina em `/dpp/publicar`;
- sessão pseudônima em `sessionStorage` e deduplicação por `event_id` no backend.

### Lacunas que impedem análise de UX

- componentes são identificados por `id`, `name`, tag ou `data-telemetry`; muitos botões dinâmicos não têm identificador semântico estável;
- ações implementadas por botões com `onclick`, e não por formulários, tornam `form_submit` pouco representativo;
- sucesso de criação, salvamento, cálculo, vínculo, exclusão, busca, upload, cópia, impressão e acesso ao QR não é registrado;
- falha de validação/publicação aparece apenas como `api_error`, sem `error_code`, quantidade ou categoria de bloqueios;
- `flow_complete` cobre somente publicação do DPP;
- não existem eventos explícitos de início de fluxo, vazio, zero resultado, retorno, cancelamento ou recuperação de erro;
- `visibility_end` pode ocorrer várias vezes na mesma página e não representa necessariamente abandono;
- a sessão não permite medir retorno entre sessões ou adoção por conta; qualquer identificador persistente exige decisão e revisão de privacidade;
- não há endpoint analítico, teste de cobertura por funcionalidade ou monitoramento da taxa de eventos rejeitados/perdidos.

## 3. Convenção recomendada para a v2

Usar eventos semânticos no padrão `<objeto>_<ação>`, no passado quando o resultado já ocorreu. Exemplos: `piece_created`, `material_linked`, `dpp_publication_blocked`.

Todo fluxo relevante deve observar quatro momentos, quando aplicáveis:

1. **entrada:** usuário iniciou ou acessou o fluxo;
2. **intenção:** usuário solicitou uma ação relevante;
3. **resultado:** ação concluiu ou falhou;
4. **recuperação:** usuário corrigiu o problema e concluiu.

### Propriedades comuns permitidas

| Propriedade | Uso | Regra |
|---|---|---|
| `schema_version` | versão do contrato | obrigatório |
| `event_id` | deduplicação | UUID aleatório |
| `session_id` | sequência dentro da aba/sessão | pseudônimo e efêmero |
| `occurred_at` | ordenação temporal | UTC |
| `surface` | `studio`, `atelier`, `public_passport`, `label`, `api` | enum |
| `page` | rota sem query string | allowlist |
| `flow` | jornada funcional | enum |
| `step` | etapa da jornada | enum |
| `component` | controle semântico estável | `data-telemetry`, nunca texto visível |
| `outcome` | `success`, `failure`, `blocked`, `cancelled`, `empty` | enum |
| `error_code` | causa operacional estável | enum; sem mensagem livre |
| `duration_ms` | tempo técnico ou de fluxo | número; preferir também faixas em análises |
| `result_count_bucket` | utilidade de busca | `0`, `1_5`, `6_20`, `21_plus` |
| `validation_issue_count` | intensidade de atrito | número, sem nomes/valores de campos |
| `evidence_level` | nível selecionado | enum permitido; sem conteúdo da evidência |

Não coletar nome, e-mail, CNPJ, GTIN, código/nome da peça, fornecedor, texto de busca, descrição, medidas corporais, composição, certificados, URLs com parâmetros, arquivos, mensagens livres, stack trace ou valores de campos.

## 4. Catálogo funcional e eventos recomendados

**Status funcional:** `UI` = disponível na interface; `API` = disponível no backend; `PUBLIC` = superfície pública. A presença no código não comprova publicação nem uso real.

### 4.1 Entrada, navegação e descoberta

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Abrir Studio/Ateliê | UI | `workspace_viewed` | entrada e retorno ao produto |
| Navegar pelas etapas Descrever → Selecionar → Ajustes → Técnico → Ficha → Material → Corte → Validar | UI | `workflow_step_viewed`, `workflow_step_backtracked`, `workflow_step_locked_clicked` | progressão, retorno e navegação bloqueada |
| Buscar peça existente | UI/API | `piece_search_started`, `piece_search_completed` | uso da busca e zero resultado |
| Visualizar lista de peças | UI/API | `piece_list_viewed`, `piece_list_empty_viewed` | descoberta do acervo e primeiro uso |

### 4.2 Ideação, molde e seleção de peça

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Descrever intenção da peça e usar chips | UI | `piece_brief_started`, `piece_brief_option_selected`, `piece_brief_completed` | início e conclusão sem capturar a descrição |
| Buscar variações de molde por filtros | UI/API | `pattern_search_started`, `pattern_search_completed`, `pattern_search_failed` | latência, zero resultado e erro |
| Selecionar ou remover molde | UI | `pattern_selected`, `pattern_selection_removed` | utilidade das recomendações |
| Recomendar referências de modelagem | API | `pattern_recommendation_requested`, `pattern_recommendation_completed` | adoção e cobertura das recomendações |
| Criar peça | UI/API | `piece_create_started`, `piece_created`, `piece_create_failed`, `piece_create_cancelled` | conversão do primeiro objeto e causas de falha |
| Abrir peça existente | UI/API | `piece_opened` | recorrência e continuidade de trabalho |

### 4.3 Ajustes e desenho técnico

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Preencher e salvar medidas/ajustes | UI/API | `fit_adjustment_started`, `fit_adjustment_saved`, `fit_adjustment_save_failed` | conclusão e erro; nunca coletar medidas |
| Gerar/atualizar desenho técnico | UI | `technical_drawing_requested`, `technical_drawing_rendered`, `technical_drawing_failed` | uso e confiabilidade do desenho |
| Anexar referência técnica por arquivo ou arrastar/soltar | UI | `technical_reference_upload_started`, `technical_reference_uploaded`, `technical_reference_upload_failed` | adoção, canal e falhas; apenas `file_type` e faixa de tamanho se aprovados |
| Remover referência técnica | UI | `technical_reference_removed` | retrabalho e correção |
| Criar, revisar e excluir especificação de modelagem | API | `modeling_spec_created`, `modeling_spec_revised`, `modeling_spec_deleted`, `modeling_spec_action_failed` | uso do ciclo de revisão |

### 4.4 Ficha técnica e evidência

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Preencher ficha por seletores e observações | UI/API | `technical_sheet_started`, `technical_sheet_field_edited` | campos que geram atrito, sem valor |
| Salvar/criar/atualizar ficha | UI/API | `technical_sheet_save_started`, `technical_sheet_saved`, `technical_sheet_save_failed` | conclusão, latência e erro |
| Definir status de evidência por campo | API/modelo | `evidence_level_selected`, `evidence_level_changed` | evolução de qualidade documental sem capturar conteúdo |
| Consultar referências visuais e vinculá-las à peça | API | `visual_reference_search_completed`, `visual_reference_linked`, `visual_reference_link_failed` | uso do apoio visual |

### 4.5 Materiais, impacto e certificações

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Buscar catálogo de matérias-primas | UI/API | `material_search_started`, `material_search_completed`, `material_search_failed` | zero resultado, latência e falha |
| Navegar por grupos de materiais | UI/API | `material_group_opened`, `material_group_result_viewed` | descoberta sem busca textual |
| Vincular material de fornecedor à peça | UI/API | `material_link_started`, `material_linked`, `material_link_failed` | adoção e falhas de vínculo |
| Remover material vinculado | UI/API | `material_unlinked`, `material_unlink_failed` | correções/retrabalho |
| Compor fibras manualmente e validar total | UI/API | `fiber_row_added`, `fiber_row_removed`, `composition_validation_failed`, `composition_completed` | dificuldade para atingir composição válida |
| Calcular fatores do blend e indicadores da peça | UI/API | `impact_calculation_started`, `impact_calculated`, `impact_calculation_failed` | conclusão, latência e causa estável da falha |
| Adicionar/remover certificação e informar reciclado | UI/API | `certification_section_enabled`, `certification_added`, `certification_removed`, `recycled_content_enabled` | adoção sem coletar número ou conteúdo |
| Salvar cuidados, composição e dados ambientais | UI/API | `material_sheet_save_started`, `material_sheet_saved`, `material_sheet_save_failed` | conclusão da etapa material |
| Consultar banco e evidências de fatores de impacto | API | `impact_evidence_viewed`, `impact_database_summary_viewed` | transparência/metodologia |

### 4.6 Fornecedores e cadeia produtiva

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Criar, consultar, editar e remover fornecedor | API | `supplier_created`, `supplier_viewed`, `supplier_updated`, `supplier_deleted`, `supplier_action_failed` | adoção e manutenção cadastral |
| Adicionar/remover produto do fornecedor | API | `supplier_product_added`, `supplier_product_removed`, `supplier_product_action_failed` | cobertura do catálogo próprio |
| Adicionar/remover certificação do fornecedor | API | `supplier_certification_added`, `supplier_certification_removed`, `supplier_certification_action_failed` | cobertura documental |
| Registrar e listar etapa produtiva | UI/API | `production_stage_add_started`, `production_stage_added`, `production_stage_add_failed`, `production_timeline_viewed` | completude da rastreabilidade e erro |

### 4.7 Validação, publicação e histórico

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Abrir painel de validação | UI | `publication_readiness_viewed` | intenção de publicar |
| Solicitar publicação | UI/API | `dpp_publication_started` | denominador do funil de publicação |
| Gate bloquear publicação | UI/API | `dpp_publication_blocked` | `validation_issue_count` e `error_code`; nunca conteúdo livre |
| Publicar DPP com sucesso | UI/API | `dpp_published` | principal evento de ativação B1 |
| Corrigir após bloqueio e republicar | UI/API | `dpp_publication_recovered` | capacidade de recuperação e clareza dos erros |
| Consultar ledger/histórico de publicações | API | `publication_history_viewed` | uso de auditoria e versionamento |

### 4.8 Painel, compartilhamento, QR e etiqueta

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Abrir painel de peças e status | UI | `dashboard_viewed` | recorrência de gestão |
| Abrir passaporte após publicação | UI/PUBLIC | `dpp_share_screen_viewed`, `public_passport_viewed` | chegada ao valor interno e consumo externo |
| Copiar link do passaporte | UI | `dpp_link_copied`, `dpp_link_copy_failed` | intenção de compartilhar |
| Abrir/ocultar prévia do QR | UI | `qr_preview_opened`, `qr_preview_closed`, `qr_load_failed` | confiança antes de imprimir/compartilhar |
| Gerar/abrir QR GS1 Digital Link | API/PUBLIC | `qr_requested`, `qr_served`, `qr_request_failed` | confiabilidade do acesso por QR |
| Abrir e imprimir etiqueta | UI/PUBLIC | `label_viewed`, `label_print_requested` | conclusão operacional; impressão efetiva não é garantida pelo browser |
| Consultar DPP por API pública | API/PUBLIC | `public_dpp_api_requested`, `public_dpp_api_served`, `public_dpp_api_failed` | integração/consumo técnico, preferencialmente por log servidor |

### 4.9 Experiência do passaporte público

| Funcionalidade desenvolvida | Status | Eventos principais | Sinal de UX |
|---|---|---|---|
| Ver identidade, composição, impacto, circularidade e cadeia | PUBLIC | `public_passport_section_viewed` | seções alcançadas; propriedade `section` em enum |
| Navegar no carrossel/cards e indicadores | PUBLIC | `public_passport_card_changed` | compreensão e profundidade de leitura |
| Ver status de evidência, fonte e metodologia | PUBLIC | `evidence_explanation_viewed`, `impact_source_viewed` | busca por confiança e transparência |
| Sair/ocultar a página | PUBLIC | `public_passport_session_ended` | duração aproximada e último card, sem inferir sucesso isoladamente |

## 5. Eventos prioritários para o piloto B1

Instrumentar primeiro o conjunto mínimo que responde se uma marca consegue publicar e se um buyer consegue consumir o passaporte:

1. `workspace_viewed`
2. `piece_create_started`, `piece_created`, `piece_create_failed`
3. `technical_sheet_saved`, `material_sheet_saved`, `production_stage_added`
4. `publication_readiness_viewed`
5. `dpp_publication_started`, `dpp_publication_blocked`, `dpp_published`, `dpp_publication_recovered`
6. `dpp_link_copied`, `qr_requested`, `qr_served`, `label_print_requested`
7. `public_passport_viewed`, `public_passport_section_viewed`, `evidence_explanation_viewed`
8. eventos `*_failed` dos mesmos fluxos, com `error_code` controlado.

Eventos de baixo sinal, como cada clique ou cada alteração de campo, devem ser usados apenas para perguntas específicas e com amostragem/expiração definida. O catálogo semântico não elimina a telemetria técnica, mas evita que ela seja a fonte principal de decisão de produto.

## 6. Métricas de experiência derivadas

| Pergunta | Métrica | Eventos |
|---|---|---|
| O usuário chega ao primeiro valor? | taxa de ativação = sessões com `dpp_published` / sessões com `workspace_viewed` | workspace e publicação |
| Onde o fluxo perde usuários? | conversão entre etapas e abandono após tempo limite acordado | `workflow_step_viewed` + resultados por etapa |
| Quanto tempo leva para publicar? | mediana e p75 entre `piece_created` e `dpp_published` | criação e publicação |
| O gate ajuda ou paralisa? | taxa de bloqueio, recuperação e tempo até recuperação | started, blocked, recovered/published |
| Quais etapas geram retrabalho? | retornos de etapa, remoções e múltiplos salvamentos | backtracked, removed, saved |
| Busca de molde/material funciona? | zero-result rate, seleção após busca e latência | search completed + selected/linked |
| O compartilhamento funciona? | cópia de link, QR servido e etiqueta solicitada por DPP publicado | sharing/QR/label |
| O buyer entende a evidência? | alcance de seções e abertura de explicações/fontes | passport section/evidence/source |
| A interface é confiável? | falhas por 100 ações e sessões com erro JS/API | eventos de falha |

`dpp_published` é a ativação operacional da marca. Não deve ser confundido com valor comprovado para o buyer; este exige ao menos consumo do passaporte e, idealmente, pesquisa qualitativa ou feedback explícito.

## 7. Controles de privacidade, qualidade e evidência

- aprovar finalidade, base legal, transparência, retenção e descarte antes da produção;
- separar telemetria de UX de logs de segurança e do ledger regulatório;
- registrar versão, owner, changelog e data de retirada de cada evento;
- validar enums e limites de tamanho no servidor; rejeitar chaves desconhecidas;
- nunca enviar valores de campos, seletores contendo dados de negócio ou mensagens de erro livres;
- preferir eventos de resultado emitidos pelo backend para mutações críticas; o cliente registra intenção e percepção da UI;
- usar `event_id` ou chave de correlação para evitar contar intenção e confirmação como duas conversões;
- medir `accepted`, `rejected`, duplicados, atraso de ingestão e eventos sem propriedade obrigatória;
- testar cobertura em unidade, integração e fluxo ponta a ponta;
- exigir teste independente dos controles de minimização e allowlist antes de declarar eficácia;
- não habilitar identificação persistente de usuário/organização sem decisão do founder e revisão de Privacidade.

## 8. Critérios de aceite da futura implementação

- eventos prioritários emitidos em sucesso, falha e bloqueio com contrato versionado;
- nenhuma amostra de payload contém conteúdo digitado ou identificador proibido;
- backend rejeita evento, propriedade ou enum fora da allowlist;
- testes demonstram deduplicação e correlação dos resultados críticos;
- dashboard distingue entrada, intenção, sucesso, falha, bloqueio e recuperação;
- documentação e changelog atualizados;
- retenção e descarte configurados e comprovados;
- QA valida o fluxo completo em ambiente publicado;
- revisão independente registra escopo, amostra, resultado e limitações.

## 9. Decisões que permanecem com o founder

1. aprovar a prioridade do conjunto B1 acima;
2. decidir se o piloto precisa medir retorno entre sessões ou apenas sessões pseudônimas efêmeras;
3. aprovar eventual identificação pseudônima de conta após análise de privacidade;
4. definir a ferramenta de análise/dashboard e o orçamento correspondente;
5. aprovar a retenção final antes de produção.

## 10. Fontes e limitações desta versão

Fontes locais consultadas: `app/main.py`, `app/api/routes.py`, `app/api/fornecedores.py`, `app/api/modelagem.py`, `app/api/catalogo.py`, `app/models/models.py`, `app/schemas/schemas.py`, `app/templates/index.html`, `app/templates/dpp_consumer.html`, `app/templates/etiqueta.html`, `phyllos/telemetry.js`, `produto/decisoes/evidence-os-usage-events-v1.md` e documentos operacionais obrigatórios.

Esta é uma análise estática do repositório em 2026-07-22. “Desenvolvida” significa encontrada no código local; não significa integrada, testada, publicada ou validada com usuários. A página raiz também pode servir `phyllos/dpp-studio.html`, um artefato empacotado distinto do template do Ateliê; a paridade funcional entre as duas superfícies deve ser verificada no teste ponta a ponta antes da instrumentação.
