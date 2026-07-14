# DPP MVP — Especificação de Implementação

**Projeto:** Fashion OS v1 — PHYLLOS  
**Versão:** 1.0  
**Data:** 2026-06-23  
**Status:** referencia de implementacao legada — complementar ao PRD v0 de 2026-06-25
**Owner:** CPO  

> Atualizacao 2026-06-25: esta especificacao descreve a implementacao DPP existente no backend legado (`_legado/app`). Para a V1 vigente de DPP Integrado, usar como fontes principais:
>
> - [prd-dpp-integrado-v0.md](prd-dpp-integrado-v0.md)
> - [dpp-data-contract-v0.md](dpp-data-contract-v0.md)
> - [dpp-anti-greenwashing-qa-v0.md](dpp-anti-greenwashing-qa-v0.md)
> - [backlog-codex-dpp-2026-06-25.md](backlog-codex-dpp-2026-06-25.md)
>
> Esta pagina continua util como fotografia tecnica do que ja existe, mas nao deve prevalecer sobre os gates de evidencia, anti-greenwashing e escopo sem edicao de molde definidos no PRD v0.

---

## 1. Contexto e Motivação

O Digital Product Passport (DPP) é um registro digital estruturado que acompanha um produto ao longo de seu ciclo de vida, tornando rastreável a composição de fibras, a cadeia produtiva, as certificações ambientais e as instruções de reparo e descarte.

A implementação neste ciclo é motivada por três pressões regulatórias concretas:

| Regulação | Escopo | Prazo |
|---|---|---|
| EU ESPR (Ecodesign for Sustainable Products Regulation) | DPP obrigatório para têxteis vendidos na União Europeia | ~2028 (delegated acts em votação) |
| Loi AGEC (França) | QR com composição e origem obrigatório para marcas acima de 10.000 unidades no mercado francês | Em vigor |
| INMETRO Portaria 459 | GTIN + QR obrigatório para fabricantes brasileiros | 31/07/2026 |
| Registro Central DPP da UE | Repositório central operacional | 19/07/2026 |

A PHYLLOS tem distribuição planejada para mercado brasileiro e europeu. Não implementar o DPP antes de 31/07/2026 implica risco de não conformidade com a Portaria 459 do INMETRO para o mercado doméstico e bloqueio de entrada no mercado francês via AGEC.

A decisão de implementar agora — em vez de aguardar o prazo europeu de 2028 — é deliberada: o custo de adaptação retroativa em uma base de dados grande é superior ao custo de modelar corretamente desde o início.

---

## 2. Stack e Escopo

**Stack:** FastAPI + SQLAlchemy + SQLite  
**Aplicação:** `app/main.py` + `app/api/routes.py` + `app/models/models.py`  
**Padrão de saída DPP:** JSON-LD com contexto dual `schema.org` + `gs1.org/voc/`  
**Identificação:** GTIN (EAN-13) como chave pública; UUID v4 interno como identificador DPP  
**QR:** GS1 Digital Link URI apontando para `https://dpp.phyllos.com.br/dpp/{gtin}`  

---

## 3. Modelo de Dados

### 3.1 Diagrama de Entidades

```
+------------------+          +---------------------+
|      Peca        |          |    FichaTecnica      |
+------------------+          +---------------------+
| id               |1       1 | id                  |
| codigo (UK)      +----------+ peca_id (FK)        |
| nome             |          | descricao_tecnica   |
| gtin (UK)        |          | composicao_fibras * |
| dpp_uuid (UK)    |          | instrucoes_reparo * |
| dpp_status       |          | instrucoes_fim_vida*|
| colecao_id (FK)  |          | certificacoes *     |
+------------------+          | conteudo_reciclado  |
        |                     | pegada_carbono      |
        |1                    | durabilidade_ciclos |
        |                     +---------------------+
        |n
+----------------------+
|   EtapaProducao      |
+----------------------+
| id                   |
| peca_id (FK)         |
| etapa                |
| pais                 |
| instalacao_nome      |
| instalacao_gln       |
+----------------------+

* campos novos adicionados neste ciclo
```

Campos marcados com `*` são adições deste ciclo ao modelo preexistente.

### 3.2 Campos Adicionados a `Peca`

| Campo | Tipo SQLAlchemy | Constraint | Descrição |
|---|---|---|---|
| `gtin` | `String` | `unique=True, nullable=True` | EAN-13 ou GTIN-14. Obrigatório para publicar DPP. |
| `dpp_uuid` | `String` | `unique=True, nullable=True` | UUID v4 gerado automaticamente na publicação se ausente. |
| `dpp_status` | `String` | `nullable=True` | Ciclo de vida: `rascunho`, `publicado`, `revogado`. Default `rascunho`. |

Relacionamento adicionado: `etapas_producao` — `relationship("EtapaProducao", back_populates="peca")`.

### 3.3 Campos Adicionados a `FichaTecnica`

| Campo | Tipo SQLAlchemy | Unidade / Formato | Descrição |
|---|---|---|---|
| `composicao_fibras` | `Text` | JSON Array | Lista de fibras e percentuais (ver seção 4.1). |
| `instrucoes_reparo` | `Text` | Texto livre | Instruções de manutenção e reparo para o consumidor. |
| `instrucoes_fim_de_vida` | `Text` | Texto livre | Descarte, reciclagem, doação — exigência AGEC e ESPR. |
| `certificacoes` | `Text` | JSON Array | Lista de certificações com nome, número e validade. |
| `conteudo_reciclado_pct` | `Float` | % (0–100) | Percentual de conteúdo reciclado pré ou pós-consumo. |
| `pegada_carbono_kgco2e` | `Float` | kgCO2e | Pegada de carbono do produto (escopo 1+2+3 recomendado). |
| `durabilidade_ciclos_lavagem` | `Integer` | Ciclos | Número de ciclos de lavagem validados sem degradação relevante. |

### 3.4 Nova Tabela `EtapaProducao`

```
Tabela: etapas_producao
```

| Coluna | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | `Integer PK` | sim | Auto-incremento. |
| `peca_id` | `Integer FK → pecas.id` | sim | Peça à qual a etapa pertence. |
| `etapa` | `String` | sim | Enum de texto: `fiacao`, `tecelagem`, `corte`, `costura`, `tingimento`, `acabamento`, `lavanderia`. |
| `pais` | `String` | sim | Código ISO 3166-1 alpha-2 recomendado (ex: `BR`, `PT`, `CN`). |
| `instalacao_nome` | `String` | sim | Nome da instalação ou fornecedor. |
| `instalacao_gln` | `String` | não | Global Location Number GS1 (13 dígitos). Permite rastreabilidade formal na cadeia GS1. |

A sequência de etapas é determinada pela ordem de inserção (`id` crescente). Não há campo de ordenação explícito neste MVP — se a ordem de inserção não refletir a ordem real da cadeia, o consumidor da API deve reordenar por lógica de negócio ou por campo a ser adicionado na Fase 2.

---

## 4. Formatos de Payload

### 4.1 `composicao_fibras` (JSON armazenado como Text)

```json
[
  {"fibra": "poliester_reciclado", "pct": 78},
  {"fibra": "elastano", "pct": 22}
]
```

A soma dos percentuais deve ser 100. Validação de soma não está implementada no MVP — é responsabilidade do sistema chamador ou de validação a ser adicionada na Fase 2.

Valores de fibra recomendados (não enumerados no banco, livres neste MVP): `algodao_organico`, `poliester_reciclado`, `poliamida`, `elastano`, `viscose`, `linho`, `la`, `seda`, `lyocell`.

### 4.2 `certificacoes` (JSON armazenado como Text)

```json
[
  {"nome": "OEKO-TEX Standard 100", "numero": "XX-XXXXX", "validade": "2027-06-01"},
  {"nome": "GRS", "numero": "CU1234567XXXX", "validade": "2028-01-01"}
]
```

O campo `validade` segue ISO 8601 (`YYYY-MM-DD`). Validação de data não é aplicada no banco neste MVP.

### 4.3 Payload para `POST /pecas/{codigo}/etapas-producao`

```json
{
  "etapa": "costura",
  "pais": "BR",
  "instalacao_nome": "Confeccoes Alfa Ltda",
  "instalacao_gln": "7891234567890"
}
```

### 4.4 Resposta de `GET /dpp/{gtin}` (JSON-LD)

```json
{
  "@context": ["https://schema.org/", "https://gs1.org/voc/"],
  "@type": "Product",
  "gtin": "07891234567890",
  "identifier": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "name": "Calca Trail Performance",
  "description": "Calca de corte reto em tecido stretch reciclado",
  "material": [
    {"fibra": "poliester_reciclado", "pct": 78},
    {"fibra": "elastano", "pct": 22}
  ],
  "recycledContent": 78.0,
  "carbonFootprint": {"value": 3.2, "unitCode": "KGM"},
  "certifications": [
    {"nome": "OEKO-TEX Standard 100", "numero": "XX-XXXXX", "validade": "2027-06-01"}
  ],
  "repairInstructions": "Reforcar costura lateral com linha de poliester 40. Evitar lavagem acima de 40C.",
  "endOfLifeInstructions": "Encaminhar para ponto de coleta Phyllos ou reciclagem textil municipal.",
  "durability": {"washCycles": 80},
  "productionChain": [
    {"stage": "fiacao", "country": "BR", "facility": "Fios Sul Ltda", "gln": "7890000000001"},
    {"stage": "tecelagem", "country": "BR", "facility": "Tecelagem Central", "gln": "7890000000002"},
    {"stage": "corte", "country": "BR", "facility": "Confeccoes Alfa Ltda", "gln": "7891234567890"},
    {"stage": "costura", "country": "BR", "facility": "Confeccoes Alfa Ltda", "gln": "7891234567890"}
  ]
}
```

---

## 5. Endpoints DPP

Todos os endpoints abaixo estão registrados com `tags=["DPP"]` no router FastAPI e visíveis em `/docs`.

| Metodo | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/pecas/{codigo}/etapas-producao` | — | Adiciona uma etapa de producao a uma peca existente. |
| `GET` | `/pecas/{codigo}/etapas-producao` | — | Lista todas as etapas de producao de uma peca. |
| `POST` | `/pecas/{codigo}/dpp/publicar` | — | Valida campos obrigatorios e muda `dpp_status` para `publicado`. Gera `dpp_uuid` se ausente. |
| `GET` | `/dpp/{gtin}` | — | Retorna o DPP completo em JSON-LD. Disponivel apenas para DPPs com status `publicado`. |
| `GET` | `/dpp/{gtin}/qr` | — | Retorna PNG com QR code GS1 Digital Link URI. Retorna `501` se `qrcode[pil]` nao instalado. |

### Regras de Publicacao (`POST /pecas/{codigo}/dpp/publicar`)

A transicao para `publicado` requer:

1. `ficha_tecnica.composicao_fibras` presente e nao nulo.
2. `peca.gtin` presente e nao nulo.

Se qualquer condicao falhar, a API retorna `400` com mensagem descritiva. O endpoint nao valida as etapas de producao como obrigatorias para publicacao neste MVP — recomenda-se adicionar essa validacao na Fase 2.

### Ciclo de Vida do DPP

```
[nao existe] --> POST /dpp/publicar --> [publicado]
[publicado]  --> PATCH peca (dpp_status=revogado) --> [revogado]
```

A transicao para `revogado` nao possui endpoint dedicado neste MVP. Deve ser feita via `PATCH /pecas/{codigo}` com o campo `dpp_status`. Endpoint dedicado de revogacao esta previsto na Fase 2.

---

## 6. GS1 Digital Link e QR

O QR gerado em `GET /dpp/{gtin}/qr` encoda o seguinte URI:

```
https://dpp.phyllos.com.br/dpp/{gtin}
```

Este formato e compativel com a especificacao GS1 Digital Link v1.2. O resolvedor em `dpp.phyllos.com.br` nao esta implementado neste ciclo — o dominio ainda nao esta configurado. O QR e tecnicamente valido mas o link nao resolverao em producao ate o dominio ser provisionado.

Risco: QR codes fisicos impressos antes do dominio estar ativo vao gerar experiencia quebrada para o consumidor final. Nao imprimir QR em etiquetas fisicas ate o dominio estar ativo.

---

## 7. Dependencias

| Pacote | Versao minima | Obrigatorio | Uso |
|---|---|---|---|
| `fastapi` | ^0.110 | sim | Framework HTTP |
| `sqlalchemy` | ^2.0 | sim | ORM |
| `pydantic` | ^2.0 | sim | Schemas e validacao |
| `qrcode[pil]` | ^7.4 | nao | Geracao de QR code. Endpoint retorna `501` se ausente. |

Para instalar a dependencia opcional:

```bash
pip install "qrcode[pil]"
```

---

## 8. Lacunas e Riscos

| Item | Tipo | Descricao | Mitigacao |
|---|---|---|---|
| Validacao de soma de fibras | Lacuna tecnica | `composicao_fibras` nao valida se a soma dos `pct` e 100. | Adicionar validacao Pydantic no schema na Fase 2. |
| Ordenacao de etapas de producao | Lacuna tecnica | A ordem real da cadeia depende da ordem de insercao no banco. | Adicionar campo `ordem` inteiro na tabela `EtapaProducao` na Fase 2. |
| Dominio DPP nao provisionado | Risco operacional | `dpp.phyllos.com.br` nao esta configurado. QR impresso sem dominio ativo e inutilizavel. | Nao imprimir QR em etiqueta fisica ate dominio ativo e testado. |
| Revogacao de DPP sem endpoint dedicado | Lacuna de produto | Revogar exige `PATCH /pecas/{codigo}` manual. | Endpoint `/pecas/{codigo}/dpp/revogar` na Fase 2. |
| Autenticacao ausente nos endpoints DPP | Risco de seguranca | Qualquer usuario pode publicar ou revogar um DPP. | Adicionar autenticacao JWT ou API key antes de expor em producao publica. |
| Validacao de GTIN | Lacuna tecnica | O banco aceita qualquer string como GTIN. O digito verificador GS1 nao e validado. | Adicionar validacao de checksum EAN-13 no schema Pydantic. |
| `pegada_carbono_kgco2e` sem metodologia declarada | Lacuna regulatoria | A ESPR exigira declaracao de metodologia de calculo (escopo, fronteiras de sistema). | Adicionar campo `metodologia_carbono` (texto) e `escopo_carbono` na FichaTecnica antes da conformidade ESPR. |

---

## 9. Proximas Fases

### Fase 2 — Consolidacao e Conformidade (estimativa: Q3 2026)

- Endpoint `/pecas/{codigo}/dpp/revogar` dedicado.
- Autenticacao JWT em todos os endpoints de escrita DPP.
- Validacao de checksum GTIN-13/14 no schema Pydantic.
- Validacao de soma de percentuais em `composicao_fibras`.
- Campo `ordem` em `EtapaProducao` para ordenacao explicita da cadeia.
- Campo `metodologia_carbono` em `FichaTecnica`.
- Provisionamento e teste do dominio `dpp.phyllos.com.br` com resolvedor GS1 Digital Link.
- Integracao com NF-e como fonte verificavel de cadeia produtiva (rastreabilidade documental).

### Fase 3 — DPP-as-a-Service (estimativa: Q1 2027)

- Multi-tenancy: outras marcas podem emitir DPPs via Fashion OS com namespace proprio.
- Painel de gestao DPP por marca.
- Exportacao para o Registro Central DPP da UE (endpoint da Comissao Europeia, operacional desde 19/07/2026).
- Assinatura digital dos DPPs (W3C Verifiable Credentials ou equivalente GS1).

---

## 10. Proximos Passos Imediatos

1. **Founder humano / Product & Data** valida esta especificacao e aprova ou ajusta o escopo funcional da Fase 2.
2. **Tech Lead Full-stack & Data + DevOps & Security Agent** provisionam o dominio `dpp.phyllos.com.br`, configuram o resolvedor e registram o runbook antes de qualquer uso real do QR.
3. **Implementation & Customer Success Lead + Implementation & Customer Success Analyst** confirmam os identificadores e dados reais necessários ao piloto antes do onboarding.
4. **Regulatory Specialist + Backend & Data Engineer** documentam campos obrigatorios, regras, evidencias e validacoes no contrato de dados e na API.
5. **Tech Lead Full-stack & Data + DevOps & Security Agent** executam o fluxo completo: criar peca com GTIN → criar ficha tecnica com composicao → adicionar etapas → publicar DPP → validar JSON-LD → gerar QR → resolver URL.

---

*Documento mantido por Founder humano / Product & Data, Tech Lead Full-stack & Data e Backend & Data Engineer. Versionar junto ao codigo e atualizar a cada ciclo que altere modelo, endpoints ou regras de publicacao.*
