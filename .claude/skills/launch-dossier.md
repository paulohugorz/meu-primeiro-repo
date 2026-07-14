# Skill: Launch Dossier

Use esta skill para verificar se uma funcionalidade, piloto, passaporte digital, fluxo de onboarding, comunicação comercial ou publicação pública da PHYLLOS está pronta para uso externo. É o gate final antes de go-live, envio a cliente, demo comercial ou publicação.

**Quem usa:** execution-orchestrator, tech-lead-fullstack-data, regulatory-specialist, sales-partnerships-lead, implementation-cs-lead, devops-security-agent, finance-administration

---

## Checklist de aprovação - 6 gates

### Gate 1 - Direção humana e escopo
- [ ] Problema, objetivo, usuário/cliente e resultado esperado foram aprovados pelo founder humano.
- [ ] Produto, dados estratégicos e design foram validados pelo founder humano quando aplicável.
- [ ] Escopo e fora de escopo estão registrados.
- [ ] Critérios de aceite e decisão de go/no-go estão claros.

### Gate 2 - Evidência e regulação
- [ ] Claims passaram por `claim-validation`.
- [ ] Claims ambientais passaram por `anti-greenwashing-check`.
- [ ] Critérios de evidência foram revisados por `regulatory-specialist`.
- [ ] Fontes, vigência, jurisdição, limitações e incertezas estão documentadas.
- [ ] Nenhuma promessa de conformidade jurídica definitiva foi feita.

### Gate 3 - Dados e cálculo
- [ ] Campos, schemas, fórmulas, unidades e versões estão documentados.
- [ ] Origem, linhagem e qualidade dos dados foram verificadas.
- [ ] Alterações que afetam histórico estão registradas.
- [ ] Resultados podem ser reproduzidos.

### Gate 4 - Produto e experiência
- [ ] Fluxo aprovado pelo founder/product design humano foi implementado sem omitir informação obrigatória.
- [ ] Estados de erro, vazio, loading, permissão, evidência e publicação estão cobertos.
- [ ] Acessibilidade e responsividade foram verificadas quando houver interface.
- [ ] Linguagem pública diferencia fato, hipótese, estimativa e recomendação.

### Gate 5 - Tecnologia e segurança
- [ ] Frontend, backend, dados e integrações estão testados contra contrato versionado.
- [ ] Logs, alertas, rollback e backup foram considerados.
- [ ] Segredos, permissões e dados sensíveis não foram expostos.
- [ ] Deploy ou uso externo tem aprovação humana quando for ação crítica.

### Gate 6 - Comercial, implementação e finanças
- [ ] Sales recebeu limites claros de promessa, preço, prazo e escopo.
- [ ] Implementation/CS recebeu handoff com critérios de sucesso, dados, riscos e pendências.
- [ ] Finance recebeu impacto em custo, receita, cobrança, runway ou orçamento quando aplicável.
- [ ] Status separa feito localmente, integrado, testado, documentado, commitado, pushado, publicado e verificado ao vivo.

## Formato de saída

```text
Iniciativa:
Data de avaliação:

Status geral: APROVADO / BLOQUEADO / APROVADO COM RESSALVAS

Gates aprovados:
Gates bloqueados:
Evidências verificadas:
Riscos:
Decisão recomendada:
Aprovação humana necessária:
```

## Regra final

Uma iniciativa bloqueada em qualquer gate crítico não deve ir para cliente, buyer, público ou produção. O custo de publicar evidência frágil, claim exagerado, dado sem origem ou promessa comercial não autorizada é maior do que o custo de atrasar.
