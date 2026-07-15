# Gatilhos de verification_tasks v0.1.0

| Condição | Tarefa |
|---|---|
| foco ausente ou inadequado | `recapture_focus` |
| macro ausente | `recapture_macro_structure` |
| contraluz ausente | `recapture_backlight` |
| conjunto visual incompleto | `complete_capture_set` |
| sinais estruturais conflitantes | `resolve_structural_conflict` |
| família estrutural indeterminada | `verify_structure_family` |
| ligamento de tecido plano indeterminado | `verify_construction_primary` |
| transparência indeterminada | `verify_visual_transparency` |
| captura limitada, ainda que classificada | `quality_audit_limited_capture` |
| amostra de controle determinística | `control_audit` |

A geração é idempotente por amostra, snapshot oficial, tipo de tarefa e versão da política.
