# PHYLLOS — Auditoria de completude do catálogo ambiental v1.1

## Status da entrega

**Aprovada como auditoria e base para revisão/coleta.** Ainda não está pronta para cálculo oficial, publicação de impacto ou alegações ambientais.

## Resultado preservado

- 70 amostras auditadas;
- 17 com alguma menção de composição;
- 7 com composição percentual extraída e soma válida;
- 14 com gramatura explícita;
- 7 com composição percentual extraída + gramatura;
- 63 classificadas como `not_calculable`;
- 0 Evidence validada;
- 0 EPD ou ACV específica vinculada;
- 0 fator ambiental associado;
- completude média de 36,9/100.

## Correção de interpretação dos sete casos

Os sete registros antes descritos como “estimativa material possível” são agora tratados como **candidatos provisórios** a `material_estimate_only`.

Todos possuem:

- `composition_extraction_status = percentual extraído — revisão pendente`;
- `calculability_review_status = pending_human_review`;
- `review_required = Sim`;
- nenhuma Evidence validada.

Portanto, eles não autorizam:

- cálculo oficial;
- resultado ambiental publicável;
- alegação de pegada;
- comparação de sustentabilidade;
- promoção para `secondary_estimate` ou nível superior.

## Correções de schema incorporadas

1. Nomes alinhados ao dicionário:
   - `fiber_percentage`;
   - `factor_value`;
   - `factor_unit`;
   - `calculation_status`.
2. `article_id` passou a ser obrigatório.
3. `verified_environmental_profile` exige ao menos uma Evidence com:
   - `authenticity = verified`;
   - `relevance = sufficient`.
4. `supplier_specific_estimate` exige Evidence primária, laboratorial ou de certificação.
5. `calculability_review_status` tornou-se obrigatório.
6. Cálculos são bloqueados enquanto a revisão estiver pendente, rejeitada ou não aplicável.
7. Referências internas são verificadas pelo validador semântico executável.

## Decisão

A implementação de entidades persistentes pode usar o schema v0.3 como base técnica, mas o motor de cálculo e qualquer comunicação ambiental permanecem bloqueados até:

- revisão humana das extrações;
- recebimento e validação dos documentos;
- criação e aprovação do catálogo de fatores;
- definição da metodologia e fronteiras;
- testes de cálculo e reprodução;
- aprovação conjunta por Arquitetura, Especialista Têxtil, ACV e Evidências.

---

## Nota de distribuição v0.3

A dependência `jsonschema` passou a ser declarada em `requirements.txt`, e a suíte foi ampliada para os cenários de integridade referencial, duplicidade, perfis específicos/verificados e todos os estados de revisão de calculabilidade. A conclusão metodológica permanece inalterada: os sete casos são provisórios e não autorizam cálculo oficial ou alegações ambientais.
