# Skill: Claim Validation

Use esta skill para validar qualquer claim técnico, ambiental, regulatório, comercial ou operacional antes de aparecer em passaporte digital, proposta, demo, site, ficha pública, apresentação, onboarding ou comunicação com cliente.

**Quem usa:** regulatory-specialist, regulatory-analyst, sales-partnerships-lead, account-executive-partnerships, implementation-cs-lead, frontend-integrations-engineer

---

## Tipos de claims cobertos

- Rastreabilidade: origem, etapa produtiva, fornecedor, evidência documental.
- Composição e material: fibra, insumo, certificado, lote, unidade e validade.
- Impacto ou sustentabilidade: percentual, metodologia, fronteira, limitação e fonte.
- Conformidade: obrigação, jurisdição, vigência, aplicabilidade e incerteza.
- Processo: coleta, validação, auditoria, trilha de evidência e revisão.
- Produto digital: funcionalidade disponível, integração, SLA, automação e segurança.
- Resultado comercial: prazo, economia, redução de risco, melhoria operacional e ROI.

## Regra inegociável

Nenhum claim pode ser aprovado sem:

1. **Fonte:** quem afirma ou comprova isso?
2. **Documento ou dado:** laudo, certificado, registro, fonte oficial, contrato, log ou base validada?
3. **Responsável técnico:** qual agente revisou e responde pela evidência?
4. **Versão e validade:** a fonte está vigente e a versão foi registrada?
5. **Limitação conhecida:** o que o claim não cobre?
6. **Status:** fato confirmado, informação fornecida pelo usuário, interpretação, estimativa, hipótese ou recomendação?

## Formato de saída

| Claim | Evidência existente | Status | Risco se publicado sem evidência | Redação segura |
|---|---|---|---|---|
| [claim] | [documento/dado/fonte] | aprovado / pendente / reprovado | alto / médio / baixo | [versão segura] |

## Escalonamento

- Claim pendente de fonte primária ou documento -> bloquear publicação e acionar `regulatory-analyst` ou `implementation-cs-analyst`.
- Claim com interpretação regulatória -> acionar `regulatory-specialist`.
- Claim dependente de cálculo, dado ou integração -> acionar `backend-data-engineer` e `tech-lead-fullstack-data`.
- Claim comercial com preço, prazo, ROI ou customização -> acionar `sales-partnerships-lead` e founder humano.
- Claim reprovado -> remover da comunicação e registrar risco no handoff.
