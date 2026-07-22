# PHYLLOS Evidence OS — Contrato de eventos de uso v1

**Versão:** `usage-event-v1`  
**Bloco:** B1  
**Owner operacional:** Data Platform Lead  
**Revisão de privacidade:** pendente de validação independente

## Finalidade

Medir adoção, abandono, erros e conclusão dos fluxos do Evidence OS para melhorar usabilidade e operação do piloto. Os eventos não servem para publicidade comportamental nem para inferir atributos pessoais.

## Eventos permitidos

| Evento | Evidência produzida |
|---|---|
| `page_view` | tela acessada e viewport |
| `ui_click` | componente ativado, sem texto ou valor |
| `form_submit` | formulário enviado, sem conteúdo |
| `field_change` | tipo e identificador técnico do campo, sem valor |
| `api_error` | status HTTP e etapa técnica |
| `js_error` | ocorrência de erro de interface, sem stack ou mensagem livre |
| `flow_complete` | conclusão de fluxo nomeado |
| `visibility_end` | duração aproximada da sessão na página |

## Minimização e limites

- Sessão pseudônima criada em `sessionStorage`; não usa nome, e-mail, IP no payload ou identificador de cliente.
- Query strings, conteúdo digitado, texto de botões, stack traces e valores de campos não são coletados.
- O backend aplica allowlist de eventos e metadados e deduplica por `event_id`.
- Retenção proposta: 90 dias para eventos brutos e agregados não identificáveis por até 24 meses.
- A política de retenção e o fundamento legal devem ser aprovados antes de uso em produção.

## Evidência e operação

Os registros ficam em `usage_events`, com horário do cliente e do servidor, versão do schema, página, componente, ação e metadados minimizados. Mudanças no contrato exigem nova versão, análise de impacto e changelog.
