# PHYLLOS — Plataforma de Passaporte Digital para Moda

**PHYLLOS** é uma plataforma SaaS B2B que permite qualquer marca de moda publicar o passaporte digital (DPP) de suas peças — validando compliance regulatório e conectando com buyers internacionais que exigem DPP como critério de compra.

> Dados entram. Passaporte sai.

---

## O que o produto entrega

- Passaporte digital por SKU com URL pública e QR code
- Status de evidência por campo: `declarado / calculado / documentado / verificado / ausente`
- Validação INMETRO Portaria 459/2025 (calçados, prazo 31/07/2026)
- Validação EU ESPR (~2028, vestuário exportador)
- Página legível por buyer sem necessidade de login

## O que o produto não é

Não é CAD, PLM, ERP, ferramenta de modelagem, ACV oficial ou auditoria ambiental.

---

## Stack técnico

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + Python (`app/`) |
| ORM | SQLAlchemy |
| DB dev | SQLite |
| DB produção | Supabase (PostgreSQL) |
| Deploy backend | Render (`render.yaml`) |
| Deploy frontend | Netlify (`phyllos/`) |
| Edge/CDN | Cloudflare (obrigatório) |
| QR | GS1 Digital Link + qrcode[pil] |

```bash
# Rodar local
uvicorn app.main:app --reload

# Testes
python -m unittest discover -s tests
```

---

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| `app/` | Backend FastAPI — modelos, rotas, calculadora DPP, validadores |
| `phyllos/` | Frontend Netlify — DPP Studio, site institucional, páginas de estratégia |
| `roadmap/` | Cronograma executivo com fases, responsáveis e critérios de aceite |
| `produto/decisoes/` | PRD, backlog, contrato de dados, QA anti-greenwashing, piloto |
| `.claude/agents/` | Time de agentes Claude — 40 agentes com missão, KPIs e alocação por fase |
| `.claude/agents/references/` | Premissas estratégicas, posicionamento e blocos evolutivos de produto |
| `tests/` | Testes unitários dos cálculos e validadores |
| `_legado/` | Código histórico preservado — não usar em produção |

---

## Bloco atual: B0 → B1 (Jun–Ago/2026)

**B0 — Fundação:** infra de produção no ar, schema aprovado, 5 marcas piloto confirmadas
**B1 — Passaporte Mínimo:** marca publica, buyer lê, QR funciona

Para instruções completas de desenvolvimento, leia **[CLAUDE.md](CLAUDE.md)**.
Para o cronograma completo, leia **[roadmap/roadmap-dpp-integrado-phyllos.md](roadmap/roadmap-dpp-integrado-phyllos.md)**.
Para a alocação de agentes por fase, leia **[.claude/agents/references/product-blocks-allocation.md](.claude/agents/references/product-blocks-allocation.md)**.

---

## Regulação vigente

| Regulação | Escopo | Prazo |
|---|---|---|
| INMETRO Portaria 459/2025 | Calçados — fabricantes e importadores | 31/07/2026 |
| INMETRO Portaria 459/2025 | Calçados — varejo | 31/12/2027 |
| EU ESPR (Reg. UE 2024/1781) | Têxtil — qualquer produto vendido na Europa | ~2028 |
| EU AI Act Art. 50 | Interfaces de IA devem declarar proveniência | 02/08/2026 |
