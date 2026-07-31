# Execution Brief — DPP Assistido / Intake v1

**Decision ID:** `DPP-ASSISTIDO-INTAKE-2026-07-31`
**Bloco:** B0 → B1
**Direcionamento:** implementar primeiro o schema e a validação de intake descritos
na especificação do serviço DPP Assistido.

## Resultado e escopo

- Entrega: contrato Pydantic com 49 pontos operacionais, função determinística e
  `POST /intake/validate` com erro específico por campo/ponto.
- Não escopo: persistência, painel, publicação, PDF, deploy e declaração jurídica
  de conformidade.
- Owner de implementação/operação: Engineering/Data (primeira linha).
- Revisão regulatória requerida: Certification/Compliance (segunda linha).
- Teste independente de eficácia antes do go-live: QA/Internal Audit, sem ser o
  executor do controle.

## Obrigação, risco e controle

- Obrigação em análise: ESPR (UE) 2024/1781 e futuros requisitos setoriais para
  têxteis; requisitos brasileiros devem ser validados separadamente por categoria.
- Risco: tratar uma lista interna como obrigação legal definitiva ou aceitar dados
  incompletos sem diagnóstico acionável.
- Controle preventivo: perfil explicitamente `provisional`, 49 campos obrigatórios,
  erros ligados a identificador estável e bloqueio por HTTP 422.
- Evidência: código versionado, testes automatizados e metadados de fonte/escopo/
  limitação em toda resposta.
- Retenção: a definir pelo owner de Evidence & Records antes de persistir payloads;
  este endpoint não persiste conteúdo.

## Dependências, aceite e decisões

1. Engineering/Data implementa contrato e endpoint.
2. QA valida os critérios: 49 mapeamentos, erros específicos, soma de composição e
   sucesso do payload completo.
3. Certification substitui ou aprova o catálogo provisório quando o ato setorial e
   fontes oficiais aplicáveis forem consolidados.
4. Founder decide go-live somente após revisão independente e política de retenção.

**Critério de aceite local:** payload incompleto recebe 422 e lista cada campo com
seu ponto; payload completo recebe 200; suíte existente continua passando.
