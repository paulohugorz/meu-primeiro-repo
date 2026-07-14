# PHYLLOS — Premissas Estratégicas Vigentes

**Data:** 2026-06-26
**Status:** fonte canônica para todos os agentes PHYLLOS
**Substitui:** premissas anteriores centradas em marca de vestuário

---

## 1. Decisão central

A PHYLLOS é uma **plataforma SaaS B2B** que permite qualquer marca de moda publicar o passaporte digital de suas peças.

O produto entrega dois valores indissociáveis:

1. **Compliance** — valida que a marca cumpre a regulação vigente (INMETRO 31/07/2026; EU ESPR ~2028)
2. **Acesso a buyers** — o passaporte publicado é a credencial que buyers internacionais exigem para fechar pedidos

## 2. Produto em uma frase

PHYLLOS transforma os dados técnicos que a marca já tem no passaporte digital que regulação exige e buyers aceitam.

## 3. Categoria

**Infraestrutura de compliance para moda.**

Não é auditoria. Não é consultoria. É software que organiza, valida e publica — sem prometer mais do que está documentado.

## 4. Quem usa

Marcas de moda independentes, ateliês, pequenas e médias que precisam:
- Documentar suas peças para regulação nacional (INMETRO) ou europeia (EU ESPR)
- Responder a buyers internacionais que exigem DPP como critério de compra
- Sair da ficha técnica em Excel e ter um passaporte público por SKU

## 5. O que o produto entrega

- Passaporte digital por SKU com URL pública
- QR code para etiqueta física
- Status de evidência por campo: declarado, calculado, documentado, verificado, ausente
- Validação contra critérios INMETRO e EU ESPR
- Página legível por buyer sem necessidade de login

## 6. O que o produto não faz

- Não emite certificações (GOTS, OEKO-TEX, etc.) — referencia as existentes
- Não audita fornecedores
- Não promete compliance que os dados não sustentam
- Não cria fichas técnicas — recebe o que a marca já tem
- Não é ferramenta de modelagem, encaixe ou CAD

## 7. Princípio anti-greenwashing

Nenhum indicador aparece como verdade absoluta se for estimado ou declarado.

Todo campo público carrega status de evidência visível:
- **declarado** — fornecedor informou, sem documento
- **calculado** — derivado de área, gramatura e fatores
- **documentado** — existe arquivo de apoio
- **verificado** — certificado ou laudo independente
- **ausente** — dado não disponível

## 8. Modelo de negócio

| Fase | Produto | Preço |
|---|---|---|
| Piloto (ago/2026) | Passaporte assistido | Gratuito |
| Fase 1 (out/2026) | Por passaporte | R$149–299 / DPP |
| Fase 2 | Assinatura | R$490/mês / marca |
| Fase 3 | API / Plataforma B2B | USD 20–200K / contrato |

## 9. Premissas financeiras

- Investimento até 1º cliente: **R$6.500** (revisado: inclui infra de produção)
- Infra piloto (ago–out/2026): **R$280/mês** — Supabase Pro + Railway Starter + Netlify + Cloudflare Free
- Infra Fase 1 (out/2026–mar/2027): **R$480/mês** — Railway Pro + Supabase Pro + Netlify Pro + Cloudflare Pro
- Infra Fase 2 (escala 200+ marcas): **R$1.100/mês** — Fly.io multi-region + Supabase Pro + Cloudflare Pro + Sentry
- Breakeven operacional: **Mar/2027** (mantido — impacto de R$2K no runway, absorvido)
- Valuation base (pós 1º cliente): R$5M
- Política: zero captação antes de breakeven (exceto B2B urgente)

**Racional da revisão de infra:** o DPP é acessado por buyers internacionais em momentos de negociação — indisponibilidade ou latência destroem a credencial. Supabase Free pausa banco com inatividade (bloqueante para produção). Cloudflare como edge CDN resolve performance global a custo zero. Supabase Pro é inegociável para o primeiro cliente real.

## 9b. Requisitos de infraestrutura (não-negociáveis para produção)

| Requisito | Por quê | Como resolver | Custo |
|---|---|---|---|
| **Edge CDN global** | Buyer em EU/US acessando DPP com latência > 500ms = credencial fraca | Cloudflare Free à frente de Railway + Netlify | R$0 |
| **DB sempre ligado / PITR** | Supabase Free pausa banco — QR que retorna 503 destrói a promessa | Supabase Pro | $25/mês |
| **SLA de backend** | Railway Starter sem SLA = risco de indisponibilidade em negociação crítica | Railway Pro ou Fly.io | $20–40/mês |
| **WAF + DDoS básico** | DPP público = surface de ataque; WAF protege sem custo no Cloudflare Free | Cloudflare Free WAF | R$0 |
| **Backup e audit log** | Passaporte é documento com valor legal/regulatório — precisa de imutabilidade e histórico | Supabase PITR + Row-level audit via triggers | incluso no Pro |
| **Data residency (futuro)** | EU ESPR pode exigir dados de marcas europeias em servidores UE | Planejar migração Supabase para região EU antes de Fase 2 | avaliar em 2027 |

**Critério de saída de cada ferramenta:**
- Railway → Fly.io quando precisar de multi-region ou Railway Pro ficar acima de $40/mês
- Netlify → Vercel quando DPP Studio tiver mais de 10K deploys/mês ou precisar de Edge Functions
- Supabase → avaliar self-hosted apenas acima de 500 marcas ativas

## 10. Handoffs esperados por departamento e agente

- **Founder humano:** direção, prioridades, investimento e go/no-go
- **Founder humano / Product & Data:** problema, funcionalidades, prioridade, métricas, roadmap e critérios de aceite
- **Founder humano / Product Design:** jornada, UI, UX, acessibilidade e design QA
- **Execution Orchestrator:** decomposição, owners, dependências, acompanhamento e escalonamento
- **Tech Lead Full-stack & Data:** arquitetura, APIs, segurança, qualidade, dados e release
- **Backend & Data Engineer:** contrato e schema DPP, dicionário, eventos, cálculos, validações e trilha de auditoria
- **Frontend & Integrations Engineer:** interface, portais públicos, importadores, integrações e estados de evidência
- **DevOps & Security Agent:** ambientes, deploy controlado, observabilidade, backups, permissões e incidentes
- **Regulatory Specialist + Regulatory Analyst:** mapeamento de requisitos INMETRO e EU ESPR por campo, fontes e critérios de evidência
- **Sales & Partnerships:** recrutamento, demanda, pipeline, parcerias, objeções e posicionamento B2B
- **Implementation & Customer Success:** onboarding, adoção, suporte, health score e feedback operacional
- **Finance & Administration:** realizado, comprometido, forecast, premissas, runway e unit economics

## 11. Regulação vigente

- **INMETRO Portaria 459/2025 — calçados:** prazo fabricantes/importadores 31/07/2026 · varejo 31/12/2027 · campos: GTIN, composição por parte, país de fabricação, CNPJ, QR rastreável · multa até R$1,5M. Para vestuário: regulação equivalente ainda não publicada.
- **EU ESPR (~2028):** DPP têxtil completo obrigatório para vender na Europa
- **EU AI Act Art. 50 (02/08/2026):** interfaces de IA devem declarar proveniência de outputs

## 12. Mecanismo de adoção antecipada

Marcas adotam o DPP antes da obrigatoriedade quando percebem que ele gera resultado comercial — não quando temem a penalidade regulatória.

**O passaporte funciona como credencial de acesso a um novo estágio de negociação.** A marca que chega com DPP publicado não está respondendo a um questionário de buyer — está iniciando a conversa com um nível diferente de credibilidade. Isso muda a posição da marca na mesa, não só o compliance.

**Implicação para produto:** o DPP precisa ser percebido como ativo comercial, não como custo de conformidade. A página pública do passaporte deve ser apresentável como material de negociação — não apenas como documento técnico.

**Implicação para vendas:** o argumento de entrada não é "evite a multa" nem "cumpra a lei". É "use o passaporte para abrir uma negociação que você não conseguia ter antes."

**Implicação para o piloto:** o critério de sucesso não é "passaporte publicado". É "passaporte usado em uma conversa com buyer" — a marca enviou o link, o buyer leu, a negociação avançou.
