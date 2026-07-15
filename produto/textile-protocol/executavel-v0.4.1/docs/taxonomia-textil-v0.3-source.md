# Taxonomia têxtil v0.3

Reestruturação sobre a v0.2, incorporando revisão especializada. Duas mudanças estruturais grandes nesta versão:
1. camada de evidência/confiança passa a ser **transversal** — todo campo de qualquer módulo pode carregá-la;
2. nome comercial deixa de ser lista de tags e passa a ser **entidade relacional**.

O benchmark 1 continua congelado exatamente como definido na v0.1/v0.2 — nada aqui altera seu escopo.

---

## 0. Camada transversal de evidência e confiança

Todo campo classificado nesta taxonomia — família estrutural, ligamento, padrão, atributo aparente, propriedade mensurada, composição, nome comercial, processo de acabamento ou função declarada — pode e deve carregar este envelope quando a fonte permitir:

```
valor: <valor do campo>
fonte_da_evidencia: <macrofotografia | ficha_tecnica | laudo_laboratorial | declaracao_fornecedor | inferencia_visual | outro>
tipo_de_evidencia: <observado | inferido | declarado_nao_verificado | declarado_verificado>
metodo: <norma ou protocolo, quando aplicável>
data_da_evidencia: <data>
confianca: <alta | media | baixa | indeterminada>
qualidade_da_captura: <adequada | limitada | insuficiente>
publicavel: <sim | nao | parcial>
motivo_da_abstencao: <texto livre, obrigatório se publicavel = nao>
evidencias_conflitantes: <sim | nao | nao_aplicavel>
```

Regras:
- `tipo_de_evidencia = inferido` nunca pode gerar `confianca = alta` sozinho; inferência visual tem teto de confiança média, salvo corroboração por outra fonte independente.
- Nenhuma função declarada de acabamento (ver módulo 7) pode ser publicada com `tipo_de_evidencia = declarado_nao_verificado` em canal de consumidor final sem aviso explícito de status.
- Campos sem este envelope preenchido são tratados como `confianca = indeterminada` por padrão, não como ausentes.

Esta camada é o que torna a taxonomia auditável para fins de ISCM/DPP/ESPR — sem ela, "composição completa" ou "antimicrobiano" são afirmações sem proveniência.

---

## 1. Estrutura física

- `tecido_plano`
- `malha_trama`
- `malha_urdume`
- `nao_tecido`
- `entrelacado_trancado` — fitas, tranças, rendas de bilro; fios interlaçados sem sistema trama/urdume ortogonal.
- `costurado_stitch_bonded` — estruturas tipo Malimo/Arachne.
- `estrutura_composta` — ver definição operacional no módulo 6.
- `indeterminado`

Pergunta correta de triagem: "tecido plano, malha, não tecido, entrelaçado, costurado ou indeterminado".

---

## 2. Fio (camada nova entre fibra e tecido)

Aplicável a qualquer estrutura tecida ou de malha, quando a evidência permitir análise de fio removido ou macrofotografia de alta resolução.

| Atributo | Valores |
|---|---|
| Continuidade | `filamento_continuo`, `fibra_descontinua`, `misto`, `indeterminado` |
| Sistema de fiação | `fiado`, `multifilamento`, `monofilamento`, `indeterminado` |
| Número de cabos | numérico, ou `indeterminado` |
| Torção | `torcido_S`, `torcido_Z`, `sem_torção_aparente`, `indeterminado` |
| Título/densidade linear | `tex`, `dtex`, `Nm`, `Ne`, conforme ISO 7211-5 / ISO 2060, ou `indeterminado` |
| Texturização | `texturizado`, `nao_texturizado`, `indeterminado` |
| Fio fantasia | `bouclé`, `chenille`, `flamê`, `core_spun`, `nao_aplicavel`, `indeterminado` |

Densidade de fios (fios/cm), torção e massa por unidade de urdume/trama seguem a família ISO 7211 quando o método for laboratorial; valores de fotografia comum entram como `inferido` na camada de evidência, nunca como medição.

---

## 3. Construção primária

**Tecido plano** — ligamentos-base:
- `tafeta`
- `sarja`
- `cetim`
- `leno_gaze` — par de fios de urdume entrelaçados em torno da trama; 4º ligamento fundamental, fora do escopo do benchmark 1.
- `indeterminado`

**Malha de trama** — construções-base:
- `jersey`
- `ribana_canelada`
- `interlock`
- `purl_links_links`
- `pique_malha`
- `indeterminado`

Subtaxonomia de malha (backlog, tratar como módulo próprio dado o volume terminológico da ISO para malharia):
- distinção malha simples / malha dupla;
- estrutura de laçada: `ponto_meia`, `ponto_reverso`, `tuck`, `miss`;
- `moletom`, `plush`, `jacquard_de_malha`, `renda_de_malha`, `malha_espacadora`;
- inserção de trama (`weft_insertion`);
- abertura: `estrutura_aberta`, `estrutura_fechada`, `estrutura_rede`.

**Malha de urdume**:
- `tricot`
- `raschel`
- `milanese`
- `indeterminado`

---

## 4. Padronização e derivação (reestruturado em 4 dimensões independentes)

A v0.2 ainda misturava níveis diferentes num campo único. A partir da v0.3, são 4 campos independentes — um item pode ter valor em mais de um simultaneamente.

**4.1 Derivação do ligamento**
- `cestaria_panama_basket`
- `espinha_de_peixe`
- `broken_twill`
- `sarja_cruzada`
- `sarja_composta`
- `cetim_derivado`
- `indeterminado`

**4.2 Mecanismo de padronização**
- `dobby`
- `jacquard`
- `estampa`
- `bordado`
- `indeterminado`

**4.3 Construção especial**
- `ripstop`
- `gaze_leno` *(referência cruzada com 3 — aqui como técnica aplicada, não como ligamento-base)*
- `pique`
- `crepe_estrutural`
- `indeterminado`

**4.4 Estrutura superficial ou multicamada**
- `pelo_cortado`
- `pelo_em_laco`
- `felpa`
- `dupla_face`
- `dupla_camada`
- `tecido_espacador`
- `indeterminado`

Nota: `oxford` foi removido como valor de padrão nesta versão — ele é predominantemente um nome comercial (ver módulo 8) com tendência de construção em cestaria; mantê-lo como valor de padrão duplicava o conceito em dois módulos.

---

## 5. Atributos visuais, táteis e propriedades ensaiadas (separados)

**5.1 Atributos visuais** (qualificador "aparente" obrigatório; fonte tipicamente fotografia)

| Atributo | Valores |
|---|---|
| Transparência | `opaco`, `semiopaco`, `semitransparente`, `transparente`, `indeterminado` |
| Brilho | `fosco`, `semifosco`, `acetinado`, `brilhante`, `indeterminado` |
| Textura visual | `lisa`, `granulada`, `canelada`, `felpuda`, `aveludada`, `slub_aparente`, `indeterminado` |
| Regularidade | `regular`, `irregular`, `indeterminado` |
| Cor aparente | `lisa_aparente`, `estampada_aparente`, `jacquard_multicor_aparente`, `indeterminado` |
| Uniformidade de cor | `uniforme`, `com_variacao_aparente`, `indeterminado` |
| Padrão aparente / escala / orientação | texto livre estruturado, `indeterminado` |
| Contraste urdume x trama | `alto`, `baixo`, `indeterminado` |
| Abertura/cobertura aparente | `fechada`, `aberta`, `indeterminado` |
| Pilosidade aparente | `presente`, `ausente`, `indeterminado` |
| Relevo aparente | `plano`, `em_relevo`, `indeterminado` |
| Face/avesso distinguíveis | `sim`, `nao`, `indeterminado` |
| Defeitos aparentes | texto livre estruturado, `indeterminado` |

**5.2 Atributos táteis** (nunca inferidos de fotografia comum; exigem amostra física ou declaração de quem manuseou)
- `suave`, `aspero`, `seco`, `frio_ao_toque`, `macio`, `indeterminado`.
Campo bloqueado para `fonte_da_evidencia = macrofotografia` — deve rejeitar e forçar `indeterminado` se a única evidência for imagem.

**5.3 Propriedades ensaiadas** (exigem método, condição, direção e unidade — nunca só o número)
- gramatura (`g/m²`);
- densidade de fios (`fios/cm`, `carreiras/cm`, `colunas/cm` — ISO 7211-2);
- espessura sob pressão especificada (`mm`);
- largura útil (`cm`);
- alongamento e recuperação (`%`, por direção e método);
- caimento (método definido);
- absorção / tempo de molhamento (protocolo);
- resistência à tração (`N` ou `kgf`, método);
- resistência ao rasgo (`N`, método);
- estouro (`kPa`, método);
- abrasão (ciclos até falha, método);
- pilling (escala de referência, método);
- estabilidade dimensional / encolhimento (`%`, ciclo definido);
- permeabilidade ao ar (`mm/s`) e ao vapor (`g/m²/dia`);
- resistência térmica;
- solidez de cor (lavagem, luz, atrito — escala de referência, método);
- inflamabilidade (norma aplicável);
- resistência à água;
- proteção UV (UPF, método);
- resistência ao snagging.

---

## 6. Estrutura composta (definição operacional)

`estrutura_composta` só se aplica quando há combinação física de duas ou mais estruturas têxteis (ou têxtil + não-têxtil) formando uma unidade não separável sem dano. Valores:
- `laminado`
- `revestido`
- `dublado`
- `acolchoado`
- `com_membrana`
- `sanduiche_textil`
- `reforcado`
- `com_filme`
- `com_espuma`
- `compósito_fibra_matriz`
- `indeterminado`

Distinção obrigatória: um acabamento aplicado sobre uma estrutura única (ex: resinado, revestido em camada fina) não torna a peça `estrutura_composta` — isso é acabamento (módulo 7). `estrutura_composta` exige camada estrutural adicional com função própria (isolamento, barreira, reforço mecânico), não apenas tratamento de superfície.

---

## 7. Não-tecidos (alinhado a ISO 9092:2026)

Mantido no backlog para classificação automática até dataset especializado, mas a estrutura de referência já pode ser fixada, citando ISO 9092:2026 (Nonwovens — Vocabulary, 4ª edição) como norma-base:

- formação da manta: `cardada`, `airlaid`, `wetlaid`, `spunlaid`;
- formação por extrusão: `spunbond`, `meltblown`;
- consolidação: `agulhado`, `hidroentrelacado`, `termico`, `quimico`;
- orientação das fibras: `orientada`, `aleatoria`, `indeterminado`;
- número de camadas: numérico, ou `indeterminado`;
- combinações nomeadas: `SMS`, `laminado_nao_tecido`, `outro`.

---

## 8. Acabamento (reestruturado: processo ≠ função declarada)

**8.1 Processos de acabamento** (o que foi fisicamente feito)
- `mercerizado`
- `calandrado`
- `sanforizado`
- `escovado`
- `lixado`
- `peletizado`
- `resinado`
- `revestido`
- `termofixado`
- `enzimatico_bio_polimento`
- `outro`
- `nao_informado`

**8.2 Funções declaradas** (o que se afirma que o processo confere — sempre com envelope de evidência do módulo 0 obrigatório, não opcional)
- `impermeabilizado`
- `repelente`
- `antimicrobiano`
- `anti_chama`
- `anti_pilling`
- `antiestatico`
- `hidrofilico`
- `protecao_uv`
- `outro`
- `nao_informado`

Regra dura: nenhuma função declarada em 8.2 é publicável sem `fonte_da_evidencia` e `metodo` preenchidos (módulo 0). Um item processado com "revestido" não herda automaticamente "impermeabilizado" — são afirmações independentes que precisam de comprovação própria. Isso é diretamente relevante para conformidade com diretrizes de alegações ambientais/funcionais na UE.

---

## 9. Composição

- `composicao_ausente`
- `composicao_parcial_nao_publicavel`
- `composicao_completa`

Por fibra, quando a fonte permitir:
- origem: `virgem`, `reciclado_pre_consumo`, `reciclado_pos_consumo`, `origem_nao_informada`;
- certificação: lista aberta com fonte obrigatória (GOTS, GRS, OEKO-TEX, `sem_certificacao_informada`);
- rastreabilidade: `nivel_fibra`, `nivel_lote`, `nivel_fornecedor`, `nao_rastreado`.

`composicao_completa` não implica rastreabilidade completa — campos independentes, cada um com seu próprio envelope de evidência (módulo 0).

---

## 10. Nome comercial (schema relacional completo)

Nome comercial deixa de ser enum de tags e passa a ser entidade com relações explícitas para outros módulos. Estrutura de registro:

```
nome_canonico: <string>
sinonimos: [<string>, ...]
idioma_regiao: [<idioma-BR | idioma-EU | idioma-outro>, ...]
definicao_usual: <texto curto>
construcoes_compativeis: [<referência a módulo 3 e/ou 4>, ...]   # relação N:N, não obrigatória 1:1
composicoes_frequentes: [<referência a módulo 9>, ...]           # tendência de mercado, não regra
excecoes_conhecidas: <texto livre>
fonte: <string ou lista>
grau_de_ambiguidade: <baixo | medio | alto>
```

Exemplos de registro (ilustrativos, não exaustivos):

| nome_canonico | construções compatíveis | composições frequentes | ambiguidade |
|---|---|---|---|
| `chambray` | tafeta | algodão, algodão+elastano | baixo |
| `denim` | sarja | algodão, algodão+elastano | baixo |
| `cambraia` | tafeta | algodão, viscose | baixo |
| `voil` | tafeta, leno_gaze | algodão, poliéster | medio |
| `organza` | tafeta | seda, poliéster | baixo |
| `popeline` | tafeta | algodão, algodão+poliéster | baixo |
| `gabardine` | sarja | algodão, poliéster, lã | baixo |
| `oxford` | cestaria (padrão 4.1); também mecanismo dobby (4.2) em variantes | algodão, algodão+poliéster | **alto** — mesmo nome ocupa posição de padrão de tecelagem E denominação comercial; tratar como duas entidades relacionadas, nunca inferir uma a partir da outra |
| `moletom` | malha (jersey/felpa) | algodão, algodão+poliéster | baixo |
| `veludo` | felpa_pelo_cortado (4.4) | algodão, viscose, poliéster | medio |
| `crepe` (comercial) | crepe_estrutural (4.3) ou acabamento químico | poliéster, seda, viscose | medio — mecanismo de origem do efeito nem sempre determinável por aparência |

Regra dura: nenhuma inferência automática de construção, composição ou ligamento a partir de nome comercial sem passar pelo campo `grau_de_ambiguidade`. Nome comercial com ambiguidade `alto` nunca preenche automaticamente módulos 3/4/9 — força decisão `pedir_nova_evidencia` no fluxo de classificação.

---

## Escopo congelado para o primeiro benchmark (inalterado)
1. família estrutural (módulo 1);
2. tafetá, sarja e cetim em tecido plano (módulo 3 — leno fica no backlog do benchmark 2);
3. transparência aparente (módulo 5.1);
4. qualidade da captura (módulo 0);
5. decisão `classificar / abster / pedir_nova_evidencia`.

## Backlog priorizado para benchmark 2+
1. `leno_gaze` como ligamento-base — validação própria.
2. Subtaxonomia de malha (módulo 3, estrutura de laçada e variantes).
3. Classificação automática de não-tecidos por macrofotografia (módulo 7) — provavelmente inviável só com imagem; avaliar necessidade de evidência complementar.
4. População inicial do schema relacional de nome comercial (módulo 10) — priorizar os nomes de maior volume no catálogo Phyllos antes de expandir a lista.
5. Escala de referência padronizada para pilling e solidez de cor — decidir ISO, ABNT ou ambas conforme mercado de destino (BR vs. UE/ESPR).
6. Integração do módulo 0 (evidência/confiança) ao pipeline de classificação — decidir onde o envelope é preenchido automaticamente vs. onde exige input humano.