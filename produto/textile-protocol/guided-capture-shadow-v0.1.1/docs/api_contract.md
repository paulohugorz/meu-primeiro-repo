# Contrato HTTP local

## Captura

- `GET /api/protocol`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}`
- `POST /api/sessions/{session_id}/captures`
- `POST /api/sessions/{session_id}/finalize`

O envio de imagem usa JSON com `data_base64`. É adequado ao protótipo e deve ser substituído por upload multipart ou URL pré-assinada em produção.

## Verificação shadow

- `GET /api/tasks?status=open`
- `GET /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/resolve`
- `POST /api/tasks/{task_id}/compare`
- `GET /api/shadow-report`

Não existe endpoint de promoção ou alteração da decisão oficial.
