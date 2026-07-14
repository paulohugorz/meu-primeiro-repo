# Skill: Anti-Greenwashing Check

Use esta skill para revisar qualquer afirmação ambiental, social, regulatória ou de sustentabilidade antes de publicação, proposta, passaporte digital, demo, página pública ou comunicação com cliente.

**Quem usa:** regulatory-specialist, regulatory-analyst, sales-partnerships-lead, account-executive-partnerships, implementation-cs-lead, frontend-integrations-engineer

---

## Verificações obrigatórias

1. A afirmação possui documentação vigente, verificável e autorizada para uso?
2. A certificação citada tem número, emissor, escopo e data de validade?
3. O claim é específico, com dado, percentual, metodologia ou fonte, ou é genérico?
4. O texto promete mais do que a evidência comprova?
5. Há linguagem vaga como "eco", "verde", "consciente", "responsável", "sustentável" ou "baixo impacto" sem prova?
6. A limitação do produto, processo, cálculo ou fonte foi comunicada com honestidade?
7. A rastreabilidade é documentada por etapa, e não apenas declarada?
8. A fronteira do claim está clara: peça, lote, coleção, fornecedor, processo, empresa ou cadeia?
9. O status da informação está claro: confirmado, declarado pelo cliente, estimado, interpretado ou recomendado?

## Sinais de alerta imediato

- "Sustentável" sem critério e evidência.
- "Eco", "verde" ou "consciente" sem dado verificável.
- Percentual sem fonte, metodologia, lote ou escopo.
- Certificação expirada, genérica ou fora do escopo do claim.
- Carbono, água, circularidade ou impacto social sem metodologia declarada.
- Rastreabilidade apresentada como auditoria quando é apenas declaração.
- Promessa de conformidade quando há apenas interpretação preliminar.

## Formato de saída

```text
Status: aprovado / aprovado com ressalvas / reprovado

Claims problemáticos:
- [claim] -> problema: [descrição] -> evidência necessária: [documento/dado/fonte]

Versão segura da redação:
[texto revisado sem o claim problemático ou com a qualificação correta]

Escalonamento:
[regulatory-specialist / founder humano / outro agente]
```

## Regra final

Na dúvida entre publicar e esperar evidência, a PHYLLOS espera. Greenwashing detectado após publicação tem custo de reputação, comercial e regulatório desproporcional.
