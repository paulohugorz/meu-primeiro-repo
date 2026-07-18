# PHYLLOS — Instruções para Agentes de Código

## O que é a PHYLLOS

Plataforma SaaS B2B que permite qualquer marca de moda publicar o passaporte digital (DPP) de suas peças.

Dois valores entregues:
1. **Compliance** — valida que a marca cumpre INMETRO Portaria 459/2025 (calçados, prazo 31/07/2026) e EU ESPR (~2028)
2. **Credencial comercial** — o passaporte publicado é o que buyers internacionais exigem para fechar pedidos

O produto não é uma ferramenta de moda. É infraestrutura de dados com QR público por SKU.

---

## Bloco atual: B0 → B1

**Estamos em B0/B1 (Jun–Ago/2026).**

Contexto completo dos blocos evolutivos: `.claude/agents/references/product-blocks-allocation.md`

### O que precisa existir ao final de B1
- Backend FastAPI funcional: CRUD produto/material/DPP, cálculo determinístico, endpoint QR, rota pública
- Passaporte público por SKU com URL permanente (sem login para buyer)
- QR GS1 Digital Link funcional
- Status de evidência visível em cada campo (declarado/calculado/documentado/verificado/ausente)
- Validação INMETRO Tier 1: composição por parte, GTIN, CNPJ, país de fabricação
- Deploy no Railway com Cloudflare na frente

---

## Stack

| Camada | Tecnologia | Localização |
|---|---|---|
| Backend | FastAPI + Python | `app/main.py` |
| ORM | SQLAlchemy | `app/models/` |
| DB dev | SQLite | local |
| DB produção | Supabase (PostgreSQL) | variável `DATABASE_URL` |
| Templates | Jinja2 | `app/templates/` |
| QR | qrcode[pil] + GS1 Digital Link | `app/services/` |
| Deploy backend | Railway | `railway.toml` |
| Deploy frontend | Netlify | `phyllos/` |
| Edge/CDN | Cloudflare | obrigatório na frente de todas as URLs DPP públicas |

### Comandos úteis
```bash
uvicorn app.main:app --reload           # servidor local
python -m unittest discover -s tests   # testes
python3 -m compileall app tests        # verificação de sintaxe
```

### Variáveis de ambiente necessárias
```
DATABASE_URL=         # Supabase PostgreSQL em produção; SQLite local para dev
DPP_BASE_URL=         # URL base para QR (ex: https://phyllos-production.up.railway.app)
SECRET_KEY=           # chave para JWT/auth futuro
```

---

## Estrutura do app

```
app/
├── main.py                  # entrypoint FastAPI
├── models/models.py         # SQLAlchemy: Colecao, Peca, FichaTecnica, DPP, EvidenceLedger
├── schemas/                 # Pydantic schemas
├── api/routes.py            # rotas REST
├── services/
│   └── dpp_calculator.py    # cálculo determinístico (área, peso, água, energia, carbono)
├── validators/
│   └── dpp_validators.py    # gate anti-greenwashing antes de publicar
└── templates/
    └── dpp_consumer.html    # página pública do passaporte (sem login)
```

---

## Regras inegociáveis

1. **Nenhum campo publicado sem status de evidência** — declarado/calculado/documentado/verificado/ausente
2. **Cálculos são determinísticos e testados** — nenhum número ambiental gerado por IA sem revisão humana
3. **QR só é gerado após gate anti-greenwashing passar** — `app/validators/dpp_validators.py`
4. **Supabase Free é proibido em produção** — pausa banco com inatividade; usar Pro
5. **Cloudflare é obrigatório na frente de URLs públicas** — DPP é acessado por buyers em negociação
6. **Toda feature declara qual bloco atende** — B0, B1, B2, B3 ou B4
7. **V1 não edita molde, não é CAD, não é PLM, não é ERP**

---

## Documentos de referência

| Documento | O que tem |
|---|---|
| `.claude/agents/references/dpp-integrado-strategic-premises.md` | premissas estratégicas, modelo de negócio, regulação |
| `.claude/agents/references/product-blocks-allocation.md` | blocos evolutivos, alocação de agentes, gates |
| `roadmap/roadmap-dpp-integrado-phyllos.md` | cronograma de fases com responsáveis e critérios de aceite |
| `produto/decisoes/prd-dpp-integrado-v0.md` | PRD com escopo, ICP, jornada e critérios de aceite do MVP |
| `produto/decisoes/dpp-data-contract-v0.md` | contrato de dados: schema, campos, tipos, restrições |
| `produto/decisoes/dpp-anti-greenwashing-qa-v0.md` | regras de QA anti-greenwashing |
| `produto/decisoes/backlog-codex-dpp-2026-06-25.md` | backlog técnico com status por ciclo |

---

## O que não fazer

- Não criar "score verde", "nota de sustentabilidade" ou índice composto público
- Não publicar campo estimado sem badge de evidência visível
- Não usar Supabase Free em produção
- Não fazer deploy no Netlify e declarar concluído sem validar a URL final
- Não implementar features de B2/B3/B4 antes do gate de B1 ser aprovado pelo CEO

## Compliance, auditoria e assurance

Toda mudança material deve consultar `AGENTS.md`.

### Gates obrigatórios

- IA, modelo, prompt, dataset ou automação:
  `ai-governance-model-risk-agent`.
- Dados pessoais:
  `privacy-data-protection-agent`.
- Fornecedor, subprocessador, API ou cloud:
  `third-party-risk-agent`.
- Método, fórmula, fonte ou evidência:
  `evidence-records-governance-agent`.
- Mudança regulatória geral:
  `regulatory-intelligence-agent`.
- Requisito regulatório por campo:
  `certification-agent`.
- Auditoria ou diligência:
  `audit-readiness-agent`.
- Teste independente:
  `internal-audit-assurance-agent`.
- Exceção material:
  `chief-compliance-risk-officer` e founder.

Quem implementa um controle não pode ser a única parte a validar sua eficácia.
