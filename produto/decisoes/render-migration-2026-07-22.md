# Migração do Evidence OS para Render — 2026-07-22

## Decisão e escopo

Preparar e validar o backend do Evidence OS no Render, mantendo o Railway como
rollback até que o novo serviço passe nos testes de saúde, autenticação e
persistência. O Render passa a ser um novo fornecedor de infraestrutura e
subprocessador técnico; a aceitação comercial do plano pago continua sendo uma
decisão do founder.

## Arquitetura de validação

- web service Docker conectado ao branch principal;
- health check em `/api/status`;
- PostgreSQL gerenciado injetado por `DATABASE_URL`;
- dashboard em `/telemetry/dashboard` protegido por Basic Auth;
- segredos configurados no Render, nunca versionados;
- Railway preservado, sem alteração de DNS ou desligamento, durante o aceite.

O `render.yaml` usa instâncias gratuitas somente para validar o deploy sem
incorrer custo. Essa configuração não é uma solução de produção: o web service
pode hibernar e o PostgreSQL gratuito expira após 30 dias. O corte definitivo
exige aprovar e aplicar planos pagos antes de coletar telemetria real.

## Dados, controles e evidências

| Item | Definição |
|---|---|
| Dados tratados | dados operacionais do Evidence OS e eventos agregáveis de uso |
| Dados proibidos nos eventos | conteúdo livre, documentos, e-mail, nome e identificadores pessoais diretos |
| Controle preventivo | minimização no contrato de telemetria e segredos fora do Git |
| Controle detectivo | health check, testes do dashboard e revisão periódica dos campos coletados |
| Owner operacional | Engenharia / DevOps PHYLLOS |
| Owner de privacidade | privacy-data-protection-agent, com decisão final do founder |
| Retenção | permanece pendente de decisão formal; não presumir retenção ilimitada |
| Evidência esperada | commit, deploy Render, URL validada e registro do teste de persistência |

## Risco de terceiro e limitações

- fornecedor novo: Render Services, Inc.; termos, DPA, região e subprocessadores
  devem ser confirmados antes do go-live com dados reais;
- instâncias gratuitas não atendem continuidade ou retenção de produção;
- a aplicação cria o esquema inicial via SQLAlchemy, mas ainda não possui uma
  ferramenta formal de migração de schema para PostgreSQL;
- não há migração automática de dados do SQLite/Railway neste change. Antes do
  cutover, comparar contagens, integridade e período de indisponibilidade;
- rollback: manter o Railway operante e reverter `DPP_BASE_URL`/integrações para
  a URL anterior se os critérios falharem.

## Critérios de aceite para o cutover

1. plano persistente aprovado e ativado no web service e no PostgreSQL;
2. `/api/status` responde com sucesso na URL `onrender.com`;
3. dashboard exige credenciais e abre com credenciais válidas;
4. evento sintético permanece disponível após novo deploy;
5. amostra de dados migrados confere em quantidade e conteúdo permitido;
6. DPA, região, subprocessadores, retenção e owner registrados;
7. Railway só é desativado após janela de rollback aprovada pelo founder.

## Fontes

- Render, “Deploying on Render”: https://render.com/docs/deploys
- Render, “Deploy for Free”: https://render.com/docs/free
- Render, “Persistent Disks”: https://render.com/docs/disks
- Render, “Blueprint YAML Reference”: https://render.com/docs/blueprint-spec

Fontes consultadas em 2026-07-22. Preços e condições comerciais devem ser
revalidados no momento da contratação.
