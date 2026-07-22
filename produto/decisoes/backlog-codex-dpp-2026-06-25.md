# Backlog Codex - DPP Integrado

**Data:** 2026-06-25  
**Status:** em execucao local - ciclo Codex C1-C6 iniciado  
**Relacionado:** [prd-dpp-integrado-v0.md](prd-dpp-integrado-v0.md)

---

## 1. Observacao sobre o repo atual

O briefing recebido cita `app/main.py`, `app/services/dpp_calculator.py`, `app/models/models.py` e `templates/dpp_public.html` como destinos de implementacao.

No checkout original deste ciclo, a raiz `app/` existia como estrutura, mas estava vazia. A implementacao FastAPI/DPP existente estava em `_legado/app/`, incluindo:

- `_legado/app/main.py`;
- `_legado/app/api/routes.py`;
- `_legado/app/models/models.py`;
- `_legado/app/templates/dpp_consumer.html`;
- `_legado/app/templates/etiqueta.html`.

Decisao operacional recebida em 2026-06-25:

1. promover `_legado/app` para `app/` por copia, nao por move;
2. tratar `_legado/` como referencia historica;
3. nao migrar `_legado/app/revenda/` para o backend DPP V1.

## 2. Execucao imediata ja concluida neste ciclo

- PRD v0 criado em `produto/decisoes/prd-dpp-integrado-v0.md`.
- Contrato de dados criado em `produto/decisoes/dpp-data-contract-v0.md`.
- QA anti-greenwashing criado em `produto/decisoes/dpp-anti-greenwashing-qa-v0.md`.
- Este backlog criou a ponte entre PRD e implementacao.
- Backend funcional promovido de `_legado/app` para `app/`, sem migrar `revenda`.
- Modelos, schemas e migracao simples receberam campos DPP: area, perda, lote, versao, datas, gramatura, fatores, indicadores calculados e status de evidencia.
- `app/services/dpp_calculator.py` criado com formula deterministica para area total, area perdida, peso, agua, energia e carbono.
- `app/validators/dpp_validators.py` criado com validacao de composicao 100%, evidencias minimas, GTIN/ficha obrigatorios e alertas de certificacao.
- `app/api/routes.py` atualizado para publicar DPP somente apos calculo e gate anti-greenwashing.
- `app/templates/dpp_consumer.html` atualizado para exibir badges de evidencia nos indicadores publicos e remover comparacoes ambientais nao auditadas.
- Testes unitarios criados em `tests/test_dpp_calculator.py` e `tests/test_dpp_validators.py`.
- Estrategia operacional de piloto criada em `produto/decisoes/phyllos-dpp-v1-estrategia-piloto.md`.

## 3. Proxima execucao no Codex

### C8 - Ledger de publicação do Evidence OS

Status: concluído localmente em 2026-07-21; commit, push e deploy pendentes.

- Cada execução do gate gera um registro append-only em `dpp_publication_records`.
- Tentativas aprovadas preservam snapshot canônico, status de evidência, versão do gate e SHA-256.
- Tentativas bloqueadas preservam erros, alertas e status de evidência sem gerar UUID público.
- `GET /pecas/{codigo}/dpp/publicacoes` expõe o histórico para operação e auditoria.
- O endpoint não oferece alteração ou exclusão dos registros.
- Suite local: 43 testes passando no ambiente Python do projeto.

Limites do ciclo:

- o controle é append-only na aplicação, mas ainda não possui proteção contra alteração direta no banco;
- identidade do publicador, segregação de aprovação e retenção formal dependem de autenticação e desenho posterior;
- validação independente do controle permanece pendente conforme o modelo de três linhas.

### C9 - Telemetria transversal da interface

Status: concluído localmente em 2026-07-21; revisão de privacidade, commit, push e deploy pendentes.

- Contrato versionado `usage-event-v1` e endpoint `POST /events/usage`.
- Captura transversal de page view, clique, submit, mudança de campo, erro de API/JavaScript, conclusão de publicação e fim de visibilidade.
- Instrumentação aplicada ao DPP Studio, Ateliê, passaporte público e etiqueta.
- Conteúdo digitado, valores de campos, query strings, texto visível e stack traces não são coletados.
- Sessão pseudônima em `sessionStorage`; eventos deduplicados por `event_id`.
- Política e taxonomia documentadas em `evidence-os-usage-events-v1.md`.

### C0 - Pendencias antes de push/deploy

- Concluido: `phyllos/dpp-studio.html` foi substituido pela versao canonica fornecida pelo founder em `/Users/paulonascimento/Downloads/dpp-studio.html`.
- Hash canonico validado local/GitHub: `560add24d6e31860fee858805644270b31e030b0a5d0d5ab273d21d52194b8c2`.
- Decisao registrada em `produto/decisoes/dpp-studio-versao-canonica-2026-06-25.md`.
- Pendente: publicar na Netlify como ultima versao quando houver permissao/liberacao; nao declarar Netlify atualizado antes de validar a URL final.
- Instalar dependencias Python de `requirements.txt` ou rodar em ambiente que ja tenha FastAPI/Jinja para validar render do template.
- Decidir se os arquivos novos em `app/` e `tests/` serao commitados neste branch.
- Se aprovado, commitar e subir as alteracoes.

### C7 - Preparacao do piloto assistido

Status: preparacao tecnica concluida localmente em 2026-06-27; deploy publico pendente de autenticacao GitHub/Railway.

Gate executado antes de nova implementacao:

- app local iniciou com Uvicorn e `GET /api/status` retornou `200`;
- publicacao Tier 1 sem GTIN foi criada por API e `GET /p/{uuid}` retornou HTML `200`;
- QR do mesmo UUID retornou PNG `200`;
- registro temporario do smoke test foi removido apos a validacao;
- suite completa: 42 testes passando;
- Railway respondeu `200` em `/api/status`, mas ainda servia uma versao anterior sem UUID automatico; commit local C7 `adca97b` aguarda push/deploy.

- Usar `produto/decisoes/phyllos-dpp-v1-estrategia-piloto.md` como roteiro do piloto.
- Usar Railway como ambiente publico inicial, com `DPP_BASE_URL=https://phyllos-production.up.railway.app`.
- Validar `GET /p/{uuid}` antes de orientar uso fisico do QR.
- Usar SKU/codigo PHYLLOS como identificador operacional, com GTIN opcional.
- Permitir publicacao Tier 1 sem indicadores de agua/energia/carbono; Tier 2 entra quando area, gramatura, perda e fatores estiverem disponiveis.
- Registrar tempo de onboarding, Tier alcancado, campos ausentes, link publico, QR compartilhado e objecao principal em `outputs/piloto-dpp-v1.csv`.
- Separar 5 marcas independentes com 1 a 3 pecas prontas ou quase prontas.
- Executar o piloto como servico assistido gratuito para 3 a 5 usuarios.
- Manter QR ativo por 90 dias mesmo se a marca nao virar cliente.
- Converter lacunas recorrentes em backlog tecnico ou decisao de oferta concierge.

Artefatos preparados:

- `scripts/dpp_pilot_preflight.py`: valida healthcheck, pagina publica e QR antes de liberar impressao/uso fisico;
- `outputs/piloto-dpp-v1.csv`: schema alinhado ao roteiro, incluindo `qr_ativo_ate` para controlar os 90 dias;
- `outputs/piloto-dpp-v1-candidatos.csv`: cinco slots de recrutamento sem inventar nomes de marcas;
- `tests/test_dpp_public_route.py`: cobre pagina publica Tier 1 sem GTIN e UUID inexistente;
- suporte a `DATABASE_URL` em `app/core/database.py`, mantendo SQLite como fallback local.

Pendencias externas/operacionais:

- autenticar o push de `adca97b` para `origin/main` e aguardar o deploy Railway;
- criar um DPP tecnico no ambiente publicado e executar o preflight contra a URL real;
- preencher os cinco slots com marcas reais, enviar as abordagens e agendar 3 a 5 onboardings;
- registrar resultados reais no CSV e converter lacunas recorrentes em backlog/oferta concierge.

### C1 - Backend promovido para `app/`

Status: concluido localmente.

- Copiar `_legado/app` para `app/`.
- Excluir `revenda` da migracao.
- Preservar templates, rotas, modelos, schemas e servicos necessarios ao DPP.

### C2 - Campos novos em `Peca` e `FichaTecnica`

Status: concluido localmente.

- `Peca`: `area_peca_m2`, `perda_corte_pct`, `lote_quantidade`, `dpp_version`, `data_publicacao`, `data_atualizacao`.
- `FichaTecnica`: `gramatura_g_m2`, fatores de agua/energia/carbono, resultados calculados e `evidencia_statuses`.

### C3 - Calculo deterministico

Status: concluido localmente.

- modulo: `app/services/dpp_calculator.py`.
- teste: `tests/test_dpp_calculator.py`.

### C4 - Validadores anti-greenwashing

Status: concluido localmente.

- modulo: `app/validators/dpp_validators.py`.
- teste: `tests/test_dpp_validators.py`.

### C5 - Endpoint de publicacao DPP

Status: concluido localmente.

- rota: `POST /pecas/{codigo}/dpp/publicar`.
- retorna `422` com erros, alertas e status de evidencia se faltar dado minimo.
- salva resultados calculados antes da publicacao quando o gate passa.

### C6 - Badges no passaporte publico

Status: concluido localmente em `app/templates/dpp_consumer.html`.

- Indicadores publicos exibem badge de evidencia.
- Texto comparativo nao auditado foi removido.
- Carbono, agua, energia e perda de corte aparecem como estimativas calculadas quando disponiveis.

## 4. Verificacao executada

- `python3 -m compileall app tests` com `PYTHONPYCACHEPREFIX=/private/tmp/codex_pycache`: passou.
- `python3 -m unittest discover -s tests`: 4 testes passaram.
- Varredura por textos antigos de promessa ambiental no template publico: sem ocorrencias.
- Validacao Jinja isolada nao executada porque os runtimes locais nao tinham `jinja2` instalado, embora `requirements.txt` declare `jinja2==3.1.5`.

## 5. Fora do ciclo Codex atual

- Parsers DXF/AAMA/ASTM/PDF.
- ISCM publico como score verde.
- Integracoes externas.
- Auth, multi-tenant e faturamento.
- Revenda.
- Pattern Engine e edicao de molde.
