# Taxonomia têxtil v0.3

**Status:** versão vigente pós-revisão especializada

**Benchmark 1:** inalterado

## 0. Envelope transversal de evidência e confiança

Todo campo pode carregar:

```yaml
valor: null
fonte_da_evidencia: macrofotografia | ficha_tecnica | laudo_laboratorial | declaracao_fornecedor | inferencia_visual | outro
tipo_de_evidencia: observado | inferido | declarado_nao_verificado | declarado_verificado
metodo: null
data_da_evidencia: null
confianca: alta | media | baixa | indeterminada
qualidade_da_captura: adequada | limitada | insuficiente
publicavel: sim | nao | parcial
motivo_da_abstencao: null
evidencias_conflitantes: sim | nao | nao_aplicavel
```

Regras:

- inferência visual isolada tem teto de confiança média;
- campo sem envelope completo assume confiança indeterminada;
- função declarada exige fonte e método para publicação;
- o envelope complementa, mas não substitui, o estado canônico de evidência PHYLLOS;
- `publicavel = nao` exige motivo de abstenção.

## 1. Estrutura física

- `tecido_plano`
- `malha_trama`
- `malha_urdume`
- `nao_tecido`
- `entrelacado_trancado`
- `costurado_stitch_bonded`
- `estrutura_composta`
- `indeterminado`

Pergunta de triagem: tecido plano, malha, não tecido, entrelaçado, costurado ou indeterminado?

## 2. Fio

| Atributo | Valores ou unidade |
|---|---|
| Continuidade | `filamento_continuo`, `fibra_descontinua`, `misto`, `indeterminado` |
| Sistema | `fiado`, `multifilamento`, `monofilamento`, `indeterminado` |
| Número de cabos | numérico ou `indeterminado` |
| Torção | `torcido_S`, `torcido_Z`, `sem_torcao_aparente`, `indeterminado` |
| Título | `tex`, `dtex`, `Nm`, `Ne` ou `indeterminado` |
| Texturização | `texturizado`, `nao_texturizado`, `indeterminado` |
| Fio fantasia | `boucle`, `chenille`, `flame`, `core_spun`, `nao_aplicavel`, `indeterminado` |

Fotografia comum não produz medição de densidade, torção ou título.

## 3. Construção primária

### Tecido plano

- `tafeta`
- `sarja`
- `cetim`
- `leno_gaze`
- `indeterminado`

`leno_gaze` permanece fora do benchmark 1.

### Malha de trama

- `jersey`
- `ribana_canelada`
- `interlock`
- `purl_links_links`
- `pique_malha`
- `indeterminado`

Subtaxonomia de laçadas, malhas simples/duplas, jacquard, renda, espaçadoras e inserção de trama permanece no backlog.

### Malha de urdume

- `tricot`
- `raschel`
- `milanese`
- `indeterminado`

## 4. Padronização e derivação

São quatro dimensões independentes e simultâneas.

### 4.1 Derivação do ligamento

- `cestaria_panama_basket`
- `espinha_de_peixe`
- `broken_twill`
- `sarja_cruzada`
- `sarja_composta`
- `cetim_derivado`
- `indeterminado`

### 4.2 Mecanismo de padronização

- `dobby`
- `jacquard`
- `estampa`
- `bordado`
- `indeterminado`

### 4.3 Construção especial

- `ripstop`
- `gaze_leno`
- `pique`
- `crepe_estrutural`
- `indeterminado`

### 4.4 Estrutura superficial ou multicamada

- `pelo_cortado`
- `pelo_em_laco`
- `felpa`
- `dupla_face`
- `dupla_camada`
- `tecido_espacador`
- `indeterminado`

Oxford deixa de ser valor desta camada e passa ao modelo relacional de nome comercial.

## 5. Atributos e propriedades

### 5.1 Visuais aparentes

| Atributo | Valores |
|---|---|
| Transparência | `opaco`, `semiopaco`, `semitransparente`, `transparente`, `indeterminado` |
| Brilho | `fosco`, `semifosco`, `acetinado`, `brilhante`, `indeterminado` |
| Textura | `lisa`, `granulada`, `canelada`, `felpuda`, `aveludada`, `slub_aparente`, `indeterminado` |
| Regularidade | `regular`, `irregular`, `indeterminado` |
| Cor aparente | `lisa_aparente`, `estampada_aparente`, `jacquard_multicor_aparente`, `indeterminado` |
| Uniformidade de cor | `uniforme`, `com_variacao_aparente`, `indeterminado` |
| Contraste urdume × trama | `alto`, `baixo`, `indeterminado` |
| Abertura/cobertura | `fechada`, `aberta`, `indeterminado` |
| Pilosidade | `presente`, `ausente`, `indeterminado` |
| Relevo | `plano`, `em_relevo`, `indeterminado` |
| Face/avesso distinguíveis | `sim`, `nao`, `indeterminado` |

Padrão, escala, orientação e defeitos aparentes usam texto livre estruturado.

### 5.2 Táteis

- `suave`
- `aspero`
- `seco`
- `frio_ao_toque`
- `macio`
- `indeterminado`

São bloqueados para macrofotografia; exigem amostra física ou declaração de quem manuseou.

### 5.3 Propriedades ensaiadas

Exigem método, condição, direção e unidade:

- gramatura;
- densidade de fios, carreiras e colunas;
- espessura e largura útil;
- alongamento e recuperação;
- caimento e absorção;
- tração, rasgo e estouro;
- abrasão, pilling e snagging;
- estabilidade dimensional;
- permeabilidade ao ar e ao vapor;
- resistência térmica;
- solidez de cor;
- inflamabilidade;
- resistência à água;
- proteção UV.

## 6. Estrutura composta

Só se aplica quando duas ou mais estruturas formam unidade não separável sem dano:

- `laminado`
- `revestido`
- `dublado`
- `acolchoado`
- `com_membrana`
- `sanduiche_textil`
- `reforcado`
- `com_filme`
- `com_espuma`
- `composito_fibra_matriz`
- `indeterminado`

Tratamento superficial isolado permanece acabamento, não estrutura composta.

## 7. Não tecidos

Taxonomia de referência, ainda fora da classificação automática:

- formação da manta: `cardada`, `airlaid`, `wetlaid`, `spunlaid`;
- extrusão: `spunbond`, `meltblown`;
- consolidação: `agulhado`, `hidroentrelacado`, `termico`, `quimico`;
- orientação: `orientada`, `aleatoria`, `indeterminado`;
- número de camadas;
- combinações: `SMS`, `laminado_nao_tecido`, `outro`.

Referências normativas devem ser confirmadas antes de uso público ou contratual.

## 8. Acabamento

### 8.1 Processo executado

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

### 8.2 Função declarada

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

Processo não implica função. Toda função exige envelope de evidência, fonte e método.

## 9. Composição

Estados:

- `composicao_ausente`
- `composicao_parcial_nao_publicavel`
- `composicao_completa`

Campos independentes por fibra:

- percentual e fonte;
- origem: virgem, reciclado pré-consumo, reciclado pós-consumo ou não informada;
- certificações, com fonte obrigatória;
- rastreabilidade: fibra, lote, fornecedor ou não rastreado.

Composição completa não implica rastreabilidade completa.

## 10. Nome comercial relacional

```yaml
nome_canonico: string
sinonimos: []
idioma_regiao: []
definicao_usual: string
construcoes_compativeis: []
composicoes_frequentes: []
excecoes_conhecidas: string
fonte: []
grau_de_ambiguidade: baixo | medio | alto
```

Exemplos iniciais:

| Nome | Construções compatíveis | Composições frequentes | Ambiguidade |
|---|---|---|---|
| Chambray | tafetá | algodão; algodão + elastano | baixa |
| Denim | sarja | algodão; algodão + elastano | baixa |
| Cambraia | tafetá | algodão; viscose | baixa |
| Voil | tafetá; leno | algodão; poliéster | média |
| Organza | tafetá | seda; poliéster | baixa |
| Popeline | tafetá | algodão; algodão + poliéster | baixa |
| Gabardine | sarja | algodão; poliéster; lã | baixa |
| Oxford | cestaria e variantes dobby | algodão; algodão + poliéster | alta |
| Moletom | malha jersey/felpa | algodão; algodão + poliéster | baixa |
| Veludo | pelo cortado | algodão; viscose; poliéster | média |
| Crepe | estrutural ou acabamento | poliéster; seda; viscose | média |

Nome com ambiguidade alta nunca preenche automaticamente construção ou composição; gera `pedir_nova_evidencia`.

## Benchmark 1 congelado

1. família estrutural;
2. tafetá, sarja e cetim em tecido plano;
3. transparência aparente;
4. qualidade da captura;
5. decisão `classificar / abster / pedir_nova_evidencia`.

## Backlog para benchmark 2+

1. Leno/gaze.
2. Subtaxonomia de malhas.
3. Não tecidos com evidência complementar.
4. População do catálogo relacional de nomes comerciais.
5. Escalas normativas para pilling e solidez.
6. Integração completa do envelope de evidência ao pipeline.
